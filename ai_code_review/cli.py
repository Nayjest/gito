import asyncio
import logging
import sys
import os
import shutil
import textwrap

import requests

import microcore as mc
import typer
from git import Repo

from .core import review, get_diff, filter_diff
from .report_struct import Report
from .constants import ENV_CONFIG_FILE
from .bootstrap import bootstrap
from .project_config import ProjectConfig
from .utils import no_subcommand, parse_refs_pair

app = typer.Typer(pretty_exceptions_show_locals=False)
app_no_subcommand = typer.Typer(pretty_exceptions_show_locals=False)


def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    if no_subcommand(app):
        app()
    else:
        bootstrap()
        app_no_subcommand()


@app.callback(invoke_without_command=True)
def cli(ctx: typer.Context):
    if ctx.invoked_subcommand != "setup":
        bootstrap()


def args_to_target(refs, what, against) -> tuple[str | None, str | None]:
    _what, _against = parse_refs_pair(refs)
    if _what:
        if what:
            raise typer.BadParameter(
                "You cannot specify both 'refs' <WHAT>..<AGAINST> and '--what'. Use one of them."
            )
    else:
        _what = what
    if _against:
        if against:
            raise typer.BadParameter(
                "You cannot specify both 'refs' <WHAT>..<AGAINST> and '--against'. Use one of them."
            )
    else:
        _against = against
    return _what, _against


def arg_refs() -> typer.Argument:
    return typer.Argument(
        default=None,
        help="Git refs to review, [what]..[against] e.g. 'HEAD..HEAD~1'"
    )


def arg_what() -> typer.Option:
    return typer.Option(None, "--what", "-w", help="Git ref to review")


def arg_filters() -> typer.Option:
    return typer.Option(
        "", "--filter", "-f", "--filters",
        help="""
            filter reviewed files by glob / fnmatch pattern(s),
            e.g. 'src/**/*.py', may be comma-separated
            """,
    )


def arg_against() -> typer.Option:
    return typer.Option(
        None,
        "--against", "-vs", "--vs",
        help="Git ref to compare against"
    )


@app_no_subcommand.command(name="review", help="Perform code review")
@app.command(name="review", help="Perform code review")
def cmd_review(
    refs: str = arg_refs(),
    what: str = arg_what(),
    against: str = arg_against(),
    filters: str = arg_filters()
):
    _what, _against = args_to_target(refs, what, against)
    asyncio.run(review(what=_what, against=_against, filters=filters))


@app.command(help="Configure LLM for local usage interactively")
def setup():
    mc.interactive_setup(ENV_CONFIG_FILE)


@app.command()
def render(format: str = Report.Format.MARKDOWN):
    print(Report.load().render(format=format))


@app.command(help="Review remote code")
async def remote(url=typer.Option(), branch=typer.Option()):
    if os.path.exists("reviewed-repo"):
        shutil.rmtree("reviewed-repo")
    Repo.clone_from(url, branch=branch, to_path="reviewed-repo")
    prev_dir = os.getcwd()
    try:
        os.chdir("reviewed-repo")
        asyncio.run(review())
    finally:
        os.chdir(prev_dir)


@app.command(help="Leave a GitHub PR comment with the review.")
def github_comment(
    token: str = typer.Option(
        os.environ.get("GITHUB_TOKEN", ""), help="GitHub token (or set GITHUB_TOKEN env var)"
    ),
):
    """
    Leaves a comment with the review on the current GitHub pull request.
    """
    file = "code-review-report.txt"
    if not os.path.exists(file):
        print(f"Review file not found: {file}")
        raise typer.Exit(4)

    with open(file, "r", encoding="utf-8") as f:
        body = f.read()

    if not token:
        print("GitHub token is required (--token or GITHUB_TOKEN env var).")
        raise typer.Exit(1)

    github_env = ProjectConfig.load().prompt_vars["github_env"]
    repo = github_env.get("github_repo", "")
    pr_env_val = github_env.get("github_pr_number", "")
    logging.info(f"github_pr_number = {pr_env_val}")

    # e.g. could be "refs/pull/123/merge" or a direct number
    if "/" in pr_env_val and "pull" in pr_env_val:
        # refs/pull/123/merge
        try:
            pr_num_candidate = pr_env_val.strip("/").split("/")
            idx = pr_num_candidate.index("pull")
            pr = int(pr_num_candidate[idx + 1])
        except Exception:
            pr = 0
    else:
        try:
            pr = int(pr_env_val)
        except Exception:
            pr = 0

    api_url = f"https://api.github.com/repos/{repo}/issues/{pr}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    data = {"body": body}

    resp = requests.post(api_url, headers=headers, json=data)
    if 200 <= resp.status_code < 300:
        logging.info(f"Posted review comment to PR #{pr} in {repo}")
    else:
        logging.error(f"Failed to post comment: {resp.status_code} {resp.reason}\n{resp.text}")
        raise typer.Exit(5)


@app.command(help="List files in the diff. Might be useful to check what will be reviewed.")
def files(
    refs: str = arg_refs(),
    what: str = arg_what(),
    against: str = arg_against(),
    filters: str = arg_filters(),
    diff: bool = typer.Option(default=False, help="Show diff content")
):
    _what, _against = args_to_target(refs, what, against)
    repo = Repo(".")
    patch_set = get_diff(repo=repo, what=what, against=against)
    patch_set = filter_diff(patch_set, filters)
    print(
        f"Changed files: "
        f"{mc.ui.green(_what or 'INDEX')} vs "
        f"{mc.ui.yellow(_against or repo.remotes.origin.refs.HEAD.reference.name)}"
        f"{' filtered by '+mc.ui.cyan(filters) if filters else ''}"
    )

    for patch in patch_set:
        if patch.is_added_file:
            color = mc.ui.green
        elif patch.is_removed_file:
            color = mc.ui.red
        else:
            color = mc.ui.blue
        print(f"- {color(patch.path)}")
        if diff:
            print(mc.ui.gray(textwrap.indent(str(patch), "  ")))

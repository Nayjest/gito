import asyncio
import logging
import sys
import os
import shutil
import requests

import microcore as mc
import async_typer
import typer
from ai_code_review.utils import parse_refs_pair
from git import Repo

from .core import review
from .report_struct import Report
from .constants import ENV_CONFIG_FILE
from .bootstrap import bootstrap
from .project_config import ProjectConfig
from .utils import is_app_command_invocation


app = async_typer.AsyncTyper(pretty_exceptions_show_locals=False)
default_command_app = async_typer.AsyncTyper(pretty_exceptions_show_locals=False)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def main():
    if is_app_command_invocation(app):
        app()
    else:
        bootstrap()
        default_command_app()


@app.callback(invoke_without_command=True)
def cli(ctx: typer.Context):
    if ctx.invoked_subcommand != "setup":
        bootstrap()


@default_command_app.async_command(name="review", help="Perform code review")
@app.async_command(name="review", help="Perform code review")
async def cmd_review(
    refs: str = typer.Argument(
        default=None,
        help="Git refs to review, [what]..[against] e.g. 'HEAD..HEAD~1'"
    ),
    what: str = typer.Option(None, "--what", "-w", help="Git ref to review"),
    against: str = typer.Option(
        None,
        "--against", "-vs", "--vs",
        help="Git ref to compare against"
    ),
    filters: str = typer.Option(
        "", "--filter", "-f", "--filters",
        help="""
        filter reviewed files by glob / fnmatch pattern(s),
        e.g. 'src/**/*.py', may be comma-separated
        """,
    )
):
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
    await review(what=_what, against=_against, filters=filters)


@app.async_command(help="Configure LLM for local usage interactively")
async def setup():
    mc.interactive_setup(ENV_CONFIG_FILE)


@app.async_command()
async def render(format: str = Report.Format.MARKDOWN):
    print(Report.load().render(format=format))


@app.async_command(help="Review remote code")
async def remote(url=typer.Option(), branch=typer.Option()):
    if os.path.exists("reviewed-repo"):
        shutil.rmtree("reviewed-repo")
    Repo.clone_from(url, branch=branch, to_path="reviewed-repo")
    prev_dir = os.getcwd()
    try:
        os.chdir("reviewed-repo")
        await review()
    finally:
        os.chdir(prev_dir)


@app.async_command(help="Leave a GitHub PR comment with the review.")
async def github_comment(
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

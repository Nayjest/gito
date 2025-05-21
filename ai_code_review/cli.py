import asyncio
import sys
import os
import shutil

import microcore as mc
import async_typer
import typer
from .core import review
from .report_struct import Report
from git import Repo

from .constants import ENV_CONFIG_FILE
from .bootstrap import bootstrap


app = async_typer.AsyncTyper(
    pretty_exceptions_show_locals=False,
)


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@app.callback(invoke_without_command=True)
def cli(ctx: typer.Context, filters=typer.Option("", "--filter", "-f", "--filters")):
    if ctx.invoked_subcommand != "setup":
        bootstrap()
    if not ctx.invoked_subcommand:
        asyncio.run(review(filters=filters))


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

@app.async_command(
    help="Leave a comment with the review (from latest code-review-report.txt) on the current GitHub PR, if environment is detected."
)
async def github_comment(
    token: str = typer.Option(
        os.environ.get("GITHUB_TOKEN", ""), help="GitHub token (or set GITHUB_TOKEN env var)"
    ),
    repo: str = typer.Option("", help="GitHub repo (owner/name, auto-detected if not provided)"),
    pr: int = typer.Option(0, help="GitHub PR number (auto-detected if not provided)"),
    file: str = typer.Option("code-review-report.txt", help="File to post as comment"),
):
    """
    Leaves a comment with the review on the current pull request.
    """
    import requests
    from ai_code_review.project_config import _detect_github_env

    if not token:
        print("GitHub token is required (--token or GITHUB_TOKEN env var).")
        raise typer.Exit(1)

    github_env = _detect_github_env()
    repo = repo or github_env.get("github_repo", "")
    pr_env_val = github_env.get("github_pr_number", "")
    parsed_pr = 0
    # Try to parse PR number robustly
    if not pr and pr_env_val:
        # e.g. could be "refs/pull/123/merge" or a direct number
        if "/" in pr_env_val and "pull" in pr_env_val:
            # refs/pull/123/merge
            try:
                pr_num_candidate = pr_env_val.strip("/").split("/")
                idx = pr_num_candidate.index("pull")
                parsed_pr = int(pr_num_candidate[idx + 1])
            except Exception:
                parsed_pr = 0
        else:
            try:
                parsed_pr = int(pr_env_val)
            except Exception:
                parsed_pr = 0
    pr = pr or parsed_pr

    if not repo:
        print("Unable to detect GitHub repo. Use --repo option.")
        raise typer.Exit(2)
    if not pr:
        print("Unable to detect GitHub PR number. Use --pr option.")
        raise typer.Exit(3)

    path = file
    if not os.path.exists(path):
        print(f"Review file not found: {path}")
        raise typer.Exit(4)

    with open(path, "r", encoding="utf-8") as f:
        body = f.read()

    api_url = f"https://api.github.com/repos/{repo}/issues/{pr}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    data = {"body": body}

    resp = requests.post(api_url, headers=headers, json=data)
    if 200 <= resp.status_code < 300:
        print(f"Posted review comment to PR #{pr} in {repo}")
    else:
        print(f"Failed to post comment: {resp.status_code} {resp.reason}\n{resp.text}")
        raise typer.Exit(5)
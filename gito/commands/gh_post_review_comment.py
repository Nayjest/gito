import logging
import os

import typer
from gito.bootstrap import app
from gito.constants import GITHUB_MD_REPORT_FILE_NAME
from gito.gh_api import post_gh_comment
from gito.project_config import ProjectConfig


@app.command(help="Leave a GitHub PR comment with the review.")
def github_comment(
    token: str = typer.Option(
        os.environ.get("GITHUB_TOKEN", ""), help="GitHub token (or set GITHUB_TOKEN env var)"
    ),
):
    """
    Leaves a comment with the review on the current GitHub pull request.
    """
    file = GITHUB_MD_REPORT_FILE_NAME
    if not os.path.exists(file):
        logging.error(f"Review file not found: {file}, comment will not be posted.")
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

    pr = None
    # e.g. could be "refs/pull/123/merge" or a direct number
    if "/" in pr_env_val and "pull" in pr_env_val:
        # refs/pull/123/merge
        try:
            pr_num_candidate = pr_env_val.strip("/").split("/")
            idx = pr_num_candidate.index("pull")
            pr = int(pr_num_candidate[idx + 1])
        except Exception:
            pass
    else:
        try:
            pr = int(pr_env_val)
        except ValueError:
            pass
    if not pr:
        if pr_str := os.getenv("PR_NUMBER_FROM_WORKFLOW_DISPATCH"):
            try:
                pr = int(pr_str)
            except ValueError:
                pass
    if not pr:
        logging.error("Could not resolve PR number from environment variables.")
        raise typer.Exit(3)

    if not post_gh_comment(repo, pr, token, body):
        raise typer.Exit(5)

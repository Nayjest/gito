import logging
import os

import requests
import typer
from gito.bootstrap import app
from gito.constants import GITHUB_MD_REPORT_FILE_NAME
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

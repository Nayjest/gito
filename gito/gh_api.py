import os
import logging

import requests
from ghapi.all import GhApi

from .constants import HTML_CR_COMMENT_MARKER


def resolve_gh_token(token_or_none):
    return token_or_none or os.getenv("GITHUB_TOKEN", None) or os.getenv("GH_TOKEN", None)


def post_gh_comment(
    gh_repository: str,  # e.g. "owner/repo"
    pr_or_issue_number: int,
    gh_token: str,
    text: str,
) -> bool:
    """
    Post a comment to a GitHub pull request or issue.
    Arguments:
        gh_repository (str): The GitHub repository in the format "owner/repo".
        pr_or_issue_number (int): The pull request or issue number.
        gh_token (str): GitHub personal access token with permissions to post comments.
        text (str): The comment text to post.
    Returns:
        True if the comment was posted successfully, False otherwise.
    """
    api_url = f"https://api.github.com/repos/{gh_repository}/issues/{pr_or_issue_number}/comments"
    headers = {
        "Authorization": f"token {gh_token}",
        "Accept": "application/vnd.github+json",
    }
    data = {"body": text}

    resp = requests.post(api_url, headers=headers, json=data)
    if 200 <= resp.status_code < 300:
        logging.info(f"Posted review comment to #{pr_or_issue_number} in {gh_repository}")
        return True
    else:
        logging.error(f"Failed to post comment: {resp.status_code} {resp.reason}\n{resp.text}")
        return False


def collapse_gh_outdated_cr_comments(
    gh_repository: str,
    pr_or_issue_number: int,
    token: str = None
):
    """
    Collapse outdated code review comments in a GitHub pull request or issue.
    """
    logging.info(f"Collapsing outdated comments in {gh_repository} #{pr_or_issue_number}...")

    token = resolve_gh_token(token)
    owner, repo = gh_repository.split('/')
    api = GhApi(owner, repo, token=token)

    comments = api.issues.list_comments(pr_or_issue_number)
    review_marker = HTML_CR_COMMENT_MARKER
    collapsed_title = "🗑️ <s>Outdated Code Review by Gito</s>"
    collapsed_marker = f"<summary>{collapsed_title}</summary>"
    outdated_comments = [
        c for c in comments
        if c.body and review_marker in c.body and collapsed_marker not in c.body
    ][:-1]
    if not outdated_comments:
        logging.info("No outdated comments found")
        return
    for comment in outdated_comments:
        logging.info(f"Collapsing comment {comment.id}...")
        new_body = f"<details>\n<summary>{collapsed_title}</summary>\n\n{comment.body}\n</details>"
        api.issues.update_comment(comment.id, new_body)
    logging.info("All outdated comments collapsed successfully.")

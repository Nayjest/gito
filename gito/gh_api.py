import logging

import requests


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

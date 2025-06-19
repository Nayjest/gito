import logging
import os

import git
from gito.issue_trackers import extract_issue_key, IssueTrackerIssue
from jira import JIRA


def fetch_issue(issue_key, jira_url, username, api_token):
    jira = JIRA(jira_url, basic_auth=(username, api_token))
    issue = jira.issue(issue_key)
    return IssueTrackerIssue(
        title=issue.fields.summary,
        description=issue.fields.description or "",
        url=f"{jira_url.rstrip('/')}/browse/{issue_key}"
    )

def fetch_associated_issue(
    repo: git.Repo,
    jira_url = None,
    jira_username= None,
    jira_api_token = None,
    **kwargs
):
    """
    Pipeline step to fetch a Jira issue based on the current branch name.
    """
    try:
        branch_name = repo.active_branch.name
    except TypeError:
        logging.error("Could not determine the active branch name. Can't fetch Jira issue.")
        return None

    if not (issue_key := extract_issue_key(branch_name)):
        logging.error(f"No Jira issue key found in branch name: {branch_name}")
        return None

    jira_url = jira_url or os.getenv("JIRA_URL")
    jira_username = jira_username or os.getenv("JIRA_USERNAME") or os.getenv("JIRA_EMAIL")
    jira_token = (
        jira_api_token
        or os.getenv("JIRA_API_TOKEN")
        or os.getenv("JIRA_API_KEY")
        or os.getenv("JIRA_TOKEN")
    )
    try:
        assert jira_url, "JIRA_URL is not set"
        assert jira_username, "JIRA_USERNAME is not set"
        assert jira_token, "JIRA_API_TOKEN is not set"
    except AssertionError as e:
        logging.error(f"Jira configuration error: {e}")
        return None
    return dict(
        associated_issue = fetch_issue(issue_key, jira_url, jira_username, jira_token)
    )

import logging
import os
import requests

import git

from gito.issue_trackers import IssueTrackerIssue, resolve_issue_key


def fetch_issue(issue_key, api_token) -> IssueTrackerIssue | None:
    """
    Fetch a Linear issue using GraphQL API.
    """
    try:
        url = "https://api.linear.app/graphql"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        # GraphQL query to fetch issue by identifier
        query = """
        query GetIssue($id: String!) {
            issue(id: $id) {
                id
                identifier
                title
                description
                url
            }
        }
        """

        response = requests.post(
            url,
            json={
                "query": query,
                "variables": {"id": issue_key}
            },
            headers=headers
        )
        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            logging.error(f"Linear API error: {data['errors']}")
            return None

        issue = data.get("data", {}).get("issue")
        if not issue:
            logging.error(f"Linear issue {issue_key} not found")
            return None

        return IssueTrackerIssue(
            title=issue["title"],
            description=issue.get("description") or "",
            url=issue["url"]
        )

    except requests.RequestException as e:
        logging.error(f"Failed to fetch Linear issue {issue_key}: {e}")
        return None
    except Exception as e:
        logging.error(f"Failed to fetch Linear issue {issue_key}: {e}")
        return None


def fetch_associated_issue(
    repo: git.Repo,
    linear_api_token=None,
    **kwargs
):
    """
    Pipeline step to fetch a Linear issue based on the current branch name.
    """
    linear_token = (
        linear_api_token
        or os.getenv("LINEAR_API_TOKEN")
        or os.getenv("LINEAR_TOKEN")
        or os.getenv("LINEAR_API_KEY")
    )
    if not linear_token:
        logging.error("LINEAR_API_TOKEN environment variable is not set")
        return

    issue_key = resolve_issue_key()
    return dict(
        associated_issue=fetch_issue(issue_key, jira_url, jira_username, jira_token)
    ) if issue_key else None
import logging
import os
import requests

import git

from gito.issue_trackers import IssueTrackerIssue, resolve_issue_key


def fetch_issue(issue_key, api_key) -> IssueTrackerIssue | None:
    """
    Fetch a Linear issue using GraphQL API.
    """
    try:
        url = "https://api.linear.app/graphql"
        headers = {
            "Authorization": f"Bearer {api_key}",
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
    api_key=None,
    **kwargs
):
    """
    Pipeline step to fetch a Linear issue based on the current branch name.
    """
    api_key = api_key or os.getenv("LINEAR_API_KEY")
    if not api_key:
        logging.error("LINEAR_API_KEY environment variable is not set")
        return

    issue_key = resolve_issue_key(repo)
    return dict(
        associated_issue=fetch_issue(issue_key, api_key)
    ) if issue_key else None

import re
from dataclasses import dataclass, field


def extract_issue_key(branch_name: str, min_len=2, max_len=10) -> str | None:
    pattern = fr"\b[A-Z][A-Z0-9]{{{min_len - 1},{max_len - 1}}}-\d+\b"
    match = re.search(pattern, branch_name)
    return match.group(0) if match else None


@dataclass
class IssueTrackerIssue:
    title: str = field(default="")
    description: str = field(default="")
    url: str = field(default="")

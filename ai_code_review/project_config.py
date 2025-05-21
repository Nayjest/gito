import logging
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import microcore as mc

from .constants import PROJECT_CONFIG_FILE, PROJECT_CONFIG_DEFAULTS_FILE


def _detect_github_env() -> dict:
    """
    Try to detect GitHub repository/PR info from environment variables (for GitHub Actions).
    Returns a dict with github_repo, github_pr_sha, github_pr_number, github_ref, etc.
    """
    import os

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    pr_sha = os.environ.get("GITHUB_SHA", "")
    pr_number = os.environ.get("GITHUB_REF", "")
    branch = ""
    ref = os.environ.get("GITHUB_REF", "")
    # Try to resolve PR head SHA if available. On PRs, GITHUB_HEAD_REF/BASE_REF contain branch names.
    if "GITHUB_HEAD_REF" in os.environ:
        branch = os.environ["GITHUB_HEAD_REF"]
    elif ref.startswith("refs/heads/"):
        branch = ref[len("refs/heads/") :]
    elif ref.startswith("refs/pull/"):
        # for pull_request events
        branch = ref

    d = {
        "github_repo": repo,
        "github_pr_sha": pr_sha,
        "github_pr_number": pr_number,
        "github_branch": branch,
        "github_ref": ref,
    }
    # Fallback for local usage: try to get from git
    if not repo:
        try:
            from git import Repo as GitRepo

            git = GitRepo(".", search_parent_directories=True)
            origin = git.remotes.origin.url
            # e.g. git@github.com:Nayjest/ai-code-review.git -> Nayjest/ai-code-review
            import re

            match = re.search(r"[:/]([\w\-]+)/([\w\-\.]+?)(\.git)?$", origin)
            if match:
                d["github_repo"] = f"{match.group(1)}/{match.group(2)}"
            d["github_pr_sha"] = git.head.commit.hexsha
            d["github_branch"] = (
                git.active_branch.name
                if hasattr(git, "active_branch")
                else ""
            )
        except Exception:
            pass
    # If branch is not a commit SHA, prefer branch for links
    if d["github_branch"]:
        d["github_pr_sha_or_branch"] = d["github_branch"]
    elif d["github_pr_sha"]:
        d["github_pr_sha_or_branch"] = d["github_pr_sha"]
    else:
        d["github_pr_sha_or_branch"] = "main"
    return d


@dataclass
class ProjectConfig:
    prompt: str = ""
    summary_prompt: str = ""
    report_template_md: str = ""
    """Markdown report template"""
    post_process: str = ""
    retries: int = 3
    """LLM retries for one request"""
    max_code_tokens: int = 32000
    prompt_vars: dict = field(default_factory=dict)

    @staticmethod
    def load(custom_config_file: str | Path | None = None) -> "ProjectConfig":
        config_file = Path(custom_config_file or PROJECT_CONFIG_FILE)
        with open(PROJECT_CONFIG_DEFAULTS_FILE, "rb") as f:
            config = tomllib.load(f)
        github_env = _detect_github_env()
        if config_file.exists():
            logging.info(
                f"Loading project-specific configuration from {mc.utils.file_link(config_file)}..."
            )
            default_prompt_vars = config.get("prompt_vars", {})
            with open(config_file, "rb") as f:
                loaded = tomllib.load(f)
            # safeguard: ensure key exists
            custom_prompt_vars = loaded.get("prompt_vars", {})
            config.update(loaded)
            # overriding prompt_vars config section will not empty default values
            config["prompt_vars"] = {**default_prompt_vars, **custom_prompt_vars, **github_env}
        else:
            logging.info(f"Config file {config_file} not found, using defaults")
            config["prompt_vars"] = {**config.get("prompt_vars", {}), **github_env}

        return ProjectConfig(**config)
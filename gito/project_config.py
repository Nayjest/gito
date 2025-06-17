import re
import logging
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import microcore as mc
from microcore import ui
from git import Repo

from .constants import PROJECT_CONFIG_BUNDLED_DEFAULTS_FILE, PROJECT_CONFIG_FILE_PATH


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
    # Try to resolve PR head SHA if available.
    # On PRs, GITHUB_HEAD_REF/BASE_REF contain branch names.
    if "GITHUB_HEAD_REF" in os.environ:
        branch = os.environ["GITHUB_HEAD_REF"]
    elif ref.startswith("refs/heads/"):
        branch = ref[len("refs/heads/"):]
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
        git_repo = None
        try:
            git_repo = Repo(".", search_parent_directories=True)
            origin = git_repo.remotes.origin.url
            # e.g. git@github.com:Nayjest/ai-code-review.git -> Nayjest/ai-code-review
            match = re.search(r"[:/]([\w\-]+)/([\w\-\.]+?)(\.git)?$", origin)
            if match:
                d["github_repo"] = f"{match.group(1)}/{match.group(2)}"
            d["github_pr_sha"] = git_repo.head.commit.hexsha
            d["github_branch"] = (
                git_repo.active_branch.name if hasattr(git_repo, "active_branch") else ""
            )
        except Exception:
            pass
        finally:
            if git_repo:
                try:
                    git_repo.close()
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
    report_template_cli: str = ""
    """Report template for CLI output"""
    post_process: str = ""
    retries: int = 3
    """LLM retries for one request"""
    max_code_tokens: int = 32000
    prompt_vars: dict = field(default_factory=dict)

    @staticmethod
    def _read_bundled_defaults() -> dict:
        with open(PROJECT_CONFIG_BUNDLED_DEFAULTS_FILE, "rb") as f:
            config = tomllib.load(f)
        return config

    @staticmethod
    def load_for_repo(repo: Repo):
        return ProjectConfig.load(Path(repo.working_tree_dir) / PROJECT_CONFIG_FILE_PATH)

    @staticmethod
    def load(config_path: str | Path | None = None) -> "ProjectConfig":
        config = ProjectConfig._read_bundled_defaults()
        github_env = _detect_github_env()
        config["prompt_vars"] |= github_env | dict(github_env=github_env)

        config_path = Path(config_path or PROJECT_CONFIG_FILE_PATH)
        if config_path.exists():
            logging.info(
                f"Loading project-specific configuration from {mc.utils.file_link(config_path)}...")
            default_prompt_vars = config["prompt_vars"]
            with open(config_path, "rb") as f:
                config.update(tomllib.load(f))
            # overriding prompt_vars config section will not empty default values
            config["prompt_vars"] = default_prompt_vars | config["prompt_vars"]
        else:
            logging.info(
                f"No project config found at {ui.blue(config_path)}, using defaults"
            )

        return ProjectConfig(**config)

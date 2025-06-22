import logging
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import microcore as mc
from gito.utils import detect_github_env
from microcore import ui
from git import Repo

from .constants import PROJECT_CONFIG_BUNDLED_DEFAULTS_FILE, PROJECT_CONFIG_FILE_PATH
from .pipeline import PipelineStep


@dataclass
class ProjectConfig:
    prompt: str = ""
    summary_prompt: str = ""
    answer_prompt: str = ""
    report_template_md: str = ""
    """Markdown report template"""
    report_template_cli: str = ""
    """Report template for CLI output"""
    post_process: str = ""
    retries: int = 3
    """LLM retries for one request"""
    max_code_tokens: int = 32000
    prompt_vars: dict = field(default_factory=dict)
    mention_triggers: list[str] = field(default_factory=list)
    answer_github_comments: bool = field(default=True)
    """
    Defines the keyword or mention tag that triggers bot actions
    when referenced in code review comments.
    """
    pipeline_steps: dict[str, dict | PipelineStep] = field(default_factory=dict)

    def __post_init__(self):
        self.pipeline_steps = {
            k: PipelineStep(**v) if isinstance(v, dict) else v
            for k, v in self.pipeline_steps.items()
        }

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
        github_env = detect_github_env()
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

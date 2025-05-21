import logging
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import microcore as mc

from .constants import PROJECT_CONFIG_FILE, PROJECT_CONFIG_DEFAULTS_FILE


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
        if config_file.exists():
            logging.info(
                f"Loading project-specific configuration from {mc.utils.file_link(config_file)}...")
            default_prompt_vars = config["prompt_vars"]
            with open(config_file, "rb") as f:
                config.update(tomllib.load(f))
            # overriding prompt_vars config section will not empty default values
            config["prompt_vars"] = default_prompt_vars | config["prompt_vars"]
        else:
            logging.info(f"Config file {config_file} not found, using defaults")

        return ProjectConfig(**config)

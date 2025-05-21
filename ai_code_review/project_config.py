import tomllib
from dataclasses import dataclass, field

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
    def load():
        with open(PROJECT_CONFIG_DEFAULTS_FILE, "rb") as f:
            config = tomllib.load(f)
        if PROJECT_CONFIG_FILE.exists():
            default_prompt_vars = config["prompt_vars"]
            with open(PROJECT_CONFIG_FILE, "rb") as f:
                config.update(tomllib.load(f))
            # overriding prompt_vars config section will not empty default values
            config["prompt_vars"] = default_prompt_vars | config["prompt_vars"]

        return ProjectConfig(**config)

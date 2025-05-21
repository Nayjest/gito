import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import StrEnum

import microcore as mc

from .constants import JSON_REPORT_FILE_NAME
from .project_config import ProjectConfig
from .utils import syntax_hint


@dataclass
class Issue:
    @dataclass
    class AffectedCode:
        start_line: int = field()
        end_line: int | None = field(default=None)
        file: str = field(default="")
        proposal: str = field(default="")
        affected_code: str = field(default="")

        @property
        def syntax_hint(self) -> str:
            return syntax_hint(self.file)

    id: str = field()
    title: str = field()
    details: str = field(default="")
    severity: int | None = field(default=None)
    confidence: int | None = field(default=None)
    tags: list[str] = field(default_factory=list)
    file: str = field(default="")
    affected_lines: list[AffectedCode] = field(default_factory=list)

    def __post_init__(self):
        self.affected_lines = [
            Issue.AffectedCode(**dict(file=self.file) | i)
            for i in self.affected_lines
        ]


@dataclass
class Report:
    class Format(StrEnum):
        MARKDOWN = "md"

    issues: dict = field(default_factory=dict)
    summary: str = field(default="")
    total_issues: int = field(init=False)
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    model: str = field(default_factory=lambda: mc.config().MODEL)

    @property
    def plain_issues(self):
        return [
            issue
            for file, issues in self.issues.items()
            for issue in issues
        ]

    def __post_init__(self):
        issue_id: int = 0
        for file in self.issues.keys():
            self.issues[file] = [
                Issue(
                    **{
                        "id": (issue_id := issue_id + 1),
                        "file": file,
                    } | issue
                )
                for issue in self.issues[file]
            ]
        self.total_issues = issue_id

    def save(self, file_name: str = ""):
        file_name = file_name or JSON_REPORT_FILE_NAME
        with open(file_name, "w") as f:
            json.dump(asdict(self), f, indent=4)
        logging.info(f"Report saved to {mc.utils.file_link(file_name)}")

    @staticmethod
    def load(file_name: str = ""):
        with open(file_name or JSON_REPORT_FILE_NAME, "r") as f:
            data = json.load(f)
        data.pop("total_issues", None)
        return Report(**data)

    def render(
        self, cfg: ProjectConfig = None, format: Format = Format.MARKDOWN
    ) -> str:
        cfg = cfg or ProjectConfig.load()
        template = getattr(cfg, f"report_template_{format}")
        return mc.prompt(template, report=self, **cfg.prompt_vars)

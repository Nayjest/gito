import json
import logging
from enum import StrEnum
from dataclasses import dataclass, field
import microcore as mc
from git import Repo

from unidiff.constants import DEV_NULL

from .project_config import ProjectConfig
from .core_functions import get_diff, filter_diff
from .constants import JSON_REPORT_FILE_NAME


def file_lines(repo: Repo, file: str, max_tokens: int = None) -> str:
    text = repo.tree()[file].data_stream.read().decode()
    lines = [f"{i + 1}: {line}\n" for i, line in enumerate(text.splitlines())]
    if max_tokens:
        lines, removed_qty = mc.tokenizing.fit_to_token_size(lines, max_tokens)
        if removed_qty:
            lines.append(
                f"(!) DISPLAYING ONLY FIRST {len(lines)} LINES DUE TO LARGE FILE SIZE\n"
            )
    return ''.join(lines)


class ReportFormat(StrEnum):
    MARKDOWN = "md"


@dataclass
class Report:
    class Format(StrEnum):
        MARKDOWN = "md"

    issues: dict
    summary: str
    total_issues: int = field(init=False)

    @property
    def plain_issues(self):
        issue_id: int = 0
        return [
            {
                "file": file,
                **issue,
            }
            for file, issues in self.issues.items()
            for issue in issues
        ]

    def __post_init__(self):
        issue_id: int = 0
        for file, file_issues in self.issues.items():
            for i in file_issues:
                issue_id += 1
                i["id"] = issue_id
        self.total_issues = issue_id

    def save(self, file_name: str = ""):
        file_name = file_name or JSON_REPORT_FILE_NAME
        json.dump(self, open(file_name, "w"), indent=4)
        logging.info(f"Report saved to {mc.utils.file_link(file_name)}")

    @staticmethod
    def load(file_name: str = ""):
        data = json.load(open(file_name or JSON_REPORT_FILE_NAME, "r"))
        data.pop("total_issues", None)
        return Report(**data)

    def render(self, cfg: ProjectConfig = None, format: Format = Format.MARKDOWN) -> str:
        cfg = cfg or ProjectConfig.load()
        template = getattr(cfg, f"report_template_{format}")
        return mc.prompt(template, report=self, **cfg.prompt_vars)


async def review(filter: str = ""):
    cfg = ProjectConfig.load()
    repo = Repo('.')
    diff = get_diff(repo=repo, against='HEAD')
    diff = filter_diff(diff, filter)
    if not diff:
        logging.error("Nothing to review")
        return
    lines = {
        file_diff.path: file_lines(
            repo,
            file_diff.path,
            cfg.max_code_tokens - mc.tokenizing.num_tokens_from_string(str(file_diff))
        ) if file_diff.target_file != DEV_NULL else ""
        for file_diff in diff
    }
    responses = await mc.llm_parallel(
        [
            mc.prompt(
                cfg.prompt,
                input=file_diff,
                file_lines=lines[file_diff.path],
                **cfg.prompt_vars
            )
            for file_diff in diff
        ],
        retries=cfg.retries,
        parse_json=True
    )
    issues = {file.path: issues for file, issues in zip(diff, responses) if issues}
    for file, file_issues in issues.items():
        for issue in file_issues:
            for i in issue.get("affected_lines", []):
                if lines[file]:
                    f_lines = lines[file].splitlines()
                    i["affected_code"] = '\n'.join(f_lines[i["start_line"] - 1:i["end_line"] - 1])
    exec(cfg.post_process, {"mc": mc, **locals()})
    summary = mc.prompt(
        cfg.summary_prompt,
        diff=mc.tokenizing.fit_to_token_size(diff, cfg.max_code_tokens)[0],
        issues=issues,
        **cfg.prompt_vars
    ).to_llm() if cfg.summary_prompt else ""
    report = Report(
        issues=issues,
        summary=summary
    )
    report.save()
    report_text = report.render(cfg, Report.Format.MARKDOWN)
    print(mc.ui.yellow(report_text))
    open("code-review-report.txt", "w", encoding="utf-8").write(report_text)

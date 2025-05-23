import fnmatch
import logging
from typing import Iterable

import microcore as mc
from git import Repo
from unidiff import PatchSet, PatchedFile
from unidiff.constants import DEV_NULL

from .project_config import ProjectConfig
from .report_struct import Report


def get_diff(repo: Repo = None, against: str = "HEAD") -> PatchSet | list[PatchedFile]:
    repo = repo or Repo(".")
    base = repo.remotes.origin.refs.HEAD.reference.name
    logging.info(f"{base}...{against}")
    diff_content = repo.git.diff(base, against)
    diff = PatchSet.from_string(diff_content)
    return diff


def filter_diff(
    patch_set: PatchSet | Iterable[PatchedFile], filters: str | list[str]
) -> PatchSet | Iterable[PatchedFile]:
    """
    Filter the diff files by the given fnmatch filters.
    """
    print([f.path for f in patch_set])
    assert isinstance(filters, (list, str))
    if not isinstance(filters, list):
        filters = [f.strip() for f in filters.split(",") if f.strip()]
    if not filters:
        return patch_set
    files = [
        file
        for file in patch_set
        if any(fnmatch.fnmatch(file.path, pattern) for pattern in filters)
    ]
    print([f.path for f in files])
    return files


def file_lines(repo: Repo, file: str, max_tokens: int = None) -> str:
    text = repo.tree()[file].data_stream.read().decode()
    lines = [f"{i + 1}: {line}\n" for i, line in enumerate(text.splitlines())]
    if max_tokens:
        lines, removed_qty = mc.tokenizing.fit_to_token_size(lines, max_tokens)
        if removed_qty:
            lines.append(
                f"(!) DISPLAYING ONLY FIRST {len(lines)} LINES DUE TO LARGE FILE SIZE\n"
            )
    return "".join(lines)


def make_cr_summary(cfg: ProjectConfig, report: Report, diff):
    return mc.prompt(
        cfg.summary_prompt,
        diff=mc.tokenizing.fit_to_token_size(diff, cfg.max_code_tokens)[0],
        issues=report.issues,
        **cfg.prompt_vars,
    ).to_llm() if cfg.summary_prompt else ""


async def review(filters: str | list[str] = ""):
    cfg = ProjectConfig.load()
    repo = Repo(".")
    diff = get_diff(repo=repo, against="HEAD")
    diff = filter_diff(diff, filters)
    if not diff:
        logging.error("Nothing to review")
        return
    lines = {
        file_diff.path: (
            file_lines(
                repo,
                file_diff.path
                cfg.max_code_tokens
                - mc.tokenizing.num_tokens_from_string(str(file_diff)),
            )
            if file_diff.target_file != DEV_NULL
            else ""
        )
        for file_diff in diff
    }
    responses = await mc.llm_parallel(
        [
            mc.prompt(
                cfg.prompt,
                input=file_diff,
                file_lines=lines[file_diff.path],
                **cfg.prompt_vars,
            )
            for file_diff in diff
        ],
        retries=cfg.retries,
        parse_json=True,
    )
    issues = {file.path: issues for file, issues in zip(diff, responses) if issues}
    for file, file_issues in issues.items():
        for issue in file_issues:
            for i in issue.get("affected_lines", []):
                if lines[file]:
                    f_lines = [""] + lines[file].splitlines()
                    i["affected_code"] = "\n".join(
                        f_lines[i["start_line"]: i["end_line"]+1]
                    )
    exec(cfg.post_process, {"mc": mc, **locals()})
    report = Report(issues=issues, number_of_processed_files=len(diff))
    report.summary = make_cr_summary(cfg, report, diff)
    report.save()
    report_text = report.render(cfg, Report.Format.MARKDOWN)
    print(mc.ui.yellow(report_text))
    open("code-review-report.txt", "w", encoding="utf-8").write(report_text)

import asyncio
import tomllib
from dataclasses import dataclass, field

from git import Repo
from unidiff import PatchSet
from pathlib import Path
import microcore as mc

mc.configure(
    DOT_ENV_FILE=Path("~/.env.ai-code-review").expanduser(),  # for usage as local cli
    VALIDATE_CONFIG=False,
    USE_LOGGING=True,
)


@dataclass
class ProjectCodeReviewConfig:
    prompt: str = ""
    summary_prompt: str = ""
    report: str = ""
    post_process: str = ""
    retries: int = 3
    max_code_tokens: int = 32000
    prompt_vars: dict = field(default_factory=dict)

    @staticmethod
    def load():
        fn = ".ai-code-review.toml"
        return ProjectCodeReviewConfig(**{
            **tomllib.load(open(Path(__file__).resolve().parent / fn, "rb")),
            **(tomllib.load(open(fn, "rb")) if Path(fn).exists() else {}),
        })


async def main():
    cfg = ProjectCodeReviewConfig.load()
    repo = Repo('.')
    diff_content = repo.git.diff(repo.remotes.origin.refs.HEAD.reference.name, 'HEAD')
    diff = PatchSet.from_string(diff_content)
    responses = await mc.llm_parallel(
        [mc.prompt(cfg.prompt, input=file, **cfg.prompt_vars) for file in diff],
        retries=cfg.retries,
        parse_json=True
    )
    issues = {file.path: issues for file, issues in zip(diff, responses) if issues}
    exec(cfg.post_process, {"mc": mc, **locals()})
    summary = mc.prompt(
        cfg.summary_prompt,
        diff=mc.tokenizing.fit_to_token_size(diff, cfg.max_code_tokens),
        issues=issues,
        **cfg.prompt_vars
    ).to_llm() if cfg.summary_prompt else ""
    report_text = mc.prompt(cfg.report, issues=issues, summary=summary)
    print(mc.ui.yellow(report_text))
    open("code-review-report.txt", "w", encoding="utf-8").write(report_text)


if __name__ == "__main__":
    asyncio.run(main())

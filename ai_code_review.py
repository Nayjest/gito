import asyncio
import tomllib
from dataclasses import dataclass

from git import Repo
from unidiff import PatchSet
from pathlib import Path
from microcore import storage, configure, prompt, llm_parallel

configure(
    DOT_ENV_FILE=Path("~/.env.ai-code-review").expanduser(),  # for usage as local cli
    PROMPT_TEMPLATES_PATH=(CR_APP_ROOT := Path(__file__).resolve().parent),
    STORAGE_PATH=CR_APP_ROOT / "storage",
    EMBEDDING_DB_TYPE="",
    USE_LOGGING=True,
)


@dataclass
class ProjectCodeReviewConfig:
    prompt: str = ""
    report: str = ""
    post_process: str = ""
    retries: int = 3

    @staticmethod
    def load():
        fn = ".ai-code-review.toml"
        return ProjectCodeReviewConfig(**{
            **tomllib.load(open(CR_APP_ROOT / fn, "rb")),
            **(tomllib.load(open(fn, "rb")) if Path(fn).exists() else {}),
        })


async def main():
    config = ProjectCodeReviewConfig.load()
    repo = Repo('.')
    diff_content = repo.git.diff(repo.remotes.origin.refs.HEAD.reference.name, 'HEAD')
    diff = PatchSet.from_string(diff_content)
    responses = await llm_parallel(
        [prompt(config.prompt, input=file) for file in diff],
        retries=config.retries,
        parse_json=True
    )
    issues = {file.path: issues for file, issues in zip(diff, responses) if issues}
    exec(config.post_process, {**globals(), **locals()})
    storage.write_json("code_review.json", {"issues": issues})
    report_text = prompt(config.report, issues=issues)
    print(report_text)


if __name__ == "__main__":
    asyncio.run(main())

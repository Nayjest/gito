import sys
import os
from pathlib import Path
import typer


_EXT_TO_HINT: dict[str, str] = {
    # scripting & languages
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".rb": "ruby",
    ".go": "go",
    ".rs": "rust",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".dart": "dart",
    ".php": "php",
    ".pl": "perl",
    ".pm": "perl",
    ".lua": "lua",
    # web & markup
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".less": "less",
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".csv": "csv",
    ".md": "markdown",
    ".rst": "rest",
    # shell & config
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    ".fish": "bash",
    ".ps1": "powershell",
    ".dockerfile": "dockerfile",
    # build & CI
    ".makefile": "makefile",
    ".mk": "makefile",
    "CMakeLists.txt": "cmake",
    "Dockerfile": "dockerfile",
    ".gradle": "groovy",
    ".travis.yml": "yaml",
    # data & queries
    ".sql": "sql",
    ".graphql": "graphql",
    ".proto": "protobuf",
    ".yara": "yara",
}


def syntax_hint(file_path: str | Path) -> str:
    """
    Returns a syntax highlighting hint based on the file's extension or name.

    This can be used to annotate code blocks for rendering with syntax highlighting,
    e.g., using Markdown-style code blocks: ```<syntax_hint>\n<code>\n```.

    Args:
      file_path (str | Path): Path to the file.

    Returns:
      str: A syntax identifier suitable for code highlighting (e.g., 'python', 'json').
    """
    p = Path(file_path)
    ext = p.suffix.lower()
    if not ext:
        name = p.name.lower()
        if name == "dockerfile":
            return "dockerfile"
        return ""
    return _EXT_TO_HINT.get(ext, ext.lstrip("."))


def is_running_in_github_action():
    return os.getenv("GITHUB_ACTIONS") == "true"


def no_subcommand(app: typer.Typer) -> bool:
    """
    Checks if the current script is being invoked as a command in a target Typer application.
    """
    return not (
        (first_arg := next((a for a in sys.argv[1:] if not a.startswith('-')), None))
        and first_arg in (
            cmd.name or cmd.callback.__name__.replace('_', '-')
            for cmd in app.registered_commands
        )
        or '--help' in sys.argv
    )


def parse_refs_pair(refs: str) -> tuple[str | None, str | None]:
    SEPARATOR = '..'
    if not refs:
        return None, None
    if SEPARATOR not in refs:
        return refs, None
    what, against = refs.split(SEPARATOR, 1)
    return what or None, against or None


def max_line_len(text: str) -> int:
    return max((len(line) for line in text.splitlines()), default=0)


def block_wrap_lr(text: str, left: str = "", right: str = "", max_rwrap: int = 60) -> str:
    ml = max_line_len(text)
    lines = text.splitlines()
    wrapped_lines = []
    for line in lines:
        ln = left+line
        if ml <= max_rwrap:
            ln += ' ' * (ml - len(line)) + right
        wrapped_lines.append(ln)
    return "\n".join(wrapped_lines)

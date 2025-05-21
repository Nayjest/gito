from pathlib import Path

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


def syntax_hint(file_name: str) -> str:
    """
    Get the syntax hint for a file based on its extension.
    """
    p = Path(file_name)
    ext = p.suffix.lower()
    if not ext:
        name = p.name.lower()
        if name == "dockerfile":
            return "dockerfile"
        return ""
    return _EXT_TO_HINT.get(ext, ext.lstrip("."))

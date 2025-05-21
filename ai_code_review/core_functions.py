import fnmatch
from typing import Iterable

from git import Repo
from unidiff import PatchSet, PatchedFile


def get_diff(repo: Repo = None, against: str = "HEAD") -> PatchSet | list[PatchedFile]:
    repo = repo or Repo(".")
    diff_content = repo.git.diff(repo.remotes.origin.refs.HEAD.reference.name, against)
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

"""
Make code review of changes using GPT-4 (any programming language):

Usage:

1. Make patch file
Examples:
git diff master..feature-branch > feature.patch
git diff main -- '*.py'> storage/feature.patch

2. Run this app:
python app.py <full-path-to-patch-file>

"""

import json
import sys
from pathlib import Path
from colorama import Fore as C
from microcore import tpl, storage, configure
from microcore import llm

CR_APP_ROOT = Path(__file__).resolve().parent
configure(
    PROMPT_TEMPLATES_PATH=CR_APP_ROOT,
    STORAGE_PATH=CR_APP_ROOT / "storage",
    USE_LOGGING=True,
    LLM_DEFAULT_ARGS={"temperature": 0.05},
)

diff_file_name = sys.argv[1] if sys.argv[1:] else "feature.patch"

max_files_to_review = 10
skip_first_n = 0
skip_files = []


def split_diff_by_files(file_name: str) -> list[str]:
    parts = ("\n" + storage.read(file_name)).split("\ndiff --git")[1:]
    return ["diff --git" + i for i in parts]


diff_by_files = split_diff_by_files(diff_file_name)
for diff_part in diff_by_files[skip_first_n : skip_first_n + max_files_to_review]:
    first_line = diff_part.split("\n")[0].replace("diff --git", "").strip()

    if len(first_line) == 0 or any(s in first_line for s in skip_files):
        continue

    a, b = first_line.split(" ")
    fn = b.replace("b/", "") + ".txt"
    print(C.LIGHTYELLOW_EX + fn)
    out = llm(tpl("cr-prompt.j2", input=diff_part))
    if len(out.strip()) < 10:
        continue
    try:
        lines = json.loads(out)
        out = "\nISS: " + "\nISS:".join(lines)
    except json.decoder.JSONDecodeError:
        pass
    storage.write("out/" + fn, out)
print("Done")
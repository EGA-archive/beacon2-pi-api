import re
import sys
import tokenize
from pathlib import Path

from spellchecker import SpellChecker

target_dir = Path(sys.argv[1])

spell = SpellChecker(language="en")

ALLOWED_WORDS = {
    "json",
    "yaml",
    "api",
    "uuid",
    "metadata",
    "config",
    "configs",
    "dataset",
    "datasets",
    "enum",
    "enums",
}

language_exceptions = []

for py_file in target_dir.rglob("*.py"):
    with open(py_file, "rb") as f:
        for token in tokenize.tokenize(f.readline):
            if token.type != tokenize.COMMENT:
                continue

            text = token.string.lstrip("#").strip()

            words = [
                w.lower()
                for w in re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)?", text)
            ]

            if len(words) < 3:
                continue

            unknown = [
                w
                for w in words
                if w not in ALLOWED_WORDS
                and w not in spell
            ]

            if len(unknown) > len(words) / 2:
                language_exceptions.append(
                    f"file: {py_file} at line {token.start[0]} "
                    f"may contain non-English comment: {text}"
                )

if language_exceptions:
    print("WARNING! Potentially non-English comments found:")
    print("\n".join(language_exceptions))
else:
    print("SUCCESS! All comments appear to be English.")
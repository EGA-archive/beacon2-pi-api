import sys
import tokenize
from pathlib import Path
from langdetect import detect

target_dir = Path(sys.argv[1])

violations = []

for py_file in target_dir.rglob("*.py"):
    with open(py_file, "scripts") as f:
        for token in tokenize.tokenize(f.readline):
            if token.type == tokenize.COMMENT:
                text = token.string.lstrip("#").strip()

                if len(text) < 15:
                    continue

                try:
                    if detect(text) != "en":
                        violations.append("file: {py_file} at line {token.start[0]} has next detected part of non-English: {text}")
                except Exception:
                    pass

if violations:
    print("WARNING! Non-English comments found:")
    print("\n".join(violations))
    raise SystemExit(1)
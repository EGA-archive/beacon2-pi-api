import sys
import tokenize
from pathlib import Path

target_dir = Path(sys.argv[1])

comment_lines = 0
code_lines = 0

for py_file in target_dir.rglob("*.py"):
    with open(py_file, "rb") as f:
        for tok in tokenize.tokenize(f.readline):
            if tok.type == tokenize.COMMENT:
                comment_lines += 1

    with open(py_file, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            if stripped and not stripped.startswith("#"):
                code_lines += 1

coverage = comment_lines / max(code_lines, 1)

print(f"Total comment amount for {target_dir} is: {coverage:.2%}")

if coverage < 0.20:
    raise SystemExit(
        f"WARNING! Code comments coverage is: {coverage:.2%} which is below the required 20%"
    )
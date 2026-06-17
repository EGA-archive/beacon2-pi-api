import sys
import tokenize
from pathlib import Path
from langdetect import detect

target_dir = Path(sys.argv[1])

language_exceptions = []

for py_file in target_dir.rglob("*.py"):
    with open(py_file, "rb") as f:
        for token in tokenize.tokenize(f.readline):
            if token.type == tokenize.COMMENT:
                text = token.string.lstrip("#").strip()

                if len(text) < 15:
                    continue

                try:
                    if "en" not in detect(text):
                        lang_exception = "file: {} at line {} has next detected part of non-English: {}. Text is in language: {}".format(py_file, token.start[0], text, detect(text))
                        splitted_le = lang_exception.split("language:")
                        if "en" not in splitted_le[1]:
                            language_exceptions.append(lang_exception)
                except Exception:
                    pass

if language_exceptions:
    print("WARNING! Non-English comments found:")
    print("\n".join(language_exceptions))
    raise SystemExit(1)
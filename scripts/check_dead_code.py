import subprocess
import sys
from pathlib import Path

TARGET_DIR = Path(sys.argv[1])

MIN_CONFIDENCE = 80

result = subprocess.run(
    [
        "vulture",
        str(TARGET_DIR),
        "--min-confidence",
        str(MIN_CONFIDENCE),
    ],
    capture_output=True,
    text=True,
)




stdout_splitted = result.stdout.splitlines()
list_without_validators=[]
for stdout_item in stdout_splitted:
    if '/validator/' not in stdout_item:
        list_without_validators.append(stdout_item)

if list_without_validators == []:
    print("SUCCESS: No dead code detected.")
    sys.exit(0)
else:
    finalstr=""
    for final_item in list_without_validators:
        finalstr+=final_item+"\n"
    print("WARNING: Potential dead code found:\n")
    print(finalstr)

    sys.exit(0)
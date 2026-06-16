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

if result.returncode == 0:
    print("SUCCESS: No dead code detected.")
    sys.exit(0)

print("WARNING: Potential dead code found:\n")
print(result.stdout)

sys.exit(1)
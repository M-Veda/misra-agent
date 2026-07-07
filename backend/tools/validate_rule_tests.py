from pathlib import Path
import json
import subprocess
import sys
import re

ROOT = Path("backend/tests/rules")

CLI = Path("backend/cli.py")

for folder in sorted(ROOT.iterdir()):

    if not folder.is_dir():
        continue

    expected = json.loads((folder / "expected.json").read_text())

    for test in ("bad.c", "good.c"):

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                str(folder / test),
                "--rule",
                expected["rule"],
            ],
            capture_output=True,
            text=True,
        )

        output = result.stdout + result.stderr

        match = re.search(
            r"Violations\s*:\s*(\d+)",
            output,
        )

        violations = int(match.group(1)) if match else -1

        print(
            f"{folder.name:15} {test:6} -> {violations}"
        )
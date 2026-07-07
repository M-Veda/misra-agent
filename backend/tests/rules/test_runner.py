from pathlib import Path
import json
import subprocess
import sys
import re

ROOT = Path(__file__).parent
CLI = Path(__file__).parents[2] / "cli.py"

total = 0
passed = 0
failed = 0
errors = 0

print("=" * 70)
print("MISRA C:2012 REGRESSION TEST SUITE")
print("=" * 70)

for folder in sorted(ROOT.iterdir()):

    if not folder.is_dir():
        continue

    expected_file = folder / "expected.json"
    bad_file = folder / "bad.c"

    if not expected_file.exists() or not bad_file.exists():
        continue

    expected = json.loads(expected_file.read_text())
    expected_count = expected["violations"]

    result = subprocess.run(
    [
        sys.executable,
        str(CLI),
        str(bad_file),
        "--rule",
        expected["rule"],
    ],
    capture_output=True,
    text=True,
)

    output = result.stdout + "\n" + result.stderr

    match = re.search(
        r"Violations\s*:\s*(\d+)",
        output,
        re.IGNORECASE,
    )

    total += 1

    if result.returncode != 0:

        errors += 1

        print(f"[ERROR] {folder.name}")
        print(output)
        print("-" * 70)

        continue

    if match is None:

        errors += 1

        print(f"[ERROR] {folder.name}")
        print("Couldn't parse violation count.")
        print(output)
        print("-" * 70)

        continue

    actual = int(match.group(1))

    if actual == expected_count:

        passed += 1

        print(f"[PASS] {folder.name}")

    else:

        failed += 1

        print(f"[FAIL] {folder.name}")
        print(f"Expected : {expected_count}")
        print(f"Actual   : {actual}")
        print("-" * 70)

print()
print("=" * 70)
print("FAILED RULES")
print("=" * 70)

for folder in sorted(ROOT.iterdir()):

    if not folder.is_dir():
        continue

    expected = json.loads(
        (folder / "expected.json").read_text()
    )

    bad_file = folder / "bad.c"

    result = subprocess.run(
        [
            sys.executable,
            str(CLI),
            str(bad_file),
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

    actual = int(match.group(1)) if match else -1

    if actual != expected["violations"]:
        print(
            f"{expected['rule']}  Expected={expected['violations']}  Actual={actual}"
        )

print()
print("=" * 70)
print(f"TOTAL  : {total}")
print(f"PASSED : {passed}")
print(f"FAILED : {failed}")
print(f"ERRORS : {errors}")
print("=" * 70)
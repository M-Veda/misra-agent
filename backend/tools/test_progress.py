from pathlib import Path
import json

ROOT = Path("backend/tests/rules")

rows = []

for folder in sorted(ROOT.iterdir()):

    if not folder.is_dir():
        continue

    expected = json.loads(
        (folder / "expected.json").read_text()
    )

    bad = (folder / "bad.c").read_text().strip()
    good = (folder / "good.c").read_text().strip()

    status = (
        "READY"
        if bad != good
        else "PLACEHOLDER"
    )

    rows.append(
        (
            expected["rule"],
            status,
        )
    )

ready = sum(
    status == "READY"
    for _, status in rows
)

placeholder = sum(
    status == "PLACEHOLDER"
    for _, status in rows
)

print("=" * 55)
print("MISRA RULE TEST PROGRESS")
print("=" * 55)

for rule, status in rows:
    print(f"{rule:6} {status}")

print("=" * 55)
print(f"READY       : {ready}")
print(f"PLACEHOLDER : {placeholder}")
print("=" * 55)
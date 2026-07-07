from pathlib import Path
import json

ROOT = Path("backend/tests/rules")

total = 0
implemented = 0

for folder in sorted(ROOT.iterdir()):

    if not folder.is_dir():
        continue

    total += 1

    expected = json.loads(
        (folder / "expected.json").read_text()
    )

    if (
        (folder / "bad.c").read_text().strip()
        !=
        (folder / "good.c").read_text().strip()
    ):
        implemented += 1

print(f"Total rule folders : {total}")
print(f"Implemented tests  : {implemented}")
print(f"Remaining          : {total - implemented}")
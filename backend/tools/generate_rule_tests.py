from pathlib import Path
import json

from rule_templates import RULE_TESTS

ROOT = Path("backend/tests/rules")

for rule, data in RULE_TESTS.items():

    folder = ROOT / f"rule_{rule.replace('.', '_')}"
    folder.mkdir(parents=True, exist_ok=True)

    (folder / "bad.c").write_text(
        data["bad"].strip() + "\n"
    )

    (folder / "good.c").write_text(
        data["good"].strip() + "\n"
    )

    (folder / "expected.json").write_text(
        json.dumps(
            {
                "rule": rule,
                "violations": data["violations"],
            },
            indent=4,
        )
    )

print(f"Generated {len(RULE_TESTS)} rule test suites.")
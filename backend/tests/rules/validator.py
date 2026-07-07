import json
from pathlib import Path


class RuleValidator:
    """
    Validates analyzer output against
    expected.json.
    """

    def validate(
        self,
        expected_file,
        violations,
    ):

        expected = json.loads(
            Path(expected_file).read_text(
                encoding="utf-8"
            )
        )

        expected_count = expected.get(
            "violations",
            0,
        )

        actual_count = len(violations)

        return {
            "passed":
                expected_count == actual_count,
            "expected":
                expected_count,
            "actual":
                actual_count,
            "rule":
                expected.get("rule"),
        }
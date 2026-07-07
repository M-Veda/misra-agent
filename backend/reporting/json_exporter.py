import json
from pathlib import Path


class JSONExporter:
    """
    Exports analysis results to JSON.
    """

    def export(
        self,
        violations,
        execution_summary,
        output_file,
    ):

        data = {
            "summary": execution_summary,
            "violations": [
                violation.to_dict()
                for violation in violations
            ],
        }

        Path(output_file).write_text(
            json.dumps(
                data,
                indent=4,
            ),
            encoding="utf-8",
        )
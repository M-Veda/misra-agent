import json
from pathlib import Path

from config.settings import REPORT_DIR, ensure_runtime_directories


def generate_report(report_data, report_path=None):
    ensure_runtime_directories()

    if report_path is None:
        session_id = report_data.get("session_id", "session")
        report_path = REPORT_DIR / f"{session_id}_compliance_report.json"
    else:
        report_path = Path(report_path)

    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=4)

    return {
        "tool": "report_generator",
        "status": "Report Generated",
        "path": str(report_path),
        "report": report_data,
    }

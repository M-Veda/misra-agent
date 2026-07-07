import json
from datetime import datetime
from pathlib import Path

from config.settings import REPORT_DIR, ensure_runtime_directories


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _grade(score):
    if score >= 95:
        return "A+"
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "FAIL"


def _summary(report):
    analysis = report.get("analysis_summary", {})
    patches = report.get("patch_statistics", {})
    score = report.get("final_score", {}).get("score", 0)

    return {
        "overall_status": (
            "PASS"
            if score >= 80
            else "FAIL"
        ),
        "grade": _grade(score),
        "score": score,
        "violations_found": analysis.get(
            "total_violations",
            0,
        ),
        "violations_reviewed": analysis.get(
            "reviewed",
            0,
        ),
        "accepted_fixes": analysis.get(
            "accepted",
            0,
        ),
        "rejected_fixes": analysis.get(
            "rejected",
            0,
        ),
        "skipped_fixes": analysis.get(
            "skipped",
            0,
        ),
        "patches_applied": patches.get(
            "applied",
            0,
        ),
        "conflicted_patches": patches.get(
            "conflicted",
            0,
        ),
    }


def generate_report(report_data, report_path=None):
    ensure_runtime_directories()

    session = report_data.get(
        "session_info",
        {}
    )

    if report_path is None:
        session_id = session.get(
            "session_id",
            "session",
        )
        report_path = (
            REPORT_DIR
            / f"{session_id}_compliance_report.json"
        )
    else:
        report_path = Path(report_path)

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    final_report = {
        "metadata": {
            "tool": "MISRA AI Agent",
            "generated_at": _now(),
            "version": "2.0",
            "format": "JSON",
        },
        **report_data,
        "summary": _summary(report_data),
    }

    with report_path.open(
        "w",
        encoding="utf-8",
    ) as fp:
        json.dump(
            final_report,
            fp,
            indent=4,
            ensure_ascii=False,
        )

    return {
        "tool": "report_generator",
        "status": "Report Generated",
        "path": str(report_path),
        "report": final_report,
    }
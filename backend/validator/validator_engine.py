from datetime import datetime
from pathlib import Path

from analyzer.cppcheck_runner import run_cppcheck_analysis
from utils.logger import logger


def _normalize_report(result):
    """
    Supports both:
        - str
        - dict returned by cppcheck runner
    """

    if isinstance(result, dict):
        return {
            "report": result.get("report", ""),
            "issues": result.get("issues", []),
            "metadata": result.get("metadata", {}),
            "summary": result.get("summary", {}),
        }

    report = str(result)

    return {
        "report": report,
        "issues": [
            line.strip()
            for line in report.splitlines()
            if line.strip()
        ],
        "metadata": {},
        "summary": {},
    }


def run_validation(file_path):
    """
    Final validation stage.

    Responsibilities
    ----------------
    • Execute Cppcheck validation
    • Normalize validator output
    • Produce dashboard-ready statistics
    • Return rich validation result
    """

    started = datetime.now()

    logger.info(
        "Validation started: %s",
        file_path,
    )

    raw_result = run_cppcheck_analysis(file_path)

    normalized = _normalize_report(raw_result)

    issues = normalized["issues"]

    validation = {
        "is_valid": len(issues) == 0,
        "report": normalized["report"],
        "issues": issues,
        "metadata": {
            "validated_at": started.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "validator": "Cppcheck",
            "file": Path(file_path).name,
        },
        "summary": {
            "total_issues": len(issues),
            "passed": len(issues) == 0,
        },
        "dashboard": {
            "status": (
                "PASSED"
                if len(issues) == 0
                else "FAILED"
            ),
            "issue_count": len(issues),
        },
    }

    if normalized["summary"]:
        validation["summary"].update(
            normalized["summary"]
        )

    if normalized["metadata"]:
        validation["metadata"].update(
            normalized["metadata"]
        )

    logger.info(
        "Validation completed (%d issues).",
        len(issues),
    )

    return validation
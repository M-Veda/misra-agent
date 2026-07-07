from pathlib import Path
from datetime import datetime

from analyzer.cppcheck_runner import run_cppcheck_analysis


class CppcheckService:
    """
    Service wrapper around the Cppcheck analysis engine.

    Responsibilities
    ----------------
    - Execute Cppcheck.
    - Normalize the returned structure.
    - Attach useful metadata.
    - Ensure downstream services always receive
      a consistent response format.
    """

    def analyze(self, file_path):
        start_time = datetime.now()

        result = run_cppcheck_analysis(file_path)

        if result is None:
            result = {}

        result.setdefault("issues", [])
        result.setdefault("report", "")
        result.setdefault("is_valid", True)

        issues = result["issues"]

        error_count = sum(
            1
            for issue in issues
            if "error" in str(issue).lower()
        )

        warning_count = sum(
            1
            for issue in issues
            if "warning" in str(issue).lower()
        )

        style_count = sum(
            1
            for issue in issues
            if "style" in str(issue).lower()
        )

        performance_count = sum(
            1
            for issue in issues
            if "performance" in str(issue).lower()
        )

        portability_count = sum(
            1
            for issue in issues
            if "portability" in str(issue).lower()
        )

        information_count = sum(
            1
            for issue in issues
            if "information" in str(issue).lower()
        )

        result["summary"] = {
            "total_issues": len(issues),
            "errors": error_count,
            "warnings": warning_count,
            "style": style_count,
            "performance": performance_count,
            "portability": portability_count,
            "information": information_count,
        }

        result["metadata"] = {
            "tool": "Cppcheck",
            "file": Path(file_path).name,
            "timestamp": start_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

        result["dashboard"] = {
            "status": (
                "PASSED"
                if result["is_valid"]
                else "FAILED"
            ),
            "issue_count": len(issues),
        }

        return result
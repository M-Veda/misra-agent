from pathlib import Path
from typing import Any, Dict, List, Optional

from validator.validator_engine import run_validation


class ValidationService:
    """
    Executes the final validation stage after patch application.

    Responsibilities:
        - Run validator engine.
        - Attach patch statistics.
        - Attach review history.
        - Compute validation summary.
        - Produce dashboard-friendly metadata.
    """

    def validate(
        self,
        file_path,
        patches=None,
        session=None,
    ):
        result = run_validation(file_path)

        patches = patches or []

        applied = sum(
            1
            for patch in patches
            if getattr(patch, "applied", False)
        )

        conflicted = sum(
            1
            for patch in patches
            if getattr(patch, "status", "") == "conflicted"
        )

        queued = sum(
            1
            for patch in patches
            if getattr(patch, "status", "") == "queued"
        )

        patch_summary = {
            "generated": len(patches),
            "applied": applied,
            "conflicted": conflicted,
            "queued": queued,
            "success_rate": (
                round((applied / len(patches)) * 100, 2)
                if patches
                else 100.0
            ),
        }

        issues = result.get("issues", [])

        validation_summary = {
            "passed": result.get("is_valid", False),
            "issue_count": len(issues),
            "error_count": sum(
                1
                for issue in issues
                if str(issue).lower().startswith("error")
            ),
            "warning_count": sum(
                1
                for issue in issues
                if str(issue).lower().startswith("warning")
            ),
        }

        dashboard = {
            "validation_status": (
                "PASSED"
                if validation_summary["passed"]
                else "FAILED"
            ),
            "file": Path(file_path).name,
            "total_patches": len(patches),
            "successful_patches": applied,
            "remaining_issues": len(issues),
        }

        result["patch_summary"] = patch_summary
        result["validation_summary"] = validation_summary
        result["dashboard"] = dashboard

        if session is not None:
            result["session_id"] = session.get("session_id")

            result["patch_history"] = session.get(
                "patch_history",
                [],
            )

            result["review_progress"] = session.get(
                "progress",
                {},
            )

            result["review_statistics"] = {
                "accepted": sum(
                    1
                    for d in session.get("decisions", [])
                    if d.action.value in ("accept", "edit")
                ),
                "rejected": sum(
                    1
                    for d in session.get("decisions", [])
                    if d.action.value == "reject"
                ),
                "skipped": sum(
                    1
                    for d in session.get("decisions", [])
                    if d.action.value == "skip"
                ),
            }

        return result
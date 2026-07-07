from collections import Counter

from config.settings import MISRA_VERSION
from report.report_generator import generate_report
from report.score_calculator import calculate_compliance_score
from utils.serialization import (
    serialize_decision,
    serialize_patch,
    serialize_violation,
)


class ReportService:
    """Creates the complete MISRA compliance report."""

    def generate(self, session, validation_result):
        violations = session.get("violations", [])
        decisions = session.get("decisions", [])
        patches = session.get("patches", [])

        remaining_issues = validation_result.get("issues", [])

        accepted = sum(
            1
            for decision in decisions
            if decision.action.value in ("accept", "edit")
        )

        rejected = sum(
            1
            for decision in decisions
            if decision.action.value == "reject"
        )

        skipped = sum(
            1
            for decision in decisions
            if decision.action.value == "skip"
        )

        applied_patches = sum(
            1 for patch in patches if patch.applied
        )

        conflicted_patches = sum(
            1
            for patch in patches
            if getattr(patch, "status", "") == "conflicted"
        )

        severity_counter = Counter()

        category_counter = Counter()

        rule_counter = Counter()

        auto_fixable = 0

        for violation in violations:
            severity_counter[violation.severity] += 1
            category_counter[violation.category] += 1
            rule_counter[violation.rule_id] += 1

            if violation.auto_fixable:
                auto_fixable += 1

        compliance_score = calculate_compliance_score(
            len(violations),
            len(remaining_issues),
        )

        report = {
            "session_info": {
                "session_id": session["session_id"],
                "misra_version": MISRA_VERSION,
                "source_file": session["file_path"],
                "output_file": session.get(
                    "output_file_path",
                    "",
                ),
            },
            "analysis_summary": {
                "total_violations": len(violations),
                "reviewed": len(decisions),
                "accepted": accepted,
                "rejected": rejected,
                "skipped": skipped,
                "auto_fixable": auto_fixable,
            },
            "rule_statistics": {
                "severity": dict(severity_counter),
                "categories": dict(category_counter),
                "rules": dict(rule_counter),
            },
            "patch_statistics": {
                "generated": len(patches),
                "applied": applied_patches,
                "conflicted": conflicted_patches,
                "queue": session.get("patch_queue", []),
                "history": session.get("patch_history", []),
            },
            "validation": validation_result,
            "final_score": {
                "score": compliance_score,
                "remaining_cppcheck_issues": len(
                    remaining_issues
                ),
            },
            "violations": [
                serialize_violation(v)
                for v in violations
            ],
            "decisions": [
                serialize_decision(d)
                for d in decisions
            ],
            "patches": [
                serialize_patch(p)
                for p in patches
            ],
            "analysis_report": session.get(
                "analysis_report",
                "",
            ),
        }

        generated = generate_report(report)

        session["report_path"] = generated["path"]
        session["compliance_report"] = generated["report"]

        return generated
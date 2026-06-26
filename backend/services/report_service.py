from config.settings import MISRA_VERSION
from report.report_generator import generate_report
from report.score_calculator import calculate_compliance_score
from utils.serialization import serialize_decision, serialize_patch, serialize_violation


class ReportService:
    def generate(self, session, validation_result):
        violations = session.get("violations", [])
        decisions = session.get("decisions", [])
        patches = session.get("patches", [])
        remaining_issues = validation_result.get("issues", [])

        report = {
            "session_id": session["session_id"],
            "misra_version": MISRA_VERSION,
            "source_file": session["file_path"],
            "output_file": session.get("output_file_path", ""),
            "total_violations": len(violations),
            "reviewed_violations": len(decisions),
            "accepted": sum(1 for decision in decisions if decision.action.value in ("accept", "edit")),
            "rejected": sum(1 for decision in decisions if decision.action.value == "reject"),
            "skipped": sum(1 for decision in decisions if decision.action.value == "skip"),
            "applied_patches": sum(1 for patch in patches if patch.applied),
            "compliance_score": calculate_compliance_score(len(violations), len(remaining_issues)),
            "validation": validation_result,
            "violations": [serialize_violation(violation) for violation in violations],
            "decisions": [serialize_decision(decision) for decision in decisions],
            "patches": [serialize_patch(patch) for patch in patches],
            "analysis_report": session.get("analysis_report", ""),
        }

        generated = generate_report(report)
        session["report_path"] = generated["path"]
        session["compliance_report"] = generated["report"]
        return generated

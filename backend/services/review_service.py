from config.settings import OUTPUT_DIR, ensure_runtime_directories
from models.decision import Decision
from models.review_action import ReviewAction
from models.session_state import SessionState
from services.final_code_service import FinalCodeService
from services.patch_service import PatchService
from services.report_service import ReportService
from services.session_service import SessionService
from services.validation_service import ValidationService
from utils.serialization import serialize_decision, serialize_patch, serialize_violation


class ReviewService:
    def __init__(self):
        self.sessions = SessionService()
        self.patch_service = PatchService()
        self.final_code_service = FinalCodeService()
        self.validation_service = ValidationService()
        self.report_service = ReportService()

    def current(self, session_or_id):
        session = self._resolve_session(session_or_id)
        violation = self._current_violation(session)
        return serialize_violation(violation) if violation else None

    def status(self, session_id):
        session = self.sessions.require(session_id)
        return self._session_response(session)

    def explain_current(self, session_id):
        session = self.sessions.require(session_id)
        violation = self._current_violation(session)
        if violation is None:
            raise ValueError("Review is complete; there is no current rule to explain.")

        return {
            "session_id": session_id,
            "violation_id": violation.violation_id,
            "rule_id": violation.rule_id,
            "title": violation.title,
            "severity": violation.severity,
            "category": violation.category,
            "description": violation.description,
            "explanation": violation.explanation or violation.description,
            "original_code": violation.original_code,
            "suggested_code": violation.suggested_code,
            "auto_fixable": violation.auto_fixable,
        }

    def submit(self, session_id, action, edited_code="", comment=""):
        session = self.sessions.require(session_id)
        review_action = ReviewAction(action)
        violation = self._current_violation(session)
        if violation is None:
            return self._session_response(session)

        patch = self._build_patch_for_decision(violation, review_action, edited_code)
        patch_id = patch.patch_id if patch else ""

        decision = Decision(
            violation_id=violation.violation_id,
            action=review_action,
            patch_id=patch_id,
            edited_code=edited_code if review_action == ReviewAction.EDIT else "",
            comment=comment,
        )

        violation.approved = decision.approved if review_action != ReviewAction.SKIP else None
        session["decisions"].append(decision)
        if patch is not None:
            session["patches"].append(patch)
            violation.patch_id = patch.patch_id

        session["current_index"] += 1
        if self._review_complete(session):
            session["status"] = SessionState.BUILDING.value

        self.sessions.update(session_id, session)
        response = self._session_response(session)
        response["decision"] = serialize_decision(decision)
        return response

    def finalize(self, session_id):
        session = self.sessions.require(session_id)

        if not self._review_complete(session):
            raise ValueError("Review must be completed before final code can be generated.")

        if session.get("status") == SessionState.FINISHED.value and session.get("final_code"):
            return self._final_response(session)

        ensure_runtime_directories()
        session["status"] = SessionState.BUILDING.value
        final_code = self.final_code_service.generate(session["original_code"], session["patches"])

        output_file = OUTPUT_DIR / f"{session_id}.c"
        output_file.write_text(final_code, encoding="utf-8")

        session["final_code"] = final_code
        session["output_file_path"] = str(output_file)
        session["status"] = SessionState.VALIDATING.value

        validation_result = self.validation_service.validate(output_file)
        session["validation_result"] = validation_result

        generated_report = self.report_service.generate(session, validation_result)
        session["status"] = SessionState.FINISHED.value
        self.sessions.update(session_id, session)

        response = self._final_response(session)
        response["report_generation"] = {
            "status": generated_report["status"],
            "path": generated_report["path"],
        }
        return response

    def generate(self, session_id):
        session = self.sessions.require(session_id)
        if session.get("status") == SessionState.FINISHED.value:
            return self._final_response(session)
        return self._session_response(session)

    def _build_patch_for_decision(self, violation, action, edited_code):
        if action == ReviewAction.ACCEPT:
            if not violation.suggested_code:
                return None
            return self.patch_service.create_patch(
                violation,
                violation.suggested_code,
                strategy=violation.fix_strategy or "rule_suggestion",
            )

        if action == ReviewAction.EDIT:
            return self.patch_service.create_patch(
                violation,
                edited_code,
                strategy="user_edit",
                description="User-edited remediation",
            )

        return None

    def _session_response(self, session):
        return {
            "session_id": session["session_id"],
            "status": session["status"],
            "total_violations": len(session["violations"]),
            "current_index": min(session["current_index"], len(session["violations"])),
            "review_complete": self._review_complete(session),
            "current_violation": self.current(session),
            "progress": self._progress(session),
            "original_code": session["original_code"],
            "analysis_report": session.get("analysis_report", ""),
        }

    def _final_response(self, session):
        response = self._session_response(session)
        response.update(
            {
                "final_code": session.get("final_code", ""),
                "validation_result": session.get("validation_result"),
                "compliance_report": session.get("compliance_report"),
                "output_file_path": session.get("output_file_path", ""),
                "report_path": session.get("report_path", ""),
                "decisions": [serialize_decision(decision) for decision in session.get("decisions", [])],
                "patches": [serialize_patch(patch) for patch in session.get("patches", [])],
            }
        )
        return response

    def _progress(self, session):
        decisions = session.get("decisions", [])
        accepted = sum(1 for decision in decisions if decision.action in (ReviewAction.ACCEPT, ReviewAction.EDIT))
        rejected = sum(1 for decision in decisions if decision.action == ReviewAction.REJECT)
        skipped = sum(1 for decision in decisions if decision.action == ReviewAction.SKIP)
        return {
            "reviewed": len(decisions),
            "remaining": max(len(session["violations"]) - len(decisions), 0),
            "accepted": accepted,
            "rejected": rejected,
            "skipped": skipped,
            "patches_ready": len(session.get("patches", [])),
        }

    def _current_violation(self, session):
        index = session["current_index"]
        if index >= len(session["violations"]):
            return None
        return session["violations"][index]

    def _review_complete(self, session):
        return session["current_index"] >= len(session["violations"])

    def _resolve_session(self, session_or_id):
        if isinstance(session_or_id, str):
            return self.sessions.require(session_or_id)
        return session_or_id

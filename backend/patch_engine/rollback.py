from datetime import datetime, timezone
from typing import Dict, List


class PatchRollbackManager:
    def __init__(self):
        self._rollback_history: List[Dict] = []

    def rollback_patch(self, patch, code, session=None):
        if patch.status == "rolled_back":
            return code, False
        restored_code = code
        if patch.replacement_code and patch.original_code:
            restored_code = code.replace(patch.replacement_code, patch.original_code, 1) if patch.replacement_code in code else code
        patch.status = "rolled_back"
        patch.rolled_back_at = datetime.now(timezone.utc)
        patch.history.append({"event": "rolled_back", "timestamp": patch.rolled_back_at.isoformat()})
        record = {
            "patch_id": patch.patch_id,
            "timestamp": patch.rolled_back_at.isoformat(),
            "status": patch.status,
            "session_id": session.get("session_id") if session else None,
        }
        self._rollback_history.append(record)
        if session is not None:
            session.setdefault("patch_history", []).append(record)
        return restored_code, True

    def rollback_session(self, session, code):
        patches = session.get("patches", [])
        restored_code = code
        for patch in reversed(patches):
            if patch.status == "applied":
                restored_code, _ = self.rollback_patch(patch, restored_code, session=session)
        return restored_code

    def history(self):
        return list(self._rollback_history)

from datetime import datetime, timezone
from typing import Any, Dict, List


class PatchHistoryManager:
    def __init__(self):
        self._records: List[Dict[str, Any]] = []

    def record(self, event, patch, session=None, details=None):
        entry = {
            "event": event,
            "patch_id": patch.patch_id,
            "strategy": patch.strategy,
            "description": patch.description,
            "status": patch.status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {},
        }
        patch.history.append(entry)
        self._records.append(entry)
        if session is not None:
            session.setdefault("patch_history", []).append(entry)
        return entry

    def get(self, patch_id: str):
        return [entry for entry in self._records if entry.get("patch_id") == patch_id]

    def by_session(self, session):
        return session.get("patch_history", []) if session else []

    def snapshot(self):
        return list(self._records)

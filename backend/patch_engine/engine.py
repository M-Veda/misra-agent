from datetime import datetime, timezone
from typing import List

from patch_engine.conflict_detector import PatchConflictDetector
from patch_engine.history import PatchHistoryManager
from patch_engine.queue import PatchQueue
from patch_engine.rollback import PatchRollbackManager
from patch_engine.strategies import PatchStrategyRegistry


class PatchEngine:
    def __init__(self):
        self.queue = PatchQueue()
        self.history = PatchHistoryManager()
        self.rollback_manager = PatchRollbackManager()
        self.conflict_detector = PatchConflictDetector()
        self.strategy_registry = PatchStrategyRegistry()

    def enqueue(self, patch, session=None):
        self.queue.enqueue(patch)
        patch.status = "queued"
        self.history.record("queued", patch, session=session)
        return patch

    def execute(self, code, patches, session=None):
        if not patches:
            return code

        ordered = self.queue.ordered_patches(patches)
        applied_code = code
        applied_patches = []
        for patch in ordered:
            conflicts = self.conflict_detector.detect_conflicts([patch], applied_patches)
            if conflicts:
                patch.status = "conflicted"
                patch.conflict_reason = "; ".join(conflicts)
                self.history.record("conflicted", patch, session=session, details={"reason": patch.conflict_reason})
                continue

            strategy = self.strategy_registry.get(patch.strategy)
            try:
                patched_code = strategy.apply(applied_code, patch)
            except Exception as exc:
                patch.status = "conflicted"
                patch.conflict_reason = f"Execution failure: {exc}"
                self.history.record("conflicted", patch, session=session, details={"reason": patch.conflict_reason})
                continue

            patch.applied = True
            patch.status = "applied"
            patch.applied_at = datetime.now(timezone.utc)
            self.history.record("applied", patch, session=session, details={"order": len(applied_patches) + 1})
            applied_code = patched_code
            applied_patches.append(patch)

        return applied_code

    def rollback(self, patch, code, session=None):
        return self.rollback_manager.rollback_patch(patch, code, session=session)

    def rollback_session(self, session, code):
        return self.rollback_manager.rollback_session(session, code)

    def history_for(self, patch_id):
        return self.history.get(patch_id)

    def session_history(self, session):
        return self.history.by_session(session)

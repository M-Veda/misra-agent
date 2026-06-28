import uuid

from models.patch import Patch
from services.patch_strategies import PatchStrategyRegistry


class PatchService:
    def __init__(self):
        self.strategy_registry = PatchStrategyRegistry()

    def create_patch(self, violation, replacement_code, strategy, description="", metadata=None):
        if violation.original_code is None:
            raise ValueError("Cannot create a patch without original code context.")

        patch = Patch(
            patch_id=str(uuid.uuid4()),
            violation_id=violation.violation_id,
            rule_id=violation.rule_id,
            file_path=violation.file_path,
            line_number=violation.line_number,
            original_code=violation.original_code,
            replacement_code=replacement_code,
            description=description or violation.title,
            strategy=strategy,
            confidence=violation.confidence,
            metadata=metadata or {},
        )
        patch.history.append({"event": "created", "strategy": strategy, "description": patch.description})
        return patch

    def enqueue_patch(self, session, patch):
        queue = session.setdefault("patch_queue", [])
        queue.append(
            {
                "patch_id": patch.patch_id,
                "violation_id": patch.violation_id,
                "rule_id": patch.rule_id,
                "strategy": patch.strategy,
                "description": patch.description,
                "status": "queued",
            }
        )
        patch.status = "queued"
        patch.history.append({"event": "queued", "patch_id": patch.patch_id})
        session.setdefault("patch_history", []).append(self._history_entry(patch, "queued"))
        return queue

    def apply_patches(self, code, patches):
        applied_code = code
        applied_patches = []
        for patch in sorted(patches, key=lambda item: item.line_number, reverse=True):
            try:
                self._detect_conflict(patch, applied_patches)
                strategy = self.strategy_registry.get(patch.strategy)
                patched_code = strategy.apply(applied_code, patch)
                patch.applied = True
                patch.status = "applied"
                patch.applied_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
                patch.history.append({"event": "applied", "strategy": patch.strategy})
                applied_code = patched_code
                applied_patches.append(patch)
            except Exception as exc:
                patch.applied = False
                patch.status = "conflicted"
                patch.conflict_reason = f"Conflict: {exc}"
                patch.history.append({"event": "conflicted", "reason": patch.conflict_reason})
        return applied_code

    def rollback_patch(self, code, patch):
        if patch.status == "rolled_back":
            return code
        if patch.original_code is None:
            raise ValueError("Cannot rollback a patch without original code context.")
        restored_code = code.replace(patch.replacement_code, patch.original_code, 1) if patch.replacement_code else code
        patch.status = "rolled_back"
        patch.rolled_back_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        patch.history.append({"event": "rolled_back"})
        return restored_code

    def get_patch_history(self, patch):
        return patch.history

    def _detect_conflict(self, patch, applied_patches):
        for applied_patch in applied_patches:
            if applied_patch.file_path != patch.file_path:
                continue
            if patch.line_number != applied_patch.line_number:
                continue
            if applied_patch.original_code and patch.original_code and applied_patch.original_code == patch.original_code:
                raise ValueError("Conflict: overlapping patch targets the same source location.")
        return None

    def _history_entry(self, patch, event):
        return {
            "event": event,
            "patch_id": patch.patch_id,
            "strategy": patch.strategy,
            "description": patch.description,
            "status": patch.status,
            "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        }

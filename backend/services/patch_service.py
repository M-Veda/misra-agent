import uuid

from models.patch import Patch
from patch_engine.engine import PatchEngine


class PatchService:
    def __init__(self):
        self.engine = PatchEngine()

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
        self.engine.enqueue(patch, session=session)
        queue = session.setdefault("patch_queue", [])
        queue.append(
            {
                "patch_id": patch.patch_id,
                "violation_id": patch.violation_id,
                "rule_id": patch.rule_id,
                "strategy": patch.strategy,
                "description": patch.description,
                "status": patch.status,
            }
        )
        return queue

    def apply_patches(self, code, patches):
        return self.engine.execute(code, patches)

    def rollback_patch(self, code, patch):
        return self.engine.rollback(patch, code)[0]

    def get_patch_history(self, patch):
        return patch.history

import uuid

from models.patch import Patch
from patch_engine.engine import PatchEngine
from utils.logger import logger


class PatchService:
    """
    Service responsible for creating, queueing,
    applying and rolling back patches.
    """

    def __init__(self):
        self.engine = PatchEngine()

    def create_patch(
        self,
        violation,
        replacement_code,
        strategy,
        description="",
        metadata=None,
    ):

        if violation.original_code is None:
            raise ValueError(
                "Cannot create a patch without original code."
            )

        replacement_code = (replacement_code or "").rstrip()

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
            metadata=dict(metadata or {}),
        )

        patch.add_history(
            "created",
            strategy=strategy,
            description=patch.description,
        )

        logger.info(
            "Created patch %s for Rule %s",
            patch.patch_id,
            patch.rule_id,
        )

        return patch

    def enqueue_patch(
        self,
        session,
        patch,
    ):

        self.engine.enqueue(
            patch,
            session=session,
        )

        queue = session.setdefault(
            "patch_queue",
            [],
        )

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

        logger.info(
            "Queued patch %s",
            patch.patch_id,
        )

        return queue

    def apply_patches(
        self,
        code,
        patches,
        session=None,
    ):

        if not patches:
            logger.info("No patches to apply.")
            return code

        logger.info(
            "Applying %d patch(es).",
            len(patches),
        )

        return self.engine.execute(
            code,
            patches,
            session=session,
        )

    def rollback_patch(
        self,
        code,
        patch,
        session=None,
    ):

        logger.info(
            "Rolling back patch %s",
            patch.patch_id,
        )

        restored_code, _ = self.engine.rollback(
            patch,
            code,
            session=session,
        )

        return restored_code

    def rollback_session(
        self,
        session,
        code,
    ):

        logger.info(
            "Rolling back session %s",
            session.get("session_id", ""),
        )

        return self.engine.rollback_session(
            session,
            code,
        )

    def get_patch_history(
        self,
        patch,
    ):

        return list(
            patch.history,
        )

    def get_engine_history(
        self,
        patch_id,
    ):

        return self.engine.history_for(
            patch_id,
        )

    def get_session_history(
        self,
        session,
    ):

        return self.engine.session_history(
            session,
        )
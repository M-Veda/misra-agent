import uuid

from models.patch import Patch


class PatchService:
    def create_patch(self, violation, replacement_code, strategy, description=""):
        if violation.original_code is None:
            raise ValueError("Cannot create a patch without original code context.")

        return Patch(
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
        )

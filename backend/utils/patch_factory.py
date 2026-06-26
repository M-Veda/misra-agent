import uuid

from models.patch import Patch


def create_patch(violation, replacement, strategy="rule_suggestion"):
    return Patch(
        patch_id=str(uuid.uuid4()),
        violation_id=violation.violation_id,
        rule_id=violation.rule_id,
        file_path=violation.file_path,
        line_number=violation.line_number,
        original_code=violation.original_code,
        replacement_code=replacement,
        description=violation.title,
        strategy=strategy,
        confidence=violation.confidence,
    )

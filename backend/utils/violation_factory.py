import uuid

from models.violation import Violation


def create_violation(
    rule,
    file_path,
    line,
    original,
    suggestion="",
    explanation=""
):

    return Violation(

        violation_id=str(uuid.uuid4()),

        rule_id=rule.RULE_ID,

        title=rule.TITLE,

        description=rule.DESCRIPTION,

        severity=rule.SEVERITY,

        category=rule.CATEGORY,

        file_path=file_path,

        line_number=line,

        original_code=original,

        suggested_code=suggestion,

        explanation=explanation,

        auto_fixable=bool(suggestion)
    )
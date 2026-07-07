import uuid
from datetime import datetime, timezone

from models.violation import Violation


def create_violation(
    rule,
    file_path,
    line,
    original,
    suggestion="",
    explanation="",
    column=0,
    metadata=None,
):
    """
    Creates a standardized Violation object.

    Every rule plugin should use this helper instead of directly
    constructing Violation objects.
    """

    rule_metadata = rule.metadata()

    violation_metadata = {
        "chapter": rule_metadata.chapter,
        "rationale": rule_metadata.rationale,
        "references": list(rule_metadata.references),
        "priority": rule_metadata.priority,
        "capabilities": list(rule_metadata.capabilities),
        "rule_metadata": dict(rule_metadata.metadata),
        "detected_at": datetime.now(timezone.utc).isoformat(),
    }

    if metadata:
        violation_metadata.update(metadata)

    suggestion = (suggestion or "").rstrip()

    explanation = (
        explanation.strip()
        if explanation
        else rule_metadata.rationale
    )

    return Violation(
        violation_id=str(uuid.uuid4()),
        rule_id=rule_metadata.rule_id,
        title=rule_metadata.title,
        description=rule_metadata.description,
        severity=rule_metadata.severity,
        category=rule_metadata.category,
        file_path=file_path,
        line_number=int(line),
        column_number=max(int(column), 0),
        original_code=(original or "").rstrip(),
        suggested_code=suggestion,
        explanation=explanation,
        auto_fixable=bool(suggestion) and rule_metadata.fixable,
        fix_strategy=rule_metadata.fix_strategy,
        confidence=1.0,
        tags=[
            f"chapter:{rule_metadata.chapter}",
            f"priority:{rule_metadata.priority}",
            f"severity:{rule_metadata.severity.lower()}",
            f"category:{rule_metadata.category.lower()}",
        ],
        metadata=violation_metadata,
    )

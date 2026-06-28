import uuid

from models.violation import Violation


def create_violation(rule, file_path, line, original, suggestion="", explanation="", column=0, metadata=None):
    rule_metadata = rule.metadata()
    violation_metadata = {
        "chapter": rule_metadata.chapter,
        "rationale": rule_metadata.rationale,
        "references": list(rule_metadata.references),
        "priority": rule_metadata.priority,
        "capabilities": list(rule_metadata.capabilities),
        "rule_metadata": rule_metadata.metadata,
    }
    if metadata:
        violation_metadata.update(metadata)

    return Violation(
        violation_id=str(uuid.uuid4()),
        rule_id=rule_metadata.rule_id,
        title=rule_metadata.title,
        description=rule_metadata.description,
        severity=rule_metadata.severity,
        category=rule_metadata.category,
        file_path=file_path,
        line_number=line,
        column_number=column,
        original_code=original,
        suggested_code=suggestion,
        explanation=explanation or rule_metadata.rationale,
        auto_fixable=bool(suggestion) and rule_metadata.fixable,
        fix_strategy=rule_metadata.fix_strategy,
        confidence=1.0,
        tags=[f"chapter:{rule_metadata.chapter}", f"priority:{rule_metadata.priority}"],
        metadata=violation_metadata,
    )
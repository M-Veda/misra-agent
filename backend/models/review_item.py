from dataclasses import dataclass


@dataclass
class ReviewItem:

    violation_id: str

    rule_id: str

    title: str

    description: str

    severity: str

    line_number: int

    original_code: str

    suggested_code: str

    explanation: str

    auto_fixable: bool
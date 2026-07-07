from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class AutoFix:
    """
    Represents one automatic fix.
    """

    rule_id: str

    line: int

    original: str

    replacement: str

    explanation: str = ""

    confidence: float = 1.0

class AutoFixCollection:

    def __init__(self):
        self.fixes = []

    def add(
        self,
        fix,
    ):
        self.fixes.append(fix)

    def __len__(self):
        return len(self.fixes)

    def all(self):
        return list(self.fixes)

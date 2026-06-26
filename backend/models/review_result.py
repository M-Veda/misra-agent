from dataclasses import dataclass


@dataclass
class ReviewResult:

    accepted: int

    rejected: int

    total: int
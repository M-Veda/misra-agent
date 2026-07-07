from dataclasses import dataclass


@dataclass(slots=True)
class FixResult:

    success: bool

    original: str

    modified: str

    message: str = ""
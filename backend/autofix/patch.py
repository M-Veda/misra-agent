from dataclasses import dataclass


@dataclass(slots=True)
class Patch:

    start: int

    end: int

    replacement: str
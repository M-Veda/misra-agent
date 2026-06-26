from dataclasses import dataclass


@dataclass
class APIResponse:

    success: bool

    message: str

    data: dict
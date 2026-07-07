from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any


def _json_value(value: Any):
    """
    Recursively converts Python objects into
    JSON-serializable values.
    """

    if value is None:
        return None

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, Path):
        return str(value)

    if is_dataclass(value):
        return {
            key: _json_value(item)
            for key, item in asdict(value).items()
        }

    if isinstance(value, dict):
        return {
            str(key): _json_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [
            _json_value(item)
            for item in value
        ]

    return value


def serialize_violation(violation):
    """
    Serialize a Violation model.
    """

    return _json_value(violation)


def serialize_patch(patch):
    """
    Serialize a Patch model.
    """

    return _json_value(patch)


def serialize_decision(decision):
    """
    Serialize a Decision model.
    """

    return _json_value(decision)


def serialize_session(session):
    """
    Serialize an entire review session.
    """

    return _json_value(session)


def serialize(value):
    """
    Generic serializer for any supported object.
    """

    return _json_value(value)
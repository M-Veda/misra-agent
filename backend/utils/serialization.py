from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum


def _json_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _json_value(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value


def serialize_violation(violation):
    return _json_value(violation)


def serialize_patch(patch):
    return _json_value(patch)


def serialize_decision(decision):
    return _json_value(decision)

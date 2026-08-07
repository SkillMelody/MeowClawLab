from __future__ import annotations

import hashlib
import json
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Optional, Tuple, Union, get_args, get_origin, get_type_hints

from .model import DecisionCase, SCHEMA_VERSION


def _to_primitive(value: Any) -> Any:
    if is_dataclass(value):
        return {item.name: _to_primitive(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        return {key: _to_primitive(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_to_primitive(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def canonical_json(case: DecisionCase) -> str:
    return json.dumps(_to_primitive(case), ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def input_snapshot_sha256(case: DecisionCase) -> str:
    return hashlib.sha256(canonical_json(case).encode("utf-8")).hexdigest()


def _from_primitive(expected: Any, value: Any) -> Any:
    if value is None:
        return None
    origin = get_origin(expected)
    args = get_args(expected)
    if origin is Union:
        target = next((arg for arg in args if arg is not type(None)), Any)
        return _from_primitive(target, value)
    if origin in (tuple, Tuple):
        item_type = args[0] if args else Any
        if len(args) > 1 and args[1] is not Ellipsis:
            return tuple(_from_primitive(kind, item) for kind, item in zip(args, value))
        return tuple(_from_primitive(item_type, item) for item in value)
    if origin in (dict, Mapping):
        return value
    if expected is Any:
        return value
    if expected is Decimal:
        return Decimal(value)
    if expected is datetime:
        return datetime.fromisoformat(value)
    if expected is date:
        return date.fromisoformat(value)
    if isinstance(expected, type) and issubclass(expected, Enum):
        return expected(value)
    if isinstance(expected, type) and is_dataclass(expected):
        hints = get_type_hints(expected)
        return expected(**{item.name: _from_primitive(hints[item.name], value[item.name]) for item in fields(expected) if item.name in value})
    return value


def save_decision_case(case: DecisionCase, path: Path) -> None:
    if case.schema_version != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema version: {case.schema_version}")
    path.write_text(canonical_json(case) + "\n", encoding="utf-8")


def load_decision_case(path: Path) -> DecisionCase:
    payload = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    version = payload.get("schema_version")
    if version != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema version: {version}")
    return _from_primitive(DecisionCase, payload)


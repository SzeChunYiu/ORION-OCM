"""Minimal JSON Schema (draft 2020-12 subset) for the G2.1 schemas."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .canonical import SchemaError

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"


class ValidationError(SchemaError):
    """Instance failed a G2.1 JSON Schema."""


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / name
    if not path.is_file():
        raise SchemaError(f"missing schema {name}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_named(instance: Any, name: str) -> None:
    validate(instance, load_schema(name), base=SCHEMA_DIR, root=load_schema(name), current=SCHEMA_DIR / name)


def validate(instance: Any, schema: Any, *, base: Path, root: dict[str, Any], current: Path) -> None:
    if schema is True:
        return
    if schema is False:
        raise ValidationError("false schema")
    if not isinstance(schema, dict):
        raise ValidationError("invalid schema")
    if "$ref" in schema:
        target, new_root, new_current = _resolve(schema["$ref"], base=base, root=root, current=current)
        validate(instance, target, base=base, root=new_root, current=new_current)
        return
    if "allOf" in schema:
        for item in schema["allOf"]:
            validate(instance, item, base=base, root=root, current=current)
    if "anyOf" in schema:
        errors = []
        for item in schema["anyOf"]:
            try:
                validate(instance, item, base=base, root=root, current=current)
                break
            except ValidationError as exc:
                errors.append(exc)
        else:
            raise ValidationError("anyOf failed")
    if "oneOf" in schema:
        matched = 0
        for item in schema["oneOf"]:
            try:
                validate(instance, item, base=base, root=root, current=current)
                matched += 1
            except ValidationError:
                pass
        if matched != 1:
            raise ValidationError("oneOf failed")
    if "const" in schema and instance != schema["const"]:
        raise ValidationError(f"const {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        raise ValidationError(f"enum {schema['enum']}")
    if "type" in schema and not _type_ok(instance, schema["type"]):
        raise ValidationError(f"type {schema['type']}")
    if "minimum" in schema and isinstance(instance, (int, float)) and type(instance) is not bool:
        if instance < schema["minimum"]:
            raise ValidationError("minimum")
    if "minLength" in schema and isinstance(instance, str) and len(instance) < schema["minLength"]:
        raise ValidationError("minLength")
    if "minItems" in schema and isinstance(instance, list) and len(instance) < schema["minItems"]:
        raise ValidationError("minItems")
    if schema.get("uniqueItems") and isinstance(instance, list):
        encoded = [json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False) for x in instance]
        if len(encoded) != len(set(encoded)):
            raise ValidationError("uniqueItems")
    if "required" in schema:
        if not isinstance(instance, dict):
            raise ValidationError("object required")
        missing = [k for k in schema["required"] if k not in instance]
        if missing:
            raise ValidationError(f"required {missing}")
    if "properties" in schema or "additionalProperties" in schema:
        if not isinstance(instance, dict):
            raise ValidationError("object")
        props = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in props:
                validate(value, props[key], base=base, root=root, current=current)
            elif additional is False:
                raise ValidationError(f"additional property {key}")
            elif additional is not True:
                validate(value, additional, base=base, root=root, current=current)
    if "items" in schema and isinstance(instance, list):
        for item in instance:
            validate(item, schema["items"], base=base, root=root, current=current)


def _type_ok(instance: Any, declared: Any) -> bool:
    if isinstance(declared, list):
        return any(_type_ok(instance, item) for item in declared)
    if declared == "object":
        return isinstance(instance, dict)
    if declared == "array":
        return isinstance(instance, list)
    if declared == "string":
        return type(instance) is str
    if declared == "integer":
        return type(instance) is int
    if declared == "number":
        return type(instance) in (int, float) and type(instance) is not bool
    if declared == "boolean":
        return type(instance) is bool
    if declared == "null":
        return instance is None
    return False


def _resolve(ref: str, *, base: Path, root: dict[str, Any], current: Path) -> tuple[Any, dict[str, Any], Path]:
    file_part, _, pointer = ref.partition("#")
    if file_part:
        path = (current.parent / file_part).resolve()
        if not path.is_relative_to(base.resolve()):
            raise ValidationError("schema $ref escaped schema directory")
        schema = json.loads(path.read_text(encoding="utf-8"))
        root = schema
        current = path
    else:
        schema = root
    if not pointer:
        return schema, root, current
    if not pointer.startswith("/"):
        raise ValidationError(f"bad $ref {ref}")
    node: Any = schema
    for part in pointer.lstrip("/").split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            raise ValidationError(f"unresolved $ref {ref}")
    return node, root, current

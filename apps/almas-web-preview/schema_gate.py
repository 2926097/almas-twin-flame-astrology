"""Offline, fail-closed JSON Schema Draft 2020-12 validator for canonical ALMAS outputs.

Reads ONLY local schemas from the checked-out ALMAS repository. No calculation,
no writes, no HTTP request, no personal-data logging. Not a replacement for M30.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

SCHEMA_NAME = "canonical-analysis.schema.json"
SCHEMA_BASE = "https://example.invalid/almas/"
MAX_BYTES = 5 * 1024 * 1024


def _load_json(path: Path) -> object:
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("JSON file exceeds the 5 MiB limit")
    return json.loads(path.read_text(encoding="utf-8"))


def _refs(value: object):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "$ref" and isinstance(item, str):
                yield item
            else:
                yield from _refs(item)
    elif isinstance(value, list):
        for item in value:
            yield from _refs(item)


def build_validator(repo_root: Path) -> Draft202012Validator:
    schema_dir = repo_root / "schemas"
    if not schema_dir.is_dir():
        raise FileNotFoundError("ALMAS schemas/ directory not found")
    registry = Registry()
    documents: dict[str, object] = {}
    for path in sorted(schema_dir.glob("*.json")):
        document = _load_json(path)
        if not isinstance(document, dict):
            raise ValueError("Invalid schema document: " + path.name)
        uri = SCHEMA_BASE + path.name
        declared_id = document.get("$id")
        if declared_id is not None and (not isinstance(declared_id, str) or not declared_id):
            raise ValueError("Malformed schema identifier: " + path.name)
        resource = Resource.from_contents(document, default_specification=DRAFT202012)
        documents[uri] = document
        registry = registry.with_resource(uri, resource)
        if declared_id and declared_id != uri:
            # Aliases resolve to files already bundled locally; never retrieve HTTP.
            documents[declared_id] = document
            registry = registry.with_resource(declared_id, resource)
    target_id = SCHEMA_BASE + SCHEMA_NAME
    if target_id not in documents:
        raise FileNotFoundError("The authoritative canonical schema is unavailable")
    checked: set[str] = set()
    pending = [target_id]
    while pending:
        uri = pending.pop()
        if uri in checked:
            continue
        checked.add(uri)
        document = documents[uri]
        resolver = registry.resolver(base_uri=uri)
        for ref in _refs(document):
            # Fail closed on unresolved URI or fragment; never fetch network.
            resolver.lookup(ref)
            external = ref.partition("#")[0]
            if not external:
                continue
            absolute = external if "://" in external else SCHEMA_BASE + external
            if absolute not in documents:
                raise ValueError("Unbundled schema dependency")
            pending.append(absolute)
    root = documents[target_id]
    Draft202012Validator.check_schema(root)
    return Draft202012Validator(root, registry=registry)


def validate_document(validator: Draft202012Validator, document: object) -> list[dict[str, str]]:
    problems = sorted(
        validator.iter_errors(document),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    # Do not echo instance values from jsonschema ValidationError.message.
    return [
        {
            "path": "/" + "/".join(map(str, error.absolute_path)),
            "constraint": str(error.validator),
        }
        for error in problems
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline schema gate for ALMAS canonical JSON")
    parser.add_argument("canonical", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    try:
        validator = build_validator(args.repo_root)
        document = _load_json(args.canonical)
        problems = validate_document(validator, document)
    except (OSError, ValueError, json.JSONDecodeError, Exception) as exc:
        # Never print input contents, secrets or raw validator exception values.
        print("BLOCKED: schema or input cannot be safely validated (" + type(exc).__name__ + ")", file=sys.stderr)
        return 2
    if problems:
        print(json.dumps({"state": "INVALID", "errors": problems[:25], "truncated": len(problems) > 25}), file=sys.stdout)
        return 1
    print(json.dumps({"state": "SCHEMA_VALID", "note": "Not M30/empirical validation"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

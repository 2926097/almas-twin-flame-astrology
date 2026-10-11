"""Generate the complete offline Draft 2020-12 schema registry from the repo.

This is a build-only, deterministic script; no network or canonical input.
"""
import json
from pathlib import Path

APP = Path(__file__).resolve().parent
SCHEMAS = APP.parents[1] / "schemas"
if not SCHEMAS.is_dir():
    raise SystemExit("Full schema build needs repository checkout: schemas/ missing")

registry = []
ids = set()
for path in sorted(SCHEMAS.glob("*.json")):
    schema = json.loads(path.read_text(encoding="utf-8"))
    identifier = schema.get("$id")
    # Official ALMAS contracts use multiple host namespaces; hostnames are
    # identifiers ONLY. No URL is fetched, opened or resolved over HTTP.
    if identifier is None:
        # Some official Draft 2020-12 files omit $id. Give the in-memory
        # copy a stable local identifier at the same base as canonical.
        identifier = "https://example.invalid/almas/" + path.name
        schema["$id"] = identifier
    if not isinstance(identifier, str) or not identifier.startswith("https://"):
        raise SystemExit(f"Invalid bundled schema id: {path.name}")
    if identifier in ids:
        raise SystemExit(f"Duplicate schema id: {identifier}")
    ids.add(identifier)
    registry.append(schema)
if len(registry) < 100:
    raise SystemExit("Schema registry incomplete")
if "https://example.invalid/almas/canonical-analysis.schema.json" not in ids:
    raise SystemExit("Canonical root is absent")

content = "// Generated offline from schemas/*.json; DO NOT EDIT\n"
content += "export default " + json.dumps(registry, separators=(",", ":"), ensure_ascii=False) + ";\n"
(APP / "schema-registry.generated.mjs").write_text(content, encoding="utf-8")
print(f"Bundled {len(registry)} pinned ALMAS schemas with no remote resolution")

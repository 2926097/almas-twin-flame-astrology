"""Build the transitive closure of official Draft 2020-12 ALMAS schemas.

Only schema identifiers in the GENERATED registry are normalized. The source
contracts are never edited; all refs resolve entirely within repo/schemas.
No network access or remote schema loading is possible.
"""
import json
from pathlib import Path
from urllib.parse import urlparse

APP = Path(__file__).resolve().parent
ROOT = APP.parents[1]
SCHEMAS = ROOT / "schemas"
BASE = "https://example.invalid/almas/"
ROOT_NAMES = (
    "canonical-analysis.schema.json",
    "report-gate-output.schema.json",
    "report-document-model.schema.json",
)
all_schemas = {
    path.name: json.loads(path.read_text(encoding="utf-8"))
    for path in sorted(SCHEMAS.glob("*.json"))
}

def iter_refs(value):
    if isinstance(value, list):
        for item in value:
            yield from iter_refs(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in ("$ref", "$dynamicRef") and isinstance(item, str):
                yield item
            else:
                yield from iter_refs(item)

def basename(ref):
    if ref.startswith("#"):
        return None
    parsed = urlparse(ref)
    if parsed.scheme and parsed.scheme != "https":
        raise SystemExit("Unsupported schema reference scheme")
    name = parsed.path.rsplit("/", 1)[-1]
    if not name or "/" in name:
        raise SystemExit("Invalid schema reference")
    if name not in all_schemas:
        raise SystemExit(f"Unresolved local schema dependency: {name}")
    return name

def normalize(obj):
    if isinstance(obj, list):
        return [normalize(x) for x in obj]
    if not isinstance(obj, dict):
        return obj
    result = {}
    for key, value in obj.items():
        if key in ("$ref", "$dynamicRef") and isinstance(value, str) and not value.startswith("#"):
            name = basename(value)
            fragment = value.partition("#")[2]
            result[key] = BASE + name + ("#" + fragment if "#" in value else "")
        else:
            result[key] = normalize(value)
    return result

pending = list(ROOT_NAMES)
closure = set()
while pending:
    name = pending.pop()
    if name in closure:
        continue
    if name not in all_schemas:
        raise SystemExit(f"Required schema missing: {name}")
    schema = all_schemas[name]
    if schema.get("$schema") not in (None, "https://json-schema.org/draft/2020-12/schema"):
        raise SystemExit(f"Different JSON Schema dialect in dependency {name}")
    closure.add(name)
    for ref in iter_refs(schema):
        target = basename(ref)
        if target is not None and target not in closure:
            pending.append(target)

if len(closure) < len(ROOT_NAMES):
    raise SystemExit("Schema graph incomplete")
registry = []
for name in sorted(closure):
    schema = normalize(all_schemas[name])
    schema["$id"] = BASE + name
    registry.append(schema)
content = "// Generated from checked-in JSON Schema 2020-12 closure; NO NETWORK\n"
content += "export default " + json.dumps(registry, separators=(",", ":"), ensure_ascii=False) + ";\n"
(APP / "schema-registry.generated.mjs").write_text(content, encoding="utf-8")
print(f"Bundled {len(registry)} transitively referenced schemas, no remote resolver")

# ALMAS Web — Canonical M30/M31 synthetic gate

**Purpose**: demonstrate the production **contracts** on a wholly synthetic,
in-repository fixture. This is **not** an API to process real-person records.

Pipeline:
1. `tests/test_canonical_schema_validation.valid_canonical_analysis()` produces
   the public synthetic, schema-conformant canonical.
2. `schema_gate.build_validator(..., canonical-analysis.schema.json)` validates it
   against Draft 2020-12 with all dependencies resolved locally.
3. The existing `m30_report_gate` checks reportability and produces the
   canonical SHA-256 fingerprint. Execution trace is deliberately unavailable:
   **PARTIAL** must remain visible, not silently promoted to READY.
4. `m31_report` consumes M30 + the unmodified canonical and verifies its
   fingerprint before building the **declarative** report-document model.
5. The existing report gate and report model schemas validate those objects.
6. The HTTP endpoint returns **only metadata**: pass status, M30/M31 states,
   fingerprint, degradation reasons and section IDs. It never returns the
   canonical, positions, model indices, interpretive atlas, promotion
   reporting, prose, natal records or personal data.

Security and semantics:
- Only `GET /v1/canonical-demo` on Render, requiring the existing Bearer secret.
  Fixed route; no parameters, uploads, POST, dynamic file paths or input.
- Vercel exposes only `GET /api/canonical-demo` via the existing *encrypted*
  Preview credentials and Vercel Authentication. The proxy allowlists response
  keys to prevent leakage of unexpected canonical data.
- Render must install `pip install -e '.[schema-validation]'`. Do not change the
  build of the previously deployed precomputed-pillars demonstration service.
- No persistent data, no database, no analytics of individual users.
- M30 `PARTIAL` because of unavailable M00–M29 trace is expected and retained.
- **Not** an operational authorization to analyze people, store cases or publish
  relationship classifications. Atacires remains SHADOW/NO-GO.
- **No** production engine, index, schema or ontology changes.

Tests:
```bash
PYTHONPATH=src:tests python -m unittest discover -s apps/almas-api-sandbox -p 'test_*.py' -v
node --test apps/almas-web-preview/test/validator.test.mjs apps/almas-web-preview/test/proxy.test.mjs apps/almas-web-preview/test/canonical-demo.test.mjs
```

A subsequent real-case workflow will require verified identity/authentication,
consent/lawful basis, audit access rules, retention, privacy threat modeling,
server-side canonical schema validation, M30/M31 pipeline orchestration and
deployment E2E tests. Such a workflow is **out of scope**.

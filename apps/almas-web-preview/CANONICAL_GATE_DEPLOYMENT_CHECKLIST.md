# ALMAS Web — Activation checklist for the synthetic M30/M31 preview

**Status: SYNTHETIC PREVIEW DEPLOYED, protected HTTPS GET E2E PASS (10 October 2026). NO-GO for all real-person analyses and production promotion.**

This runbook preserves the separation between the existing Render service
`almas-engine-synthetic-preview` (precomputed pillars) and the distinct,
proposed **synthetic canonical gate** service. Do not repurpose or change the
existing service, Atacires, or ALMAS main.

## Preconditions

- PR #106 CI: node / Python / schema gates PASS at the exact candidate SHA.
- Runtime Docker/Python package version, schema version and SectionSpec contract
  checked from that SHA. The gate currently exposes twelve M31 sections.
- The isolated Render service `almas-twin-flame` already exists under the confirmed
  workspace, with `autoDeploy=no`, Frankfurt and **free** plan. A previous
  API attempt to create a differently named service was blocked; the actual
  service was provisioned separately and must not be confused with the original
  `almas-engine-synthetic-preview`.
- Every HTTP payload is synthetic, public, and fixed in the repository.
  No file import, client-supplied canonical, POST, case identifier, or personal data.

## Verified Render configuration (already provisioned)

Do **not** create or repurpose another service. The existing isolated Render
service is `almas-twin-flame` (ID `srv-db5a5m59fdbs73c525a0`, URL
`https://almas-twin-flame.onrender.com`). Its reviewed settings are:

| Setting | Value |
| --- | --- |
| Repository | `https://github.com/2926097/almas-twin-flame-astrology` |
| Branch | `feature/almas-web-synthetic-canonical-m30-m31-20261010` |
| Runtime | Python |
| Plan | Free (rechecked before acceptance) |
| Region | Frankfurt |
| Build | `python -m pip install -e '.[schema-validation]'` |
| Start | `python apps/almas-api-sandbox/server.py` |
| Auto deploy | **Off** |
| Env | `ALMAS_API_SHARED_SECRET` (strong random value, min 32 characters) |

A separate credential has been configured in Render as
`ALMAS_API_SHARED_SECRET` and in Vercel Preview as
`ALMAS_CANONICAL_GATE_SECRET`, of type `encrypted`. Do not paste or display
it in this repository, logs, screenshots or tickets. Do not reuse the
credential of the precomputed-pillars demo service.

Check the resulting Render **new** service URL and Git SHA. Verify only
`GET /_health` publicly reports the safe synthetic scope. Without an
Authorization header, `GET /v1/canonical-demo` must return 401. Only
authenticated internal tests may request a result; there is no CORS policy.

## Vercel Preview configuration

Keep `almas-web-preview` in the existing Vercel team, with **Vercel
Authentication enabled for all deployments**.

Verified **encrypted server-side Preview-only** environment variables:

- `ALMAS_CANONICAL_GATE_URL`: the exact HTTPS URL of the NEW Render service
  (not the existing precomputed-pillars service).
- `ALMAS_CANONICAL_GATE_SECRET`: the new secret matching the Render
  `ALMAS_API_SHARED_SECRET`. Never prefix this variable with `NEXT_PUBLIC_`,
  `VITE_`, etc.

The isolated deployment `dpl_6kpnDqd5rXEfdhrgvtGMA86CU4E6` included
`index.html`, `app.mjs`, `validator.mjs`, `api/synthetic.js`,
`api/canonical-demo.js`, and `vercel.json` from code SHA
`724f752f31a356110b64a98fbce65c1c9f9187e0`. It returned **READY**.
Vercel Authentication remains on for all deployments. No promotion to
production, external public domain or CI auto-deployment was made.

## Required protected HTTP end-to-end tests

Use the caller's authenticated Vercel CLI (e.g. `vercel curl`), or its
short-lived project-scoped OIDC token. Do not disable Vercel Authentication
or print tokens. Check:

1. `GET /api/canonical-demo` returns 200 **through protected Preview**;
   `kind=ALMAS_SYNTHETIC_CANONICAL_GATE_V1`, `synthetic=true`,
   `schema_validation=PASS`, `canonical_returned=false`.
2. M30 is `PARTIAL` when M00–M29 trace is absent, never silently READY.
   M31 `report_state` matches M30 and `canonical_fingerprint_verified=true`.
   The SHA-256 fingerprint is 64 lowercase hex characters and the M31 section
   list matches the current official `SECTION_SPECS`.
3. Browser receives **no** canonical object, source data, personal metadata,
   natal points, scoring, interpretive atlas, prose, auth tokens or secrets.
4. `POST /api/canonical-demo` returns 405; missing Render secret fails closed.
   A rejected upstream response returns a sanitized failure, not raw body.
5. `Cache-Control: no-store`; no unexpected CORS or data retention.
6. The existing `/api/synthetic` and local canonical JSON import remain
   functional and never send the imported JSON over HTTP.
7. Check Vercel Function logs and Render logs for errors **without**
   logging response bodies, request identifiers, headers or sensitive material.

## E2E receipt (protected preview, 10 October 2026)

- **GitHub source SHA tested**: `724f752f31a356110b64a98fbce65c1c9f9187e0`.
- **GitHub Actions**: six workflows completed PASS; ALMAS Web
  [run 38082546486](https://github.com/2926097/almas-twin-flame-astrology/actions/runs/38082546486): 46/46 tests.
- **Render service**: `srv-db5a5m59fdbs73c525a0`, isolated,
  free/Frankfurt, `autoDeploy=no`; deploy `dep-db5ae0jbc2fs73esffeg`,
  source SHA above, status `live` after its credentials were configured.
- **Vercel project**: `almas-web-preview`, deploy
  `dpl_6kpnDqd5rXEfdhrgvtGMA86CU4E6`, status `READY`,
  protected with Vercel Authentication. Preview-only encrypted env names:
  `ALMAS_CANONICAL_GATE_URL` and `ALMAS_CANONICAL_GATE_SECRET`.
- **Authenticated provider-side HTTPS GET, 2026-10-10 20:59:56 UTC**:
  `GET /api/canonical-demo` returned **HTTP 200** and
  `ALMAS_SYNTHETIC_CANONICAL_GATE_V1`, `synthetic=true`,
  `schema_validation=PASS`, `canonical_returned=false`;
  M30=`PARTIAL`, `EXECUTION_TRACE_UNAVAILABLE` disclosed;
  M31=`PARTIAL`, `canonical_fingerprint_verified=true`,
  12 section IDs, and 64 lowercase hex SHA-256. No embedded canonical,
  indices or personal data. `Cache-Control: no-store, max-age=0`.
- **Regression checks of existing routes**, same protected deployment:
  `GET /` and `GET /api/synthetic` each returned HTTP 200; the
  latter retained `PRECOMPUTED_PILLARS` and `no-store`.
- **Negative-path checks**: local HTTP server rejects unauthenticated
  requests (401) and unsupported methods (405); Vercel proxy regression
  tests cover method rejection and response allowlisting. A separate
  live HTTPS POST/405 invocation was **not** recorded by the protected
  GET-only fetch; do not claim that particular runtime assertion as PASS.
- **Protection**: temporary authorized provider access was used to test;
  no project-wide protection setting was disabled and no bypass link was
  disclosed. The source response contained no secrets.

This receipt certifies **only the synthetic, zero-input integration**.
It does not authorize receiving personal data, running ephemerides on cases,
M30/M31 production promotion, or any ontological claim.

## Acceptance and rollback

E2E core GET is **PASS** with exact IDs, status, content invariants and timestamp.
The live POST negative-path check remains an explicitly documented residual.
Treat source changes after this receipt as requiring fresh CI and rerun E2E.


On any error, disable the new Preview environment variables or revert
only the new Vercel Preview deployment. Preserve the existing synthetic
precomputed service and all production code.

**Non-goals:** processing personal canonical files, M00–M29 real-world
ephemerides, identity matching, production APIs, scientific/metaphysical
validation, changes to IEM/IDD/IRC/IAT/ICC/ICE, ontology, or Atacires SHADOW/NO-GO.

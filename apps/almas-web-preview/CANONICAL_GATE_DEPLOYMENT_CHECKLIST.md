# ALMAS Web — Activation checklist for the synthetic M30/M31 preview

**Status: NOT DEPLOYED. NO-GO for HTTP E2E and all real-person analyses.**

This runbook preserves the separation between the existing Render service
`almas-engine-synthetic-preview` (precomputed pillars) and the distinct,
proposed **synthetic canonical gate** service. Do not repurpose or change the
existing service, Atacires, or ALMAS main.

## Preconditions

- PR #106 CI: node / Python / schema gates PASS at the exact candidate SHA.
- Runtime Docker/Python package version, schema version and SectionSpec contract
  checked from that SHA. The gate currently exposes twelve M31 sections.
- A team-authorized operator provisions the separate Render **free** web service
  in the confirmed workspace. The API action to create this new service was
  blocked; no alternative provisioning route was executed.
- Every HTTP payload is synthetic, public, and fixed in the repository.
  No file import, client-supplied canonical, POST, case identifier, or personal data.

## Manual Render setup (requires authorized action)

From the confirmed workspace in Render, create **a new** Python web service
with the proposed name `almas-canonical-gate-preview` and settings:

| Setting | Value |
| --- | --- |
| Repository | `https://github.com/2926097/almas-twin-flame-astrology` |
| Branch | `feature/almas-web-synthetic-canonical-m30-m31-20261010` |
| Runtime | Python |
| Plan | Free |
| Region | Frankfurt |
| Build | `python -m pip install -e '.[schema-validation]'` |
| Start | `python apps/almas-api-sandbox/server.py` |
| Auto deploy | **Off** |
| Env | `ALMAS_API_SHARED_SECRET` (strong random value, min 32 characters) |

Generate a **new** independent random secret directly in a trusted provider
or secrets manager. Do **not** paste it in this repository, the ChatGPT
conversation, logs, command arguments, fixtures, screenshots or tickets. Do not
reuse the credential of the precomputed-pillars demo service.

Check the resulting Render **new** service URL and Git SHA. Verify only
`GET /_health` publicly reports the safe synthetic scope. Without an
Authorization header, `GET /v1/canonical-demo` must return 401. Only
authenticated internal tests may request a result; there is no CORS policy.

## Vercel Preview configuration

Keep `almas-web-preview` in the existing Vercel team, with **Vercel
Authentication enabled for all deployments**.

Set these as **encrypted server-side Preview-only** environment variables:

- `ALMAS_CANONICAL_GATE_URL`: the exact HTTPS URL of the NEW Render service
  (not the existing precomputed-pillars service).
- `ALMAS_CANONICAL_GATE_SECRET`: the new secret matching the Render
  `ALMAS_API_SHARED_SECRET`. Never prefix this variable with `NEXT_PUBLIC_`,
  `VITE_`, etc.

Deploy exactly `index.html`, `app.mjs`, `validator.mjs`,
`api/synthetic.js`, `api/canonical-demo.js`, and `vercel.json` from the
reviewed SHA into the isolated **Preview** project. Do not promote to
production, assign external public domains, or enable CI auto deployment.

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

## Acceptance and rollback

Only mark E2E **PASS** after recording the protected deployment ID, new
Render service ID, their exact Git SHA, HTTP status/response invariants, and
test timestamp. CI PASS and `READY/live` alone are not HTTP verification.

On any error, disable the new Preview environment variables or revert
only the new Vercel Preview deployment. Preserve the existing synthetic
precomputed service and all production code.

**Non-goals:** processing personal canonical files, M00–M29 real-world
ephemerides, identity matching, production APIs, scientific/metaphysical
validation, changes to IEM/IDD/IRC/IAT/ICC/ICE, ontology, or Atacires SHADOW/NO-GO.

# ALMAS engine demo API — isolation contract

This is a **synthetic-only, authenticated, read-only** HTTP bridge to the existing public
`almas_tfa.analysis.analyze_precomputed` Python function. It reads only
`examples/precomputed-pillars.json` on disk. It **does not accept requests with
data**, execute astrology/ephemerides, generate `canonical_analysis`, validate M30,
or expose any personal information.

## Security

* `GET /_health` is public and contains only `{"status":"ok","scope":"synthetic_only"}`.
* `GET /v1/synthetic` requires `Authorization: Bearer <random 32+ character token>`.
* Every other route and method is rejected. Query parameters rejected. All replies `no-store`.
* No CORS, no HTTP logs containing request metadata, no secrets in source control.
* Explicit Render workspace, **free plan**, Frankfurt region and `autoDeploy=no` required.
* Vercel stores the same token as an **encrypted server-side environment variable**. The browser
  calls Vercel `/api/synthetic`, never Render directly; Vercel Authentication remains enabled.
* The Vercel proxy pins the upstream origin to a `.onrender.com` HTTPS hostname and forwards
  only the fixed synthetic route. No user-supplied URL or payload can reach Render.

## Local checks

```bash
PYTHONPATH=src python -m unittest discover -s apps/almas-api-sandbox -p test_server.py -v
```

## Render runtime

```text
Repository: 2926097/almas-twin-flame-astrology
Branch: feature/almas-web-authenticated-engine-demo-20261010 (pin for test)
Runtime: python
Build: python -m pip install -e .
Start: python apps/almas-api-sandbox/server.py
Environment: ALMAS_API_SHARED_SECRET (random; not committed)
```

There is **no automatic promotion or deployment to production**, and no connection to
Atacires SHADOW/NO-GO. A user-facing analysis API requires a separate security
review, schema validation, subject consent/retention controls, and explicitly
versioned M30/M31 gate tests before development may start.

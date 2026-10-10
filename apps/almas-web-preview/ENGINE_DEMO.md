# ALMAS Web — Python engine, synthetic demonstration only

The page imports local canonical JSON in browser-only mode, separately from the
new **synthetic-only** engine demo. `GET /api/synthetic` is a Vercel Function;
it forwards a fixed GET to the Render engine API using the server-only
`ALMAS_API_SHARED_SECRET` and `ALMAS_ENGINE_URL` environment variables.

No file imports, personal natal data, form input, case data or identity information
are transmitted. Vercel Authentication remains required. The Render API performs
only `analyze_precomputed` against the checked-in **public synthetic pillars**.
Its `PRECOMPUTED_PILLARS` output is **not a canonical analysis** and does not
execute M30/M31 or imply scientific/metaphysical validation.

Do not add arbitrary POST, dynamic URLs, user-submitted input or public caching
in this stage. Maintain SHADOW/NO-GO for Atacires.

Integration checks: `node --test apps/almas-web-preview/test/*.test.mjs`;
`PYTHONPATH=src python -m unittest discover -s apps/almas-api-sandbox -p test_server.py -v`.

"use strict";
/** Zero-input, authenticated, synthetic M30/M31 demo. Never proxy user data. */
module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store, max-age=0");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  const reply = (code, data) => res.status(code).json(data);
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    return reply(405, { error: "METHOD_NOT_ALLOWED" });
  }
  const endpoint = process.env.ALMAS_CANONICAL_GATE_URL;
  const secret = process.env.ALMAS_CANONICAL_GATE_SECRET;
  if (!endpoint || !secret || secret.length < 32) {
    return reply(503, { error: "DEMO_NOT_CONFIGURED" });
  }
  let origin;
  try {
    const uri = new URL(endpoint);
    const host = uri.hostname.toLowerCase();
    if (uri.protocol !== "https:" || uri.username || uri.password ||
      uri.pathname !== "/" || uri.search || uri.hash ||
      !(host === "onrender.com" || host.endsWith(".onrender.com"))) {
      return reply(503, { error: "INVALID_UPSTREAM_CONFIGURATION" });
    }
    origin = uri.origin;
  } catch {
    return reply(503, { error: "INVALID_UPSTREAM_CONFIGURATION" });
  }
  try {
    const upstream = await fetch(origin + "/v1/canonical-demo", {
      method: "GET",
      headers: { Authorization: "Bearer " + secret, Accept: "application/json" },
      redirect: "error", cache: "no-store", signal: AbortSignal.timeout(45000)
    });
    if (!upstream.ok) return reply(503, { error: "ENGINE_UNAVAILABLE" });
    const wire = await upstream.text();
    if (wire.length > 65536) return reply(502, { error: "INVALID_ENGINE_RESPONSE" });
    const body = JSON.parse(wire);
    const expectedSections = [
      "S01_SYNTHESIS", "S02_DATA_METHOD", "S03_NUMERIC_ONTOLOGY",
      "S04_STRUCTURE", "S05_RELATIONAL", "S06_DIFFERENTIAL",
      "S07_TEMPORAL", "S08_ROBUSTNESS", "S09_DOCTRINE",
      "S10_FINAL_SYNTHESIS", "S11_SOURCES_APPENDICES", "S12_PHASE_DYNAMICS"
    ];
    if (!body || body.kind !== "ALMAS_SYNTHETIC_CANONICAL_GATE_V1" ||
      body.synthetic !== true || body.schema_validation !== "PASS" ||
      body.canonical_returned !== false || body.m30_executed !== true ||
      body.m31_executed !== true ||
      !/^[0-9a-f]{64}$/.test(body.canonical_fingerprint) ||
      body.m30?.state !== "PARTIAL" ||
      body.m30?.execution_trace_state !== "UNAVAILABLE" ||
      body.m30?.reportable !== true || body.m30?.canonical_values_mutated !== false ||
      body.m31?.canonical_fingerprint_verified !== true ||
      body.m31?.canonical_values_embedded !== false ||
      body.m31?.prose_generated !== false ||
      body.m31?.report_state !== body.m30.state ||
      !Array.isArray(body.m31?.section_ids) ||
      body.m31.section_ids.length !== expectedSections.length ||
      !body.m31.section_ids.every((x, i) => x === expectedSections[i]) ||
      !Array.isArray(body.m30?.degradation_reasons) ||
      body.m30.degradation_reasons.length > 30 ||
      !body.m30.degradation_reasons.includes("EXECUTION_TRACE_UNAVAILABLE") ||
      !body.m30.degradation_reasons.every(x => typeof x === "string")) {
      return reply(502, { error: "INVALID_ENGINE_RESPONSE" });
    }
    // Strict explicit allowlist: no imported canonical, positions, scores, prose, or identities.
    return reply(200, {
      kind: body.kind,
      synthetic: true,
      schema_validation: "PASS",
      canonical_returned: false,
      canonical_fingerprint: body.canonical_fingerprint,
      m30: {
        state: body.m30.state,
        reportable: true,
        canonical_values_mutated: false,
        degradation_reasons: body.m30.degradation_reasons
      },
      m31: {
        report_state: body.m31.report_state,
        canonical_fingerprint_verified: true,
        canonical_values_embedded: false,
        prose_generated: false,
        section_ids: body.m31.section_ids
      }
    });
  } catch {
    return reply(503, { error: "ENGINE_UNAVAILABLE" });
  }
};

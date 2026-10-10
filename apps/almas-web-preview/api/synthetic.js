"use strict";
/**
 * Vercel -> Render. Synthetic demo only; no request payload or personal data.
 * Outer Vercel Authentication is also required by the project policy.
 */
module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store, max-age=0");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  const reply = (code, data) => res.status(code).json(data);
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    return reply(405, { error: "METHOD_NOT_ALLOWED" });
  }
  const endpoint = process.env.ALMAS_ENGINE_URL;
  const secret = process.env.ALMAS_API_SHARED_SECRET;
  if (!endpoint || !secret || secret.length < 32) {
    return reply(503, { error: "DEMO_NOT_CONFIGURED" });
  }
  let origin;
  try {
    const parsed = new URL(endpoint);
    const host = parsed.hostname.toLowerCase();
    if (parsed.protocol !== "https:" || parsed.username || parsed.password ||
        parsed.pathname !== "/" || parsed.search || parsed.hash ||
        !(host === "onrender.com" || host.endsWith(".onrender.com"))) {
      return reply(503, { error: "INVALID_UPSTREAM_CONFIGURATION" });
    }
    origin = parsed.origin;
  } catch {
    return reply(503, { error: "INVALID_UPSTREAM_CONFIGURATION" });
  }
  try {
    const upstream = await fetch(origin + "/v1/synthetic", {
      method: "GET",
      headers: {
        "Authorization": "Bearer " + secret,
        "Accept": "application/json"
      },
      redirect: "error",
      cache: "no-store",
      signal: AbortSignal.timeout(12000)
    });
    if (!upstream.ok) return reply(503, { error: "ENGINE_UNAVAILABLE" });
    const body = await upstream.text();
    if (body.length > 65536) return reply(502, { error: "INVALID_ENGINE_RESPONSE" });
    const result = JSON.parse(body);
    if (!result || result.kind !== "ALMAS_SYNTHETIC_ENGINE_RESULT_V1" ||
        result.synthetic !== true || result.canonical_analysis !== false ||
        result.m30_executed !== false ||
        result.engine_result?.input_mode !== "PRECOMPUTED_PILLARS" ||
        !result.engine_result?.models || typeof result.engine_result.models !== "object") {
      return reply(502, { error: "INVALID_ENGINE_RESPONSE" });
    }
    return reply(200, result);
  } catch {
    return reply(503, { error: "ENGINE_UNAVAILABLE" });
  }
};

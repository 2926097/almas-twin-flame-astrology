import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const handler = require("../api/canonical-demo.js");
const valid = {
  kind: "ALMAS_SYNTHETIC_CANONICAL_GATE_V1",
  synthetic: true, schema_validation: "PASS", canonical_returned: false,
  m30_executed: true, m31_executed: true,
  canonical_fingerprint: "a".repeat(64),
  m30: {state:"PARTIAL",reportable:true,canonical_values_mutated:false,
    degradation_reasons:["EXECUTION_TRACE_UNAVAILABLE"]},
  m31: {report_state:"PARTIAL",canonical_fingerprint_verified:true,
    canonical_values_embedded:false,prose_generated:false,
    section_ids: Array.from({length:12},(_,i)=>"S"+String(i+1).padStart(2,"0")+"_SYNTHETIC")},
  canonical_analysis: {positions:"SHOULD_NOT_LEAK"},
  secret: "NEVER_COPY"
};
const reply = () => ({
  code:0, headers:{}, body:null,
  setHeader(k,v){this.headers[k]=v;return this},
  status(code){this.code=code;return this},
  json(payload){this.body=payload;return this},
});
const setEnv = () => {
  process.env.ALMAS_ENGINE_URL="https://almas-engine-synthetic-preview.onrender.com";
  process.env.ALMAS_API_SHARED_SECRET="x".repeat(64);
};
async function withFetch(implementation, fn) {
  const existing=globalThis.fetch;
  globalThis.fetch=implementation;
  try { return await fn() } finally { globalThis.fetch=existing }
}
test("reject non-GET without reaching Render",async()=>{
  setEnv();await withFetch(()=>{throw Error("NO FETCH")},async()=>{
    let r=reply();await handler({method:"POST"},r);
    assert.equal(r.code,405);
  });
});
test("reject missing secret fail closed",async()=>{
  setEnv();delete process.env.ALMAS_API_SHARED_SECRET;
  const r=reply();await handler({method:"GET"},r);assert.equal(r.code,503);
});
test("reject SSRF or query in configured URL",async()=>{
  setEnv();process.env.ALMAS_ENGINE_URL="https://localhost:8443/?user=1";
  const r=reply();await handler({method:"GET"},r);assert.equal(r.code,503);
});
test("forward only fixed GET route, and strip all extra payload",async()=>{
  setEnv();let requested;
  await withFetch(async (url,opts)=>{
    requested={url,opts};
    return {ok:true,text:async()=>JSON.stringify(valid)};
  },async()=>{
    const r=reply();await handler({method:"GET"},r);
    assert.equal(r.code,200);
    assert.equal(requested.url,"https://almas-engine-synthetic-preview.onrender.com/v1/canonical-demo");
    assert.equal(requested.opts.headers.Authorization,"Bearer "+"x".repeat(64));
    assert.equal(r.headers["Cache-Control"],"no-store, max-age=0");
    const encoded=JSON.stringify(r.body);
    assert.ok(!encoded.includes("SHOULD_NOT_LEAK"));
    assert.ok(!encoded.includes("NEVER_COPY"));
    assert.ok(!encoded.includes('"canonical_analysis"'));
    assert.deepEqual(r.body.m31.section_ids,valid.m31.section_ids);
  });
});
test("reject fingerprint tampering",async()=>{
  setEnv();await withFetch(async()=>({ok:true,text:async()=>JSON.stringify({...valid,canonical_fingerprint:"BAD"})}),async()=>{
    const r=reply();await handler({method:"GET"},r);assert.equal(r.code,502)
  });
});
test("reject M31 when fingerprint or reportability not certified",async()=>{
  setEnv();await withFetch(async()=>({ok:true,text:async()=>JSON.stringify({...valid,m31:{...valid.m31,canonical_fingerprint_verified:false}})}),async()=>{
    const r=reply();await handler({method:"GET"},r);assert.equal(r.code,502)
  });
});
test("upstream errors never expose response body",async()=>{
  setEnv();await withFetch(async()=>({ok:false,status:403,text:async()=>"private"}),async()=>{
    const r=reply();await handler({method:"GET"},r);
    assert.equal(r.code,503);assert.ok(!JSON.stringify(r.body).includes("private"))
  });
});

import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const handler = require("../api/synthetic.js");
const demo = {kind:"ALMAS_SYNTHETIC_ENGINE_RESULT_V1", synthetic:true,
  canonical_analysis:false, m30_executed:false,
  engine_result:{input_mode:"PRECOMPUTED_PILLARS",models:{AF:{iem_final:10}}}};
function response(){
  return {code:0, headers:{}, data:null,
    setHeader(k,v){this.headers[k]=v;return this},
    status(c){this.code=c;return this},
    json(d){this.data=d;return this}};
}
function config(){process.env.ALMAS_ENGINE_URL="https://almas-sandbox.onrender.com";process.env.ALMAS_API_SHARED_SECRET="x".repeat(64)}
test("method gate denies mutation and does not fetch", async()=>{
  config();const old=globalThis.fetch;globalThis.fetch=()=>{throw Error("fetch not allowed")};
  try{const r=response();await handler({method:"POST"},r);assert.equal(r.code,405);assert.equal(r.data.error,"METHOD_NOT_ALLOWED")}finally{globalThis.fetch=old}
});
test("missing secret fails closed", async()=>{
  process.env.ALMAS_ENGINE_URL="https://almas-sandbox.onrender.com";delete process.env.ALMAS_API_SHARED_SECRET;
  const r=response();await handler({method:"GET"},r);assert.equal(r.code,503)
});
test("forbids SSRF-style endpoint overrides", async()=>{
  config();process.env.ALMAS_ENGINE_URL="http://localhost:8080";
  const r=response();await handler({method:"GET"},r);assert.equal(r.code,503);assert.equal(r.data.error,"INVALID_UPSTREAM_CONFIGURATION")
});
test("fetches only the fixed synthetic route and forwards token server-side", async()=>{
  config();let requested;
  const old=globalThis.fetch;
  globalThis.fetch=async(url,opts)=>{requested={url,opts};return {ok:true,text:async()=>JSON.stringify(demo)}};
  try{
    const r=response();await handler({method:"GET"},r);
    assert.equal(r.code,200);assert.deepEqual(r.data,demo);
    assert.equal(requested.url,"https://almas-sandbox.onrender.com/v1/synthetic");
    assert.equal(requested.opts.headers.Authorization,"Bearer "+"x".repeat(64));
    assert.equal(r.headers["Cache-Control"],"no-store, max-age=0");
    assert.ok(!JSON.stringify(r.data).includes("x".repeat(64)));
  }finally{globalThis.fetch=old}
});
test("rejects an upstream response that claims to be canonical", async()=>{
  config();const old=globalThis.fetch;
  globalThis.fetch=async()=>({ok:true,text:async()=>JSON.stringify({...demo,canonical_analysis:true})});
  try{const r=response();await handler({method:"GET"},r);assert.equal(r.code,502)}finally{globalThis.fetch=old}
});
test("rejects upstream HTTP error without leaking details", async()=>{
  config();const old=globalThis.fetch;
  globalThis.fetch=async()=>({ok:false,status:401,text:async()=>"private info"});
  try{const r=response();await handler({method:"GET"},r);assert.equal(r.code,503);assert.ok(!JSON.stringify(r.data).includes("private"))}finally{globalThis.fetch=old}
});

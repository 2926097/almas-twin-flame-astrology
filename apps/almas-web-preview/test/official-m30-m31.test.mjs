import test from "node:test";
import assert from "node:assert/strict";
import {execFileSync} from "node:child_process";
import {fileURLToPath} from "node:url";
import {validateAlmasFull} from "../full-schema-validator.mjs";
import {assessReportTriplet} from "../report-view.mjs";
import {canonicalizePythonRaw,digestCanonicalRaw} from "../json-lexical-digest.mjs";

const root=fileURLToPath(new URL("../../../",import.meta.url));
function officialTriplet(){
  const code=[
    "import json",
    "from canonical_demo import _ctx",
    "from test_canonical_schema_validation import valid_canonical_analysis",
    "from almas_tfa.report_gate_handlers import m30_report_gate",
    "from almas_tfa.report_model_handlers import m31_report",
    "canonical=valid_canonical_analysis()",
    "gate_run=m30_report_gate(_ctx('M30',{'canonical_analysis':canonical},{}))",
    "gate=dict(gate_run.payload)",
    "model=dict(m31_report(_ctx('M31',{},",
    "  {'canonical_analysis':canonical,'report_gate':gate})).payload)",
    "raw=json.dumps(canonical,ensure_ascii=False,sort_keys=True,separators=(\',\',\':\'),default=str)",
    "print(json.dumps({'canonical':canonical,'canonicalRaw':raw,'m30':gate,'m31':model},ensure_ascii=False,default=str))"
  ].join("\n");
  const wire=execFileSync(process.env.ALMA_PYTHON||"python3",["-c",code],{
    cwd:root,env:{...process.env,PYTHONPATH:"src:tests:apps/almas-api-sandbox"},
    encoding:"utf8",maxBuffer:10*1024*1024
  });
  return JSON.parse(wire);
}
test("real Python canonical M30/M31 outputs validate against fully bundled Draft 2020-12",()=>{
  const {canonical,m30,m31}=officialTriplet();
  for(const [name,object] of [
    ["canonical-analysis.schema.json",canonical],
    ["report-gate-output.schema.json",m30],
    ["report-document-model.schema.json",m31]]) {
    const result=validateAlmasFull(object,name);
    assert.equal(result.ok,true,name+" "+JSON.stringify(result.errors).slice(0,650));
  }
});
test("full local gate evaluates real synthetic M30 and M31 without mutation",async()=>{
  const {canonical,m30,m31,canonicalRaw}=officialTriplet();
  const before=JSON.stringify(canonical);
  const evaluated=await assessReportTriplet(canonical,m30,m31,{validate:validateAlmasFull,digest:()=>digestCanonicalRaw(canonicalRaw)});
  assert.equal(evaluated.ok,true,evaluated.reason);
  assert.equal(evaluated.state,"PARTIAL");
  assert.equal(evaluated.sections.length,12);
  assert.equal(JSON.stringify(canonical),before);
  assert.equal(m30.canonical_fingerprint,m31.canonical_fingerprint);
});

test("lexical canonicalization preserves Python float and exponent spellings",()=>{
  const wire='{"z":1.0,"a":1e-07,"n":-0.0,"nested":{"y":3,"x":2.5}}';
  assert.equal(canonicalizePythonRaw(wire),
    '{"a":1e-07,"n":-0.0,"nested":{"x":2.5,"y":3},"z":1.0}');
  assert.throws(()=>canonicalizePythonRaw('{"x":1,"x":2}'),/Duplicate/);
  assert.throws(()=>canonicalizePythonRaw('{"x":1e}'),/(JSON|Expected comma|Invalid)/);
});

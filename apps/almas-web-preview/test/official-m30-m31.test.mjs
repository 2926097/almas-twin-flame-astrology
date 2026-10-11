import test from "node:test";
import assert from "node:assert/strict";
import {execFileSync} from "node:child_process";
import {fileURLToPath} from "node:url";
import {validateAlmasFull} from "../full-schema-validator.mjs";
import {assessReportTriplet} from "../report-view.mjs";

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
    "print(json.dumps({'canonical':canonical,'m30':gate,'m31':model},ensure_ascii=False,default=str))"
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
  const {canonical,m30,m31}=officialTriplet();
  const before=JSON.stringify(canonical);
  const evaluated=await assessReportTriplet(canonical,m30,m31,{validate:validateAlmasFull});
  assert.equal(evaluated.ok,true,evaluated.reason);
  assert.equal(evaluated.state,"PARTIAL");
  assert.equal(evaluated.sections.length,12);
  assert.equal(JSON.stringify(canonical),before);
  assert.equal(m30.canonical_fingerprint,m31.canonical_fingerprint);
});

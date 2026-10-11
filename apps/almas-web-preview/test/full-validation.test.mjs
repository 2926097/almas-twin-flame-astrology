import test from "node:test";
import assert from "node:assert/strict";
import {execFileSync} from "node:child_process";
import {fileURLToPath} from "node:url";
import {validateCanonicalFull,validateAlmasFull} from "../full-schema-validator.mjs";
const repo=fileURLToPath(new URL("../../../",import.meta.url));
function officialSynthetic(){
  const wire=execFileSync(process.env.ALMA_PYTHON || "python3",["-c",
    "import json;from test_canonical_schema_validation import valid_canonical_analysis;print(json.dumps(valid_canonical_analysis(),ensure_ascii=False))"
  ],{cwd:repo,env:{...process.env,PYTHONPATH:"src:tests"},encoding:"utf8"});
  return JSON.parse(wire);
}
test("Draft 2020-12 validates the authoritative synthetic canonical",()=>{
  const c=officialSynthetic(),before=JSON.stringify(c);
  const result=validateCanonicalFull(c);
  assert.equal(result.kind,"JSON_SCHEMA_DRAFT_2020_12");
  assert.equal(result.ok,true,JSON.stringify(result.errors));
  assert.ok(result.schemaCount>=3);
  assert.equal(JSON.stringify(c),before);
});
test("full schema rejects a root violation omitted by basic browser preflight",()=>{
  const c=officialSynthetic();
  c.evidence=[{evidence_id:"ROOT:fake"}];
  const result=validateCanonicalFull(c);
  assert.equal(result.ok,false);
  assert.ok(result.errors.some(x=>x.path.includes("evidence")||x.keyword==="required"));
});
test("full schema rejects unexpected nested fields",()=>{
  const c=officialSynthetic();c.models.LG.not_in_contract=true;
  assert.equal(validateCanonicalFull(c).ok,false);
});
test("full schema rejects unknown canonical schema and cannot use network refs",()=>{
  const c=officialSynthetic();
  const result=validateAlmasFull(c,"https://unknown.example/twin-flame.json");
  assert.equal(result.ok,false);assert.equal(result.kind,"SCHEMA_ENGINE_UNAVAILABLE");
});
test("schema error summaries do not echo private user values",()=>{
  const c=officialSynthetic();c.models.AF.state="PRIVATE_SECRET_IDENTIFIER";
  const result=validateCanonicalFull(c);
  assert.equal(result.ok,false);
  assert.ok(!JSON.stringify(result).includes("PRIVATE_SECRET_IDENTIFIER"));
});

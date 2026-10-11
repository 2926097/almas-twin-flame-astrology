import test from "node:test";
import assert from "node:assert/strict";
import {execFileSync} from "node:child_process";
import {fileURLToPath} from "node:url";
import {buildRelationalWorkRequest, POLICY_PRESET, PUBLIC_VERSION} from "../birth-request.mjs";

const root=fileURLToPath(new URL("../../../",import.meta.url));
const sample=()=>({
  analysis_profile:"FULL_ASTROLOGY",
  analysis_policy_profile:POLICY_PRESET,
  subjects:[
    {id:"A",display_name:"Ejemplo A",birth_date:"2000-02-29",birth_time:"05:30",
      timezone:"Europe/Madrid",place:"Ciudad sintética",latitude:"41.3",longitude:"-0.8",
      time_reliability:"A",birth_time_source_class:"DOCUMENTARY"},
    {id:"B",display_name:"Ejemplo B",birth_date:"2001-04-15",birth_time:"21:20",
      timezone:"America/Santo_Domingo",latitude:"18.4",longitude:"-69.6",
      time_reliability:"B",birth_time_source_class:"REPORTED"}
  ]
});
const expectReject=(mutate,expression)=>{const input=sample();mutate(input);assert.throws(()=>buildRelationalWorkRequest(input),expression)};
test("request is official, exact two subjects, no computed positions, no shadow promotion",()=>{
  const before=sample(),clone=JSON.stringify(before),out=buildRelationalWorkRequest(before);
  assert.equal(JSON.stringify(before),clone);
  assert.deepEqual(Object.keys(out),["request"]);
  assert.equal(out.request.format,"ALMAS_WORK_REQUEST");
  assert.equal(out.request.execution_state,"REQUEST_ONLY");
  assert.equal(out.request.public_version,PUBLIC_VERSION);
  assert.equal(out.request.analysis_policy_profile,POLICY_PRESET);
  assert.deepEqual(out.request.events,[]);
  assert.equal(out.request.subjects.length,2);
  assert.equal(out.request.subjects[0].latitude,41.3);
  assert.equal(out.request.subjects[1].longitude,-69.6);
  for(const key of ["analysis_policies","atacires_requests","indices","scoring","canonical_analysis","result"])assert.ok(!(key in out.request),key);
});
test("reject date overflows, malformed local time and absent timezone",()=>{
  expectReject(x=>x.subjects[0].birth_date="2001-02-29",/fecha gregoriana inválida/);
  expectReject(x=>x.subjects[1].birth_date="2000-13-15",/fecha gregoriana inválida/);
  expectReject(x=>x.subjects[0].birth_time="24:00",/HH:MM/);
  expectReject(x=>x.subjects[1].birth_time="",/obligatoria|entre 1/);
  expectReject(x=>x.subjects[0].timezone="",/entre 1/);
  expectReject(x=>x.subjects[0].timezone="Not/A_Real_Zone",/desconocida/);
});
test("reject missing coordinates, fabricated defaults, ambiguous subject identity",()=>{
  expectReject(x=>x.subjects[0].latitude="",/coordenada obligatoria/);
  expectReject(x=>x.subjects[0].longitude="181",/fuera del rango/);
  expectReject(x=>x.subjects[1].latitude="NaN",/fuera del rango/);
  expectReject(x=>x.subjects[1].id="A",/distintos/);
  expectReject(x=>x.subjects=x.subjects.slice(0,1),/exactamente dos/);
  expectReject(x=>x.subjects[0].time_reliability="",/entre 1/);
});
test("explicit frozen experimental preset and approved profile required",()=>{
  expectReject(x=>x.analysis_policy_profile="",/explícitamente/);
  expectReject(x=>x.analysis_profile="MYSTIC_AUTO_SCORE",/perfil/);
  expectReject(x=>x.subjects[0].birth_time_source_class="guess",/fuente/);
});
test("Python official relational adapter accepts and fingerprints generated request",()=>{
  const payload=buildRelationalWorkRequest(sample());
  const code=[
    "import json,sys",
    "from almas_tfa.relational_request_pipeline import assess_relational_work_request,prepare_relational_raw_input",
    "from almas_tfa.relational_policy_presets import resolve_relational_policy_preset",
    "req=json.load(sys.stdin)",
    "assessment=assess_relational_work_request(req)",
    "assert assessment['ready_for_raw_input']",
    "assert assessment['analysis_policy_profile']=='ALMAS_RELATIONAL_STRICT_RESEARCH_V1'",
    "raw=prepare_relational_raw_input(req)",
    "assert raw['request_adapter_trace']['implicit_orbs_used'] is False",
    "assert raw['request_adapter_trace']['case_fitting_used'] is False",
    "assert raw['subjects'][0]['birth_time']=='05:30'",
    "assert raw['subjects'][1]['timezone']=='America/Santo_Domingo'",
    "assert raw['request_adapter_trace']['analysis_policy_fingerprint']==assessment['analysis_policy_fingerprint']",
    "print('ADAPTER_PASS')"
  ].join("\n");
  const output=execFileSync(process.env.ALMA_PYTHON||"python3",["-c",code],{
    input:JSON.stringify(payload),encoding:"utf8",cwd:root,
    env:{...process.env,PYTHONPATH:"src:tests"},timeout:20000
  });
  assert.match(output,/ADAPTER_PASS/);
});

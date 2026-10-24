import test from "node:test";
import assert from "node:assert/strict";
import {execFileSync} from "node:child_process";
import {fileURLToPath} from "node:url";
import {buildTwoBirthRequest,describeTwoBirthReadiness,POLICY_PRESET} from "../birth-request.mjs";
const a={display_name:"Sujeto A",birth_date:"1988-06-17",birth_time:"13:20",time_reliability:"A",timezone:"Europe/Madrid",latitude:40.4168,longitude:-3.7038};
const b={display_name:"Sujeto B",birth_date:"1990-11-06",birth_time:"09:10",time_reliability:"B",timezone:"America/Chicago",latitude:41.8781,longitude:-87.6298};
test("two births map to frozen relational adapter request without inferred orbs",()=>{
 const request=buildTwoBirthRequest(a,b);
 assert.equal(request.format,"ALMAS_WORK_REQUEST");
 assert.equal(request.type,"RELATIONAL");
 assert.equal(request.execution_state,"REQUEST_ONLY");
 assert.equal(request.public_version,"1.26.0");
 assert.equal(request.analysis_policy_profile,POLICY_PRESET);
 assert.equal(request.subjects.length,2);
 assert.equal(request.subjects[0].birth_time,"13:20");
 assert.deepEqual(request.events,[]);
 assert.equal(Object.hasOwn(request,"atacires_requests"),false);
 assert.equal(Object.hasOwn(request,"analysis_policies"),false);
 assert.equal(describeTwoBirthReadiness(request).automatic_calculation,false);
});
test("bad dates, coordinates, unknown zone, hour quality and policy fail closed",()=>{
 for(const sample of [
 {...a,birth_date:"1977-02-30"},{...a,latitude:""},{...a,longitude:"NaN"},
 {...a,latitude:91},{...a,birth_time:"25:15"},{...a,time_reliability:"X"},
 {...a,timezone:""},{...a,birth_time:"",time_reliability:"A"}
 ])assert.throws(()=>buildTwoBirthRequest(sample,b));
 assert.throws(()=>buildTwoBirthRequest(a,b,{profile:"MADE_UP"}));
 assert.throws(()=>buildTwoBirthRequest(a,b,{policyPreset:"MADE_UP"}));
});
test("uncertain hour remains explicitly missing instead of fabricated",()=>{
 const request=buildTwoBirthRequest({...a,birth_time:"",time_reliability:"D",timezone:""},b);
 assert.equal(Object.hasOwn(request.subjects[0],"birth_time"),false);
 assert.equal(Object.hasOwn(request.subjects[0],"timezone"),false);
 assert.equal(describeTwoBirthReadiness(request).timed_subjects,1);
});
test("unknown IANA zones and nonnumeric coordinates fail before export",()=>{
 for(const timezone of ["Not/A_Real_Zone","Europe/Unknown"])
  assert.throws(()=>buildTwoBirthRequest({...a,timezone},b));
 for(const latitude of [null,true,false,[],{},"   "])
  assert.throws(()=>buildTwoBirthRequest({...a,latitude},b));
});
test("exported request passes the official Python adapter without implicit orbs",()=>{
 const request=buildTwoBirthRequest(a,b,{profile:"FULL_ASTROLOGY",policyPreset:POLICY_PRESET});
 const code=[
  "import json,sys",
  "from almas_tfa.relational_request_pipeline import assess_relational_work_request,prepare_relational_raw_input",
  "req=json.load(sys.stdin)",
  "assessment=assess_relational_work_request(req)",
  "assert assessment['ready_for_raw_input']",
  "raw=prepare_relational_raw_input(req)",
  "trace=raw['request_adapter_trace']",
  "assert trace['implicit_orbs_used'] is False",
  "assert trace['case_fitting_used'] is False",
  "assert trace['analysis_policy_fingerprint']==assessment['analysis_policy_fingerprint']",
  "assert raw['subjects']==req['subjects']",
  "assert 'atacires_requests' not in raw",
  "print('ADAPTER_PASS')"
 ].join("\n");
 const output=execFileSync(process.env.ALMA_PYTHON||"python3",["-c",code],{
  input:JSON.stringify(request),encoding:"utf8",
  cwd:fileURLToPath(new URL("../../../",import.meta.url)),
  env:{...process.env,PYTHONPATH:"src:tests"},timeout:20000
 });
 assert.match(output,/ADAPTER_PASS/);
});

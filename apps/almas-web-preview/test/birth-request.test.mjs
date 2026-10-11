import test from "node:test";
import assert from "node:assert/strict";
import {buildTwoBirthRequest,describeTwoBirthReadiness,POLICY_PRESET} from "../birth-request.mjs";
const a={display_name:"Sujeto A",birth_date:"1977-03-20",birth_time:"17:45",time_reliability:"A",timezone:"Europe/Madrid",latitude:41.65,longitude:-0.89};
const b={display_name:"Sujeto B",birth_date:"1991-05-23",birth_time:"04:15",time_reliability:"B",timezone:"America/Santo_Domingo",latitude:18.45,longitude:-69.3};
test("two births map to frozen relational adapter request without inferred orbs",()=>{
 const request=buildTwoBirthRequest(a,b);
 assert.equal(request.format,"ALMAS_WORK_REQUEST");
 assert.equal(request.type,"RELATIONAL");
 assert.equal(request.execution_state,"REQUEST_ONLY");
 assert.equal(request.public_version,"1.26.0");
 assert.equal(request.analysis_policy_profile,POLICY_PRESET);
 assert.equal(request.subjects.length,2);
 assert.equal(request.subjects[0].birth_time,"17:45");
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

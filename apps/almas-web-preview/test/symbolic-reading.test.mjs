import test from "node:test";
import assert from "node:assert/strict";
import {buildSymbolicReadings,POLICY_ID} from "../symbolic-reading.mjs";
const sample={
 natal_context:{subjects:{
  A:{point_signs:{
   VENUS:{longitude:42,sign:"TAURUS",retrograde:false,decan:"segundo"},
   JUNO:{longitude:255,sign:"SAGITTARIUS",retrograde:true},
   UNKNOWN_POINT:{longitude:17,sign:"ARIES"}
  },house_placements:{VENUS:{house:8},JUNO:{house:3}},
  rulerships:{VENUS:"VENUS",JUNO:"JUPITER"}},
  B:{point_signs:{MARS:{longitude:112,sign:"CANCER",retrograde:null}},
     house_placements:{}}
 }}
};
test("symbolic interpretations are tagged hypotheses with canonical refs",()=>{
 const x=buildSymbolicReadings(sample);
 assert.equal(x.policy_id,POLICY_ID);
 assert.equal(x.created_new_scores,false);
 assert.equal(x.calculated_new_positions,false);
 assert.equal(x.is_authoritative_authored_report,false);
 assert.equal(x.metaphysical_classification,"NOT_EVALUABLE");
 assert.equal(x.subjects.length,2);
 const a=x.subjects[0].readings;
 assert.equal(a.length,3);
 const v=a.find(i=>i.point==="VENUS");
 assert.match(v.interpretation,/vínculo/i);
 assert.match(v.interpretation,/casa 8/i);
 assert.match(v.interpretation,/segundo/);
 assert.match(v.interpretation,/Regente declarado: VENUS/);
 assert.match(v.canonical_ref,/\/natal_context\/subjects\/A\/point_signs\/VENUS/);
 assert.equal(v.epistemic_class,"E_PROJECT_HYPOTHESIS");
 const j=a.find(i=>i.point==="JUNO");
 assert.match(j.interpretation,/retrógrado registrado/);
 const unknown=a.find(i=>i.point==="UNKNOWN_POINT");
 assert.equal(unknown.has_defined_symbolism,false);
 assert.match(unknown.interpretation,/No hay un significado específico autorizado/);
 assert.match(unknown.interpretation,/no se infiere/);
});
test("missing source information never fabricated",()=>{
 const x=buildSymbolicReadings({natal_context:{subjects:{
   A:{point_signs:{MERCURY:{longitude:10}}}
 }}});
 const row=x.subjects[0].readings[0];
 assert.match(row.interpretation,/signo no está disponible/);
 assert.match(row.interpretation,/casa no es evaluable/);
 assert.match(row.interpretation,/Decanato no declarado/);
 assert.match(row.interpretation,/Regente no declarado/);
 assert.match(row.interpretation,/Movimiento retrógrado\/directo no evaluable/);
 assert.equal(row.house,null);
 assert.equal(row.sign,null);
});
test("canonicals with no natal subjects give no readings, not inferred charts",()=>{
 const doc={models:{AF:{state:"INSUFFICIENT"}}};
 const before=JSON.stringify(doc);
 const x=buildSymbolicReadings(doc);
 assert.deepEqual(x.subjects,[]);
 assert.equal(JSON.stringify(doc),before);
 assert.throws(()=>buildSymbolicReadings(null));
});

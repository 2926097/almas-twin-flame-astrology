import test from "node:test";
import assert from "node:assert/strict";
import {selectRootRows,selectCounterRows,selectLimitations,displayValue} from "../local-inspection.mjs";
const makeRoot=(id,strength,state="CALCULATED_CORE",extra={})=>({
  evidence_id:id,root_id:id.replace("ROOT:",""),root_key:"PAIR:"+id,
  strength,strength_state:state,core_eligible:state==="CALCULATED_CORE",
  dependency_families:["FAMILY_ONE"],independent_family_count:1,
  point_ids:["P1"],relation_ids:["R1"],concrete_contacts:[{id:"c"}],
  ...extra
});
const makeCounter=(id,model,severity,extra={})=>({
  id,model,severity,kind:"EXPLICIT_CONTRADICTION",
  dependency_family:"FAMILY_ONE",essential:true,
  evidence_refs:["ROOT:A"],note:{private_birth_location:"not to project"},...extra
});
test("orders roots by original strength; null remains non-evaluable",()=>{
  const data=[makeRoot("ROOT:Z",null,"NOT_EVALUABLE"),makeRoot("ROOT:B",0.6),makeRoot("ROOT:A",0.6),makeRoot("ROOT:C",0)];
  const p=selectRootRows(data);
  assert.deepEqual(p.rows.map(x=>x.id),["ROOT:A","ROOT:B","ROOT:C","ROOT:Z"]);
  assert.equal(p.rows.at(-1).strength,null);
  assert.equal(p.rows[2].strength,0);
  assert.equal(displayValue(0),"0");
  assert.equal(displayValue(null),"No evaluable");
});
test("restrict roots by state without mutating the supplied array",()=>{
  const roots=[makeRoot("ROOT:A",.2),makeRoot("ROOT:B",.8,"CALCULATED_SUPPORT_ONLY")];
  const copy=structuredClone(roots);
  const r=selectRootRows(roots,{state:"CALCULATED_SUPPORT_ONLY"});
  assert.equal(r.sourceCount,2);assert.equal(r.matchingCount,1);
  assert.equal(r.rows[0].id,"ROOT:B");assert.deepEqual(roots,copy);
});
test("search IDs, root keys and dependency family case-insensitively",()=>{
  const r=[makeRoot("ROOT:ALPHA",.2),makeRoot("ROOT:BETA",.8,"CALCULATED_CORE",{dependency_families:["DYNAMIC_MOTIF"]})];
  assert.deepEqual(selectRootRows(r,{query:"dynamic_motif"}).rows.map(x=>x.id),["ROOT:BETA"]);
  assert.deepEqual(selectRootRows(r,{query:"alpha"}).rows.map(x=>x.id),["ROOT:ALPHA"]);
});
test("unknown filter values fail closed instead of showing everything",()=>{
  assert.equal(selectRootRows([makeRoot("ROOT:A",.2)],{state:"FUTURE_UNREVIEWED"}).matchingCount,0);
  assert.equal(selectCounterRows([makeCounter("C1","LG",.2)],{model:"UNKNOWN"}).matchingCount,0);
});
test("display capped at 100; matching count preserves total",()=>{
  const roots=Array.from({length:151},(_,i)=>makeRoot("ROOT:"+String(i).padStart(3,"0"),i/151));
  const r=selectRootRows(roots,{limit:100000});
  assert.equal(r.sourceCount,151);assert.equal(r.matchingCount,151);
  assert.equal(r.rows.length,100);assert.equal(r.truncated,true);
});
test("dependency families and contact counts are descriptions, not an independence score",()=>{
  const r=selectRootRows([makeRoot("ROOT:A",.3,"CALCULATED_CORE",{dependency_families:["ONE","TWO"],independent_family_count:1,concrete_contacts:[1,2,3,4]})]);
  assert.equal(r.rows[0].contactCount,4);
  assert.equal(r.rows[0].independentFamilyCount,1);
  assert.deepEqual(r.rows[0].dependencyFamilies,["ONE","TWO"]);
});
test("counterevidence filters exact model with original severity and reference counts",()=>{
  const c=[makeCounter("C1","AF",null),makeCounter("C2","LG",0),makeCounter("C3","LG",0.9)];
  const result=selectCounterRows(c,{model:"LG"});
  assert.equal(result.sourceCount,3);assert.equal(result.matchingCount,2);
  assert.deepEqual(result.rows.map(r=>r.id),["C3","C2"]);
  assert.equal(result.rows[1].severity,0);
});
test("free-form counterevidence notes never enter the projection",()=>{
  const c=[makeCounter("C1","AF",.3,{note:"<img src=x onerror=alert(1)> SECRET"})];
  const result=selectCounterRows(c);
  assert.ok(!JSON.stringify(result).includes("SECRET"));
  assert.ok(!Object.keys(result.rows[0]).includes("note"));
});
test("root selections do not preserve unrelated raw evidence fields",()=>{
  const roots=[makeRoot("ROOT:A",.3,"CALCULATED_CORE",{raw_subject_name:"PRIVATE",root_key:"PRIVATE KEY"})];
  const result=selectRootRows(roots);
  assert.ok(!JSON.stringify(result).includes("PRIVATE"));
});
test("limits do not change original limitations or escape them into HTML",()=>{
  const x=["No timing available","<script>not interpreted</script>",...Array.from({length:99},(_,i)=>"L"+i)];
  const p=selectLimitations(x,80);
  assert.equal(p.rows.length,80);assert.equal(p.count,101);assert.equal(p.truncated,true);
  assert.equal(p.rows[1],"<script>not interpreted</script>");
  assert.equal(x.length,101);
});
test("empty or malformed array inputs never throw or create fake evidence",()=>{
  assert.deepEqual(selectRootRows(null).rows,[]);
  assert.deepEqual(selectCounterRows({kind:"A"}).rows,[]);
  assert.deepEqual(selectLimitations(null).rows,[]);
});

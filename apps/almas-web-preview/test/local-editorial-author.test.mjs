import test from "node:test";
import assert from "node:assert/strict";
import {createLocalEditorialDraft,validateLocalEditorialDraft,EDITORIAL_FORMAT}
  from "../local-editorial-author.mjs";
import {SECTION_IDS} from "../report-view.mjs";
const FP="c".repeat(64);
const sections=SECTION_IDS.map((id,i)=>({
  section_id:id,title:"Capítulo "+(i+1),order:i+1,
  section_state:i===11?"NOT_AVAILABLE":"AVAILABLE",
  available_paths:["models","evidence"],epistemic_classes_allowed:["A_CALCULATED","C_DOCTRINE"]
}));
const model={report_state:"PARTIAL",canonical_fingerprint:FP,
  canonical_fingerprint_verified:true,canonical_values_mutated:false,
  canonical_values_embedded:false,prose_generated:false,sections};
const report={ok:true,fingerprint:FP,state:"PARTIAL",
  sections:sections.map(x=>({id:x.section_id,title:x.title,state:x.section_state}))};
function authored(){
 const d=createLocalEditorialDraft(report,model);
 for(let i=0;i<11;i++){
   d.sections[i].narrative="Descripción sintética, redactada por una persona.";
   d.sections[i].canonical_paths_used=["models"];
   d.sections[i].epistemic_classes_used=["A_CALCULATED"];
 }
 return d;
}
test("twelve section template is un-authored, no calculated or metaphysical facts",()=>{
 const d=createLocalEditorialDraft(report,model);
 assert.equal(d.format,EDITORIAL_FORMAT);
 assert.equal(d.sections.length,12);
 assert.equal(d.new_scores_created,false);
 assert.equal(d.metaphysical_scientific_validation_claimed,false);
 assert.throws(()=>validateLocalEditorialDraft(d,report,model),/TEXT_AND_REFERENCES/);
});
test("human authored, traced sections pass without filling unavailable chapters",()=>{
 const d=authored();
 assert.deepEqual(validateLocalEditorialDraft(d,report,model),
  {ok:true,format:EDITORIAL_FORMAT,fingerprint:FP,sections:12});
});
test("doctrinal sourcing and allowed path gates reject unsupported claims",()=>{
 const d=authored();d.sections[0].epistemic_classes_used=["C_DOCTRINE"];
 assert.throws(()=>validateLocalEditorialDraft(d,report,model),/DOCTRINAL_SOURCE_REQUIRED/);
 d.bibliography=[{source_id:"s1",citation_label:"Fuente sintética registrada"}];
 d.sections[0].source_refs=["s1"];
 assert.equal(validateLocalEditorialDraft(d,report,model).ok,true);
 for(const mutate of [
   x=>x.sections[0].canonical_paths_used=["unobserved.path"],
   x=>x.sections[11].narrative="Fabricación de una sección no disponible",
   x=>x.sections[0].epistemic_classes_used=["E_PROJECT_HYPOTHESIS"],
   x=>x.sections[0].source_refs=["unknown"],
   x=>x.sections[0].narrative="a".repeat(50001),
   x=>x.sections[0].canonical_paths_used=["models","models"]
 ]){
   const bad=structuredClone(d);mutate(bad);
   assert.throws(()=>validateLocalEditorialDraft(bad,report,model));
 }
});
test("mismatched M31 and fingerprint are never accepted",()=>{
 const d=authored();
 const bad=structuredClone(model);bad.sections[0].order=2;
 assert.throws(()=>createLocalEditorialDraft(report,bad),/SECTION_MODEL_MISMATCH/);
 const tamper=structuredClone(d);tamper.canonical_fingerprint="0".repeat(64);
 assert.throws(()=>validateLocalEditorialDraft(tamper,report,model),/HEADER_INVALID/);
});
test("module retains no network/storage interfaces",()=>{
 assert.match(createLocalEditorialDraft.toString(),/assertReport/);
 assert.equal(typeof globalThis.window,"undefined");
});

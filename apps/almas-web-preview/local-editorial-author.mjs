/** Local-only experimental authoring of 12 M31 sections.
 * This module never calls fetch, storage, LLMs or any remote endpoint.
 * The Python editorial validator remains the authoritative publication gate.
 */
import {SECTION_IDS} from "./report-view.mjs";
export const EDITORIAL_FORMAT = "ALMAS_LOCAL_EDITORIAL_12_V1";
const VALID_CLASSES = new Set([
  "A_CALCULATED","B_TECHNIQUE","C_DOCTRINE",
  "D_CONTEMPORARY_USAGE","E_PROJECT_HYPOTHESIS"
]);
const isObject = v => v!==null && typeof v==="object" && !Array.isArray(v);
const fail = code => {throw new Error(code);};
const noDuplicates = items => Array.isArray(items) && new Set(items).size===items.length;
const strings = values => Array.isArray(values) && values.every(v=>typeof v==="string");
function assertReport(report, model) {
  if(!isObject(report)||report.ok!==true||
     !["READY","PARTIAL"].includes(report.state)||
     !/^[a-f0-9]{64}$/.test(report.fingerprint||""))
    fail("EDITORIAL_OFFICIAL_REPORT_REQUIRED");
  if(!isObject(model)||!Array.isArray(model.sections)||
     model.sections.length!==SECTION_IDS.length||
     model.report_state!==report.state||
     model.canonical_fingerprint!==report.fingerprint||
     model.canonical_fingerprint_verified!==true||
     model.canonical_values_mutated!==false||
     model.canonical_values_embedded!==false||
     model.prose_generated!==false)
    fail("EDITORIAL_M31_INTEGRITY_INVALID");
  for(let i=0;i<SECTION_IDS.length;i++){
    const spec=model.sections[i],summary=report.sections?.[i];
    if(!isObject(spec)||spec.section_id!==SECTION_IDS[i]||spec.order!==i+1||
       !isObject(summary)||summary.id!==spec.section_id||
       summary.title!==spec.title||summary.state!==spec.section_state||
       !Array.isArray(spec.available_paths)||!Array.isArray(spec.epistemic_classes_allowed))
      fail("EDITORIAL_SECTION_MODEL_MISMATCH");
  }
}
export function createLocalEditorialDraft(report,model){
  assertReport(report,model);
  return {
    format:EDITORIAL_FORMAT,
    canonical_fingerprint:report.fingerprint,
    report_state:report.state,
    language:"es",
    metaphysical_scientific_validation_claimed:false,
    new_calculations_performed:false,
    new_scores_created:false,
    bibliography:[],
    sections:model.sections.map(spec=>({
      section_id:spec.section_id,title:spec.title,narrative:"",
      canonical_paths_used:[],epistemic_classes_used:[],
      source_refs:[],
      limitations:["Borrador pendiente de autoría con evidencia trazable."]
    }))
  };
}
export function validateLocalEditorialDraft(draft,report,model) {
  assertReport(report,model);
  if(!isObject(draft)||draft.format!==EDITORIAL_FORMAT||
     draft.canonical_fingerprint!==report.fingerprint||
     draft.report_state!==report.state||draft.language!=="es"||
     draft.metaphysical_scientific_validation_claimed!==false||
     draft.new_calculations_performed!==false||draft.new_scores_created!==false)
    fail("EDITORIAL_HEADER_INVALID");
  const b=draft.bibliography;
  if(!Array.isArray(b)||!b.every(x=>isObject(x)&&typeof x.source_id==="string"&&
     x.source_id.trim()!==""&&typeof x.citation_label==="string"&&
     x.citation_label.trim()!=="")||!noDuplicates(b.map(x=>x.source_id)))
    fail("EDITORIAL_BIBLIOGRAPHY_INVALID");
  if(!Array.isArray(draft.sections)||draft.sections.length!==SECTION_IDS.length)
    fail("EDITORIAL_SECTIONS_INVALID");
  const sourceIds=new Set(b.map(x=>x.source_id));
  for(let i=0;i<SECTION_IDS.length;i++){
    const section=draft.sections[i],spec=model.sections[i];
    if(!isObject(section)||section.section_id!==spec.section_id||
       section.title!==spec.title)fail("EDITORIAL_SECTION_MISMATCH");
    const {narrative,canonical_paths_used:paths,epistemic_classes_used:classes,
           source_refs:refs,limitations}=section;
    if(typeof narrative!=="string"||narrative.length>50000||
       !strings(paths)||!noDuplicates(paths)||!paths.every(x=>spec.available_paths.includes(x))||
       !strings(classes)||!noDuplicates(classes)||
       !classes.every(x=>VALID_CLASSES.has(x)&&spec.epistemic_classes_allowed.includes(x))||
       !strings(refs)||!noDuplicates(refs)||!refs.every(x=>sourceIds.has(x))||
       !strings(limitations))
      fail("EDITORIAL_SECTION_PROVENANCE_INVALID");
    if(spec.section_state==="NOT_AVAILABLE"){
      if(narrative||paths.length||classes.length||refs.length)
        fail("EDITORIAL_UNAVAILABLE_CANNOT_BE_AUTHORED");
    }else{
      if(!narrative.trim()||!paths.length||!classes.length)
        fail("EDITORIAL_AVAILABLE_REQUIRES_TEXT_AND_REFERENCES");
    }
    if(classes.some(c=>c==="C_DOCTRINE"||c==="D_CONTEMPORARY_USAGE")&&!refs.length)
      fail("EDITORIAL_DOCTRINAL_SOURCE_REQUIRED");
  }
  return {ok:true,format:EDITORIAL_FORMAT,fingerprint:report.fingerprint,
          sections:draft.sections.length};
}

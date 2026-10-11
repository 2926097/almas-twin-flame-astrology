import test from "node:test";
import assert from "node:assert/strict";
import {buildEvidenceGraph} from "../evidence-graph.mjs";
import {chartAvailability,selectNatalChart,selectRelationshipChart,selectVedicChart,selectDraconicChart,describePlacement} from "../astrology-view.mjs";
import {assessReportTriplet,createLocalReportHtml,SECTION_IDS,parseContractJsonStrict} from "../report-view.mjs";

test("dependency graph edges derive only from explicit canonical roots",()=>{
  const c={
    evidence:[
      {evidence_id:"ROOT:A",dependency_families:["F1","F2"],strength:0.6},
      {evidence_id:"ROOT:B",dependency_families:["F1"],strength:null}
    ],
    counterevidence:[
      {id:"C1",model:"LG",dependency_family:"F1",evidence_refs:["ROOT:A","ROOT:ABSENT"]}
    ]
  };
  const before=JSON.stringify(c),g=buildEvidenceGraph(c);
  assert.equal(g.sourceRootCount,2);
  assert.equal(g.sourceCounterCount,1);
  assert.equal(g.edges.filter(x=>x.type==="HAS_DEPENDENCY").length,3);
  assert.equal(g.edges.filter(x=>x.type==="REFERENCES_ROOT").length,1);
  assert.equal(g.edges.filter(x=>x.type==="CONTRADICTS_MODEL").length,1);
  assert.equal(JSON.stringify(c),before);
  assert.ok(g.nodes.every(x=>!Object.keys(x).includes("strength")));
});
test("large graph bounded with total source counts and no fabricated independence",()=>{
  const c={evidence:Array.from({length:500},(_,i)=>({evidence_id:"ROOT:"+i,dependency_families:["SHARED"]})),counterevidence:[]};
  const g=buildEvidenceGraph(c,{maxNodes:21,maxEdges:3});
  assert.ok(g.nodes.length<=21);assert.ok(g.edges.length<=3);
  assert.equal(g.sourceRootCount,500);assert.equal(g.truncated,true);
  assert.match(g.meaning,/not independent/);
});
test("chart availability does not invent composite Davison or missing modalities",()=>{
  const out=chartAvailability({natal_context:{subjects:{A:{point_signs:{}}}}});
  assert.equal(out.find(x=>x.key==="natal_context").state,"DECLARED");
  assert.equal(out.find(x=>x.key==="composite").state,"NOT_AVAILABLE");
  assert.equal(out.find(x=>x.key==="davison").state,"NOT_AVAILABLE");
});
test("natal chart preserves original longitude, sign, house, retrograde metadata",()=>{
  const input={natal_context:{subjects:{X:{
    timed:true,
    point_signs:{Mars:{sign:"Aries",longitude:30.5,decan:"II",retrograde:true},Moon:"Tauro"},
    house_placements:{Mars:{house:3},Moon:{house:1}},
    rulerships:{Mars:"Escorpio"},house_cusps:{"1":75}
  }}}};
  const before=JSON.stringify(input),chart=selectNatalChart(input,"X");
  assert.equal(chart.subject,"X");assert.equal(chart.timed,true);
  const mars=chart.points.find(x=>x.name==="Mars");
  const row=describePlacement(mars);
  assert.equal(row.longitude,"30.5°");assert.equal(row.decan,"II");
  assert.equal(row.retrograde,"Sí");assert.equal(row.house,"3");
  const moon=chart.points.find(x=>x.name==="Moon");
  assert.equal(moon.longitude,null);
  assert.equal(JSON.stringify(input),before);
});
test("missing natal chart never computes a position",()=>{
  const chart=selectNatalChart({},"X");
  assert.equal(chart.available,false);
  assert.deepEqual(chart.points,[]);
});
const fp="a".repeat(64);
const validGate={
  state:"PARTIAL",reportable:true,canonical_values_mutated:false,
  canonical_fingerprint:fp,degradation_reasons:["EXECUTION_TRACE_UNAVAILABLE"]
};
const validModel={
  report_state:"PARTIAL",canonical_values_mutated:false,canonical_values_embedded:false,
  canonical_fingerprint_verified:true,canonical_fingerprint:fp,prose_generated:false,
  sections:SECTION_IDS.map((id,i)=>({section_id:id,order:i+1,title:id,
    section_state:"PARTIAL",missing_required_paths:[],missing_optional_paths:[],
    epistemic_classes_allowed:["A_CALCULATED"]}))
};
const good=()=>({ok:true,kind:"JSON_SCHEMA_DRAFT_2020_12"});
const hash=async()=>({ok:true,hash:fp});
test("local M30/M31 report requires three complete validations and the exact fingerprint",async()=>{
  const result=await assessReportTriplet({},validGate,validModel,{validate:good,digest:hash});
  assert.equal(result.ok,true);assert.equal(result.state,"PARTIAL");
  assert.equal(result.sections.length,12);assert.equal(result.narrativeGenerated,false);
  const exported=createLocalReportHtml(result);
  assert.match(exported,/S12_PHASE_DYNAMICS/);
  assert.match(exported,/No se ha generado narrativa/);
});
test("report gate denies absent offline schema, invalid schemas, tampered fingerprint and bad order",async()=>{
  assert.equal((await assessReportTriplet({},validGate,validModel,{})).ok,false);
  assert.equal((await assessReportTriplet({},validGate,validModel,{validate:()=>({ok:false})})).ok,false);
  assert.equal((await assessReportTriplet({},validGate,validModel,{validate:good,digest:async()=>({ok:true,hash:"b".repeat(64)})})).ok,false);
  const invalid={...validModel,sections:validModel.sections.slice().reverse()};
  assert.equal((await assessReportTriplet({},validGate,invalid,{validate:good,digest:hash})).ok,false);
});
test("report refuses HTML export without verified gate and escapes document labels",async()=>{
  assert.throws(()=>createLocalReportHtml({ok:false}),/cannot be exported/);
  const copy={...validModel,sections:validModel.sections.map(x=>({...x}))};
  copy.sections[0].title="<script>malicious</script>";
  const res=await assessReportTriplet({},validGate,copy,{validate:good,digest:hash});
  const html=createLocalReportHtml(res);
  assert.ok(!html.includes("<script>malicious</script>"));
  assert.ok(html.includes("&lt;script&gt;malicious&lt;/script&gt;"));
});
test("blocked M30 cannot be promoted by a model reporting READY",async()=>{
  const b={...validGate,state:"BLOCKED",reportable:false};
  const result=await assessReportTriplet({},b,validModel,{validate:good,digest:hash});
  assert.equal(result.ok,false);
  assert.equal(result.state,"BLOCKED");
});

test("composite and Davison use actual relationship_field positions without adding houses",()=>{
  const c={relationship_field:{
    composite:{positions:{Sun:{longitude:34.2,sign:"TAURUS"}}},
    davison:{positions:{Moon:{longitude:120.2,sign:"LEO"}},house_placements:{Moon:4},house_cusps:{}}
  }};
  const modes=chartAvailability(c);
  assert.equal(modes.find(x=>x.key==="composite").state,"DECLARED");
  assert.equal(modes.find(x=>x.key==="davison").state,"DECLARED");
  const composite=selectRelationshipChart(c,"composite");
  assert.equal(composite.points[0].longitude,34.2);
  assert.equal(composite.points[0].house,null);
  const davison=selectRelationshipChart(c,"davison");
  assert.equal(davison.points[0].house,4);
  assert.equal(davison.points[0].longitude,120.2);
});
test("Vedic D1/D9 display only provided sidereal positions without external validation claim",()=>{
  const c={vedic:{charts:[{d1:{Moon:{longitude:48.5,sign:1}},d9:{Moon:{longitude:210.5,sign:7}}}]}};
  const d1=selectVedicChart(c,"d1"),d9=selectVedicChart(c,"d9");
  assert.equal(d1.points[0].sign,"Tauro");
  assert.equal(d9.points[0].longitude,210.5);
  assert.equal(d9.points[0].retrograde,null);
  assert.equal(selectVedicChart(c,"d7").available,false);
});

test("Draconic M10 coordinates remain exactly as declared, without nodal recalculation",()=>{
  const c={draconic_context:{individual:{charts:{PersonA:{positions:{Sun:{longitude:23.5,sign:"ARIES",source_longitude:173.5}},houses:{"1":10.25}}}}}};
  const first=selectDraconicChart(c,"PersonA");
  assert.equal(first.available,true);
  assert.equal(first.points[0].longitude,23.5);
  assert.equal(first.points[0].origin,"draconic_context.individual.charts[PersonA].positions.Sun");
  assert.equal(first.houses[0].longitude,10.25);
  assert.equal(selectDraconicChart({},"PersonA").available,false);
});


test("strict M30/M31 parser rejects duplicate keys, including nested keys",()=>{
  assert.deepEqual(parseContractJsonStrict('{"state":"PARTIAL","reportable":true}'),
    {state:"PARTIAL",reportable:true});
  assert.throws(()=>parseContractJsonStrict('{"reportable":true,"reportable":false}'),/Duplicate JSON key/);
  assert.throws(()=>parseContractJsonStrict('{"sections":[{"order":1,"order":2}]}'),/Duplicate JSON key/);
  assert.throws(()=>parseContractJsonStrict('{"state":"READY",}'));
});

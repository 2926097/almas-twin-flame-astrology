import {structuralPreflight,formatOriginal} from "./validator.mjs";
import {selectRootRows,selectCounterRows,selectLimitations,displayValue} from "./local-inspection.mjs";
import {buildEvidenceGraph,renderEvidenceGraph} from "./evidence-graph.mjs";
import {chartAvailability,selectChartMode,drawNatalWheel,describePlacement} from "./astrology-view.mjs";
import {assessReportTriplet,createLocalReportHtml} from "./report-view.mjs";

async function fullSchemaValidate(doc,name="canonical-analysis.schema.json"){
  try {
    const mod=await import("./full-schema-validator.mjs");
    return mod.validateAlmasFull(doc,name);
  } catch {
    return {ok:false,kind:"SCHEMA_ENGINE_UNAVAILABLE",errors:[{path:"$",message:"Validador integral local no compilado. No se admite el archivo."}]};
  }
}

const $=id=>document.getElementById(id),maxBytes=5*1024*1024;
let loadedCanonical=null,loadEpoch=0;
const LOCAL_PAGE_SIZE=80;
let verifiedReport=null,reportEpoch=0;

function renderAdvanced(){
  if(!loadedCanonical)return;
  const graph=buildEvidenceGraph(loadedCanonical);
  $("graphSummary").textContent=graph.nodes.length+" nodos · "+graph.edges.length+" enlaces documentales."+
    (graph.truncated?" Visualización limitada.":"")+
    " Raíces originales: "+graph.sourceRootCount+". No equivalen a observaciones independientes.";
  renderEvidenceGraph($("graphSvg"),graph,$("graphDetail"));

  const modes=chartAvailability(loadedCanonical);
  $("chartAvailability").textContent=modes.map(m=>m.label+": "+(m.state==="DECLARED"?"declarada":"sin dato canónico")).join(" · ");
  const subjects=Object.keys(loadedCanonical.natal_context?.subjects||{}).sort();
  const selector=$("natalSubject");
  selector.replaceChildren();
  for(const id of subjects){
    const option=document.createElement("option");option.value=id;option.textContent=id;selector.appendChild(option);
  }
  renderSelectedNatal();
}

function renderSelectedNatal(){
  $("astroRows").replaceChildren();$("natalWheel").replaceChildren();
  if(!loadedCanonical)return;
  const chart=selectChartMode(loadedCanonical,$("chartMode").value,$("natalSubject").value);
  if(!chart.available){$("chartSummary").textContent=chart.reason;return}
  $("chartSummary").textContent="Sujeto "+chart.subject+" · "+(chart.timed?"Datos cronometrados declarados":"Sin hora certificada")+
    " · "+chart.points.length+" puntos documentados.";
  const visual=drawNatalWheel($("natalWheel"),chart);
  $("chartSummary").textContent+=" Longitudes representables: "+visual.renderedPoints+
    ". Sin coordenada: "+visual.missingCoordinates+".";
  for(const p of chart.points){
    const row=describePlacement(p);
    appendRow("astroRows",[row.name,row.sign,row.house,row.decan,row.ruler,row.retrograde,row.longitude]);
  }
}
$("natalSubject").addEventListener("change",renderSelectedNatal);
$("chartMode").addEventListener("change",renderSelectedNatal);
function resetReport(){
  reportEpoch++;
  verifiedReport=null;
  $("exportDocument").disabled=true;
  $("reportStatus").textContent="Sin validar.";
  $("reportSections").replaceChildren();
}
for(const id of ["m30File","m31File"])$(id).addEventListener("change",resetReport);
$("verifyDocument").addEventListener("click",async()=>{
  resetReport();
  const token=loadEpoch,reportToken=reportEpoch;
  if(!loadedCanonical){
    $("reportStatus").textContent="Primero importa un canonical válido.";return;
  }
  try{
    const a=$("m30File").files?.[0],b=$("m31File").files?.[0];
    if(!a||!b)throw Error("Se requieren ambas salidas oficiales: M30 y M31.");
    for(const file of [a,b])if(file.size>maxBytes||!/\.json$/i.test(file.name))throw Error("Archivo incompatible o mayor de 5 MB");
    const [m30,m31]=await Promise.all([a.text(),b.text()]);
    if(token!==loadEpoch||reportToken!==reportEpoch)return;
    const gate=JSON.parse(m30),model=JSON.parse(m31);
    const check=await assessReportTriplet(loadedCanonical,gate,model,{validate:(d,name)=>{
      // The pinned validator module is imported once prior to the assessment.
      return globalSchemaValidator(d,name);
    }});
    if(token!==loadEpoch||reportToken!==reportEpoch)return;
    if(!check.ok)throw Error(check.reason);
    verifiedReport=check;
    $("reportStatus").textContent="M30/M31 "+check.state+
      " · huella validada · documento declarativo, sin narrativa generada.";
    $("exportDocument").disabled=false;
    for(const section of check.sections){
      const p=document.createElement("p");
      p.textContent=section.id+" — "+section.title+" · "+section.state+
        (section.requiredMissing.length?" · faltan "+section.requiredMissing.join(", "):"");
      $("reportSections").appendChild(p);
    }
  }catch(e){if(token!==loadEpoch||reportToken!==reportEpoch)return;$("reportStatus").textContent="BLOQUEADO: "+(e.message||"Error al verificar salidas");}
});
let globalSchemaValidator=()=>({ok:false});
async function ensureValidatorLoaded(){
  const module=await import("./full-schema-validator.mjs");
  if(typeof module.validateAlmasFull!=="function")throw Error("Validador sin contrato");
  globalSchemaValidator=module.validateAlmasFull;
}
$("exportDocument").addEventListener("click",()=>{
  if(!verifiedReport?.ok||$("exportDocument").disabled)return;
  const html=createLocalReportHtml(verifiedReport);
  const url=URL.createObjectURL(new Blob([html],{type:"text/html;charset=utf-8"}));
  const link=document.createElement("a");link.href=url;link.download="almas-m31-modelo-local.html";
  document.body.appendChild(link);link.click();link.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
});

function appendRow(parent, values) {
  const row=document.createElement("tr");
  for(const value of values){const td=document.createElement("td");td.textContent=displayValue(value);row.appendChild(td)}
  $(parent).appendChild(row);
}
function renderLocalEvidence(){
  if(loadedCanonical===null)return;
  for(const id of ["rootRows","counterRows","limitationRows"])$(id).replaceChildren();
  const roots=selectRootRows(loadedCanonical.evidence,{state:$("rootState").value,query:$("rootQuery").value,limit:LOCAL_PAGE_SIZE});
  $("rootCount").textContent="Se muestran "+roots.rows.length+" de "+roots.matchingCount+" raíces coincidentes ("+roots.sourceCount+" declaradas)."+(roots.truncated?" Vista limitada a 80.":"");
  for(const root of roots.rows)appendRow("rootRows",[root.id,root.state,root.strength,root.coreEligible?"Sí":"No",root.dependencyFamilies.join(", ")||"Ninguna declarada",root.contactCount]);
  const counter=selectCounterRows(loadedCanonical.counterevidence,{model:$("counterModel").value,limit:LOCAL_PAGE_SIZE});
  $("counterCount").textContent="Se muestran "+counter.rows.length+" de "+counter.matchingCount+" contraevidencias coincidentes ("+counter.sourceCount+" declaradas)."+(counter.truncated?" Vista limitada a 80.":"");
  for(const rec of counter.rows)appendRow("counterRows",[rec.id,rec.model,rec.kind,rec.family,rec.severity,rec.essential?"Sí":"No",rec.referenceCount]);
  const limitations=selectLimitations(loadedCanonical.limitations,LOCAL_PAGE_SIZE);
  $("limitationCount").textContent="Se muestran "+limitations.rows.length+" de "+limitations.count+" limitaciones declaradas."+(limitations.truncated?" Vista limitada a 80.":"");
  for(const entry of limitations.rows){const item=document.createElement("li");item.textContent=entry;$("limitationRows").appendChild(item)}
}
for(const id of ["rootState","counterModel"])$(id).addEventListener("change",renderLocalEvidence);
$("rootQuery").addEventListener("input",renderLocalEvidence);
function cell(parent,title,value){const box=document.createElement("div");box.className="card";const a=document.createElement("small");a.textContent=title;const b=document.createElement("div");b.className="value";b.textContent=formatOriginal(value);box.append(a,b);$(parent).append(box)}
function clear(){loadEpoch++;loadedCanonical=null;resetReport();$("m30File").value="";$("m31File").value="";$("chartMode").value="natal";$("natalSubject").replaceChildren();$("astroRows").replaceChildren();$("natalWheel").replaceChildren();$("graphSvg").replaceChildren();for(const id of ["graphSummary","graphDetail","chartSummary","chartAvailability"])$(id).textContent="";for(const id of ["context","indices","models","audit","rootRows","counterRows","limitationRows"])$(id).replaceChildren();$("rootState").value="ALL";$("rootQuery").value="";$("counterModel").value="ALL";for(const id of ["rootCount","counterCount","limitationCount"])$(id).textContent="";$("results").hidden=true;$("status").textContent="No se ha seleccionado archivo.";$("status").className=""}
function show(d){cell("context","Schema",d.schema_version);cell("context","Perfil",d.analysis_profile);cell("context","Modo",d.analysis_mode);cell("context","Backend astronómico",d.astronomy_backend.state);for(const id of ["IDD","IAT","ICC","IRC","ICE"])cell("indices",id,d.indices[id]);for(const id of ["AF","KA","AG","LG"]){const m=d.models[id],tr=document.createElement("tr");for(const v of [id,m.state,m.iem,m.ice,m.supported_gate]){const td=document.createElement("td");td.textContent=formatOriginal(v);tr.append(td)}$("models").append(tr)}cell("audit","Raíces declaradas (no independientes por definición)",d.evidence.length);cell("audit","Contraevidencias",d.counterevidence.length);cell("audit","Limitaciones",d.limitations.length);cell("audit","ICE evaluable",d.counterevidence_state.ice_evaluable);cell("audit","Atacires SHADOW",d.temporal.atacires_shadow===undefined?"No presente":"Presente, sin promoción");loadedCanonical=d;renderLocalEvidence();renderAdvanced();$("results").hidden=false}
$("clear").addEventListener("click",()=>{$("file").value="";clear()});
$("file").addEventListener("change",async()=>{const f=$("file").files?.[0];clear();if(!f)return;const token=loadEpoch;try{if(f.size>maxBytes)throw Error("El archivo supera 5 MB");if(!/\.json$/i.test(f.name))throw Error("Se requiere extensión .json");const raw=await f.text();if(token!==loadEpoch)return;const d=JSON.parse(raw),gate=structuralPreflight(d);if(!gate.ok)throw Error(gate.errors.slice(0,5).map(e=>e.path+": "+e.reason).join("; "));await ensureValidatorLoaded();const full=await fullSchemaValidate(d);if(token!==loadEpoch)return;if(!full.ok)throw Error("JSON Schema oficial: "+(full.errors?.slice(0,3).map(e=>e.path+" "+e.message).join("; ")||"fallo"));show(d);$("status").textContent="JSON Schema Draft 2020-12 local: PASS. No sustituye M30/M31.";$("status").className="ok"}catch(e){if(token!==loadEpoch)return;$("status").textContent="Archivo rechazado: "+(e.message||"error");$("status").className="error"}});

/* Optional synthetic engine connectivity test. No local JSON or natal data is transmitted. */
$("runDemo").addEventListener("click", async () => {
  const button = $("runDemo");
  button.disabled = true;
  $("demoResult").hidden = true;
  $("demoStatus").textContent = "Consultando el servicio sintético protegido…";
  try {
    const response = await fetch("/api/synthetic", {
      method: "GET", cache: "no-store", credentials: "same-origin",
      headers: { "Accept": "application/json" }
    });
    if (!response.ok) throw new Error("La conexión de prueba no está disponible (" + response.status + ")");
    const payload = await response.json();
    if (payload.kind !== "ALMAS_SYNTHETIC_ENGINE_RESULT_V1" ||
        payload.synthetic !== true || payload.canonical_analysis !== false ||
        payload.engine_result?.input_mode !== "PRECOMPUTED_PILLARS") {
      throw new Error("La respuesta no cumple el contrato sintético.");
    }
    const lines = ["Motor: " + String(payload.engine_result.public_version),
      "Modo: PRECOMPUTED_PILLARS (sin astronomía ni M30)",
      "Fixture: público, sintético",
      "", "Índices calculados por el núcleo, no por el navegador:"];
    for (const key of ["AF", "KA", "AG", "LG"]) {
      const result = payload.engine_result.models?.[key];
      lines.push(key + ": IEM_final=" + (result?.iem_final ?? "NO EVALUABLE") +
        " | ICE=" + (result?.ice ?? "NO EVALUABLE") +
        " | gate=" + String(result?.supported_gate ?? "NO EVALUABLE"));
    }
    $("demoResult").textContent = lines.join("\n");
    $("demoResult").hidden = false;
    $("demoStatus").textContent = "Motor Python conectado para datos sintéticos. No es análisis canónico ni inferencia metafísica.";
    $("demoStatus").className = "ok";
  } catch (error) {
    $("demoStatus").textContent = error.message || "Conexión no disponible.";
    $("demoStatus").className = "error";
  } finally {
    button.disabled = false;
  }
});

/* Entirely synthetic M30/M31 demonstration; no uploaded canonical is sent. */
$("runCanonicalDemo").addEventListener("click", async () => {
  const button = $("runCanonicalDemo");
  button.disabled = true;
  $("canonicalDemoStatus").textContent = "Verificando esquema, M30 y M31 de un fixture público sintético…";
  $("canonicalDemoResult").hidden = true;
  try {
    const response = await fetch("/api/canonical-demo", {
      method: "GET", cache: "no-store", credentials: "same-origin",
      headers: { Accept: "application/json" }
    });
    if (!response.ok) throw new Error("No se pudo comprobar el servicio M30/M31 (" + response.status + ").");
    const data = await response.json();
    if (data.kind !== "ALMAS_SYNTHETIC_CANONICAL_GATE_V1" ||
        data.synthetic !== true || data.schema_validation !== "PASS" ||
        data.canonical_returned !== false ||
        !["READY","PARTIAL"].includes(data.m30?.state) ||
        data.m31?.canonical_fingerprint_verified !== true) {
      throw new Error("El servicio no entregó una validación sintética reconocida.");
    }
    const lines = [
      "Esquema canónico Draft 2020-12: PASS",
      "M30, estado técnico: " + data.m30.state,
      "M30, reportable: " + String(data.m30.reportable),
      "M31, fingerprint verificado: " + String(data.m31.canonical_fingerprint_verified),
      "M31, secciones: " + String(data.m31.section_ids?.length),
      "Huella SHA-256: " + data.canonical_fingerprint,
      "Degradaciones: " + (data.m30.degradation_reasons?.join(", ") || "Ninguna"),
      "",
      "Caso sintético. No se analizaron datos personales.",
      "No equivale a validez empírica ni metafísica."
    ];
    $("canonicalDemoResult").textContent = lines.join("\n");
    $("canonicalDemoResult").hidden = false;
    $("canonicalDemoStatus").textContent = "Esquema, M30 y M31 verificados sobre un caso sintético.";
    $("canonicalDemoStatus").className = "ok";
  } catch (err) {
    $("canonicalDemoStatus").textContent = err?.message || "Servicio de prueba no disponible.";
    $("canonicalDemoStatus").className = "error";
  } finally {
    button.disabled = false;
  }
});

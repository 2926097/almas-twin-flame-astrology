import {structuralPreflight,formatOriginal} from "./validator.mjs";
import {selectRootRows,selectCounterRows,selectLimitations,displayValue} from "./local-inspection.mjs";
const $=id=>document.getElementById(id),maxBytes=5*1024*1024;
let loadedCanonical=null,loadEpoch=0;
const LOCAL_PAGE_SIZE=80;
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
function clear(){loadEpoch++;loadedCanonical=null;for(const id of ["context","indices","models","audit","rootRows","counterRows","limitationRows"])$(id).replaceChildren();$("rootState").value="ALL";$("rootQuery").value="";$("counterModel").value="ALL";for(const id of ["rootCount","counterCount","limitationCount"])$(id).textContent="";$("results").hidden=true;$("status").textContent="No se ha seleccionado archivo.";$("status").className=""}
function show(d){cell("context","Schema",d.schema_version);cell("context","Perfil",d.analysis_profile);cell("context","Modo",d.analysis_mode);cell("context","Backend astronómico",d.astronomy_backend.state);for(const id of ["IDD","IAT","ICC","IRC","ICE"])cell("indices",id,d.indices[id]);for(const id of ["AF","KA","AG","LG"]){const m=d.models[id],tr=document.createElement("tr");for(const v of [id,m.state,m.iem,m.ice,m.supported_gate]){const td=document.createElement("td");td.textContent=formatOriginal(v);tr.append(td)}$("models").append(tr)}cell("audit","Raíces declaradas (no independientes por definición)",d.evidence.length);cell("audit","Contraevidencias",d.counterevidence.length);cell("audit","Limitaciones",d.limitations.length);cell("audit","ICE evaluable",d.counterevidence_state.ice_evaluable);cell("audit","Atacires SHADOW",d.temporal.atacires_shadow===undefined?"No presente":"Presente, sin promoción");loadedCanonical=d;renderLocalEvidence();$("results").hidden=false}
$("clear").addEventListener("click",()=>{$("file").value="";clear()});
$("file").addEventListener("change",async()=>{const f=$("file").files?.[0];clear();if(!f)return;try{if(f.size>maxBytes)throw Error("El archivo supera 5 MB");if(!/\.json$/i.test(f.name))throw Error("Se requiere extensión .json");const token=loadEpoch;const raw=await f.text();if(token!==loadEpoch)return;const d=JSON.parse(raw),gate=structuralPreflight(d);if(!gate.ok)throw Error(gate.errors.slice(0,5).map(e=>e.path+": "+e.reason).join("; "));show(d);$("status").textContent="Estructura preliminar admisible. NO es validación integral ni informe M30.";$("status").className="ok"}catch(e){$("status").textContent="Archivo rechazado: "+(e.message||"error");$("status").className="error"}});

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

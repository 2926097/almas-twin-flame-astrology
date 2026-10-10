import {structuralPreflight,formatOriginal} from "./validator.mjs";
const $=id=>document.getElementById(id),maxBytes=5*1024*1024;
function cell(parent,title,value){const box=document.createElement("div");box.className="card";const a=document.createElement("small");a.textContent=title;const b=document.createElement("div");b.className="value";b.textContent=formatOriginal(value);box.append(a,b);$(parent).append(box)}
function clear(){for(const id of ["context","indices","models","audit"])$(id).replaceChildren();$("results").hidden=true;$("status").textContent="No se ha seleccionado archivo.";$("status").className=""}
function show(d){cell("context","Schema",d.schema_version);cell("context","Perfil",d.analysis_profile);cell("context","Modo",d.analysis_mode);cell("context","Backend astronómico",d.astronomy_backend.state);for(const id of ["IDD","IAT","ICC","IRC","ICE"])cell("indices",id,d.indices[id]);for(const id of ["AF","KA","AG","LG"]){const m=d.models[id],tr=document.createElement("tr");for(const v of [id,m.state,m.iem,m.ice,m.supported_gate]){const td=document.createElement("td");td.textContent=formatOriginal(v);tr.append(td)}$("models").append(tr)}cell("audit","Raíces declaradas (no independientes por definición)",d.evidence.length);cell("audit","Contraevidencias",d.counterevidence.length);cell("audit","Limitaciones",d.limitations.length);cell("audit","ICE evaluable",d.counterevidence_state.ice_evaluable);cell("audit","Atacires SHADOW",d.temporal.atacires_shadow===undefined?"No presente":"Presente, sin promoción");$("results").hidden=false}
$("clear").addEventListener("click",()=>{$("file").value="";clear()});
$("file").addEventListener("change",async()=>{const f=$("file").files?.[0];clear();if(!f)return;try{if(f.size>maxBytes)throw Error("El archivo supera 5 MB");if(!/\.json$/i.test(f.name))throw Error("Se requiere extensión .json");const d=JSON.parse(await f.text()),gate=structuralPreflight(d);if(!gate.ok)throw Error(gate.errors.slice(0,5).map(e=>e.path+": "+e.reason).join("; "));show(d);$("status").textContent="Estructura preliminar admisible. NO es validación integral ni informe M30.";$("status").className="ok"}catch(e){$("status").textContent="Archivo rechazado: "+(e.message||"error");$("status").className="error"}});

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

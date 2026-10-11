import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, accessSync } from "node:fs";
import {execFileSync} from "node:child_process";
import {fileURLToPath} from "node:url";
const root = fileURLToPath(new URL("../../../", import.meta.url));

// Minimal DOM for testing the actual imported app.mjs event handlers.
// This is a contract test, not a browser/PW visual certification.
class FakeElement {
  constructor(name = "") {
    this.name = name; this.listeners = {}; this.children = [];
    this.files = []; this.value = ""; this.textContent = "";
    this.className = ""; this.hidden = true; this.disabled = false;
  }
  addEventListener(type, fn) { this.listeners[type] = fn; }
  setAttribute(name, value) { this[name] = String(value); }
  removeAttribute(name) { delete this[name]; }
  replaceChildren() { this.children = []; }
  appendChild(child) { this.children.push(child); return child; }
  append(...children) { this.children.push(...children); }
}
const elements = new Map();
function el(id) {
  if (!elements.has(id)) elements.set(id, new FakeElement(id));
  return elements.get(id);
}
globalThis.document = {
  getElementById: el,
  createElement: type => new FakeElement(type),
  createElementNS: (_ns, type) => new FakeElement(type)
};
await import("../app.mjs");

function canonical() {
  const wire=execFileSync(process.env.ALMA_PYTHON || "python3",["-c",
    "import json;from test_canonical_schema_validation import valid_canonical_analysis;print(json.dumps(valid_canonical_analysis(),ensure_ascii=False))"
  ],{cwd:root,encoding:"utf8",env:{...process.env,PYTHONPATH:"src:tests"}});
  return JSON.parse(wire);
}
function selectFile(file) {
  el("file").files = [file];
  return el("file").listeners.change();
}
function clear() {
  el("clear").listeners.click();
}

test("imported asset list includes every static module and both fixed API functions", () => {
  const readme = readFileSync(new URL("../README.md", import.meta.url), "utf8");
  for (const path of [
    "index.html", "app.mjs", "validator.mjs", "local-inspection.mjs",
    "evidence-graph.mjs", "astrology-view.mjs", "report-view.mjs", "json-lexical-digest.mjs", "birth-request.mjs", "birth-intake.mjs",
    "api/synthetic.js", "api/canonical-demo.js", "vercel.json"
  ]) {
    assert.ok(readme.includes("`" + path + "`"), "missing documented asset " + path);
    accessSync(new URL("../" + path, import.meta.url));
  }
});

test("clearing a session ignores a later rejection of the old File.text()", async () => {
  clear();
  let fail;
  const pending = new Promise((_, reject) => { fail = reject; });
  const old = selectFile({ name: "old.json", size: 16, text: () => pending });
  clear();
  assert.equal(el("status").textContent, "No se ha seleccionado archivo.");
  fail(new Error("STALE_READ_DO_NOT_SHOW"));
  await old;
  assert.equal(el("status").textContent, "No se ha seleccionado archivo.");
  assert.notEqual(el("status").className, "error");
  assert.equal(el("results").hidden, true);
});

test("a stale rejection cannot overwrite a newly rendered canonical", async () => {
  clear();
  let fail;
  const pending = new Promise((_, reject) => { fail = reject; });
  const old = selectFile({ name: "old.json", size: 20, text: () => pending });
  const currentCanonical = canonical();
  const newData = JSON.stringify(currentCanonical);
  await selectFile({ name: "fresh.json", size: newData.length, text: async () => newData });
  assert.equal(el("status").className, "ok");
  assert.equal(el("results").hidden, false);
  const prior = el("status").textContent;
  fail(new Error("OLD_ERROR_MUST_BE_IGNORED"));
  await old;
  assert.equal(el("status").className, "ok");
  assert.equal(el("status").textContent, prior);
  assert.equal(el("results").hidden, false);
  assert.match(el("rootCount").textContent, new RegExp("Se muestran " + currentCanonical.evidence.length + " de " + currentCanonical.evidence.length + " raíces coincidentes"));
  clear();
});

test("a fresh rejection is still shown as an error", async () => {
  clear();
  await selectFile({
    name: "current.json", size: 10,
    text: () => Promise.reject(new Error("CURRENT_READ_FAILED"))
  });
  assert.equal(el("status").className, "error");
  assert.match(el("status").textContent, /CURRENT_READ_FAILED/);
  clear();
});

test("a changed M30 selection invalidates an in-flight stale report verification",async()=>{
  clear();
  const input=JSON.stringify(canonical());
  await selectFile({name:"canonical.json",size:input.length,text:async()=>input});
  assert.equal(el("status").className,"ok");
  let finishOld;
  const pending=new Promise(resolve=>{finishOld=resolve});
  el("m30File").files=[{name:"m30.json",size:100,text:()=>pending}];
  el("m31File").files=[{name:"m31.json",size:100,text:async()=>JSON.stringify({})}];
  const inflight=el("verifyDocument").listeners.click();
  el("m30File").files=[{name:"different-m30.json",size:100,text:async()=>JSON.stringify({})}];
  el("m30File").listeners.change();
  assert.equal(el("reportStatus").textContent,"Sin validar.");
  finishOld(JSON.stringify({state:"PARTIAL"}));
  await inflight;
  assert.equal(el("reportStatus").textContent,"Sin validar.");
  assert.equal(el("exportDocument").disabled,true);
  clear();
});

test("a canonical with duplicate JSON keys is rejected before rendering",async()=>{
  clear();
  const legitimate=JSON.stringify(canonical());
  const repeated='{"canonical_duplicate_guard":1,"canonical_duplicate_guard":2,'+legitimate.slice(1);
  await selectFile({name:"ambiguous-canonical.json",size:Buffer.byteLength(repeated),text:async()=>repeated});
  assert.equal(el("status").className,"error");
  assert.match(el("status").textContent,/Duplicate JSON key/);
  assert.equal(el("results").hidden,true);
  assert.equal(el("exportDocument").disabled,true);
  clear();
});

test("birth intake produces a browser-only request, invalidates changes and erases local fields",async()=>{
  const sample={
    A:{Id:"A",Name:"Synthetic A",Date:"2000-02-29",Time:"05:30",Zone:"Europe/Madrid",Place:"Synthetic",
      Lat:"41",Lon:"-1",Quality:"A",Source:"DOCUMENTARY"},
    B:{Id:"B",Name:"Synthetic B",Date:"2001-04-05",Time:"09:15",Zone:"America/New_York",Place:"Synthetic",
      Lat:"40",Lon:"-73",Quality:"B",Source:"REPORTED"}
  };
  for(const letter of ["A","B"])for(const [suffix,value] of Object.entries(sample[letter]))
    el("birth"+letter+suffix).value=value;
  el("birthProfile").value="FULL_ASTROLOGY";
  el("birthPreset").value="ALMAS_RELATIONAL_STRICT_RESEARCH_V1";
  const oldCreate=URL.createObjectURL,oldRevoke=URL.revokeObjectURL,oldFetch=globalThis.fetch;
  let blob=null,revoked=0,networkCalls=0;
  URL.createObjectURL=file=>{blob=file;return "blob:synthetic-local-contract"};
  URL.revokeObjectURL=()=>{revoked++};
  globalThis.fetch=()=>{networkCalls++;throw Error("PERSONAL_DATA_CANNOT_BE_SENT")};
  try{
    el("birthPrepare").listeners.click();
    assert.equal(el("birthDownload").hidden,false);
    assert.equal(el("birthStatus").className,"ok");
    const payload=JSON.parse(await blob.text());
    assert.equal(payload.request.subjects.length,2);
    assert.equal(payload.request.subjects[0].birth_time,"05:30");
    assert.equal(payload.request.subjects[1].timezone,"America/New_York");
    assert.equal(payload.request.execution_state,"REQUEST_ONLY");
    assert.equal(networkCalls,0);
    el("birthADate").value="2000-03-01";
    el("birthADate").listeners.input();
    assert.equal(el("birthDownload").hidden,true);
    assert.equal(revoked,1);
    el("birthErase").listeners.click();
    assert.equal(el("birthAId").value,"");
    assert.equal(el("birthBTime").value,"");
    assert.equal(el("birthPreset").value,"");
    assert.equal(networkCalls,0);
  }finally{
    URL.createObjectURL=oldCreate;URL.revokeObjectURL=oldRevoke;globalThis.fetch=oldFetch;
  }
});

import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, accessSync } from "node:fs";

// Minimal DOM for testing the actual imported app.mjs event handlers.
// This is a contract test, not a browser/PW visual certification.
class FakeElement {
  constructor(name = "") {
    this.name = name; this.listeners = {}; this.children = [];
    this.files = []; this.value = ""; this.textContent = "";
    this.className = ""; this.hidden = true; this.disabled = false;
  }
  addEventListener(type, fn) { this.listeners[type] = fn; }
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
  createElement: type => new FakeElement(type)
};
await import("../app.mjs");

const model = () => ({
  iem: 10, state: "INSUFFICIENT", core: 0.1, support: null, iem_pre: 10,
  iem_final: null, ice: null, ice_state: "NOT_EVALUABLE", supported_gate: false,
  birth_time_gate_required: false, birth_time_gate_satisfied: false
});
const canonical = () => ({
  schema_version: "1.0.0", analysis_mode: "FULL", analysis_profile: "FULL_ASTROLOGY",
  profile_policy_id: "ALMAS_ANALYSIS_PROFILES_V1",
  astronomy_backend: {
    state: "NOT_AVAILABLE", backend_id: null, backend_version: null,
    provenance_state: "NOT_AVAILABLE", provenance: null
  },
  evidence: [], models: { AF: model(), KA: model(), AG: model(), LG: model() },
  indices: { IDD: null, IAT: null, ICC: null, IRC: null, ICE: null },
  pairwise_idd: {}, coverage: {}, robustness: {}, counterevidence: [],
  counterevidence_state: { ice_evaluable: false }, ontology: {},
  doctrine: [], temporal: {}, limitations: [], assembly: {}
});
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
  const newData = JSON.stringify(canonical());
  await selectFile({ name: "fresh.json", size: newData.length, text: async () => newData });
  assert.equal(el("status").className, "ok");
  assert.equal(el("results").hidden, false);
  const prior = el("status").textContent;
  fail(new Error("OLD_ERROR_MUST_BE_IGNORED"));
  await old;
  assert.equal(el("status").className, "ok");
  assert.equal(el("status").textContent, prior);
  assert.equal(el("results").hidden, false);
  assert.equal(el("rootCount").textContent.includes("0 raíces"), true);
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

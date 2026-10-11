/** Full schema validator compiled locally from official checked-in ALMAS schemas. */
import Ajv2020 from "ajv/dist/2020.js";
import registry from "./schema-registry.generated.mjs";
const BASE = "https://example.invalid/almas/";
const ALLOWED = new Set(["canonical-analysis.schema.json","report-gate-output.schema.json","report-document-model.schema.json"]);
let ajvInstance = null;
const compiled = new Map();
export function validateAlmasFull(document, schemaName) {
  try {
    if (!ALLOWED.has(schemaName)) throw Error("Schema not authorized");
    if (ajvInstance === null) {
      const ajv = new Ajv2020({
        allErrors: true, strict: false, validateFormats: false,
        coerceTypes: false, removeAdditional: false, useDefaults: false,
        loadSchema: undefined
      });
      // All $refs resolve against the bundled in-repo registry, not the network.
      for (const schema of registry) ajv.addSchema(schema);
      ajvInstance = ajv;
    }
    let validator = compiled.get(schemaName);
    if (!validator) {
      validator = ajvInstance.getSchema(BASE + schemaName);
      if (typeof validator !== "function") throw Error("Root schema unavailable");
      compiled.set(schemaName, validator);
    }
    const passed = validator(document);
    return {
      ok: passed === true, kind: "JSON_SCHEMA_DRAFT_2020_12",
      schemaCount: registry.length,
      errors: passed ? [] : (validator.errors || []).slice(0, 30).map(x => ({
        path: String(x.instancePath || "$"), keyword: String(x.keyword),
        // No parameter values or source data are returned from validation.
        message: String(x.message || "Schema constraint failed")
      }))
    };
  } catch {
    // Compile/unresolved refs are service failures, never acceptance.
    return {ok: false, kind: "SCHEMA_ENGINE_UNAVAILABLE", schemaCount: registry.length,
      errors: [{path:"$",keyword:"engine",message:"Offline schema registry or compiler unavailable"}]};
  }
}
\nexport const validateCanonicalFull = document => validateAlmasFull(document, "canonical-analysis.schema.json");\n
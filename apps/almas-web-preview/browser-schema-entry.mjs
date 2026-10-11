/** Full schema validator compiled locally from official checked-in ALMAS schemas. */
import Ajv2020 from "ajv/dist/2020.js";
import registry from "./schema-registry.generated.mjs";
const ROOT_ID = "https://example.invalid/almas/canonical-analysis.schema.json";
let compiled = null;
export function validateCanonicalFull(document) {
  try {
    if (compiled === null) {
      const ajv = new Ajv2020({
        allErrors: true, strict: false, validateFormats: false,
        coerceTypes: false, removeAdditional: false, useDefaults: false,
        loadSchema: undefined
      });
      // All $refs resolve against the bundled in-repo registry, not the network.
      for (const schema of registry) ajv.addSchema(schema);
      const validator = ajv.getSchema(ROOT_ID);
      if (typeof validator !== "function") throw Error("No canonical root schema");
      compiled = validator;
    }
    const passed = compiled(document);
    return {
      ok: passed === true, kind: "JSON_SCHEMA_DRAFT_2020_12",
      schemaCount: registry.length,
      errors: passed ? [] : (compiled.errors || []).slice(0, 30).map(x => ({
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

/**
 * Browser-only projections of ALMAS canonical evidence. No network access,
 * recalculation, indexing, or mutation of original evidence objects.
 *
 * A displayed ROOT is NOT automatically an independent observation:
 * dependent families and contact repetitions must be interpreted separately.
 */
const isRecord = value => value !== null && typeof value === "object" && !Array.isArray(value);
const list = value => Array.isArray(value) ? value : [];
const str = value => typeof value === "string" ? value : "";
const limitTo = value => Number.isInteger(value) ? Math.max(1, Math.min(100, value)) : 80;
const safeQuery = value => str(value).trim().toLocaleLowerCase("es").slice(0, 80);
export const displayValue = value => value === null || value === undefined ?
  "No evaluable" : String(value);

export function selectRootRows(evidence, { state = "ALL", query = "", limit = 80 } = {}) {
  const all = list(evidence).filter(isRecord);
  const normalizedQuery = safeQuery(query);
  const acceptedState = new Set(["ALL", "CALCULATED_CORE", "CALCULATED_SUPPORT_ONLY", "NOT_EVALUABLE"]);
  const filtered = all.filter(root => {
    if (!acceptedState.has(state) || (state !== "ALL" && root.strength_state !== state)) return false;
    const haystack = [root.evidence_id, root.root_id, root.root_key, ...list(root.dependency_families)]
      .filter(x => typeof x === "string").join(" ").toLocaleLowerCase("es");
    return haystack.includes(normalizedQuery);
  }).sort((a, b) => {
    const av = typeof a.strength === "number" && Number.isFinite(a.strength) ? a.strength : -1;
    const bv = typeof b.strength === "number" && Number.isFinite(b.strength) ? b.strength : -1;
    return bv - av || str(a.evidence_id).localeCompare(str(b.evidence_id));
  });
  return {
    sourceCount: all.length,
    matchingCount: filtered.length,
    truncated: filtered.length > limitTo(limit),
    rows: filtered.slice(0, limitTo(limit)).map(root => ({
      id: str(root.evidence_id),
      root: str(root.root_id),
      state: str(root.strength_state),
      strength: root.strength ?? null,
      coreEligible: root.core_eligible === true,
      independentFamilyCount: Number.isInteger(root.independent_family_count) ? root.independent_family_count : null,
      dependencyFamilies: list(root.dependency_families).filter(x => typeof x === "string").slice(),
      pointCount: list(root.point_ids).length,
      relationCount: list(root.relation_ids).length,
      contactCount: list(root.concrete_contacts).length
    }))
  };
}

export function selectCounterRows(counterevidence, { model = "ALL", limit = 80 } = {}) {
  const all = list(counterevidence).filter(isRecord);
  const acceptedModels = new Set(["ALL", "AF", "KA", "AG", "LG"]);
  const filtered = all.filter(record => acceptedModels.has(model) && (model === "ALL" || record.model === model))
    .sort((a, b) => {
      const av = typeof a.severity === "number" && Number.isFinite(a.severity) ? a.severity : -1;
      const bv = typeof b.severity === "number" && Number.isFinite(b.severity) ? b.severity : -1;
      return bv - av || str(a.id).localeCompare(str(b.id));
    });
  return {
    sourceCount: all.length,
    matchingCount: filtered.length,
    truncated: filtered.length > limitTo(limit),
    rows: filtered.slice(0, limitTo(limit)).map(c => ({
      id: str(c.id),
      model: str(c.model),
      kind: str(c.kind),
      family: str(c.dependency_family),
      severity: c.severity ?? null,
      essential: c.essential === true,
      referenceCount: list(c.evidence_refs).length
      // Deliberately omit "note", which may contain free-form/private data.
    }))
  };
}

export function selectLimitations(limitations, limit = 80) {
  const all = list(limitations).filter(x => typeof x === "string");
  return { count: all.length, truncated: all.length > limitTo(limit), rows: all.slice(0, limitTo(limit)) };
}

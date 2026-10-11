/**
 * ALMAS 1.3 local birth intake.
 * Never performs network I/O, geocoding, planetary calculations or scoring.
 * Produces a request consumed by the existing PRIVATE relational Python runner.
 */
export const POLICY_PRESET = "ALMAS_RELATIONAL_STRICT_RESEARCH_V1";
export const PUBLIC_VERSION = "1.26.0";
const PROFILES = new Set(["FULL_ASTROLOGY", "FULL_MULTIDISCIPLINARY", "TEMPORAL", "SOUL_CONTRACT"]);
const RELIABILITY = new Set(["A", "B", "C", "D"]);
const SOURCES = new Set(["DOCUMENTARY", "REPORTED", "RECTIFIED", "UNKNOWN"]);

function textField(raw, label, max = 100) {
  if (typeof raw !== "string") throw Error(label + ": se requiere texto.");
  const value = raw.trim();
  if (!value || value.length > max) throw Error(label + ": debe contener entre 1 y " + max + " caracteres.");
  return value;
}

function dateField(raw, label) {
  const value = textField(raw, label, 10);
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) throw Error(label + ": fecha obligatoria AAAA-MM-DD.");
  const year = Number(match[1]), month = Number(match[2]), day = Number(match[3]);
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (!year || month < 1 || month > 12 || day < 1 || day > days[month - 1])
    throw Error(label + ": fecha gregoriana inválida.");
  return value;
}

function timeField(raw, label) {
  const value = textField(raw, label, 5);
  if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(value)) throw Error(label + ": hora local HH:MM obligatoria.");
  return value;
}

function timezoneField(raw, label) {
  const value = textField(raw, label, 80);
  if (!/^[A-Za-z_]+(?:\/[A-Za-z0-9_+\-]+)+$/.test(value) && value !== "UTC")
    throw Error(label + ": introduce una zona horaria IANA, por ejemplo Europe/Madrid.");
  try { new Intl.DateTimeFormat("es-ES", { timeZone: value }); }
  catch { throw Error(label + ": zona horaria IANA desconocida."); }
  return value;
}

function coordinateField(raw, label, min, max) {
  if (typeof raw === "string" && !raw.trim()) throw Error(label + ": coordenada obligatoria.");
  if (typeof raw !== "string" && typeof raw !== "number") throw Error(label + ": coordenada numérica obligatoria.");
  const value = Number(raw);
  if (!Number.isFinite(value) || value < min || value > max)
    throw Error(label + ": valor fuera del rango " + min + " a " + max + ".");
  return value;
}

function subjectField(raw, index) {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) throw Error("Sujeto " + index + ": datos inválidos.");
  const prefix = "Sujeto " + index + " ";
  const id = textField(raw.id, prefix + "identificador", 64);
  if (!/^[\p{L}\p{N}_-]+$/u.test(id)) throw Error(prefix + "identificador: solo letras, números, guion o guion bajo.");
  const name = typeof raw.display_name === "string" ? raw.display_name.trim() : "";
  if (name.length > 100) throw Error(prefix + "nombre: máximo 100 caracteres.");
  const reliability = textField(raw.time_reliability, prefix + "fiabilidad", 1);
  if (!RELIABILITY.has(reliability)) throw Error(prefix + "fiabilidad: elige A, B, C o D.");
  const source = textField(raw.birth_time_source_class, prefix + "fuente", 20);
  if (!SOURCES.has(source)) throw Error(prefix + "fuente: selecciona una opción válida.");
  const place = typeof raw.place === "string" ? raw.place.trim() : "";
  if (place.length > 120) throw Error(prefix + "lugar: máximo 120 caracteres.");
  return {
    id,
    ...(name ? {display_name: name} : {}),
    birth_date: dateField(raw.birth_date, prefix + "fecha"),
    birth_time: timeField(raw.birth_time, prefix + "hora"),
    timezone: timezoneField(raw.timezone, prefix + "zona"),
    ...(place ? {place} : {}),
    latitude: coordinateField(raw.latitude, prefix + "latitud", -90, 90),
    longitude: coordinateField(raw.longitude, prefix + "longitud", -180, 180),
    time_reliability: reliability,
    birth_time_source_class: source
  };
}

/** Produce only the official REQUEST_ONLY envelope; execution is never implied. */
export function buildRelationalWorkRequest(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) throw Error("Datos de formulario inválidos.");
  if (!PROFILES.has(input.analysis_profile)) throw Error("Selecciona un perfil de análisis admitido.");
  if (input.analysis_policy_profile !== POLICY_PRESET)
    throw Error("Selecciona explícitamente el preset de orbes de investigación aprobado.");
  if (!Array.isArray(input.subjects) || input.subjects.length !== 2)
    throw Error("La solicitud requiere exactamente dos nacimientos.");
  const subjects = input.subjects.map((item, index) => subjectField(item, index + 1));
  if (subjects[0].id === subjects[1].id) throw Error("Los identificadores de las dos personas deben ser distintos.");
  return {
    request: {
      format: "ALMAS_WORK_REQUEST",
      public_version: PUBLIC_VERSION,
      type: "RELATIONAL",
      analysis_profile: input.analysis_profile,
      analysis_policy_profile: POLICY_PRESET,
      subjects,
      events: [],
      execution_state: "REQUEST_ONLY"
    }
  };
}

export function serializeRelationalWorkRequest(input) {
  return JSON.stringify(buildRelationalWorkRequest(input), null, 2) + "\n";
}

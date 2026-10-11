import { buildRelationalWorkRequest } from "./birth-request.mjs";

const $ = id => document.getElementById(id);
const FIELDS = ["Id", "Name", "Date", "Time", "Zone", "Place", "Lat", "Lon", "Quality", "Source"];
function readSubject(letter) {
  const value = suffix => $( "birth" + letter + suffix ).value;
  return {
    id: value("Id"),
    display_name: value("Name"),
    birth_date: value("Date"),
    birth_time: value("Time"),
    timezone: value("Zone"),
    place: value("Place"),
    latitude: value("Lat"),
    longitude: value("Lon"),
    time_reliability: value("Quality"),
    birth_time_source_class: value("Source")
  };
}

/** Keep the file and natal data in browser memory. Never fetch or POST. */
export function registerBirthIntake() {
  let downloadUrl = null;
  const link = $("birthDownload");
  const status = $("birthStatus");
  const invalidate = () => {
    if (downloadUrl) URL.revokeObjectURL(downloadUrl);
    downloadUrl = null;
    link.hidden = true;
    link.removeAttribute("href");
    status.textContent = "Solicitud aún no preparada. Los datos permanecen en este navegador.";
    status.className = "muted";
  };
  for (const letter of ["A", "B"]) {
    for (const suffix of FIELDS) {
      $( "birth" + letter + suffix ).addEventListener("input", invalidate);
      $( "birth" + letter + suffix ).addEventListener("change", invalidate);
    }
  }
  $("birthProfile").addEventListener("change", invalidate);
  $("birthPreset").addEventListener("change", invalidate);
  $("birthPrepare").addEventListener("click", () => {
    invalidate();
    try {
      const request = buildRelationalWorkRequest({
        analysis_profile: $("birthProfile").value,
        analysis_policy_profile: $("birthPreset").value,
        subjects: [readSubject("A"), readSubject("B")]
      });
      const text = JSON.stringify(request, null, 2) + "\n";
      downloadUrl = URL.createObjectURL(new Blob([text], {type: "application/json"}));
      link.href = downloadUrl;
      link.download = "almas-relational-request.local.json";
      link.hidden = false;
      status.textContent = "REQUEST_ONLY válido localmente. Descarga la solicitud y ejecútala con el runner privado; aún no se han calculado cartas ni índices.";
      status.className = "ok";
    } catch (error) {
      status.textContent = "No se ha creado la solicitud: " + (error?.message || "datos no válidos");
      status.className = "error";
    }
  });
  $("birthErase").addEventListener("click", () => {
    invalidate();
    for (const letter of ["A", "B"]) {
      for (const suffix of FIELDS) $( "birth" + letter + suffix ).value = "";
    }
    $("birthProfile").value = "";
    $("birthPreset").value = "";
    status.textContent = "Formulario local borrado.";
  });
}

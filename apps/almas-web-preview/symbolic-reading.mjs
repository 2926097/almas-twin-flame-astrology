/** ALMAS Web experimental symbolic commentary.
 * Every technical placement is read from canonical via astrology-view.mjs.
 * No geometry, orbs, new aspect/score, psychological diagnosis or ontology.
 * Symbolic semantics are openly E_PROJECT_HYPOTHESIS, not factual evidence.
 */
import {selectNatalChart} from "./astrology-view.mjs";
export const POLICY_ID="ALMAS_SYMBOLIC_EDITORIAL_V1";
const SYMBOLS=Object.freeze({
  SUN:"identidad, vitalidad y expresión de la voluntad",
  MOON:"necesidades emocionales y hábitos de cuidado",
  MERCURY:"comunicación, aprendizaje y razonamiento",
  VENUS:"vínculo, aprecio, gusto y reciprocidad",
  MARS:"acción, deseo, voluntad y límites",
  JUPITER:"ampliación de perspectivas y confianza",
  SATURN:"estructura, responsabilidad y permanencia",
  URANUS:"cambio, autonomía y reformulación",
  NEPTUNE:"imaginación, idealización y disolución de límites",
  PLUTO:"transformación, poder y procesos de profundidad",
  CHIRON:"sensibilidad simbólica ante heridas y aprendizaje",
  JUNO:"acuerdos, compromisos y reciprocidad en vínculos",
  CERES:"cuidado, sostenimiento y separación",
  VESTA:"dedicación, concentración y preservación",
  NORTH_NODE:"dirección simbólica de aprendizaje",
  SOUTH_NODE:"patrones conocidos y recursos adquiridos"
});
const SIGNS=Object.freeze({
  ARIES:"iniciativa y afirmación",TAURUS:"continuidad y materialidad",
  GEMINI:"intercambio y diversidad",CANCER:"cuidado y pertenencia",
  LEO:"creatividad y visibilidad",VIRGO:"discernimiento y detalle",
  LIBRA:"equilibrio y diálogo",SCORPIO:"intensidad y transformación",
  SAGITTARIUS:"exploración y sentido",CAPRICORN:"organización y perseverancia",
  AQUARIUS:"independencia y comunidad",PISCES:"intuición e imaginación"
});
const HOUSE_DOMAINS=Object.freeze({
  1:"presencia e iniciativa personal",2:"recursos y valores",
  3:"comunicación y entorno",4:"raíces y vida privada",
  5:"creatividad y expresión",6:"rutinas y trabajo cotidiano",
  7:"asociaciones y vínculos",8:"intimidad y recursos compartidos",
  9:"creencias y aprendizaje",10:"vocación e imagen pública",
  11:"comunidad y proyectos",12:"retiro y vida interior"
});
const ALIAS=Object.freeze({
 "ARIES":"ARIES","TAURO":"TAURUS","TAURUS":"TAURUS",
 "GÉMINIS":"GEMINI","GEMINIS":"GEMINI","GEMINI":"GEMINI",
 "CÁNCER":"CANCER","CANCER":"CANCER","LEO":"LEO",
 "VIRGO":"VIRGO","LIBRA":"LIBRA","ESCORPIO":"SCORPIO",
 "SCORPIO":"SCORPIO","SAGITARIO":"SAGITTARIUS",
 "SAGITTARIUS":"SAGITTARIUS","CAPRICORNIO":"CAPRICORN",
 "CAPRICORN":"CAPRICORN","ACUARIO":"AQUARIUS",
 "AQUARIUS":"AQUARIUS","PISCIS":"PISCES","PISCES":"PISCES"
});
const ptr=s=>String(s).replace(/~/g,"~0").replace(/\//g,"~1");
const stringsafe=x=>typeof x==="string"?x:"";
function subjectCommentary(canonical,id){
 const chart=selectNatalChart(canonical,id);
 if(!chart.available)return {subject:id,state:"NOT_EVALUABLE",readings:[]};
 const readings=chart.points.map(p=>{
  const key=String(p.name).toUpperCase(),signKey=ALIAS[stringsafe(p.sign).toUpperCase()]||null;
  const functionText=SYMBOLS[key]||null;
  const quality=signKey?SIGNS[signKey]||null:null;
  const domain=Number.isInteger(p.house)?HOUSE_DOMAINS[p.house]||null:null;
  // Use point/decan/regent/retrograde as supplied. No derived positions or orbs.
  const parts=[];
  if(functionText)parts.push("En la interpretación simbólica del proyecto, "+p.name+
   " se asocia a "+functionText+".");
  else parts.push("No hay un significado específico autorizado para "+p.name+
   " en esta política editorial; se ofrece únicamente la posición disponible.");
  if(quality)parts.push("El signo "+p.sign+" introduce el tema de "+quality+".");
  else parts.push("El signo no está disponible en el canónico.");
  if(domain)parts.push("La casa "+p.house+" sitúa la lectura en "+domain+".");
  else parts.push("La casa no es evaluable con los datos actuales.");
  if(p.decan!==null)parts.push("Decanato declarado: "+p.decan+".");
  else parts.push("Decanato no declarado; no se infiere.");
  if(p.ruler!==null)parts.push("Regente declarado: "+p.ruler+".");
  else parts.push("Regente no declarado; no se infiere.");
  if(p.retrograde===true)parts.push("Movimiento retrógrado registrado: lectura simbólica de revisión del tema.");
  else if(p.retrograde===false)parts.push("Movimiento directo registrado.");
  else parts.push("Movimiento retrógrado/directo no evaluable.");
  return {
    subject:id,point:p.name,
    canonical_ref:"/natal_context/subjects/"+ptr(id)+"/point_signs/"+ptr(p.name),
    sign:p.sign,house:p.house,decan:p.decan,ruler:p.ruler,
    retrograde:p.retrograde,
    epistemic_class:"E_PROJECT_HYPOTHESIS",
    interpretation:parts.join(" "),
    has_defined_symbolism:!!functionText,
    is_astronomical_calculation:false,
    claims_empirical_validation:false
  };
 });
 return {subject:id,state:readings.length?"DESCRIPTIVE_SYMBOLIC":"NOT_EVALUABLE",readings};
}
export function buildSymbolicReadings(canonical){
 if(!canonical||typeof canonical!=="object"||Array.isArray(canonical))
   throw new TypeError("CANONICAL_REQUIRED");
 const subjectIds=Object.keys(canonical?.natal_context?.subjects||{}).sort().slice(0,2);
 const subjects=subjectIds.map(id=>subjectCommentary(canonical,id));
 return {
  policy_id:POLICY_ID,epistemic_class:"E_PROJECT_HYPOTHESIS",
  generated_automatically:true,calculated_new_positions:false,
  created_new_scores:false,is_authoritative_authored_report:false,
  metaphysical_classification:"NOT_EVALUABLE",
  limitations:[
   "Asociaciones astrológicas simbólicas, no efectos psicológicos científicamente demostrados.",
   "No se interpreta como prueba de alma gemela, origen monádico o llama gemela.",
   "Las casas, regentes, decanatos y retrogradaciones solo se muestran si figuran en el canónico.",
   "La autoría editorial con fuentes y el documento oficial M31 requieren validación independiente."
  ],subjects
 };
}

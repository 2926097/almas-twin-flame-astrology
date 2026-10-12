// ALMAS Web 1.3 — request-only two-birth adapter. No network I/O.
export const POLICY_PRESET="ALMAS_RELATIONAL_STRICT_RESEARCH_V1";
export const PUBLIC_VERSION="1.26.0";
export const PROFILES=Object.freeze(["FULL_ASTROLOGY","FULL_MULTIDISCIPLINARY","TEMPORAL","SOUL_CONTRACT"]);
const fail=m=>{throw new TypeError(m)};
function dateValid(raw){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(raw))return false;
 const [y,m,d]=raw.split("-").map(Number),dt=new Date(Date.UTC(y,m-1,d));
 return y>=1600&&y<=2200&&dt.getUTCFullYear()===y&&dt.getUTCMonth()===m-1&&dt.getUTCDate()===d;
}
function subject(input,id){
 if(!input||typeof input!=="object"||Array.isArray(input))fail(id+": faltan datos de nacimiento.");
 const date=String(input.birth_date||"").trim();
 if(!dateValid(date))fail(id+": fecha de nacimiento inválida.");
 const time=String(input.birth_time||"").trim();
 if(time&&!/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(time))fail(id+": hora local inválida.");
 const reliability=String(input.time_reliability||"");
 if(!["A","B","C","D"].includes(reliability))fail(id+": calidad horaria A/B/C/D obligatoria.");
 if(["A","B"].includes(reliability)&&!time)fail(id+": calidad A/B exige hora registrada.");
 const tz=String(input.timezone||"").trim();
 if(time&&!/^[A-Za-z][A-Za-z0-9_+\/-]{2,100}$/.test(tz))fail(id+": indica zona horaria IANA.");
 const lat=Number(input.latitude),lon=Number(input.longitude);
 if(input.latitude===""||input.longitude===""||!Number.isFinite(lat)||!Number.isFinite(lon)||lat< -90||lat>90||lon< -180||lon>180)
   fail(id+": latitud (-90 a 90) y longitud (-180 a 180) son obligatorias.");
 const out={id,birth_date:date,time_reliability:reliability,latitude:lat,longitude:lon};
 if(time){out.birth_time=time;out.timezone=tz;}
 const name=String(input.display_name||"").trim();
 if(name){if(name.length>100)fail(id+": nombre demasiado largo.");out.display_name=name;}
 return out;
}
export function buildTwoBirthRequest(a,b,{profile="FULL_MULTIDISCIPLINARY",policyPreset=POLICY_PRESET}={}){
 if(!PROFILES.includes(profile))fail("Perfil de análisis no reconocido.");
 if(policyPreset!==POLICY_PRESET)fail("Preset de política no reconocido.");
 return {format:"ALMAS_WORK_REQUEST",type:"RELATIONAL",execution_state:"REQUEST_ONLY",
 public_version:PUBLIC_VERSION,analysis_profile:profile,analysis_policy_profile:policyPreset,
 subjects:[subject(a,"A"),subject(b,"B")],events:[]};
}
export function describeTwoBirthReadiness(request){
 return {state:"REQUEST_ONLY",automatic_calculation:false,
 timed_subjects:request.subjects.filter(s=>Boolean(s.birth_time)).length,
 profile:request.analysis_profile,
 missing:["backend Moira/JPL con efemérides verificadas","entorno privado autorizado",
 "manifest de orquestación","ejecución M00–M31 y verificación M30/M31"]};
}

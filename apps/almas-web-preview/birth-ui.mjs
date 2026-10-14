import {buildTwoBirthRequest,describeTwoBirthReadiness,PROFILES} from "./birth-request.mjs";
import {buildCitySearchUrl,normalizeCityResults,createCitySelection} from "./birth-geocoding.mjs";
const $=id=>document.getElementById(id);
const cityPickers=new Map();
function readSubject(prefix){
 const field=name=>$(prefix+name).value;
 const city=cityPickers.get(prefix)?.current();
 if(!city)throw new TypeError((prefix==="birthA"?"Persona A":"Persona B")+
  ": busca y selecciona una ciudad de nacimiento de la lista.");
 // The values still feed the existing coordinate-based adapter, invisibly to the user.
 return {display_name:field("Name"),birth_date:field("Date"),birth_time:field("Time"),
 time_reliability:field("Quality"),timezone:city.timezone,
 latitude:city.latitude,longitude:city.longitude};
}
function collectRequest(){
 return buildTwoBirthRequest(readSubject("birthA"),readSubject("birthB"),{profile:$("birthProfile").value});
}
function downloadJson(name,obj){
 const url=URL.createObjectURL(new Blob([JSON.stringify(obj,null,2)+"\n"],{type:"application/json"}));
 const a=document.createElement("a");a.href=url;a.download=name;
 document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
const form=$("birthIntakeForm"),download=$("birthDownload"),status=$("birthIntakeStatus");
let localCSRF=null,inputEpoch=0;
if(form){
 for(const profile of PROFILES){
  const option=document.createElement("option");option.value=profile;option.textContent=profile;
  $("birthProfile").appendChild(option);
 }
 $("birthProfile").value="FULL_MULTIDISCIPLINARY";
 const reset=()=>{
  inputEpoch++;
  download.disabled=true;download.onclick=null;status.textContent="Sin solicitud validada.";
  $("birthBundleDownload").disabled=true;$("birthBundleDownload").onclick=null;
  $("birthLocalResult").textContent="";
 };
 form.addEventListener("input",reset);form.addEventListener("change",reset);
 // Never geocode on typing or page load. Only a click (or Enter) sends the city string.
 function installCityPicker(prefix){
  const input=$(prefix+"City"),search=$(prefix+"CitySearch"),
    results=$(prefix+"CityResults"),message=$(prefix+"CityStatus");
  const selection=createCitySelection();
  let serial=0,controller=null;
  function erase(){
   serial++;controller?.abort();controller=null;selection.clear();
   $(prefix+"Zone").value="";$(prefix+"Lat").value="";$(prefix+"Lon").value="";
   results.replaceChildren();
   message.textContent="Busca y selecciona una localidad de la lista.";
   reset();
  }
  input.addEventListener("input",erase);
  input.addEventListener("keydown",event=>{
   if(event.key==="Enter"){event.preventDefault();search.click();}
  });
  search.addEventListener("click",async()=>{
   serial++;const token=serial;
   controller?.abort();controller=null;selection.clear();
   $(prefix+"Zone").value="";$(prefix+"Lat").value="";$(prefix+"Lon").value="";
   results.replaceChildren();reset();
   let url;
   try{url=buildCitySearchUrl(input.value);}
   catch{message.textContent="Introduce al menos dos letras de la ciudad.";return;}
   search.disabled=true;
   message.textContent="Buscando localidades; solo se envía el nombre de la ciudad…";
   const abort=new AbortController();controller=abort;
   try{
    const response=await fetch(url,{method:"GET",mode:"cors",credentials:"omit",
      cache:"no-store",referrerPolicy:"no-referrer",signal:abort.signal,
      headers:{"Accept":"application/json"}});
    if(!response.ok)throw Error("SEARCH_FAILED");
    const data=await response.json();
    if(token!==serial)return;
    const options=normalizeCityResults(data);
    if(!options.length){
     message.textContent="No hay coincidencias. Prueba con ciudad, provincia o país.";
     return;
    }
    message.textContent="Selecciona la localidad correcta entre "+options.length+" coincidencias.";
    for(const option of options){
     const item=document.createElement("button");item.type="button";
     item.textContent=option.label;item.setAttribute("aria-label","Elegir "+option.label);
     item.addEventListener("click",()=>{
      if(token!==serial)return;
      selection.choose(option);input.value=option.label;
      $(prefix+"Zone").value=option.timezone;
      $(prefix+"Lat").value=String(option.latitude);
      $(prefix+"Lon").value=String(option.longitude);
      results.replaceChildren();
      message.textContent="Localidad seleccionada: "+option.label+
       " · zona IANA: "+option.timezone+". Comprueba su correspondencia histórica.";
      serial++;reset();
     });
     results.appendChild(item);
    }
   }catch(err){
    if(token!==serial||err?.name==="AbortError")return;
    message.textContent="Búsqueda no disponible. Vuelve a intentar; no se ha seleccionado una ciudad.";
   }finally{
    if(token===serial){search.disabled=false;controller=null;}
    else search.disabled=false;
   }
  });
  return {current:()=>selection.current(input.value)};
 }
 for(const prefix of ["birthA","birthB"])cityPickers.set(prefix,installCityPicker(prefix));

 form.addEventListener("submit",event=>{
  event.preventDefault();reset();
  try{
   const request=collectRequest(),state=describeTwoBirthReadiness(request);
   status.textContent="Solicitud local válida ("+state.state+"). "+state.timed_subjects+"/2 horas registradas. Todavía no se han calculado posiciones ni índices.";
   download.disabled=false;
   download.onclick=()=>downloadJson("almas-two-birth-request.json",request);
  }catch(e){status.textContent="BLOQUEADO: "+(e.message||"Solicitud inválida.");}
 });
 const calculate=$("birthRunLocal");
 if(globalThis.location?.hostname==="127.0.0.1"&&globalThis.location?.protocol==="http:"){
  fetch("/local/capabilities",{method:"GET",cache:"no-store",credentials:"same-origin"})
   .then(async response=>{
     if(!response.ok)throw Error("LOCAL_NOT_AVAILABLE");
     const data=await response.json();
     if(data.kind!=="ALMAS_LOCAL_ENGINE_V1"||data.loopback_only!==true||
        typeof data.csrf_token!=="string"||data.csrf_token.length<32||
        data.backend_configured!==true)throw Error("LOCAL_CAPABILITY_INVALID");
     localCSRF=data.csrf_token;calculate.hidden=false;calculate.disabled=false;
   }).catch(()=>{localCSRF=null;calculate.hidden=true;calculate.disabled=true});
 }
 calculate.addEventListener("click",async()=>{
  // Never send natal data from a public preview or remote hostname.
  if(globalThis.location?.hostname!=="127.0.0.1"||
     globalThis.location?.protocol!=="http:"||!localCSRF)return;
  calculate.disabled=true;
  $("birthLocalResult").textContent="";
  const epoch=inputEpoch;
  try{
   const request=collectRequest();
   status.textContent="Ejecutando M00–M31 en el equipo local. Ningún dato se envía a Vercel.";
   const res=await fetch("/local/analyze",{
     method:"POST",cache:"no-store",credentials:"same-origin",
     headers:{"Content-Type":"application/json","X-ALMAS-CSRF":localCSRF},
     body:JSON.stringify(request)
   });
   const data=await res.json();
   if(epoch!==inputEpoch)return; // never render obsolete pairs after edits
   if(!res.ok)throw Error(data.error||"LOCAL_ENGINE_UNAVAILABLE");
   const modules=Object.entries(data.module_statuses||{});
   const ready=modules.filter(([,v])=>v==="COMPLETED").length;
   const notReady=modules.filter(([,v])=>v!=="COMPLETED");
   $("birthLocalResult").textContent="Estado: "+data.state+" · módulos completados: "+ready+"/"+modules.length+
     " · no completados: "+notReady.map(([k,v])=>k+"="+v).join(", ")+
     (data.m31?" · secciones M31: "+data.m31.sections?.length:"")+
     ". Interpretación autoral todavía NO_GENERADA; los índices proceden únicamente del motor.";
   if(data.canonical_analysis){
    const {ingestCanonicalLocal,ingestOfficialLocalReport}=await import("./app.mjs");
    if(epoch!==inputEpoch)return;
    const accepted=await ingestCanonicalLocal(JSON.stringify(data.canonical_analysis));
    if(!accepted)throw Error("CANONICAL_REJECTED_BY_BROWSER_VALIDATOR");
    const reportAccepted=await ingestOfficialLocalReport(data.m30,data.m31);
    if(epoch!==inputEpoch)return; // edited inputs cannot reactivate an obsolete export
    $("birthLocalResult").textContent+=" · M30/M31 navegador: "+(reportAccepted?"PASS, HTML disponible":"BLOQUEADO, consulta detalle del informe");
    if(!reportAccepted)throw Error("M30_M31_BROWSER_GATE_REJECTED");
    $("birthBundleDownload").disabled=false;
    $("birthBundleDownload").onclick=()=>downloadJson("almas-local-results.json",{
      canonical_analysis:data.canonical_analysis,m30:data.m30,m31:data.m31,
      atlas:data.atlas,assessment:data.assessment,module_statuses:data.module_statuses,
      limitations:data.limitations
    });
   }
   status.textContent=data.canonical_analysis?
    "Cálculo local terminado y canónico validado en el navegador. M30/M31 conservan estado "+data.state+".":
    "Pipeline local "+data.state+": no se fabricó un análisis canónico.";
  }catch(e){
    if(epoch!==inputEpoch)return;
    status.textContent="Cálculo local BLOQUEADO: "+(e.message||"Error no especificado");
  }finally{calculate.disabled=false}
 });
}

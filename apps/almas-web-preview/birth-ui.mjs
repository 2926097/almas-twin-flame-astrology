import {buildTwoBirthRequest,describeTwoBirthReadiness,PROFILES} from "./birth-request.mjs";
const $=id=>document.getElementById(id);
function readSubject(prefix){
 const field=name=>$(prefix+name).value;
 return {display_name:field("Name"),birth_date:field("Date"),birth_time:field("Time"),
 time_reliability:field("Quality"),timezone:field("Zone"),latitude:field("Lat"),longitude:field("Lon")};
}
const form=$("birthIntakeForm"),download=$("birthDownload"),status=$("birthIntakeStatus");
if(form){
 for(const profile of PROFILES){const option=document.createElement("option");option.value=profile;option.textContent=profile;$("birthProfile").appendChild(option)}
 $("birthProfile").value="FULL_MULTIDISCIPLINARY";
 const reset=()=>{download.disabled=true;download.onclick=null;status.textContent="Sin solicitud validada."};
 form.addEventListener("input",reset);form.addEventListener("change",reset);
 form.addEventListener("submit",event=>{
  event.preventDefault();reset();
  try{
   const request=buildTwoBirthRequest(readSubject("birthA"),readSubject("birthB"),{profile:$("birthProfile").value});
   const state=describeTwoBirthReadiness(request);
   status.textContent="Solicitud local válida ("+state.state+"). "+state.timed_subjects+"/2 horas registradas. No se han calculado cartas, índices ni interpretaciones; no se envían datos al servidor.";
   download.disabled=false;
   download.onclick=()=>{
     const url=URL.createObjectURL(new Blob([JSON.stringify(request,null,2)+"\n"],{type:"application/json"}));
     const a=document.createElement("a");a.href=url;a.download="almas-two-birth-request.json";
     document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
   };
  }catch(e){status.textContent="BLOQUEADO: "+(e.message||"Solicitud inválida.");}
 });
}

import test from "node:test";
import assert from "node:assert/strict";

class FakeElement{
 constructor(id=""){this.id=id;this.value="";this.textContent="";this.disabled=false;
  this.hidden=false;this.listeners={};this.children=[];this.onclick=null;}
 addEventListener(type,callback){this.listeners[type]=callback;}
 appendChild(child){this.children.push(child);return child;}
 replaceChildren(...items){this.children=items;}
 setAttribute(name,value){this[name]=value;}
 click(){return this.listeners.click?.();}
}
const elements=new Map(),el=id=>{
 if(!elements.has(id))elements.set(id,new FakeElement(id));
 return elements.get(id);
};
globalThis.document={getElementById:el,createElement:type=>new FakeElement(type)};
globalThis.location={hostname:"example.test",protocol:"https:"};
const calls=[];
globalThis.fetch=async(url,opts)=>{
 calls.push({url:String(url),opts});
 const city=new URL(String(url)).searchParams.get("name");
 const location=city==="Madrid"?
   {id:101,name:"Madrid",country:"España",admin1:"Madrid",latitude:40.4168,
    longitude:-3.7038,timezone:"Europe/Madrid"}:
   {id:202,name:"Chicago",country:"Estados Unidos",admin1:"Illinois",
    latitude:41.8781,longitude:-87.6298,timezone:"America/Chicago"};
 return {ok:true,json:async()=>({results:[location]})};
};
await import("../birth-ui.mjs");

async function searchAndSelect(prefix,name){
 const input=el(prefix+"City");
 input.value=name;
 input.listeners.input();
 await el(prefix+"CitySearch").listeners.click();
 assert.equal(el(prefix+"CityResults").children.length,1);
 el(prefix+"CityResults").children[0].click();
 return input.value;
}

test("city controls neither geocode nor transmit natal data at startup",()=>{
 assert.equal(calls.length,0);
 assert.equal(el("birthRunLocal").hidden,false); // fake fixture default only; no local capability requested
});
test("user selects two unambiguous cities, hidden coordinates/timezone power existing request",async()=>{
 el("birthAName").value="Sujeto sintético A";
 el("birthADate").value="1988-06-17";el("birthATime").value="13:20";
 el("birthAQuality").value="A";
 el("birthBName").value="Sujeto sintético B";
 el("birthBDate").value="1990-11-06";el("birthBTime").value="09:10";
 el("birthBQuality").value="B";
 const first=await searchAndSelect("birthA","Madrid");
 const second=await searchAndSelect("birthB","Chicago");
 assert.match(first,/Madrid/);assert.match(second,/Chicago/);
 assert.equal(el("birthALat").value,"40.4168");
 assert.equal(el("birthALon").value,"-3.7038");
 assert.equal(el("birthAZone").value,"Europe/Madrid");
 assert.equal(el("birthBZone").value,"America/Chicago");
 assert.equal(calls.length,2);
 for(const call of calls){
  assert.equal(call.opts.method,"GET");assert.equal(call.opts.credentials,"omit");
  assert.equal(call.opts.referrerPolicy,"no-referrer");
  assert.equal(call.url.includes("1988"),false);
  assert.equal(call.url.includes("Sujeto"),false);
 }
 let prevented=false;
 el("birthIntakeForm").listeners.submit({preventDefault(){prevented=true;}});
 assert.equal(prevented,true);
 assert.equal(el("birthDownload").disabled,false);
 assert.match(el("birthIntakeStatus").textContent,/Solicitud local válida/);
});
test("editing a selected city invalidates both geocoding and prior request",()=>{
 const input=el("birthACity");input.value="Otro lugar";
 input.listeners.input();
 assert.equal(el("birthALat").value,"");
 assert.equal(el("birthAZone").value,"");
 assert.equal(el("birthDownload").disabled,true);
 el("birthIntakeForm").listeners.submit({preventDefault(){}});
 assert.match(el("birthIntakeStatus").textContent,/busca y selecciona una ciudad/);
 assert.equal(el("birthDownload").disabled,true);
});

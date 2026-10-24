import test from "node:test";
import assert from "node:assert/strict";
import {buildCitySearchUrl,normalizeCityResults,createCitySelection} from "../birth-geocoding.mjs";

const madrid={id:3117735,name:"Madrid",admin1:"Comunidad de Madrid",country:"España",
 latitude:40.4168,longitude:-3.7038,timezone:"Europe/Madrid"};
test("explicit city search URL carries only the city query, not any natal fields",()=>{
 const value=buildCitySearchUrl("  Madrid, España  ");
 const url=new URL(value);
 assert.equal(url.origin,"https://geocoding-api.open-meteo.com");
 assert.equal(url.pathname,"/v1/search");
 assert.equal(url.searchParams.get("name"),"Madrid, España");
 assert.equal(url.searchParams.get("count"),"10");
 assert.equal(url.searchParams.get("language"),"es");
 assert.deepEqual([...url.searchParams.keys()].sort(),["count","format","language","name"]);
 for(const fragment of ["birth_date","birth_time","display_name","subjects","latitude","longitude"])
   assert.equal(value.includes(fragment),false);
});
test("short or malformed location queries fail closed",()=>{
 for(const s of [""," ","M","a".repeat(101),"Madrid\nAuthorization:secret"])
   assert.throws(()=>buildCitySearchUrl(s),/CITY_QUERY_INVALID/);
});
test("normalize global matches, deduplicate and reject missing IANA timezone or coordinates",()=>{
 const rows=normalizeCityResults({results:[
  madrid,{...madrid,id:3117736,name:"Madrid",country:"Colombia",admin1:"Cundinamarca",latitude:4.7324,longitude:-74.2627,timezone:"America/Bogota"},
  madrid,{...madrid,id:77,timezone:null},
  {...madrid,id:78,latitude:Infinity},{...madrid,id:79,longitude:999},
  {...madrid,id:80,name:""}
 ]});
 assert.equal(rows.length,2);
 assert.equal(rows[0].latitude,40.4168);
 assert.equal(rows[0].timezone,"Europe/Madrid");
 assert.match(rows[0].label,/Madrid/);
 assert.match(rows[1].label,/Colombia/);
 assert.throws(()=>normalizeCityResults({error:true}),/CITY_PROVIDER_INVALID/);
 assert.deepEqual(normalizeCityResults({}),[]);
});
test("selection cannot survive changed freeform city text",()=>{
 const state=createCitySelection(),city=normalizeCityResults({results:[madrid]})[0];
 assert.equal(state.current(city.label),null);
 state.choose(city);
 assert.equal(state.current(city.label).timezone,"Europe/Madrid");
 assert.equal(state.current(city.label+" otra"),null);
 state.clear();
 assert.equal(state.current(city.label),null);
});

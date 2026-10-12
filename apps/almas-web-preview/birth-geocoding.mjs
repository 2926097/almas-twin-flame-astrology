// ALMAS Web — public-geocoding adapter. Only a user-clicked city query leaves the browser.
// GeoNames-backed Open-Meteo results are not a source of natal time accuracy.
const ENDPOINT="https://geocoding-api.open-meteo.com/v1/search";
export function buildCitySearchUrl(raw){
  if(typeof raw!=="string"||/[\x00-\x1f\x7f]/.test(raw))
    throw new TypeError("CITY_QUERY_INVALID");
  const query=raw.trim().replace(/\s+/g," ");
  if(query.length<2||query.length>100)
    throw new TypeError("CITY_QUERY_INVALID");
  const params=new URLSearchParams({name:query,count:"10",language:"es",format:"json"});
  return ENDPOINT+"?"+params.toString();
}
export function normalizeCityResults(payload){
  if(!payload||typeof payload!=="object"||Array.isArray(payload)||payload.error===true)
    throw new TypeError("CITY_PROVIDER_INVALID");
  if(payload.results!==undefined&&!Array.isArray(payload.results))
    throw new TypeError("CITY_RESULTS_INVALID");
  const seen=new Set(),results=[];
  for(const row of (payload.results||[]).slice(0,20)){
    if(!row||typeof row!=="object"||typeof row.name!=="string"||
       !Number.isSafeInteger(row.id)||typeof row.country!=="string"||
       typeof row.latitude!=="number"||!Number.isFinite(row.latitude)||
       typeof row.longitude!=="number"||!Number.isFinite(row.longitude)||
       row.latitude< -90||row.latitude>90||row.longitude< -180||row.longitude>180||
       typeof row.timezone!=="string"||
       !/^[A-Za-z][A-Za-z0-9_+\/-]{2,100}$/.test(row.timezone)||
       seen.has(row.id))continue;
    const name=row.name.trim(),country=row.country.trim();
    if(!name||!country)continue;
    seen.add(row.id);
    const segments=[name,row.admin2,row.admin1,country].filter(x=>typeof x==="string"&&x.trim());
    const label=segments.map(x=>x.trim()).filter((x,i,a)=>a.indexOf(x)===i).join(", ");
    results.push(Object.freeze({id:row.id,label,latitude:row.latitude,
      longitude:row.longitude,timezone:row.timezone}));
    if(results.length===10)break;
  }
  return results;
}
// Fail closed: a typed but unselected city does not authorize coordinates.
export function createCitySelection(){
  let chosen=null;
  return {
    choose(option){if(!option||!Number.isSafeInteger(option.id)||
      !Number.isFinite(option.latitude)||!Number.isFinite(option.longitude)||
      typeof option.label!=="string"||typeof option.timezone!=="string")
        throw new TypeError("CITY_SELECTION_INVALID");
      chosen=option;return option;
    },
    clear(){chosen=null;},
    current(text){return chosen&&text===chosen.label?chosen:null;}
  };
}

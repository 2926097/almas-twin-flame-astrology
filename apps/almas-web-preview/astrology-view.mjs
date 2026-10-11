/** Canonical-data-only astrological positions. This module performs no ephemeris,
 * zodiac conversion, synthesis, horoscope or predictive calculation. */
const zodiac=["Aries","Tauro","Géminis","Cáncer","Leo","Virgo","Libra","Escorpio","Sagitario","Capricornio","Acuario","Piscis"];
const types=[
  ["natal_context","Natal y superposiciones"],
  ["relationship_field","Sinastría y campo relacional"],
  ["draconic_context","Dracónica"],
  ["vedic","Védica"],
  ["lots_context","Partes arábigas"],
  ["temporal","Activaciones temporales"]
];
const record=x=>x!==null&&typeof x==="object"&&!Array.isArray(x)?x:{};
const text=x=>typeof x==="string"?x:null;
const numeric=x=>typeof x==="number"&&Number.isFinite(x)?x:null;
const printable=x=>x===null||x===undefined?"No disponible":String(x);
export function chartAvailability(canonical){
  return types.map(([key,label])=>{
    const value=canonical?.[key];
    const present=key==="draconic_context" ? Object.keys(record(value?.individual?.charts)).length>0 :
      value!==undefined&&value!==null&&
      (typeof value!=="object"||Object.keys(value).length>0);
    return {key,label,state:present?"DECLARED":"NOT_AVAILABLE"};
  }).concat([
    {key:"composite",label:"Carta compuesta",
      state:Object.keys(record(canonical?.relationship_field?.composite?.positions)).length?"DECLARED":"NOT_AVAILABLE"},
    {key:"davison",label:"Davison",
      state:Object.keys(record(canonical?.relationship_field?.davison?.positions)).length?"DECLARED":"NOT_AVAILABLE"}
  ]);
}
export function selectNatalChart(canonical,subjectId){
  const subjects=record(canonical?.natal_context?.subjects);
  const ids=Object.keys(subjects).sort();
  const selected=ids.includes(subjectId)?subjectId:ids[0]||null;
  if(!selected)return {available:false,subject:null,points:[],houses:[],reason:"Sin datos natales declarados en canonical"};
  const person=record(subjects[selected]);
  const signs=record(person.point_signs),placements=record(person.house_placements);
  const rulers=record(person.rulerships);
  const points=Object.entries(signs).sort((a,b)=>a[0].localeCompare(b[0])).map(([name,entry])=>{
    const value=record(entry);
    const placement=record(placements[name]);
    const longitude=numeric(value.longitude)??numeric(value.longitude_deg)??numeric(placement.longitude);
    const longitudeValid=longitude!==null&&longitude>=0&&longitude<360?longitude:null;
    return {
      name,sign:text(entry)??text(value.sign)??text(value.zodiac_sign),
      house:Number.isInteger(placement.house)&&placement.house>=1&&placement.house<=12?placement.house:null,
      longitude:longitudeValid,
      decan:text(value.decan)??text(value.decanate),
      ruler:text(rulers[name])??text(record(rulers[name]).ruler),
      retrograde:typeof value.retrograde==="boolean"?value.retrograde:null,
      origin:"natal_context.subjects["+selected+"].point_signs."+name
    };
  });
  const cusp=record(person.house_cusps);
  const houses=Object.entries(cusp).map(([house,v])=>{
    const index=Number(house),longitude=numeric(v)??numeric(record(v).longitude);
    return {house:index,longitude:longitude!==null&&longitude>=0&&longitude<360?longitude:null};
  }).filter(x=>Number.isInteger(x.house)&&x.house>=1&&x.house<=12).sort((a,b)=>a.house-b.house);
  return {available:true,subject:selected,timed:person.timed===true,points,houses,reason:null};
}
export function drawNatalWheel(svg,chart){
  const ns="http://www.w3.org/2000/svg";
  svg.replaceChildren();svg.setAttribute("viewBox","0 0 480 480");
  svg.setAttribute("role","img");
  svg.setAttribute("aria-label","Rueda zodiacal descriptiva de posiciones existentes en canonical");
  const make=(tag,attrs={})=>{
    const e=document.createElementNS(ns,tag);
    for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));
    return e;
  };
  const circle=(r)=>svg.appendChild(make("circle",{cx:240,cy:240,r,fill:"none",stroke:"#879fbe","stroke-width":1}));
  for(const r of [92,146,195])circle(r);
  const polar=(long,r)=>{
    const angle=(long-90)*Math.PI/180;
    return {x:240+r*Math.cos(angle),y:240+r*Math.sin(angle)};
  };
  for(let i=0;i<12;i++){
    const start=polar(i*30,92),end=polar(i*30,195);
    svg.appendChild(make("line",{x1:start.x,y1:start.y,x2:end.x,y2:end.y,stroke:"#526784"}));
    const label=polar(i*30+15,173),t=make("text",{x:label.x,y:label.y,fill:"#e1e9f5","text-anchor":"middle","font-size":12});
    t.textContent=zodiac[i].slice(0,3);svg.appendChild(t);
  }
  for(const cusp of chart.houses){
    if(cusp.longitude===null)continue;
    const a=polar(cusp.longitude,92),b=polar(cusp.longitude,146);
    svg.appendChild(make("line",{x1:a.x,y1:a.y,x2:b.x,y2:b.y,stroke:"#d9a66a","stroke-width":2}));
  }
  const positions=chart.points.filter(p=>p.longitude!==null);
  positions.forEach((point,index)=>{
    const r=106+(index%3)*12,pos=polar(point.longitude,r);
    const mark=make("circle",{cx:pos.x,cy:pos.y,r:4.5,fill:"#9ee2ca"});
    const tt=make("title");
    tt.textContent=point.name+" "+point.longitude+"° (dato canónico)";
    mark.append(tt);svg.append(mark);
  });
  return {renderedPoints:positions.length,missingCoordinates:chart.points.length-positions.length};
}
export function describePlacement(point){
  return {
    name:point.name,
    sign:printable(point.sign),
    house:printable(point.house),
    decan:printable(point.decan),
    ruler:printable(point.ruler),
    retrograde:point.retrograde===null?"No disponible":point.retrograde?"Sí":"No",
    longitude:point.longitude===null?"No disponible":point.longitude+"°"
  };
}

/** Exact positions from canonical relationship_field — never calculate a new chart. */
export function selectRelationshipChart(canonical,mode){
  if(!["composite","davison"].includes(mode))return {available:false,reason:"Modalidad no admitida",points:[],houses:[]};
  const source=record(canonical?.relationship_field?.[mode]);
  const positions=record(source.positions);
  const points=Object.entries(positions).sort((a,b)=>a[0].localeCompare(b[0])).map(([name,p])=>{
    const value=record(p),longitude=numeric(value.longitude);
    return {
      name,sign:text(value.sign),longitude:longitude!==null&&longitude>=0&&longitude<360?longitude:null,
      house:mode==="davison"?Number.isInteger(source.house_placements?.[name])?source.house_placements[name]:null:null,
      decan:null,ruler:null,retrograde:null,origin:"relationship_field."+mode+".positions."+name
    };
  });
  const houses=mode==="davison"?Object.entries(record(source.house_cusps)).map(([house,val])=>{
    const value=record(val),longitude=numeric(value.longitude),number=Number(house);
    return {house:number,longitude:longitude!==null&&longitude>=0&&longitude<360?longitude:null};
  }).filter(x=>Number.isInteger(x.house)&&x.house>=1&&x.house<=12):[];
  return {available:points.length>0,subject:mode,timed:mode==="davison"&&houses.length>0,points,houses,
    reason:points.length?null:"Sin posiciones de "+mode+" en el canonical"};
}
export function selectVedicChart(canonical,division="d1",index=0){
  if(!["d1","d9"].includes(division))return {available:false,points:[],houses:[],reason:"División no admitida"};
  const source=Array.isArray(canonical?.vedic?.charts)?canonical.vedic.charts[index]:null;
  const positions=record(source?.[division]);
  const points=Object.entries(positions).sort((a,b)=>a[0].localeCompare(b[0])).map(([name,item])=>{
    const v=record(item),longitude=numeric(v.longitude),sign=Number.isInteger(v.sign)&&v.sign>=0&&v.sign<=11?zodiac[v.sign]:null;
    return {name,sign,house:null,longitude:longitude!==null&&longitude>=0&&longitude<360?longitude:null,
      decan:null,ruler:null,retrograde:null,origin:"vedic.charts["+index+"]."+division+"."+name};
  });
  return {available:points.length>0,subject:"védica "+division.toUpperCase()+" ["+index+"]",timed:false,points,houses:[],
    reason:points.length?null:"Sin posiciones védicas "+division.toUpperCase()+" en canonical"};
}
/** M10 draconic points precomputed in canonical, without recomputing nodal offsets. */
export function selectDraconicChart(canonical,subjectId){
  const charts=record(canonical?.draconic_context?.individual?.charts);
  const ids=Object.keys(charts).sort();
  const selected=ids.includes(subjectId)?subjectId:ids[0]||null;
  if(!selected)return {available:false,subject:null,points:[],houses:[],
    reason:"No hay carta dracónica calculada en canonical"};
  const chart=record(charts[selected]);
  const positions=record(chart.positions),cusps=record(chart.houses);
  const points=Object.entries(positions).sort((a,b)=>a[0].localeCompare(b[0])).map(([name,item])=>{
    const v=record(item),longitude=numeric(v.longitude);
    return {name,sign:text(v.sign),house:null,decan:null,ruler:null,retrograde:null,
      longitude:longitude!==null&&longitude>=0&&longitude<360?longitude:null,
      origin:"draconic_context.individual.charts["+selected+"].positions."+name};
  });
  const houses=Object.entries(cusps).map(([house,value])=>({
    house:Number(house),longitude:numeric(value)})).filter(x=>
      Number.isInteger(x.house)&&x.house>=1&&x.house<=12&&
      x.longitude!==null&&x.longitude>=0&&x.longitude<360);
  return {available:points.length>0,subject:selected,timed:houses.length===12,
    points,houses,reason:points.length?null:"Carta dracónica sin puntos"};
}
export function selectChartMode(canonical,mode,subjectId){
  if(mode==="composite"||mode==="davison")return selectRelationshipChart(canonical,mode);
  if(mode==="draconic")return selectDraconicChart(canonical,subjectId);
  if(mode==="vedic-d1")return selectVedicChart(canonical,"d1");
  if(mode==="vedic-d9")return selectVedicChart(canonical,"d9");
  return selectNatalChart(canonical,subjectId);
}

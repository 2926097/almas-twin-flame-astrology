/** A read-only, capped graph of ROOTs, dependency families and counterevidence.
 * Every edge is grounded in explicit canonical IDs. No inference of statistical
 * independence, probabilities, relationship status or metaphysical exclusivity.
 */
const array = value => Array.isArray(value) ? value : [];
const val = value => typeof value === "string" ? value : "";
const safeId = (type, raw) => type + ":" + encodeURIComponent(raw);
export function buildEvidenceGraph(canonical, {maxNodes=90,maxEdges=180} = {}) {
  const nodeLimit=Math.max(1,Math.min(120,Number.isFinite(maxNodes)?Math.floor(maxNodes):90));
  const edgeLimit=Math.max(1,Math.min(300,Number.isFinite(maxEdges)?Math.floor(maxEdges):180));
  const nodes=new Map(),edges=[],seen=new Set();
  const addNode=(id,type,label)=>{
    if(!id||nodes.has(id))return nodes.has(id);
    if(nodes.size>=nodeLimit)return false;
    nodes.set(id,{id,type,label});return true;
  };
  const addEdge=(source,target,type)=>{
    if(!nodes.has(source)||!nodes.has(target)||edges.length>=edgeLimit)return;
    const id=JSON.stringify([source,target,type]);
    if(seen.has(id))return; seen.add(id);
    edges.push({source,target,type});
  };
  const roots=array(canonical?.evidence).filter(x=>x&&typeof x==="object").slice().sort((a,b)=>val(a.evidence_id).localeCompare(val(b.evidence_id)));
  const counters=array(canonical?.counterevidence).filter(x=>x&&typeof x==="object").slice().sort((a,b)=>val(a.id).localeCompare(val(b.id)));
  for(const root of roots){
    const id=val(root.evidence_id);if(!id)continue;
    const rootNode=safeId("ROOT",id);if(!addNode(rootNode,"ROOT",id))continue;
    for(const f of array(root.dependency_families)){
      if(!val(f))continue;
      const family=safeId("FAMILY",f);
      if(addNode(family,"FAMILY",f))addEdge(rootNode,family,"HAS_DEPENDENCY");
    }
  }
  for(const c of counters){
    const cid=val(c.id);if(!cid)continue;
    const cnode=safeId("COUNTER",cid);if(!addNode(cnode,"COUNTER",cid))continue;
    const model=val(c.model);
    if(["AF","KA","AG","LG"].includes(model)){
      const mid=safeId("MODEL",model);
      if(addNode(mid,"MODEL",model))addEdge(cnode,mid,"CONTRADICTS_MODEL");
    }
    const fam=val(c.dependency_family);
    if(fam){
      const fid=safeId("FAMILY",fam);
      if(addNode(fid,"FAMILY",fam))addEdge(cnode,fid,"DEPENDENCY_FAMILY");
    }
    for(const ref of array(c.evidence_refs)){
      if(typeof ref!=="string")continue;
      const rid=safeId("ROOT",ref);
      if(nodes.has(rid))addEdge(cnode,rid,"REFERENCES_ROOT");
    }
  }
  return {
    nodes:[...nodes.values()],edges,
    sourceRootCount:roots.length,sourceCounterCount:counters.length,
    truncated: nodes.size>=nodeLimit||edges.length>=edgeLimit,
    meaning:"Declarative links only; not independent observations"
  };
}

/** SVG and click selection. All labels inserted through textContent, no HTML. */
export function renderEvidenceGraph(svg,graph,detail){
  const ns="http://www.w3.org/2000/svg";
  svg.replaceChildren();
  svg.setAttribute("viewBox","0 0 850 470");
  svg.setAttribute("role","img");
  svg.setAttribute("aria-label","Grafo local de raíces, familias, contraevidencias y modelos");
  const columns={ROOT:110,FAMILY:330,COUNTER:555,MODEL:755};
  const types=["ROOT","FAMILY","COUNTER","MODEL"];
  const positions=new Map();
  for(const type of types){
    const subset=graph.nodes.filter(n=>n.type===type);
    subset.forEach((n,i)=>positions.set(n.id,{x:columns[type],y:30+410*(i+1)/(subset.length+1)}));
  }
  const make=(tag,attributes={})=>{
    const node=document.createElementNS(ns,tag);
    for(const [key,value] of Object.entries(attributes))node.setAttribute(key,String(value));
    return node;
  };
  for(const edge of graph.edges){
    const a=positions.get(edge.source),b=positions.get(edge.target);
    if(!a||!b)continue;
    svg.appendChild(make("line",{x1:a.x,y1:a.y,x2:b.x,y2:b.y,stroke:"#68809f","stroke-width":1.3,opacity:.5}));
  }
  for(const node of graph.nodes){
    const p=positions.get(node.id),group=make("g",{role:"button",tabindex:0,"aria-label":node.type+" "+node.label});
    const circle=make("circle",{cx:p.x,cy:p.y,r:node.type==="FAMILY"?8:10,fill:node.type==="COUNTER"?"#d5a55e":node.type==="MODEL"?"#83bbad":"#96b5df"});
    const title=make("title");title.textContent=node.label;
    const label=make("text",{x:p.x+15,y:p.y+4,fill:"#e5ecf7","font-size":10});
    label.textContent=node.label.slice(0,31);
    const select=()=>{detail.textContent=node.type+": "+node.label+". Solo relación documental; no inferencia adicional."};
    group.addEventListener("click",select);
    group.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();select()}});
    group.append(circle,label,title);svg.appendChild(group);
  }
}

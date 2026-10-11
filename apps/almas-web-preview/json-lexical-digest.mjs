/** Exact lexical SHA-256 of a Python-serialized canonical JSON document.
 * Unlike JSON.parse -> JSON.stringify, this retains number spelling, such as
 * 1.0 versus 1, and exponent leading zeros. Keys are sorted as Python does.
 *
 * Reject duplicate keys and invalid JSON; no network access, eval or mutation.
 * A changed numeric notation cannot be silently accepted: the final digest
 * MUST equal both official M30 and M31 fingerprints.
 */
const MAX_BYTES=5*1024*1024;
const numberPattern=/-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/y;
const codePointCompare=(a,b)=>{
  const x=Array.from(a).map(c=>c.codePointAt(0)),y=Array.from(b).map(c=>c.codePointAt(0));
  for(let k=0;k<Math.min(x.length,y.length);k++){if(x[k]!==y[k])return x[k]-y[k]}
  return x.length-y.length;
};
export function canonicalizePythonRaw(raw){
  if(typeof raw!=="string"||raw.length>MAX_BYTES)throw Error("JSON size invalid");
  let i=0;
  const skip=()=>{while(i<raw.length&&/[\x20\t\r\n]/.test(raw[i]))i++};
  const parseString=()=>{
    if(raw[i]!=='"')throw Error("String expected");
    const start=i++;
    while(i<raw.length){
      const c=raw[i++];
      if(c==='"')return JSON.parse(raw.slice(start,i));
      if(c==="\\") {
        if(i>=raw.length)throw Error("Invalid escape");
        const esc=raw[i++];
        if(esc==="u")i+=4;
      }
    }
    throw Error("Unterminated JSON string");
  };
  const parse=(depth=0)=>{
    if(depth>128)throw Error("Max nesting exceeded");
    skip();const c=raw[i];
    if(c==='"')return {t:"s",v:parseString()};
    if(c==='{'||c==='['){
      const object=c==='{';i++;skip();
      const end=object?'}':']',list=[],keys=new Set();
      if(raw[i]===end){i++;return {t:object?"o":"a",v:list}}
      while(true){
        let key=null;
        if(object){skip();key=parseString();if(keys.has(key))throw Error("Duplicate JSON key");
          keys.add(key);skip();if(raw[i++]!==':')throw Error("Expected colon")}
        const value=parse(depth+1);list.push(object?[key,value]:value);skip();
        const next=raw[i++];
        if(next===end)break;
        if(next!==',')throw Error("Expected comma");
      }
      return {t:object?"o":"a",v:list};
    }
    for(const token of ["null","true","false"]){
      if(raw.startsWith(token,i)){i+=token.length;return {t:"literal",v:token}}
    }
    numberPattern.lastIndex=i;
    const m=numberPattern.exec(raw);
    if(!m)throw Error("JSON value expected");
    i=numberPattern.lastIndex;return {t:"num",v:m[0]};
  };
  const tree=parse();skip();if(i!==raw.length)throw Error("Trailing JSON data");
  const encode=node=>{
    switch(node.t){
      case "literal":case "num":return node.v;
      case "s":return JSON.stringify(node.v);
      case "a":return "["+node.v.map(encode).join(",")+"]";
      case "o":return "{"+node.v.slice().sort((x,y)=>codePointCompare(x[0],y[0]))
        .map(([key,value])=>JSON.stringify(key)+":"+encode(value)).join(",")+"}";
      default:throw Error("Unknown JSON node");
    }
  };
  return encode(tree);
}
export async function digestCanonicalRaw(raw){
  try{
    const normalized=canonicalizePythonRaw(raw);
    const bytes=new TextEncoder().encode(normalized);
    const digest=await crypto.subtle.digest("SHA-256",bytes);
    return {ok:true,hash:Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,"0")).join("")};
  }catch{
    return {ok:false,hash:null,reason:"No se pudo verificar el SHA-256 sobre los literales numéricos originales."};
  }
}

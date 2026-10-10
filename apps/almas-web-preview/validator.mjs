// Isolated structural preflight only; NOT complete JSON Schema Draft 2020-12 validation.
// No mutation, network, index calculation or Atacires promotion.
export function structuralPreflight(d) {
  const errors=[], fail=(path,reason)=>errors.push({path,reason});
  const object=v=>v!==null&&typeof v==="object"&&!Array.isArray(v);
  const own=(v,k)=>Object.prototype.hasOwnProperty.call(v,k);
  const numeric=(v,max,nullable=true)=> (nullable&&v===null)||(typeof v==="number"&&Number.isFinite(v)&&v>=0&&v<=max);
  const required=["schema_version","analysis_mode","analysis_profile","profile_policy_id","astronomy_backend","evidence","models","indices","pairwise_idd","coverage","robustness","counterevidence","counterevidence_state","ontology","doctrine","temporal","limitations","assembly"];
  const allowed=new Set([...required,"natal_context","relationship_field","dynamic_phases","actor_states","phase_transitions","doctrinal_sequences","temporal_sequence_graph","temporal_layers","root_recurrence","causal_firewall","preregistered_predictions","angular_robustness","semantic_motifs","time_sensitivity","ontological_discrimination","null_models","draconic_context","lots_context","surrender_vestal","ssar","vedic"]);
  const modelKeys=["iem","state","core","support","iem_pre","iem_final","ice","ice_state","supported_gate","birth_time_gate_required","birth_time_gate_satisfied"];
  const states=["SUPPORTED","COMPATIBLE","INSUFFICIENT","CONTRADICTED","NOT_EVALUABLE"];
  if(!object(d))return {ok:false,kind:"PREFLIGHT_ONLY",errors:[{path:"$",reason:"object required"}]};
  for(const k of required)if(!own(d,k))fail(k,"required field absent");
  for(const k of Object.keys(d))if(!allowed.has(k))fail(k,"unrecognized top-level property");
  if(d.schema_version!=="1.0.0")fail("schema_version","unsupported");
  if(!["FULL","TEMPORAL"].includes(d.analysis_mode))fail("analysis_mode","unrecognized");
  if(!["FULL_MULTIDISCIPLINARY","FULL_ASTROLOGY","TEMPORAL","SOUL_CONTRACT"].includes(d.analysis_profile))fail("analysis_profile","unrecognized");
  if(d.profile_policy_id!=="ALMAS_ANALYSIS_PROFILES_V1")fail("profile_policy_id","unrecognized");
  for(const k of ["evidence","counterevidence","doctrine","limitations"])if(!Array.isArray(d[k]))fail(k,"array required");
  for(const k of ["models","indices","pairwise_idd","coverage","robustness","counterevidence_state","ontology","temporal","assembly","astronomy_backend"])if(!object(d[k]))fail(k,"object required");
  if(object(d.indices)){
    for(const k of ["IDD","IAT","ICC","IRC","ICE"])if(!own(d.indices,k)||!numeric(d.indices[k],100))fail("indices."+k,"expected value 0–100 or null");
    for(const k of Object.keys(d.indices))if(!["IDD","IAT","ICC","IRC","ICE"].includes(k))fail("indices."+k,"unrecognized index");
  }
  if(object(d.models)){
    for(const k of ["AF","KA","AG","LG"]){
      const m=d.models[k];
      if(!object(m)){fail("models."+k,"model required");continue}
      for(const key of modelKeys)if(!own(m,key))fail("models."+k+"."+key,"required field absent");
      for(const key of Object.keys(m))if(!modelKeys.includes(key))fail("models."+k+"."+key,"unexpected property");
      if(!states.includes(m.state))fail("models."+k+".state","invalid");
      for(const key of ["iem","ice","iem_final"])if(!numeric(m[key],100))fail("models."+k+"."+key,"range 0–100/null");
      if(!numeric(m.iem_pre,100,false))fail("models."+k+".iem_pre","range 0–100 required");
      if(!numeric(m.core,1,false)||!numeric(m.support,1))fail("models."+k+".core/support","range 0–1 or null for support");
      for(const key of ["supported_gate","birth_time_gate_required","birth_time_gate_satisfied"])if(typeof m[key]!=="boolean")fail("models."+k+"."+key,"boolean required");
      if(m.ice_state==="NOT_EVALUABLE"&&(m.ice!==null||m.iem_final!==null||m.supported_gate!==false))fail("models."+k+".ice_state","NOT_EVALUABLE requires null ICE and final IEM and false gate");
      else if(m.ice_state==="EVALUABLE"&&(!numeric(m.ice,100,false)||!numeric(m.iem_final,100,false)))fail("models."+k+".ice_state","EVALUABLE requires numeric ICE and final IEM");
      else if(!["NOT_EVALUABLE","EVALUABLE"].includes(m.ice_state))fail("models."+k+".ice_state","invalid");
    }
    for(const k of Object.keys(d.models))if(!["AF","KA","AG","LG"].includes(k))fail("models."+k,"unrecognized model");
  }
  if(object(d.astronomy_backend)){
    const a=d.astronomy_backend;
    for(const k of ["state","backend_id","backend_version","provenance_state","provenance"])if(!own(a,k))fail("astronomy_backend."+k,"required field absent");
    if(!["AVAILABLE","NOT_AVAILABLE"].includes(a.state))fail("astronomy_backend.state","invalid");
    if(!["DECLARED","NOT_DECLARED","NOT_AVAILABLE"].includes(a.provenance_state))fail("astronomy_backend.provenance_state","invalid");
  }
  if(object(d.counterevidence_state)&&typeof d.counterevidence_state.ice_evaluable!=="boolean")fail("counterevidence_state.ice_evaluable","boolean required");
  return {ok:errors.length===0,kind:"PREFLIGHT_ONLY",errors};
}
export function formatOriginal(v){return v===null||v===undefined?"No evaluable":typeof v==="boolean"?(v?"Sí":"No"):String(v)}

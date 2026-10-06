"""Señales sombra en vocabulario M26, sin entrada en agregación productiva."""
from collections import defaultdict
from ..temporal_dependency import FAMILY_CLUSTERS
from ..evidence_handlers import AXIS_GROUPS
from .provenance import fingerprint_payload

def to_temporal_signals(result, subject_id, roots):
    if len(roots)>10000:raise ValueError("Límite de raíces excedido.")
    signals=[]
    passes=defaultdict(int)
    roots_by_endpoint=defaultdict(list)
    for root in roots:
        if not isinstance(root,dict) or not isinstance(root.get('root_key'),str) or not root.get('root_id'):
            continue
        for endpoint in root['root_key'].split('|')[:2]:
            roots_by_endpoint[endpoint].append(root)
    for index,event in enumerate(result['events']):
        signature=(event['source_point'],event['target_point'],event['oriented_aspect_deg'])
        passes[signature]+=1
        endpoint=f"{subject_id}:{AXIS_GROUPS.get(event['source_point'], event['source_point'])}"
        matched=roots_by_endpoint.get(endpoint,[])
        # Cada vínculo se conserva; no convierte varias raíces en varias evidencias temporales.
        for root in matched or [None]:
            root_id=root['root_id'] if root else None
            identity={'input':result['provenance']['input_fingerprint'],'event':event,'root_id':root_id}
            signals.append({'signal_id':'ATACIR_'+fingerprint_payload(identity),
                            'execution_mode':'SHADOW','layer':'TEMPORAL','temporal_family':'TATACIR','technique':'UNIFORM_CYCLE',
                            'technique_variant':'C'+str(result['calculation']['cycle_years']),
                            'root_id':root_id,'anchored':root is not None,
                            'dependency_group':'ATACIR_FAMILY','dependency_cluster':FAMILY_CLUSTERS['TATACIR'],
                            'activation_class':'ENDPOINT_ACTIVATION' if root else 'UNANCHORED',
                            'window_status':'EXPLORATORY' if root else 'UNANCHORED',
                            'source_subject':subject_id,'source_point':event['source_point'],
                            'target_point':event['target_point'],'aspect_deg':event['aspect_deg'],
                            'oriented_aspect_deg':event['oriented_aspect_deg'],'exact_datetime':event['exact_datetime'],
                            'orb':result['calculation']['orb_deg'],'angular_residual_deg':event['angular_residual_deg'],
                            'window_start_utc':event['window_start_utc'],'window_end_utc':event['window_end_utc'],
                            'pass_number':passes[signature],'preregistered':False,'iat_eligible':False,
                            'creates_structural_root':False,'predicts_real_world_event':False,
                            'provenance':result['provenance']})
            if len(signals)>10000:raise ValueError("Límite de vínculos temporales excedido.")
    for signal in signals:
        variants=result["provenance"]["node_variants"]
        variant=variants.get(signal["source_point"]) or variants.get(signal["target_point"])
        if variant:
            signal["node_variant"]=variant
            signal["nodal_axis_id"]="LUNAR_NODE_AXIS"
    # Repetir una solicitud no produce múltiples copias de una señal idéntica.
    return list({s['signal_id']:s for s in signals}.values())

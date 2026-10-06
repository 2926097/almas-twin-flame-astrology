"""Huellas reproducibles; el instante operativo no entra en la huella del cálculo."""
import hashlib
import json

def serialize(payload):
    return json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)

def fingerprint_payload(payload):
    return hashlib.sha256(serialize(payload).encode('utf-8')).hexdigest()

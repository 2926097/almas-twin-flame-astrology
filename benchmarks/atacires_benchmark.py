"""Presupuesto reproducible: core sintético y M26 desactivado, sin datos privados."""
import json
from pathlib import Path
import platform
import os
import statistics
import sys
import time
import tracemalloc
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from almas_tfa.atacires.engine import calculate
from almas_tfa.module_contract import ModuleContext
from almas_tfa.integrations.atacires_temporal import make_atacires_temporal_handler
from almas_tfa.temporal_handlers import m26_temporal_activation

def measure(fn,n=200):
    fn();values=[]
    for _ in range(n):
        start=time.perf_counter_ns();fn();values.append((time.perf_counter_ns()-start)/1e6)
    values.sort();return {'p50_ms':statistics.median(values),'p95_ms':values[int(.95*n)],'p99_ms':values[int(.99*n)],'iterations':n}

def main():
    data={'schema_version':'1.0','technique':'UNIFORM_CYCLE','datetime_local':'2000-01-01T00:00:00',
          'timezone_id':'Etc/UTC','start_utc':'2000-01-01T00:00:00Z','end_utc':'2050-01-01T00:00:00Z',
          'cycle_years':60,'year_days':365.2422,'natal_points':{f'P{i}':i*18. for i in range(20)},
          'positions_source':'SYNTHETIC_BENCHMARK','aspects_deg':[0,60,90,120,180],'orb_deg':1,'output_timezone':'Etc/UTC'}
    sig={'signal_id':'T1','root_id':'R1','temporal_family':'TTRANSIT','activation_class':'DIRECT_REPETITION','strength':.5,'window_status':'CURRENT_ACTIVE','preregistered':True,'structural_family':'SYN','exactitude_orb':.5,'preregistered_window_rule':'SYNTHETIC_BENCHMARK'}
    context=ModuleContext('M26','Temporal','FULL',{'temporal_signals':[sig]},{'independent_roots':{'roots':[{'root_id':'R1'}]}},{})
    os.environ["ALMAS_TEMPORAL_ATACIRES_ENABLED"]="false"
    off=make_atacires_temporal_handler(m26_temporal_activation)
    base=measure(lambda:m26_temporal_activation(context),2000);disabled=measure(lambda:off(context),2000)
    small={**data,'natal_points':{'P0':0.,'P1':90.}}
    core={'small':measure(lambda:calculate(small)),'medium':measure(lambda:calculate(data))}
    tracemalloc.start();calculate(data);_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    result={'python':platform.python_version(),'core':core,'peak_memory_bytes':peak,'m26_baseline':base,'m26_feature_off':disabled,
            'feature_off_p95_ratio':disabled['p95_ms']/base['p95_ms'],'method':'fixed synthetic geometry; ns timer; same process; no ephemeris',
            'limits':{'max_points':100,'max_aspects':20,'max_events_per_request':10000,'max_requests':16,'max_signals_total':10000,'max_combinations':40000},
            'metaphysical_validation':False}
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

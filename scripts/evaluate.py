"""Reproduce synthetic demonstration outputs, not a held-out benchmark.
Default is deterministic demo. --llm performs real configured inference; never
silently falls back. Remote calls still require explicit provider opt-in.
"""
import argparse,json,sys,platform
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analysis import AnalysisInput,analyze
from fixtures import run_fixture
from samples import SAMPLES
p=argparse.ArgumentParser();p.add_argument('--llm',action='store_true');p.add_argument('--output',default='tests/results/synthetic_evaluation.json');args=p.parse_args()
results=[]
for sample in SAMPLES:
    payload={k:sample[k] for k in ('requirement','source_before','source_after','tests_before','tests_after')}
    payload['mode']='llm' if args.llm else 'demo'
    result=analyze(AnalysisInput(**payload))
    results.append({'sample_id':sample['id'],'analysis':result,'trusted_execution':run_fixture(sample['id'])})
report={'scope':'App-authored synthetic development examples; not held-out quality evaluation','python':platform.python_version(),'actual_llm_requested':args.llm,'cases':results}
path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2))
print(f'Saved {len(results)} synthetic case reports to {path}')

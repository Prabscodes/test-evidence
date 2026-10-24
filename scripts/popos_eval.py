"""One-shot local readout. The run path never opens labels.json.

Run with the app venv: python scripts/popos_eval.py run
Only after outputs are sealed: python scripts/popos_eval.py score
"""
import hashlib,json,sys,time,subprocess
from datetime import datetime,timezone
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1]
SET=ROOT/'tests/popos_frozen_v1'
OUT=ROOT/'tests/results/popos/frozen_v1'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reduce_status(values):
    for status in ['potentially_missing','unresolved','supported']:
        if status in values:return status
    return 'error'

def run():
    manifest=json.loads((SET/'manifest.json').read_text())
    assert digest(SET/'inputs.json')==manifest['files']['inputs.json']
    with httpx.Client(timeout=5,trust_env=False) as preflight:
        preflight.get('http://127.0.0.1:18081/health').raise_for_status()
    OUT.mkdir(exist_ok=False)
    sources={p.relative_to(ROOT).as_posix():digest(p) for p in list(ROOT.glob('*.py'))+list((ROOT/'static').glob('*'))}
    (OUT/'source_sha256.json').write_text(json.dumps(sources,indent=2))
    records=[]
    with httpx.Client(base_url='http://127.0.0.1:8765',timeout=360,trust_env=False) as c:
        status=c.get('/api/status').json()
        assert status['processing_location']=='loopback_endpoint'
        assert status['model']=='te-dolphin3-8b-q4'
        for case in json.loads((SET/'inputs.json').read_text()):
            started=time.monotonic()
            record={'id':case['id'],'started_at':datetime.now(timezone.utc).isoformat()}
            try:
                response=c.post('/api/analyze',json=case['payload'])
                record.update(http_status=response.status_code,response=response.json())
            except Exception as e:record['error_type']=type(e).__name__
            record['elapsed_seconds']=round(time.monotonic()-started,3)
            records.append(record)
            (OUT/(case['id']+'.json')).write_text(json.dumps(record,indent=2)+'\n')
            print(case['id'],record.get('http_status'),record['elapsed_seconds'],flush=True)
    seal={'completed_at':datetime.now(timezone.utc).isoformat(),'inputs_sha256':digest(SET/'inputs.json'),'provider_status':status,'protocol_sha256':digest(SET/'protocol.json'),'evaluator_sha256':digest(Path(__file__)),'runtime_manifest_sha256':digest(ROOT/'tests/results/popos/selected_runtime.json'),'launch_script_sha256':digest(ROOT/'scripts/launch_popos.py'),'outputs':{p.name:digest(p) for p in OUT.glob('*.json')}}
    (OUT/'seal.json').write_text(json.dumps(seal,indent=2)+'\n')

def score():
    manifest=json.loads((SET/'manifest.json').read_text());seal=json.loads((OUT/'seal.json').read_text())
    assert digest(SET/'labels.json')==manifest['files']['labels.json']
    assert all(digest(OUT/k)==v for k,v in seal['outputs'].items())
    mapping={'checked':'supported','gap':'potentially_missing','unknown':'unresolved'}
    rows=[]
    for label in json.loads((SET/'labels.json').read_text()):
        record=json.loads((OUT/(label['id']+'.json')).read_text());response=record.get('response',{})
        guarded=reduce_status([x['status'] for x in response.get('obligations',[])])
        try:
            raw=json.loads(response['provider']['raw_response'])
            raw_status=reduce_status([mapping[x['test_support']] for x in raw['obligations']])
        except (ValueError,KeyError,TypeError):raw_status='error'
        rows.append(dict(id=label['id'],expected=label['expected_status'],raw=raw_status,guarded=guarded,elapsed_seconds=record['elapsed_seconds'],basis=label['basis']))
    summary={'scope':manifest['scope'],'cases':rows,'counts':{}}
    for layer in ['raw','guarded']:
        summary['counts'][layer]={'label_matches':sum(x[layer]==x['expected'] for x in rows),'total':len(rows),'false_support':sum(x[layer]=='supported' and x['expected']!='supported' for x in rows),'false_accusation':sum(x[layer]=='potentially_missing' and x['expected']!='potentially_missing' for x in rows),'unresolved':sum(x[layer]=='unresolved' for x in rows),'errors':sum(x[layer]=='error' for x in rows)}
    (OUT/'score.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':
    {'run':run,'score':score}[sys.argv[1]]()

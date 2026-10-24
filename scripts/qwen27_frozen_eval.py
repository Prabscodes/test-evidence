"""One label-free, fixed-profile local frozen readout; never executes snippets."""
from pathlib import Path
from datetime import datetime,timezone
import json,time,hashlib,subprocess,urllib.request,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.durable_request import atomic,run
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 data=ROOT/'tests/qwen27_frozen_v2';protocol=json.loads((data/'manifest.json').read_text());source=data/'inputs.json';assert sha(source)==protocol['inputs_sha256'];cases=json.loads(source.read_text());out=ROOT/'tests/results/qwen27_v2';out.mkdir(exist_ok=False);started=time.monotonic();op=urllib.request.build_opener(urllib.request.ProxyHandler({}));outcomes=[]
 atomic(out/'run_manifest.json',(json.dumps({'started_at':datetime.now(timezone.utc).isoformat(),'protocol_sha256':sha(data/'manifest.json'),'inputs_sha256':sha(source),'runner_sha256':sha(Path(__file__)),'labels_read':False,'scope':'New author-authored synthetic cases; not independent benchmark. Frozen settings; no retries.','concurrent_cpu_tasks_note':'Local container build and silent video editing may run; no other GPU workload is started.'},indent=2)+'\n').encode())
 for case in cases:
  remaining=protocol['budget_seconds']-(time.monotonic()-started)
  if remaining<305:outcomes.append({'id':case['id'],'outcome':'not_started_time_budget'});continue
  assert all(sha(ROOT/name)==value for name,value in protocol['source_sha256'].items()),'Pinned source changed; no next request sent'
  with op.open('http://127.0.0.1:8765/api/status',timeout=5) as f:state=json.load(f)
  assert not state['public_mode'] and state['model']=='te-qwen35-27b-ct4' and not state['analysis_running']
  with op.open('http://127.0.0.1:18083/metrics',timeout=5) as f:activity=[x for x in f.read().decode().splitlines() if x.startswith(('vllm:num_requests_running{','vllm:num_requests_waiting{'))]
  assert activity and all(float(x.rsplit(' ',1)[1])==0 for x in activity)
  free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip());assert free>=6000
  spec=out/(case['id']+'_request.json');atomic(spec,(json.dumps({'url':'http://127.0.0.1:8765/api/analyze','body':case['payload'],'timeout_seconds':300},indent=2)+'\n').encode());print(case['id'],'starting',flush=True)
  try:
   receipt=run(spec,out/case['id']);outcome={'id':case['id'],'outcome':receipt['status'],'http_status':receipt['http_status'],'seconds':receipt['elapsed_seconds'],'gpu_free_mib_before':free};outcomes.append(outcome);print(json.dumps(outcome),flush=True)
   if receipt['http_status']>=500:break
  except BaseException as e:
   outcomes.append({'id':case['id'],'outcome':'uncertain','error_type':type(e).__name__});break
 completed_ids={x['id'] for x in outcomes}
 outcomes.extend({'id':case['id'],'outcome':'not_started_after_stop'} for case in cases if case['id'] not in completed_ids)
 files={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
 atomic(out/'seal.json',(json.dumps({'sealed_at':datetime.now(timezone.utc).isoformat(),'complete':all(x['outcome']=='response_saved' for x in outcomes),'outcomes':outcomes,'files':files},indent=2)+'\n').encode());print('Sealed',len(outcomes),'outcomes',flush=True)
if __name__=='__main__':main()

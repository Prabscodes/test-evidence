"""One private loopback evaluation request, with durable intent/raw receipt.
No retries, response interpretation, label loading, GPU management or app integration.
Run under a user service manager to outlive a terminal/tool client.
"""
import argparse,hashlib,json,os,tempfile,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
import httpx

def atomic(path,data):
    """Commit bytes before publishing the state that references them."""
    fd,name=tempfile.mkstemp(prefix='.pending-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(name,path)
        directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if os.path.exists(name):os.unlink(name)

def run(spec_path,destination):
    raw=Path(spec_path).read_bytes();spec=json.loads(raw);url=spec['url'];parsed=urlsplit(url)
    if parsed.scheme!='http' or parsed.hostname!='127.0.0.1' or parsed.username or parsed.password or parsed.query or parsed.fragment or not parsed.port:
        raise ValueError('Evaluation destination must be exact loopback HTTP with a port and no URL credentials/query/fragment.')
    timeout=spec.get('timeout_seconds',300)
    if not isinstance(timeout,(int,float)) or not 1<=timeout<=300:raise ValueError('Timeout must be from1 to300 seconds.')
    dest=Path(destination);dest.mkdir(mode=0o700,parents=False,exist_ok=False)
    parent=os.open(dest.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(parent)
    finally:os.close(parent)
    state={'status':'prepared','created_at':datetime.now(timezone.utc).isoformat(),'request_sha256':hashlib.sha256(raw).hexdigest(),'pid':os.getpid(),'parent_pid':os.getppid(),'process_group':os.getpgrp(),'session_id':os.getsid(0),'scope':'Synthetic/local evaluation transport only; a saved HTTP response is not a validated model judgment.'}
    atomic(dest/'request.json',raw);atomic(dest/'state.json',(json.dumps(state,indent=2)+'\n').encode())
    state.update(status='dispatched',dispatched_at=datetime.now(timezone.utc).isoformat())
    atomic(dest/'state.json',(json.dumps(state,indent=2)+'\n').encode());start=time.monotonic()
    try:
        with httpx.Client(timeout=timeout,trust_env=False,follow_redirects=False) as client:
            response=client.post(url,json=spec['body'])
        # Save exact HTTP response bytes before any downstream JSON/model parsing.
        atomic(dest/'response.body',response.content)
        state.update(status='response_saved',http_status=response.status_code,elapsed_seconds=round(time.monotonic()-start,6),response_sha256=hashlib.sha256(response.content).hexdigest(),response_bytes=len(response.content),completed_at=datetime.now(timezone.utc).isoformat())
        atomic(dest/'state.json',(json.dumps(state,indent=2)+'\n').encode());return state
    except BaseException as exc:
        state.update(status='uncertain',error_type=type(exc).__name__,elapsed_seconds=round(time.monotonic()-start,6),instruction='Do not repeat this dispatched attempt. Inspect any saved response and provider state; completion may be unknown.')
        atomic(dest/'state.json',(json.dumps(state,indent=2)+'\n').encode());raise

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('spec',type=Path);p.add_argument('destination',type=Path);a=p.parse_args()
    run(a.spec,a.destination)

"""Single-process public MVP admission. No content persistence or upstream selection."""
from collections import deque
from contextlib import contextmanager
import hashlib,os,threading,time
from urllib.parse import urlsplit
from fastapi import HTTPException
import provider

class PublicGuard:
    def __init__(self):
        self._rate_lock=threading.Lock();self._work=threading.Lock();self._peers={};self._total=deque();self._salt=os.urandom(32);self._started=None
    @staticmethod
    def enabled():return os.getenv('TE_PUBLIC')=='1'
    def allow_post(self,peer):
        if not self.enabled():return True
        now=time.monotonic();key=hashlib.sha256(self._salt+str(peer).encode()).digest()
        with self._rate_lock:
            while self._total and now-self._total[0]>=60:self._total.popleft()
            for k in list(self._peers):
                q=self._peers[k]
                while q and now-q[0]>=60:q.popleft()
                if not q:del self._peers[k]
            q=self._peers.get(key)
            if len(self._total)>=20 or (q is not None and len(q)>=6) or (q is None and len(self._peers)>=1024):return False
            if q is None:q=deque();self._peers[key]=q
            q.append(now);self._total.append(now);return True
    def status(self):
        enabled=self.enabled();config=provider.status();name=os.getenv('TE_PUBLIC_PROVIDER_NAME','').strip();policy=os.getenv('TE_PUBLIC_PROVIDER_POLICY_URL','').strip()
        try:
            u=urlsplit(policy);policy_ok=u.scheme=='https' and bool(u.hostname) and not (u.username or u.password or u.query or u.fragment)
        except ValueError:policy_ok=False
        ready=enabled and config['backend']=='openai-compatible' and config['configured'] and config['endpoint_config_valid'] and config['processing_location']=='external_endpoint' and config['endpoint_calls_enabled'] and config['timeout_config_valid'] and config['temperature_config_valid'] and bool(os.getenv('TE_API_KEY')) and 0<len(name)<=80 and policy_ok
        token=hashlib.sha256((name+'\n'+policy+'\n'+os.getenv('TE_API_BASE','')+'\n'+config['model']).encode()).hexdigest() if ready else ''
        return {'provider_consent_token':token,'public_mode':enabled,'public_live_ready':bool(ready),'provider_processing_required':bool(ready),'public_provider_name':name if ready else '', 'public_provider_policy_url':policy if ready else '', 'public_work_running':enabled and self._work.locked()}
    def require_live(self,consent):
        if not self.enabled():return
        if not self.status()['public_live_ready']:raise HTTPException(503,'Live public inference is unavailable. No review was sent. A configured approved hosted provider is required; labelled demo remains separate.')
        if consent!=self.status()['provider_consent_token']:raise HTTPException(400,'Explicit provider-processing consent is required before sending source, tests and review context to the named external provider.')
    @contextmanager
    def work(self):
        if not self.enabled():yield;return
        if not self._work.acquire(blocking=False):raise HTTPException(429,'The public instance is handling another request. Wait before explicitly trying again; no request was queued.')
        self._started=time.monotonic()
        try:yield
        finally:self._started=None;self._work.release()

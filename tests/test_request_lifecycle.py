import json,os,threading,time,unittest,socket
import uvicorn
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import httpx
from fastapi.testclient import TestClient
import app as app_module
from analysis import analyze as real_analyze
from samples import SAMPLES

def payload(mode='demo'):
    return {**{k:SAMPLES[0][k] for k in ['requirement','source_before','source_after','tests_before','tests_after']},'mode':mode}

class RequestLifecycleTests(unittest.TestCase):
    def setUp(self):self.client=TestClient(app_module.app)
    def test_running_status_and_duplicate_request_remain_locked_until_completion(self):
        entered=threading.Event();release=threading.Event();calls=[]
        def held(req):
            calls.append(req);entered.set()
            if not release.wait(5):raise RuntimeError('test wait expired')
            return real_analyze(req)
        with patch('app.analyze',side_effect=held),ThreadPoolExecutor(max_workers=1) as pool:
            pending=pool.submit(self.client.post,'/api/analyze',json=payload())
            try:
                self.assertTrue(entered.wait(2))
                state=self.client.get('/api/status').json()
                self.assertTrue(state.get('analysis_running'),state)
                self.assertGreaterEqual(state['analysis_elapsed_seconds'],0)
                self.assertNotIn('source_after',json.dumps(state))
                self.assertEqual(self.client.post('/api/analyze',json=payload()).status_code,429)
                self.assertEqual(len(calls),1)
            finally:release.set()
            self.assertEqual(pending.result(timeout=5).status_code,200)
        state=self.client.get('/api/status').json()
        self.assertIs(state.get('analysis_running'),False)
        self.assertIsNone(state.get('analysis_elapsed_seconds'))
    def test_disconnected_http_client_does_not_release_active_review_lock(self):
        entered=threading.Event();release=threading.Event();calls=[]
        def held(req):
            calls.append(req);entered.set()
            if not release.wait(5):raise RuntimeError('test wait expired')
            return real_analyze(req)
        listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen(8)
        port=listener.getsockname()[1]
        server=uvicorn.Server(uvicorn.Config(app_module.app,host='127.0.0.1',port=port,log_level='critical',lifespan='off'))
        thread=threading.Thread(target=server.run,kwargs={'sockets':[listener]},daemon=True)
        with patch('app.analyze',side_effect=held):
            thread.start()
            try:
                deadline=time.monotonic()+2
                while not server.started and time.monotonic()<deadline:time.sleep(.01)
                self.assertTrue(server.started)
                body=json.dumps(payload()).encode()
                conn=socket.create_connection(('127.0.0.1',port),timeout=2)
                conn.sendall(('POST /api/analyze HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\nContent-Length: '+str(len(body))+'\r\n\r\n').encode()+body)
                self.assertTrue(entered.wait(2));conn.close()
                with httpx.Client(base_url='http://127.0.0.1:'+str(port),trust_env=False,timeout=2) as client:
                    self.assertTrue(client.get('/api/status').json()['analysis_running'])
                    self.assertEqual(client.post('/api/analyze',json=payload()).status_code,429)
                self.assertEqual(len(calls),1)
            finally:
                release.set();server.should_exit=True;thread.join(timeout=5);listener.close()
            self.assertFalse(thread.is_alive())
        self.assertFalse(app_module._lock.locked())

    def check_failure(self,handler,expected,phrase):
        calls=[]
        def counted(request):calls.append(request);return handler(request)
        transport=httpx.MockTransport(counted)
        client=httpx.Client(transport=transport)
        env={'TE_PROVIDER':'openai-compatible','TE_API_BASE':'http://127.0.0.1:18081/v1','TE_MODEL':'local-test','TE_ALLOW_REMOTE':'1','TE_API_KEY':'SECRET-CREDENTIAL'}
        with patch.dict(os.environ,env,clear=True),patch('provider.httpx.Client',return_value=client):
            response=self.client.post('/api/analyze',json=payload('llm'))
        self.assertEqual(response.status_code,expected,response.text)
        self.assertIn(phrase,response.json()['detail'])
        self.assertNotIn('SECRET',response.text)
        self.assertEqual(len(calls),1,'No automatic transport retry')
        self.assertFalse(self.client.get('/api/status').json().get('analysis_running'))
    def test_timeout_is_actionable_and_does_not_retry(self):
        def fail(request):raise httpx.ReadTimeout('SECRET-UPSTREAM',request=request)
        self.check_failure(fail,504,'may still be finishing')
    def test_unreachable_model_is_actionable_and_sanitized(self):
        def fail(request):raise httpx.ConnectError('SECRET-HOST',request=request)
        self.check_failure(fail,503,'model server')
    def test_missing_model_is_actionable_without_upstream_body(self):
        self.check_failure(lambda request:httpx.Response(404,json={'error':'SECRET-SOURCE'},request=request),503,'model name')
    def test_context_rejection_suggests_shorter_excerpts_without_leaking_body(self):
        self.check_failure(lambda request:httpx.Response(400,json={'error':'SECRET-SOURCE'},request=request),400,'Shorten')
    def test_access_rejection_keeps_credentials_out_of_error(self):
        self.check_failure(lambda request:httpx.Response(401,json={'error':'SECRET-CREDENTIAL'},request=request),502,'access')

if __name__=='__main__':unittest.main()

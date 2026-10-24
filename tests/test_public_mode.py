import os,json,unittest,threading,time,asyncio
from unittest.mock import patch
import httpx
from fastapi.testclient import TestClient
import app as server
from tests.test_duplicate_json import DATA,wrapped

ENV={'TE_PUBLIC':'1','TE_PROVIDER':'openai-compatible','TE_API_BASE':'https://provider.example/v1','TE_API_KEY':'SERVER_ONLY_SENTINEL','TE_ALLOW_REMOTE':'1','TE_TIMEOUT_SECONDS':'90','TE_PUBLIC_PROVIDER_NAME':'Test provider','TE_PUBLIC_PROVIDER_POLICY_URL':'https://provider.example/privacy'}
class PublicModeTests(unittest.TestCase):
 def setUp(self):
  self.env=patch.dict(os.environ,ENV,clear=True);self.env.start();from public_runtime import PublicGuard
  self.guard=patch('app.public_guard',PublicGuard());self.guard.start();self.client=TestClient(server.app)
 def tearDown(self):self.guard.stop();self.env.stop()
 def test_public_llm_requires_explicit_processing_consent(self):
  with patch('analysis.provider.infer') as infer:r=self.client.post('/api/analyze',json=DATA)
  self.assertEqual(r.status_code,400);self.assertIn('consent',r.text.lower());infer.assert_not_called()
 def test_absent_public_provider_fails_closed(self):
  with patch.dict(os.environ,{'TE_API_KEY':''}),patch('analysis.provider.infer') as infer:r=self.client.post('/api/analyze',json=DATA,headers={'X-Provider-Consent':self.client.get('/api/status').json()['provider_consent_token']})
  self.assertEqual(r.status_code,503);infer.assert_not_called()
 def test_public_blocks_loopback_provider_and_local_model_loading(self):
  for change in [{'TE_API_BASE':'http://127.0.0.1:18083/v1'},{'TE_PROVIDER':'local'}]:
   with self.subTest(change=change),patch.dict(os.environ,change),patch('analysis.provider.infer') as infer:r=self.client.post('/api/analyze',json=DATA,headers={'X-Provider-Consent':self.client.get('/api/status').json()['provider_consent_token']});self.assertEqual(r.status_code,503);infer.assert_not_called()
 def test_public_timeout_config_is_bounded(self):
  with patch.dict(os.environ,{'TE_TIMEOUT_SECONDS':'300'}),patch('analysis.provider.infer') as infer:r=self.client.post('/api/analyze',json=DATA,headers={'X-Provider-Consent':self.client.get('/api/status').json()['provider_consent_token']})
  self.assertEqual(r.status_code,503);infer.assert_not_called()
 def test_consented_request_uses_server_config_without_secret_echo(self):
  with patch('analysis.provider.infer',return_value=(wrapped('"test_support":"checked"'),{'actual_inference':True,'model':'synthetic-public-test'})) as infer:r=self.client.post('/api/analyze',json=DATA,headers={'X-Provider-Consent':self.client.get('/api/status').json()['provider_consent_token']})
  self.assertEqual(r.status_code,200);infer.assert_called_once();self.assertNotIn('SERVER_ONLY_SENTINEL',r.text)
  status=self.client.get('/api/status');self.assertTrue(status.json()['public_mode']);self.assertTrue(status.json()['provider_processing_required']);self.assertNotIn('SERVER_ONLY_SENTINEL',status.text);self.assertNotIn('https://provider.example/v1',status.text)
 def test_client_cannot_choose_upstream(self):
  with patch('analysis.provider.infer') as infer:r=self.client.post('/api/analyze',json={**DATA,'api_base':'https://attacker.example'},headers={'X-Provider-Consent':self.client.get('/api/status').json()['provider_consent_token']})
  self.assertEqual(r.status_code,422);infer.assert_not_called()
 def test_public_post_rate_is_bounded(self):
  # Unknown routes exercise admission without executing fixtures/inference.
  codes=[self.client.post('/api/nonexistent').status_code for _ in range(7)]
  self.assertEqual(codes[:6],[404]*6);self.assertEqual(codes[6],429)
 def test_public_body_read_has_timeout(self):
  class Slow(httpx.AsyncByteStream):
   async def __aiter__(self):
    await asyncio.sleep(.05);yield b'{}'
  async def call():
   async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app),base_url='http://test') as c:return await c.post('/api/analyze',content=Slow())
  with patch('app.PUBLIC_BODY_TIMEOUT_SECONDS',.01,create=True):r=asyncio.run(call())
  self.assertEqual(r.status_code,408)
 def test_fixture_and_review_share_public_work_slot(self):
  from public_runtime import PublicGuard
  guard=PublicGuard();started=threading.Event();release=threading.Event()
  def blocked(_):started.set();release.wait(2);return {'ok':True}
  with patch('app.public_guard',guard),patch('app.run_fixture',side_effect=blocked):
   worker=threading.Thread(target=lambda:self.client.post('/api/fixtures/example/run'));worker.start();self.assertTrue(started.wait(1))
   try:
    with patch('analysis.provider.infer') as infer:r=self.client.post('/api/analyze',json=DATA,headers={'X-Provider-Consent':self.client.get('/api/status').json()['provider_consent_token']})
    self.assertEqual(r.status_code,429);infer.assert_not_called()
   finally:release.set();worker.join(3)

 def test_consent_is_bound_to_server_provider_configuration(self):
  token=self.client.get('/api/status').json()['provider_consent_token']
  with patch.dict(os.environ,{'TE_API_BASE':'https://other.example/v1'}),patch('analysis.provider.infer') as infer:
   response=self.client.post('/api/analyze',json=DATA,headers={'X-Provider-Consent':token})
  self.assertEqual(response.status_code,400);infer.assert_not_called()
 def test_rate_window_and_global_ceiling(self):
  from public_runtime import PublicGuard
  guard=PublicGuard()
  with patch('public_runtime.time.monotonic',return_value=0):
   self.assertTrue(all(guard.allow_post(str(n)) for n in range(20)))
   self.assertFalse(guard.allow_post('new'))
  with patch('public_runtime.time.monotonic',return_value=61):self.assertTrue(guard.allow_post('new'))
 def test_public_work_slot_released_on_error(self):
  from public_runtime import PublicGuard
  guard=PublicGuard()
  with self.assertRaises(ValueError):
   with guard.work():raise ValueError('synthetic')
  with guard.work():self.assertTrue(guard.status()['public_work_running'])

 def test_arbitrary_forwarded_headers_do_not_reset_peer_budget(self):
  codes=[self.client.post('/api/nonexistent',headers={'X-Forwarded-For':f'198.51.100.{n}','Forwarded':f'for=198.51.100.{n}'}).status_code for n in range(7)]
  self.assertEqual(codes[:6],[404]*6);self.assertEqual(codes[6],429)
 def test_public_errors_do_not_echo_upstream_body_or_source(self):
  from errors import ProviderFailure
  data={**DATA,'source_after':'PRIVATE_SOURCE_SENTINEL'}
  with patch('analysis.provider.infer',side_effect=ProviderFailure('http_failure')):
   response=self.client.post('/api/analyze',json=data,headers={'X-Provider-Consent':self.client.get('/api/status').json()['provider_consent_token']})
  self.assertEqual(response.status_code,502);self.assertNotIn('PRIVATE_SOURCE_SENTINEL',response.text);self.assertNotIn('SERVER_ONLY_SENTINEL',response.text)

 def test_public_validation_errors_do_not_echo_input_values(self):
  marker='PRIVATE_INPUT_SENTINEL'
  for body in [{**DATA,'mode':marker},{**DATA,'source_after':marker*2000}]:
   response=self.client.post('/api/analyze',json=body)
   self.assertEqual(response.status_code,422);self.assertNotIn(marker,response.text)

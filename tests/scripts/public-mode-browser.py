"""Real public UI/admission with synthetic provider only; no external model calls."""
import os,json,sys,time,socket,subprocess,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));from tests.test_duplicate_json import DATA
OUT=ROOT/'tests/results/public_mode_v1/browser';OUT.mkdir(exist_ok=False)
servers=[];logs=[]
for port,ready in [(8766,True),(8767,False)]:
 with socket.socket() as s:s.bind(('127.0.0.1',port))
 env=dict(os.environ,TE_PUBLIC='1',TE_PROVIDER='openai-compatible',TE_API_BASE='https://provider.example/v1',TE_API_KEY='SERVER_ONLY_SENTINEL' if ready else '',TE_ALLOW_REMOTE='1',TE_TIMEOUT_SECONDS='90',TE_PUBLIC_PROVIDER_NAME='Synthetic QA provider',TE_PUBLIC_PROVIDER_POLICY_URL='https://provider.example/privacy')
 code="""import sys,json,uvicorn
sys.path.insert(0,sys.argv[1]);import analysis;from errors import ProviderFailure
from tests.test_duplicate_json import wrapped
def fake(data):
 if data.get('clarification')=='simulate provider error':raise ProviderFailure('http_failure')
 return wrapped('"test_support":"checked"'),{'actual_inference':False,'backend':'synthetic-public-browser-QA','model':'synthetic-not-a-model'}
analysis.provider.infer=fake
uvicorn.run('app:app',host='127.0.0.1',port=int(sys.argv[2]),access_log=False,proxy_headers=False)
"""
 log=(OUT/f'server_{port}.log').open('w');logs.append(log);servers.append(subprocess.Popen([str(ROOT/'.venv/bin/python'),'-c',code,str(ROOT),str(port)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT))
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
try:
 for port in [8766,8767]:
  for _ in range(100):
   try:
    with op.open(f'http://127.0.0.1:{port}/api/status',timeout=1):break
   except OSError:time.sleep(.1)
  else:raise RuntimeError('Isolated public app not ready')
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True);page=browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True);page.set_default_timeout(15000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));posts=[]
  page.on('request',lambda r:posts.append(r.headers) if r.method=='POST' and r.url.endswith('/api/analyze') else None)
  page.goto('http://127.0.0.1:8766');page.wait_for_load_state('networkidle');assert page.locator('#provider-privacy').is_visible();assert 'Synthetic QA provider' in page.locator('#provider-processing-note').inner_text()
  for k in ['requirement','source_before','source_after','tests_before','tests_after']:page.fill('#'+k,DATA[k])
  page.select_option('#mode','llm');assert page.locator('#analyze').is_disabled();page.check('#provider-consent');assert page.locator('#analyze').is_enabled()
  with page.expect_response(lambda r:r.url.endswith('/api/analyze') and r.request.method=='POST') as pending:page.click('#analyze')
  data=pending.value.json();assert pending.value.status==200;page.wait_for_function('() => !document.getElementById("analyze").disabled');assert len(posts)==1 and posts[0].get('x-provider-consent')
  with page.expect_download() as d:page.click('#export-json')
  d.value.save_as(OUT/'own_review_export.json');assert 'SERVER_ONLY_SENTINEL' not in (OUT/'own_review_export.json').read_text();assert json.loads((OUT/'own_review_export.json').read_text())['artifacts']['source_after']==DATA['source_after']
  status=page.request.get('http://127.0.0.1:8766/api/status').json();page.route('**/api/status',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps({**status,'provider_consent_token':'changed-config','public_provider_name':'Changed QA provider'})))
  page.click('#check-status');page.wait_for_function('() => !document.getElementById("provider-consent").checked');assert page.locator('#analyze').is_disabled();page.unroute('**/api/status');page.click('#check-status');page.wait_for_function('() => document.getElementById("provider-processing-note").textContent.includes("Synthetic QA provider")');page.check('#provider-consent')
  page.fill('#clarification','simulate provider error');page.fill('#source_after','PRIVATE_ERROR_SOURCE_SENTINEL');assert page.locator('#export-json').is_disabled()
  with page.expect_response(lambda r:r.url.endswith('/api/analyze') and r.request.method=='POST') as pending:page.click('#analyze')
  assert pending.value.status==502;error_body=pending.value.text();assert 'PRIVATE_ERROR_SOURCE_SENTINEL' not in error_body and 'SERVER_ONLY_SENTINEL' not in error_body
  page.wait_for_function('() => !document.getElementById("error").hidden');assert page.locator('#export-json').is_disabled();page.screenshot(path=str(OUT/'desktop_consent_error.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(OUT/'mobile_consent_error.png'),full_page=True)
  rates=[page.request.post('http://127.0.0.1:8766/api/nonexistent',headers={'X-Forwarded-For':f'198.51.100.{n}','Forwarded':f'for=198.51.100.{n}'}).status for n in range(7)];assert 429 in rates
  page.goto('http://127.0.0.1:8767');page.wait_for_load_state('networkidle');assert 'live inference unavailable' in page.locator('#public-service-note').inner_text();page.select_option('#mode','llm');assert page.locator('#analyze').is_disabled();assert not page.locator('#provider-consent-label').is_visible()
  page.select_option('#mode','demo');page.select_option('#samples','missing_regression')
  with page.expect_response(lambda r:r.url.endswith('/api/analyze') and r.request.method=='POST') as pending:page.click('#analyze')
  demo=pending.value.json();assert not demo['provider']['actual_inference'];assert pending.value.status==200;assert not errors,errors;page.screenshot(path=str(OUT/'mobile_no_provider.png'),full_page=True)
  summary={'scope':'Real desktop/mobile public UI with synthetic provider; zero external API or GPU calls','explicit_consent_before_post':True,'consent_reset_on_config_change':True,'spoofed_forwarded_headers_still_rate_limited':True,'error_no_source_or_key_echo':True,'failed_review_exports_stale':True,'own_artifacts_in_successful_export_by_design':True,'server_key_not_exported':True,'provider_absence_fails_closed':True,'labelled_demo_separate':True,'mobile_no_overflow':True,'browser_errors':errors,'model_calls':0};(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary));browser.close()
finally:
 for server in servers:server.terminate();server.wait(timeout=10)
 for log in logs:log.close()
 for path in OUT.glob('server_*.log'):
  text=path.read_text();assert 'PRIVATE_ERROR_SOURCE_SENTINEL' not in text and 'SERVER_ONLY_SENTINEL' not in text

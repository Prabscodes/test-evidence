import os,sys,json,time,subprocess,socket,threading,hashlib,urllib.request,datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tests.test_duplicate_json import DATA,wrapped
OUT=ROOT/'tests/results/duplicate_json_v1/browser';OUT.mkdir(exist_ok=False)
PRIVATE=ROOT/'submission-private/duplicate_json_v1';PRIVATE.mkdir(mode=0o700,exist_ok=False)
raw_duplicate=wrapped('"test_support":"gap","test_support":"checked"');raw_valid=wrapped('"test_support":"checked"');calls=[];current=[raw_valid]
class Handler(BaseHTTPRequestHandler):
 def do_POST(self):
  calls.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))));body=json.dumps({'choices':[{'message':{'content':current[0]}}]}).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
stub=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=stub.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{stub.server_port}'
with socket.socket() as sock:sock.bind(('127.0.0.1',8766))
log=(OUT/'server.log').open('w');env=dict(os.environ,TE_PROVIDER='openai-compatible',TE_API_BASE=base,TE_ALLOW_REMOTE='1',TE_MODEL='synthetic-parser-contract',TE_TIMEOUT_SECONDS='30');env.pop('TE_API_KEY',None)
server=subprocess.Popen([str(ROOT/'.venv/bin/python'),'-m','uvicorn','app:app','--host','127.0.0.1','--port','8766'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
try:
 # Verify a worker owned by the existing user manager, independent of tool-shell group.
 spec=PRIVATE/'request.json';spec.write_text(json.dumps({'url':base+'/synthetic','body':{'synthetic':'transport test only'},'timeout_seconds':5}));spec.chmod(0o600)
 unit='test-evidence-journal-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')
 manager_env=dict(os.environ,XDG_RUNTIME_DIR=f'/run/user/{os.getuid()}',DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{os.getuid()}/bus')
 result=subprocess.run(['systemd-run','--user','--collect','--unit='+unit,'--property=RuntimeMaxSec=20','--property=WorkingDirectory='+str(ROOT),str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/durable_request.py'),str(spec),str(PRIVATE/'attempt')],env=manager_env,capture_output=True,text=True,timeout=10)
 (PRIVATE/'launch.json').write_text(json.dumps({'unit':unit,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr},indent=2));assert result.returncode==0,result.stderr
 for _ in range(100):
  try:
   receipt=json.loads((PRIVATE/'attempt/state.json').read_text())
   if receipt['status']=='response_saved':break
  except FileNotFoundError:pass
  time.sleep(.1)
 else:raise AssertionError('Durable worker did not complete')
 assert receipt['parent_pid']!=os.getpid() and receipt['session_id']!=os.getsid(0)
 assert (PRIVATE/'attempt/response.body').is_file()
 probe=subprocess.run(['systemctl','--user','is-active',unit],env=manager_env,capture_output=True,text=True);assert probe.stdout.strip() in ['inactive','failed','unknown'],probe.stdout
 (OUT/'durable_worker_summary.json').write_text(json.dumps({'scope':'Synthetic loopback transport; no model call','launcher_returned_before_completion':True,'worker_parent_is_user_manager':True,'worker_session_independent':True,'durable_response_saved':True,'unit_terminal_state':probe.stdout.strip(),'model_calls':0},indent=2)+'\n')
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for _ in range(100):
  try:
   with opener.open('http://127.0.0.1:8766/api/status',timeout=1):break
  except OSError:time.sleep(.1)
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True);page=browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True);page.set_default_timeout(15000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8766');page.wait_for_load_state('networkidle')
  for key in ['requirement','source_before','source_after','tests_before','tests_after']:page.fill('#'+key,DATA[key])
  page.select_option('#mode','llm')
  def review(button):
   with page.expect_response(lambda r:r.url.endswith('/api/analyze') and r.request.method=='POST') as r:page.click('#'+button)
   assert r.value.status==200;data=r.value.json();page.wait_for_function('() => !document.getElementById("analyze").disabled');return data
  valid=review('analyze');assert valid['obligations'][0]['status']=='supported'
  current[0]=raw_duplicate;invalid=review('analyze');assert invalid['obligations'][0]['status']=='unresolved';assert 'duplicate' in page.locator('#warnings').inner_text().lower()
  page.locator('#raw-response').evaluate('(e) => e.parentElement.open=true');assert page.locator('#raw-response').inner_text()==raw_duplicate
  with page.expect_download() as d:page.click('#export-json')
  d.value.save_as(OUT/'rejected_export.json');export=json.loads((OUT/'rejected_export.json').read_text());assert export==invalid and export['provider']['raw_response']==raw_duplicate
  assert export['provider']['raw_response_sha256']==hashlib.sha256(raw_duplicate.encode()).hexdigest()
  with page.expect_download() as d:page.click('#export-md')
  d.value.save_as(OUT/'rejected_export.md');assert 'unresolved' in (OUT/'rejected_export.md').read_text()
  page.screenshot(path=str(OUT/'desktop_duplicate.png'),full_page=True);page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(OUT/'mobile_duplicate.png'),full_page=True)
  page.fill('#clarification','Keep the explicit expected value.');assert page.locator('#export-json').is_disabled();refined=review('refine');assert refined['obligations'][0]['status']=='unresolved' and refined['prompt_provenance']['previous_analysis_supplied']
  assert not errors,errors;browser.close()
 summary={'scope':'Real desktop/mobile browser and real app/provider HTTP path with synthetic model responses; no LLM generation or accuracy claim','valid_then_duplicate_becomes_unresolved':True,'duplicate_warning_visible':True,'raw_exact_and_hashed':True,'json_markdown_exports':True,'refinement_and_stale_exports':True,'mobile_no_overflow':True,'browser_errors':errors,'synthetic_provider_posts':len(calls),'model_calls':0}
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
finally:
 server.terminate();server.wait(timeout=10);log.close();stub.shutdown();stub.server_close();thread.join()

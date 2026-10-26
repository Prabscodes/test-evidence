"""Public safety regression for routed UI, with explicit synthetic provider only."""
import argparse,json,os,socket,subprocess,sys,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--app-python',required=True);parser.add_argument('--out',required=True);args=parser.parse_args();ROOT=Path(args.root);sys.path.insert(0,str(ROOT));from tests.test_duplicate_json import DATA
OUT=Path(args.out);OUT.mkdir(parents=True,exist_ok=True);servers=[];logs=[]
code='''import sys,uvicorn
sys.path.insert(0,sys.argv[1]);import analysis
from tests.test_duplicate_json import wrapped
from errors import ProviderFailure
def fake(data):
 if data.get('clarification')=='simulate provider error':raise ProviderFailure('http_failure')
 return wrapped('"test_support":"checked"'),{'actual_inference':False,'backend':'synthetic-workflow-QA','model':'synthetic-not-a-model'}
analysis.provider.infer=fake
uvicorn.run('app:app',host='127.0.0.1',port=int(sys.argv[2]),access_log=False,proxy_headers=False)
'''
try:
    for port,ready in [(18771,True),(18772,False)]:
        with socket.socket() as s:s.bind(('127.0.0.1',port))
        env=dict(os.environ,TE_PUBLIC='1',TE_PROVIDER='openai-compatible',TE_API_BASE='https://provider.example/v1',TE_API_KEY='SERVER_ONLY_SENTINEL' if ready else '',TE_ALLOW_REMOTE='1',TE_TIMEOUT_SECONDS='90',TE_PUBLIC_PROVIDER_NAME='Synthetic QA provider',TE_PUBLIC_PROVIDER_POLICY_URL='https://provider.example/privacy')
        log=(OUT/f'server-{port}.log').open('w');logs.append(log);servers.append(subprocess.Popen([args.app_python,'-c',code,str(ROOT),str(port)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT))
    op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for port in [18771,18772]:
        for _ in range(100):
            try:
                with op.open(f'http://127.0.0.1:{port}/api/status',timeout=1):break
            except OSError:time.sleep(.1)
        else:raise RuntimeError('Isolated synthetic app not ready')
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True);page=browser.new_page(viewport={'width':1440,'height':1000});page.set_default_timeout(10000);errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.headers) if r.method=='POST' and r.url.endswith('/api/analyze') else None)
        page.goto('http://127.0.0.1:18771');page.wait_for_load_state('networkidle');page.click('#own-change');assert page.locator('#provider-privacy').is_visible()
        page.fill('#requirement',DATA['requirement'])
        for key in ['source_before','source_after']:page.fill('#'+key,DATA[key])
        page.click('#tests-tab')
        for key in ['tests_before','tests_after']:page.fill('#'+key,DATA[key])
        page.select_option('#mode','llm');assert page.locator('#analyze').is_disabled();assert not posts
        page.check('#provider-consent');assert page.locator('#analyze').is_enabled()
        with page.expect_response(lambda r:r.url.endswith('/api/analyze')) as response:page.click('#analyze')
        assert response.value.status==200;page.wait_for_function('() => !document.getElementById("refine").disabled');assert page.locator('#review-view').is_visible() and posts[0].get('x-provider-consent')
        page.locator('#export-tools summary').click()
        with page.expect_download() as d:page.click('#export-json')
        d.value.save_as(OUT/'own-export.json');export=(OUT/'own-export.json').read_text();assert 'SERVER_ONLY_SENTINEL' not in export and json.loads(export)['artifacts']['source_after']==DATA['source_after']
        page.click('button[data-view="workspace"]');status=page.request.get('http://127.0.0.1:18771/api/status').json()
        page.route('**/api/status',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps({**status,'provider_consent_token':'changed-config'})))
        page.click('#check-status');page.wait_for_function('() => !document.getElementById("provider-consent").checked');assert page.locator('#analyze').is_disabled();page.unroute('**/api/status');page.click('#check-status');page.wait_for_function('() => !document.getElementById("check-status").disabled');page.check('#provider-consent')
        page.click('button[data-view="review"]');page.fill('#clarification','simulate provider error');page.click('button[data-view="workspace"]');page.click('#source-tab');page.fill('#source_after','PRIVATE_ERROR_SOURCE_SENTINEL')
        with page.expect_response(lambda r:r.url.endswith('/api/analyze')) as response:page.click('#analyze')
        assert response.value.status==502;body=response.value.text();assert 'PRIVATE_ERROR_SOURCE_SENTINEL' not in body and 'SERVER_ONLY_SENTINEL' not in body
        page.wait_for_function('() => !document.getElementById("error").hidden');assert page.locator('#export-json').is_disabled();assert page.locator('#error').evaluate('(n)=>n===document.activeElement')
        rates=[page.request.post('http://127.0.0.1:18771/api/nonexistent',headers={'X-Forwarded-For':f'198.51.100.{n}','Forwarded':f'for=198.51.100.{n}'}).status for n in range(7)];assert 429 in rates
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto('http://127.0.0.1:18772');page.wait_for_load_state('networkidle');page.click('#load-example');page.select_option('#mode','llm');assert page.locator('#analyze').is_disabled();assert 'live inference unavailable' in page.locator('#public-service-note').inner_text();page.select_option('#mode','demo')
        with page.expect_response(lambda r:r.url.endswith('/api/analyze')) as response:page.click('#analyze')
        assert response.value.status==200 and not response.value.json()['provider']['actual_inference'];assert not errors,errors
        result={'scope':'Actual routed public UI with synthetic provider; zero external API/GPU calls','consent_before_post':True,'consent_reset_across_navigation':True,'source_and_key_safe_errors_exports_logs':True,'spoofed_forwarded_headers_rate_limited':True,'absence_fail_closed':True,'labelled_demo_separate':True,'mobile_no_overflow':True,'page_errors':errors};(OUT/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));browser.close()
finally:
    for server in servers:server.terminate();server.wait(timeout=10)
    for log in logs:log.close()
    for path in OUT.glob('server-*.log'):
        text=path.read_text();assert 'SERVER_ONLY_SENTINEL' not in text and 'PRIVATE_ERROR_SOURCE_SENTINEL' not in text

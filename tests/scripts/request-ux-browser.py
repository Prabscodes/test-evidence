"""Real browser request lifecycle QA with explicitly simulated slow/error transport.
No model calls; starts only an isolated labelled-demo app on loopback 8766.
"""
import json,os,socket,subprocess,sys,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'tests/results/request_ux_v1/browser_mock';OUT.mkdir(exist_ok=False)
with socket.socket() as s:s.bind(('127.0.0.1',8766))
env=dict(os.environ,TE_PROVIDER='none');env.pop('TE_API_KEY',None)
log=(OUT/'server.log').open('w');server=subprocess.Popen([str(ROOT/'.venv/bin/python'),'-m','uvicorn','app:app','--host','127.0.0.1','--port','8766'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
try:
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for _ in range(80):
        try:
            with opener.open('http://127.0.0.1:8766/api/samples',timeout=1) as resp:samples=json.load(resp)['samples']
            break
        except OSError:time.sleep(.1)
    else:raise RuntimeError('Isolated app unavailable')
    payload={k:samples[0][k] for k in ['requirement','source_before','source_after','tests_before','tests_after']};payload['mode']='demo'
    req=urllib.request.Request('http://127.0.0.1:8766/api/analyze',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with opener.open(req,timeout=10) as resp:demo=json.load(resp)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True);page=browser.new_page(viewport={'width':1440,'height':1000});page.set_default_timeout(15000)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)));pending=[];posts=[]
        def intercept(route):posts.append(route.request.post_data_json);pending.append(route)
        page.route('**/api/analyze',intercept)
        page.goto('http://127.0.0.1:8766');page.wait_for_load_state('networkidle');page.select_option('#samples',samples[0]['id']);page.select_option('#mode','llm')
        page.click('#analyze');page.wait_for_function('() => document.getElementById("elapsed").textContent.startsWith("1s") || parseInt(document.getElementById("elapsed").textContent)>1')
        assert 'active' in page.locator('#progress').inner_text();assert '%' not in page.locator('.request-state').inner_text()
        assert page.locator('#analyze').is_disabled() and page.locator('#refine').is_disabled()
        page.evaluate('document.getElementById("analyze").dispatchEvent(new Event("click"))');assert len(posts)==1
        page.locator('.request-state').screenshot(path=str(OUT/'desktop_waiting.png'))
        page.set_viewport_size({'width':390,'height':844});page.locator('.request-state').screenshot(path=str(OUT/'mobile_waiting.png'))
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        pending.pop().fulfill(status=200,content_type='application/json',body=json.dumps(demo));page.wait_for_function('() => !document.getElementById("analyze").disabled')
        assert not page.locator('#export-json').is_disabled();assert 'no LLM' in page.locator('#judgment-heading').inner_text()
        page.click('#analyze');page.wait_for_function('() => document.getElementById("analyze").disabled')
        # Browser transport cancellation is simulated. No app/model cancellation is claimed.
        while not pending:page.wait_for_timeout(10)
        pending.pop().abort('failed');page.wait_for_function('() => !document.getElementById("error").hidden')
        assert 'may still' in page.locator('#error').inner_text();assert page.locator('#export-json').is_disabled();assert page.locator('#analyze').is_disabled()
        count=len(posts);page.wait_for_timeout(1100);assert len(posts)==count
        page.locator('.request-state').screenshot(path=str(OUT/'mobile_interrupted.png'))
        page.click('#check-status');page.wait_for_function('() => !document.getElementById("analyze").disabled');assert len(posts)==count
        # A provider timeout preserves old output as stale and requires a manual status check.
        page.click('#analyze')
        while not pending:page.wait_for_timeout(10)
        message='Model request timed out. The provider may still be finishing; check its status before manually starting another review. No conclusion was accepted.'
        pending.pop().fulfill(status=504,content_type='application/json',body=json.dumps({'detail':message,'error_code':'timeout'}))
        page.wait_for_function('() => document.getElementById("error").textContent.includes("timed out")')
        assert page.locator('#export-json').is_disabled();assert page.locator('#analyze').is_disabled()
        page.click('#check-status');page.wait_for_function('() => !document.getElementById("analyze").disabled')
        # A response cannot overwrite inputs changed while the request was in flight.
        page.click('#analyze')
        while not pending:page.wait_for_timeout(10)
        page.evaluate('() => {const n=document.getElementById("source_after");n.value+="\\n# edited";n.dispatchEvent(new Event("input"));}')
        pending.pop().fulfill(status=200,content_type='application/json',body=json.dumps(demo));page.wait_for_function('() => !document.getElementById("analyze").disabled')
        assert 'Response discarded' in page.locator('#error').inner_text();assert page.locator('#export-json').is_disabled()
        # On a new page the app's running state blocks another POST. This status is mocked.
        state={'configured':True,'analysis_running':True,'analysis_elapsed_seconds':42}
        page.route('**/api/status',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps(state)))
        page.reload();page.wait_for_function('() => document.getElementById("progress").textContent.includes("still active")')
        assert page.locator('#analyze').is_disabled();count=len(posts)
        page.evaluate('document.getElementById("analyze").dispatchEvent(new Event("click"))');assert len(posts)==count
        page.locator('.request-state').screenshot(path=str(OUT/'mobile_reloaded_active.png'))
        state['analysis_running']=False;state['analysis_elapsed_seconds']=None
        page.click('#check-status');page.wait_for_function('() => !document.getElementById("analyze").disabled')
        assert not errors,errors
        result={'scope':'Real browser UX with simulated model transport; not inference or semantic accuracy evidence','elapsed_without_percentages':True,'duplicate_click_one_post':True,'transport_cancel_no_auto_retry':True,'status_recovery_get_only':True,'failed_review_old_exports_blocked':True,'provider_timeout_actionable':True,'late_edited_response_discarded':True,'reload_detects_running_app':True,'desktop_mobile_no_overflow':True,'post_count':len(posts),'browser_errors':errors,'browser_version':browser.version}
        (OUT/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));browser.close()
finally:
    server.terminate();server.wait(timeout=10);log.close()

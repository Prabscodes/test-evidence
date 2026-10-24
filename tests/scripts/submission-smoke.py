"""Bounded real-browser demo QA; no model calls, uploads never execute.
Uses an existing Playwright/browser installation. Starts only its own loopback app.
"""
import argparse,json,os,socket,subprocess,sys,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args()
OUT=Path(args.output).resolve();OUT.mkdir(parents=True,exist_ok=False)
with socket.socket() as sock:
    try:sock.bind(('127.0.0.1',8766))
    except OSError:raise SystemExit('Port 8766 occupied; no process was stopped.')
env=dict(os.environ,TE_PROVIDER='none');env.pop('TE_API_KEY',None)
log=(OUT/'server.log').open('w')
server=subprocess.Popen([os.getenv('TE_APP_PYTHON',sys.executable),'-m','uvicorn','app:app','--host','127.0.0.1','--port','8766'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
try:
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for _ in range(80):
        if server.poll() is not None:raise RuntimeError('Demo app failed to start; inspect server.log')
        try:
            with opener.open('http://127.0.0.1:8766/api/status',timeout=1) as resp:status=json.load(resp)
            break
        except OSError:time.sleep(.1)
    else:raise RuntimeError('Demo app did not become ready')
    assert status['backend']=='none' and not status['configured']
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/google-chrome'),headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
        page.set_default_timeout(15000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8766');page.wait_for_load_state('networkidle')
        def review(button='analyze'):
            with page.expect_response(lambda resp:resp.url.endswith('/api/analyze') and resp.request.method=='POST') as response:page.click('#'+button)
            resp=response.value;data=resp.json();assert resp.status==200,data
            page.wait_for_function('() => !document.getElementById("analyze").disabled')
            assert not data['provider']['actual_inference'];return data
        demos=[]
        for sample in ['missing_regression','legitimate_refactor','missing_spec','supported_boundary']:
            page.select_option('#samples',sample);data=review()
            demos.append({'sample':sample,'summary':page.locator('#summary').inner_text()})
        citation=page.locator('.citation').first;expected=citation.locator('pre').inner_text();citation.locator('button').click()
        selected=page.evaluate('document.activeElement.value.substring(document.activeElement.selectionStart,document.activeElement.selectionEnd)')
        assert selected==expected
        for button,filename in [('export-json','review.json'),('export-md','review.md')]:
            with page.expect_download() as download:page.click('#'+button)
            download.value.save_as(OUT/filename)
        page.fill('#clarification','Explicit clarification for stale-state check')
        assert page.locator('#export-json').is_disabled() and page.locator('#export-md').is_disabled()
        refined=review('refine');assert refined['artifacts']['clarification']=='Explicit clarification for stale-state check'
        assert refined['prompt_provenance']['previous_analysis_supplied']
        plain=review();assert plain['artifacts']['clarification']==refined['artifacts']['clarification']
        assert not plain['prompt_provenance']['previous_analysis_supplied']
        page.select_option('#samples','missing_regression')
        upload='raise RuntimeError("UPLOADED_CODE_MUST_NOT_EXECUTE")'+chr(10)
        page.locator('input[data-target="source_after"]').set_input_files({'name':'untrusted.py','mimeType':'text/plain','buffer':upload.encode()})
        page.wait_for_function('() => document.getElementById("source_after").value.startsWith("raise RuntimeError")')
        assert review()['artifacts']['source_after']==upload
        with page.expect_response(lambda resp:'/api/fixtures/' in resp.url) as execution_response:page.click('#run-fixture')
        execution=execution_response.value.json();assert execution['baseline_valid']
        page.wait_for_selector('#export-execution')
        with page.expect_download() as download:page.click('#export-execution')
        download.value.save_as(OUT/'execution.json')
        assert json.loads((OUT/'execution.json').read_text())==execution
        assert page.locator('#source_after').input_value()==upload
        assert any(x['outcome']=='assertion_failure' for x in execution['results'])
        page.locator('details').first.locator('summary').click();page.click('#prompts-button')
        page.wait_for_function('() => document.getElementById("prompts").textContent.includes("Persona")')
        page.screenshot(path=str(OUT/'desktop.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(OUT/'mobile.png'),full_page=True)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth');assert not errors,errors
        result={'scope':'Real browser with labelled demo only; no model-quality claim','demos':demos,'clarification_both_buttons':True,'refine_prior_context_only':True,'exact_citation_selection':True,'stale_exports_blocked':True,'ast_upload_and_immutable_execution':True,'separate_execution_export':True,'json_markdown_exports':True,'prompt_inspection':True,'mobile_no_overflow':True,'browser_errors':errors,'browser_version':browser.version}
        (OUT/'summary.json').write_text(json.dumps(result,indent=2)+chr(10));print(json.dumps(result));browser.close()
finally:
    server.terminate()
    try:server.wait(timeout=10)
    except subprocess.TimeoutExpired:server.kill();server.wait(timeout=5)
    log.close()

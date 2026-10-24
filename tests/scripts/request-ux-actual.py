"""One genuine Qwen development-example review; no frozen-case scoring or retries."""
import json,subprocess,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'tests/results/request_ux_v1/browser_actual';OUT.mkdir(exist_ok=False)
free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip())
if free<6000:raise SystemExit('GPU headroom below conservative 6000MiB; no model request sent')
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True);page=browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True);page.set_default_timeout(360000)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)));posts=[]
    page.on('request',lambda req:posts.append(req.post_data_json) if req.method=='POST' and req.url.endswith('/api/analyze') else None)
    page.goto('http://127.0.0.1:8765');page.wait_for_load_state('networkidle');page.select_option('#samples','missing_regression');page.select_option('#mode','llm')
    with page.expect_response(lambda resp:resp.url.endswith('/api/analyze') and resp.request.method=='POST') as pending:
        page.click('#analyze')
        page.wait_for_function('() => parseInt(document.getElementById("elapsed").textContent)>=1')
        assert page.locator('#analyze').is_disabled();assert '%' not in page.locator('.request-state').inner_text()
        page.locator('.request-state').screenshot(path=str(OUT/'desktop_waiting.png'))
        with opener.open('http://127.0.0.1:8765/api/status',timeout=5) as resp:active=json.load(resp)
        (OUT/'active_status.json').write_text(json.dumps(active,indent=2));assert active['analysis_running']
        page.set_viewport_size({'width':390,'height':844});page.locator('.request-state').screenshot(path=str(OUT/'mobile_waiting.png'))
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.set_viewport_size({'width':1440,'height':1000})
        print('Genuine Qwen request active; elapsed counter and server-running status verified on desktop/mobile.',flush=True)
    response=pending.value;result=response.json();(OUT/'actual_result.json').write_text(json.dumps({'scope':'Single genuine development-example UI check; no held-out claim or tuning','http_status':response.status,'request':posts[0],'response':result},indent=2)+'\n')
    assert response.status==200,result;page.wait_for_function('() => !document.getElementById("analyze").disabled')
    assert result['provider']['actual_inference'];assert result['provider']['model']=='te-qwen35-4b-bf16'
    assert 'Model judgment' in page.locator('#judgment-heading').inner_text();assert 'Actual model' in page.locator('#review-meta').inner_text()
    assert 'Static inspection' in page.locator('#observations').locator('..').inner_text()
    assert page.locator('#raw-response').text_content()==result['provider']['raw_response']
    with page.expect_download() as download:page.click('#export-json')
    download.value.save_as(OUT/'review_export.json');assert json.loads((OUT/'review_export.json').read_text())['analysis_id']==result['analysis_id']
    page.screenshot(path=str(OUT/'desktop_result.png'),full_page=True);page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(OUT/'mobile_result.png'),full_page=True)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');assert not errors,errors;assert len(posts)==1
    summary={'scope':'One actual model development example; unchanged model/prompt/settings; not frozen evaluation','actual_inference':True,'provider_elapsed_seconds':result['provider']['elapsed_seconds'],'browser_wait':page.locator('#elapsed').inner_text(),'elapsed_desktop_mobile':True,'app_running_status_verified':True,'model_static_execution_labels_distinct':True,'raw_output_and_export_match':True,'mobile_no_overflow':True,'post_count':len(posts),'browser_errors':errors,'browser_version':browser.version,'gpu_free_mib_before':free}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True);browser.close()

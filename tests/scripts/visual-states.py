import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--out',required=True);args=p.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True)
    page=browser.new_page(viewport={'width':390,'height':844});external=[];pending=[]
    page.on('request',lambda r:external.append(r.url) if not r.url.startswith((args.url,'data:','blob:')) else None)
    page.route('**/api/analyze',lambda route:pending.append(route))
    page.goto(args.url);page.wait_for_load_state('networkidle');page.click('#load-example');page.select_option('#mode','llm');page.click('#analyze')
    page.wait_for_timeout(1200);assert len(pending)==1
    page.locator('.request-state').screenshot(path=str(out/'mobile-loading.png'))
    assert '%' not in page.locator('.request-state').inner_text()
    pending.pop().fulfill(status=503,content_type='application/json',body=json.dumps({'detail':'Model service is unavailable. Check that the configured server is running. No conclusion was accepted; no automatic retry was sent.'}))
    page.wait_for_function('() => !document.getElementById("error").hidden')
    page.locator('.request-state').screenshot(path=str(out/'mobile-error.png'))
    assert page.locator('#error').evaluate('(n)=>n===document.activeElement')
    assert page.locator('#analyze').is_disabled()
    assert not external,external
    page.emulate_media(reduced_motion='reduce')
    assert page.locator('#analyze').evaluate('(n)=>getComputedStyle(n).transitionDuration')=='0s'
    ids=page.locator('[id]').evaluate_all('(ns)=>ns.map(n=>n.id)');assert len(ids)==len(set(ids))
    result={'scope':'Explicitly simulated slow/unavailable model transport, not live inference','external_asset_requests':external,'elapsed_without_percentages':True,'error_focus_no_retry':True,'reduced_motion_no_transition':True,'unique_html_ids':True}
    (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));browser.close()

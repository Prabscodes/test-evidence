"""Actual-browser UI acceptance checks; deterministic demo and explicit mocked transport only."""
import argparse,json,re
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:18766');parser.add_argument('--out',default='/tmp/test-evidence-uiux-browser');args=parser.parse_args()
out=Path(args.out);out.mkdir(parents=True,exist_ok=True)

def luminance(rgb):
    values=[v/255 for v in rgb]
    values=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
    return .2126*values[0]+.7152*values[1]+.0722*values[2]

def contrast(fg,bg):
    a,b=sorted([luminance(fg),luminance(bg)])
    return (b+.05)/(a+.05)

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000});page.set_default_timeout(10000)
    errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
    page.goto(args.url);page.wait_for_load_state('networkidle')
    assert page.locator('#load-example').count()==1,'Missing guided example action'
    assert page.locator('.workflow-nav a').nth(2).get_attribute('href')=='#results-panel','Empty navigation must not point to hidden clarification'
    assert page.locator('#refine-feedback').get_attribute('aria-live')=='off','Do not announce every elapsed second to screen readers'
    page.keyboard.press('Tab');assert page.locator('.skip-link').evaluate('(n)=>n===document.activeElement')
    page.keyboard.press('Enter');assert page.locator('#review-workspace').evaluate('(n)=>n===document.activeElement')
    page.click('#load-example');assert page.locator('#requirement').input_value()
    assert page.locator('#requirement').evaluate('(n)=>n===document.activeElement')
    assert len(posts)==0,'Loading inputs must never send a review'
    assert '5 of 5' in page.locator('#input-summary').inner_text()
    for field in ['requirement','source_before','source_after','tests_before','tests_after','clarification']:
        assert page.locator('#'+field).get_attribute('aria-describedby'),field
    names=page.locator('input[type=file]').evaluate_all('(ns)=>ns.map(n=>n.getAttribute("aria-label"))');assert all(names) and len(set(names))==5
    assert 'not verified' in page.locator('#connection').inner_text() or 'No live provider' in page.locator('#connection').inner_text()
    page.click('#analyze');page.wait_for_selector('#report',state='visible')
    assert page.locator('#judgment-heading').evaluate('(n)=>n===document.activeElement'),'Result focus should leave the submitted controls'
    assert page.locator('#result-mode').inner_text()=='DETERMINISTIC DEMO · NO LLM'
    assert 'potentially missing' in page.locator('#review-next-step').inner_text().lower()
    assert page.locator('#results-panel').get_attribute('aria-busy')=='false'
    samples=page.locator('.intro>p,.hint,.field-label,.citation button,.status,#result-mode,h1 span,.input-summary,#load-example').evaluate_all("""ns=>ns.filter(n=>n.getClientRects().length).map(n=>{let style=getComputedStyle(n),p=n,bg;do{bg=getComputedStyle(p).backgroundColor;p=p.parentElement;}while(bg==='rgba(0, 0, 0, 0)'&&p);return {text:n.textContent.slice(0,70),color:style.color,background:bg,font:parseFloat(style.fontSize),weight:parseInt(style.fontWeight)||400};})""")
    contrast_results=[]
    for sample in samples:
        fg=[float(x) for x in re.findall(r'[0-9.]+',sample['color'])[:3]];bg=[float(x) for x in re.findall(r'[0-9.]+',sample['background'])[:3]]
        ratio=contrast(fg,bg);required=3 if sample['font']>=24 or (sample['font']>=18.66 and sample['weight']>=700) else 4.5
        assert ratio>=required,(sample,ratio,required)
        contrast_results.append({**sample,'ratio':round(ratio,3),'required':required})
    (out/'contrast.json').write_text(json.dumps(contrast_results,indent=2))
    page.screenshot(path=str(out/'after-desktop.png'),full_page=True)
    page.focus('#source_before');assert page.locator('#source_before').evaluate('(n)=>getComputedStyle(n).outlineWidth')=='3px'
    page.set_viewport_size({'width':390,'height':844});page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(out/'after-mobile-start.png'))
    page.locator('#judgment-heading').scroll_into_view_if_needed();page.screenshot(path=str(out/'after-mobile-review.png'));page.set_viewport_size({'width':1440,'height':1000})
    page.locator('.citation button').first.click();assert page.evaluate('document.activeElement.tagName')=='TEXTAREA'
    assert page.evaluate('document.activeElement.selectionEnd>document.activeElement.selectionStart')
    page.click('#go-clarify');assert page.locator('#clarification').evaluate('(n)=>n===document.activeElement')
    page.click('#refine');assert page.locator('#clarification').evaluate('(n)=>n===document.activeElement')
    assert 'Add a clarification' in page.locator('#error').inner_text()
    page.fill('#clarification','Age eighteen is included, as stated in the requirement.')
    assert page.locator('#export-json').is_disabled()
    page.click('#refine');page.wait_for_function('() => !document.getElementById("refine").disabled')
    assert page.locator('#judgment-heading').evaluate('(n)=>n===document.activeElement')
    assert not page.locator('#export-json').is_disabled()
    for button in ['#export-json','#export-md']:
        with page.expect_download() as info:page.click(button)
        download=info.value;download.save_as(str(out/download.suggested_filename))
    page.click('#run-fixture');page.wait_for_selector('#export-execution')
    assert 'immutable' in page.locator('#execution').inner_text().lower()
    with page.expect_download() as info:page.click('#export-execution')
    info.value.save_as(str(out/info.value.suggested_filename))
    page.fill('#source_after',page.locator('#source_after').input_value()+'\n# edited')
    assert page.locator('#export-json').is_disabled() and page.locator('#export-execution').count()==0
    page.locator('.citation button').first.click();assert 'Inputs changed' in page.locator('#error').inner_text()
    assert page.locator('#error').evaluate('(n)=>n===document.activeElement')
    layout=[]
    for width in [320,390,768,1440]:
        page.set_viewport_size({'width':width,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
        if width==390:page.screenshot(path=str(out/'after-mobile.png'),full_page=True)
        layout.append(width)
    page.set_viewport_size({'width':1440,'height':1000})
    page.evaluate('document.documentElement.style.zoom="2"');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.evaluate('document.documentElement.style.zoom="1"')
    # Transport below is deliberately simulated. It makes no LLM call.
    pending=[]
    page.route('**/api/analyze',lambda route:pending.append(route))
    page.click('#analyze');page.wait_for_function('() => document.getElementById("analyze").disabled')
    assert page.locator('#load-example').is_disabled()
    page.evaluate('document.getElementById("analyze").dispatchEvent(new Event("click"))');page.wait_for_timeout(1100)
    assert len(pending)==1 and '1s' in page.locator('#elapsed').inner_text()
    pending.pop().abort('failed');page.wait_for_function('() => !document.getElementById("error").hidden')
    assert page.locator('#analyze').is_disabled() and page.locator('#export-json').is_disabled()
    assert page.locator('#error').evaluate('(n)=>n===document.activeElement')
    count=len(posts);page.wait_for_timeout(1100);assert len(posts)==count
    page.click('#check-status');page.wait_for_function('() => !document.getElementById("analyze").disabled');assert len(posts)==count
    page.click('#analyze')
    while not pending:page.wait_for_timeout(10)
    pending.pop().fulfill(status=503,content_type='application/json',body=json.dumps({'detail':'Cannot reach the configured model server. Check that it is running; no conclusion was accepted.'}))
    page.wait_for_function('() => document.getElementById("error").textContent.includes("model server")');assert page.locator('#export-json').is_disabled()
    page.click('#check-status');page.wait_for_function('() => !document.getElementById("analyze").disabled')
    page.click('#analyze')
    while not pending:page.wait_for_timeout(10)
    page.evaluate('document.getElementById("source_after").dispatchEvent(new Event("input"))')
    pending.pop().fulfill(status=200,content_type='application/json',body=json.dumps({'mode':'demo','obligations':[],'questions':[]}))
    page.wait_for_function('() => document.getElementById("error").textContent.includes("Response discarded")');assert page.locator('#export-json').is_disabled()
    assert not errors,errors
    summary={'browser':browser.version,'actual_demo_review_refinement_export':True,'actual_allowlisted_fixture_export':True,'keyboard_skip_result_citation_clarification_error_focus':True,'guided_load_no_post':True,'unique_upload_labels_and_described_inputs':True,'mobile_widths_no_overflow':layout,'zoom_200_no_overflow':True,'simulated_transport_only':['slow','duplicate','interrupted','503','late stale response'],'no_auto_retries':True,'page_errors':errors,'live_inference_tested':False,'sampled_text_contrast_pass':len(contrast_results),'minimum_sampled_text_contrast':min(x['ratio'] for x in contrast_results)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary));browser.close()

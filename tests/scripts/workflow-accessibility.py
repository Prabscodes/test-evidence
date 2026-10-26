import argparse,json,re
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
def luminance(rgb):
    vals=[v/255 for v in rgb];vals=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals];return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]
def contrast(fg,bg):
    lo,hi=sorted([luminance(fg),luminance(bg)]);return (hi+.05)/(lo+.05)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True);page=browser.new_page(viewport={'width':1440,'height':1000});external=[];page.on('request',lambda r:external.append(r.url) if not r.url.startswith((a.url,'data:','blob:')) else None)
    page.goto(a.url);page.wait_for_load_state('networkidle');page.keyboard.press('Tab');assert page.locator('.skip-link').evaluate('(n)=>n===document.activeElement');page.keyboard.press('Enter');assert page.locator('#main-content').evaluate('(n)=>n===document.activeElement')
    page.click('#load-example');names=page.locator('input[type=file]').evaluate_all('(ns)=>ns.map(n=>n.getAttribute("aria-label"))');assert all(names) and len(set(names))==5
    for field in ['requirement','source_before','source_after','tests_before','tests_after','clarification']:assert page.locator('#'+field).get_attribute('aria-describedby')
    page.focus('#source_after');assert page.locator('#source_after').evaluate('(n)=>getComputedStyle(n).outlineWidth')=='3px'
    page.click('#analyze');page.wait_for_selector('#report',state='visible');ratios=[];targets=[]
    for view in ['start','workspace','review']:
        page.click('button[data-view="'+view+'"]')
        samples=page.locator('h1,h2,.hint,.field-label,.status,.evidence-limit,.finding-context,.mono-label,.choice-number,.primary:not(:disabled)').evaluate_all("""ns=>ns.filter(n=>n.getClientRects().length).map(n=>{let s=getComputedStyle(n),p=n,bg;do{bg=getComputedStyle(p).backgroundColor;p=p.parentElement;}while(bg==='rgba(0, 0, 0, 0)'&&p);return {text:n.textContent.slice(0,60),color:s.color,background:bg,font:parseFloat(s.fontSize),weight:parseInt(s.fontWeight)||400};})""")
        for sample in samples:
            fg=[float(x) for x in re.findall(r'[0-9.]+',sample['color'])[:3]];bg=[float(x) for x in re.findall(r'[0-9.]+',sample['background'])[:3]];ratio=contrast(fg,bg);required=3 if sample['font']>=24 or sample['font']>=18.66 and sample['weight']>=700 else 4.5;assert ratio>=required,(view,sample,ratio);ratios.append({**sample,'view':view,'ratio':round(ratio,3),'required':required})
        for rect in page.locator('button:visible,select:visible,summary:visible,.file-label:visible').evaluate_all('(ns)=>ns.map(n=>({name:(n.textContent||n.getAttribute("aria-label")||n.id).trim().slice(0,50),width:n.getBoundingClientRect().width,height:n.getBoundingClientRect().height}))'):
            assert rect['height']>=43.5 and rect['width']>=43.5,(view,rect);targets.append(rect)
        page.evaluate('document.documentElement.style.zoom="2"');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),view;page.evaluate('document.documentElement.style.zoom="1"')
    page.emulate_media(reduced_motion='reduce');assert page.locator('#refine').evaluate('(n)=>getComputedStyle(n).transitionDuration')=='0s'
    ids=page.locator('[id]').evaluate_all('(ns)=>ns.map(n=>n.id)');assert len(ids)==len(set(ids));assert not external,external
    # Fresh direct Review has no persisted draft/output and never POSTs.
    fresh=browser.new_page();posted=[];fresh.on('request',lambda r:posted.append(r.url) if r.method=='POST' else None);fresh.goto(a.url+'/#review');fresh.wait_for_load_state('networkidle');assert fresh.locator('#empty').is_visible() and not posted
    result={'scope':'Actual labelled-demo and browser accessibility checks; not full WCAG certification','skip_keyboard':True,'associated_input_help_and_unique_uploads':True,'three_pixel_focus':True,'sampled_text_count':len(ratios),'minimum_sampled_ratio':min(x['ratio'] for x in ratios),'controls_checked_44px':len(targets),'all_views_200_percent_css_zoom_no_overflow':True,'reduced_motion':True,'unique_ids':True,'external_requests':external,'fresh_direct_review_no_result_or_post':True}
    (out/'contrast.json').write_text(json.dumps(ratios,indent=2));(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));browser.close()

"""Structural navigation/state regression. Actual demo/fixture; simulated transport is labelled."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:18770');parser.add_argument('--out',default='/tmp/test-evidence-workflow');args=parser.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000});page.set_default_timeout(10000);errors=[];posts=[]
    page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.post_data_json) if r.method=='POST' and r.url.endswith('/api/analyze') else None)
    page.goto(args.url);page.wait_for_load_state('networkidle')
    assert page.locator('#start-view').count()==1,'Missing focused start view'
    assert page.locator('#start-view').is_visible() and not page.locator('#workspace-view').is_visible()
    page.screenshot(path=str(out/'desktop-start.png'))
    page.click('#own-change');page.fill('#requirement','Keep the threshold inclusive.')
    page.fill('#source_before','def eligible(age):\n    return age >= 18\n');page.fill('#source_after','def eligible(age):\n    return age > 18\n')
    # A delayed local file read must not overwrite newer typing in this draft.
    page.evaluate("""() => {const original=File.prototype.text;window.restoreFileRead=()=>File.prototype.text=original;File.prototype.text=function(){const file=this;return new Promise(resolve=>window.finishFileRead=()=>original.call(file).then(resolve));};}""")
    page.set_input_files('input[data-target="source_after"]',{'name':'draft.py','mimeType':'text/plain','buffer':b'REPLACEMENT_FROM_FILE'})
    manual='def eligible(age):\n    return age > 18  # newest edit\n';page.fill('#source_after',manual);page.evaluate('() => window.finishFileRead()')
    page.wait_for_timeout(100);assert page.locator('#source_after').input_value()==manual,'Delayed upload must not overwrite a newer edit'
    assert 'No input was replaced' in page.locator('#error').inner_text();page.evaluate('() => window.restoreFileRead()')
    page.click('#tests-tab');assert page.locator('#tests-tab').get_attribute('aria-selected')=='true'
    page.fill('#tests_before','assert eligible(18)\n');page.fill('#tests_after','assert eligible(19)\n')
    page.click('button[data-view="start"]');assert page.locator('#start-view').is_visible()
    page.click('#own-change');assert page.locator('#requirement').input_value()=='Keep the threshold inclusive.'
    assert page.locator('#tests-tab').get_attribute('aria-selected')=='true'
    page.go_back();assert page.locator('#start-view').is_visible();page.go_forward();assert page.locator('#workspace-view').is_visible()
    assert page.locator('#tests_after').input_value()=='assert eligible(19)\n'
    assert not posts,'Navigation/loading must not submit a review'
    page.click('button[data-view="start"]');page.once('dialog',lambda d:d.dismiss());page.click('#load-example');assert page.locator('#requirement').input_value()=='Keep the threshold inclusive.'
    page.once('dialog',lambda d:d.accept());page.click('#load-example');assert 'at least 18' in page.locator('#requirement').input_value()
    assert page.locator('#workspace-view').is_visible();page.click('#source-tab');page.keyboard.press('ArrowRight');assert page.locator('#tests-tab').get_attribute('aria-selected')=='true'
    page.keyboard.press('Home');assert page.locator('#source-tab').get_attribute('aria-selected')=='true'
    page.screenshot(path=str(out/'desktop-inputs.png'))
    page.click('#analyze');page.wait_for_selector('#report',state='visible')
    assert page.locator('#review-view').is_visible() and not page.locator('#workspace-view').is_visible()
    assert page.locator('#judgment-heading').evaluate('(n)=>n===document.activeElement')
    assert page.locator('.finding-button').count()>=1
    assert page.locator('.citation').first.evaluate('(n)=>n.tagName')=='DETAILS' and not page.locator('.citation').first.get_attribute('open')
    assert 'DETERMINISTIC DEMO' in page.locator('#result-mode').inner_text()
    page.screenshot(path=str(out/'desktop-review.png'))
    page.locator('.citation summary').first.click();page.locator('.citation button').first.click()
    assert page.locator('#workspace-view').is_visible();assert page.evaluate('document.activeElement.tagName')=='TEXTAREA'
    assert page.evaluate('document.activeElement.selectionEnd>document.activeElement.selectionStart')
    page.click('button[data-view="review"]');assert page.locator('#review-view').is_visible()
    assert not page.locator('#export-json').is_disabled()
    page.click('#go-clarify');assert page.locator('#clarification').evaluate('(n)=>n===document.activeElement')
    assert 'O1' in page.locator('#clarification-context').inner_text()
    page.fill('#clarification','The requirement explicitly includes age eighteen.');assert page.locator('#export-json').is_disabled()
    with page.expect_response(lambda r:r.url.endswith('/api/analyze')) as response:page.click('#refine')
    assert response.value.status==200
    page.wait_for_function('() => !document.getElementById("refine").disabled')
    assert len(posts)==2 and 'previous_analysis' in posts[1]
    page.locator('#export-tools summary').click()
    with page.expect_download() as d:page.click('#export-json')
    d.value.save_as(str(out/'review-export.json'))
    page.locator('#execution-tools summary').click();page.click('#run-fixture');page.wait_for_selector('#export-execution')
    with page.expect_download() as d:page.click('#export-execution')
    d.value.save_as(str(out/'execution-export.json'))
    # Existing safe response used to exercise two finding selections; no extra LLM call.
    original=json.loads((out/'review-export.json').read_text());second={**original['obligations'][0],'id':'O2','description':'Second UI regression finding'}
    two={**original,'obligations':[original['obligations'][0],second]};pending=[]
    page.route('**/api/analyze',lambda route:pending.append(route));page.click('button[data-view="workspace"]');page.click('#analyze')
    while not pending:page.wait_for_timeout(10)
    page.click('button[data-view="workspace"]');assert page.locator('#requirement').is_disabled()
    pending.pop().fulfill(status=200,content_type='application/json',body=json.dumps(two));page.wait_for_function('() => !document.getElementById("analyze").disabled')
    assert page.locator('#workspace-view').is_visible(),'Late success must not steal navigation/focus'
    page.click('button[data-view="review"]');page.locator('.finding-button').nth(1).click()
    assert page.locator('.evidence-card:visible').count()==1 and 'O2' in page.locator('#clarification-context').inner_text()
    page.click('button[data-view="workspace"]');page.click('button[data-view="review"]');assert page.locator('.finding-button').nth(1).get_attribute('aria-pressed')=='true'
    page.click('button[data-view="workspace"]');page.fill('#requirement',page.locator('#requirement').input_value()+' Confirmed.')
    page.click('button[data-view="review"]');assert page.locator('#export-json').is_disabled() and 'stale' in page.locator('#review-state').inner_text().lower()
    page.click('button[data-view="workspace"]');page.click('#analyze')
    while not pending:page.wait_for_timeout(10)
    page.evaluate('document.getElementById("analyze").dispatchEvent(new Event("click"))');assert len(pending)==1
    pending.pop().abort('failed');page.wait_for_function('() => !document.getElementById("error").hidden')
    assert page.locator('#analyze').is_disabled() and page.locator('#export-json').is_disabled() and page.locator('#samples').is_disabled()
    n=len(posts);page.click('button[data-view="workspace"]');page.click('#check-status');page.wait_for_function('() => !document.getElementById("analyze").disabled');assert len(posts)==n
    layout=[]
    for width in [320,390,768,1024,1440]:
        page.set_viewport_size({'width':width,'height':844})
        for view in ['start','workspace','review']:
            page.click('button[data-view="'+view+'"]');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,view)
            if width==390:
                page.screenshot(path=str(out/('mobile-'+view+'.png')))
                if view=='workspace':
                    page.click('#jump-tests');assert page.locator('#tests-tab').get_attribute('aria-selected')=='true';page.click('#jump-requirement');assert page.locator('#requirement').evaluate('(n)=>n===document.activeElement')
        layout.append(width)
    assert not errors,errors
    result={'actual_demo_review_refinement_export':True,'actual_allowlisted_fixture_export':True,'start_workspace_review_navigation':True,'draft_and_editor_preserved':True,'delayed_upload_cannot_overwrite_newer_edit':True,'browser_back_forward_preserved':True,'sample_replace_confirm_cancel_preserved':True,'keyboard_editor_tabs':True,'citation_opens_correct_editor_and_exact_selection':True,'finding_selection_and_context_preserved':True,'late_result_does_not_steal_navigation':True,'stale_exports_blocked_across_views':True,'simulated_multi_finding_and_interrupted_transport':True,'duplicate_no_auto_retry':True,'layout_widths_all_views_no_overflow':layout,'page_errors':errors,'live_inference':False,'browser':browser.version}
    (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));browser.close()

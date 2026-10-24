"""Two actual development/demo reviews; no retries, held-out claim or AI narration."""
import json,time,subprocess,hashlib,sys,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.durable_request import atomic
OUT=ROOT/'tests/results/qwen27_v1/browser_recovery';OUT.mkdir(exist_ok=False);start=time.monotonic();events=[]
def save(name,obj):atomic(OUT/name,(json.dumps(obj,indent=2)+'\n').encode())
def mark(name):events.append({'event':name,'seconds':round(time.monotonic()-start,3)})
free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip());assert free>=6000
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
with op.open('http://127.0.0.1:8765/api/status',timeout=5) as f:assert not json.load(f)['analysis_running']
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True);context=browser.new_context(viewport={'width':1440,'height':900},record_video_dir=str(OUT/'footage'),record_video_size={'width':1440,'height':900},accept_downloads=True);page=context.new_page();page.set_default_timeout(15000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));posts=[]
 page.on('request',lambda req:posts.append(req.post_data_json) if req.method=='POST' and req.url.endswith('/api/analyze') else None)
 try:
  page.goto('http://127.0.0.1:8765');page.wait_for_load_state('networkidle');mark('title_and_requirement');page.select_option('#samples','missing_regression');page.select_option('#mode','llm');page.wait_for_timeout(2500)
  def review(button,name):
   mark(name+'_start')
   with page.expect_response(lambda r:r.url.endswith('/api/analyze') and r.request.method=='POST',timeout=330000) as pending:page.click('#'+button)
   response=pending.value;data=response.json();save(name+'.json',{'http_status':response.status,'request':posts[-1],'response':data,'scope':'Actual local model development/demo workflow; not independent accuracy'});assert response.status==200,data
   page.wait_for_function('() => !document.getElementById("analyze").disabled');mark(name+'_complete');assert data['provider']['actual_inference'] and data['provider']['model']=='te-qwen35-27b-ct4';assert page.locator('#raw-response').text_content()==data['provider']['raw_response'];return data
  first=review('analyze','review');page.locator('#summary').scroll_into_view_if_needed();page.wait_for_timeout(2500)
  citation=page.locator('.citation').first;expected=citation.locator('pre').inner_text();citation.locator('button').click();selected=page.evaluate('document.activeElement.value.substring(document.activeElement.selectionStart,document.activeElement.selectionEnd)');assert selected==expected;mark('citation_highlight');page.wait_for_timeout(2000)
  for button,name in [('export-json','review_export.json'),('export-md','review_export.md')]:
   with page.expect_download() as d:page.click('#'+button)
   d.value.save_as(OUT/name)
  assert json.loads((OUT/'review_export.json').read_text())==first
  page.get_by_text('Inspect prompts & course patterns',exact=True).click();page.click('#prompts-button');page.wait_for_function('() => document.getElementById("prompts").textContent.includes("Persona")');mark('prompt_patterns');page.wait_for_timeout(2500)
  page.fill('#clarification','Eligibility includes age18 exactly; this expected boundary behavior is authoritative.');assert page.locator('#export-json').is_disabled();page.locator('#refine').scroll_into_view_if_needed();mark('clarification');page.wait_for_timeout(1500)
  second=review('refine','refinement');assert second['prompt_provenance']['previous_analysis_supplied'];assert 'age18' in second['artifacts']['clarification'];assert page.locator('#raw-response').text_content()==second['provider']['raw_response']
  page.locator('#summary').scroll_into_view_if_needed();page.wait_for_timeout(2500)
  with page.expect_download() as d:page.click('#export-json')
  d.value.save_as(OUT/'refinement_export.json');assert json.loads((OUT/'refinement_export.json').read_text())==second
  with page.expect_response(lambda r:'/api/fixtures/' in r.url) as pending:page.click('#run-fixture')
  execution=pending.value.json();save('execution.json',execution);assert execution['baseline_valid'];page.wait_for_selector('#export-execution');assert execution['uploaded_code_executed'] is False if 'uploaded_code_executed' in execution else True
  with page.expect_download() as d:page.click('#export-execution')
  d.value.save_as(OUT/'execution_export.json');assert json.loads((OUT/'execution_export.json').read_text())==execution;mark('separate_fixture_execution');page.locator('#execution').scroll_into_view_if_needed();page.wait_for_timeout(3000)
  page.screenshot(path=str(OUT/'desktop.png'),full_page=True);mark('end_recording');assert len(posts)==2 and not errors,errors
  summary={'scope':'Actual27B local UI workflow on reused demo/development artifacts; not independent accuracy','review_seconds':first['provider']['elapsed_seconds'],'refinement_seconds':second['provider']['elapsed_seconds'],'review_statuses':[o['status'] for o in first['obligations']],'refinement_statuses':[o['status'] for o in second['obligations']],'exact_citation_selection':True,'raw_hash_json_markdown_exports':True,'clarification_prior_context':True,'stale_export_disabled':True,'immutable_fixture_separate_export':True,'actual_model_post_count':len(posts),'browser_errors':errors,'gpu_free_mib_before':free,'footage':'Genuine browser capture, no generated narration; no wait speed-up applied to raw footage.'};save('summary.json',summary)
 finally:
  save('events.json',events);context.close();browser.close()
 # Mobile read-only layout check after recorded desktop requests are complete.
 browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True);page=browser.new_page(viewport={'width':390,'height':844});page.goto('http://127.0.0.1:8765');page.wait_for_load_state('networkidle');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(OUT/'mobile.png'),full_page=True);browser.close()
print('Actual model browser review/refinement/citations/exports and footage complete.',flush=True)

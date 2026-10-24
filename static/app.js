'use strict';
const $ = id => document.getElementById(id);
const fields = ['requirement', 'source_before', 'source_after', 'tests_before', 'tests_after'];
let samples = [], analysis = null, busy = false, stale = false, inputVersion = 0;
let publicState={public_mode:false,public_live_ready:false,provider_consent_token:""};
let serverRunning=false, needsStatusCheck=false, checkingStatus=false;
let actionStarted=null, serverStarted=null, elapsedTimer=null, lastWait=null;
function blocked() { return busy || serverRunning || needsStatusCheck; }
function mirrorFeedback() { $('refine-feedback').textContent=[$('progress').textContent,$('elapsed').textContent,$('error').hidden?'':$('error').textContent].filter(Boolean).join(' · '); }
function updateElapsed() {
 const started=actionStarted ?? (serverRunning?serverStarted:null);
 $('elapsed').textContent=started!==null?`${Math.floor(Math.max(0,Date.now()-started)/1000)}s elapsed · waiting for server`:lastWait!==null?`${lastWait}s browser wait`:'';
 mirrorFeedback();
}
function updateTimer() {
 if(busy || serverRunning) { if(elapsedTimer===null) elapsedTimer=setInterval(updateElapsed,1000); }
 else if(elapsedTimer!==null) { clearInterval(elapsedTimer); elapsedTimer=null; }
 updateElapsed();
}
function publicInferenceBlocked() { return publicState.public_mode && $('mode').value==='llm' && (!publicState.public_live_ready || !$('provider-consent')?.checked); }
function reviewHeaders() { const headers={'Content-Type':'application/json'};if(publicState.public_mode && $('mode').value==='llm' && $('provider-consent')?.checked) headers['X-Provider-Consent']=publicState.provider_consent_token;return headers; }
function showPublicStatus(state) {
 const changed=publicState.provider_consent_token!==state.provider_consent_token;publicState=state;
 const panel=$('provider-privacy');if(!panel)return;panel.hidden=!state.public_mode;if(!state.public_mode)return;
 if(changed)$('provider-consent').checked=false;
 $('public-service-note').textContent=state.public_live_ready?'Public prototype · configured external LLM':'Public labelled demo · live inference unavailable';
 $('provider-processing-note').textContent=state.public_live_ready?`LLM reviews send requirement, source, tests, clarification and previous review context to ${state.public_provider_name}. Review the provider policy and consent before sending.`:'No approved live provider is configured. Labelled demo is available; no automatic model or cloud fallback runs.';
 $('provider-consent-label').hidden=!state.public_live_ready;$('provider-policy').hidden=!state.public_live_ready;
 if(state.public_live_ready)$('provider-policy').href=state.public_provider_policy_url;
}
$('provider-consent')?.addEventListener('change',updateControls);
function updateControls() {
 $('analyze').disabled=blocked() || publicInferenceBlocked(); $('refine').disabled=blocked() || publicInferenceBlocked();
 $('run-fixture').disabled=busy || serverRunning || !$('samples').value;
 $('check-status').disabled=busy || checkingStatus;
 updateExports();
}
async function checkServerStatus() {
 if(checkingStatus) return;
 checkingStatus=true; updateControls();
 try {
  const state=await request('/api/status'); const config=state.provider || state;showPublicStatus(state);
  $('connection').textContent=config.configured?'Provider configured':'Local review · configure a provider for LLM mode';
  $('connection').title=JSON.stringify(config);
  if(!busy) {
   serverRunning=state.analysis_running===true || state.public_work_running===true; needsStatusCheck=false;
   serverStarted=serverRunning?Date.now()-1000*Math.max(0,Number(state.analysis_elapsed_seconds)||0):null;
   $('progress').textContent=serverRunning?'An app review is still active. Wait, then check status; no new review was sent.':'App is idle. A new review requires your explicit click.';
   $('status-note').textContent='App status does not prove model readiness or that a timed-out provider has stopped. Leaving this page does not guarantee cancellation. No automatic retries.';
  }
 } catch {
  needsStatusCheck=true; $('connection').textContent='App status unavailable';
  error('Cannot verify app status. Check that the local app is running, then use Check app status. No review was sent by this check.');
 } finally { checkingStatus=false; updateControls(); updateTimer(); }
}
$('check-status').addEventListener('click',checkServerStatus);
function text(value) { return typeof value === 'string' ? value : JSON.stringify(value, null, 2); }
function element(tag, value, className) { const node=document.createElement(tag); if(value !== undefined) node.textContent=text(value); if(className) node.className=className; return node; }
function error(message) { $('error').textContent=message; $('error').hidden=!message; mirrorFeedback(); }
async function request(path, options={}) {
 let response;
 try { response=await fetch(path, options); }
 catch {
  const err=new Error('Connection lost or request interrupted. The server may still be working. Inputs are preserved; check app status before explicitly starting another review. No automatic retry was sent.');
  err.uncertain=true; throw err;
 }
 let data;
 try { data=await response.json(); }
 catch {
  const err=new Error(`The app returned an unreadable response (${response.status}). Check its status before trying again; the provider may still be finishing. No conclusion was accepted.`);
  err.uncertain=true; throw err;
 }
 if(!response.ok) {
  const err=new Error(response.status===422?'Some review inputs are invalid or exceed their limits. Check the fields and shorten the excerpts.':typeof data.detail==='string'?data.detail:text(data.detail || data.error || data));
  err.status=response.status; throw err;
 }
 return data;
}
function updateExports() { $('export-json').disabled=busy || stale || !analysis; $('export-md').disabled=busy || stale || !analysis; }
function setBusy(value, message='') {
 if(value) { actionStarted=Date.now(); lastWait=null; $('progress').textContent=message; }
 else {
  if(actionStarted!==null) lastWait=Math.floor(Math.max(0,Date.now()-actionStarted)/1000);
  actionStarted=null;
  $('progress').textContent=serverRunning?'An app review is still active. Check status before another request.':needsStatusCheck?'Check app status before another review; no automatic retry was sent.':message;
 }
 busy=value;
 [...fields,'clarification','samples','mode'].forEach(id=>$(id).disabled=value);
 document.querySelectorAll('input[type=file]').forEach(input=>input.disabled=value);
 $('status-note').textContent='Elapsed time is a wait timer, not model progress. Closing this page does not guarantee cancellation. No automatic retries.';
 updateControls(); updateTimer();
}
function clearReport() { analysis=null; stale=false; $('report').hidden=true; $('empty').hidden=false; $('result-mode').textContent='INPUTS CHANGED'; $('execution').replaceChildren(); updateExports(); }
function markStale() { inputVersion++; $('execution').replaceChildren(); if(analysis) { stale=true; $('result-mode').textContent='STALE · INPUTS EDITED'; $('disclaimer').textContent='Inputs have changed since this report. Reanalyze before citation navigation or export.'; } updateExports(); }
[...fields,'clarification'].forEach(id => $(id).addEventListener('input',markStale));
$('samples').addEventListener('change', () => { inputVersion++; clearReport(); const sample=samples.find(item => item.id === $('samples').value); if(!sample) { $('run-fixture').disabled=true; return; } fields.forEach(id => $(id).value=sample[id] || ''); $('clarification').value=''; error(''); $('run-fixture').disabled=busy || serverRunning; });
document.querySelectorAll('input[type=file]').forEach(input => input.addEventListener('change', async () => { const file=input.files[0]; if(!file) return; if(file.size>80000) { error('Please use a small text file (80 KB maximum).'); input.value=''; return; } const content=await file.text(); if(busy) {input.value='';return;} if(content.length>$(input.dataset.target).maxLength) { error('This file exceeds the input character limit. Please select a smaller excerpt.'); input.value=''; return; } $(input.dataset.target).value=content; $(input.dataset.target).dispatchEvent(new Event('input')); error(''); input.value=''; }));
$('mode').addEventListener('change', () => { markStale(); $('mode-note').textContent=$('mode').value==='llm' ? 'Uses the server-configured provider. Your submitted requirement and code are sent to that provider. Credentials stay on the server.' : 'Demo mode uses deterministic rules. It does not count as a model analysis.'; updateControls(); });
function renderReport(result) { $('judgment-heading').textContent=result.mode==='llm'?'Model judgment · fallible':'Labelled demo judgment · no LLM'; $('review-meta').textContent=result.provider?.actual_inference?`Actual model: ${result.provider.model || 'configured provider'} · ${result.provider.elapsed_seconds ?? 'unknown'}s provider time · no uploaded code executed`:'Hand-authored demonstration judgment · no model call'; analysis=result; stale=false; updateExports(); $('empty').hidden=true; $('report').hidden=false; $('result-mode').textContent=result.mode==='llm' ? 'LLM INFERENCE' : 'DETERMINISTIC DEMO · NO LLM'; $('disclaimer').textContent=result.disclaimer || 'Evidence of test support is not a proof of software correctness.'; $('warnings').textContent=(result.warnings || []).map(text).join(' · '); $('provider-details').textContent=JSON.stringify(result.provider || {},null,2); $('raw-response').textContent=result.provider?.raw_response || result.raw_response || ''; const obligations=result.obligations || []; $('summary').replaceChildren(); ['supported','potentially_missing','unresolved'].forEach(status => $('summary').append(element('span', `${obligations.filter(o=>o.status===status).length} ${status.replaceAll('_',' ')}`, status))); $('obligations').replaceChildren(); obligations.forEach(obligation => { const card=element('article',undefined,'evidence-card'); const head=element('div',undefined,'card-header'); head.append(element('strong',obligation.id || 'Obligation'),element('span',(obligation.status || 'unresolved').replaceAll('_',' '),'status '+(['supported','potentially_missing','unresolved'].includes(obligation.status)?obligation.status:'unresolved'))); card.append(head,element('div',obligation.origin || (result.mode==='llm'?'LLM inference':'Deterministic demo'),'origin'),element('h3',obligation.description),element('p',obligation.rationale)); (obligation.evidence || []).forEach(evidence => { const citation=element('div',undefined,'citation'), link=element('button',`${evidence.artifact}:${evidence.line_start}–${evidence.line_end}`); link.type='button'; link.title='Highlight these lines in the input'; link.addEventListener('click',()=>{ if(stale){error('Inputs changed. Reanalyze to navigate citations.');return;} const target=$(evidence.artifact); if(!target || ![...fields,'clarification'].includes(evidence.artifact)) return; const lines=target.value.split('\n'); const start=lines.slice(0,Math.max(0,evidence.line_start-1)).join('\n').length+(evidence.line_start>1?1:0); const end=lines.slice(0,evidence.line_end).join('\n').length; target.focus(); target.setSelectionRange(start,end); target.scrollIntoView({behavior:'smooth',block:'center'}); }); citation.append(link,element('pre',evidence.quote || '')); card.append(citation); }); $('obligations').append(card); }); $('observations').replaceChildren(); (result.observations || []).forEach(observation => { const row=element('div',undefined,'observation'); row.append(element('strong',observation.kind || 'Observation'),element('span',observation.detail || observation)); $('observations').append(row); }); $('questions').replaceChildren(); (result.questions || []).forEach(question => $('questions').append(element('li',typeof question==='string'?question:question.question || question))); $('questions-section').hidden=!(result.questions || []).length; }
async function analyze(refine=false) {
 if(blocked()) return;
 error('');
 if(publicInferenceBlocked()) { error('Live public inference is unavailable or provider-processing consent is required. Check app status and the provider notice.');return; }
 if(refine && !$('clarification').value.trim()) { error('Add a clarification or answer before refining.'); $('clarification').focus(); return; }
 const requestVersion=inputVersion;
 const body=Object.fromEntries(fields.map(id=>[id,$(id).value])); body.mode=$('mode').value; body.clarification=$('clarification').value;
 if(refine) body.previous_analysis={obligations:analysis?.obligations || [],questions:analysis?.questions || []};
 if(analysis) { stale=true; $('result-mode').textContent='PREVIOUS REVIEW · NEW REQUEST PENDING'; $('disclaimer').textContent='A new request is pending. This previous review is not the current result; exports remain disabled until a new review succeeds.'; }
 setBusy(true,body.mode==='llm'?(refine?'Model refinement request active · waiting for server…':'Model review request active · waiting for server…'):'Static inspection and labelled demo request active…');
 try {
  const result=await request('/api/analyze',{method:'POST',headers:reviewHeaders(),body:JSON.stringify(body)});
  if(requestVersion!==inputVersion) { error('Inputs changed while analysis was running. Response discarded. Analyze again.'); return; }
  renderReport(result.analysis || result);
 } catch(err) {
  needsStatusCheck=Boolean(err.uncertain || [429,502,503,504].includes(err.status));
  error(err.message);
  if(analysis) { stale=true; $('result-mode').textContent='PREVIOUS REVIEW · NEW REQUEST FAILED'; $('disclaimer').textContent='The new request failed. This previous review is stale; no new conclusion was accepted. Reanalyze before exporting.'; }
 } finally { setBusy(false); }
}
$('analyze').addEventListener('click',()=>analyze()); $('refine').addEventListener('click',()=>analyze(true));
function renderExecution(result) {
 const root=$('execution');root.replaceChildren();
 root.append(element('h4','Bundled fixture: '+(result.sample_id || 'unknown')));
 root.append(element('p',result.scope || 'Only the immutable bundled fixture ran.','hint'));
 const baseline=element('p',result.baseline_valid?'Baseline valid · collected tests passed':'Baseline not established · do not interpret as regression evidence',result.baseline_valid?'execution-good':'execution-warning');root.append(baseline);
 const grid=element('div',undefined,'execution-grid');
 const labels={baseline:'Before source × before tests',candidate:'After source × after tests',retained_tests:'After source × before tests',new_tests_on_before_source:'Before source × after tests',independent_requirement_oracle:'Independent requirement oracle'};
 for(const run of result.results || []) {
  const card=element('article',undefined,'execution-card'+(run.label==='independent_requirement_oracle'?' oracle-card':''));
  const outcome=run.outcome || 'unknown';card.append(element('h4',labels[run.label] || run.label));
  card.append(element('strong',outcome.replaceAll('_',' '),'execution-outcome '+(outcome==='passed'?'execution-good':outcome==='assertion_failure'?'execution-failure':'execution-warning')));
  const counts=run.counts || {};card.append(element('p',`${counts.tests_run ?? '—'} tests run · ${counts.assertion_failures ?? '—'} assertion failures · ${counts.errors ?? '—'} errors`));
  if(run.oracle_basis)card.append(element('p','Requirement: '+run.oracle_basis,'hint'));
  if(run.oracle_scope)card.append(element('p',run.oracle_scope,'hint'));
  if(run.label==='independent_requirement_oracle')root.append(card);else grid.append(card);
 }
 root.insertBefore(grid,root.children[3] || null);
 root.append(element('p','An assertion failure is an observed disagreement for these finite cases—not universal proof of a defect. Missing authority still requires clarification.','hint'));
 const details=element('details');details.append(element('summary','Inspect exact commands, hashes and raw results'),element('pre',JSON.stringify(result,null,2)));root.append(details);
 const exportButton=element('button','Export execution JSON','secondary');exportButton.type='button';exportButton.id='export-execution';exportButton.addEventListener('click',()=>download('test-evidence-execution-'+String(result.sample_id || 'fixture').replace(/[^a-zA-Z0-9_-]/g,'_')+'.json',JSON.stringify(result,null,2),'application/json'));root.append(exportButton,element('p','Separate execution artifact: immutable bundled fixture only, not the review or your edited inputs.','hint'));
}
$('run-fixture').addEventListener('click',async()=>{ if(busy || serverRunning || !$('samples').value) return; const version=inputVersion, sample=$('samples').value; $('execution').replaceChildren(); setBusy(true,'Executing the immutable bundled fixture · uploaded code is not run…'); error(''); try { const result=await request('/api/fixtures/'+encodeURIComponent(sample)+'/run',{method:'POST'}); if(version!==inputVersion) { error('Inputs changed during fixture execution. The response was discarded.'); return; } renderExecution(result); } catch(err) { error(err.message); } finally { setBusy(false); } });
$('prompts-button').addEventListener('click',async()=>{ try { $('prompts').textContent=JSON.stringify(await request('/api/prompts'),null,2); } catch(err) { error(err.message); } });
function download(filename,content,type) { const url=URL.createObjectURL(new Blob([content],{type})); const link=document.createElement('a'); link.href=url; link.download=filename; link.click(); setTimeout(()=>URL.revokeObjectURL(url),1000); }
$('export-json').addEventListener('click',()=>{if(analysis && !stale && !busy) download('test-evidence-analysis.json',JSON.stringify(analysis,null,2),'application/json');});
$('export-md').addEventListener('click',()=>{if(!analysis || stale || busy)return; const rows=['# Test Evidence review','',`Analysis: ${analysis.analysis_id || 'unspecified'}`,`Mode: ${analysis.mode}`,'',analysis.disclaimer || 'This report does not prove correctness.','']; for(const o of analysis.obligations || []) { rows.push(`## ${o.id}: ${o.description}`,`Status: ${o.status} · Origin: ${o.origin || analysis.mode}`,'',o.rationale || '',''); for(const e of o.evidence || []) rows.push(`Evidence: ${e.artifact}:${e.line_start}–${e.line_end}`,...String(e.quote || '').split('\n').map(line=>'> '+line),''); } rows.push('## Observations',...(analysis.observations || []).map(o=>`- ${o.kind}: ${text(o.detail)}`),'','## Questions',...(analysis.questions || []).map(q=>`- ${text(q)}`)); download('test-evidence-analysis.md',rows.map(line=>String(line).replaceAll('<','&lt;')).join('\n'),'text/markdown');});
async function init() {
 try {
  const data=await request('/api/samples'); samples=Array.isArray(data)?data:data.samples || [];
  samples.forEach(sample=>{const option=element('option',sample.title || sample.id);option.value=sample.id;$('samples').append(option);});
 } catch(err) { error(err.message); }
 await checkServerStatus();
}
init();


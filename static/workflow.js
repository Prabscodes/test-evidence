'use strict';
/* Presentation/navigation state only. No network, storage or assessment authority. */
(() => {
 const byId=id=>document.getElementById(id), views=['start','workspace','review'];
 let current='start', editor='source', findings=[], selected=null;
 let state={hasReview:false,stale:false,busy:false,blocked:false};
 const scroll={start:0,workspace:0,review:0};
 function route(){const value=location.hash.slice(1);return views.includes(value)?value:null;}
 function statusChanged(){byId('session-status').hidden=(current==='start'||current==='review')&&!state.busy&&!state.blocked&&byId('error').hidden;}
 function render(view, focus=true, restore=false){
  scroll[current]=window.scrollY;current=view;document.body.dataset.view=view;
  views.forEach(name=>byId(name+'-view').hidden=name!==view);
  document.querySelectorAll('button[data-view]').forEach(button=>{if(button.dataset.view===view)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');});
  byId('service-notice').hidden=view==='start';byId('review-safety').hidden=view==='review';byId('session-controls').hidden=view!=='workspace';
  byId('analyze').hidden=view!=='workspace';byId('review-edit').hidden=view!=='review';byId('inspect-fixture').hidden=view!=='workspace';
  statusChanged();
  if(focus)byId(view==='workspace'?'workspace-heading':view==='review'?'review-heading':'start-heading').focus({preventScroll:true});
  window.scrollTo(0,restore?scroll[view]:0);
 }
 function navigate(view, focus=true){if(!views.includes(view))return;if(current!==view)history.pushState(null,'','#'+view);render(view,focus);}
 function setEditor(name, focus=false){editor=name==='tests'?'tests':'source';for(const tab of ['source','tests']){const active=tab===editor;byId(tab+'-tab').setAttribute('aria-selected',String(active));byId(tab+'-tab').tabIndex=active?0:-1;byId(tab+'-panel').hidden=!active;}if(focus)byId(editor+'-tab').focus();}
 function openInputs(artifact){if(artifact?.startsWith('tests_'))setEditor('tests');else if(artifact?.startsWith('source_'))setEditor('source');navigate('workspace',false);}
 function sync(next){
  state={...state,...next};
  document.querySelectorAll('button[data-view="review"]').forEach(button=>button.disabled=!state.hasReview&&!state.busy);
  byId('finding-actions').hidden=!state.hasReview;byId('review-tools').hidden=!state.hasReview;
  byId('review-state').textContent=state.busy?'Request active. Navigation does not cancel it; no duplicate request will be sent.':state.stale?'Stale review · inputs changed or request failed. Reanalyze before exporting.':state.hasReview?'Inspect the evidence. A supported judgment is not approval.':'No current review yet.';
  byId('empty-message').textContent=state.busy?'Waiting for the server. Elapsed time is a wait timer, not model progress. You can inspect inputs while waiting.':'Return to Inputs and explicitly start a review. No conclusion was accepted; navigation never calls a model.';
  byId('own-change').textContent=['requirement','source_before','source_after','tests_before','tests_after'].some(id=>byId(id).value.trim())?'Continue my draft':'Use my own change';
  for(const kind of ['source','tests'])byId(kind+'-count').textContent=[kind+'_before',kind+'_after'].filter(id=>byId(id).value.trim()).length+' / 2';
  statusChanged();
 }
 function selectFinding(index, focus=false){
  if(!findings[index])return;selected=findings[index].id;const finding=findings[index];
  [...byId('obligations').children].forEach((card,i)=>card.hidden=i!==index);
  [...byId('finding-list').children].forEach((button,i)=>button.setAttribute('aria-pressed',String(i===index)));
  byId('finding-scope').textContent=`Finding ${index+1} of ${findings.length} · ${finding.id}`;
  byId('clarification-context').textContent=`Selected finding: ${finding.id}. Clarification applies to the complete review.`;
  const advice={supported:'Inspect the cited support against the requirement. Supported is a fallible judgment, not approval.',potentially_missing:'Check whether the cited lines establish a real gap. Confirm the requirement before changing tests.',unresolved:'Resolve missing authority or insufficient evidence. Add an authoritative clarification, then refine.'};
  byId('review-next-step').textContent=advice[finding.status]||advice.unresolved;
  if(focus){const heading=byId('obligations').children[index]?.querySelector('h3');if(heading){heading.tabIndex=-1;heading.focus();}}
 }
 function onResult(items){
  findings=items;const list=byId('finding-list');list.replaceChildren();
  items.forEach((finding,index)=>{const button=document.createElement('button');button.type='button';button.className='finding-button';button.setAttribute('aria-label',`${finding.id}: ${finding.description}. ${String(finding.status||'unresolved').replaceAll('_',' ')}`);const id=document.createElement('span'),description=document.createElement('strong'),status=document.createElement('span');id.textContent=finding.id;id.className='mono-label';description.textContent=finding.description;status.textContent=String(finding.status||'unresolved').replaceAll('_',' ');status.className='status '+(['supported','potentially_missing','unresolved'].includes(finding.status)?finding.status:'unresolved');button.append(id,description,status);button.addEventListener('click',()=>selectFinding(index,true));list.append(button);});
  const retained=items.findIndex(item=>item.id===selected);selectFinding(retained<0?0:retained);sync({hasReview:true});
  if(current!=='review')byId('navigation-note').textContent='Review ready. Open Review when you are ready; your current input view was preserved.';
  return current==='review';
 }
 function beginReview(){byId('navigation-note').textContent='';navigate('review');}
 function clearReview(){findings=[];selected=null;byId('finding-list').replaceChildren();sync({hasReview:false});}
 document.querySelectorAll('button[data-view]').forEach(button=>button.addEventListener('click',()=>navigate(button.dataset.view)));
 byId('own-change').addEventListener('click',()=>{navigate('workspace',false);byId('requirement').focus();});
 for(const id of ['empty-edit','review-edit'])byId(id).addEventListener('click',()=>navigate('workspace'));
 document.querySelectorAll('[data-open-inputs]').forEach(button=>button.addEventListener('click',()=>navigate('workspace')));
 byId('inspect-fixture').addEventListener('click',()=>{navigate('review');byId('execution-tools').open=true;byId('run-fixture').focus();});
 for(const name of ['source','tests']){
  const tab=byId(name+'-tab');tab.addEventListener('click',()=>setEditor(name));
  tab.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();setEditor(event.key==='Home'?'source':event.key==='End'?'tests':editor==='source'?'tests':'source',true);});
 }
 byId('jump-requirement').addEventListener('click',()=>byId('requirement').focus());
 for(const name of ['source','tests'])byId('jump-'+name).addEventListener('click',()=>{setEditor(name,true);byId(name+'-tab').scrollIntoView({block:'start'});});
 const back=()=>{const view=route();if(view&&view!==current)render(view,true,true);};window.addEventListener('popstate',back);window.addEventListener('hashchange',back);
 globalThis.reviewWorkflow={openInputs,onResult,beginReview,clearReview,sync,statusChanged,navigate};
 if(!route())history.replaceState(null,'','#start');render(route()||'start',false);sync({});
})();

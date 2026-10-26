// Deferred transport and clock tests against actual UI code. No model calls.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
class Node {
 constructor(){this.children=[];this.listeners={};this.value='';this.textContent='';this.hidden=true;this.disabled=false;this.maxLength=16000;}
 append(...x){this.children.push(...x)} replaceChildren(...x){this.children=x}
 addEventListener(k,f){this.listeners[k]=f} focus(){} scrollIntoView(){} setSelectionRange(){}
}
function harness(initial={}) {
 const nodes=new Map(),document={getElementById(id){if(!nodes.has(id))nodes.set(id,new Node());return nodes.get(id)},createElement(){return new Node()},querySelectorAll(){return []}};
 const get=id=>document.getElementById(id);get('mode').value='llm';
 let clock=100000,pending,posts=0,gets=0,state={configured:true,analysis_running:false,analysis_elapsed_seconds:null,http_timeout_seconds:300,...initial};const timers=new Map();let next=0;
 const context={document,console,Blob,URL,Event,setTimeout,Date:{now:()=>clock},setInterval(fn){timers.set(++next,fn);return next},clearInterval(id){timers.delete(id)},fetch:async(path,options)=>{
  if(path==='/api/analyze'){posts++;return await new Promise((resolve,reject)=>pending={resolve,reject})}
  if(path==='/api/status'){gets++;return {ok:true,json:async()=>state}}
  return {ok:true,json:async()=>({samples:[]})};
 }};
 vm.createContext(context);vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);
 const result={analysis_id:'test',mode:'llm',obligations:[],questions:[],provider:{actual_inference:true,raw_response:'{}'},observations:[]};
 return {get,timers,posts:()=>posts,gets:()=>gets,state:nextState=>state={...state,...nextState},tick(ms){clock+=ms;for(const fn of [...timers.values()])fn()},click:id=>get(id).listeners.click(),resolve:()=>pending.resolve({ok:true,status:200,json:async()=>result}),reject:()=>{const err=new Error('SECRET-TRANSPORT');err.name='AbortError';pending.reject(err)}};
}
const flush=()=>new Promise(resolve=>setImmediate(resolve));
const tests={
 async 'elapsed state advances without percentages and duplicate clicks send one POST'(){
  const h=harness();await flush();const active=h.click('analyze');await flush();h.click('analyze');assert.equal(h.posts(),1);h.tick(31000);
  assert.match(h.get('elapsed').textContent,/31\s*s/,'Elapsed time must remain visible during a slow request');
  assert(!h.get('progress').textContent.includes('%'));assert(h.get('analyze').disabled);h.resolve();await active;assert.equal(h.timers.size,0);
 },
 async 'transport cancellation requires read-only status recovery and never auto repeats'(){
  const h=harness();await flush();const active=h.click('analyze');await flush();h.reject();await active;
  assert.equal(h.posts(),1);assert.match(h.get('error').textContent,/may still|still be|continue/i);assert(!h.get('error').textContent.includes('SECRET'));
  assert(h.get('analyze').disabled,'Do not silently retry an uncertain cancelled request');
  assert.equal(typeof h.get('check-status').listeners.click,'function');await h.click('check-status');assert.equal(h.posts(),1);assert(h.gets()>=2);assert(!h.get('analyze').disabled);
 },
 async 'a failed fresh request cannot reenable exports of a previous report'(){
  const h=harness();await flush();const first=h.click('analyze');await flush();h.resolve();await first;assert(!h.get('export-json').disabled);
  const second=h.click('analyze');await flush();h.reject();await second;assert(h.get('export-json').disabled,'Old output must stay stale after failure');
 },
 async 'reloaded page sees running app request and does not start another review'(){
  const h=harness({analysis_running:true,analysis_elapsed_seconds:12});await flush();
  assert(h.get('analyze').disabled);await h.click('analyze');assert.equal(h.posts(),0);
  h.state({analysis_running:false,analysis_elapsed_seconds:null});await h.click('check-status');assert(!h.get('analyze').disabled);
 },
 async 'late response for edited inputs is discarded'(){
  const h=harness();await flush();const active=h.click('analyze');await flush();h.get('source_after').listeners.input();h.resolve();await active;
  assert.match(h.get('error').textContent,/Inputs changed/);assert(h.get('export-json').disabled);
 },
 async 'uncertain request blocks sample replacement until explicit status recovery'(){
  const h=harness();await flush();const active=h.click('analyze');await flush();h.reject();await active;
  assert(h.get('samples').disabled,'Do not allow a sample selector to show a different fixture while request outcome is uncertain');
  await h.click('check-status');assert(!h.get('samples').disabled);
 },
 async 'changing review mode invalidates an existing report'(){
  const h=harness();await flush();const active=h.click('analyze');await flush();h.resolve();await active;
  h.get('mode').value='demo';h.get('mode').listeners.change();assert(h.get('export-json').disabled,'Engine selection must not leave an old report exportable as current');
 }
};
(async()=>{let failures=0;for(const [name,test] of Object.entries(tests)){try{await test();console.log('PASS:',name)}catch(err){failures++;console.log('FAIL:',name,err.message)}}process.exitCode=failures?1:0;})();

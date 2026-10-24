// Real request construction in the existing DOM harness; no model call.
const fs = require('fs'), vm = require('vm'), assert = require('assert');
class Node {
  constructor() { this.value=''; this.children=[]; this.listeners={}; this.maxLength=16000; }
  append(...x) { this.children.push(...x); }
  replaceChildren(...x) { this.children=x; }
  addEventListener(k,f) { this.listeners[k]=f; }
  focus() {}
}
const nodes=new Map(), document={getElementById(id) { if(!nodes.has(id)) nodes.set(id,new Node()); return nodes.get(id); },createElement() {return new Node();},querySelectorAll() {return [];} };
let posted;
const ctx={document,console,Blob,URL,setTimeout,setInterval,clearInterval,Event,fetch:async(path,options)=>{
  if(path==='/api/analyze') posted=JSON.parse(options.body);
  return {ok:true,json:async()=>path==='/api/samples'?{samples:[]}:path==='/api/status'?{configured:false}:{mode:'demo',obligations:[],questions:[]}};
}};
vm.createContext(ctx); vm.runInContext(fs.readFileSync('static/app.js','utf8'),ctx);
(async()=>{
  document.getElementById('mode').value='demo';
  document.getElementById('clarification').value='Return zero for an empty batch.';
  await document.getElementById('analyze').listeners.click();
  assert.equal(posted.clarification,'Return zero for an empty batch.','Analyze must include visible authoritative clarification');
  assert.equal(posted.previous_analysis,undefined,'Prior review context is reserved for refinement');
  await document.getElementById('refine').listeners.click();
  assert.equal(posted.clarification,'Return zero for an empty batch.');
  assert.deepEqual(Object.keys(posted.previous_analysis),['obligations','questions']);
  console.log('PASS: visible clarification is sent on Analyze and Refine; prior review only on Refine.');
})();

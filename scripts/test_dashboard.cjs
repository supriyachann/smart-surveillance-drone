// A minimal DOM harness checks real dashboard actions without a browser dependency.
// This does not replace visual browser QA.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
async function run(protocol) {
class Element {
  constructor(tag) { this.tagName = tag; this.children = []; this.value = 'all'; this.textContent = ''; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(name,value) { this[name] = value; }
  click() { if(this.download) downloads.push(this); }
}
const nodes = new Map();
const downloads = [];
const blobs = [];
const context = vm.createContext({
  document: {documentElement:{dataset:{mode:protocol === 'https:' ? 'demo' : ''}},getElementById(id) { if(!nodes.has(id)) nodes.set(id,new Element('div')); return nodes.get(id); }, createElement:tag=>new Element(tag)},
  location: {protocol},
  fetch(){ throw new Error("Sample mode must not call a backend"); },
  URL: {createObjectURL(blob) { blobs.push(blob); return 'blob:test'; }, revokeObjectURL(){}},
  Blob, Date, console, setInterval(){}, setTimeout(){},
});
vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);

  await nodes.get('load').onclick();
  assert.equal(nodes.get('events').children.length,2);
  assert.match(nodes.get('connection').textContent,protocol === 'file:' ? /Offline preview/ : /Sample preview/);
  assert.match(nodes.get('scene-mode').textContent,/Synthetic/);
  const first = nodes.get('events').children[0];
  first.children[2].children[0].onclick();
  assert.match(nodes.get('inspection').textContent,/not its original camera frame/);
  await nodes.get('events').children[0].children[2].children[1].onclick();
  assert.equal(nodes.get('events').children[0].children[2].children[1].textContent,'Reviewed');
  nodes.get('filter').value='pending'; nodes.get('filter').onchange();
  assert.equal(nodes.get('events').children.length,1);
  await nodes.get('load').onclick();
  assert.match(nodes.get('message').textContent,/already loaded/);
  nodes.get('export').onclick();
  assert.equal(downloads.length,1);
  const exported = JSON.parse(await blobs[0].text());
  assert.equal(exported.events.length,2);
  assert.ok(exported.events.every(e=>e.synthetic));
  assert.equal(exported.events.filter(e=>e.reviewed).length,1);
  console.log(`${protocol} dashboard workflow passed: load, inspect, review, filter, deduplicate, export; no backend calls.`);
}
run('file:').then(()=>run('https:')).catch(error=>{console.error(error);process.exitCode=1;});

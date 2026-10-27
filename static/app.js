let events = [];
let selectedId = null;
const $ = (id) => document.getElementById(id);
const offline = location.protocol === 'file:';
const demoMode = offline || document.documentElement.dataset.mode === 'demo';
const localEvents = [];

if (demoMode) {
  $('runtime-mode').textContent = 'Interactive sample demo';
  $('storage-note').textContent = 'Sample events stay in this tab and reset when you reload. No footage or flight data is collected.';
  $('inspection').textContent = 'Load sample events to inspect and review this synthetic session. Real camera detection runs separately with the Python project.';
}

async function request(path, body) {
  // Opening index.html directly provides an honest synthetic-only demo.
  if (demoMode) {
    if (path === '/api/demo') {
      let added = 0;
      for (const [index, label] of ['person','car'].entries()) {
        const event_id = `offline-sample-${index}`;
        if (localEvents.some(e=>e.event_id===event_id)) continue;
        localEvents.unshift({schema_version:1,event_id,timestamp:'2026-01-01T00:00:00Z',source_id:'offline-demo',label,confidence:index ? .91 : .87,bbox_normalized:index ? [.5,.45,.9,.75] : [.2,.15,.4,.8],synthetic:true,reviewed:false});
        added++;
      }
      return {added};
    }
    if (path === '/api/review') {
      const event = localEvents.find(e=>e.event_id===body.event_id);
      if (event) event.reviewed = true;
      return {reviewed:Boolean(event)};
    }
    return {events:localEvents.map(e=>({...e}))};
  }
  const response = await fetch(path, body === undefined ? {} : {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed');
  return data;
}

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function inspect(event) {
  selectedId = event.event_id;
  const [x1, y1, x2, y2] = event.bbox_normalized;
  const box = $('bbox');
  Object.entries({x:x1*900,y:y1*520,width:(x2-x1)*900,height:(y2-y1)*520}).forEach(([k,v])=>box.setAttribute(k,v));
  $('box-label').textContent = `${event.label} · ${(event.confidence*100).toFixed(0)}% model confidence`;
  $('scene-mode').textContent = event.synthetic ? 'Synthetic event' : 'Detector event';
  $('inspection').textContent = `${event.source_id} · Captured ${new Date(event.timestamp).toLocaleString()}. Bounding box projected onto an illustration, not its original camera frame.`;
  render();
}

function render() {
  const filter = $('filter').value;
  const filtered = events.filter(e => filter === 'all' || (filter === 'pending' && !e.reviewed) || (filter === 'synthetic' && e.synthetic) || (filter === 'real' && !e.synthetic));
  $('event-count').textContent = `${events.filter(e=>!e.reviewed).length} awaiting review`;
  $('events').replaceChildren();
  if (!filtered.length) $('events').append(element('p', events.length ? 'No events match this filter.' : 'No detections yet. Load sample events or connect the optional detector.', 'empty'));
  for (const event of filtered) {
    const row = element('article', undefined, 'event' + (event.event_id === selectedId ? ' selected' : ''));
    const top = element('div', undefined, 'event-top');
    top.append(element('h3', event.label), element('span', event.synthetic ? 'Synthetic sample' : 'Detector event', 'tag' + (event.synthetic ? '' : ' real')));
    const date = new Date(event.timestamp);
    const meta = element('p', `${(event.confidence*100).toFixed(0)}% confidence · ${date.toLocaleString()} · ${event.source_id}`, 'meta');
    const actions = element('div', undefined, 'event-actions');
    const view = element('button', 'Inspect', 'secondary');
    view.onclick = () => inspect(event);
    actions.append(view);
    if (event.reviewed) actions.append(element('span', 'Reviewed', 'reviewed'));
    else {
      const review = element('button', 'Mark reviewed');
      review.onclick = async () => {
        try { await request('/api/review', {event_id:event.event_id}); await refresh(); }
        catch (error) { $('message').textContent = error.message; }
      };
      actions.append(review);
    }
    row.append(top, meta, actions);
    $('events').append(row);
  }
}

async function refresh() {
  try {
    const result = await request('/api/events');
    const changed = JSON.stringify(events) !== JSON.stringify(result.events);
    events = result.events;
    $('connection').textContent = offline ? 'Offline preview · synthetic data only · resets on reload' : demoMode ? 'Sample preview · synthetic data only · resets on reload' : 'Local service connected · refreshes every 2 seconds';
    if (changed) render();
  } catch (error) {
    $('connection').textContent = 'Service unavailable · restart app.py';
  }
}

$('load').onclick = async () => {
  $('load').disabled = true;
  try {
    const result = await request('/api/demo', {});
    await refresh();
    if (events.length) inspect(events.find(e=>e.synthetic) || events[0]);
    $('message').textContent = result.added ? 'Two synthetic events loaded. Select Inspect, then Mark reviewed.' : 'Sample events are already loaded; duplicate events were skipped.';
  } catch (error) { $('message').textContent = error.message; }
  finally { $('load').disabled = false; }
};
$('export').onclick = () => {
  const url = URL.createObjectURL(new Blob([JSON.stringify({exported_at:new Date().toISOString(),events},null,2)],{type:'application/json'}));
  const link = element('a'); link.href=url; link.download='surveillance-events.json'; link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  $('message').textContent = `Exported ${events.length} events, including synthetic labels and review status.`;
};
$('filter').onchange = render;
render(); refresh(); setInterval(refresh,2000);

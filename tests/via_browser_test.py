#!/usr/bin/env python3
"""Real Chromium via interactions; storage and download navigation use explicit test doubles.
No application functions are substituted. Placement, editing and routing use actual UI events.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, time, traceback, sys
from playwright.sync_api import sync_playwright
from browser_support import launch_chromium
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';IMAGES=OUT/'images'
IMAGES.mkdir(parents=True,exist_ok=True);results=[]
STORE="""() => {window.__store={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>__store[k]??null,setItem:(k,v)=>__store[k]=String(v),removeItem:k=>delete __store[k]}});window.__blobs=new Map;window.__exports=[];const orig=URL.createObjectURL;URL.createObjectURL=b=>{const u=orig.call(URL,b);__blobs.set(u,b);return u;};}"""
BLANK="""(()=>{const d=CB.blank();d.title='Vias · a connection through the board';d.board={...d.board,width:40,height:30,shape:'rect'};d.settings.grid=.5;return d;})()"""
PAIR="""(()=>{const d="""+BLANK+""";const n=CB.newNet(d,'LINK');for(const [x,side] of [[8,'top'],[32,'bottom']]){const p=CB.makePart(d,'testpoint',x,10);p.pads[0].drill=0;p.pads[0].net=n;p.side=side;p.verified=true;p.label.visible=false;d.parts.push(p);}return d;})()"""
VIA_PAIR="""(()=>{const d="""+BLANK+""";const n=CB.newNet(d,'GND');CB.V.add(d,{x:10,y:15},{net:n});CB.V.add(d,{x:30,y:15},{net:n});return d;})()"""
with sync_playwright() as pw:
 browser=launch_chromium(pw);page=browser.new_page(viewport={'width':1600,'height':1050},device_scale_factor=1)
 page.set_default_timeout(8000);errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
 page.evaluate(STORE);page.set_content((ROOT/'COPPERBENCH-portable.html').read_text(),wait_until='load')
 page.evaluate("document.addEventListener('click',e=>{const a=e.target.closest('a[download]');if(a){e.preventDefault();__exports.push({name:a.download,blob:__blobs.get(a.href)});}},true)")
 page.wait_for_function('CBAPP?.ready && CBAPP.state.checkRevision===CBAPP.state.revision')
 def check(c,m='Assertion failed'):
  if not c:raise AssertionError(m)
 def act(name):page.locator(f'button[data-action="{name}"]:visible').first.click()
 def close():
  if page.locator('#modal').evaluate('(e)=>e.open'):page.locator('#modalClose').click()
 def reset(expr=BLANK):
  close();page.evaluate('CBAPP.load('+expr+')');page.keyboard.press('Escape')
  page.locator('[data-view=copper]').click();page.locator('[data-side=top]').click()
  page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision',timeout=20000)
 def tool(name):page.locator(f'[data-tool="{name}"]:visible').first.click()
 def world(x,y):return page.evaluate('p=>{const r=CBAPP.renderer;r.setup();const q=r.project(p),b=r.canvas.getBoundingClientRect();return{x:q.x+b.left,y:q.y+b.top};}',{'x':x,'y':y})
 def point(x,y):
  p=world(x,y);page.mouse.click(p['x'],p['y']);page.wait_for_timeout(50)
 def move(x,y):
  p=world(x,y);page.mouse.move(p['x'],p['y']);page.wait_for_timeout(40)
 def number(selector,value):page.locator(selector).fill(str(value));page.locator(selector).press('Tab');page.wait_for_timeout(50)
 def test(name,fn):
  t=time.perf_counter()
  try:fn();results.append({'name':name,'pass':True,'ms':round((time.perf_counter()-t)*1000)});print('PASS',name,flush=True)
  except Exception as e:
   results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,str(e),flush=True);page.screenshot(path=str(IMAGES/f'via-failure-{len(results)}.png'));traceback.print_exc()
 def visible():
  reset();check(page.locator('.contextbar [data-tool=via]').is_visible());tool('via')
  check(page.locator('#viaNet').is_visible());check(page.locator('#viaDiameter').is_visible())
  act('via-new-net');page.fill('#viaNewNetName','GND');page.get_by_role('button',name='Create and select',exact=True).click()
  point(20,15);check(page.evaluate('CBAPP.state.doc.vias.length===1 && CB.netName(CBAPP.state.doc,CBAPP.state.doc.vias[0].net)==="GND"'))
 test('Visible Via button opens controls and creates an assigned plated via',visible)
 def repeat():
  reset();tool('via');page.select_option('#viaPreset','compact');page.check('#viaTented');point(10,8);point(20,8)
  check(page.evaluate('CBAPP.state.doc.vias.length===2 && CBAPP.state.doc.vias.every(v=>v.diameter===.7&&v.drill===.3&&v.tented)'))
  page.keyboard.press('Escape');act('undo');check(page.evaluate('CBAPP.state.doc.vias.length===1'));act('redo');check(page.evaluate('CBAPP.state.doc.vias.length===2'))
 test('Repeated placement uses preset/tenting defaults and supports undo/redo',repeat)
 def unassigned():
  reset();tool('via');point(20,15);check(page.evaluate('CB.G.findings(CBAPP.state.doc).some(f=>f.code==="unassigned-via")'))
 test('Unassigned empty-space vias stay visible to manufacturing checks',unassigned)
 def trace_snap():
  reset("""(()=>{const d="""+BLANK+""";const n=CB.newNet(d,'GND');d.traces.push({id:'t',net:n,width:.4,layer:'top',points:[{x:8,y:12.17},{x:32,y:12.17}]});return d;})()""")
  tool('via');point(18.23,12.17);check(page.evaluate('Math.abs(CBAPP.state.doc.vias[0].y-12.17)<.001 && CBAPP.state.doc.vias[0].net===CBAPP.state.doc.nets[0].id'))
 test('Placing directly on an off-grid trace snaps to its center and inherits net',trace_snap)
 def conflict():
  reset("""(()=>{const d="""+BLANK+""";for(const side of ['top','bottom'])d.traces.push({id:side,net:CB.newNet(d,side),width:.4,layer:side,points:[{x:8,y:15},{x:32,y:15}]});return d;})()""")
  tool('via');before=page.evaluate('JSON.stringify(CBAPP.state.doc)');move(20,15);check(page.evaluate('CBAPP.state.viaPreview.ok===false'));point(20,15)
  check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before);check('different nets' in page.locator('#toast').inner_text())
 test('Conflicting front/back nets produce a red preview and no board mutation',conflict)
 def blocked():
  reset();tool('via');point(.1,15);check(page.evaluate('CBAPP.state.doc.vias.length===0'))
  reset("""(()=>{const d="""+BLANK+""";d.holes.push({id:'h',x:20,y:15,drill:3.2,plated:false});return d;})()""")
  tool('via');point(20,15);check(page.evaluate('CBAPP.state.doc.vias.length===0'))
 test('Board-edge and mounting-hole clashes block standalone placement',blocked)
 def bad_size():
  reset();tool('via');number('#viaDrill',.85);check(page.evaluate('CBAPP.state.doc.settings.viaDrill===.4'))
  number('#viaDrill',.2);check(page.evaluate('CBAPP.state.doc.settings.viaDrill===.4'))
 test('Bad annular rings and undersized drills do not change placement defaults',bad_size)
 def inspect():
  reset(VIA_PAIR);point(10,15);check(page.locator('[data-prop=diameter]').is_visible())
  number('[data-prop=diameter]',1.2);number('[data-prop=drill]',.6);page.check('[data-prop=tented]');page.check('[data-prop=locked]')
  number('[data-prop=x]',14);check(page.evaluate('CBAPP.state.doc.vias[0].x===10'))
  page.uncheck('[data-prop=locked]');number('[data-prop=x]',12)
  check(page.evaluate('CBAPP.state.doc.vias[0].x===12 && CBAPP.state.doc.vias[0].diameter===1.2 && CBAPP.state.doc.vias[0].drill===.6 && CBAPP.state.doc.vias[0].tented'))
 test('Inspector edits dimensions/tenting and respects the via lock',inspect)
 def shortcut_route():
  reset(PAIR);tool('trace');point(8,10);move(20,10);page.keyboard.press('v')
  check(page.evaluate('CBAPP.state.side==="bottom" && CBAPP.state.doc.vias.length===1 && CBAPP.state.doc.traces.length===1'))
  point(32,10);check(page.evaluate('CBAPP.state.doc.traces.length===2 && CB.G.connectivity(CBAPP.state.doc).unrouted===0'))
 test('V during tracing inserts a via and continues a connected bottom-layer route',shortcut_route)
 def toolbar_route():
  reset(PAIR);tool('trace');point(8,10);act('insert-via');check(page.evaluate('CBAPP.state.viaPending && CBAPP.state.drawing!==null'))
  point(20,10);check(page.evaluate('CBAPP.state.doc.traces.length===1 && CBAPP.state.doc.vias.length===1'))
  act('undo');check(page.evaluate('CBAPP.state.doc.traces.length===0 && CBAPP.state.doc.vias.length===0'))
  act('redo');check(page.evaluate('CBAPP.state.doc.traces.length===1 && CBAPP.state.doc.vias.length===1'))
 test('Visible layer-change button commits trace plus via as one undoable edit',toolbar_route)
 def via_to_via():
  reset(VIA_PAIR);tool('trace');point(10,15);point(30,15)
  check(page.evaluate('CBAPP.state.doc.traces.length===1 && CBAPP.state.doc.traces[0].net===CBAPP.state.doc.vias[0].net'))
  page.keyboard.press('Escape');point(10,15);check(page.evaluate('CBAPP.state.selection[0]===CBAPP.state.doc.vias[0].id'))
  act('route-from-via');check(page.evaluate('CBAPP.state.tool==="trace" && CBAPP.state.drawing.points[0].x===10'))
 test('Traces start/end on vias and a via remains selectable over its trace',via_to_via)
 def via_to_trace():
  reset("""(()=>{const d="""+VIA_PAIR+""";const n=d.nets[0].id;d.traces.push({id:'branch',net:n,width:.4,layer:'top',points:[{x:8,y:6},{x:32,y:6}]});return d;})()""")
  tool('trace');point(10,15);point(10,6);check(page.evaluate('CBAPP.state.doc.traces.length===2 && CBAPP.state.drawing===null'))
 test('Via routes can finish directly on an existing same-net trace',via_to_trace)
 def blocked_insertion():
  reset("""(()=>{const d="""+PAIR+""";d.traces.push({id:'obstacle',net:CB.newNet(d,'OTHER'),width:1,layer:'bottom',points:[{x:20,y:5},{x:20,y:25}]});return d;})()""")
  tool('trace');point(8,10);move(20,10);before=page.evaluate('JSON.stringify(CBAPP.state.doc)');page.keyboard.press('v')
  check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before);check(page.evaluate('CBAPP.state.side==="top" && CBAPP.state.drawing!==null'))
 test('Blocked routing via leaves the trace, side and board unchanged',blocked_insertion)
 def manage():
  reset(VIA_PAIR);page.locator('[data-panel=nets]').click();act('vias-table');check(page.locator('[data-via-select]').count()==2)
  page.locator('[data-via-select]').last.click();check(page.evaluate('CBAPP.state.selection[0]===CBAPP.state.doc.vias[1].id'))
  act('duplicate');check(page.evaluate('CBAPP.state.doc.vias.length===3'));act('delete');check(page.evaluate('CBAPP.state.doc.vias.length===2'))
 test('Manage vias table selects objects for duplication and deletion',manage)
 def move_disconnect():
  reset(PAIR);tool('trace');point(8,10);move(20,10);page.keyboard.press('v');point(32,10);page.keyboard.press('Escape');point(20,10)
  number('[data-prop=y]',18);check(page.evaluate('CB.G.connectivity(CBAPP.state.doc).unrouted===1'))
  act('undo');check(page.evaluate('CB.G.connectivity(CBAPP.state.doc).unrouted===0'))
 test('Moving an attached via exposes disconnection instead of moving copper silently',move_disconnect)
 def backup():
  reset(VIA_PAIR);point(10,15);page.check('[data-prop=tented]');page.check('[data-prop=locked]');act('save')
  raw=page.evaluate('async()=>await __exports.at(-1).blob.text()');d=json.loads(raw)
  check(d['vias'][0]['tented'] and d['vias'][0]['locked']);check(d['schema']==5)
  page.locator('#fileInput').set_input_files({'name':'vias.json','mimeType':'application/json','buffer':raw.encode()})
  page.get_by_role('button',name='Open this board',exact=True).click();check(page.evaluate('CBAPP.state.doc.vias[0].tented && CBAPP.state.doc.vias[0].locked'))
 test('JSON backup and actual file-input import retain via details',backup)
 def kicad_warning():
  reset(VIA_PAIR);point(10,15);page.check('[data-prop=tented]');act('export');act('export-kicad')
  check('not preserved' in page.locator('#modalBody').inner_text())
  before=page.evaluate('window.__exports.length');page.get_by_role('button',name='Export geometry',exact=True).click()
  page.wait_for_function('n=>window.__exports.length>n',arg=before)
  check(page.evaluate('window.__exports.at(-1).name.endsWith(".kicad_pcb")'))
 test('KiCad export explicitly warns about via mask/lock limitations',kicad_warning)
 def blocked_nudge():
  reset('(()=>{const d=CB.blank();d.board.width=40;d.board.height=30;const n=CB.newNet(d,"GND");CB.V.add(d,{x:1,y:15},{net:n});return d;})()')
  point(1,15);before=page.evaluate('JSON.stringify(CBAPP.state.doc)');page.keyboard.press('ArrowLeft')
  check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before)
  check(page.locator('#toast').is_visible())
 test('A blocked arrow-key via move rolls back without an uncaught exception',blocked_nudge)
 def preview_capture():
  reset(PAIR);tool('trace');point(8,10);move(20,10);page.keyboard.press('v');point(32,10)
  page.keyboard.press('Escape');page.locator('[data-side=top]').click();tool('via');page.select_option('#viaPreset','standard');move(23,19)
  page.evaluate("document.getElementById('toast').hidden=true;")
  page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision && CBAPP.state.connectivity.unrouted===0');page.screenshot(path=str(IMAGES/'via-placement.png'));check(page.locator('#viaPlacementStatus').is_visible())
  page.keyboard.press('Escape');point(20,10);page.screenshot(path=str(IMAGES/'via-inspector.png'))
  page.locator('[data-view=fabrication]').click();page.wait_for_timeout(100);page.screenshot(path=str(IMAGES/'via-fabrication.png'))
  check(page.evaluate('CBAPP.state.fabData["board-PTH.drl"].objects.length===1'))
 test('Placement, inspector and generated-file views render the actual via',preview_capture)
 def mobile():
  reset();page.set_viewport_size({'width':430,'height':850});page.locator('.contextbar [data-tool=via]').click()
  check(page.evaluate('CBAPP.state.tool==="via"'))
  check(page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'), 'Mobile page overflows horizontally')
  page.screenshot(path=str(IMAGES/'via-mobile.png'));page.set_viewport_size({'width':1600,'height':1050})
 test('Narrow-screen users can reach the visible Via tool without page overflow',mobile)
 test('No external asset requests or uncaught exceptions in via workflows',lambda:check(not errors and not [r for r in requests if r.startswith('http')],str(errors)+' '+str(requests)))
 record={'version':page.evaluate('CB.VERSION'),'date':datetime.now(timezone.utc).isoformat(),'passed':sum(r['pass'] for r in results),'total':len(results),'scope':'Real Chromium controls/canvas/workers with simulated localStorage and intercepted download blobs. No file-origin persistence or hosted service-worker certification.','results':results}
 (OUT/'via-browser-results.json').write_text(json.dumps(record,indent=2));print(json.dumps({'passed':record['passed'],'total':record['total']}));browser.close()
sys.exit(0 if record['passed']==record['total'] else 1)

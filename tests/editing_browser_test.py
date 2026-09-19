#!/usr/bin/env python3
"""Real DOM/canvas/worker tests, with explicit storage and download test doubles.
No real-origin persistence, manufacturer acceptance or hardware testing is implied.
"""
from pathlib import Path
import json, time, traceback
from playwright.sync_api import sync_playwright
from browser_support import launch_chromium
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';IMAGES=OUT/'images';IMAGES.mkdir(parents=True,exist_ok=True)
RESULTS=[]
STORE="""seed=>{window.__store=seed;window.__quotaError=false;Object.defineProperty(window,'localStorage',{value:{getItem:k=>window.__store[k]??null,setItem:(k,v)=>{if(window.__quotaError)throw new DOMException('Quota','QuotaExceededError');window.__store[k]=String(v)},removeItem:k=>delete window.__store[k],clear:()=>window.__store={}}});window.__blobs=new Map;window.__exports=[];const orig=URL.createObjectURL;URL.createObjectURL=function(b){const u=orig.call(URL,b);window.__blobs.set(u,b);return u};}"""
PAIR="""(()=>{let d=CB.blank();d.title='Edit workbench';d.board={...d.board,width:60,height:45,shape:'rect'};d.settings.grid=1;const n=CB.newNet(d,'LINK');for(const [x,y] of [[10,10],[45,10]]){const p=CB.makePart(d,'testpoint',x,y);p.pads[0].net=n;p.label.visible=false;p.verified=true;d.parts.push(p);}d.traces=[{id:'route1',net:n,layer:'top',points:[{x:10,y:10},{x:45,y:10}],width:.4,locked:false}];return d;})()"""
with sync_playwright() as pw:
 browser=launch_chromium(pw);page=None;errors=[];requests=[]
 def boot(seed=None):
  global page
  if page:page.close()
  page=browser.new_page(viewport={'width':1500,'height':960},device_scale_factor=1);page.set_default_timeout(8000)
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
  page.evaluate(STORE,seed or {})
  page.set_content((ROOT/'COPPERBENCH-portable.html').read_text(),wait_until='load')
  page.evaluate("document.addEventListener('click',e=>{const a=e.target.closest('a[download]');if(a){e.preventDefault();__exports.push({name:a.download,blob:__blobs.get(a.href)});}},true)")
  page.wait_for_function('CBAPP?.ready && CBAPP.state.checkRevision===CBAPP.state.revision',timeout=20000)
 def act(name):page.locator(f'button[data-action="{name}"]:visible').first.click()
 def close():
  if page.locator('#modal').evaluate('(e)=>e.open'):page.locator('#modalClose').click()
 def reset(expr=PAIR):
  close();page.keyboard.press('Escape');page.evaluate('CBAPP.load('+expr+')');page.click('[data-view=copper]')
  page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision',timeout=20000)
 def world(x,y):return page.evaluate('p=>{const r=CBAPP.renderer;r.setup();const q=r.project(p),b=r.canvas.getBoundingClientRect();return{x:q.x+b.left,y:q.y+b.top}}',{'x':x,'y':y})
 def click(x,y):
  p=world(x,y);page.mouse.click(p['x'],p['y']);page.wait_for_timeout(60)
 def drag(a,b):
  p=world(*a);q=world(*b);page.mouse.move(p['x'],p['y']);page.mouse.down();page.mouse.move(q['x'],q['y'],steps=8);page.mouse.up();page.wait_for_timeout(100)
 def check(c,msg='Assertion failed'):
  if not c:raise AssertionError(msg)
 def test(name,fn):
  import os
  if os.environ.get('EDIT_TEST_FILTER') and os.environ['EDIT_TEST_FILTER'].lower() not in name.lower():return
  t=time.perf_counter()
  try:fn();RESULTS.append({'name':name,'pass':True,'ms':round((time.perf_counter()-t)*1000)});print('PASS',name,flush=True)
  except Exception as e:RESULTS.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,str(e),flush=True);traceback.print_exc();page.screenshot(path=str(OUT/f'editing-failure-{len(RESULTS)}.png'))
 def trace_select():page.select_option('#selectionFilter','copper');click(27,10)
 boot()
 test('v1.7 boots with 193 parts, schema 5 and focused selection controls',lambda:check(page.evaluate('version=>CB.VERSION===version && CB.LIB.length===193 && CBAPP.state.doc.schema===5', json.loads((ROOT/'package.json').read_text())['version']) and page.locator('#selectionFilter').is_visible()))
 def filters():
  reset();page.select_option('#selectionFilter','parts');click(27,10);check(page.evaluate('CBAPP.state.selection.length===0'))
  page.select_option('#selectionFilter','copper');click(27,10);check(page.evaluate('CBAPP.state.selection[0]==="route1"'));check(page.locator('#editSegment').is_visible())
 test('Parts filter ignores traces; Copper filter selects a trace',filters)
 def cycle():
  reset();page.select_option('#selectionFilter','copper');click(10,10);first=page.evaluate('CBAPP.state.selection[0]');page.keyboard.press(']');check(page.evaluate('CBAPP.state.selection[0]==="route1"'));check(first!='route1')
 test('Overlap cycling reaches a trace beneath its pad using ]',cycle)
 def slide():
  reset();trace_select();before=page.evaluate('JSON.stringify(CBAPP.state.doc)');drag((27,10),(27,20));check(page.evaluate('CBAPP.state.editPreview!==null'));check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before)
  check(page.locator('[data-action=accept-edit]').is_visible());page.evaluate("document.querySelector('#toast').hidden=true");page.screenshot(path=str(IMAGES/'editing-preview.png'))
  act('accept-edit');check(page.evaluate('CBAPP.state.doc.traces[0].points.length===4 && CB.G.connectivity(CBAPP.state.doc).unrouted===0'))
  act('undo');check(page.evaluate('CBAPP.state.doc.traces[0].points.length===2'));act('redo');check(page.evaluate('CBAPP.state.doc.traces[0].points.length===4'))
 test('Drag segment previews doglegs without mutation, then commits as one undo',slide)
 def cancel():
  reset();trace_select();before=page.evaluate('JSON.stringify(CBAPP.state.doc)');drag((27,10),(27,18));page.keyboard.press('Escape');check(page.evaluate('!CBAPP.state.editPreview'));check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before)
 test('Escape cancels preview without altering source copper',cancel)
 def width():
  reset();trace_select();act('edit-width');page.fill('#editWidth','.8');page.select_option('#widthScope','trace');page.get_by_role('button',name='Preview',exact=True).click();check(page.evaluate('CBAPP.state.doc.traces[0].width===.4'));act('accept-edit');check(page.evaluate('CBAPP.state.doc.traces[0].width===.8'))
 test('Width scope dialog stages and applies a validated width',width)
 def segment_width():
  reset("(()=>{const d="+PAIR+";d.traces[0].points.splice(1,0,{x:20,y:10},{x:35,y:10});return d;})()");trace_select();page.select_option('#editSegment','1');act('edit-width');page.fill('#editWidth','.8');page.select_option('#widthScope','segment');page.get_by_role('button',name='Preview',exact=True).click();act('accept-edit');check(page.evaluate('CBAPP.state.doc.traces.length===3 && CBAPP.state.doc.traces.filter(t=>t.width===.8).length===1'))
 test('Selected-segment width preserves widths of neighbouring sections',segment_width)
 def corners():
  reset();trace_select();act('edit-insert');page.fill('#pointX','27');page.fill('#pointY','10');page.get_by_role('button',name='Preview',exact=True).click();act('accept-edit');check(page.evaluate('CBAPP.state.doc.traces[0].points.length===3'))
  drag((27,10),(27,18));act('accept-edit');check(page.evaluate('CBAPP.state.doc.traces[0].points[1].y===18'));act('edit-remove');page.get_by_role('button',name='Preview',exact=True).click();act('accept-edit');check(page.evaluate('CBAPP.state.doc.traces[0].points.length===2'))
 test('Insert, drag and remove an interior corner using canvas and controls',corners)
 def replace():
  reset();trace_select();act('edit-replace');page.fill('#replacePoints','15,20\n40,20');page.get_by_role('button',name='Preview',exact=True).click();act('accept-edit');check(page.evaluate('CBAPP.state.doc.traces[0].points.length===4'))
 test('Replace-section dialog preserves fixed endpoints and inserts waypoints',replace)
 def cleanup():
  reset("(()=>{const d="+PAIR+";d.traces[0].points.splice(1,0,{x:20,y:10},{x:30,y:10});return d;})()");trace_select();act('simplify-trace');check(page.evaluate('CBAPP.state.editPreview!==null && CBAPP.state.doc.traces[0].points.length===4'));act('accept-edit');check(page.evaluate('CBAPP.state.doc.traces[0].points.length===2'))
 test('Cleanup proposals remove redundant collinear points, not user intent',cleanup)
 def connected():
  reset();act('connected-drag');drag((10,10),(10,20));check(page.evaluate('CBAPP.state.editPreview!==null && CBAPP.state.doc.parts[0].y===10'));act('accept-edit');check(page.evaluate('CBAPP.state.doc.parts[0].y===20 && CB.G.connectivity(CBAPP.state.doc).unrouted===0'));act('undo');check(page.evaluate('CBAPP.state.doc.parts[0].y===10'))
 test('Drag-connected toggle moves a part and its attachment as one transaction',connected)
 def coordinate():
  reset();click(10,10);act('connected-position');page.fill('#connectedX','15');page.fill('#connectedY','20');page.get_by_role('button',name='Preview',exact=True).click();act('accept-edit');check(page.evaluate('CBAPP.state.doc.parts[0].x===15 && CBAPP.state.doc.parts[0].y===20'))
 test('Exact-coordinate connected move is available in component inspector',coordinate)
 def rejection():
  reset("(()=>{const d="+PAIR+";d.traces[0].points[0].x=9.8;return d;})()");before=page.evaluate('JSON.stringify(CBAPP.state.doc)');act('connected-drag');drag((10,10),(10,20));check(page.evaluate('!CBAPP.state.editPreview'));check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before);check('centered' in page.locator('#toast').inner_text())
 test('Unsupported off-centre attachment explains rejection without moving board objects',rejection)
 def connected_via():
  reset("(()=>{const d="+PAIR+";d.parts[1].side='bottom';d.parts[1].y=30;d.traces[0].points[1]={x:30,y:10};d.vias=[{id:'via1',x:30,y:10,net:d.nets[0].id,diameter:1,drill:.4,tented:true,locked:false}];d.traces.push({id:'bottom',net:d.nets[0].id,layer:'bottom',points:[{x:30,y:10},{x:45,y:30}],width:.4,locked:false});return d;})()");act('connected-drag');drag((30,10),(30,20));act('accept-edit');check(page.evaluate('CBAPP.state.doc.vias[0].y===20 && CB.G.connectivity(CBAPP.state.doc).unrouted===0'))
 test('Connected via move updates attachments on both copper layers',connected_via)
 def mark_move():
  reset("(()=>{const d=CB.blank();d.board={...d.board,width:60,height:45,shape:'rect'};d.settings.grid=1;const p=CB.makePart(d,'diode',30,20);d.parts.push(p);return d;})()");click(30,20);act('mark-reference');act('mark-polarity');before=page.evaluate('JSON.stringify(CB.pads(CBAPP.state.doc))');pos=page.evaluate("(()=>{const b=CB.Edit.markGroups(CBAPP.state.doc,'top').find(m=>m.kind==='polarity').bounds;return{x:(b.minX+b.maxX)/2,y:(b.minY+b.maxY)/2}})()");drag((pos['x'],pos['y']),(pos['x'],pos['y']+3));act('accept-edit');check(page.evaluate('JSON.stringify(CB.pads(CBAPP.state.doc))')==before);check(page.evaluate('CBAPP.state.doc.parts[0].polaritySilk.y===3'));page.screenshot(path=str(IMAGES/'editing-markings.png'))
 test('Dragging printed polarity changes only print geometry, not physical pins',mark_move)
 def mark_fields():
  page.fill('[data-mark-option=size]','1.1');page.locator('[data-mark-option=size]').press('Tab');check(page.evaluate('CBAPP.state.doc.parts[0].polaritySilk.size===1.1'));page.uncheck('[data-mark-option=visible]');check(page.evaluate("CB.Edit.markGroups(CBAPP.state.doc,'top').every(m=>m.kind!=='polarity')"));page.check('[data-mark-option=visible]');act('mark-finish')
 test('Compact print inspector supports size and visibility without pin-role changes',mark_fields)
 def manifest():
  reset();act('export');check(page.locator('.export-review-card').count()==2);page.screenshot(path=str(IMAGES/'editing-export.png'));page.click('#downloadFab');page.wait_for_function('__exports.length>0');r=page.evaluate("async()=>{const b=__exports.at(-1).blob,z=await JSZip.loadAsync(await b.arrayBuffer());return JSON.parse(await z.file('manufacturing-manifest.json').async('string'));}");check(r['valid']);check(r['schema']==5);check('not established' in r['qualification']['independentCAM']);close()
 test('Fabrication ZIP contains revision-bound generated-file review manifest',manifest)
 def stale():
  reset();act('export');page.evaluate("CBAPP.commit('Concurrent change',d=>d.title='Changed title',{copper:false})");before=page.evaluate('__exports.length');page.click('#downloadFab');check(page.evaluate('__exports.length')==before);check('design changed' in page.locator('#toast').inner_text());close()
 test('Export refuses a design changed after its review dialog opened',stale)
 def fab_noedit():
  reset();page.click('[data-view=fabrication]');page.wait_for_timeout(150);before=page.evaluate('JSON.stringify(CBAPP.state.doc)');click(10,10);page.keyboard.press('Delete');page.keyboard.press('r');check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before);check(page.locator('#selectionTools').is_hidden())
 test('Fabrication readback is not an accidental geometry-editing surface',fab_noedit)
 def mobile():
  reset();page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(150);check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'));check(page.locator('#selectionFilter').is_visible());check(page.locator('#connectedDrag').is_visible());page.evaluate("document.querySelector('#toast').hidden=true");page.screenshot(path=str(IMAGES/'editing-mobile.png'));page.set_viewport_size({'width':1500,'height':960})
 test('Narrow workbench keeps editing tools reachable without horizontal page overflow',mobile)
 def conflict():
  boot();reset();page.wait_for_timeout(800);page.evaluate("__store['copperbench.project.v1']='{\"otherTab\":true}'");page.evaluate("CBAPP.commit('Local edit',d=>d.title='Do not overwrite other tab',{copper:false})");page.wait_for_timeout(800);check(page.evaluate("__store['copperbench.project.v1']==='{\"otherTab\":true}'"));check('paused' in page.locator('#saveState').inner_text());act('save');check(page.evaluate('__exports.length>0'))
 test('Autosave detects changed stored data and preserves it; JSON backup still works',conflict)
 def recovery():
  page.click('[data-panel=records]');act('recovery');page.get_by_role('button',name='Download both copies',exact=True).click();check(page.evaluate('__exports.at(-1).name==="copperbench-save-conflict.json"'));page.get_by_role('button',name='Replace local autosave',exact=True).click();check(page.evaluate("JSON.parse(__store['copperbench.project.v1']).title==='Do not overwrite other tab'"));check('Saved locally' in page.locator('#saveState').inner_text())
 test('Explicit recovery exports both copies before enabling replacement autosave',recovery)
 def corrupt():
  boot({'copperbench.project.v1':'{broken'});page.evaluate("CBAPP.commit('Changed open board',d=>d.title='Recovered work',{copper:false})");page.wait_for_timeout(800);check(page.evaluate("__store['copperbench.project.v1']==='{broken'"));check('paused' in page.locator('#saveState').inner_text())
 test('Unreadable startup autosave is not overwritten by later edits',corrupt)
 def quota():
  boot();reset();page.wait_for_timeout(800);old=page.evaluate("__store['copperbench.project.v1']");page.evaluate("__quotaError=true;CBAPP.commit('Quota failure',d=>d.title='Unsaved change',{copper:false})");page.wait_for_timeout(800);check(page.evaluate("__store['copperbench.project.v1']")==old);check('failed' in page.locator('#saveState').inner_text());act('save');check(page.evaluate('__exports.length>0'))
 test('Quota errors keep previous autosave and allow independent JSON backup',quota)
 def cancelled_drag_undo():
  boot();reset();page.evaluate("CBAPP.commit('Title change',d=>d.title='Intermediate revision',{copper:false})");trace_select();p=world(27,10);q=world(27,18);page.mouse.move(p['x'],p['y']);page.mouse.down();page.mouse.move(q['x'],q['y'],steps=3);check(page.evaluate('CBAPP.state.drag?.mode==="trace-edit"'))
  page.keyboard.press('Control+z');page.mouse.up();page.keyboard.press('Escape');check(page.evaluate('CBAPP.state.doc.title==="Edit workbench" && !CBAPP.state.drag && !CBAPP.state.editPreview && CBAPP.state.doc.traces[0].points.length===2'))
 test('Undo during a preview-only drag cancels it without restoring the wrong revision',cancelled_drag_undo)
 def cancelled_drag_commit():
  reset();act('connected-drag');p=world(10,10);q=world(10,20);page.mouse.move(p['x'],p['y']);page.mouse.down();page.mouse.move(q['x'],q['y'],steps=3);check(page.evaluate('CBAPP.state.drag?.mode==="connected-edit"'));page.evaluate("CBAPP.commit('Concurrent edit',d=>d.title='Latest revision',{copper:false})");page.mouse.up();page.keyboard.press('Escape');check(page.evaluate('CBAPP.state.doc.title==="Latest revision" && CBAPP.state.doc.parts[0].y===10 && !CBAPP.state.editPreview'))
 test('A concurrent command safely cancels connected dragging without losing the command',cancelled_drag_commit)
 def cancelled_plane_refill():
  for use_escape in [False,True]:
   reset("(()=>{const d="+PAIR+";CB.Planes.set(d,'bottom',CB.newNet(d,'GND'));d.settings.autoPlanes=false;return d;})()");page.evaluate('CBAPP.state.doc.settings.autoPlanes=true');trace_select();act('edit-width');page.fill('#editWidth','.5');page.get_by_role('button',name='Preview',exact=True).click();check(page.evaluate('!!CBAPP.state.editPreview'));page.wait_for_timeout(550);check(page.evaluate('CBAPP.state.doc.zones.every(z=>!z.fill)'))
   if use_escape:page.keyboard.press('Escape')
   else:act('cancel-edit')
   page.wait_for_function('CBAPP.state.doc.zones.every(z=>z.fill)',timeout=45000);check(page.evaluate('CBAPP.state.doc.traces[0].width===.4'))
 test('Cancelling with Escape or Cancel resumes paused managed-plane refill',cancelled_plane_refill)
 def manufacturing_reimport():
  reset();act('export');page.click('#downloadFab');page.wait_for_function('__exports.length>0');payload=page.evaluate('async()=>Array.from(new Uint8Array(await __exports.at(-1).blob.arrayBuffer()))');close();before=page.evaluate('JSON.stringify(CBAPP.state.doc)');page.set_input_files('#fileInput',{'name':'manufacturing.zip','mimeType':'application/zip','buffer':bytes(payload)});page.wait_for_function('CBAPP.state.fabReference===true && CBAPP.state.view==="fabrication"');check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before)
 test('Manufacturing ZIP with its JSON manifest reopens as CAM reference, not native project',manufacturing_reimport)
 test('Editing uses no external runtime requests or uncaught browser errors',lambda:check(not errors and not [u for u in requests if u.startswith(('http:','https:'))],str(errors)))
 browser.close()
passed=sum(r['pass'] for r in RESULTS);(OUT/'editing-browser-results.json').write_text(json.dumps({'passed':passed,'total':len(RESULTS),'results':RESULTS,'scope':'DOM/canvas/worker; injected storage and captured downloads, not real-origin persistence'},indent=2));print(f'{passed}/{len(RESULTS)} editing browser checks passed');raise SystemExit(0 if passed==len(RESULTS) else 1)

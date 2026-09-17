#!/usr/bin/env python3
"""Real Chromium DOM/canvas/worker tests in an about:blank embedded harness.
The managed environment disallows URL navigation, so storage is an injected
Storage-shaped test double and download blobs are intercepted before navigation.
This does NOT certify file-origin persistence, service workers, Safari, or Firefox.
Requires Python Playwright and Chromium; runtime app needs neither.
"""
from pathlib import Path
from datetime import datetime, timezone
from browser_support import launch_chromium
import json, time, traceback
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'tests/output'
IMAGES=OUTPUT/'images'
IMAGES.mkdir(parents=True,exist_ok=True)
RESULTS=[]
STORE="""seed=>{window.__store=seed;window.__quotaError=false;Object.defineProperty(window,'localStorage',{value:{getItem:k=>window.__store[k]??null,setItem:(k,v)=>{if(window.__quotaError)throw new DOMException('Test storage quota exceeded','QuotaExceededError');window.__store[k]=String(v)},removeItem:k=>delete window.__store[k],clear:()=>window.__store={}}});window.__blobs=new Map;window.__exports=[];const orig=URL.createObjectURL;URL.createObjectURL=function(b){const u=orig.call(URL,b);window.__blobs.set(u,b);return u};document.addEventListener('click',e=>{const a=e.target.closest('a[download]');if(a){e.preventDefault();window.__exports.push({name:a.download,blob:window.__blobs.get(a.href)});}},true);} """
PAIR="""(()=>{let d=CB.blank();d.title='Interaction test';d.board={...d.board,width:40,height:30,shape:'rect'};let n=CB.newNet(d,'LINK');for(let [x,y] of [[8,12],[31,12],[20,23]]){let p=CB.makePart(d,'testpoint',x,y);p.pads[0].net=n;p.label.visible=false;d.parts.push(p);}return d;})()"""
with sync_playwright() as pw:
 browser=launch_chromium(pw)
 page=browser.new_page(viewport={'width':1600,'height':1050},device_scale_factor=1)
 errors=[];requests=[]
 page.set_default_timeout(8000)
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:requests.append(r.url))
 def start(seed=None):
  page.evaluate(STORE,seed or {})
  page.set_content((ROOT/'COPPERBENCH-portable.html').read_text(encoding='utf-8'),wait_until='load')
  page.evaluate("document.addEventListener('click',e=>{let a=e.target.closest('a[download]');if(a){e.preventDefault();__exports.push({name:a.download,blob:__blobs.get(a.href)})}},true)")
  page.wait_for_function('window.CBAPP?.ready && CBAPP.state.checkRevision===CBAPP.state.revision',timeout=15000)
 def act(name):page.locator(f'button[data-action="{name}"]:visible').first.click()
 def close():
  if page.locator('#modal').evaluate('(e)=>e.open'): page.locator('#modalClose').click()
 def reset(expr=PAIR):
  close();page.evaluate('CBAPP.load('+expr+')');page.keyboard.press('Escape')
  page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision',timeout=20000)
 def world(x,y):return page.evaluate('p=>{let r=CBAPP.renderer;r.setup();let q=r.project(p),b=r.canvas.getBoundingClientRect();return {x:q.x+b.left,y:q.y+b.top}}',{'x':x,'y':y})
 def point(x,y):
  p=world(x,y);page.mouse.click(p['x'],p['y']);page.wait_for_timeout(70)
 def drawpts(points):
  for x,y in points:point(x,y)
 def test(name,fn):
  t=time.perf_counter()
  try:fn();RESULTS.append({'name':name,'pass':True,'ms':round((time.perf_counter()-t)*1000)});print('PASS',name,flush=True)
  except Exception as e:
   RESULTS.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,str(e),flush=True);page.screenshot(path=str(OUTPUT/f'failure-{len(RESULTS)}.png'));traceback.print_exc()
 def check(cond,msg='Assertion failed'):
  if not cond:raise AssertionError(msg)
 start()
 test('Boot renders 3D parts and embedded worker completes design checks',lambda:check(page.evaluate('CBAPP.ready && CBAPP.state.doc.parts.length===5 && CBAPP.state.connectivity.unrouted===6')))
 def placement():
  reset();page.click('[data-panel=parts]');page.click('[data-place="r-axial"]');page.keyboard.press('r');point(20,7);page.keyboard.press('Escape')
  check(page.evaluate('CBAPP.state.doc.parts.length===4 && CBAPP.state.doc.parts[3].rotation===90'))
  point(20.32,6.35);page.keyboard.press('f');check(page.evaluate('CBAPP.state.doc.parts[3].side==="bottom"'))
  act('undo');check(page.evaluate('CBAPP.state.doc.parts[3].side==="top"'))
  act('redo');check(page.evaluate('CBAPP.state.doc.parts[3].side==="bottom"'))
 test('Click-to-place, rotate, flip, undo and redo use the real controls',placement)
 def manual():
  reset();page.click('[data-view=copper]');page.select_option('#traceWidth','.8');page.click('[data-tool=trace]');drawpts([(8,12),(31,12)])
  check(page.evaluate('CBAPP.state.doc.traces.length===1 && CBAPP.state.doc.traces[0].width===.8'))
  check(page.evaluate('CB.G.connectivity(CBAPP.state.doc).unrouted===1'))
 test('Manual lead-to-lead trace honors selected width',manual)
 def auto():
  reset();page.click('[data-view=copper]');page.select_option('#traceWidth','.8');page.click('[data-tool=connect]');drawpts([(8,12),(31,12),(20,23)])
  check(page.evaluate('CBAPP.state.selectedPads.length===3'))
  act('autowire');page.wait_for_function('CBAPP.state.routePreview!==null',timeout=15000)
  check(page.evaluate('CBAPP.state.doc.traces.length===0 && CBAPP.state.routePreview.traces.every(t=>t.width===.8)'))
  act('accept-route');page.wait_for_function('CBAPP.state.connectivity?.unrouted===0',timeout=15000)
  check(page.evaluate('CBAPP.state.doc.traces.length>=2'))
  act('undo');check(page.evaluate('CBAPP.state.doc.traces.length===0 && CBAPP.state.doc.nets.length===1'))
 test('Three picked leads preview and commit an actual connected route',auto)
 def starter():
  reset("CB.example('starter')");page.click('[data-panel=nets]')
  ids=page.evaluate('CBAPP.state.doc.nets.map(n=>n.id)')
  for nid in ids:
   page.click('[data-net-route="'+nid+'"]');page.wait_for_function('CBAPP.state.routePreview!==null',timeout=20000)
   check(page.evaluate('CBAPP.state.routePreview.failures.length===0'),str(page.evaluate('CBAPP.state.routePreview.failures')))
   act('accept-route')
  page.wait_for_function('CBAPP.state.connectivity?.unrouted===0',timeout=20000)
  check(page.evaluate('CB.G.findings(CBAPP.state.doc).filter(f=>f.severity==="error").length===0'))
  page.click('[data-view=bench]');page.keyboard.press('Escape');page.wait_for_timeout(300)
  page.evaluate("document.getElementById('toast').hidden=true");page.screenshot(path=str(IMAGES/'routed-bench.png'))
  routed=page.evaluate('CBAPP.state.doc');(OUTPUT/'little-light-routed.json').write_text(json.dumps(routed,indent=2))
  page.click('[data-view=copper]');page.evaluate("document.getElementById('toast').hidden=true");page.screenshot(path=str(IMAGES/'copper.png'))
 test('Starter board routes all three nets without blocking geometry findings',starter)
 def native():
  act('save');page.wait_for_timeout(100)
  info=page.evaluate('async()=>({name:__exports.at(-1).name,data:JSON.parse(await __exports.at(-1).blob.text())})')
  check(info['name'].endswith('.json'));check(len(info['data']['traces'])>=3)
  file={'name':'roundtrip.json','mimeType':'application/json','buffer':json.dumps(info['data']).encode()}
  page.set_input_files('#fileInput',file);page.wait_for_selector('#modal[open]');page.get_by_role('button',name='Open this board',exact=True).click()
  check(page.evaluate('CBAPP.state.doc.traces.length')==len(info['data']['traces']))
 test('Native JSON export blob and reviewed file-input import round-trip',native)
 def invalid():
  old=page.evaluate('CBAPP.state.doc.id')
  page.set_input_files('#fileInput',{'name':'bad.json','mimeType':'application/json','buffer':b'{"app":"COPPERBENCH","schema":900}'})
  page.wait_for_selector('#modal[open]');check('Import stopped' in page.locator('#modalTitle').inner_text());check(page.evaluate('CBAPP.state.doc.id')==old);close()
 test('Unsupported native import leaves the existing board unchanged',invalid)
 def fab():
  golden=json.loads((ROOT/'examples/golden-coupon.json').read_text(encoding='utf-8'));reset(json.dumps(golden))
  page.click('[data-view=fabrication]');check(page.evaluate('Object.keys(CBAPP.state.fabData).length>=9'))
  page.wait_for_timeout(300);page.evaluate("document.getElementById('toast').hidden=true");page.screenshot(path=str(IMAGES/'fabrication.png'))
  act('export');page.wait_for_selector('#downloadFab');check(page.is_enabled('#downloadFab'))
  page.click('#downloadFab');page.wait_for_function('__exports.at(-1)?.name.endsWith("fabrication.zip")')
  info=page.evaluate('async()=>{let z=await JSZip.loadAsync(await __exports.at(-1).blob.arrayBuffer());return Object.keys(z.files)}')
  check('board-F_Cu.gbr' in info and 'board-NPTH.drl' in info and 'READ-ME.txt' in info);close()
 test('Fabrication reads actual files and produces a complete manufacturing ZIP blob',fab)
 def blocked_export():
  reset();act('export');page.wait_for_selector('#downloadFab');check(not page.is_enabled('#downloadFab'));page.check('#diagnosticExport');check(page.is_enabled('#downloadFab'));close()
 test('Unrouted boards require explicit diagnostic-export override',blocked_export)
 def board_resize():
  reset();before=page.evaluate('JSON.stringify(CBAPP.state.doc.parts)');page.click('[data-panel=board]');page.fill('[data-board=width]','54');page.locator('[data-board=width]').press('Tab')
  check(page.evaluate('CBAPP.state.doc.board.width')==54);check(page.evaluate('JSON.stringify(CBAPP.state.doc.parts)')==before)
  page.click('[data-tool=outline]');drawpts([(1,1),(49,1),(49,28),(1,28)]);page.keyboard.press('Enter');check(page.evaluate('CBAPP.state.doc.board.shape')=='polygon')
 test('Board size and polygon tools edit boundaries without scaling footprints',board_resize)
 def text_and_shape():
  reset();page.click('[data-panel=silk]');page.click('[data-tool=text]');point(9,6);page.fill('#silkText','GSG / TEST');page.get_by_role('button',name='Place text',exact=True).click();check(page.evaluate('CBAPP.state.doc.art[0].text')=='GSG / TEST')
  page.click('[data-tool=silk-rect]');a=world(6,5);b=world(26,9);page.mouse.move(a['x'],a['y']);page.mouse.down();page.mouse.move(b['x'],b['y'],steps=8);page.mouse.up();check(page.evaluate('CBAPP.state.doc.art.some(a=>a.kind==="rect")'))
 test('Silkscreen text and drag-drawn shapes create editable manufacturing geometry',text_and_shape)
 def images():
  from PIL import Image,ImageDraw
  import io
  im=Image.new('RGB',(240,100),'white');di=ImageDraw.Draw(im);di.rectangle((15,15,65,85),fill='black');di.ellipse((95,15,165,85),fill='black');di.polygon([(190,80),(215,15),(239,80)],fill='black');out=io.BytesIO();im.save(out,format='PNG')
  page.set_input_files('#imageInput',{'name':'local-logo.png','mimeType':'image/png','buffer':out.getvalue()});page.wait_for_selector('#imageWidth')
  check('vector rectangles' in page.locator('#imageInfo').inner_text());page.evaluate("document.getElementById('toast').hidden=true");page.screenshot(path=str(IMAGES/'silkscreen.png'))
  page.get_by_role('button',name='Place converted image',exact=True).click()
  check(page.evaluate('CBAPP.state.doc.art.some(a=>a.kind==="image"&&a.rects.length>0)&&CBAPP.state.doc.assets.length===1'))
 test('Image conversion embeds its original and emits real silkscreen rectangles',images)
 def malicious_svg():
  before=page.evaluate('CBAPP.state.doc.art.length')
  page.set_input_files('#imageInput',{'name':'unsafe.svg','mimeType':'image/svg+xml','buffer':b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'});page.wait_for_timeout(200)
  check(page.evaluate('CBAPP.state.doc.art.length')==before);check('scripts' in page.locator('#toast').inner_text())
 test('Executable SVG is rejected before image conversion',malicious_svg)
 def footprint():
  reset();page.click('[data-panel=parts]');act('footprint');page.fill('#fp-name','My bench connector');page.fill('#fp-count','5');page.get_by_role('button',name='Add to parts drawer',exact=True).click();point(20,6);page.keyboard.press('Escape');check(page.evaluate('CBAPP.state.doc.parts.some(p=>p.name==="My bench connector"&&p.pads.length===5)'))
 test('Custom footprint wizard produces a placeable self-contained part',footprint)
 def zone():
  reset();page.click('[data-view=copper]');page.click('[data-tool=zone]');drawpts([(4,7),(35,7),(35,26),(4,26)]);page.keyboard.press('Enter');page.wait_for_selector('#zoneNet');page.select_option('#zoneNet',page.evaluate('CBAPP.state.doc.nets[0].id'));page.uncheck('#zoneThermal');page.get_by_role('button',name='Create zone',exact=True).click();page.wait_for_function('CBAPP.state.doc.zones[0]?.fill!==null',timeout=20000)
  check(page.evaluate('CBAPP.state.doc.zones[0].fill.rects.length>0'));check(page.evaluate('CB.G.connectivity(CBAPP.state.doc).unrouted')==0)
  page.evaluate("document.getElementById('toast').hidden=true");page.screenshot(path=str(IMAGES/'pour.png'))
 test('Copper-zone drawing invokes worker fill and establishes physical connectivity',zone)
 def pin_table():
  reset();page.click('[data-panel=nets]');act('connections-table');page.fill('#pinSearch','TP1');check(page.locator('#pinRows tr').count()==1);page.check('#pinRows input[type=checkbox]');check(page.evaluate('CBAPP.state.selectedPads.length')==1);close()
 test('Searchable pin table provides an alternative to picking small pads',pin_table)
 def baseline():
  page.click('[data-panel=records]');act('baseline');# direct capture action
  if page.locator('#modal').evaluate('(e)=>e.open'):
   btn=page.locator('#modalFooter button.primary');btn.click()
  check(page.evaluate('!!CBAPP.state.doc.baseline'))
  page.evaluate('CBAPP.commit("Test change",d=>d.parts[0].x+=1)');act('compare');check(page.locator('#modal').evaluate('(e)=>e.open'));close();act('report');check('Not manufacturer-approved' in page.locator('#modalBody').inner_text());page.get_by_role('button',name='Save HTML report',exact=True).click();check(page.evaluate('__exports.at(-1).name.endsWith("report.html")'));close()
 test('Baseline comparison and downloadable review report work',baseline)
 def storage():
  page.wait_for_timeout(700);check(page.evaluate('__store["copperbench.project.v1"]!==undefined'))
  saved=page.evaluate('__store');saved_doc=json.loads(saved['copperbench.project.v1']);new=browser.new_page(viewport={'width':1600,'height':1050});new.evaluate(STORE,saved);new.set_content((ROOT/'COPPERBENCH-portable.html').read_text(encoding='utf-8'));new.wait_for_function('CBAPP?.ready');check(new.evaluate('CBAPP.state.doc.id')==saved_doc['id']);new.close()
  page.evaluate('__quotaError=true; CBAPP.commit("Quota test",d=>d.title="Quota test")');page.wait_for_timeout(750);check('failed' in page.locator('#saveState').inner_text().lower() or 'save json' in page.locator('#saveState').inner_text().lower(),page.locator('#saveState').inner_text());act('save');check(page.evaluate('__exports.at(-1).name.endsWith(".json")'));page.evaluate('__quotaError=false')
 test('Autosave/reload and quota-failure recovery work with the storage test double',storage)
 def themes_mobile():
  reset("CB.example('mixed')");act('theme');check(page.evaluate('document.documentElement.dataset.theme')=='dark');page.evaluate("document.getElementById('toast').hidden=true");page.screenshot(path=str(IMAGES/'dark.png'));act('theme');check(page.evaluate('document.documentElement.dataset.theme')=='contrast');page.evaluate("document.getElementById('toast').hidden=true");page.screenshot(path=str(IMAGES/'high-contrast.png'))
  page.set_viewport_size({'width':430,'height':932});page.wait_for_timeout(300);act('fit');page.evaluate("document.getElementById('toast').hidden=true");page.screenshot(path=str(IMAGES/'mobile.png'));check(page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1'))
  page.set_viewport_size({'width':1600,'height':1050});act('theme')
 test('Dark/high-contrast themes and narrow responsive layout avoid page overflow',themes_mobile)
 def no_network():
  check(not [r for r in requests if r.startswith('http:') or r.startswith('https:')],str(requests));check(not errors,str(errors))
 test('No external asset requests or uncaught application exceptions',no_network)
 browser.close()
summary={'date':datetime.now(timezone.utc).isoformat(),'environment':'Chromium, about:blank embedded portable HTML. Storage test double and intercepted download blobs; no real-origin persistence or service-worker validation in this suite.','passed':sum(r['pass'] for r in RESULTS),'total':len(RESULTS),'results':RESULTS,'uncaught':errors,'network_requests':requests}
(OUTPUT/'browser-results.json').write_text(json.dumps(summary,indent=2));print(json.dumps({k:summary[k] for k in ['passed','total']},indent=2))
raise SystemExit(0 if all(r['pass'] for r in RESULTS) else 1)

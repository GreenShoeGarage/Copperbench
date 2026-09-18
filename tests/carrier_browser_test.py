#!/usr/bin/env python3
"""v1.5 actual Chromium controls/canvas/worker tests. In-memory storage and
captured download blobs; no native-file, CAM, manufacturing or fit claim."""
from pathlib import Path
import json,time,traceback,sys
from playwright.sync_api import sync_playwright
from browser_support import launch_chromium
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';IMAGES=OUT/'images';IMAGES.mkdir(parents=True,exist_ok=True);results=[]
STORE="""()=>{window.__store={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>__store[k]??null,setItem:(k,v)=>__store[k]=String(v),removeItem:k=>delete __store[k]}});window.__blobs=new Map;window.__exports=[];const orig=URL.createObjectURL;URL.createObjectURL=function(b){const u=orig.call(URL,b);__blobs.set(u,b);return u};}"""
with sync_playwright() as pw:
 browser=launch_chromium(pw);page=browser.new_page(viewport={'width':1600,'height':1050},device_scale_factor=1);page.set_default_timeout(10000);errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url));page.evaluate(STORE);page.set_content((ROOT/'COPPERBENCH-portable.html').read_text(),wait_until='load');page.evaluate("document.addEventListener('click',e=>{const a=e.target.closest('a[download]');if(a){e.preventDefault();__exports.push({name:a.download,blob:__blobs.get(a.href)})}},true)");page.wait_for_function('CBAPP?.ready && CBAPP.state.checkRevision===CBAPP.state.revision',timeout=20000)
 def check(c,msg='Assertion failed'):
  if not c:raise AssertionError(msg)
 def test(name,fn):
  t=time.perf_counter()
  try:fn();results.append({'name':name,'pass':True,'ms':round((time.perf_counter()-t)*1000)});print('PASS',name,flush=True)
  except Exception as e:
   results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,e,flush=True);traceback.print_exc();page.screenshot(path=str(IMAGES/f'carrier-failure-{len(results)}.png'))
 def act(name):page.locator(f'button[data-action="{name}"]:visible').first.click()
 def close():
  if page.locator('#modal').evaluate('el=>el.open'):page.locator('#modalClose').click()
 def done():page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision',timeout=30000)
 def filled():page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision && !CBAPP.state.job && !CBAPP.state.planeFilling && CBAPP.state.doc.zones.every(z=>z.fill)',timeout=60000)
 def reset(expr='CB.blank()'):
  close();page.evaluate('CBAPP.load('+expr+')');page.keyboard.press('Escape');page.locator('[data-panel=parts]').click();done()
 def point(x,y):
  q=page.evaluate('p=>{const r=CBAPP.renderer;r.setup();const q=r.project(p),b=r.canvas.getBoundingClientRect();return{x:q.x+b.left,y:q.y+b.top}}',{'x':x,'y':y});page.mouse.click(q['x'],q['y']);page.wait_for_timeout(80)
 def select_first():
  close();page.keyboard.press('Escape');page.locator('[data-view=copper]').click();p=page.evaluate('CB.pads(CBAPP.state.doc)[0]');point(p['x'],p['y']);page.locator('[data-view=bench]').click()
 def new(family='pico2-w',role='carrier'):
  close();page.locator('[data-panel=parts]').click();act('carrier-catalog');page.locator(f'[data-family-choice="{family}"]').click();page.select_option('#platformRole',role);page.get_by_role('button',name='Start new board',exact=True).click();done()
 def picker():
  reset();act('carrier-catalog');check(page.locator('[data-family-choice]').count()==12);check(page.locator('[data-family-choice=pico2]').get_attribute('aria-pressed')=='true');check(page.locator('#platformRole').input_value()=='carrier');check('40 plated contacts' in page.locator('#platformSummary').inner_text());page.screenshot(path=str(IMAGES/'carrier-picker.png'));close()
 test('Controller picker is visible, has twelve families, and defaults to Pico 2 carrier',picker)
 def all_new():
  for f,count in [('pico',40),('pico2',40),('pico-w',40),('pico2-w',40),('nano-classic',30),('esp32-devkitc-v4',38),('feather-classic',28),('xiao-rp2040',14),('xiao-esp32c3',14)]:
   new(f);check(page.evaluate('CBAPP.state.doc.parts[0].pads.length')==count);check(page.evaluate('CBAPP.state.doc.parts[0].locked'));check(page.evaluate('CBAPP.state.doc.parts[0].side')=='top');check(page.locator('[data-action=carrier-details]').is_visible())
 test('Every new variant creates a locked, routable, correctly sized header template',all_new)
 def no_holes():
  act('carrier-catalog');page.locator('[data-family-choice="xiao-rp2040"]').click();check(page.locator('#platformHoles').is_disabled());check(not page.locator('#platformHoles').is_checked());page.locator('[data-family-choice="pico2"]').click();check(not page.locator('#platformHoles').is_disabled());check(page.locator('#platformHoles').is_checked());close()
 test('No-hole hosts cannot accidentally enable invented mounting drills',no_holes)
 def addon():
  new('feather-classic','addon');check(page.evaluate("CBAPP.state.doc.parts[0].side==='bottom'"));check(page.evaluate("CB.pads(CBAPP.state.doc).find(a=>a.pin==='L.16').signal==='FREE / VARIANT SPECIFIC'"));check(page.locator('[data-action=carrier-details]').is_visible())
 test('FeatherWing-style add-on exposes the bottom mating face and variant-specific FREE contact',addon)
 def place():
  reset();before=page.evaluate('JSON.stringify(CBAPP.state.doc.board)');act('carrier-catalog');page.locator('[data-family-choice="xiao-rp2040"]').click();page.get_by_role('button',name='Place headers on current board',exact=True).click();point(40,28);page.keyboard.press('Escape');check(page.evaluate('CBAPP.state.doc.parts[0].carrier.model').startswith('Seeed XIAO RP2040'));check(page.evaluate('JSON.stringify(CBAPP.state.doc.board)')==before)
 test('Place-on-current-board preserves the boundary and adds the selected exact interface',place)
 def labels():
  new('esp32-devkitc-v4');check('GPIO36 / VP / INPUT ONLY' in page.locator('#inspectorContent').inner_text());check('GPIO6 / FLASH RESERVED' in page.locator('#inspectorContent').inner_text());act('carrier-details');check('WROOM-32E' in page.locator('#modalBody').inner_text());check(page.locator('#carrierEnforce').is_checked());check(page.locator('[data-carrier-region]').count()==8);close()
 test('Inspector shows functional contact labels, source model and editable RF/access regions',labels)
 def clearances():
  new();act('carrier-details');page.locator('#carrierGap').fill('6.2');page.locator('[data-carrier-region="1"][data-region-key="w"]').fill('8.2');page.get_by_role('button',name='Apply clearances',exact=True).click();done();check(page.evaluate('CBAPP.state.doc.parts[0].carrier.stackGap')==6.2);check(page.evaluate('CBAPP.state.doc.parts[0].carrier.regions[1].w')==8.2);act('undo');check(page.evaluate('CBAPP.state.doc.parts[0].carrier.stackGap')==8.5);check(page.evaluate('CBAPP.state.doc.parts[0].carrier.regions[1].w')==9)
 test('Guard dimensions and stack-gap edits are one undoable operation',clearances)
 def reject_override():
  select_first();act('carrier-details');page.locator('#carrierEnforce').uncheck();page.get_by_role('button',name='Apply clearances',exact=True).click();check(page.locator('#modal').evaluate('el=>el.open'));check('reason' in page.locator('#toast').inner_text());check(page.evaluate('CBAPP.state.doc.parts[0].carrier.enforceAntenna'));page.locator('#carrierReason').fill('External antenna redesign reviewed separately');page.get_by_role('button',name='Apply clearances',exact=True).click();done();check(page.evaluate('CB.keepouts(CBAPP.state.doc).length')==0);check(page.evaluate("CBAPP.state.findings.some(f=>f.code==='carrier-rf-disabled')"));act('undo');done()
 test('RF override requires a recorded reason; the accepted override remains a warning',reject_override)
 def display():
  select_first();before=page.evaluate('JSON.stringify(CBAPP.exportFiles())');act('carrier-details');page.locator('#carrierShow').uncheck();page.get_by_role('button',name='Apply clearances',exact=True).click();done();check(page.evaluate('CB.keepouts(CBAPP.state.doc).length')==1);check(page.evaluate('JSON.stringify(CBAPP.exportFiles())')==before);act('undo');done()
 test('Hiding overlays does not disable guards or alter manufacturing output',display)
 def transforms():
  select_first();page.locator('[data-prop=locked]').uncheck();before=page.evaluate('JSON.stringify(CB.keepouts(CBAPP.state.doc)[0].points)');act('rotate');done();check(page.evaluate('JSON.stringify(CB.keepouts(CBAPP.state.doc)[0].points)')!=before);act('flip');done();check(page.evaluate('CBAPP.state.doc.parts[0].side')=='bottom');check(page.evaluate('CB.keepouts(CBAPP.state.doc)[0].layer')=='both')
 test('Rotate and flip controls transform the attached guard without changing its two-face protection',transforms)
 def worker_planes():
  new();page.evaluate("CBAPP.commit('Plane test',d=>{let n=CB.newNet(d,'GND');d.parts[0].pads.find(a=>a.number==='3').net=n;CB.Planes.set(d,'top',n);CB.Planes.set(d,'bottom',n)})");filled();check(page.evaluate('CBAPP.state.doc.zones.every(z=>z.fill?.area>100)'));check(page.evaluate('(()=>{const d=CBAPP.state.doc,k=CB.keepouts(d)[0];return d.zones.every(z=>z.fill.rects.every(r=>CB.G.polyDist(CB.G.rect(r.x,r.y,r.w,r.h),k.points)>.003))})()'));page.locator('[data-view=copper]').click();page.screenshot(path=str(IMAGES/'carrier-plane.png'))
 test('Actual worker refills both plane faces around the attached RF exclusion',worker_planes)
 def via_guard():
  page.locator('[data-tool=via]:visible').first.click();b=page.evaluate('CB.G.bounds(CB.keepouts(CBAPP.state.doc)[0].points)');point((b['minX']+b['maxX'])/2,b['minY']+2);check(page.evaluate('CBAPP.state.doc.vias.length')==0);check('keepout' in page.locator('#toast').inner_text().lower() or 'blocked' in page.locator('#toast').inner_text().lower());page.keyboard.press('Escape')
 test('Visible Via tool refuses to place a via inside the RF guard',via_guard)
 def json_backup():
  act('save');page.wait_for_timeout(150);saved=page.evaluate("async()=>JSON.parse(await __exports.filter(e=>e.name.endsWith('.json')).at(-1).blob.text())");check(saved['schema']==5);check(saved['parts'][0]['carrier']['enforceAntenna']);check(saved['parts'][0]['carrier']['regions'][1]['kind']=='antenna');check(len(saved['zones'])==2)
  page.locator('[data-panel=records]').click();act('project-zip');page.wait_for_function("__exports.some(e=>e.name.endsWith('-project.zip'))");z=page.evaluate("async()=>{const b=__exports.filter(e=>e.name.endsWith('-project.zip')).at(-1).blob,z=await JSZip.loadAsync(await b.arrayBuffer());return {readme:await z.file('README.txt').async('string'),schema:JSON.parse(await z.file('project.json').async('string')).schema}}");check(z['schema']==5 and 'schema-5' in z['readme']);page.locator('[data-panel=parts]').click()
 test('Saved JSON and project ZIP retain schema 5, host metadata, guards and planes',json_backup)
 def kicad_export():
  act('export');act('export-kicad');check('independent KiCad keepouts' in page.locator('#modalBody').inner_text());page.get_by_role('button',name='Export geometry',exact=True).click();page.wait_for_timeout(100);text=page.evaluate("async()=>__exports.filter(e=>e.name.endsWith('.kicad_pcb')).at(-1).blob.text()");check(text.count('(keepout ')==2);check('(tracks not_allowed)' in text);close()
 test('KiCad export discloses metadata loss and includes two independent keepout zones',kicad_export)
 def demo_screenshot():
  new();page.evaluate("CBAPP.commit('Reference illustration',d=>{d.title='Pico 2 W · carrier workbench';let n=CB.newNet(d,'GND');d.parts[0].pads.find(a=>a.number==='3').net=n;CB.Planes.set(d,'bottom',n)})");filled();page.locator('[data-view=bench]').click();page.locator('[data-side=bottom]').click();page.locator('#tilt').fill('20');page.locator('#tilt').dispatch_event('input');page.locator('[data-side=top]').click();page.screenshot(path=str(IMAGES/'carrier-workbench.png'));act('carrier-details');page.screenshot(path=str(IMAGES/'carrier-clearances.png'));close()
 test('Bench and clearance inspector render the controller and its separate reference geometry',demo_screenshot)
 def mobile():
  page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(250);act('files');act('examples');act('carrier-catalog');page.locator('[data-family-choice="xiao-esp32c3"]').click();check(page.locator('#platformRole').input_value()=='carrier');check(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'));check(page.locator('#modal').bounding_box()['width']<=390);page.screenshot(path=str(IMAGES/'carrier-mobile.png'));close();page.set_viewport_size({'width':1600,'height':1050});page.wait_for_timeout(200)
 test('Controller selection and template workflow fit a 390 px viewport',mobile)
 def health():check(not errors,'Uncaught browser errors: '+str(errors));check(not [u for u in requests if u.startswith(('https://','http://'))],str(requests))
 test('No uncaught browser errors or external runtime dependencies',health)
 browser.close()
(OUT/'carrier-browser-results.json').write_text(json.dumps({'passed':sum(r['pass'] for r in results),'total':len(results),'results':results,'browser':'Chromium','storage':'simulated','downloads':'captured blobs'},indent=2));print(f"{sum(r['pass'] for r in results)}/{len(results)} carrier browser checks passed.");sys.exit(0 if all(r['pass'] for r in results) else 1)

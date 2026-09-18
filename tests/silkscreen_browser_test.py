#!/usr/bin/env python3
"""Polarity UI and actual Gerber rendering regressions in Chromium.
Storage and download navigation are explicit test doubles, not persistence tests.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys, time, traceback
from playwright.sync_api import sync_playwright
from browser_support import launch_chromium
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'tests/output'; IMAGES=OUT/'images'; IMAGES.mkdir(parents=True,exist_ok=True)
FIX=OUT/'fixtures/silkscreen'; DOC=json.loads((FIX/'all-tools/project.json').read_text()); results=[]
STORE="""()=>{window.__store={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>__store[k]??null,setItem:(k,v)=>__store[k]=String(v),removeItem:k=>delete __store[k]}});window.__blobs=new Map;window.__exports=[];const orig=URL.createObjectURL;URL.createObjectURL=b=>{const u=orig.call(URL,b);__blobs.set(u,b);return u;};}"""
with sync_playwright() as pw:
 browser=launch_chromium(pw);page=browser.new_page(viewport={'width':1600,'height':1050},device_scale_factor=1);page.set_default_timeout(8000)
 errors=[];requests=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
 page.evaluate(STORE);page.set_content((ROOT/'COPPERBENCH-portable.html').read_text(),wait_until='load')
 page.evaluate("document.addEventListener('click',e=>{const a=e.target.closest('a[download]');if(a){e.preventDefault();__exports.push({name:a.download,blob:__blobs.get(a.href)});}},true)")
 page.wait_for_function('CBAPP?.ready && CBAPP.state.checkRevision===CBAPP.state.revision',timeout=30000)
 def check(value,message='Assertion failed'):
  if not value:raise AssertionError(message)
 def act(name):page.locator(f'button[data-action="{name}"]:visible').first.click()
 def close():
  if page.locator('#modal').evaluate('(e)=>e.open'):page.locator('#modalClose').click()
 def stable():page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision && !CBAPP.state.job',timeout=30000)
 def reset(doc=DOC):
  close();page.keyboard.press('Escape');page.evaluate('d=>CBAPP.load(d)',doc);page.keyboard.press('Escape')
  page.locator('[data-view=bench]').click();page.locator('[data-side=top]').click();stable()
  page.evaluate("")
 def point(x,y):
  q=page.evaluate('p=>{const r=CBAPP.renderer;r.setup();const q=r.project(p),b=r.canvas.getBoundingClientRect();return{x:q.x+b.left,y:q.y+b.top};}',{'x':x,'y':y})
  page.mouse.click(q['x'],q['y']);return q
 def choose(i=0):
  # Use the component body, not the pin or a testing-only selection action.
  p=page.evaluate('i=>{const p=CBAPP.state.doc.parts[i];return {x:p.x,y:p.y}}',i);point(p['x'],p['y'])
  page.wait_for_selector('#inspector [data-action=polarity]')
 def dialog(i=0):choose(i);act('polarity');page.wait_for_selector('#polarityPrint')
 def apply():page.get_by_role('button',name='Apply polarity labels',exact=True).click();stable()
 def screenshot(name):
  page.mouse.move(1590,1030);page.evaluate("document.getElementById('toast').hidden=true;document.getElementById('tooltip').hidden=true")
  page.screenshot(path=str(IMAGES/name))
 def pixel(x,y):
  return page.evaluate('p=>{const r=CBAPP.renderer;r.draw();const q=r.project(p),c=r.ctx;return Array.from(c.getImageData(Math.round(q.x*r.dpr),Math.round(q.y*r.dpr),1,1).data);}',{'x':x,'y':y})
 def diff(a,b):return sum(abs(x-y) for x,y in zip(a[:3],b[:3]))
 def test(name,fn):
  t=time.perf_counter()
  try:fn();results.append({'name':name,'pass':True,'ms':round((time.perf_counter()-t)*1000)});print('PASS',name,flush=True)
  except Exception as e:results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,e,flush=True);page.screenshot(path=str(IMAGES/f'silkscreen-failure-{len(results)}.png'));traceback.print_exc()
 def builtins():
  reset();marks=page.evaluate('CBAPP.renderer.polarityHitLabels');check(len(marks)==8);check({m['label'] for m in marks}=={'Anode','Cathode','Positive','Negative'})
  choose();text=page.locator('#inspector').inner_text();check('Anode' in text and 'Cathode' in text);screenshot('polarity-workbench.png')
 test('Recognizable diode, LED and capacitor terminals have badges and full inspector names',builtins)
 def hover():
  reset();choose();q=page.evaluate('()=>{const r=CBAPP.renderer;r.draw();const a=r.polarityHitLabels.find(a=>a.role==="cathode"),b=r.canvas.getBoundingClientRect();return{x:a.x+b.left,y:a.y+b.top,pad:a.padId}}')
  page.mouse.move(q['x'],q['y']);page.wait_for_function('document.getElementById("tooltip").textContent.includes("Cathode")');check(page.evaluate('CBAPP.state.hoverPad')==q['pad'])
 test('Hovering the K badge identifies the actual cathode lead rather than a nearby body',hover)
 def click_badge():
  reset();page.locator('[data-tool=connect]').first.click();q=page.evaluate('()=>{const r=CBAPP.renderer;r.draw();const a=r.polarityHitLabels.find(a=>a.role==="anode"),b=r.canvas.getBoundingClientRect();return{x:a.x+b.left,y:a.y+b.top,pad:a.padId}}')
  page.mouse.click(q['x'],q['y']);check(page.evaluate('CBAPP.state.selectedPads')==[q['pad']]);page.keyboard.press('Escape')
 test('Clicking an A badge in connection mode selects that exact anode pad',click_badge)
 def table():
  reset();page.locator('[data-panel=nets]').click();act('connections-table');page.fill('#pinSearch','cathode');check(page.locator('#pinRows tr').count()==3);check('Cathode' in page.locator('#pinRows').inner_text());close()
 test('Pin table searches by full electrical role, not just pin number',table)
 def hide():
  reset();dialog();check(page.locator('[data-polarity-pad="0"]').input_value()=='cathode');before=page.evaluate('CB.silkStrokes(CBAPP.state.doc).length')
  page.uncheck('#polarityPrint');apply();check(page.evaluate('CB.silkStrokes(CBAPP.state.doc).length')<before);check(page.evaluate('CBAPP.renderer.polarityHitLabels.filter(a=>a.padId.startsWith(CBAPP.state.doc.parts[0].id+":")).length')==2)
  act('undo');stable();check(page.evaluate('CB.polarityOptions(CBAPP.state.doc.parts[0]).visible'));act('redo');stable();check(not page.evaluate('CB.polarityOptions(CBAPP.state.doc.parts[0]).visible'))
 test('Printing can be disabled without losing editor identification; undo and redo work',hide)
 def custom():
  d=page.evaluate('(()=>{let d=CB.blank();d.parts.push(CB.makePart(d,"header2",25,25));return d;})()');reset(d)
  before=page.evaluate('CBAPP.state.doc.parts[0].pads.map(a=>[a.number,a.net,a.x,a.y])');dialog();page.select_option('[data-polarity-pad="0"]','anode');page.select_option('[data-polarity-pad="1"]','cathode');apply()
  check(page.evaluate('CBAPP.state.doc.parts[0].pads.map(a=>[a.number,a.net,a.x,a.y])')==before);check(page.evaluate('CBAPP.state.doc.parts[0].pads.map(a=>a.polarity)')==['anode','cathode'])
 test('Numeric/custom pins gain explicit roles without renumbering or copper/net changes',custom)
 def dimensions():
  reset();dialog();page.fill('#polaritySize','1.8');page.fill('#polarityGap','1.1');page.fill('#polarityX','.5');page.fill('#polarityY','1.5');apply()
  o=page.evaluate('CBAPP.state.doc.parts[0].polaritySilk');check(o=={'visible':True,'size':1.8,'gap':1.1,'x':.5,'y':1.5});act('save')
  raw=page.evaluate('async()=>await __exports.at(-1).blob.text()');d=json.loads(raw);check(d['schema']==5 and d['parts'][0]['polaritySilk']==o)
  page.locator('#fileInput').set_input_files({'name':'polarized.json','mimeType':'application/json','buffer':raw.encode()});page.get_by_role('button',name='Open this board',exact=True).click();stable()
  check(page.evaluate('CBAPP.state.doc.parts[0].polaritySilk')==o)
 test('Printable size/gap/offsets survive real JSON download and file-input import',dimensions)
 def flip():
  reset();choose();before=page.evaluate('CBAPP.state.doc.parts[0].pads.map(a=>[a.number,a.net,a.polarity])');act('rotate');act('flip');stable()
  check(page.evaluate('CBAPP.state.doc.parts[0].pads.map(a=>[a.number,a.net,a.polarity])')==before);check(page.evaluate('CB.polarityMarks(CBAPP.state.doc.parts[0]).every(m=>m.layer==="bottom")'))
 test('Rotation and side changes retain terminal identity and move printed symbols to the correct face',flip)
 def default_silk():
  reset();page.locator('[data-view=fabrication]').click();check(page.evaluate('CBAPP.state.fabLayers.includes("board-F_Silkscreen.gbr")'));check(page.locator('[data-action=fab-silk-top]').is_visible())
 test('Fabrication defaults include silk and expose both silk-only inspection controls',default_silk)
 def top():
  reset();page.locator('[data-view=fabrication]').click();act('fab-silk-top');check(page.evaluate('CBAPP.state.fabLayers.length===2 && CBAPP.state.side==="top"'))
  ink=pixel(40,12);empty=pixel(40,11);check(diff(ink,empty)>40,f'Expected actual top ink: {ink}, {empty}')
  screenshot('silkscreen-gerber-top.png')
 test('Final top Gerber visibly retains the on-board line after all clear operations',top)
 def bottom():
  reset();page.locator('[data-view=fabrication]').click();act('fab-silk-bottom');check(page.evaluate('CBAPP.state.side==="bottom" && CBAPP.state.fabLayers.includes("board-B_Silkscreen.gbr")'))
  p=page.evaluate('()=>{const s=CB.silkStrokes(CBAPP.state.doc).find(s=>s.layer==="bottom");return {x:(s.points[0].x+s.points[1].x)/2,y:(s.points[0].y+s.points[1].y)/2}}')
  ink=pixel(p['x'],p['y']);empty=pixel(5,30);check(diff(ink,empty)>40,f'Expected actual bottom ink: {ink}, {empty}');screenshot('silkscreen-gerber-bottom.png')
 test('Final bottom Gerber retains readable component-side markings in the flipped view',bottom)
 def legacy():
  reset();page.locator('[data-view=fabrication]').click();act('fab-silk-top');page.evaluate('t=>{CBAPP.state.fabData["board-F_Silkscreen.gbr"]=CB.M.readGerber(t);}',(FIX/'legacy-frame.gbr').read_text())
  check(diff(pixel(20,10),pixel(20,11))<6,'Viewer still incorrectly treats clear contours as a hole')
 test('Viewer now correctly shows the old nested clear-frame reproducer as completely blank',legacy)
 def nested_dark():
  reset();page.locator('[data-view=fabrication]').click();act('fab-silk-top');page.evaluate('t=>{CBAPP.state.fabData["board-F_Silkscreen.gbr"]=CB.M.readGerber(t);}',(FIX/'union-contours.gbr').read_text())
  check(diff(pixel(15,15),pixel(50,40))>40,'Viewer incorrectly punched a hole through overlapping dark contours')
 test('Viewer unions overlapping dark contours even with reversed winding',nested_dark)
 def exported():
  reset();act('export');check('top:' in page.locator('#silkExportInventory').inner_text());check('bottom:' in page.locator('#silkExportInventory').inner_text())
  if page.locator('#diagnosticExport').count():page.check('#diagnosticExport')
  previous=page.evaluate('__exports.length');page.locator('#downloadFab').click();page.wait_for_function(f'__exports.length>{previous}')
  files=page.evaluate('async()=>{const z=await JSZip.loadAsync(__exports.at(-1).blob);return {top:await z.file("board-F_Silkscreen.gbr").async("string"),bottom:await z.file("board-B_Silkscreen.gbr").async("string")}}')
  expected=page.evaluate('()=>{const f=CB.M.files(CBAPP.state.doc);return {top:f["board-F_Silkscreen.gbr"],bottom:f["board-B_Silkscreen.gbr"]}}')
  check(files==expected);check(all('G36*' in t and 'D01*' in t for t in files.values()));close()
 test('The actual UI-generated ZIP contains the tested top and bottom Gerber text',exported)
 def mobile():
  reset();choose();page.set_viewport_size({'width':430,'height':850});page.wait_for_function('document.getElementById("inspector").classList.contains("collapsed")');act('toggle-inspector');act('polarity');check(page.locator('#polarityPrint').is_visible());check(page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),'Root horizontal overflow')
  check('A = anode. K = cathode.' in page.locator('#modalBody').inner_text());page.screenshot(path=str(IMAGES/'polarity-mobile.png'));close();page.set_viewport_size({'width':1600,'height':1050})
 test('Polarity controls remain reachable and labeled on a narrow screen',mobile)
 test('No external runtime requests or uncaught exceptions during the new workflows',lambda:check(not errors and not [r for r in requests if r.startswith('http')],str(errors)))
 record={'version':page.evaluate('CB.VERSION'),'date':datetime.now(timezone.utc).isoformat(),'passed':sum(r['pass'] for r in results),'total':len(results),'scope':'Actual Chromium UI/canvas/workers, simulated localStorage, captured download blobs. Not external CAM, hosted offline behavior or manufacturer acceptance.','results':results}
 (OUT/'silkscreen-browser-results.json').write_text(json.dumps(record,indent=2));print(f"{record['passed']}/{record['total']} silkscreen browser tests passed.");browser.close()
sys.exit(0 if record['passed']==record['total'] else 1)

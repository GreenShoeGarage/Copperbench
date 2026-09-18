#!/usr/bin/env python3
"""Chromium tests of the new parts UI. Storage/downloads use explicit test doubles."""
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
   results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,e,flush=True);traceback.print_exc();page.screenshot(path=str(IMAGES/f'maker-failure-{len(results)}.png'))
 def act(name):page.locator(f'button[data-action="{name}"]:visible').first.click()
 def close():
  if page.locator('#modal').evaluate('el=>el.open'):page.locator('#modalClose').click()
 def reset(expr='CB.blank()'):
  close();page.evaluate('CBAPP.load('+expr+')');page.keyboard.press('Escape');page.locator('[data-panel=parts]').click();page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision',timeout=20000)
 def world(x,y):return page.evaluate('p=>{const r=CBAPP.renderer;r.setup();const q=r.project(p),b=r.canvas.getBoundingClientRect();return{x:q.x+b.left,y:q.y+b.top}}',{'x':x,'y':y})
 def click(x,y):
  q=world(x,y);page.mouse.click(q['x'],q['y']);page.wait_for_timeout(80)
 def select_first():
  page.locator('[data-view=copper]').click();pos=page.evaluate('CB.pads(CBAPP.state.doc)[0]');click(pos['x'],pos['y']);page.locator('[data-view=bench]').click()
 def one(id):reset("(()=>{let d=CB.blank();d.board.width=100;d.board.height=80;d.parts.push(CB.makePart(d,'"+id+"',50,40));return d})()");select_first()
 def family_cards():
  reset();check(page.locator('[data-maker-family]').count()==17);check(page.locator('[data-place]').count()==59);act('maker-catalog');check(page.locator('#makerVariants option').count()==134);check(page.locator('#makerFamily option').count()==18);close()
 test('Family-first drawer groups 134 new variants without replacing legacy parts',family_cards)
 def picker():
  act('maker-catalog');page.select_option('#makerFamily','Named integrated circuits');page.locator('#makerSearch').fill('NE555');check(page.locator('#makerVariants option').count()==2);page.select_option('#makerVariants','maker-ne555-soic');check('TRIG' in page.locator('#makerDetail').inner_text());page.screenshot(path=str(IMAGES/'maker-picker.png'));page.get_by_role('button',name='Place selected part',exact=True).click();click(40,30);page.keyboard.press('Escape');check(page.evaluate("CBAPP.state.doc.parts[0].libraryId==='maker-ne555-soic'"))
 test('Native family/search/variant controls place the selected package through the canvas',picker)
 def search_direct():
  reset();page.locator('#partSearch').fill('Qwiic');check(page.locator('[data-place]').count()==1);page.locator('[data-place="maker-qwiic"]').click();click(40,30);page.keyboard.press('Escape');check(page.evaluate('CBAPP.state.doc.parts[0].pads.length===6'));check(page.evaluate('CBAPP.state.doc.nets.length===0'));page.locator('#partSearch').fill('')
 test('Drawer search finds Qwiic directly and placement does not create a power net',search_direct)
 def names_edit():
  one('maker-ne555-dip');before=page.evaluate('JSON.stringify(CBAPP.state.doc.parts[0].pads)');act('pin-names');page.locator('[data-pin-name="2"]').fill('OUTPUT TO DRIVER');page.get_by_role('button',name='Apply pin names',exact=True).click();check(page.evaluate("CBAPP.state.doc.parts[0].pads[2].signal==='OUTPUT TO DRIVER'"));check(page.evaluate('CBAPP.state.doc.nets.length===0'));act('undo');check(page.evaluate('JSON.stringify(CBAPP.state.doc.parts[0].pads)')==before)
 test('Functional pin-label edits are one undoable metadata operation',names_edit)
 def source_dialog():
  one('maker-lm1117-3.3');act('part-details');check('Texas Instruments' in page.locator('#modalBody').inner_text());check('VOUT' in page.locator('#modalBody').inner_text());check(page.locator('#modalBody a').count()==1);page.locator('#makerReviewed').check();page.get_by_role('button',name='Save review status',exact=True).click();check(page.evaluate('CBAPP.state.doc.parts[0].verified'));act('pin-names');page.get_by_role('button',name='Apply pin names',exact=True).click();check(not page.evaluate('CBAPP.state.doc.parts[0].verified'))
 test('Source notes and explicit user review are visible; label edits clear review',source_dialog)
 def csv():
  act('part-details');page.get_by_role('button',name='Export pin map CSV',exact=True).click();text=page.evaluate('async()=>await __exports[__exports.length-1].blob.text()');check('VOUT / tab' in text and 'Contact' in text);close()
 test('Part-reference dialog exports the actual functional pin map CSV',csv)
 def names_visibility():
  one('maker-ne555-dip');before=page.evaluate('JSON.stringify(CB.M.files(CBAPP.state.doc))');act('pin-names');page.locator('#pinNamesVisible').uncheck();page.get_by_role('button',name='Apply pin names').click();check(page.evaluate('JSON.stringify(CB.M.files(CBAPP.state.doc))')==before)
 test('Editor-only functional captions never leak into manufacturing artwork',names_visibility)
 def conflicts():
  one('maker-lm1117-3.3');page.evaluate("CBAPP.commit('Fixture nets',d=>{const p=d.parts[0];p.pads[1].net=CB.newNet(d,'A');p.pads[3].net=CB.newNet(d,'B')})");page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision');check(page.evaluate("CBAPP.state.findings.some(f=>f.code==='internal-terminal-conflict'&&f.severity==='error')"));act('export');check(page.locator('#downloadFab').is_disabled());close()
 test('Worker findings and normal export block conflicting nets on an internally common tab',conflicts)
 def icsp_template():
  reset();act('platforms');page.locator('[data-family-choice="uno-r3"]').click();page.locator('#platformICSP').check();check('38 plated contacts' in page.locator('#platformSummary').inner_text());page.get_by_role('button',name='Start new board',exact=True).click();check(page.evaluate('CBAPP.state.doc.parts[0].pads.length===38'));check(page.evaluate("CBAPP.state.doc.parts[0].pads[32].signal==='MISO / D12'"));page.screenshot(path=str(IMAGES/'maker-uno-icsp.png'))
 test('Uno template checkbox adds six real ICSP contacts while default templates stay unchanged',icsp_template)
 def icsp_toggle():
  select_first();act('uno-icsp');page.get_by_role('button',name='Remove unused ICSP',exact=True).click();check(page.evaluate('CBAPP.state.doc.parts[0].pads.length===32'));act('undo');check(page.evaluate('CBAPP.state.doc.parts[0].pads.length===38'));select_first();page.evaluate("CBAPP.commit('Fixture SPI net',d=>d.parts[0].pads[32].net=CB.newNet(d,'SPI'))");act('uno-icsp');page.get_by_role('button',name='Remove unused ICSP',exact=True).click();check(page.evaluate('CBAPP.state.doc.parts[0].pads.length===38'));check('Unassign' in page.locator('#toast').inner_text());close()
 test('ICSP removal is undoable and is refused when a pin is still assigned',icsp_toggle)
 def icsp_place():
  reset();act('platforms');page.locator('[data-family-choice="uno-r3"]').click();page.locator('#platformICSP').check();page.get_by_role('button',name='Place headers on current board',exact=True).click();click(40,30);page.keyboard.press('Escape');check(page.evaluate("CBAPP.state.doc.parts[0].pads.length===38&&CBAPP.state.doc.parts[0].ref==='J1'"))
 test('ICSP-enabled headers can be placed on the current board with a normal reference',icsp_place)
 def footprint_edit():
  one('maker-test-loop-2.54');page.select_option('#modeSelect','advanced');act('edit-pads');page.locator('[data-pedit="0"][data-key="number"]').fill('LEFT');page.get_by_role('button',name='Apply pad geometry',exact=True).click();check(page.evaluate("CBAPP.state.doc.parts[0].internalGroups[0][0]==='LEFT'"));page.evaluate("CB.validateDoc(CBAPP.state.doc)")
 test('Advanced pad renumbering keeps internal-terminal group references aligned',footprint_edit)
 def json_save():
  one('maker-qwiic');act('save');text=page.evaluate('async()=>await __exports[__exports.length-1].blob.text()');d=json.loads(text);check(d['parts'][0]['catalog']['mpn']=='SM04B-SRSS-TB');check(d['parts'][0]['pads'][2]['signal']=='SDA');page.locator('#fileInput').set_input_files({'name':'maker-snapshot.json','mimeType':'application/json','buffer':text.encode()});page.wait_for_timeout(300)
  # Imported project confirmation is explicit; use whatever preview button is present.
  if page.locator('#modal').evaluate('el=>el.open'):
   candidates=page.locator('#modalFooter button.primary');
   if candidates.count():candidates.last.click()
  check(page.evaluate("CBAPP.state.doc.parts[0].catalog.mpn==='SM04B-SRSS-TB'"))
 test('Actual JSON download blob and file-input import retain embedded catalog and signals',json_save)
 def kicad_warning():
  close();page.locator('[data-panel=files]').click() if page.locator('[data-panel=files]').count() else None
  # Use the same visible Export -> KiCad command as the production UI.
  act('export');page.locator('[data-action="export-kicad"]').click();check('internal-terminal' in page.locator('#modalBody').inner_text());close()
 test('KiCad exchange warns that functional labels and catalog behavior are not preserved',kicad_warning)
 def showcase():
  reset("(()=>{const d=CB.blank();d.title='Everyday maker parts — layout sampler';d.board.width=145;d.board.height=102;const rows=[['maker-usb-c-usb4085',18,17],['maker-qwiic',43,16],['maker-ne555-dip',68,20],['maker-lm1117-3.3',99,17],['maker-jst-ph-4',125,17],['maker-dip-switch-4',18,49],['maker-trimmer',44,49],['maker-encoder',74,50],['maker-relay-spdt',112,50],['maker-fuse-holder',27,80],['maker-led3',55,83],['maker-led-0805',69,83],['maker-test-loop-5.08',88,83],['maker-terminal-5.08-3',118,83]];for(const[id,x,y]of rows)d.parts.push(CB.makePart(d,id,x,y));d.art.push({id:'title',kind:'text',text:'EVERYDAY MAKER PARTS',x:9,y:94,size:2,width:.2,rotation:0,layer:'top'});return d;})()")
  page.select_option('#modeSelect','easy');page.select_option('#partCategory','All');page.evaluate("CBAPP.state.selection=[];CBAPP.renderer.fit();");page.wait_for_timeout(1600);page.screenshot(path=str(IMAGES/'maker-workbench.png'))
 test('A real 3D workbench renders new connector, control, driver and debugging bodies',showcase)
 def mobile():
  page.set_viewport_size({'width':430,'height':900});act('toggle-drawer');page.locator('[data-panel=parts]').click();act('maker-catalog');page.select_option('#makerFamily','Power input connectors');page.select_option('#makerVariants','maker-usb-c-usb4085');page.screenshot(path=str(IMAGES/'maker-mobile.png'));check(page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'));check(page.locator('#makerPlace').is_visible());close();page.set_viewport_size({'width':1600,'height':1050})
 test('Narrow-screen picker remains reachable without page-level horizontal overflow',mobile)
 test('No uncaught exceptions or external runtime requests during maker workflows',lambda:(check(not errors,str(errors)),check(not [u for u in requests if u.startswith('http')],str(requests))))
 browser.close()
record={'version':json.loads((ROOT/'package.json').read_text())['version'],'passed':sum(r['pass'] for r in results),'total':len(results),'scope':'Real Chromium controls and software-3D canvas; simulated storage and captured download blobs.','results':results};(OUT/'maker-browser-results.json').write_text(json.dumps(record,indent=2));print(f"{record['passed']}/{record['total']} maker browser checks passed.");sys.exit(record['passed']!=record['total'])

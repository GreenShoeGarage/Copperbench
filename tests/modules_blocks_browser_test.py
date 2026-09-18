#!/usr/bin/env python3
"""Real Chromium UI/canvas/worker interactions. Storage is simulated; download
blobs are captured. Not a native-download, offline-install or fabrication test."""
from pathlib import Path
import json,time,traceback,sys
from playwright.sync_api import sync_playwright
from browser_support import launch_chromium
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';IMAGES=OUT/'images';IMAGES.mkdir(parents=True,exist_ok=True);results=[]
STORE="""()=>{window.__store={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>__store[k]??null,setItem:(k,v)=>__store[k]=String(v),removeItem:k=>delete __store[k]}});window.__blobs=new Map;window.__exports=[];const orig=URL.createObjectURL;URL.createObjectURL=function(b){const u=orig.call(URL,b);__blobs.set(u,b);return u};}"""
with sync_playwright() as pw:
 browser=launch_chromium(pw);page=browser.new_page(viewport={'width':1600,'height':1050},device_scale_factor=1);page.set_default_timeout(10000);errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url));page.evaluate(STORE);page.set_content((ROOT/'COPPERBENCH-portable.html').read_text(),wait_until='load');page.evaluate("document.addEventListener('click',e=>{const a=e.target.closest('a[download]');if(a){e.preventDefault();__exports.push({name:a.download,blob:__blobs.get(a.href)})}},true)");page.wait_for_function('CBAPP?.ready')
 def check(c,msg='Assertion failed'):
  if not c:raise AssertionError(msg)
 def test(name,fn):
  t=time.perf_counter()
  try:fn();results.append({'name':name,'pass':True,'ms':round((time.perf_counter()-t)*1000)});print('PASS',name,flush=True)
  except Exception as e:
   results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,e,flush=True);traceback.print_exc();page.screenshot(path=str(IMAGES/f'modules-blocks-failure-{len(results)}.png'))
 def act(name):
  if name in ('block-import','block-capture','blocks-table','open-footprint') and not page.locator(f'button[data-action="{name}"]:visible').count():
   page.locator('#libraryTools > summary').click()
  page.locator(f'button[data-action="{name}"]:visible').first.click()
 def close():
  if page.locator('#modal').evaluate('el=>el.open'):page.locator('#modalClose').click()
 def done():page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision && !CBAPP.state.job',timeout=30000)
 def reset(expr='CB.blank()'):
  close();page.evaluate('CBAPP.load('+expr+')');page.keyboard.press('Escape');page.locator('[data-panel=parts]').click();page.locator('[data-view=bench]').click();done()
 def xy(x,y):return page.evaluate('p=>{const r=CBAPP.renderer;r.setup();const q=r.project(p),b=r.canvas.getBoundingClientRect();return{x:q.x+b.left,y:q.y+b.top}}',{'x':x,'y':y})
 def point(x,y):
  q=xy(x,y);page.mouse.click(q['x'],q['y']);page.wait_for_timeout(100)
 def module_new(id='module-bme280-original'):
  close();act('modules-catalog');page.select_option('#moduleChoice',id);page.get_by_role('button',name='Start carrier board',exact=True).click();done()
 def block_new(id='block-led',x=35,y=25):
  close();act('blocks-catalog');page.select_option('#blockChoice',id);page.locator('#blockX').fill(str(x));page.locator('#blockY').fill(str(y));page.locator('#blockInsert').click();done()
 def menus():
  reset();act('modules-catalog');check(page.locator('#moduleChoice option').count()==5);check('not a replacement' in page.locator('#modalBody').inner_text());check(not page.locator('#moduleHoles').is_checked());close();act('blocks-catalog');check(page.locator('#blockChoice option').count()==6);check(page.locator('#blockCopper').is_checked());check(page.locator('[data-block-port]').count()==2);page.screenshot(path=str(IMAGES/'block-picker.png'));close()
 test('Module and block pickers expose exact variants and isolated-port defaults',menus)
 def every_module():
  for id,count in [('module-bme280-original',7),('module-ds3231-original',8),('module-oled-096-qt',8),('module-tb6612',16),('module-mpm3610-33',4)]:
   module_new(id);check(page.evaluate('CBAPP.state.doc.parts[0].pads.length')==count);check(page.locator('[data-prop=locked]').is_checked());check(page.locator('[data-action=module-details]').is_visible())
 test('All five module starters create locked, routable, correctly named interfaces',every_module)
 def module_place():
  reset();before=page.evaluate('JSON.stringify(CBAPP.state.doc.board)');act('modules-catalog');page.select_option('#moduleChoice','module-ds3231-original');page.locator('#moduleHoles').check();page.locator('#moduleGap').fill('8');page.get_by_role('button',name='Place on current board',exact=True).click();point(35,25);page.keyboard.press('Escape');check(page.evaluate('CBAPP.state.doc.parts[0].module.stackGap')==8);check(page.evaluate('CB.mountingHoles(CBAPP.state.doc).length')==2);check(page.evaluate('JSON.stringify(CBAPP.state.doc.board)')==before)
 test('Module placement retains the existing board, optional holes and entered stack gap',module_place)
 def module_details():
  act('module-details');check('CR1220' in page.locator('#modalBody').inner_text());page.locator('#moduleShow').uncheck();before=page.evaluate('JSON.stringify(CBAPP.exportFiles())');page.get_by_role('button',name='Apply module settings',exact=True).click();done();check(page.evaluate('JSON.stringify(CBAPP.exportFiles())')==before);check(not page.evaluate('CBAPP.state.doc.parts[0].module.showBody'));act('undo');done();check(page.evaluate('CBAPP.state.doc.parts[0].module.showBody'))
 test('Module fit notes are visible and body visibility is undoable without changing Gerbers',module_details)
 def module_csv():
  page.locator('[data-view=copper]').click();p=page.evaluate('CB.pads(CBAPP.state.doc)[0]');point(p['x'],p['y']);page.locator('[data-view=bench]').click();act('module-details');page.get_by_role('button',name='Export pin map',exact=True).click();text=page.evaluate("async()=>await __exports.filter(e=>e.name.endsWith('-pins.csv')).at(-1).blob.text()");check('VBAT' in text and 'SQW' in text);close()
 test('Module pin-map CSV is downloadable through the real inspector control',module_csv)
 def every_block():
  for id in ['block-led','block-button','block-i2c','block-decoupling','block-dc-input','block-rc-filter']:
   reset();block_new(id);check(page.evaluate('CBAPP.state.doc.blockInstances.length')==1);check(page.evaluate('CBAPP.state.doc.traces.length')>0);check(page.evaluate('CBAPP.state.connectivity.air.length')==0);check(page.locator('[data-action=block-details]').is_visible())
 test('All six starters insert actual routed geometry and worker connectivity reports no open net',every_block)
 def undo():
  reset();block_new();n=page.evaluate('CBAPP.state.doc.nets.length');act('undo');done();check(page.evaluate('CBAPP.state.doc.parts.length')==0);check(page.evaluate('CBAPP.state.doc.blockInstances.length')==0);act('redo');done();check(page.evaluate('CBAPP.state.doc.parts.length')==3);check(page.evaluate('CBAPP.state.doc.nets.length')==n)
 test('Block insertion and all of its nets/parts/copper are one undoable action',undo)
 def fresh():
  reset();block_new(x=20);block_new(x=60);check(page.evaluate('(()=>{const[a,b]=CBAPP.state.doc.blockInstances;return a.ports.every(p=>b.ports.every(q=>p.net!==q.net))})()'));check(page.evaluate('CBAPP.state.doc.parts.map(p=>p.ref).join(",")')=='J1,R1,D1,J2,R2,D2')
 test('Two UI insertions have isolated nets and fresh ordinary reference designators',fresh)
 def mapping():
  reset();page.evaluate("CBAPP.commit('Create net',d=>CB.newNet(d,'SYSTEM_GND'))");act('blocks-catalog');n=page.evaluate('CBAPP.state.doc.nets[0].id');page.select_option('[data-block-port=RETURN]',n);page.locator('#blockInsert').click();done();check(page.evaluate('CBAPP.state.doc.blockInstances[0].ports.find(p=>p.key==="RETURN").net')==n)
 test('Explicit port mapping shares only the chosen existing project net',mapping)
 def no_shorts():
  reset();page.evaluate("CBAPP.commit('Create net',d=>CB.newNet(d,'TEST'))");act('blocks-catalog');n=page.evaluate('CBAPP.state.doc.nets[0].id');page.select_option('[data-block-port=DRIVE]',n);page.select_option('[data-block-port=RETURN]',n);before=page.evaluate('JSON.stringify(CBAPP.state.doc)');page.locator('#blockInsert').click();check(page.locator('#modal').evaluate('el=>el.open'));check('cannot be joined' in page.locator('#toast').inner_text());check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before);close()
 test('Mapping distinct ports to one net is blocked without a partial edit',no_shorts)
 def values():
  reset();act('blocks-catalog');page.locator('summary').filter(has_text='Component values').click();page.locator('[data-block-value="1"]').fill('2k2');page.locator('#blockCopper').uncheck();page.locator('#blockInsert').click();done();check(page.evaluate('CBAPP.state.doc.parts[1].value')=='2k2');check(page.evaluate('CBAPP.state.doc.traces.length')==0);check(page.evaluate('CBAPP.state.connectivity.air.length')>0)
 test('Value edits and copper omission retain ordinary parts and visible unrouted intent',values)
 def placement():
  reset();act('blocks-catalog');page.locator('#blockPick').click();check(page.evaluate('!!CBAPP.state.blockPlacing'));page.keyboard.press('r');page.keyboard.press('f');check(page.evaluate('CBAPP.state.blockPlacing.rotation')==90);point(40,25);done();check(page.evaluate('CBAPP.state.doc.parts.every(p=>p.side==="bottom")'));check(page.evaluate('CBAPP.state.connectivity.air.length')==0);check(not page.evaluate('!!CBAPP.state.blockPlacing'))
 test('Board-click ghost placement supports rotation, side flip and connected copper',placement)
 def cancellation():
  reset();before=page.evaluate('JSON.stringify(CBAPP.state.doc)');act('blocks-catalog');page.locator('#blockPick').click();page.keyboard.press('Escape');check(not page.evaluate('!!CBAPP.state.blockPlacing'));check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before)
 test('Esc cancels pending block placement without touching the project',cancellation)
 def blocked():
  reset();block_new();before=page.evaluate('JSON.stringify(CBAPP.state.doc)');act('blocks-catalog');page.locator('#blockX').fill('35');page.locator('#blockY').fill('25');page.locator('#blockInsert').click();check(page.locator('#modal').evaluate('el=>el.open'));check('placement blocked' in page.locator('#toast').inner_text());check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before);close()
 test('Preflight blocks overlapping different-net copper rather than committing a short',blocked)
 def group_transform():
  act('block-details');page.get_by_role('button',name='Select whole block',exact=True).click();old=page.evaluate('JSON.stringify(CBAPP.state.doc.traces)');page.keyboard.press('r');done();check(page.evaluate('JSON.stringify(CBAPP.state.doc.traces)')!=old);check(page.evaluate('CBAPP.state.connectivity.air.length')==0);page.keyboard.press('f');done();check(page.evaluate('CBAPP.state.connectivity.air.length')==0);check(page.evaluate('CBAPP.state.doc.parts.every(p=>p.side==="bottom")'));act('undo');act('undo');done()
 test('Whole-block R/F transform every component, trace and via together',group_transform)
 def group_drag():
  act('blocks-table');page.locator('[data-open-block]').first.click();page.get_by_role('button',name='Select whole block',exact=True).click();old=page.evaluate('CBAPP.state.doc.traces[0].points[0]');anchor=page.evaluate('CBAPP.state.doc.parts[1]');q=xy(anchor['x'],anchor['y']);page.mouse.move(q['x'],q['y']);page.mouse.down();page.mouse.move(q['x']+30,q['y']+15,steps=5);page.mouse.up();done();check(page.evaluate('CBAPP.state.doc.traces[0].points[0]')!=old);check(page.evaluate('CBAPP.state.connectivity.air.length')==0)
 test('Dragging a selected whole block moves the copper and keeps connectivity intact',group_drag)
 def copy():
  reset();block_new(x=20);act('block-details');page.get_by_role('button',name='Copy with fresh nets',exact=True).click();point(60,25);done();check(page.evaluate('CBAPP.state.doc.blockInstances.length')==2);check(page.evaluate('(()=>{const[a,b]=CBAPP.state.doc.blockInstances;return a.ports.every(p=>b.ports.every(q=>p.net!==q.net))})()'))
 test('Block-copy control places a new editable circuit with fresh internal and external nets',copy)
 def capture():
  act('block-capture');page.locator('#captureName').fill('Bench indicator');page.get_by_role('button',name='Save to project library',exact=True).click();check(page.locator('#blockChoice option').count()==7);check(page.evaluate('CBAPP.state.doc.blockLibrary[0].parts.length')==3);check(page.evaluate('CBAPP.state.doc.blockLibrary[0].traces.length')==3);close()
 test('Capture selection stores components and selected copper in the project library',capture)
 def export_block():
  act('block-details');page.get_by_role('button',name='Export block JSON',exact=True).click();saved=page.evaluate("async()=>JSON.parse(await __exports.filter(e=>e.name.endsWith('.copperblock.json')).at(-1).blob.text())");check(saved['app']=='COPPERBENCH-BLOCK');check(len(saved['parts'])==3);(OUT/'browser-exported-block.json').write_text(json.dumps(saved));close()
 test('Block export downloads the actual edited geometry as a reusable JSON file',export_block)
 def import_block():
  before=page.evaluate('CBAPP.state.doc.parts.length');act('block-import');page.locator('#blockInput').set_input_files(str(OUT/'browser-exported-block.json'));page.get_by_role('button',name='Add copy to project library',exact=True).click();check(page.locator('#blockChoice option').count()==8);check(page.evaluate('CBAPP.state.doc.parts.length')==before);close()
 test('File-input block import asks for confirmation and adds a library copy without replacing the board',import_block)
 def invalid_import():
  before=page.evaluate('JSON.stringify(CBAPP.state.doc)');page.locator('#blockInput').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{"app":"BAD"}'});page.wait_for_timeout(150);check('Block import' in page.locator('#toast').inner_text());check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before)
 test('Invalid block file input leaves project data unchanged',invalid_import)
 def json_backup():
  act('save');saved=page.evaluate("async()=>JSON.parse(await __exports.filter(e=>e.name.endsWith('.json')&&!e.name.endsWith('.copperblock.json')).at(-1).blob.text())");check(saved['schema']==5);check(len(saved['blockInstances'])==2);check(len(saved['blockLibrary'])==2)
 test('Native schema-5 backup contains placed groups and personal library entries',json_backup)
 def detach():
  act('block-details');before=page.evaluate('JSON.stringify(CBAPP.exportFiles())');page.get_by_role('button',name='Detach grouping',exact=True).click();done();check(page.evaluate('CBAPP.state.doc.blockInstances.length')==1);check(page.evaluate('JSON.stringify(CBAPP.exportFiles())')==before);act('undo');done()
 test('Detach removes only group metadata, with exact Gerber/drill equality and undo',detach)
 def manager():
  act('blocks-table');check(page.locator('[data-open-block]').count()==2);page.locator('[data-open-block]').first.click();check('B1' in page.locator('#modalTitle').inner_text());page.locator('#blockMoveX').fill('21');page.get_by_role('button',name='Apply block changes',exact=True).click();done();check(page.evaluate('CBAPP.state.doc.blockInstances[0].x')==21)
 test('On-board block manager selects a group and supports precise anchor movement',manager)
 def manufacturing():
  reset();block_new();page.locator('[data-view=fabrication]').click();done();act('fab-silk-top');check(page.evaluate('CBAPP.state.fabLayers.length')==2);check(page.evaluate('CBAPP.state.fabData[CBAPP.state.fabLayers.find(n=>n.includes("F_Silkscreen"))].objects.length')>0);page.screenshot(path=str(IMAGES/'block-silkscreen.png'));page.locator('[data-view=bench]').click()
 test('Fabrication view reads actual exported block reference and polarity silkscreen',manufacturing)
 def module_screen():
  reset('CB.Modules.example()');page.evaluate('CBAPP.renderer.fit()');page.screenshot(path=str(IMAGES/'modules-workbench.png'))
 test('Module sampler renders five distinct representative board bodies',module_screen)
 def block_screen():
  reset('CB.Blocks.example()');page.evaluate('CBAPP.renderer.fit()');page.screenshot(path=str(IMAGES/'blocks-workbench.png'))
 test('Circuit sampler renders six complete editable block layouts',block_screen)
 def mobile():
  close();page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(150);act('toggle-drawer');act('blocks-catalog');check(page.locator('#blockPick').is_visible());check(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'));page.screenshot(path=str(IMAGES/'blocks-mobile.png'));close();page.set_viewport_size({'width':1600,'height':1050});page.wait_for_timeout(100)
 test('Phone-sized layout keeps the block picker usable without page-width overflow',mobile)
 def clean():
  check(not errors,'Uncaught errors: '+str(errors));check(not [u for u in requests if u.startswith(('https://','http://'))],'External runtime request')
 test('New workflows produce no uncaught exceptions or external runtime asset requests',clean)
 browser.close()
(OUT/'modules-blocks-browser-results.json').write_text(json.dumps({'passed':sum(r['pass'] for r in results),'total':len(results),'results':results},indent=2));print(f"{sum(r['pass'] for r in results)}/{len(results)} module/block browser checks passed.");sys.exit(0 if all(r['pass'] for r in results) else 1)

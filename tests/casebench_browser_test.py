#!/usr/bin/env python3
"""CaseBench handoff UI: real Chromium controls/canvas/workers, test-double
storage and captured download blobs. Does not execute the CaseBench importer."""
from pathlib import Path
import ast, json, traceback
from playwright.sync_api import sync_playwright
from browser_support import launch_chromium
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';IMAGES=OUT/'images';IMAGES.mkdir(parents=True,exist_ok=True)
module=ast.parse((ROOT/'tests/browser_test.py').read_text())
STORE=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='STORE' for t in n.targets))
results=[];errors=[];requests=[];captured={}
with sync_playwright() as pw:
 browser=launch_chromium(pw);page=browser.new_page(viewport={'width':1600,'height':1000},device_scale_factor=1);page.set_default_timeout(10000)
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
 page.evaluate(STORE,{})
 page.set_content((ROOT/'COPPERBENCH-portable.html').read_text(),wait_until='load')
 page.evaluate("document.addEventListener('click',e=>{const a=e.target.closest('a[download]');if(a){e.preventDefault();__exports.push({name:a.download,blob:__blobs.get(a.href)})}},true)")
 page.wait_for_function('window.CBAPP?.ready && CBAPP.state.checkRevision===CBAPP.state.revision',timeout=25000)
 def check(cond,msg='Assertion failed'):
  if not cond:raise AssertionError(msg)
 def test(name,fn):
  try:fn();results.append({'name':name,'pass':True});print('PASS',name,flush=True)
  except Exception as e:results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,e,flush=True);traceback.print_exc();page.screenshot(path=str(IMAGES/f'casebench-fail-{len(results)}.png'))
 def act(action):
  modal=page.locator('#modal')
  scope=modal if modal.evaluate('e=>e.open') else page
  scope.locator(f'[data-action="{action}"]:visible').first.click()
 def close():
  if page.locator('#modal').evaluate('e=>e.open'):page.locator('#modalClose').click()
 def reset(expr='CB.example("mixed")'):
  close();page.set_viewport_size({'width':1600,'height':1000});page.evaluate('CBAPP.load('+expr+')');page.keyboard.press('Escape');page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision && !CBAPP.state.job',timeout=25000)
 def open_export():
  act('exports');act('export-casebench');page.wait_for_selector('#casebenchDownload')
 def blob():return page.evaluate('async()=>{const e=__exports.at(-1);return{name:e.name,text:await e.blob.text()}}')
 def menu():
  check(page.locator('[data-action=exports]').is_visible());act('exports');check(page.locator('#modalTitle').inner_text()=='Export board');check(page.locator('.export-format-list button').count()==4);act('export-casebench');check(page.locator('#modalTitle').inner_text()=='Export to CaseBench');check(not page.locator('.casebench-details').evaluate('e=>e.open'));check(page.locator('#casebenchDownload').is_enabled());close()
 test('Compact export arrow opens a dedicated CaseBench option with collapsed details',menu)
 def download_native():
  reset();before=page.evaluate('JSON.stringify(CBAPP.state.doc)');open_export();check('7 components' in page.locator('#casebenchSummary').inner_text());page.click('#casebenchDownload');r=blob();d=json.loads(r['text']);check(r['name'].endswith('-casebench.json'));check(d['app']=='COPPERBENCH' and d['schema']==5 and d['units']=='mm');check(len(d['parts'])==7 and len(d['art'])==0);check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before);captured.update(r);(OUT/'casebench-browser-export.json').write_text(r['text'])
 test('Download captures a valid native schema-5 board without modifying the editor',download_native)
 def transform():
  reset('(()=>{const d=CB.example("mixed");d.parts[0].rotation=37;d.parts[0].side="bottom";return d})()');before=page.evaluate('JSON.stringify(CB.pads(CBAPP.state.doc))');act('units');check(page.evaluate('CBAPP.state.units')=='mil');page.locator('[data-side=bottom]').click();act('pan');open_export();page.click('#casebenchDownload');d=json.loads(blob()['text']);check(d['units']=='mm');check(d['parts'][0]['rotation']==37 and d['parts'][0]['side']=='bottom');check(page.evaluate('d=>JSON.stringify(CB.pads(d))',d)==before);act('units');act('pan')
 test('Bottom view, pan and mil display never transform or rescale exported coordinates',transform)
 def extras():
  reset();open_export();page.locator('.casebench-details summary').click();page.check('#casebenchExtras');page.click('#casebenchDownload');d=json.loads(blob()['text']);check(len(d['art'])>0);check(d['parts']==page.evaluate('CBAPP.state.doc.parts'))
 test('Optional project extras include original artwork without changing geometry',extras)
 def pending():
  for field in ['drawing','editPreview','blockPlacing','routePreview']:
   reset();page.evaluate('field=>CBAPP.state[field]={pending:true,traces:[],vias:[]}',field);open_count=page.evaluate('__exports.length');act('exports');act('export-casebench');check('pending' in page.locator('#toast').inner_text());check(page.evaluate('__exports.length')==open_count);page.evaluate('field=>CBAPP.state[field]=null',field);close()
 test('Uncommitted trace, connected edit, block placement and autowire previews block handoff',pending)
 def stale():
  reset();open_export();before=page.evaluate('__exports.length');page.evaluate("CBAPP.commit('Changed thickness',d=>d.board.thickness=2,{copper:false})");page.click('#casebenchDownload');check(page.evaluate('__exports.length')==before);check(page.locator('#casebenchDownload').is_disabled());check('board changed' in page.locator('#toast').inner_text().lower());close()
 test('A changed revision cannot download the previously reviewed board',stale)
 def stale_plane():
  reset('(()=>{const d=CB.example();d.settings.autoPlanes=false;CB.Planes.set(d,"bottom",d.nets[0].id);return d;})()');check(page.evaluate('!CBAPP.state.doc.zones[0].fill'));open_export();check(page.locator('#casebenchDownload').is_enabled());page.click('#casebenchDownload');d=json.loads(blob()['text']);check(len(d['zones'])==1)
 test('Unrouted boards and unfilled planes can be exported for enclosure work',stale_plane)
 def board_panel():
  reset();page.locator('[data-panel=board]').click();act('export-casebench');check(page.locator('#modalTitle').inner_text()=='Export to CaseBench');close()
 test('Board panel provides a direct CaseBench export independent of fabrication',board_panel)
 def fullsize():
  reset('(()=>{const d=CB.example();d.assets=[{id:"big",data:"data:image/png;base64,"+"A".repeat(8388608)}];return d})()');open_export();check(page.locator('#casebenchDownload').is_enabled());page.locator('.casebench-details summary').click();page.check('#casebenchExtras');check(page.locator('#casebenchDownload').is_disabled());check('JSON bytes' in page.locator('#casebenchSummary').inner_text());page.uncheck('#casebenchExtras');check(page.locator('#casebenchDownload').is_enabled());close()
 test('Oversized full project is blocked; compact board-only export remains available',fullsize)
 def module_holes():
  reset('(()=>{const d=CB.Modules.template("module-ds3231-original",true);d.title="RTC enclosure carrier";d.parts[0].rotation=180;d.parts[0].side="bottom";return d})()');before=page.evaluate('CB.G.holes(CBAPP.state.doc)');height=page.evaluate('CBAPP.state.doc.parts[0].body.z');open_export();check('2 mounting holes' in page.locator('#casebenchSummary').inner_text());page.click('#casebenchDownload');d=json.loads(blob()['text']);check(page.evaluate('d=>CB.G.holes(d)',d)==before);check(d['parts'][0]['body']['z']==height);check(d['holes']==[])
 test('Rotated bottom module keeps active local holes and existing stacked body height',module_holes)
 def reimport():
  reset('CB.blank()');page.locator('#fileInput').set_input_files({'name':captured['name'],'mimeType':'application/json','buffer':captured['text'].encode()});page.wait_for_selector('#modalFooter .primary');check('Review before replacing' in page.locator('#modalTitle').inner_text());page.locator('#modalFooter .primary').click();check(page.evaluate('CBAPP.state.doc.parts.length')==7);check(page.evaluate('CBAPP.state.doc.units')=='mm')
 test('Downloaded handoff reopens through the real CopperBench JSON import controls',reimport)
 def screenshot():
  reset('(()=>{const d=CB.Modules.template("module-ds3231-original",true);d.title="RTC enclosure carrier";return d})()');page.evaluate("document.getElementById('toast').hidden=true;document.getElementById('inspector').classList.add('collapsed');CBAPP.renderer.fit()");page.locator('[data-panel=board]').click();open_export();page.screenshot(path=str(IMAGES/'casebench-export.png'));check(page.locator('#casebenchDownload').is_visible())
 test('Desktop export summary remains compact and readable',screenshot)
 def mobile():
  reset();page.set_viewport_size({'width':390,'height':844});check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'));act('exports');act('export-casebench');check(page.locator('#casebenchDownload').is_visible());check(page.locator('#modal').bounding_box()['width']<=390);page.screenshot(path=str(IMAGES/'casebench-export-mobile.png'));close();act('files');act('export-casebench');check(page.locator('#casebenchDownload').is_enabled());close()
 test('Mobile export menu and project files both reach the handoff without horizontal overflow',mobile)
 def safe_text():
  reset('(()=>{const d=CB.blank();d.title="<img src=x onerror=alert(1)>";return d})()');open_export();check(page.locator('#modalBody img').count()==0);close()
 test('Project title is escaped in the export summary',safe_text)
 def request_check():
  check(not errors,'Uncaught JS errors: '+str(errors));check(not [u for u in requests if not u.startswith(('blob:','data:','about:'))],str(requests))
 test('Handoff controls produce no uncaught JavaScript errors or external requests',request_check)
 browser.close()
summary={'environment':'Chromium controls/canvas/workers; simulated storage and captured download blobs; CaseBench target importer not executed.', 'passed':sum(r['pass'] for r in results),'total':len(results),'results':results,'uncaught':errors}
(OUT/'casebench-browser-results.json').write_text(json.dumps(summary,indent=2)+'\n')
print(f"{summary['passed']}/{summary['total']} CaseBench browser checks passed")
raise SystemExit(0 if summary['passed']==summary['total'] else 1)

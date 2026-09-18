#!/usr/bin/env python3
"""Real plane controls/canvas/worker regressions. Storage and download navigation are test doubles."""
from pathlib import Path
from datetime import datetime,timezone
import json,time,traceback,sys
from playwright.sync_api import sync_playwright
from browser_support import launch_chromium
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';IMAGES=OUT/'images';IMAGES.mkdir(parents=True,exist_ok=True)
results=[]
STORE="""()=>{window.__store={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>__store[k]??null,setItem:(k,v)=>__store[k]=String(v),removeItem:k=>delete __store[k]}});window.__blobs=new Map;window.__exports=[];const orig=URL.createObjectURL;URL.createObjectURL=b=>{const u=orig.call(URL,b);__blobs.set(u,b);return u;};}"""
BASE="""(()=>{const d=CB.blank();d.title='Ground where you need it';d.board={...d.board,width:32,height:24,shape:'rect'};const n=CB.newNet(d,'GND');for(const [x,y,th,net] of [[6,6,true,n],[17,13,false,null]]){const p=CB.makePart(d,'testpoint',x,y);p.pads[0].drill=th?.8:0;p.pads[0].net=net;p.label.visible=false;p.verified=true;d.parts.push(p);}return d;})()"""
SEED="(()=>{const d="+BASE+";CB.Planes.groundPreset(d);return d;})()"
with sync_playwright() as pw:
 browser=launch_chromium(pw);page=browser.new_page(viewport={'width':1600,'height':1050},device_scale_factor=1);page.set_default_timeout(8000)
 errors=[];requests=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
 page.evaluate(STORE);page.set_content((ROOT/'COPPERBENCH-portable.html').read_text(),wait_until='load')
 page.evaluate("document.addEventListener('click',e=>{const a=e.target.closest('a[download]');if(a){e.preventDefault();__exports.push({name:a.download,blob:__blobs.get(a.href)});}},true)")
 page.wait_for_function('CBAPP?.ready && CBAPP.state.checkRevision===CBAPP.state.revision',timeout=30000)
 def check(c,m='Assertion failed'):
  if not c:raise AssertionError(m)
 def act(n):page.locator(f'button[data-action="{n}"]:visible').first.click()
 def close():
  if page.locator('#modal').evaluate('(e)=>e.open'):page.locator('#modalClose').click()
 def stable(fill=True):
  page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision && !CBAPP.state.job'+(' && CBAPP.state.doc.zones.every(z=>z.fill)' if fill else ''),timeout=60000)
 def reset(expr=SEED):
  close();page.keyboard.press('Escape');page.evaluate('CBAPP.load('+expr+')');page.keyboard.press('Escape')
  page.locator('[data-view=copper]').click();page.locator('[data-side=top]').click();page.locator('[data-panel=planes]').click();stable(page.evaluate('CB.Planes.list(CBAPP.state.doc).length>0'))
 def point(x,y,button='left'):
  q=page.evaluate('p=>{const r=CBAPP.renderer;r.setup();const q=r.project(p),b=r.canvas.getBoundingClientRect();return{x:q.x+b.left,y:q.y+b.top};}',{'x':x,'y':y})
  page.mouse.click(q['x'],q['y'],button=button)
 def preview(x=17,y=13):
  page.locator('[data-plane-connect=bottom]').click();point(x,y);page.wait_for_function('CBAPP.state.routePreview?.planePlan',timeout=60000)
 def accept():act('accept-route');stable()
 def test(name,fn):
  t=time.perf_counter()
  try:fn();results.append({'name':name,'pass':True,'ms':round((time.perf_counter()-t)*1000)});print('PASS',name,flush=True)
  except Exception as e:results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,e,flush=True);page.screenshot(path=str(IMAGES/f'plane-failure-{len(results)}.png'));traceback.print_exc()
 def ground():
  reset(BASE);history=page.evaluate('CBAPP.state.history.length');act('ground-plane');stable();check(page.locator('[data-plane-net=top]').input_value()=='')
  check(page.evaluate('CB.Planes.get(CBAPP.state.doc,"bottom").net===CBAPP.state.doc.nets[0].id && CBAPP.state.doc.parts[1].pads[0].net===null'))
  check('1 / 1 leads connected' in page.locator('.plane-card.bottom').inner_text());check(page.evaluate('CBAPP.state.history.length')==history+1)
 test('Bottom-ground preset assigns one face and auto-fills without inventing pin nets or undo steps',ground)
 def power():
  reset();page.select_option('[data-plane-net=top]','__new');page.fill('#planeNewNetName','+5V');page.get_by_role('button',name='Create and assign',exact=True).click();stable()
  check(page.evaluate('CB.Planes.list(CBAPP.state.doc).length===2 && CBAPP.state.doc.parts[1].pads[0].net===null'))
  check('No attached copper yet' in page.locator('.plane-card.top').inner_text())
 test('Top-power dropdown creates a separate named net and honestly reports no attached copper',power)
 def direct():
  reset();preview(6,6);check(page.evaluate('CBAPP.state.routePreview.traces.length===0 && CBAPP.state.routePreview.vias.length===0'));check(page.locator('[data-action=accept-route]').is_enabled());accept()
  check(page.evaluate('CBAPP.state.doc.vias.length===0'))
 test('Through-hole lead accepts a direct plane attachment without an unnecessary via',direct)
 def other():
  reset();preview();check(page.evaluate('CBAPP.state.doc.vias.length===0 && CBAPP.state.doc.parts[1].pads[0].net===null'))
  check(page.evaluate('CBAPP.state.routePreview.vias.length===1 && CBAPP.state.routePreview.traces.length===1'));accept()
  check(page.evaluate('CBAPP.state.planeReport[0].connected===2 && CBAPP.state.doc.vias.length===1'))
 test('Opposite-face SMT lead previews then commits an actual trace and via',other)
 def discard():
  reset();before=page.evaluate('JSON.stringify(CBAPP.state.doc)');preview();act('reject-route');check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before)
 test('Discarding an attachment leaves the native board unchanged',discard)
 def history():
  reset();preview();accept();act('undo');stable();check(page.evaluate('CBAPP.state.doc.vias.length===0 && CBAPP.state.doc.parts[1].pads[0].net===null'))
  act('redo');stable();check(page.evaluate('CBAPP.state.doc.vias.length===1 && CBAPP.state.planeReport[0].connected===2'))
 test('One undo or redo handles net assignment, short trace, via and plane state together',history)
 def perpin():
  reset();point(17,13);button=page.locator('#inspector [data-plane-pin]').first;button.focus();page.keyboard.press('Enter')
  check(page.locator('#planeTarget').is_visible());page.get_by_role('button',name='Preview connection',exact=True).click();page.wait_for_function('CBAPP.state.routePreview?.planePlan',timeout=60000);accept()
 test('Inspector pin action supports keyboard-based plane attachment',perpin)
 def picked():
  reset();page.locator('[data-tool=connect]').first.click();point(6,6);point(17,13);act('connect-plane');page.get_by_role('button',name='Preview connection',exact=True).click()
  page.wait_for_function('CBAPP.state.routePreview?.planePlan',timeout=60000);check(page.evaluate('CBAPP.state.routePreview.steps.length===2'));accept()
 test('Two picked leads connect in one checked batch rather than merging every net',picked)
 def context():
  reset();point(17,13,'right');page.get_by_role('button',name='Connect this lead to a plane',exact=True).click();check(page.locator('#planeTarget').is_visible());close()
 test('Pad context menu exposes the same explicit plane workflow',context)
 def conflict():
  reset('(()=>{const d='+SEED+';d.parts[1].pads[0].net=CB.newNet(d,"OTHER");return d;})()');before=page.evaluate('JSON.stringify(CBAPP.state.doc)')
  page.locator('[data-plane-connect=bottom]').click();point(17,13);page.wait_for_function('!CBAPP.state.job');page.wait_for_function('document.getElementById("toast").textContent.includes("never merge nets")')
  check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before)
 test('A conflicting assigned pin is rejected without a net merge or partial copper',conflict)
 def cancel():
  reset();page.locator('[data-plane-connect=bottom]').click();point(17,13);act('cancel-job');page.wait_for_timeout(500)
  check(page.evaluate('!CBAPP.state.job && !CBAPP.state.routePreview && CBAPP.state.doc.vias.length===0'))
 test('Cancelling the real connection worker adds no proposed copper',cancel)
 def stale():
  reset();page.locator('[data-plane-connect=bottom]').click();point(17,13)
  page.evaluate('CBAPP.commit("Concurrent edit",d=>d.title="Newer revision",{copper:false})');stable();check(page.evaluate('!CBAPP.state.routePreview && CBAPP.state.doc.vias.length===0 && CBAPP.state.doc.title==="Newer revision"'))
 test('A worker proposal cannot overwrite a newer board revision',stale)
 def resize():
  reset();parts=page.evaluate('JSON.stringify(CBAPP.state.doc.parts)');page.locator('[data-panel=board]').click();page.fill('[data-board=width]','38');page.locator('[data-board=width]').press('Tab');stable()
  check(page.evaluate('Math.max(...CB.Planes.get(CBAPP.state.doc,"bottom").points.map(p=>p.x))===38'));check(page.evaluate('JSON.stringify(CBAPP.state.doc.parts)')==parts)
 test('Board resize refollows and refills the plane without scaling components',resize)
 def manual():
  reset('(()=>{const d='+BASE+';d.zones.push({id:"manual",net:d.nets[0].id,layer:"top",points:CB.G.rect(3,3,8,8),thermal:false,gap:.3,spoke:.5,step:.25});CB.Planes.refill(d);return d;})()')
  act('ground-plane');stable();check(page.evaluate('CBAPP.state.doc.zones.some(z=>z.id==="manual"&&!z.boardPlane&&z.fill.area>0)'))
 test('Ground preset preserves existing manual copper zones',manual)
 def off():
  reset();page.uncheck('#autoPlanes');page.locator('[data-panel=board]').click();page.fill('[data-board=width]','34');page.locator('[data-board=width]').press('Tab');stable(False)
  check(page.evaluate('CBAPP.state.doc.zones.every(z=>!z.fill)'))
  check(page.evaluate('(()=>{try{CB.M.files(CBAPP.state.doc);return false}catch(e){return /Refill/.test(e.message)}})()'))
  page.locator('[data-panel=planes]').click();act('fill-zones');stable();check(page.evaluate('CBAPP.state.doc.settings.autoPlanes===false'))
 test('Auto-refill can be disabled; stale fabrication is blocked until a manual refill',off)
 def change():
  reset('(()=>{const d='+SEED+';CB.newNet(d,"POWER");return d;})()');old=page.evaluate('CBAPP.state.doc.parts[0].pads[0].net');new=page.evaluate('CBAPP.state.doc.nets[1].id')
  page.select_option('[data-plane-net=bottom]',new);check('keep their original nets' in page.locator('#modalBody').inner_text());page.get_by_role('button',name='Change plane net',exact=True).click();stable()
  check(page.evaluate('CBAPP.state.doc.parts[0].pads[0].net')==old)
 test('Changing plane assignment requires confirmation and retains existing lead nets',change)
 def split():
  reset(json.dumps(json.loads((OUT/'fixtures/planes/split/project.json').read_text())));check('2 separate copper regions' in page.locator('.plane-card.bottom').inner_text())
  page.locator('[data-plane-inspect=bottom]').click();page.wait_for_selector('#modal[open]');check('Isolated copper region' in page.locator('#modalBody').inner_text());close()
 test('Connections report exposes real disconnected plane islands, not just matching net names',split)
 def display():
  reset();files=page.evaluate('JSON.stringify(CB.M.files(CBAPP.state.doc))');page.uncheck('#showPlanes');check(page.evaluate('!CBAPP.state.showPlanes'));check(page.evaluate('JSON.stringify(CB.M.files(CBAPP.state.doc))')==files)
  page.check('#showPlanes');page.locator('[data-plane-view=bottom]').click();check(page.evaluate('CBAPP.state.side==="bottom" && CBAPP.state.view==="copper"'))
 test('Hide-fill and face-view controls do not alter manufacturing copper',display)
 def backup():
  reset();preview();accept();act('save');raw=page.evaluate('async()=>await __exports.at(-1).blob.text()');d=json.loads(raw);check(d['schema']==5 and d['zones'][0]['boardPlane'] and d['vias'])
  page.locator('#fileInput').set_input_files({'name':'planes.json','mimeType':'application/json','buffer':raw.encode()});page.get_by_role('button',name='Open this board',exact=True).click();stable()
  check(page.evaluate('CB.Planes.list(CBAPP.state.doc).length===1 && CBAPP.state.planeReport[0].connected===2'))
 test('Schema-3 backup and actual file-input import retain planes and verified attachments',backup)
 def settings():
  reset();page.locator('[data-plane-settings=bottom]').click();page.uncheck('#planeThermal');page.fill('#planeGap','.4');page.get_by_role('button',name='Apply settings',exact=True).click();stable()
  check(page.evaluate('CB.Planes.get(CBAPP.state.doc,"bottom").thermal===false && CB.Planes.get(CBAPP.state.doc,"bottom").gap===.4'))
 test('Per-face thermal settings persist and trigger a new fill',settings)
 def captured():
  reset('CB.example()');act('ground-plane');stable();preview(53,32)
  page.evaluate("document.getElementById('toast').hidden=true;document.getElementById('tooltip').hidden=true;")
  page.mouse.move(1590,1030);page.screenshot(path=str(IMAGES/'plane-connection.png'));accept();page.locator('[data-view=bench]').click()
  page.evaluate("document.getElementById('toast').hidden=true;document.getElementById('tooltip').hidden=true")
  page.screenshot(path=str(IMAGES/'planes-bench.png'));page.locator('[data-plane-view=bottom]').click();page.screenshot(path=str(IMAGES/'planes-copper.png'))
  check('4 / 4 leads connected' in page.locator('.plane-card.bottom').inner_text())
 test('Screenshots show real plane preview, accepted 3D board and copper-face views',captured)
 def mobile():
  reset();page.set_viewport_size({'width':430,'height':850});act('planes');check(page.locator('[data-plane-net=bottom]').is_visible())
  check(page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),'Horizontal overflow')
  page.screenshot(path=str(IMAGES/'planes-mobile.png'));page.set_viewport_size({'width':1600,'height':1050})
 test('Plane assignment controls remain reachable on a narrow screen',mobile)
 test('No external runtime requests or uncaught exceptions in plane workflows',lambda:check(not errors and not [r for r in requests if r.startswith('http')],str(errors)))
 record={'version':page.evaluate('CB.VERSION'),'date':datetime.now(timezone.utc).isoformat(),'passed':sum(r['pass'] for r in results),'total':len(results),'scope':'Actual Chromium controls/canvas/workers with simulated localStorage and captured download blobs. Not a hosted service-worker or file-origin persistence test.','results':results}
 (OUT/'plane-browser-results.json').write_text(json.dumps(record,indent=2));print(f"{record['passed']}/{record['total']} plane browser tests passed.");browser.close()
sys.exit(0 if record['passed']==record['total'] else 1)

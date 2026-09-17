#!/usr/bin/env python3
"""Real Chromium platform UI regressions in the same embedded harness as v1.0.
Storage is simulated; download blobs are intercepted. No claim of native file
persistence, hosted service-worker execution, CAM approval or physical fit.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, time, traceback
from playwright.sync_api import sync_playwright
from browser_support import launch_chromium
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tests/output'; IMAGES=OUT/'images'; IMAGES.mkdir(parents=True,exist_ok=True)
results=[]
STORE="""()=>{window.__store={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>__store[k]??null,setItem:(k,v)=>__store[k]=String(v),removeItem:k=>delete __store[k]}});window.__blobs=new Map;window.__exports=[];const orig=URL.createObjectURL;URL.createObjectURL=function(b){const u=orig.call(URL,b);__blobs.set(u,b);return u};}"""
with sync_playwright() as pw:
    browser=launch_chromium(pw)
    page=browser.new_page(viewport={'width':1600,'height':1050},device_scale_factor=1)
    page.set_default_timeout(10000);errors=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:requests.append(r.url))
    page.evaluate(STORE)
    page.set_content((ROOT/'COPPERBENCH-portable.html').read_text(),wait_until='load')
    page.evaluate("document.addEventListener('click',e=>{const a=e.target.closest('a[download]');if(a){e.preventDefault();__exports.push({name:a.download,blob:__blobs.get(a.href)})}},true)")
    page.wait_for_function('CBAPP?.ready && CBAPP.state.checkRevision===CBAPP.state.revision',timeout=20000)
    def check(cond,msg='Assertion failed'):
        if not cond: raise AssertionError(msg)
    def test(name,fn):
        start=time.perf_counter()
        try: fn();results.append({'name':name,'pass':True,'ms':round(1000*(time.perf_counter()-start))});print('PASS',name,flush=True)
        except Exception as e:
            results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,str(e),flush=True)
            page.screenshot(path=str(OUT/f'platform-failure-{len(results)}.png'));traceback.print_exc()
    def act(name): page.locator(f'button[data-action="{name}"]:visible').first.click()
    def close():
        if page.locator('#modal').evaluate('(e)=>e.open'):page.locator('#modalClose').click()
    def reset(expr='CB.blank()'):
        close();page.evaluate('CBAPP.load('+expr+')');page.keyboard.press('Escape');page.locator('[data-panel=parts]').click()
        page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision',timeout=20000)
    def new(family='pi40',role='addon',holes=True):
        close();page.locator('[data-panel=parts]').click();act('platforms')
        page.locator('[data-family-choice="'+family+'"]').click();page.select_option('#platformRole',role)
        page.locator('#platformHoles').set_checked(holes)
        page.get_by_role('button',name='Start new board',exact=True).click()
        page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision',timeout=20000)
    def world(x,y):return page.evaluate('p=>{let r=CBAPP.renderer;r.setup();let q=r.project(p),b=r.canvas.getBoundingClientRect();return{x:q.x+b.left,y:q.y+b.top}}',{'x':x,'y':y})
    def point(x,y):
        p=world(x,y);page.mouse.click(p['x'],p['y']);page.wait_for_timeout(60)
    def catalogue():
        reset();page.locator('[data-filter=Platforms]').click()
        check(page.locator('[data-place]').count()==6)
        page.locator('#partSearch').fill('MKR');check(page.locator('[data-place]').count()==2)
        page.locator('#partSearch').fill('');page.screenshot(path=str(IMAGES/'platform-parts.png'))
    test('Platforms category exposes six searchable add-on/carrier parts',catalogue)
    def chooser():
        act('platforms');check(page.locator('[data-family-choice]').count()==3)
        page.locator('[data-family-choice="uno-r3"]').click()
        check('4.064' in page.locator('#platformSummary').inner_text())
        check(page.locator('[data-family-choice=\"uno-r3\"]').get_attribute('aria-pressed')=='true')
        check(page.locator('[data-family-choice=pi40]').get_attribute('aria-pressed')=='false')
        page.screenshot(path=str(IMAGES/'platform-chooser.png'));close()
    test('Platform chooser renders a preview and explains nominal dimensions',chooser)
    def templates():
        for fam,count in [('pi40',40),('uno-r3',32),('mkr',28)]:
            new(fam)
            check(page.evaluate(f'CBAPP.state.doc.parts[0].pads.length==={count} && CBAPP.state.doc.parts[0].side==="bottom" && CBAPP.state.doc.parts[0].locked'))
            check(page.evaluate('CB.mountingHoles(CBAPP.state.doc).length===4'))
        new('mkr','carrier',False)
        check(page.evaluate('CBAPP.state.doc.parts[0].side==="top" && CBAPP.state.doc.board.width===81.5 && CB.mountingHoles(CBAPP.state.doc).length===0'))
        page.screenshot(path=str(IMAGES/'mkr-carrier.png'))
    test('Every family creates an editable template; MKR carrier applies margin and hole options',templates)
    def undo_new():
        reset("(()=>{let d=CB.blank();d.title='Original bench';return d;})()")
        new('uno-r3');act('undo');check(page.evaluate('CBAPP.state.doc.title==="Original bench" && CBAPP.state.doc.parts.length===0'))
        act('redo');check(page.evaluate('CBAPP.state.doc.parts[0].platform.family==="uno-r3"'))
    test('Starting a template is undoable and restores the previous project',undo_new)
    def transforms():
        new('uno-r3');before=page.evaluate('CB.mountingHoles(CBAPP.state.doc).map(p=>[p.x,p.y])')
        page.locator('input[data-prop=locked]').uncheck();page.keyboard.press('r')
        check(page.evaluate('CBAPP.state.doc.parts[0].rotation===90'))
        after=page.evaluate('CB.mountingHoles(CBAPP.state.doc).map(p=>[p.x,p.y])');check(before!=after)
        page.keyboard.press('f');check(page.evaluate('CBAPP.state.doc.parts[0].side==="top"'))
        act('undo');check(page.evaluate('CBAPP.state.doc.parts[0].side==="bottom"'))
    test('Unlock, rotate and flip controls move the compound header and its mounts',transforms)
    def reference_options():
        new('uno-r3');before=page.evaluate('JSON.stringify(CB.M.files(CBAPP.state.doc))')
        act('platform-details');page.locator('#platformShowHost').uncheck();page.locator('#platformShowPins').uncheck()
        page.get_by_role('button',name='Apply reference options').click()
        check(page.evaluate('JSON.stringify(CB.M.files(CBAPP.state.doc))')==before)
        act('platform-details');page.locator('#platformMounts').uncheck();page.get_by_role('button',name='Apply reference options').click()
        check(page.evaluate('CB.mountingHoles(CBAPP.state.doc).length===0'))
    test('Reference visibility is manufacturing-neutral; mounting-hole toggle updates real NPTH',reference_options)
    def existing_board():
        reset();before=page.evaluate('JSON.stringify(CBAPP.state.doc.board)')
        act('platforms');page.locator('[data-family-choice=mkr]').click();page.select_option('#platformRole','carrier')
        page.get_by_role('button',name='Place headers on current board',exact=True).click();point(40,27);page.keyboard.press('Escape')
        check(page.evaluate('CBAPP.state.doc.parts.length===1 && CBAPP.state.doc.parts[0].side==="top"'))
        check(page.evaluate('JSON.stringify(CBAPP.state.doc.board)')==before)
        check(page.evaluate('CB.mountingHoles(CBAPP.state.doc).length===0'))
    test('Place-on-current-board leaves the board boundary and existing data intact',existing_board)
    def pin_search():
        new('pi40');page.locator('[data-panel=nets]').click();act('connections-table')
        page.locator('#pinSearch').fill('GPIO17');check(page.locator('#pinRows tr').count()==1)
        check('GPIO17' in page.locator('#pinRows').inner_text())
        page.locator('#pinRows input[type=checkbox]').check();check(page.evaluate('CBAPP.state.selectedPads.length===1'));close()
    test('Searchable pin table finds GPIO aliases and selects the actual connector pad',pin_search)
    def route_gpio():
        reset("(()=>{let d=CB.Platforms.template('pi40'),p=CB.makePart(d,'testpoint',21.07,16);p.label.visible=false;d.parts.push(p);let n=CB.newNet(d,'GPIO17');CB.assignPads(d,[d.parts[0].id+':10',p.id+':0'],n);return d;})()")
        page.locator('[data-view=copper]').click();page.locator('[data-tool=connect]').click();point(21.07,4.77);point(21.07,16)
        check(page.evaluate('CBAPP.state.selectedPads.length===2'))
        act('autowire');page.wait_for_function('CBAPP.state.routePreview!==null',timeout=20000);act('accept-route')
        page.wait_for_function('CBAPP.state.connectivity?.unrouted===0',timeout=20000)
        check(page.evaluate('CBAPP.state.doc.traces.length>0'))
        page.locator('[data-view=bench]').click();page.screenshot(path=str(IMAGES/'pi-hat-routed.png'))
    test('Locked Pi interface pads can be clicked and routed to a new component',route_gpio)
    def csv():
        new('uno-r3');act('platform-pin-csv')
        page.wait_for_function('__exports.length>0')
        data=page.evaluate('async()=>{let x=__exports[__exports.length-1];return{name:x.name,text:await x.blob.text()}}')
        check(data['name'].endswith('-pins.csv'));check('"DIGITAL8.8","D0 / RX"' in data['text'])
        check(len(data['text'].strip().splitlines())==33)
        page.screenshot(path=str(IMAGES/'uno-shield.png'))
    test('Pin-map CSV download contains physical IDs, signal names and top-view coordinates',csv)
    def native_save():
        act('save');page.wait_for_function('__exports[__exports.length-1].name.endsWith(".json")')
        check(page.evaluate('async()=>{let d=JSON.parse(await __exports[__exports.length-1].blob.text());return d.parts[0].platform.family==="uno-r3" && d.parts[0].mountingHoles.length===4 && d.parts[0].pads[0].signal==="NC";}'))
    test('Native JSON download preserves embedded platform metadata and linked holes',native_save)
    def narrow():
        page.set_viewport_size({'width':480,'height':850});act('toggle-drawer');act('platforms');page.wait_for_timeout(100)
        check(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        check(page.locator('#modal').evaluate('e=>e.scrollWidth<=e.clientWidth+1'))
        page.screenshot(path=str(IMAGES/'platform-mobile.png'));close();page.set_viewport_size({'width':1600,'height':1050})
    test('Platform workflow stays within the narrow-screen viewport',narrow)
    test('No uncaught errors or external runtime asset requests',lambda:(check(not errors,str(errors)),check(not [r for r in requests if r.startswith(('http:','https:'))],str(requests))))
    browser.close()
OUT.mkdir(exist_ok=True)
record={'version':'1.1.0','date':datetime.now(timezone.utc).isoformat(),'passed':sum(x['pass'] for x in results),'total':len(results),'environment':'Chromium embedded about:blank; Storage test double; intercepted download blobs','results':results}
(OUT/'platform-browser-results.json').write_text(json.dumps(record,indent=2))
print(json.dumps({k:record[k] for k in ('passed','total')},indent=2))
raise SystemExit(0 if all(x['pass'] for x in results) else 1)

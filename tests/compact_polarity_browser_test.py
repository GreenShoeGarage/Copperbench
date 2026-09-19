#!/usr/bin/env python3
"""Context-only compact polarity labels, print controls, and actual silk readback.

Real Chromium DOM/canvas/worker interactions; explicit storage and download-blob
harness. No real-origin persistence, hosted offline, or physical PCB claim.
"""
from pathlib import Path
import ast,json,time,traceback
from playwright.sync_api import sync_playwright
from browser_support import launch_chromium
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';IMAGES=OUT/'images';IMAGES.mkdir(parents=True,exist_ok=True)
DOC=json.loads((OUT/'fixtures/compact-polarity/demo.json').read_text());results=[];errors=[];requests=[]
module=ast.parse((ROOT/'tests/browser_test.py').read_text());STORE=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='STORE' for t in n.targets))
with sync_playwright() as pw:
    browser=launch_chromium(pw);page=browser.new_page(viewport={'width':1600,'height':1050},device_scale_factor=1);page.set_default_timeout(12000)
    page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
    page.evaluate(STORE,{});page.set_content((ROOT/'COPPERBENCH-portable.html').read_text(),wait_until='load')
    page.evaluate("document.addEventListener('click',e=>{const a=e.target.closest('a[download]');if(a){e.preventDefault();__exports.push({name:a.download,blob:__blobs.get(a.href)})}},true)")
    page.wait_for_function('window.CBAPP?.ready && CBAPP.state.checkRevision===CBAPP.state.revision',timeout=30000)
    def check(ok,msg='Assertion failed'):
        if not ok:raise AssertionError(msg)
    def act(a):page.locator(f'[data-action="{a}"]:visible').first.click()
    def stable():page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision && !CBAPP.state.job',timeout=30000)
    def close():
        if page.locator('#modal').evaluate('(e)=>e.open'):page.locator('#modalClose').click()
    def reset(doc=DOC):
        close();page.set_viewport_size({'width':1600,'height':1050});page.keyboard.press('Escape');page.evaluate('d=>CBAPP.load(d)',doc);page.keyboard.press('Escape')
        page.locator('[data-view=bench]').click();page.locator('[data-side=top]').click()
        page.evaluate("CBAPP.state.tilt=27;CBAPP.state.yaw=0;CBAPP.state.selection=[];CBAPP.state.selectedPads=[];CBAPP.state.hoverPad=null;CBAPP.renderer.fit();document.getElementById('inspector').classList.remove('collapsed')");stable()
    def choose(index=1):
        q=page.evaluate('i=>{const r=CBAPP.renderer;r.setup();const p=CBAPP.state.doc.parts[i],q=r.project(p),b=r.canvas.getBoundingClientRect();return{x:q.x+b.left,y:q.y+b.top}}',index)
        page.mouse.click(q['x'],q['y']);page.wait_for_selector('#inspector [data-action=polarity]');page.mouse.move(1550,50);page.evaluate('CBAPP.renderer.draw()')
    def tags():return page.evaluate('CBAPP.renderer.polarityHitLabels.filter(a=>a.mode==="tag")')
    def shot(name):
        page.mouse.move(1550,50);page.evaluate("document.getElementById('toast').hidden=true;document.getElementById('tooltip').hidden=true;CBAPP.renderer.draw()");page.screenshot(path=str(IMAGES/name))
    def test(name,fn):
        t=time.perf_counter()
        try:fn();results.append({'name':name,'pass':True,'ms':round((time.perf_counter()-t)*1000)});print('PASS',name,flush=True)
        except Exception as e:results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,e,flush=True);traceback.print_exc();page.screenshot(path=str(IMAGES/f'compact-failure-{len(results)}.png'))
    def idle():
        reset();check(len(tags())==0,'Idle badges were not removed');check(page.evaluate('CB.silkStrokes(CBAPP.state.doc).filter(s=>s.polarity).length')>0);shot('compact-polarity-idle.png')
    test('Idle bench uses the printable symbols without floating A/K billboards',idle)
    def selected():
        reset();choose();ts=tags();check(len(ts)==2);check({x['text'] for x in ts}=={'A','K'});check(all(x['fontSize']==9 and x['w']<=14 and x['h']<=14 for x in ts));check('Anode' in page.locator('#inspector').inner_text());shot('compact-polarity-selected.png')
    test('Selecting a tall LED shows only 9-pixel A/K tags, never expanded full-name badges',selected)
    def no_overlap():
        reset();choose()
        for tilt in [0,27,65]:
            for yaw in [0,90,180,270]:
                result=page.evaluate('''([tilt,yaw])=>{const r=CBAPP.renderer,s=CBAPP.state;s.tilt=tilt;s.yaw=yaw;r.draw();const tags=r.polarityHitLabels.filter(a=>a.mode==='tag');let ok=true;for(const p of s.doc.parts){const ps=[];for(const z of [0,p.body.z+.3])for(const x of [-p.body.w/2,p.body.w/2])for(const y of [-p.body.h/2,p.body.h/2])ps.push(r.project(CB.world(p,{x,y}),z));const b={minX:Math.min(...ps.map(p=>p.x)),maxX:Math.max(...ps.map(p=>p.x)),minY:Math.min(...ps.map(p=>p.y)),maxY:Math.max(...ps.map(p=>p.y))};for(const t of tags)if(t.x+t.w/2>b.minX && t.x-t.w/2<b.maxX && t.y+t.h/2>b.minY && t.y-t.h/2<b.maxY)ok=false;}return {ok,count:tags.length};}''',[tilt,yaw])
                check(result['ok'],f'Tag covers projected body at {tilt}/{yaw}');check(result['count']>0)
    test('Tags avoid all projected component bodies at twelve tilt/orbit combinations',no_overlap)
    def print_size():
        reset();choose();act('polarity');page.fill('#polaritySize','6');page.get_by_role('button',name='Apply polarity labels',exact=True).click();stable();check(all(t['fontSize']==9 and t['w']==14 for t in tags()));check(page.evaluate('CB.polarityOptions(CBAPP.state.doc.parts[1]).size')==6)
    test('Large custom print settings cannot enlarge editor tags',print_size)
    def zoom():
        reset();choose();page.evaluate('CBAPP.renderer.scale=80;CBAPP.renderer.draw()');check(all(t['fontSize']==9 for t in tags()));page.evaluate('CBAPP.renderer.scale=1;CBAPP.renderer.draw()');check(all(t['fontSize']==9 for t in tags()))
    test('Zooming never scales up the screen-space tag typography',zoom)
    def checkbox():
        reset();choose();key=page.evaluate('CBAPP.state.doc.parts[1].id');before=page.evaluate('JSON.stringify(CBAPP.state.doc.parts[1].pads)');page.locator('[data-polarity-print]').uncheck();stable()
        check(page.evaluate('id=>CB.silkStrokes(CBAPP.state.doc).filter(s=>s.owner===id&&s.polarity).length',key)==0);check(len(tags())==2)
        page.locator('[data-polarity-print]').check();stable();check(page.evaluate('id=>CB.silkStrokes(CBAPP.state.doc).filter(s=>s.owner===id&&s.polarity).length',key)>0);check(page.evaluate('JSON.stringify(CBAPP.state.doc.parts[1].pads)')==before)
        act('undo');stable();choose();check(not page.locator('[data-polarity-print]').is_checked());act('redo');stable();choose();check(page.locator('[data-polarity-print]').is_checked())
    test('Direct silkscreen checkbox changes printing only and supports undo/redo',checkbox)
    def defaults():
        reset();choose();act('polarity');page.fill('#polaritySize','3');page.fill('#polarityX','4');page.uncheck('#polarityPrint');page.get_by_role('button',name='Compact print defaults',exact=True).click();check(page.locator('#polaritySize').input_value()=='0.9');check(page.locator('#polarityX').input_value()=='0');check(page.locator('#polarityPrint').is_checked());page.get_by_role('button',name='Apply polarity labels',exact=True).click();stable();check(page.evaluate('CB.polarityOptions(CBAPP.state.doc.parts[1]).size')==.9)
    test('Compact print defaults restores small enabled marks without reassigning roles',defaults)
    def hover():
        reset();choose();q=page.evaluate('()=>{const r=CBAPP.renderer,t=r.polarityHitLabels.find(t=>t.mode==="tag"&&t.role==="cathode"),b=r.canvas.getBoundingClientRect();return {x:t.x+b.left,y:t.y+b.top,id:t.padId}}');page.mouse.move(q['x'],q['y']);page.wait_for_function('document.getElementById("tooltip").textContent.includes("Cathode")');check(page.evaluate('CBAPP.state.hoverPad')==q['id']);check(all(t['text'] in ['A','K'] for t in tags()))
    test('Full cathode identity stays in the tooltip without expanding its board label',hover)
    def clicking():
        reset();page.locator('[data-tool=connect]').first.click();page.evaluate('CBAPP.renderer.draw()');q=page.evaluate('()=>{const r=CBAPP.renderer,t=r.polarityHitLabels.find(t=>t.mode==="tag"&&t.role==="anode"),b=r.canvas.getBoundingClientRect();return {x:t.x+b.left,y:t.y+b.top,id:t.padId}}');page.mouse.click(q['x'],q['y']);check(q['id'] in page.evaluate('CBAPP.state.selectedPads'));page.keyboard.press('Escape')
    test('Small tags remain clickable targets for the exact electrical pad',clicking)
    def readback():
        reset();before=page.evaluate('CBAPP.exportFiles()');page.locator('[data-view=fabrication]').click();act('fab-silk-top');check(len(tags())==0);check(page.evaluate('CBAPP.exportFiles()')==before)
        # Every role stroke has matching dark line geometry in the actual generated layer.
        check(page.evaluate('''()=>{const d=CBAPP.state.doc,g=CBAPP.state.fabData['board-F_Silkscreen.gbr'];return CB.silkStrokes(d).filter(s=>s.polarity).every(s=>s.points.slice(1).every((p,i)=>g.objects.some(o=>o.kind==='line'&&o.polarity==='dark'&&Math.hypot(o.a.x-s.points[i].x,o.a.y-(d.board.height-s.points[i].y))<.00001&&Math.hypot(o.b.x-p.x,o.b.y-(d.board.height-p.y))<.00001)));}'''))
        shot('compact-polarity-silkscreen.png')
    test('Fabrication reads actual small role glyphs with no editor overlays or camera-induced file changes',readback)
    def bottom():
        reset();choose();act('flip');stable();page.locator('[data-view=fabrication]').click();act('fab-silk-bottom');check(page.evaluate('CBAPP.state.fabData["board-B_Silkscreen.gbr"].objects.some(o=>o.polarity==="dark")'));check(len(tags())==0);shot('compact-polarity-bottom.png')
    test('Flipping the component moves the printable marks to the bottom Gerber',bottom)
    def rgb():
        reset();choose(4);check(len(tags())==4);check(len(set((round(t['x']),round(t['y'])) for t in tags()))==4);shot('compact-polarity-rgb.png')
    test('Four-terminal RGB LEDs receive separate compact labels, not overlapping A/K pairs',rgb)
    def mobile():
        reset();page.set_viewport_size({'width':390,'height':844});page.locator('[data-tool=connect]').first.click();page.evaluate('CBAPP.renderer.fit()');check(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'));check(all(t['fontSize']==9 for t in tags()));check(page.evaluate('()=>{const r=CBAPP.renderer,d=CBAPP.state.doc;return d.parts.filter(p=>p.libraryId.includes("rgb")).every(p=>{const a=r.polarityHitLabels.filter(t=>t.mode==="tag"&&t.padId.startsWith(p.id+":"));return a.length>=3&&Math.max(...a.map(t=>t.y))-Math.min(...a.map(t=>t.y))<35;});}'),'RGB labels were stacked far from their component');shot('compact-polarity-mobile.png')
    test('Narrow-screen routing retains bounded labels without page overflow',mobile)
    def themes():
        reset();choose();page.evaluate("document.documentElement.dataset.theme='contrast';CBAPP.renderer.draw()");check(len(tags())==2);shot('compact-polarity-contrast.png');page.evaluate("document.documentElement.dataset.theme='dark';CBAPP.renderer.draw()");check(len(tags())==2);shot('compact-polarity-dark.png')
    test('Compact labels remain present in high-contrast and dark themes',themes)
    test('No uncaught browser errors or remote runtime requests',lambda:(check(not errors,str(errors)),check(not [r for r in requests if r.startswith(('http:','https:'))],str(requests))))
    browser.close()
(OUT/'compact-polarity-browser-results.json').write_text(json.dumps({'total':len(results),'passed':sum(r['pass'] for r in results),'results':results},indent=2))
print(f"{sum(r['pass'] for r in results)}/{len(results)} browser checks passed.")
raise SystemExit(0 if all(r['pass'] for r in results) else 1)

#!/usr/bin/env python3
"""Camera navigation regression checks with real Chromium mouse/keyboard/touch events.

Storage is an injected test double. Touch gestures use Chromium's input protocol,
not physical hardware. No browser policy changes or network services are required.
"""
from pathlib import Path
import json
import time
import traceback
from playwright.sync_api import sync_playwright
from browser_support import launch_chromium

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'tests/output'
IMAGES = OUTPUT / 'images'
IMAGES.mkdir(parents=True, exist_ok=True)
STORE = """() => {const m=new Map;Object.defineProperty(window,'localStorage',{value:{getItem:k=>m.get(k)??null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k)}});} """
FIXTURE = """(()=>{const d=CB.blank();d.title='Pan view regression';d.board.width=60;d.board.height=40;d.board.shape='rect';const n=CB.newNet(d,'LINK');for(const [x,y] of [[15,24],[45,24]]){const p=CB.makePart(d,'testpoint',x,y);p.pads[0].net=n;p.label.visible=false;d.parts.push(p);}d.parts.push(CB.makePart(d,'r-axial',30,12));return d;})()"""
results = []
with sync_playwright() as pw:
    browser = launch_chromium(pw)
    page = browser.new_page(viewport={'width':1500,'height':1000}, has_touch=True, device_scale_factor=1)
    page.set_default_timeout(10000)
    errors, requests = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('request', lambda r: requests.append(r.url))
    page.evaluate(STORE)
    page.set_content((ROOT/'COPPERBENCH-portable.html').read_text(), wait_until='load')
    page.wait_for_function('window.CBAPP?.ready && CBAPP.state.checkRevision===CBAPP.state.revision')
    cdp = page.context.new_cdp_session(page)

    def check(ok, message='Assertion failed'):
        if not ok:
            raise AssertionError(message)

    def near(a, b, message='', tolerance=.15):
        check(abs(a-b)<tolerance, f'{message}: {a} != {b}')

    def test(name, fn):
        start=time.perf_counter()
        try:
            fn()
            results.append({'name':name,'pass':True,'ms':round((time.perf_counter()-start)*1000)})
            print('PASS',name,flush=True)
        except Exception as e:
            results.append({'name':name,'pass':False,'error':str(e)})
            print('FAIL',name,e,flush=True)
            traceback.print_exc()
            page.screenshot(path=str(IMAGES/f'pan-failure-{len(results)}.png'))
            # Release all physical test inputs so one failure does not poison later cases.
            for key in ['Space','Alt','Shift','Control','Meta']:
                page.keyboard.up(key)
            page.mouse.up()
            page.mouse.up(button='middle')
            try:
                cdp.send('Input.dispatchTouchEvent',{'type':'touchCancel','touchPoints':[]})
            except Exception:
                pass

    def close():
        if page.locator('#modal').evaluate('(e)=>e.open'):
            page.locator('#modalClose').click()

    def reset():
        close()
        page.set_viewport_size({'width':1500,'height':1000})
        page.evaluate('CBAPP.load('+FIXTURE+');CBAPP.state.tilt=27;CBAPP.state.yaw=0;CBAPP.state.side="top";CBAPP.renderer.fit()')
        page.keyboard.press('Escape')
        page.locator('[data-panel=parts]').click()
        page.locator('#partSearch').fill('')
        page.select_option('#partCategory','All')
        page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision && !CBAPP.state.job')
        page.locator('#canvas').focus()
        page.evaluate("document.getElementById('toast').hidden=true")

    def point(x=30,y=20):
        return page.evaluate('p=>{const r=CBAPP.renderer;r.setup();const q=r.project(p),b=r.canvas.getBoundingClientRect();return {x:q.x+b.left,y:q.y+b.top}}',{'x':x,'y':y})

    def camera():
        return page.evaluate('({x:CBAPP.renderer.panX,y:CBAPP.renderer.panY,s:CBAPP.renderer.scale,tilt:CBAPP.state.tilt,yaw:CBAPP.state.yaw})')

    def stable():
        return page.evaluate('JSON.stringify({doc:CBAPP.state.doc,h:CBAPP.state.history,f:CBAPP.state.future,rev:CBAPP.state.revision,selection:CBAPP.state.selection,pads:CBAPP.state.selectedPads,drawing:CBAPP.state.drawing,placing:CBAPP.state.placing,block:CBAPP.state.blockPlacing,via:CBAPP.state.viaPending})')

    def drag(p=None,dx=85,dy=47,button='left'):
        p=p or point()
        page.mouse.move(p['x'],p['y'])
        page.mouse.down(button=button)
        check(page.locator('#canvas').evaluate('e=>getComputedStyle(e).cursor')=='grabbing','Missing grabbing cursor')
        page.mouse.move(p['x']+dx,p['y']+dy,steps=5)
        page.mouse.up(button=button)
        page.wait_for_timeout(35)

    def touch(kind, points):
        cdp.send('Input.dispatchTouchEvent', {'type':kind,'touchPoints':[{'id':i,'x':p['x'],'y':p['y'],'radiusX':5,'radiusY':5,'force':1} for i,p in points]})

    def two_finger(dx=70,dy=35,scale=1):
        a=point(24,20);b={'x':a['x']+100,'y':a['y']}
        mid={'x':(a['x']+b['x'])/2,'y':a['y']}
        touch('touchStart',[(0,a)])
        touch('touchStart',[(0,a),(1,b)])
        touch('touchMove',[(0,{'x':mid['x']-50*scale+dx,'y':mid['y']+dy}), (1,{'x':mid['x']+50*scale+dx,'y':mid['y']+dy})])
        touch('touchEnd',[(1,{'x':mid['x']+50*scale+dx,'y':mid['y']+dy})])
        # Remaining contact must not become a component placement or edit drag.
        touch('touchMove',[(1,{'x':mid['x']+50*scale+dx+10,'y':mid['y']+dy+5})])
        touch('touchEnd',[])
        page.wait_for_timeout(50)
        return mid

    reset()
    def discoverable():
        b=page.get_by_role('button',name='Pan view',exact=True)
        check(b.is_visible());check(b.get_attribute('aria-pressed')=='false')
        b.focus();page.keyboard.press('Enter')
        check(b.get_attribute('aria-pressed')=='true')
        check(page.locator('#toolName').inner_text()=='PAN')
        check(page.locator('#canvas').evaluate('e=>getComputedStyle(e).cursor')=='grab')
        page.keyboard.press('Escape')
        check(not page.evaluate('CBAPP.state.panMode'))
        check(not page.locator('#toolHint').is_visible())
    test('Labelled Pan control is keyboard-operable with pressed and grab states',discoverable)

    for view in ['bench','copper','fabrication']:
        for side in ['top','bottom']:
            def each(view=view,side=side):
                reset()
                page.locator(f'[data-side={side}]').click()
                page.locator(f'[data-view={view}]').click()
                page.locator('#panButton').click()
                before=stable();cam=camera();files=page.evaluate('JSON.stringify(CBAPP.exportFiles())')
                drag(point(30,12))
                after=camera();near(after['x']-cam['x'],85);near(after['y']-cam['y'],47)
                near(after['s'],cam['s']);check(stable()==before,'Navigation changed project/edit state')
                check(page.evaluate('JSON.stringify(CBAPP.exportFiles())')==files,'Export changed')
                check(page.evaluate('CBAPP.state.view')==view)
            test(f'Pan moves only the camera in {view}, {side} face, even over a component',each)

    def middle():
        reset();before=stable();p=point();cam=camera();drag(p,button='middle')
        near(camera()['x']-cam['x'],85);check(stable()==before)
        check(page.evaluate('CBAPP.state.tool')=='select');check(not page.evaluate('CBAPP.state.panMode'))
    test('Middle-button drag pans without selecting or moving a part',middle)

    def temporary_placement():
        reset();page.locator('[data-place=r-axial]').click();before=stable()
        page.keyboard.down('Space');drag(point(30,12));page.keyboard.up('Space')
        check(stable()==before);check(page.evaluate('CBAPP.state.placing')=='r-axial')
        check(page.locator('#canvas').evaluate('e=>getComputedStyle(e).cursor')=='copy')
        p=point(40,33);page.mouse.click(p['x'],p['y'])
        check(page.evaluate('CBAPP.state.doc.parts.length')==4)
    test('Space-drag preserves a pending part and permits subsequent placement',temporary_placement)

    def unfinished_trace():
        reset();page.keyboard.press('t');p=point(15,24);page.mouse.click(p['x'],p['y'])
        check(page.evaluate('!!CBAPP.state.drawing'))
        before=stable();page.keyboard.press('p');drag(point(30,20));page.keyboard.press('Escape')
        check(stable()==before);check(page.evaluate('CBAPP.state.tool')=='trace')
        p=point(45,24);page.mouse.click(p['x'],p['y'])
        check(page.evaluate('CBAPP.state.doc.traces.length')==1,'Trace did not finish at reprojected pin')
    test('Pan can suspend and resume a live trace with no added waypoint or net',unfinished_trace)

    def fit():
        reset();page.keyboard.press('p');drag(dx=240,dy=-70)
        page.locator('[data-action=fit]').click();near(camera()['x'],0);near(camera()['y'],0)
        drag(dx=-100,dy=40);page.keyboard.press('Home');near(camera()['x'],0);near(camera()['y'],0)
    test('Fit and Home recover the board after moving it away from the centre',fit)

    def arrows():
        reset();p=point(30,12);page.mouse.click(p['x'],p['y']);check(page.evaluate('CBAPP.state.selection.length')==1)
        page.keyboard.press('p');before=stable();cam=camera()
        page.keyboard.press('ArrowRight');page.keyboard.press('Shift+ArrowDown')
        near(camera()['x']-cam['x'],40);near(camera()['y']-cam['y'],120);check(stable()==before)
        page.keyboard.press('r');page.keyboard.press('f');page.keyboard.press('Delete');check(stable()==before)
        page.keyboard.press('p');page.keyboard.press('ArrowRight');check(stable()!=before,'Normal nudge was lost')
    test('Arrows pan in Pan mode without nudging, rotating, flipping or deleting selection',arrows)

    def wheel():
        reset();page.keyboard.press('p');p=point();page.mouse.move(p['x'],p['y']);cam=camera();before=stable()
        page.mouse.wheel(45,70);page.wait_for_timeout(75)
        near(camera()['x']-cam['x'],-45);near(camera()['y']-cam['y'],-70);near(camera()['s'],cam['s']);check(stable()==before)
        page.keyboard.down('Control');page.mouse.wheel(0,-100);page.keyboard.up('Control');page.wait_for_timeout(75)
        check(camera()['s']>cam['s']);check(stable()==before)
    test('Scroll pans in Pan mode; Ctrl-scroll still zooms rather than translating',wheel)

    def shift_wheel():
        reset();p=point();page.mouse.move(p['x'],p['y']);cam=camera();before=stable()
        page.keyboard.down('Shift');page.mouse.wheel(0,55);page.keyboard.up('Shift');page.wait_for_timeout(75)
        near(camera()['x']-cam['x'],-55);near(camera()['s'],cam['s']);check(stable()==before)
        page.mouse.wheel(0,-100);page.wait_for_timeout(75);check(camera()['s']>cam['s'])
    test('Shift-scroll pans horizontally while the ordinary Select wheel retains zoom',shift_wheel)

    def wheel_units():
        reset();page.keyboard.press('p');before=stable();cam=camera()
        page.locator('#canvas').dispatch_event('wheel',{'deltaX':2,'deltaY':3,'deltaMode':1})
        near(camera()['x']-cam['x'],-32);near(camera()['y']-cam['y'],-48)
        cam=camera();height=page.evaluate('CBAPP.renderer.h')
        page.locator('#canvas').dispatch_event('wheel',{'deltaY':1,'deltaMode':2})
        near(camera()['y']-cam['y'],-height);check(stable()==before)
    test('Line and page wheel units are normalised, not assumed to be pixels',wheel_units)

    def input_guard():
        reset();page.locator('#partSearch').fill('p');check(not page.evaluate('CBAPP.state.panMode'))
        check(page.locator('#partSearch').input_value()=='p')
        page.locator('#canvas').focus()
        check(not page.locator('#canvas').evaluate("e=>!e.dispatchEvent(new KeyboardEvent('keydown',{key:'p',ctrlKey:true,bubbles:true,cancelable:true}))"),'Ctrl+P was swallowed')
        page.keyboard.press('p');page.locator('#toolHelp').click();check(page.locator('#modalTitle').inner_text()=='Pan tool')
        before=camera();page.keyboard.press('p');check(page.evaluate('CBAPP.state.panMode'));check(camera()==before)
        close();page.keyboard.press('Escape');check(not page.evaluate('CBAPP.state.panMode'))
    test('Typing and browser shortcuts are not hijacked; on-demand Pan help stays available',input_guard)

    def capture():
        reset();page.keyboard.press('p');p=point();before=stable();cam=camera()
        page.mouse.move(p['x'],p['y']);page.mouse.down();page.mouse.move(20,210,steps=6)
        check(page.evaluate('CBAPP.state.drag?.mode')=='pan')
        page.mouse.up();check(not page.evaluate('CBAPP.state.drag'));check(stable()==before)
        near(camera()['x']-cam['x'],20-p['x']);near(camera()['y']-cam['y'],210-p['y'])
    test('Pointer capture keeps panning when the pointer crosses the canvas edge',capture)

    def loss_cancel():
        reset();page.keyboard.down('Space');p=point();page.mouse.move(p['x'],p['y']);page.mouse.down();page.mouse.move(p['x']+50,p['y']+10)
        page.evaluate('window.dispatchEvent(new Event("blur"))');check(not page.evaluate('CBAPP.state.drag'))
        page.mouse.up();page.keyboard.up('Space');check(page.locator('#canvas').evaluate('e=>getComputedStyle(e).cursor')=='default')
        cam=camera();page.mouse.move(p['x']+90,p['y']+50);check(camera()==cam)
        page.keyboard.press('p');p=point();page.mouse.move(p['x'],p['y']);page.mouse.down()
        page.evaluate('const c=CBAPP.renderer.canvas; c.releasePointerCapture(CBAPP.state.drag.pointerId)')
        page.mouse.move(p['x']+30,p['y']);page.mouse.up()
        check(not page.evaluate('CBAPP.state.drag'))
        check(page.locator('#canvas').evaluate('e=>getComputedStyle(e).cursor')=='grab')
    test('Focus and pointer-capture loss cannot leave a stuck dragging cursor',loss_cancel)

    def single_touch():
        reset();page.keyboard.press('p');before=stable();cam=camera();p=point(30,12)
        touch('touchStart',[(0,p)]);touch('touchMove',[(0,{'x':p['x']+80,'y':p['y']+45})]);touch('touchEnd',[])
        near(camera()['x']-cam['x'],80,tolerance=1);near(camera()['y']-cam['y'],45,tolerance=1);check(stable()==before)
    test('One-finger drag in Pan moves the view, not the touched component',single_touch)

    def multi_touch():
        reset();before=stable();cam=camera();two_finger()
        near(camera()['x']-cam['x'],70,tolerance=1);near(camera()['y']-cam['y'],35,tolerance=1);near(camera()['s'],cam['s']);check(stable()==before)
        check(not page.evaluate('CBAPP.state.drag'))
    test('Two-finger translation pans in Select and ignores the remaining lifted finger',multi_touch)

    def pinch():
        reset();before=stable();cam=camera()
        a=point(24,20);centre={'x':a['x']+50,'y':a['y']}
        anchor=page.evaluate('p=>{const r=CBAPP.renderer,b=r.canvas.getBoundingClientRect();return r.unproject(p.x-b.left,p.y-b.top)}',centre)
        two_finger(dx=40,dy=25,scale=1.4)
        near(camera()['s']/cam['s'],1.4,tolerance=.02)
        q=page.evaluate('p=>{const r=CBAPP.renderer;r.setup();const q=r.project(p),b=r.canvas.getBoundingClientRect();return{x:q.x+b.left,y:q.y+b.top}}',anchor)
        near(q['x'],centre['x']+40,tolerance=1);near(q['y'],centre['y']+25,tolerance=1);check(stable()==before)
    test('Touch pinch zoom stays anchored beneath the translating gesture centre',pinch)

    def touch_edit_guard():
        for tool in ['hole','via','trace']:
            reset();page.locator(f'[data-tool={tool}]').first.click();before=stable();two_finger();check(stable()==before,tool+' edited on first touch')
        reset();page.locator('[data-place=r-axial]').click();before=stable();two_finger();check(stable()==before,'Part dropped during pinch')
        p=point(38,30);touch('touchStart',[(0,p)]);touch('touchEnd',[])
        check(page.evaluate('CBAPP.state.doc.parts.length')==4,'Ordinary touch placement failed')
    test('Two-finger gestures cannot drop parts, add holes/vias, or start a trace',touch_edit_guard)

    def selection_drag_rollback():
        reset();before=stable();p=point(30,12)
        touch('touchStart',[(0,p)]);touch('touchMove',[(0,{'x':p['x']+24,'y':p['y']})])
        check(page.evaluate('CBAPP.state.drag?.mode')=='parts')
        touch('touchStart',[(0,{'x':p['x']+24,'y':p['y']}),(1,{'x':p['x']+120,'y':p['y']})])
        touch('touchMove',[(0,{'x':p['x']+40,'y':p['y']+25}),(1,{'x':p['x']+136,'y':p['y']+25})])
        touch('touchEnd',[]);check(stable()==before,'Uncommitted part movement was not rolled back')
    test('A second finger rolls back an uncommitted component drag before navigating',selection_drag_rollback)

    def normal_drag():
        reset();p=point(30,12);page.mouse.move(p['x'],p['y']);page.mouse.down();page.mouse.move(p['x']+40,p['y']+20,steps=4);page.mouse.up()
        check(page.evaluate('CBAPP.state.doc.parts[2].x')!=30)
        page.keyboard.press('Control+z');check(page.evaluate('CBAPP.state.doc.parts[2].x')==30)
        reset();p=point(30,12);touch('touchStart',[(0,p)]);touch('touchMove',[(0,{'x':p['x']+40,'y':p['y']+20})]);touch('touchEnd',[])
        check(page.evaluate('CBAPP.state.doc.parts[2].x')!=30)
    test('Normal mouse and single-touch editing still move parts and remain undoable',normal_drag)

    def phone():
        reset();page.keyboard.press('p')
        for width in [360,390,700,900]:
            page.set_viewport_size({'width':width,'height':840});page.wait_for_timeout(90)
            b=page.locator('#panButton').bounding_box();check(b is not None and b['x']>=0 and b['x']+b['width']<=width,'Pan button off-screen')
            check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
            if width==390:page.screenshot(path=str(IMAGES/'pan-mobile.png'))
        page.set_viewport_size({'width':1500,'height':1000})
    test('Pan stays labelled and reachable at narrow screen widths without page overflow',phone)

    def themes_screenshot():
        reset();project=json.loads((ROOT/'examples/compact-polarity.json').read_text())
        page.evaluate('d=>CBAPP.load(d)',project);page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision')
        page.locator('#panButton').click();drag(dx=75,dy=-25)
        page.evaluate("document.getElementById('toast').hidden=true")
        page.screenshot(path=str(IMAGES/'pan-workbench.png'))
        page.locator('[data-view=copper]').click();page.screenshot(path=str(IMAGES/'pan-copper.png'))
        for theme in ['contrast','dark']:
            page.evaluate('t=>{document.documentElement.dataset.theme=t;CBAPP.state.theme=t;CBAPP.renderer.draw()}',theme)
            check(page.locator('#panButton').is_visible())
            check(page.locator('#panButton').get_attribute('aria-pressed')=='true')
        page.screenshot(path=str(IMAGES/'pan-dark.png'))
    test('Pan has visible active state in light, dark and high-contrast views',themes_screenshot)

    def loading_mid_drag():
        reset();p=point(30,12);page.mouse.move(p['x'],p['y']);page.mouse.down();page.mouse.move(p['x']+40,p['y'],steps=3)
        check(page.evaluate('!!CBAPP.state.drag.before'))
        page.evaluate('const d=CB.blank();d.title="New after drag";CBAPP.load(d)')
        page.mouse.up()
        check(page.evaluate('CBAPP.state.doc.title')=='New after drag')
        check(page.evaluate('CBAPP.state.doc.parts.length')==0)
        check(not page.evaluate('CBAPP.state.drag'))
    test('Loading a document cancels the old tentative drag without restoring it over the new board',loading_mid_drag)

    def stationary_cursor():
        reset();page.keyboard.press('t');page.keyboard.press('p');p=point(30,20);page.mouse.move(p['x'],p['y']);page.mouse.wheel(0,60);page.wait_for_timeout(100)
        expect=page.evaluate('p=>{const r=CBAPP.renderer,b=r.canvas.getBoundingClientRect(),g=CBAPP.state.doc.settings.grid,q=r.unproject(p.x-b.left,p.y-b.top);return{x:CB.q(Math.round(q.x/g)*g),y:CB.q(Math.round(q.y/g)*g)}}',p)
        cursor=page.evaluate('CBAPP.state.cursor');near(cursor['x'],expect['x']);near(cursor['y'],expect['y'])
    test('Scrolling refreshes the board coordinate of a stationary routing cursor',stationary_cursor)

    def clean():
        check(not errors,'Uncaught browser errors: '+str(errors))
        check(not [u for u in requests if u.startswith(('http:','https:'))],'External runtime requests')
    test('Navigation produces no uncaught errors or external runtime requests',clean)

    browser.close()
passed=sum(r['pass'] for r in results)
(OUTPUT/'pan-browser-results.json').write_text(json.dumps({'results':results,'passed':passed,'total':len(results)},indent=2)+'\n')
print(f'{passed} / {len(results)} pan browser checks passed.',flush=True)
raise SystemExit(0 if passed==len(results) else 1)

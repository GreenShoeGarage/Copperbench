#!/usr/bin/env python3
"""Quiet-workbench regressions using real Chromium DOM/canvas/workers.

Persistence is a test double; exports are intercepted blobs. Tests do not claim
file-origin, hosted-offline, manufacturer or physical-board validation.
"""
from pathlib import Path
import ast
import json
import time
import traceback
from playwright.sync_api import sync_playwright
from browser_support import launch_chromium

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tests/output'
IMAGES = OUT / 'images'
IMAGES.mkdir(parents=True, exist_ok=True)
# Reuse the retained suite's storage/blob double without executing that suite.
module = ast.parse((ROOT / 'tests/browser_test.py').read_text())
STORE = next(ast.literal_eval(n.value) for n in module.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'STORE' for t in n.targets))
results = []
errors = []
requests = []
with sync_playwright() as pw:
    browser = launch_chromium(pw)
    page = browser.new_page(viewport={'width': 1600, 'height': 1050}, device_scale_factor=1)
    page.set_default_timeout(10000)
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('request', lambda r: requests.append(r.url))
    page.evaluate(STORE, {})
    page.set_content((ROOT / 'COPPERBENCH-portable.html').read_text(), wait_until='load')
    page.evaluate("""document.addEventListener('click',e=>{const a=e.target.closest('a[download]');if(a){e.preventDefault();__exports.push({name:a.download,blob:__blobs.get(a.href)})}},true)""")
    page.wait_for_function('window.CBAPP?.ready && CBAPP.state.checkRevision===CBAPP.state.revision', timeout=25000)

    def check(value, message='Assertion failed'):
        if not value:
            raise AssertionError(message)

    def test(name, fn):
        t = time.perf_counter()
        try:
            fn()
            results.append({'name': name, 'pass': True, 'ms': round((time.perf_counter()-t)*1000)})
            print('PASS', name, flush=True)
        except Exception as exc:
            results.append({'name': name, 'pass': False, 'error': str(exc)})
            print('FAIL', name, exc, flush=True)
            traceback.print_exc()
            page.screenshot(path=str(IMAGES / f'quiet-ui-failure-{len(results)}.png'))

    def close():
        if page.locator('#modal').evaluate('(e)=>e.open'):
            page.locator('#modalClose').click()

    def act(action):
        page.locator(f'[data-action="{action}"]:visible').first.click()

    def done():
        page.wait_for_function('CBAPP.state.checkRevision===CBAPP.state.revision && !CBAPP.state.job', timeout=25000)

    def reset(expr='CB.example()'):
        close()
        page.set_viewport_size({'width':1600, 'height':1050})
        page.evaluate('CBAPP.load('+expr+')')
        page.keyboard.press('Escape')
        page.locator('[data-panel=parts]').click()
        page.locator('[data-view=bench]').click()
        page.select_option('#partCategory', 'All')
        page.fill('#partSearch', '')
        page.evaluate("document.getElementById('toast').hidden=true;document.getElementById('inspector').classList.remove('collapsed');CBAPP.renderer.fit()")
        done()

    def initial():
        check(page.locator('#welcomeCard,.welcome-card,.canvas-label,.drawer-bottom').count()==0)
        text=page.locator('body').inner_text()
        for phrase in ['Make a connection.', 'A little more', 'Your bench. Your files.', 'Real-looking bodies.', 'Start with a part.']:
            check(phrase not in text, phrase)
        check(page.locator('.version').inner_text()=='v1.6.1')
        check(page.locator('#saveState').is_visible())
        check(not page.locator('#toolHint').is_visible())
    test('Fresh startup has no slogans, welcome overlay or idle instructions', initial)

    def shelf():
        check(page.locator('#partSearch').bounding_box()['y'] < page.locator('.library-shortcuts').bounding_box()['y'])
        check(page.locator('.library-shortcuts button').count()==6)
        check(page.locator('.part-card').first.bounding_box()['y'] < 430)
        check(not page.locator('#libraryTools').evaluate('(e)=>e.open'))
        check(page.locator('.fact-grid,.legend-list').count()==0)
        page.screenshot(path=str(IMAGES/'quiet-workbench.png'))
    test('Search and six compact catalog controls expose the parts grid above the fold', shelf)

    def category_search():
        page.select_option('#partCategory','Modules')
        check(page.locator('[data-place]').count()==5)
        page.select_option('#partCategory','All')
        page.fill('#partSearch','Pico')
        check(page.locator('[data-place]').count()>=4)
        page.fill('#partSearch','part-that-does-not-exist')
        check('No matching parts.' in page.locator('#partList').inner_text())
        check(page.locator('[data-action=footprint]').is_visible())
        page.fill('#partSearch','')
    test('Category selection and named-part search retain module/controller discovery', category_search)

    def catalogs():
        for action, target in [('maker-catalog','#makerFamily'), ('carrier-catalog','#platformRole'), ('platforms','#platformRole'), ('modules-catalog','#moduleChoice'), ('blocks-catalog','#blockChoice'), ('footprint','#fp-name')]:
            act(action)
            # Maker has its existing family/variant controls; avoid asserting a new DOM.
            if action=='maker-catalog':
                check(page.locator('#modalBody select').count()>=1)
            else:
                check(page.locator(target).is_visible(), action)
            close()
    test('Every compact library button opens its complete existing workflow', catalogs)

    def disclosure():
        summary=page.locator('#libraryTools > summary')
        summary.focus();page.keyboard.press('Enter')
        check(page.locator('#libraryTools').evaluate('(e)=>e.open'))
        for action in ['block-import','block-capture','blocks-table','open-footprint']:
            check(page.locator(f'[data-action={action}]').is_visible(), action)
        page.evaluate('CBAPP.commit("Refresh test",d=>d.title="Quiet workbench test",{copper:false})')
        check(page.locator('#libraryTools').evaluate('(e)=>e.open'))
        act('blocks-table');check(page.locator('#modal').evaluate('(e)=>e.open'));close()
        summary=page.locator('#libraryTools > summary');summary.click()
    test('Library tools is keyboard-operable and keeps its state through inspector refresh', disclosure)

    def tool_hint():
        page.locator('[data-tool=trace]').first.click()
        check(page.locator('#toolHint').inner_text()=='Click a lead, via, or trace to start.')
        before=page.evaluate('JSON.stringify(CBAPP.state.doc)')
        act('tool-help');check('V inserts' not in page.locator('#modalBody').inner_text())
        check('Escape cancels' in page.locator('#modalBody').inner_text())
        close();check(page.evaluate('CBAPP.state.tool')=='trace')
        check(page.evaluate('JSON.stringify(CBAPP.state.doc)')==before)
        page.keyboard.press('Escape');check(not page.locator('#toolHint').is_visible())
    test('Active trace guidance is concise; tool help does not change the board or tool', tool_hint)

    def via_help():
        page.locator('#canvas').focus();page.keyboard.press('Shift+V')
        check(page.evaluate('CBAPP.state.tool')=='via')
        check(page.locator('#viaPlacementStatus').is_visible())
        check('net before export' in page.locator('#viaPlacementStatus').inner_text())
        act('tool-help');check('red preview blocks placement' in page.locator('#modalBody').inner_text())
        check('Auto inherits' in page.locator('#modalBody').inner_text())
        close();page.keyboard.press('Escape')
    test('Via tool retains net/placement cautions and its complete on-demand instructions', via_help)

    def placement():
        reset();page.fill('#partSearch','axial')
        page.locator('[data-place=r-axial]').click()
        check(page.evaluate('!!CBAPP.state.placing'))
        check(not page.locator('#toast').is_visible())
        check('Click to place' in page.locator('#toolHint').inner_text())
        act('tool-help');check('Check the actual part drawing' in page.locator('#modalBody').inner_text())
        close();page.keyboard.press('Escape');page.fill('#partSearch','')
    test('Part placement uses one context hint rather than a second instructional toast', placement)

    def guide():
        page.locator('#canvas').focus();page.keyboard.press('h')
        check(page.locator('#modalTitle').inner_text()=='Guide & keyboard shortcuts')
        text=page.locator('#modalBody').inner_text()
        for phrase in ['Deleting copper leaves the net intact', 'Same-net copper', 'Independent CAM review', 'Silkscreen is clipped', 'Library tools', 'KEYBOARD']:
            check(phrase in text,phrase)
        check('V1.6.1' in page.locator('#modalEyebrow').inner_text());close()
        page.locator('#toolHelp').focus();page.keyboard.press('Enter')
        check(page.locator('#modalTitle').inner_text()=='Select tool')
        page.get_by_role('button',name='Full guide',exact=True).click()
        check('keyboard shortcuts' in page.locator('#modalTitle').inner_text());close()
    test('Keyboard and touch-accessible help retains displaced instructions and limitations', guide)

    def old_prefs():
        other=browser.new_page(viewport={'width':1200,'height':850})
        other.evaluate(STORE,{'copperbench.preferences.v1':json.dumps({'welcome':False,'theme':'dark','mode':'advanced','units':'mil','inspector':False})})
        other.set_content((ROOT/'COPPERBENCH-portable.html').read_text());other.wait_for_function('window.CBAPP?.ready')
        check(other.locator('#welcomeCard').count()==0)
        check(other.evaluate('CBAPP.state.theme')=='dark')
        check(other.evaluate('CBAPP.state.mode')=='advanced')
        check(other.evaluate('CBAPP.state.units')=='mil')
        check(other.locator('#inspector').evaluate('e=>e.classList.contains("collapsed")'))
        other.close()
    test('Legacy welcome preferences do not restore clutter or discard saved UI settings', old_prefs)

    def safety():
        reset()
        check('6 errors' in page.locator('.check-summary').inner_text())
        check('5 warnings' in page.locator('.check-summary').inner_text())
        check(page.locator('.has-errors').is_visible())
        act('export');page.wait_for_selector('#downloadFab')
        check(not page.locator('#downloadFab').is_enabled())
        check(page.locator('#diagnosticExport').is_visible());close()
    test('Live error/warning counts and the fabrication export gate remain visible', safety)

    def quota():
        page.evaluate('__quotaError=true;CBAPP.commit("Storage check",d=>d.title="Storage test",{copper:false})')
        page.wait_for_timeout(850)
        check('failed' in page.locator('#saveState').inner_text().lower())
        check(page.locator('#toast').is_visible())
        check('Autosave failed' in page.locator('#toast').inner_text())
        page.evaluate('__quotaError=false');act('save');page.wait_for_timeout(100)
        check(page.evaluate('__exports.at(-1).name.endsWith(".json")'))
    test('Autosave failures still display an explicit warning and JSON backup remains available', quota)

    def panels():
        reset()
        for panel,title in [('nets','Connections'),('planes','Planes'),('board','Board'),('silk','Silkscreen'),('records','Project log')]:
            page.locator(f'[data-panel={panel}]').click()
            check(page.locator('#drawerContent h3').inner_text()==title)
            if panel=='board':check('minimum clearance' in page.locator('#drawerContent').inner_text())
        page.locator('[data-panel=silk]').click();page.locator('[data-side=bottom]').click()
        check(page.locator('#drawerContent .layer-label').inner_text()=='Bottom silkscreen')
        page.locator('[data-side=top]').click()
        reset("(()=>{const d=CB.blank();d.settings.autoPlanes=false;CB.Planes.set(d,'top',CB.newNet(d,'GND'));return d;})()")
        check(page.locator('.plane-indicator.has-warning').is_visible())
        check('Needs refill' in page.locator('.plane-indicator').inner_text())
    test('Plain panel headings retain board fabrication limits and the active silkscreen face', panels)

    def readback():
        reset()
        before=page.evaluate('JSON.stringify(CBAPP.exportFiles())')
        page.locator('[data-view=fabrication]').click()
        check(page.locator('#inspectorContent h3').inner_text()=='Export layers')
        check('independent CAM' in page.locator('#inspectorContent .notice').inner_text())
        check(page.locator('[data-fab-layer]').count()>=9)
        act('fab-silk-top')
        check(page.evaluate('JSON.stringify([...CBAPP.state.fabLayers].sort())===JSON.stringify(["board-Edge_Cuts.gbr","board-F_Silkscreen.gbr"].sort())'))
        check(page.evaluate('JSON.stringify(CBAPP.exportFiles())')==before)
        page.screenshot(path=str(IMAGES/'quiet-silkscreen.png'))
    test('Fabrication retains exported-layer selection, CAM caution and identical file bytes', readback)

    def mobile():
        reset()
        for w in [360,390,430,700,900]:
            page.set_viewport_size({'width':w,'height':844});page.wait_for_timeout(120)
            check(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),str(w))
            page.locator('[data-tool=trace]').first.click()
            check(page.locator('#toolHint').is_visible())
            check(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),str(w))
            page.keyboard.press('Escape')
        page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(150);act('fit')
        page.screenshot(path=str(IMAGES/'quiet-mobile.png'))
        act('toggle-drawer');check(page.locator('#partSearch').is_visible())
        page.select_option('#partCategory','Modules');check(page.locator('[data-place]').count()==5)
        page.screenshot(path=str(IMAGES/'quiet-mobile-parts.png'))
        act('toggle-drawer');act('tool-help')
        check(page.locator('#modal').bounding_box()['width']<=390);close()
    test('Compact and active-tool layouts remain usable from 360 to 900 pixels wide', mobile)

    def themes():
        reset()
        for theme in ['dark','contrast']:
            act('theme');check(page.evaluate('CBAPP.state.theme')==theme)
            check(page.locator('.check-summary').is_visible())
            check(page.locator('#partSearch').is_visible())
            check(page.locator('#toolName').evaluate('(e)=>getComputedStyle(e).color')==page.locator('body').evaluate('(e)=>getComputedStyle(e).color'))
            check(page.locator('.tool-rail button.active').evaluate('(e)=>getComputedStyle(e).color')=='rgb(255, 255, 255)')
            page.screenshot(path=str(IMAGES/f'quiet-{theme}.png'))
        act('theme')
    test('Dark and high-contrast themes retain readable controls and status indicators', themes)

    def compatible():
        check(page.evaluate('CB.LIB.length')==193)
        check(page.evaluate('CBAPP.state.doc.schema')==5)
        # View/control chrome does not alter native schema or embedded footprints.
        raw=page.evaluate('JSON.stringify(CBAPP.state.doc)')
        check(page.evaluate('r=>JSON.stringify(CB.validateDoc(JSON.parse(r)))',raw)==raw)
    test('The 193-part library and schema-5 native round trip remain unchanged', compatible)

    def no_network():
        check(not errors, str(errors))
        check(not [url for url in requests if url.startswith(('https:','http:'))], str(requests))
    test('Quiet-workbench interactions need no external requests and raise no uncaught errors', no_network)
    browser.close()
summary={'environment':'Chromium embedded portable HTML; simulated storage; captured download blobs.',
         'passed':sum(r['pass'] for r in results),'total':len(results),'results':results,'uncaught':errors}
(OUT/'quiet-ui-browser-results.json').write_text(json.dumps(summary,indent=2)+'\n')
print(f"{summary['passed']} / {summary['total']} quiet UI checks passed.")
raise SystemExit(0 if summary['passed']==summary['total'] else 1)

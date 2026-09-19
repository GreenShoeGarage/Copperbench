#!/usr/bin/env python3
"""Opt-in qualification: normal HTTP/file navigation, native storage/downloads.
No injected storage, intercepted downloads, request routing or policy changes.
Blocked environments are reported, never counted as successful tests.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
import json, os, tempfile, threading, time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';OUT.mkdir(exist_ok=True)
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
results=[]
def ready(page):page.wait_for_function('window.CBAPP?.ready',timeout=20000)
def rename(page,name):
    page.click('#titleButton');page.locator('#modalBody input').first.fill(name);page.locator('#modalFooter button.primary').click();page.wait_for_function("document.querySelector('#saveState').textContent.includes('Saved locally')",timeout=10000)
try:
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as temp:
        options={'headless':True,'accept_downloads':True}
        if os.environ.get('CHROMIUM_EXECUTABLE'):options['executable_path']=os.environ['CHROMIUM_EXECUTABLE']
        for label,url in [('HTTP static app',f'http://127.0.0.1:{server.server_port}/'),('Portable file',(ROOT/'COPPERBENCH-portable.html').as_uri())]:
            context=None
            try:
                profile=Path(temp)/label.replace(' ','-');context=pw.chromium.launch_persistent_context(profile,**options)
                page=context.new_page();page.goto(url,wait_until='load',timeout=20000);ready(page)
                title='Native verification '+label;rename(page,title)
                with page.expect_download(timeout=10000) as download:page.locator('[data-action=save]').first.click()
                target=Path(temp)/(profile.name+'.json');download.value.save_as(target)
                assert json.loads(target.read_text())['title']==title,'Downloaded bytes do not match current project'
                page.close();page=context.new_page();page.goto(url);ready(page)
                assert page.evaluate('CBAPP.state.doc.title')==title,'Closing/reopening page lost storage'
                context.close();context=pw.chromium.launch_persistent_context(profile,**options)
                page=context.new_page();page.goto(url);ready(page)
                assert page.evaluate('CBAPP.state.doc.title')==title,'Closing/reopening browser profile lost storage'
                if label.startswith('HTTP'):
                    page.evaluate('navigator.serviceWorker.ready');page.reload();ready(page)
                    page.wait_for_function('navigator.serviceWorker.controller!==null',timeout=10000)
                    context.set_offline(True);page.reload();ready(page)
                    assert page.evaluate('CBAPP.state.doc.title')==title,'Offline shell lost local project'
                results.append({'case':label,'status':'passed','checks':['native autosave','real JSON download','page reopen','persistent profile reopen']+(['service-worker offline reload'] if label.startswith('HTTP') else [])})
                print('PASS',label,flush=True)
            except Exception as error:
                message=str(error);blocked='ERR_BLOCKED_BY_ADMINISTRATOR' in message
                results.append({'case':label,'status':'blocked' if blocked else 'failed','error':message})
                print('BLOCKED' if blocked else 'FAIL',label,message,flush=True)
            finally:
                if context:context.close()
finally:server.shutdown();server.server_close()
(OUT/'native-browser-qualification.json').write_text(json.dumps({'cases':results,'passed':sum(r['status']=='passed' for r in results),'blocked':sum(r['status']=='blocked' for r in results),'total':len(results)},indent=2))
raise SystemExit(0 if results and all(r['status']=='passed' for r in results) else 2)

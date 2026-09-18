#!/usr/bin/env python3
"""Independent-language export checks; no JavaScript reader or geometry imports.
Source-centered header coordinates are literal reviewed values below. These test
transcription and generated geometry, not a physical fit or electrical circuit.
"""
from pathlib import Path
import json,sys,math
from shapely.geometry import Point,LineString
from verify_manufacturing import read_gerber,read_drills
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';BASE=OUT/'fixtures/modules-blocks';results=[]
def test(name,fn):
 try:fn();results.append({'name':name,'pass':True});print('PASS',name)
 except Exception as e:results.append({'name':name,'pass':False,'error':repr(e)});print('FAIL',name,repr(e))
MODELS={
 'module-bme280-original':(17.78,19.05,False,[(1.27+2.54*i,2.54) for i in range(7)],[(2.54,16.51,2.2),(15.24,16.51,2.2)]),
 'module-ds3231-original':(22.86,17.78,False,[(2.54+2.54*i,2.54) for i in range(8)],[(2.54,15.24,2.5),(20.32,15.24,2.5)]),
 'module-oled-096-qt':(29.21,31.75,True,[(23.495-2.54*i,29.21) for i in range(8)],[(x,y,2.5) for x in [2.54,26.67] for y in [2.54,29.21]]),
 'module-tb6612':(20.32,26.67,False,[(2.54,24.765-2.54*i) for i in range(10)]+[(17.78,6.985+2.54*i) for i in range(6)],[(16.51,24.13,2.5),(16.51,2.54,2.5)]),
 'module-mpm3610-33':(10.16,17.145,False,[(8.89-2.54*i,2.54) for i in range(4)],[(5.08,14.605,2.5)])}
def check_model(name,bottom=False):
 w,h,reflect,pts,holes=MODELS[name];folder=BASE/(name+('-bottom' if bottom else ''));drills=read_drills(folder/'board-PTH.drl');assert len(drills)==len(pts)
 def xy(x,y):
  lx=(x-w/2)*(-1 if reflect else 1);ly=h/2-y
  return (w/2+7-ly,h/2+7+lx) if bottom else (w/2+7+lx,h/2+7-ly)
 expected=[xy(x,y) for x,y in pts]
 for x,y in expected:
  matching=[d for d in drills if math.dist(d['a'],(x,y))<.0001];assert len(matching)==1,(name,x,y);assert abs(matching[0]['diameter']-1)<1e-9;assert not matching[0]['slot']
 for face in ['F','B']:
  copper=read_gerber(folder/f'board-{face}_Cu.gbr').geometry
  assert all(copper.covers(Point(x,y)) for x,y in expected),name
  assert read_gerber(folder/f'board-{face}_Silkscreen.gbr').geometry.is_empty,'Host drawing leaked into silkscreen'
 path=folder/'board-NPTH.drl';mounts=read_drills(path) if path.exists() else []
 assert len(mounts)==(len(holes) if bottom else 0)
 if bottom:
  for x,y,diam in holes:
   a=xy(x,y);matching=[m for m in mounts if math.dist(m['a'],a)<.0001];assert len(matching)==1;assert abs(matching[0]['diameter']-diam)<1e-9
for name in MODELS:
 for bottom in [False,True]:test(name+(' rotated / bottom: ' if bottom else ' top: ')+'literal header drills, both copper faces, optional mounts and no host silk',lambda n=name,b=bottom:check_model(n,b))
def check_block(name):
 folder=BASE/name;d=json.loads((folder/'project.json').read_text());h=d['board']['height'];layers={face:read_gerber(folder/f'board-{side}_Cu.gbr').geometry for face,side in [('top','F'),('bottom','B')]}
 for t in d['traces']:
  line=LineString([(p['x'],h-p['y']) for p in t['points']]);assert layers[t['layer']].buffer(.00001).covers(line),'Trace path missing in manufacturing'
 drills=read_drills(folder/'board-PTH.drl');expected=sum(bool(p['drill']) for part in d['parts'] for p in part['pads'])+len(d['vias']);assert len(drills)==expected
 for v in d['vias']:
  xy=(v['x'],h-v['y']);assert any(math.dist(d['a'],xy)<.0001 and abs(d['diameter']-v['drill'])<.00001 for d in drills)
  assert all(covers.covers(Point(*xy)) for covers in layers.values())
 assert read_gerber(folder/'board-F_Silkscreen.gbr').geometry.area>0,'Reference / polarity silk missing'
 assert d['blockInstances'][0]['members']
for name in ['block-led','block-button','block-i2c','block-decoupling','block-dc-input','block-rc-filter']:test(name+': exported trace centerlines, drilled pins/vias and actual silkscreen',lambda n=name:check_block(n))
(OUT/'modules-blocks-independent-results.json').write_text(json.dumps({'passed':sum(r['pass'] for r in results),'total':len(results),'results':results},indent=2));print(f"{sum(r['pass'] for r in results)}/{len(results)} independent checks passed.");sys.exit(0 if all(r['pass'] for r in results) else 1)

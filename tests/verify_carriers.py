#!/usr/bin/env python3
"""Independent-language checks of v1.5 header drills, copper and RF guard output.
Literal dimensions below do not import JS. This verifies transcription/export,
not manufacturer approval, fit, complete RF clearance, or electrical operation.
"""
from pathlib import Path
import json,sys
from shapely.geometry import Point,box
from verify_manufacturing import read_gerber,read_drills
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';BASE=OUT/'fixtures/carriers';results=[]
def test(name,fn):
 try:fn();results.append({'name':name,'pass':True});print('PASS',name)
 except Exception as e:results.append({'name':name,'pass':False,'error':repr(e)});print('FAIL',name,repr(e))
def rows(id):
 if id.startswith('pico'):return 51,[(x,1.37+i*2.54) for x in [1.61,19.39] for i in range(20)]
 if id=='nano-classic':return 43.2,[(x,3.82+i*2.54) for x in [1.38,16.62] for i in range(15)]
 if id=='esp32-devkitc-v4':return 54.3,[(x,7.31+i*2.54) for x in [1.27,26.67] for i in range(19)]
 if id=='feather-classic':return 22.86,[(6.35+i*2.54,21.59) for i in range(16)]+[(16.51+i*2.54,1.27) for i in range(12)]
 return 21,[(x,2.88+i*2.54) for x in [1.28,16.52] for i in range(7)]
def check_header(id,role):
 h,pts=rows(id);pts=[(x+12,h+12-y) for x,y in pts];folder=BASE/(id+'-'+role);drills=read_drills(folder/'board-PTH.drl');assert len(drills)==len(pts)
 for x,y in pts:
  matches=[d for d in drills if abs(d['a'][0]-x)<.00001 and abs(d['a'][1]-y)<.00001];assert len(matches)==1,(id,x,y);assert abs(matches[0]['diameter']-1)<1e-9;assert not matches[0]['slot']
 for face in ['F','B']:
  copper=read_gerber(folder/f'board-{face}_Cu.gbr').geometry
  assert all(copper.covers(Point(x,y)) for x,y in pts),id
for family in ['pico','pico2','pico-w','pico2-w','nano-classic','esp32-devkitc-v4','feather-classic','xiao-rp2040','xiao-esp32c3']:
 for role in ['carrier','addon']:test(f'{family} {role}: literal pitch, bank origins, PTH count and both copper faces',lambda f=family,r=role:check_header(f,r))
def mounts():
 for f,count,diam in [('pico2',4,2.1),('nano-classic',4,1.8),('feather-classic',4,2.54),('esp32-devkitc-v4',0,0),('xiao-rp2040',0,0)]:
  path=BASE/(f+'-carrier')/'board-NPTH.drl';ds=read_drills(path) if path.exists() else [];assert len(ds)==count;assert all(abs(d['diameter']-diam)<1e-9 for d in ds)
test('Optional mounting drills are NPTH and no holes are invented for ESP32 / XIAO',mounts)
def rf():
 folder=BASE/'pico2-w-plane';guard=box(18,5,27,20)
 for face in ['F','B']:
  copper=read_gerber(folder/f'board-{face}_Cu.gbr').geometry;assert copper.area>100;assert copper.intersection(guard).area<1e-8,'Copper leaked into antenna guard'
  assert copper.covers(Point(13.61,51+12-(1.37+2*2.54)))
test('Generated filled Gerbers exclude literal antenna rectangle on both faces',rf)
def neutral_art():
 for id in ['pico2-w','esp32-devkitc-v4','xiao-esp32c3']:
  folder=BASE/(id+'-carrier')
  for face in ['F','B']:assert read_gerber(folder/f'board-{face}_Silkscreen.gbr').geometry.is_empty
  assert len(read_drills(folder/'board-PTH.drl'))==len(rows(id)[1])
test('Host reference drawings, access labels and RF overlays invent no silkscreen or drills',neutral_art)
OUT.mkdir(exist_ok=True);(OUT/'carrier-independent-results.json').write_text(json.dumps({'passed':sum(r['pass'] for r in results),'total':len(results),'results':results},indent=2));print(f"{sum(r['pass'] for r in results)}/{len(results)} independent carrier checks passed.");sys.exit(0 if all(r['pass'] for r in results) else 1)

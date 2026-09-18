#!/usr/bin/env python3
"""Independent-language checks of literal selected maker-part fabrication geometry.
No imported JS geometry. This is not third-party CAM or physical fit validation.
"""
from pathlib import Path
import json,sys
from shapely.geometry import Point
from verify_manufacturing import read_gerber,read_drills
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';BASE=OUT/'fixtures/maker';results=[]
def test(name,fn):
 try:fn();results.append({'name':name,'pass':True});print('PASS',name)
 except Exception as e:results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,e)
def close(a,b):assert abs(a-b)<.00001,(a,b)
def drills_at(name,expected,diameters):
 d=read_drills(BASE/name/'board-PTH.drl');assert len(d)==len(expected)
 for (x,y),dia in zip(expected,diameters):
  match=[p for p in d if abs(p['a'][0]-x)<.00001 and abs(p['a'][1]-y)<.00001 and not p['slot']];assert len(match)==1,(name,x,y,match);close(match[0]['diameter'],dia)
def ne555():
 expected=[(46.19,43.81),(46.19,41.27),(46.19,38.73),(46.19,36.19),(53.81,36.19),(53.81,38.73),(53.81,41.27),(53.81,43.81)]
 drills_at('maker-ne555-dip',expected,[.9]*8)
 for side in ('F','B'):
  layer=read_gerber(BASE/'maker-ne555-dip'/f'board-{side}_Cu.gbr').geometry
  assert all(layer.covers(Point(x,y)) for x,y in expected)
test('NE555 PDIP-8 literal 7.62 mm row spacing, 2.54 mm pitch, drills and both copper faces',ne555)
def soic():
 d=BASE/'maker-ne555-soic';assert not (d/'board-PTH.drl').exists();top=read_gerber(d/'board-F_Cu.gbr').geometry;bottom=read_gerber(d/'board-B_Cu.gbr').geometry
 assert bottom.is_empty
 for x in (47.35,52.65):
  for y in (38.095,39.365,40.635,41.905):assert top.covers(Point(x,y))
test('NE555 SOIC-8 is top surface copper with no invented drill or bottom copper',soic)
def regulator():
 d=BASE/'maker-lm1117-3.3';g=read_gerber(d/'board-F_Cu.gbr').geometry
 for x,y in [(47.7,36.9),(50,36.9),(52.3,36.9),(50,43.1)]:assert g.covers(Point(x,y))
 assert not (d/'board-PTH.drl').exists()
test('LM1117 SOT-223 exports three lead lands and the separate output tab',regulator)
def qwiic():
 g=read_gerber(BASE/'maker-qwiic'/'board-F_Cu.gbr').geometry
 for x in [48.5,49.5,50.5,51.5]:assert g.covers(Point(x,42.025))
 for x in [47.2,52.8]:assert g.covers(Point(x,38.9))
test('Qwiic has four 1 mm-pitch signal lands and two mechanical mounting lands',qwiic)
def usb():
 d=BASE/'usb-top';dr=read_drills(d/'board-PTH.drl');assert len(dr)==20 and sum(v['slot'] for v in dr)==4
 for y in [44.025,42.675]:
  for i in range(8):
   x=47.025+i*.85
   assert any(not a['slot'] and abs(a['a'][0]-x)<.00001 and abs(a['a'][1]-y)<.00001 and abs(a['diameter']-.4)<.00001 for a in dr)
 slots=[a for a in dr if a['slot']];assert sorted(round(abs(a['b'][1]-a['a'][1]),3) for a in slots)==[.8,.8,1.5,1.5]
 assert all(abs(a['diameter']-.6)<.00001 for a in slots)
test('USB4085 Excellon has 16 literal 0.4 mm signal drills and four vertical shell slots',usb)
def usb_rot():
 a=read_drills(BASE/'usb-top'/'board-PTH.drl');b=read_drills(BASE/'usb-bottom-90'/'board-PTH.drl');assert len(a)==len(b)
 # Top->bottom plus 90 deg: old manufacturing (x,y) -> (y+10,x-10).
 for old in a:
  candidates=[q for q in b if q['slot']==old['slot'] and abs(q['diameter']-old['diameter'])<.00001]
  want={(round(v[1]+10,6),round(v[0]-10,6)) for v in (old['a'],old['b'])}
  assert any({(round(v[0],6),round(v[1],6)) for v in (q['a'],q['b'])}==want for q in candidates)
test('USB slots and contact coordinates transform consistently after bottom flip plus 90° rotation',usb_rot)
def icsp():
 dr=read_drills(BASE/'uno-icsp'/'board-PTH.drl');assert len(dr)==38
 for x in (63.627,66.167):
  for y in (30.48,27.94,25.4):assert any(abs(a['a'][0]-x)<.00001 and abs(a['a'][1]-y)<.00001 for a in dr)
test('Uno ICSP adds six drills at the literal reference positions, not mirrored in manufacture',icsp)
def encoder():
 d=read_drills(BASE/'encoder'/'board-NPTH.drl');assert len(d)==2
 assert {(round(a['a'][0],4),round(a['a'][1],4)) for a in d}=={(50,33.5),(50,46.5)}
 assert all(abs(a['diameter']-2)<.00001 for a in d)
test('Encoder fixing holes remain non-plated and follow side/rotation transforms',encoder)
for side,name in [('F','led-top'),('B','led-bottom')]:
 def silk(side=side,name=name):
  d=BASE/name;g=read_gerber(d/f'board-{side}_Silkscreen.gbr').geometry
  assert not g.is_empty and g.area>.1
  other='B' if side=='F' else 'F';assert read_gerber(d/f'board-{other}_Silkscreen.gbr').geometry.is_empty
 test(name+': real polarity artwork survives Gerber clearing on its assigned face',silk)
record={'version':json.loads((ROOT/'package.json').read_text())['version'],'passed':sum(r['pass'] for r in results),'total':len(results),'results':results};(OUT/'maker-manufacturing-results.json').write_text(json.dumps(record,indent=2));print(f"{record['passed']}/{record['total']} checks passed.");sys.exit(record['passed']!=record['total'])

#!/usr/bin/env python3
"""Independent Python/Shapely checks of literal via drill/copper/mask coordinates.
This is an independent geometry regression, not an external CAM certification.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
from shapely.geometry import Point
from verify_manufacturing import read_drills, read_gerber
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';BASE=OUT/'fixtures/vias'
results=[]
def test(name,fn):
 try:fn();results.append({'name':name,'pass':True});print('PASS',name)
 except Exception as e:results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,e)
for name in ('open','tented'):
 folder=BASE/name
 def drill(folder=folder):
  drills=read_drills(folder/'board-PTH.drl')
  assert len(drills)==1
  assert drills[0]['a']==(12.3,22.6) and drills[0]['b']==(12.3,22.6)
  assert abs(drills[0]['diameter']-.6)<1e-8 and not drills[0]['slot']
  assert not (folder/'board-NPTH.drl').exists()
 test(name+': one plated drill at the literal expected center',drill)
 def copper(folder=folder):
  a=read_gerber(folder/'board-F_Cu.gbr');b=read_gerber(folder/'board-B_Cu.gbr')
  assert len(a.flashes)==len(b.flashes)==1
  assert a.geometry.symmetric_difference(b.geometry).area<1e-10
  circle=Point(12.3,22.6).buffer(.6,quad_segs=64)
  assert a.geometry.symmetric_difference(circle).area<.0002
  assert abs(a.geometry.boundary.distance(Point(12.3,22.6))-.6)<.0001
 test(name+': identical 1.2 mm copper on both faces, no bottom mirror',copper)
 def mask(folder=folder,name=name):
  for face in ('F','B'):
   m=read_gerber(folder/f'board-{face}_Mask.gbr').geometry
   if name=='tented':assert m.is_empty
   else:
    assert m.covers(Point(12.3,22.6).buffer(.6,quad_segs=64))
    assert len(read_gerber(folder/f'board-{face}_Mask.gbr').flashes)==1
 test(name+': mask opening follows tenting on both faces',mask)
def unchanged():
 for suffix in ('F_Cu.gbr','B_Cu.gbr','PTH.drl'):
  assert (BASE/'open'/('board-'+suffix)).read_bytes()==(BASE/'tented'/('board-'+suffix)).read_bytes()
test('Tenting changes mask only, not copper or plated-drill bytes',unchanged)
record={'version':json.loads((ROOT/'package.json').read_text())['version'],'date':datetime.now(timezone.utc).isoformat(),'passed':sum(r['pass'] for r in results),'total':len(results),'scope':'Independent Python/Shapely parser; literal single-via coordinates and diameters. No manufacturer upload or physical fabrication.','results':results}
(OUT/'via-manufacturing-results.json').write_text(json.dumps(record,indent=2));print(f"{record['passed']}/{record['total']} independent via checks passed.")
sys.exit(0 if record['passed']==record['total'] else 1)

#!/usr/bin/env python3
"""Independent Python checks of platform export coordinates and geometry.
Expected positions below are literal top-view nominal data, NOT reconstructed
from the JavaScript model. This checks export arithmetic, not physical fit.
"""
from pathlib import Path
import json, sys
from datetime import datetime, timezone
from shapely.geometry import Point, Polygon
from verify_manufacturing import read_drills, read_gerber
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';BASE=OUT/'fixtures/platforms'
expected={
 'pi40':{'h':56,'pins':[(8.37+(i//2)*2.54,4.77 if i%2==0 else 2.23) for i in range(40)],'holes':[(3.5,3.5,2.7),(61.5,3.5,2.7),(3.5,52.5,2.7),(61.5,52.5,2.7)]},
 'uno-r3':{'h':53.34,'pins':[(27.94+i*2.54,50.8) for i in range(8)]+[(50.8+i*2.54,50.8) for i in range(6)]+[(18.796+i*2.54,2.54) for i in range(10)]+[(45.72+i*2.54,2.54) for i in range(8)],'holes':[(15.24,2.54,3.2),(13.97,50.8,3.2),(66.04,17.78,3.2),(66.04,45.72,3.2)]},
 'mkr':{'h':25,'pins':[(21.92+i*2.54,y) for y in (2.44,22.76) for i in range(14)],'holes':[(2.31,2.31,2.25),(59.19,2.31,2.25),(2.31,22.69,2.25),(59.19,22.69,2.25)]}
}
results=[]
def test(name,fn):
 try:fn();results.append({'name':name,'pass':True});print('PASS',name)
 except Exception as e:results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,e)
def ordered(items):return sorted(tuple(round(v,4) for v in t) for t in items)
for family,reference in expected.items():
 for role in ('addon','carrier'):
  folder=BASE/(family+'-'+role);margin=10 if role=='carrier' else 0;height=reference['h']+2*margin
  def positions(folder=folder,r=reference,m=margin,h=height):
   p=read_drills(folder/'board-PTH.drl');n=read_drills(folder/'board-NPTH.drl')
   assert ordered((v['a'][0],h-v['a'][1],v['diameter']) for v in p)==ordered((x+m,y+m,1) for x,y in r['pins'])
   assert ordered((v['a'][0],h-v['a'][1],v['diameter']) for v in n)==ordered((x+m,y+m,z) for x,y,z in r['holes'])
   assert all(v['a']==v['b'] and not v['slot'] for v in p+n)
  test(f'{family}/{role}: exact plated and non-plated drill coordinates',positions)
  def copper(folder=folder,r=reference,m=margin,h=height):
   top=read_gerber(folder/'board-F_Cu.gbr');bottom=read_gerber(folder/'board-B_Cu.gbr')
   assert len(top.flashes)==len(r['pins'])==len(bottom.flashes)
   assert top.geometry.symmetric_difference(bottom.geometry).area<1e-8
   assert ordered((a[0],h-a[1]) for a in top.flashes)==ordered((x+m,y+m) for x,y in r['pins'])
   for face in ('F','B'):
    mask=read_gerber(folder/f'board-{face}_Mask.gbr').geometry
    assert top.geometry.difference(mask).area<1e-8
    for x,y,d in r['holes']:assert mask.covers(Point(x+m,h-y-m).buffer(d/2,quad_segs=64))
   for x,y,d in r['holes']:assert top.geometry.distance(Point(x+m,h-y-m))>=d/2+.1524-1e-5
  test(f'{family}/{role}: copper/NPTH clearance, masks, and no bottom mirror',copper)
record={'version':'1.1.0','date':datetime.now(timezone.utc).isoformat(),'passed':sum(r['pass'] for r in results),'total':len(results),'scope':'Independent Python/Shapely checks of literal nominal connector geometry, export alignment and mask coverage; not physical fit or third-party CAM certification.','results':results}
(OUT/'platform-manufacturing-results.json').write_text(json.dumps(record,indent=2))
print(f"{record['passed']}/{record['total']} independent platform checks passed.")
sys.exit(0 if record['passed']==record['total'] else 1)

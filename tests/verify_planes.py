#!/usr/bin/env python3
"""Independent Gerber/Excellon plane regression using Python/Shapely, not the JS graph.
This checks generated artwork, not plating quality, manufacturer acceptance or circuit function.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
from shapely.geometry import Point, box
from shapely.ops import unary_union
from verify_manufacturing import read_drills, read_gerber
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';BASE=OUT/'fixtures/planes'
results=[]
def test(name, fn):
 try:fn();results.append({'name':name,'pass':True});print('PASS',name)
 except Exception as e:results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,e)
def check(value,message='Unexpected exported geometry'):
 if not value:raise AssertionError(message)
def geom(f,face):return read_gerber(BASE/f/f'board-{face}_Cu.gbr').geometry
def pieces(g):return list(g.geoms) if hasattr(g,'geoms') else [g]
def region(g,xy):
 matches=[a for a in pieces(g) if a.covers(Point(*xy))]
 check(len(matches)==1,'Expected one actual copper region at '+str(xy));return matches[0]
a=geom('power-ground','F');b=geom('power-ground','B')
ground=(6,18);power=(25,18);smd=(17,11);via=(19.1142,11)

def drill():
 ds=read_drills(BASE/'power-ground/board-PTH.drl')
 check(len(ds)==3)
 check(sorted((x['a'],x['diameter']) for x in ds)==sorted([(ground,.8),(power,.8),(via,.4)]))
 check(all(x['a']==x['b'] and not x['slot'] for x in ds))
test('Power/ground fixture has exactly three plated drills at literal expected centers',drill)
test('Bottom ground plane actually joins the through-hole lead and attachment via',lambda:check(region(b,ground).covers(Point(*via))))
test('Top SMT stub actually reaches the same via without touching the power plane',lambda:(check(region(a,smd).covers(Point(*via))),check(not region(a,smd).covers(Point(*power)))))
test('Power copper and ground copper remain separated on both faces',lambda:check(all(region(g,ground).distance(region(g,power))>=.1524-1e-4 for g in (a,b))))
test('Top power plane and SMT ground stub meet the explicit clearance',lambda:check(region(a,smd).distance(region(a,power))>=.1524-1e-4))
test('Via copper diameter and annular ring survive both Gerber layers',lambda:check(all(g.covers(Point(*via).buffer(.449,quad_segs=128)) for g in (a,b)) and (.9-.4)/2>=.127))

def masks():
 for face in ('F','B'):
  m=read_gerber(BASE/'power-ground'/f'board-{face}_Mask.gbr').geometry
  check(m.covers(Point(*via).buffer(.45,quad_segs=64)))
  check(not m.covers(Point(28,5)),'Copper plane is not an exposed solder-mask opening')
test('Untented attachment via has mask openings, but the plane itself stays masked',masks)

def edges():
 inner=box(.381,.381,32-.381,24-.381)
 for f in ('power-ground','split','holes'):
  for face in ('F','B'):check(inner.covers(geom(f,face)),f+' edge clearance')
test('All fixture copper stays inside the 0.381 mm board-edge margin',edges)
test('Split fixture has exactly two actual bottom-copper regions',lambda:check(len(pieces(geom('split','B')))==2))
test('Same-net pads on opposite sides of a keepout are not physically connected',lambda:check(not region(geom('split','B'),(6,18)).covers(Point(26,16))))
test('The full-height copper keepout has no exported plane copper',lambda:check(geom('split','B').intersection(box(15,0,17,24).buffer(.1523)).is_empty))

def hole():
 ds=read_drills(BASE/'holes/board-NPTH.drl');check(len(ds)==1 and ds[0]['a']==(23,18) and ds[0]['diameter']==3.2)
 check(geom('holes','B').distance(Point(23,18))>=1.6+.1524-1e-4)
test('Non-plated mounting hole and its copper clearance agree in separate outputs',hole)
test('Internal cutout keeps copper at the required routed-edge clearance',lambda:check(geom('holes','B').distance(box(20,5,26,10))>=.381-1e-4))

def fills():
 for f in ('power-ground','split','holes'):
  doc=json.loads((BASE/f/'project.json').read_text())
  for z in doc['zones']:
   rects=unary_union([box(r['x'],24-r['y']-r['h'],r['x']+r['w'],24-r['y']) for r in z['fill']['rects']])
   exported=geom(f,'F' if z['layer']=='top' else 'B')
   # Independent coordinates; tolerate only Gerber's 0.1 micron rounding at boundaries.
   check(rects.difference(exported.buffer(.00011)).area<1e-7, f+' missing plane copper')
test('Every filled native rectangle is retained by independently parsed Gerber geometry',fills)

def thermal():
 g=geom('holes','B');seed=region(g,ground)
 check(seed.area>500 and seed.covers(Point(*ground)))
 # A thermal gap exists around the pad while its spokes keep a real connected path.
 annulus=Point(*ground).buffer(1.3).difference(Point(*ground).buffer(1.01))
 check(annulus.difference(g).area>.3)
test('Thermal-gap artwork leaves a real copper path from pad into its plane',thermal)
record={'version':json.loads((ROOT/'package.json').read_text())['version'],'date':datetime.now(timezone.utc).isoformat(),'passed':sum(r['pass'] for r in results),'total':len(results),'scope':'Independent Python/Shapely Gerber and Excellon parsing. No external CAM certification, manufacturer acceptance, fabrication or electrical-function testing.','results':results}
(OUT/'plane-manufacturing-results.json').write_text(json.dumps(record,indent=2));print(f"{record['passed']}/{record['total']} independent plane checks passed.")
sys.exit(0 if record['passed']==record['total'] else 1)

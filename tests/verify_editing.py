#!/usr/bin/env python3
"""Separate Python/Shapely checks for the edited reference board.
This reader is maintained in this repo, not a third-party CAM certification.
"""
from pathlib import Path
import json
from shapely.geometry import LineString
from shapely.ops import unary_union
from verify_manufacturing import read_gerber, pad_geometry, QUAD
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';F=OUT/'fixtures/editing';results=[]
def test(name,fn):
    try:fn();results.append({'name':name,'pass':True});print('PASS',name)
    except Exception as e:results.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,e)
def require(b,msg='Mismatch'):
    if not b:raise AssertionError(msg)
def main():
    d=json.loads((F/'project.json').read_text());h=d['board']['height'];geometries={}
    for side,prefix in [('top','F'),('bottom','B')]:
        def copper(side=side,prefix=prefix):
            actual=read_gerber(F/f'board-{prefix}_Cu.gbr').geometry;geometries[side]=actual;pieces=[]
            for p in d['parts']:
                for pad in p['pads']:
                    if pad['drill'] or p['side']==side:pieces.append(pad_geometry(p,pad,h)[0])
            for t in d['traces']:
                if t['layer']==side:pieces.append(LineString([(p['x'],h-p['y']) for p in t['points']]).buffer(t['width']/2,quad_segs=QUAD))
            expected=unary_union(pieces);require(actual.symmetric_difference(expected).area<.0003,'Edited copper differs from expected physical geometry')
        test(side+' edited copper equals independent pad and trace construction',copper)
    test('Edited trace and both terminal pads form one physical copper region',lambda:require(geometries['top'].geom_type=='Polygon'))
    test('Top printed references survive after connected movement',lambda:require(read_gerber(F/'board-F_Silkscreen.gbr').geometry.area>.1))
    test('No bottom-side artwork was spuriously generated',lambda:require(read_gerber(F/'board-B_Silkscreen.gbr').geometry.is_empty))
    test('Outline path bounds remain the original substrate dimensions',lambda:require(all(abs(a-b)<.03 for a,b in zip(read_gerber(F/'board-Edge_Cuts.gbr').geometry.bounds,(0,0,d['board']['width'],h)))))
    result={'passed':sum(r['pass'] for r in results),'total':len(results),'scope':'Separate Python/Shapely parser, not independent third-party CAM','results':results};(OUT/'editing-manufacturing-results.json').write_text(json.dumps(result,indent=2));print(f"{result['passed']}/{result['total']} geometry checks passed");return 0 if result['passed']==result['total'] else 1
if __name__=='__main__':raise SystemExit(main())

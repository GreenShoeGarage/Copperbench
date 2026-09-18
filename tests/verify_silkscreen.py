#!/usr/bin/env python3
"""Independent Python/Shapely silk-compositing regression, including the old blank-layer bug.

This is not third-party CAM certification. The previous Python checker had copied
an incorrect XOR assumption; this checker explicitly tests the Gerber 4.10 UNION
contract against nested and oppositely wound contours before checking output.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, json, math, sys
from shapely.geometry import Polygon, Point, LineString, GeometryCollection
from shapely.ops import unary_union
from verify_manufacturing import read_gerber, pad_geometry, QUAD
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';FIX=OUT/'fixtures/silkscreen';RESULTS=[]
def test(name,fn):
    try: fn();RESULTS.append({'name':name,'pass':True});print('PASS',name,flush=True)
    except Exception as e: RESULTS.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,str(e),flush=True)
def require(value,message='Assertion failed'):
    if not value: raise AssertionError(message)
def substrate(d):
    b=d['board'];w,h=b['width'],b['height'];shape=b['shape']
    if shape=='polygon': pts=[(v['x'],h-v['y']) for v in b['points']]
    elif shape=='circle': pts=[(round(w/2+math.cos(i*math.tau/128)*w/2,4),h-round(h/2+math.sin(i*math.tau/128)*h/2,4)) for i in range(128)]
    elif shape=='rounded' and b['radius']:
        r=min(b['radius'],w/2,h/2);pts=[]
        for x,y,a in [(w-r,r,-90),(w-r,h-r,0),(r,h-r,90),(r,r,180)]:
            for i in range(17):
                t=math.radians(a+i*90/16);pts.append((round(x+math.cos(t)*r,4),h-round(y+math.sin(t)*r,4)))
    else: pts=[(0,h),(w,h),(w,0),(0,0)]
    return Polygon(pts)
def openings(d,side):
    h=d['board']['height'];exp=d['profile']['maskExpansion']+.05;pieces=[]
    for part in d['parts']:
        for a in part['pads']:
            if not a['drill'] and part['side']!=side:continue
            a=copy.deepcopy(a);a['w']+=2*exp;a['h']+=2*exp;pieces.append(pad_geometry(part,a,h)[0])
    for v in d['vias']:
        if not v.get('tented'):pieces.append(Point(v['x'],h-v['y']).buffer(v['diameter']/2+exp,quad_segs=QUAD))
    for v in d['holes']:
        a=math.radians(v.get('rotation',0));s=v.get('slot',0)/2
        pts=[(v['x']-s*math.cos(a),h-v['y']+s*math.sin(a)),(v['x']+s*math.cos(a),h-v['y']-s*math.sin(a))]
        pieces.append(LineString(pts).buffer((v['drill']+.1)/2,quad_segs=QUAD))
    for cut in d['cutouts']:pieces.append(Polygon([(p['x'],h-p['y']) for p in cut['points']]))
    return unary_union(pieces)
def expected_source(folder,d,side):
    h=d['board']['height'];pieces=[]
    for s in json.loads((folder/'source-strokes.json').read_text()):
        if s['layer']==side:pieces.append(LineString([(p['x'],h-p['y']) for p in s['points']]).buffer(s['width']/2,quad_segs=QUAD))
    for s in json.loads((folder/'source-shapes.json').read_text()):
        if s['layer']==side:pieces.append(Polygon([(p['x'],h-p['y']) for p in s['poly']]))
    return unary_union(pieces).intersection(substrate(d)).difference(openings(d,side))
def main():
    if not FIX.exists():raise SystemExit('Run node tests/silkscreen.test.js first.')
    test('Standard UNION reader reproduces total ink erasure from the old clear frame',lambda:require(read_gerber(FIX/'legacy-frame.gbr').geometry.is_empty))
    test('Oppositely wound nested contours fill the entire outer region, not a donut',lambda:require(abs(read_gerber(FIX/'union-contours.gbr').geometry.area-1200)<1e-6))
    for shape in ['rect','rounded','circle','concave','reversed','offset']:
        folder=FIX/('clip-'+shape);d=json.loads((folder/'project.json').read_text())
        for side,letter in [('top','F'),('bottom','B')]:
            def flood(folder=folder,d=d,side=side,letter=letter):
                actual=read_gerber(folder/f'board-{letter}_Silkscreen.gbr').geometry;expected=substrate(d).difference(openings(d,side));delta=actual.symmetric_difference(expected).area
                require(actual.area>1000,'Flooded board unexpectedly empty');require(delta<.0003,f'Difference {delta:.8f} mm²');require(actual.difference(substrate(d).buffer(.000002)).area<.0001,'Off-board ink survived')
                require(not actual.intersects(Point(10,45)),'Mounting hole not cleared');require(not actual.intersects(Point(24,30)),'Cutout not cleared')
                require(not actual.intersects(Point(30,15)),'Open via not cleared');require(actual.intersects(Point(36,15)),'Tented via incorrectly cleared')
            test(f'{shape} / {side}: exact retained substrate, pad masks, slots, cutout and via tenting',flood)
    folder=FIX/'all-tools';d=json.loads((folder/'project.json').read_text())
    for side,letter in [('top','F'),('bottom','B')]:
        def all_tools(side=side,letter=letter):
            actual=read_gerber(folder/f'board-{letter}_Silkscreen.gbr').geometry;expected=expected_source(folder,d,side)
            require(actual.area>1,'Artwork layer is blank');require(actual.symmetric_difference(expected).area<.0002,'Strokes/polygons changed beyond tolerance')
        test(f'{side} text, references, polarity and drawing geometry survive actual Gerber compositing',all_tools)
    def regions():
        import re
        for path in FIX.glob('*/board-*_Silkscreen.gbr'):
            for block in re.findall(r'G36\*(.*?)G37\*',path.read_text(),flags=re.S):require(block.count('D02*')==1,f'{path.name}: multiple contours in a generated region')
    test('Generated legend regions do not depend on nested-hole fill semantics',regions)
    def actual_baseline():
        p=OUT/'fixtures/actual-v130/board-F_Silkscreen.gbr'
        if not p.exists():return  # optional local historical comparison; synthetic reproducer is mandatory above
        require(read_gerber(p).geometry.is_empty,'Historical release did not reproduce expected bug')
    # Do not count optional checks as passes when no historical source is present.
    if (OUT/'fixtures/actual-v130/board-F_Silkscreen.gbr').exists():test('Actual unmodified v1.3.0 Little Light top silkscreen is blank in the corrected reader',actual_baseline)
    result={'date':datetime.now(timezone.utc).isoformat(),'passed':sum(r['pass'] for r in RESULTS),'total':len(RESULTS),'scope':'Independent-language geometry checks against Gerber UNION semantics. No third-party CAM or fabrication validation.','results':RESULTS}
    (OUT/'silkscreen-manufacturing-results.json').write_text(json.dumps(result,indent=2));print(f"{result['passed']}/{result['total']} checks passed.");return 0 if result['passed']==result['total'] else 1
if __name__=='__main__':raise SystemExit(main())

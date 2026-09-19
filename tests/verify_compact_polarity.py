#!/usr/bin/env python3
"""Read the exported role glyphs using the separate Python/Shapely Gerber reader.

Checks ink after all Gerber clear operations, not just the presence of source text.
No third-party CAM, manufacturing, or physical legibility claim.
"""
from pathlib import Path
import json
from shapely.geometry import LineString
from shapely.ops import unary_union
from verify_manufacturing import read_gerber, QUAD
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tests/output';FIX=OUT/'fixtures/compact-polarity';results=[]

def test(name,fn):
    try:fn();results.append({'name':name,'pass':True});print('PASS',name,flush=True)
    except Exception as exc:results.append({'name':name,'pass':False,'error':str(exc)});print('FAIL',name,exc,flush=True)

def face(side,letter,opposite):
    folders=sorted(FIX.glob('*-'+side))
    assert len(folders)==19
    for folder in folders:
        d=json.loads((folder/'project.json').read_text());h=d['board']['height']
        strokes=json.loads((folder/'glyphs.json').read_text())
        actual=read_gerber(folder/f'board-{letter}_Silkscreen.gbr').geometry
        other=read_gerber(folder/f'board-{opposite}_Silkscreen.gbr').geometry
        assert other.is_empty,folder.name+' printed on wrong side'
        pieces=[]
        for pad in set(s['padId'] for s in strokes):
            glyph=unary_union([LineString([(p['x'],h-p['y']) for p in s['points']]).buffer(s['width']/2,quad_segs=QUAD) for s in strokes if s['padId']==pad])
            assert glyph.area>.01,folder.name+' empty role'
            assert glyph.difference(actual.buffer(.000002)).area<.00002,folder.name+' missing or clipped role '+pad
            pieces.append(glyph)
        expected=unary_union(pieces)
        assert actual.symmetric_difference(expected).area<.0001,folder.name+' unexpected/absent artwork'
        for i,a in enumerate(pieces):
            for b in pieces[i+1:]:assert a.distance(b)>.05,folder.name+' glyphs overlap'

def main():
    test('All 19 polarized variants retain every top role glyph after Gerber compositing',lambda:face('top','F','B'))
    test('All 19 rotated/flipped variants retain every bottom role glyph, with no top leakage',lambda:face('bottom','B','F'))
    data={'total':len(results),'passed':sum(r['pass'] for r in results),'scope':'38 standalone fixtures; Python/Shapely output-ink checks, not an external CAM product.','results':results}
    (OUT/'compact-polarity-manufacturing-results.json').write_text(json.dumps(data,indent=2))
    print(f"{data['passed']}/{data['total']} checks passed.")
    return int(data['passed']!=data['total'])
if __name__=='__main__':raise SystemExit(main())

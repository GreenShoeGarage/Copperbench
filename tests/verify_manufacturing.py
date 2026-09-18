#!/usr/bin/env python3
"""Independent-language geometric regression of the generated manufacturing files.

Uses Python/Shapely and its own deliberately restricted Gerber/Excellon readers;
never imports the JavaScript geometry, exporters or read-back code. This is NOT
third-party CAM certification, manufacturer upload validation or physical testing.
Run `node tests/core.test.js` first to regenerate the golden coupon.
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import json
from datetime import datetime, timezone
import math
import re
import sys
import time
from typing import Callable
import shapely
from shapely.geometry import GeometryCollection, LineString, Point, Polygon, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'tests' / 'output'
FIXTURE_ROOT = OUTPUT / 'fixtures'
FIXTURES = FIXTURE_ROOT / 'golden-fabrication'
QUAD = 128

@dataclass
class Layer:
    geometry: object
    lines: list
    flashes: list
    functions: list

def read_gerber(path: Path) -> Layer:
    """Read only the explicitly generated subset, rejecting unknown operations."""
    text = path.read_text(encoding='utf-8')
    assert '%FSLAX46Y46*%' in text and '%MOMM*%' in text
    apertures, shapes, lines, flashes, functions = {}, [], [], [], []
    x = y = 0.0
    aperture = None
    clear = False
    contours = None
    finished = False
    image = GeometryCollection()

    def apply(geometry):
        nonlocal image
        image = image.difference(geometry) if clear else image.union(geometry)

    for raw in re.findall(r'%[^%]*%|[^*%]+\*', text):
        token = raw.strip()
        if token.startswith('%'):
            p = token[1:-1].removesuffix('*')
            if p in ('FSLAX46Y46', 'MOMM'):
                continue
            if p in ('LPD', 'LPC'):
                clear = p == 'LPC'
                continue
            if p.startswith('TF.'):
                functions.append(p)
                continue
            m = re.fullmatch(r'ADD(\d+)([CRO]),([\d.X]+)', p)
            if m:
                apertures[int(m[1])] = (m[2], [float(v) for v in m[3].split('X')])
                continue
            raise ValueError(f'Unsupported Gerber parameter {p}')
        token = token.removesuffix('*')
        if token.startswith('G04') or token == 'G01':
            continue
        if token == 'M02':
            finished = True
            continue
        if token == 'G36':
            assert contours is None
            contours = []
            continue
        if token == 'G37':
            assert contours
            region = GeometryCollection()
            for contour in contours:
                polygon = Polygon(contour)
                assert polygon.is_valid
                region = region.union(polygon)  # Gerber 4.10: each contour is filled independently, not XORed.
            apply(region)
            contours = None
            continue
        m = re.fullmatch(r'D(\d+)', token)
        if m:
            aperture = apertures[int(m[1])]
            continue
        m = re.fullmatch(r'X([+-]?\d+)Y([+-]?\d+)D0([123])', token)
        if not m:
            raise ValueError(f'Unsupported Gerber operation {token}')
        nx, ny, operation = int(m[1]) / 1_000_000, int(m[2]) / 1_000_000, int(m[3])
        if contours is not None:
            if operation == 2:
                contours.append([(nx, ny)])
            elif operation == 1:
                contours[-1].append((nx, ny))
            else:
                raise ValueError('Flash in region')
        elif operation == 1:
            assert aperture and aperture[0] == 'C'
            line = LineString([(x, y), (nx, ny)])
            geom = line.buffer(aperture[1][0] / 2, quad_segs=QUAD)
            # GEOS handles a zero-length line by producing a point buffer.
            apply(geom)
            lines.append((line, aperture[1][0], clear))
        elif operation == 3:
            assert aperture
            shape, sizes = aperture
            if shape == 'C':
                geom = Point(nx, ny).buffer(sizes[0] / 2, quad_segs=QUAD)
            elif shape == 'R':
                geom = box(nx - sizes[0]/2, ny - sizes[1]/2, nx + sizes[0]/2, ny + sizes[1]/2)
            elif shape == 'O':
                w, h = sizes
                dx, dy = max(0, (w-h)/2), max(0, (h-w)/2)
                geom = LineString([(nx-dx, ny-dy), (nx+dx, ny+dy)]).buffer(min(w,h)/2, quad_segs=QUAD)
            else:
                raise ValueError(shape)
            flashes.append((nx, ny, shape, sizes, clear))
            apply(geom)
        x, y = nx, ny
    assert finished and contours is None and image.is_valid
    return Layer(image, lines, flashes, functions)

def read_drills(path: Path) -> list[dict]:
    text = path.read_text(encoding='utf-8')
    assert 'METRIC,TZ' in text and 'M30' in text
    tools, active, holes = {}, None, []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(';') or line in ('M48','METRIC,TZ','%','G90','G05','M30'):
            continue
        m = re.fullmatch(r'T(\d+)C([\d.]+)', line)
        if m:
            tools[int(m[1])] = float(m[2]); continue
        m = re.fullmatch(r'T(\d+)', line)
        if m:
            active = tools[int(m[1])]; continue
        m = re.fullmatch(r'X([+-]?\d+\.\d+)Y([+-]?\d+\.\d+)(?:G85X([+-]?\d+\.\d+)Y([+-]?\d+\.\d+))?', line)
        if not m or active is None:
            raise ValueError(f'Unsupported Excellon operation {line}')
        a = (float(m[1]), float(m[2])); b = (float(m[3]), float(m[4])) if m[3] else a
        holes.append({'diameter':active, 'a':a, 'b':b, 'slot':bool(m[3])})
    return holes

def pad_geometry(part: dict, pad: dict, height: float):
    """Construct expected pad geometry independently from native fixture numbers."""
    sign = -1 if part['side'] == 'bottom' else 1
    angle = math.radians(part['rotation'])
    lx, ly = sign * pad['x'], pad['y']
    x = round(part['x'] + lx * math.cos(angle) - ly * math.sin(angle), 4)
    y = round(part['y'] + lx * math.sin(angle) + ly * math.cos(angle), 4)
    rotation = math.radians(part['rotation'] + sign * pad.get('rotation',0))
    if pad['shape'] == 'circle':
        geom = Point(x, height-y).buffer(pad['w']/2, quad_segs=QUAD)
    elif pad['shape'] == 'rect':
        pts = []
        for px, py in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            px *= pad['w']/2; py *= pad['h']/2
            pts.append((x+px*math.cos(rotation)-py*math.sin(rotation), height-y-px*math.sin(rotation)-py*math.cos(rotation)))
        geom = Polygon(pts)
    else:
        raise ValueError('Golden coupon unexpectedly uses another pad shape')
    return geom, (x, height-y)

def expected_copper(doc: dict, layer: str):
    pieces = []; height=doc['board']['height']
    for part in doc['parts']:
        for pad in part['pads']:
            if pad['drill'] or part['side'] == layer:
                pieces.append(pad_geometry(part,pad,height)[0])
    for trace in doc['traces']:
        if trace['layer'] == layer:
            p = [(v['x'],height-v['y']) for v in trace['points']]
            pieces.append(LineString(p).buffer(trace['width']/2,quad_segs=QUAD))
    for via in doc['vias']:
        pieces.append(Point(via['x'],height-via['y']).buffer(via['diameter']/2,quad_segs=QUAD))
    return unary_union(pieces)

RESULTS=[]
def test(name: str, fn: Callable[[],None]):
    started=time.perf_counter()
    try:
        fn(); RESULTS.append({'name':name,'pass':True,'ms':round((time.perf_counter()-started)*1000)})
        print('PASS',name)
    except Exception as exc:
        RESULTS.append({'name':name,'pass':False,'error':str(exc)})
        print('FAIL',name,str(exc))

def require(condition: bool, message: str='Assertion failed'):
    if not condition:
        raise AssertionError(message)

def main() -> int:
    doc=json.loads((FIXTURE_ROOT/'golden-coupon.json').read_text(encoding='utf-8'))
    layers={p.name:read_gerber(p) for p in FIXTURES.glob('*.gbr')}
    pth=read_drills(FIXTURES/'board-PTH.drl'); npth=read_drills(FIXTURES/'board-NPTH.drl')
    board=box(0,0,40,30)
    test('All nine generated Gerbers parse independently into valid geometries',lambda:require(len(layers)==9 and all(l.geometry.is_valid for l in layers.values())))
    def outline():
        lines=layers['board-Edge_Cuts.gbr'].lines
        centers=unary_union([l[0] for l in lines]); require(centers.bounds==(0.0,0.0,40.0,30.0))
        require(abs(centers.length-140)<1e-9)
        require(len(lines)==4)
    test('Outline centerline is a closed 40 by 30 mm rectangle',outline)
    for layer,prefix in [('top','F'),('bottom','B')]:
        def copper(layer=layer,prefix=prefix):
            actual=layers[f'board-{prefix}_Cu.gbr'].geometry
            expected=expected_copper(doc,layer)
            require(actual.symmetric_difference(expected).area < .0002, f'{layer} differs by {actual.symmetric_difference(expected).area} mm²')
        test(f'{layer.capitalize()} exported copper matches independently constructed native geometry',copper)
    def bottom():
        actual=layers['board-B_Cu.gbr'].geometry
        require(actual.covers(Point(8,11)))
        require(not actual.covers(Point(32,11)))
    test('Bottom copper shares the physical origin and is not mirrored',bottom)
    def plated():
        got=sorted((h['a'][0],h['a'][1],h['diameter']) for h in pth)
        require(got==[(14.0,5.0,.5),(30.0,16.73,1.0),(30.0,19.27,1.0)])
        for h in pth:
            for face in ['F','B']:
                require(layers[f'board-{face}_Cu.gbr'].geometry.covers(Point(*h['a'])))
    test('Plated drills align with both header pads and the through via',plated)
    def slots():
        require(len(npth)==2)
        h=next(h for h in npth if h['slot'])
        require(abs(h['diameter']-1.2)<1e-9)
        require(abs(math.dist(h['a'],h['b'])-2)<.000002)
        require(abs((h['a'][0]+h['b'][0])/2-36)<1e-9)
        require(abs((h['a'][1]+h['b'][1])/2-5)<1e-9)
        require(any(h['a']==(3.0,27.0) and h['diameter']==2 and not h['slot'] for h in npth))
    test('Non-plated round hole and G85 slot preserve centers, travel and tool sizes',slots)
    def masks():
        for face in ['F','B']:
            mask=layers[f'board-{face}_Mask.gbr']
            require('TF.FilePolarity,Negative' in mask.functions)
            for part in doc['parts']:
                for pad in part['pads']:
                    if pad['drill'] or part['side']==('top' if face=='F' else 'bottom'):
                        geom,center=pad_geometry(part,pad,30)
                        require(mask.geometry.covers(Point(*center)))
                        require(geom.difference(mask.geometry).area<.00001)
    test('Mask openings cover the applicable pads on each face',masks)
    def silk():
        for face in ['F','B']:
            image=layers[f'board-{face}_Silkscreen.gbr'].geometry
            require(image.area>0)
            require(image.difference(board).area < 1e-8)
            require(image.intersection(layers[f'board-{face}_Mask.gbr'].geometry).area < 1e-8)
    test('Final silkscreen is nonempty, inside the board and clear of openings',silk)
    def paste():
        for face in ['F','B']:
            p=layers[f'board-{face}_Paste.gbr']
            require(len(p.flashes)==3)
            require(all(abs(f[3][0]-2)<1e-9 for f in p.flashes))
    test('Paste apertures include surface pads, not through-hole pads or vias',paste)
    def edgeclear():
        for face in ['F','B']:
            image=layers[f'board-{face}_Cu.gbr'].geometry
            require(board.contains(image))
            require(image.distance(board.boundary)>=doc['profile']['edge'])
    test('All exported coupon copper remains within the configured board-edge clearance',edgeclear)
    def malformed():
        # Check the independent reader does not accept an unknown interpolation mode.
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'bad.gbr';p.write_text('%FSLAX46Y46*%\n%MOMM*%\nG02X0Y0D01*\nM02*')
            try: read_gerber(p)
            except ValueError: return
            raise AssertionError('Unsupported arc accepted')
    test('Independent reader rejects unsupported Gerber operations',malformed)
    result={'date':datetime.now(timezone.utc).isoformat(),'python':sys.version.split()[0],'shapely':shapely.__version__,'passed':sum(r['pass'] for r in RESULTS),'total':len(RESULTS),'scope':'Separate Python/Shapely golden-coupon regression; not third-party CAM or physical validation.','results':RESULTS}
    (OUTPUT/'manufacturing-results.json').write_text(json.dumps(result,indent=2))
    print(f"\n{result['passed']}/{result['total']} checks passed.")
    return 0 if result['passed']==result['total'] else 1

if __name__=='__main__':
    if not (FIXTURE_ROOT/'golden-coupon.json').is_file():
        raise SystemExit('Missing generated coupon. Run: node tests/core.test.js')
    raise SystemExit(main())

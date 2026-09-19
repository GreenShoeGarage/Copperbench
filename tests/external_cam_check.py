#!/usr/bin/env python3
"""Optional independently developed parser smoke check; not fabrication approval.
Install test-only gerbonara==1.6.3 in a development environment. No app data is sent.
"""
from pathlib import Path
import argparse, json, warnings
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'tests/output';OUT.mkdir(exist_ok=True)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',nargs='?',type=Path,default=OUT/'fixtures/editing');args=p.parse_args()
report={'parser':'gerbonara','scope':'Third-party parsing and SVG rendering; does not certify circuit function, visible-ink correctness or manufacturer acceptance','files':[]}
try:
    from gerbonara import GerberFile, ExcellonFile
    from importlib.metadata import version
    report['version']=version('gerbonara')
except ImportError as error:
    report.update(status='blocked',reason=str(error));(OUT/'external-cam-qualification.json').write_text(json.dumps(report,indent=2));print('BLOCKED: install gerbonara==1.6.3 to run the independent parser check.');raise SystemExit(2)
files=sorted(args.folder.glob('*.gbr'))+sorted(args.folder.glob('*.drl'));render=OUT/'external-cam-svg';render.mkdir(exist_ok=True)
if not files:raise SystemExit('No generated Gerber/Excellon fixtures found; run the engine suites first.')
for path in files:
    try:
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter('always');cam=(ExcellonFile if path.suffix=='.drl' else GerberFile).open(path)
            svg=str(cam.to_svg());assert '<svg' in svg,'No SVG document returned'
        (render/(path.name+'.svg')).write_text(svg)
        report['files'].append({'name':path.name,'status':'passed','objects':len(cam.objects),'warnings':[str(w.message) for w in captured]})
    except Exception as error:report['files'].append({'name':path.name,'status':'failed','error':str(error)})
report['status']='passed' if all(f['status']=='passed' for f in report['files']) else 'failed'
(OUT/'external-cam-qualification.json').write_text(json.dumps(report,indent=2));print(report['status'],len(files),'files; inspect SVG output separately.');raise SystemExit(0 if report['status']=='passed' else 1)

/* COPPERBENCH -> CASEBENCH. Native schema-5 snapshots, not a second geometry model.
   Part pads/holes stay LOCAL; x/y/rotation/side stay untouched. CASEBENCH owns
   conversion into enclosure XYZ. In particular, never add module stackGap to
   body.z again or transform the already-placed circuit-block members twice. */
(function(root){
'use strict';
const C=root.CB, X=C.CaseBench={};
// Bounds retrieved from CASEBENCH's native adapter (adapter version 2.0.1,
// retained in the v2.3.0 file). This is a preflight, not an embedded importer.
X.LIMITS=Object.freeze({jsonBytes:8388608,parts:512,pads:8192,holes:1024,cutouts:128,polygon:512});
X.filename=title=>(String(title||'board').normalize('NFKD').replace(/[^a-z0-9_-]+/gi,'-').replace(/^-|-$/g,'').slice(0,80)||'board')+'-casebench.json';
X.prepare=function(input,options={}){
 if(!input||input.app!=='COPPERBENCH')throw Error('Open a CopperBench project before exporting to CaseBench.');
 if(input.units!==undefined&&input.units!=='mm')throw Error('CaseBench requires millimetres. This export never guesses or rescales units.');
 if(options.includeProjectData!==undefined&&typeof options.includeProjectData!=='boolean')throw Error('Invalid CaseBench export option.');
 const complete=options.includeProjectData===true;
 // Work only on a clone. Prune optional non-mechanical records before native
 // validation so an obsolete, unused library/baseline cannot block a handoff.
 const candidate=C.clone(input);
 if(!complete){candidate.art=[];candidate.assets=[];candidate.baseline=null;candidate.blockLibrary=[];}
 const document=C.validateDoc(candidate);
 document.units='mm';
 // Revalidated native data retains IDs, raw placement, local footprint geometry,
 // mounted-module metadata and world-positioned block members verbatim.
 const parts=document.parts,pads=parts.reduce((n,p)=>n+p.pads.length,0);
 const mounting=C.mountingHoles?C.mountingHoles(document):[];
 const holes=C.G.holes(document),outline=C.G.outline(document),bounds=C.G.bounds(outline);
 const errors=[];
 const cap=(n,max,label)=>{if(n>max)errors.push(label+' exceed the CaseBench adapter limit ('+n+' / '+max+').');};
 cap(parts.length,X.LIMITS.parts,'Placed components');cap(pads,X.LIMITS.pads,'Component pads');
 cap(document.holes.length,X.LIMITS.holes,'Standalone holes');cap(document.cutouts.length,X.LIMITS.cutouts,'Board cutouts');
 if(document.board.shape==='polygon')cap(document.board.points.length,X.LIMITS.polygon,'Board-outline vertices');
 for(const cut of document.cutouts)cap(cut.points.length,X.LIMITS.polygon,'Cutout '+cut.id+' vertices');
 if(errors.length)throw Error(errors.join(' ')); // Refuse oversize contours before quadratic boundary checks.
 // Invalid mechanical boundaries must not turn into plausible enclosure data.
 if(!C.G.simple(outline))errors.push('The board outline is not a simple closed boundary. Repair it before exporting.');
 for(const cut of document.cutouts)if(!C.G.simple(cut.points))errors.push('Cutout '+cut.id+' is not a simple closed boundary.');
 const json=JSON.stringify(document,null,2)+'\n',bytes=new TextEncoder().encode(json).byteLength;
 cap(bytes,X.LIMITS.jsonBytes,'JSON bytes');
 if(errors.length)throw Error(errors.join(' ') + (bytes>X.LIMITS.jsonBytes&&complete?' Turn off “Include project extras” to omit image assets, artwork, saved baseline and unused templates.':''));
 const warnings=[];
 if(!parts.length)warnings.push('Bare board: no component envelopes are present.');
 const outside=parts.filter(p=>!C.G.inside({x:p.x,y:p.y},outline)).map(p=>p.ref);
 if(outside.length)warnings.push('Component centres outside the board: '+outside.slice(0,8).join(', ')+(outside.length>8?'…':'')+'. Placement is preserved; inspect in CaseBench.');
 const summary={title:document.title,id:document.id,schema:document.schema,bytes,complete,
  width:C.q(bounds.maxX-bounds.minX),height:C.q(bounds.maxY-bounds.minY),thickness:document.board.thickness,
  components:parts.length,top:parts.filter(p=>p.side==='top').length,bottom:parts.filter(p=>p.side==='bottom').length,
  mountingHoles:document.holes.length+mounting.length,linkedMountingHoles:mounting.length,
  platedDrills:holes.filter(h=>h.plated).length,slots:holes.filter(h=>h.slot>0).length,cutouts:document.cutouts.length,
  blocks:document.blockInstances.length,modules:parts.filter(p=>p.module).length,
  // These are stored representative heights, NOT a verified overall assembly
  // height. No stack-gap/lead/cable assumptions are added at export.
  topEnvelopeHeight:parts.filter(p=>p.side==='top').reduce((h,p)=>Math.max(h,p.body.z),0),
  bottomEnvelopeHeight:parts.filter(p=>p.side==='bottom').reduce((h,p)=>Math.max(h,p.body.z),0)};
 return{document,json,filename:X.filename(document.title),summary,warnings};
};
if(typeof module!=='undefined')module.exports=X;
})(typeof self!=='undefined'?self:globalThis);

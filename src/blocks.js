/* COPPERBENCH circuit blocks. MIT. Ordinary PCB objects remain authoritative.
 * No circuit simulation, automatic supply joining, or implicit net-name merge.
 * Templates use local coordinates; every insertion remaps object and net IDs.
 */
(function(root){'use strict';
const C=root.CB,G=C.G,B=C.Blocks={revision:1};
const keys=['parts','traces','vias'];
const finite=(x,lo=-10000,hi=10000)=>typeof x==='number'&&Number.isFinite(x)&&x>=lo&&x<=hi;
const text=(x,n)=>typeof x==='string'&&x.length<=n;
const flipLayer=s=>s==='top'?'bottom':s==='bottom'?'top':s;
const baseValidate=C.validateDoc;
function geometry(d){return keys.flatMap(k=>d[k]||[]);}
function assert(c,msg){if(!c)throw Error(msg);}
B.validate=function(input){
 const t=C.clone(input);assert(t&&t.app==='COPPERBENCH-BLOCK'&&t.schema===1,'Use a COPPERBENCH-BLOCK schema-1 JSON file.');
 assert(text(t.id,100)&&t.id&&text(t.name,100)&&t.name.trim(),'Block identity and name are required.');
 assert(text(t.description||'',2000),'Block description is too long.');
 assert(Array.isArray(t.notes)&&t.notes.length<=30&&t.notes.every(s=>text(s,1000)),'Invalid block review notes.');
 for(const k of keys)assert(Array.isArray(t[k])&&t[k].length<=(k==='parts'?100:500),'Invalid or oversized block '+k+'.');
 assert(t.parts.length>0,'A block needs at least one component.');
 assert(Array.isArray(t.nets)&&t.nets.length<=200&&Array.isArray(t.ports)&&t.ports.length<=100,'Invalid block nets or ports.');
 for(const k of ['zones','art','holes','cutouts','keepouts','assets','blockInstances','blockLibrary'])assert(t[k]===undefined||(Array.isArray(t[k])&&t[k].length===0),'Block exchange supports components, traces and vias only; '+k+' cannot be silently discarded.');
 const ids=new Set,netIDs=new Set(t.nets.map(n=>n.id));
 for(const p of t.ports){assert(p&&text(p.key,80)&&p.key&&text(p.name,100)&&netIDs.has(p.net),'A block port must reference a declared net.');assert(!ids.has(p.key),'Duplicate block port key.');ids.add(p.key);}
 assert(new Set(t.ports.map(p=>p.net)).size===t.ports.length,'Use one port per block net.');
 const d=C.blank();d.title=t.name;for(const k of [...keys,'nets'])d[k]=C.clone(t[k]);d.baseline=null;
 const checked=baseValidate(d);for(const k of [...keys,'nets'])t[k]=checked[k];
 for(const p of t.parts){assert(!p.blockMember,'Block templates cannot embed membership pointers.');assert(text(p.name||'',200),'Invalid component name.');}
 t.revision=Number.isInteger(t.revision)&&t.revision>0?t.revision:1;return t;
};
B.entries=doc=>[...(C.BLOCK_CATALOG||[]),...(doc.blockLibrary||[])];
B.get=(doc,id)=>B.entries(doc).find(t=>t.id===id);
B.members=(doc,instance)=>keys.flatMap(k=>doc[k].filter(o=>instance.members.includes(o.id)).map(o=>({key:k,object:o})));
B.forObject=(doc,id)=>(doc.blockInstances||[]).find(b=>b.members.includes(id));
B.bounds=function(items){const pts=[];for(const p of items.parts||[])pts.push(...G.rect(-p.body.w/2,-p.body.h/2,p.body.w,p.body.h).map(q=>C.world(p,q)),...p.pads.map(q=>C.world(p,q)));for(const t of items.traces||[])pts.push(...t.points);for(const v of items.vias||[])pts.push(v);return G.bounds(pts);};
function mapGeometry(items,x,y,rotation,flip){
 const point=p=>{const q=G.rotate({x:flip?-p.x:p.x,y:p.y},rotation);return {x:C.q(x+q.x),y:C.q(y+q.y)};};
 for(const p of items.parts){const q=point(p);p.x=q.x;p.y=q.y;p.rotation=C.q((flip?-p.rotation:p.rotation)+rotation);if(flip)p.side=flipLayer(p.side);}
 for(const t of items.traces){t.points=t.points.map(point);if(flip)t.layer=flipLayer(t.layer);}
 for(const v of items.vias){const q=point(v);v.x=q.x;v.y=q.y;}
}
B.preview=function(template,x,y,rotation=0,flip=false){const t=B.validate(template);mapGeometry(t,x,y,rotation,flip);return t;};
B.insert=function(doc,input,opts={}){
 const t=B.validate(input),x=opts.x??doc.board.width/2,y=opts.y??doc.board.height/2,rotation=opts.rotation||0,flip=!!opts.flip;
 assert(finite(x)&&finite(y)&&finite(rotation,-36000,36000),'Invalid block placement.');
 let count=1;while((doc.blockInstances||[]).some(b=>b.label==='B'+count)||doc.nets.some(n=>n.name.startsWith('B'+count+'/')))count++;
 const label='B'+count,id=C.uid('block'),remap=new Map,portKeys=new Set(t.ports.map(p=>p.key)),mapping=opts.mapping||{},targets=new Set;
 for(const key of Object.keys(mapping)){assert(portKeys.has(key),'Unknown block port '+key+'.');const n=mapping[key];if(n){assert(doc.nets.some(a=>a.id===n),'Mapped port references a missing project net.');assert(!targets.has(n),'Two distinct block ports cannot be joined to the same net during insertion.');targets.add(n);}}
 for(const n of t.nets){const port=t.ports.find(p=>p.net===n.id),existing=port&&mapping[port.key];remap.set(n.id,existing||C.uid('n'));}
 const parts=[];for(const source of t.parts){const p=C.makePart({...doc,parts:[...doc.parts,...parts]},{...source,ref:source.ref.replace(/\d+$/,'')||'U'},source.x,source.y);p.libraryId=source.libraryId||source.id;p.rotation=source.rotation;p.side=source.side;p.locked=false;delete p.blockMember;for(const pad of p.pads)pad.net=pad.net?remap.get(pad.net):null;parts.push(p);}
 const traces=t.traces.map(o=>({...C.clone(o),id:C.uid('t'),net:o.net?remap.get(o.net):null,locked:false}));
 const vias=t.vias.map(o=>({...C.clone(o),id:C.uid('v'),net:o.net?remap.get(o.net):null,locked:false}));
 const placed={parts,traces,vias};mapGeometry(placed,x,y,rotation,flip);
 const nets=t.nets.filter(n=>!doc.nets.some(a=>a.id===remap.get(n.id))).map(n=>({...C.clone(n),id:remap.get(n.id),name:(label+'/'+n.name).slice(0,80)}));
 const record={id,label,name:t.name,templateId:t.id,templateRevision:t.revision,x:C.q(x),y:C.q(y),rotation:C.q(rotation),flipped:flip,members:geometry(placed).map(o=>o.id),ports:t.ports.map(p=>({...C.clone(p),net:remap.get(p.net)})),notes:C.clone(t.notes),reviewed:false};
 // Stage and validate before touching the destination; failed insertions are atomic.
 const staged=C.clone(doc);staged.nets.push(...nets);for(const k of keys)staged[k].push(...placed[k]);(staged.blockInstances??=[]).push(record);C.validateDoc(staged);
 doc.nets.push(...nets);for(const k of keys)doc[k].push(...placed[k]);(doc.blockInstances??=[]).push(record);return record;
};
// Preflight the proposed copper against the destination, not just the template.
B.plan=function(doc,input,opts={}){const staged=C.clone(doc);staged.zones.forEach(z=>z.fill=null);const record=B.insert(staged,input,opts);const ids=new Set(record.members);const errors=G.findings(staged).filter(f=>f.severity==='error'&&f.code!=='unrouted'&&(f.objects||[]).some(id=>ids.has(id)||[...ids].some(x=>id.startsWith(x+':'))));return {document:staged,record,errors,ok:!errors.length};};
B.example=function(){const d=C.blank();d.title='Circuit blocks · six editable starting points';d.board.width=156;d.board.height=105;d.board.outline=G.rect(0,0,156,105);const positions=[[25,23],[77,23],[128,23],[25,75],[78,75],[130,75]];(C.BLOCK_CATALOG||[]).forEach((t,i)=>B.insert(d,t,{x:positions[i][0],y:positions[i][1]}));return d;};
B.capture=function(doc,ids,opts={}){
 const set=new Set(ids),picked={};for(const k of keys)picked[k]=C.clone(doc[k].filter(o=>set.has(o.id)));
 assert(picked.parts.length,'Select at least one component to make a circuit block.');
 const unsupported=ids.filter(id=>!geometry(picked).some(o=>o.id===id));assert(!unsupported.length,'Only components, traces and vias can be captured. Remove other object types from the selection.');
 const b=B.bounds(picked),cx=opts.origin?.x??(b.minX+b.maxX)/2,cy=opts.origin?.y??(b.minY+b.maxY)/2;
 for(const p of picked.parts){p.x=C.q(p.x-cx);p.y=C.q(p.y-cy);p.locked=false;delete p.blockMember;}
 for(const t of picked.traces){t.points=t.points.map(p=>({x:C.q(p.x-cx),y:C.q(p.y-cy)}));t.locked=false;}
 for(const v of picked.vias){v.x=C.q(v.x-cx);v.y=C.q(v.y-cy);v.locked=false;}
 const used=new Set([...picked.parts.flatMap(p=>p.pads.map(a=>a.net)),...picked.traces.map(a=>a.net),...picked.vias.map(a=>a.net)].filter(Boolean));
 const nets=C.clone(doc.nets.filter(n=>used.has(n.id)));
 const portSeen=new Set;const ports=opts.ports?C.clone(opts.ports).filter(p=>used.has(p.net)&&!portSeen.has(p.net)&&portSeen.add(p.net)):nets.map((n,i)=>({key:'port'+(i+1),name:n.name,net:n.id,kind:'signal'}));
 return B.validate({app:'COPPERBENCH-BLOCK',schema:1,id:C.uid('customblock'),revision:1,name:opts.name||'Captured circuit',description:opts.description||'User-captured PCB geometry. Review connections, values and manufacturing rules before use.',notes:opts.notes||['User-defined circuit. No electrical operation or physical fit has been verified.'],...picked,nets,ports});
};
B.exportInstance=function(doc,id){const b=(doc.blockInstances||[]).find(b=>b.id===id);assert(b,'Select a circuit block first.');const t=B.capture(doc,b.members,{name:b.name,notes:b.notes,ports:b.ports});for(const n of t.nets)if(n.name.startsWith(b.label+'/'))n.name=n.name.slice(b.label.length+1);return t;};
B.copy=function(doc,id,opts={}){return B.insert(doc,B.exportInstance(doc,id),opts);};
B.transform=function(doc,id,{x,y,rotation=0,flip=false}={}){
 const b=(doc.blockInstances||[]).find(b=>b.id===id);assert(b,'Missing circuit block.');const members=B.members(doc,b);assert(members.every(m=>!m.object.locked),'Unlock all block members before transforming the block.');
 assert(finite(x)&&finite(y)&&finite(rotation,-36000,36000),'Invalid block transform.');
 const items={};for(const k of keys)items[k]=members.filter(m=>m.key===k).map(m=>m.object);
 for(const p of items.parts){p.x=C.q(p.x-b.x);p.y=C.q(p.y-b.y);}for(const t of items.traces)t.points=t.points.map(p=>({x:C.q(p.x-b.x),y:C.q(p.y-b.y)}));for(const v of items.vias){v.x=C.q(v.x-b.x);v.y=C.q(v.y-b.y);}
 mapGeometry(items,x,y,rotation,flip);b.x=C.q(x);b.y=C.q(y);b.rotation=C.q((flip?-b.rotation:b.rotation)+rotation);b.flipped=!!b.flipped!==!!flip;
 // External attached traces are NOT stretched; ordinary connectivity checks reveal breaks.
};
B.detach=function(doc,id){doc.blockInstances=(doc.blockInstances||[]).filter(b=>b.id!==id);};
B.sync=function(doc){const ids=new Set(geometry(doc).map(o=>o.id));doc.blockInstances=(doc.blockInstances||[]).map(b=>({...b,members:b.members.filter(id=>ids.has(id)),ports:b.ports.filter(p=>doc.nets.some(n=>n.id===p.net))})).filter(b=>b.members.length);};
C.validateDoc=function(input){
 const d=baseValidate(input);d.blockInstances??=[];d.blockLibrary??=[];
 assert(Array.isArray(d.blockInstances)&&d.blockInstances.length<=500,'Invalid circuit-block records.');assert(Array.isArray(d.blockLibrary)&&d.blockLibrary.length<=100,'Invalid personal block library.');
 const allIds=new Set([...geometry(d),...d.nets,...d.holes,...d.art,...d.zones,...d.keepouts,...d.cutouts,...d.assets].map(o=>o.id)),objectIds=new Set(geometry(d).map(o=>o.id)),taken=new Set;
 for(const b of d.blockInstances){assert(b&&text(b.id,100)&&b.id&&!allIds.has(b.id),'Duplicate circuit-block identity.');allIds.add(b.id);assert(text(b.label,30)&&text(b.name,100)&&text(b.templateId,100)&&finite(b.x)&&finite(b.y)&&finite(b.rotation,-36000,36000),'Invalid block record.');assert(Array.isArray(b.members)&&b.members.length>0&&b.members.length<=1100,'Invalid block membership.');for(const id of b.members){assert(objectIds.has(id)&&!taken.has(id),'A block member is missing or belongs to more than one block.');taken.add(id);}assert(Array.isArray(b.ports)&&b.ports.length<=100&&b.ports.every(p=>p&&text(p.key,80)&&text(p.name,100)&&d.nets.some(n=>n.id===p.net)),'Invalid block port records.');assert(Array.isArray(b.notes)&&b.notes.length<=30&&b.notes.every(s=>text(s,1000)),'Invalid block notes.');if(b.reviewed!==undefined)assert(typeof b.reviewed==='boolean','Invalid block review flag.');}
 const libIds=new Set((C.BLOCK_CATALOG||[]).map(t=>t.id));d.blockLibrary=d.blockLibrary.map(t=>{const v=B.validate(t);assert(!libIds.has(v.id),'Duplicate circuit block library identity.');libIds.add(v.id);return v;});return d;
};
B.remapPortNet=function(doc,oldNet,newNet){for(const b of doc.blockInstances||[])for(const p of b.ports)if(p.net===oldNet)p.net=newNet;};
const assign=C.assignPads;C.assignPads=function(doc,ids,net,merge=false){const old=merge?[...new Set(C.pads(doc).filter(p=>ids.includes(p.id)).map(p=>p.net).filter(Boolean))]:[];const out=assign(doc,ids,net,merge);for(const n of old)if(n!==net)B.remapPortNet(doc,n,net);return out;};
const findings=G.findings;G.findings=function(d){const f=findings(d);for(const b of d.blockInstances||[])if(!b.reviewed)f.push({id:'block-review-'+b.id,severity:'warning',code:'block-review',message:b.label+' · '+b.name+': review values, supply limits and connections.',objects:b.members,evidence:b.notes.join(' '),confidence:'review-required'});return f;};
if(typeof module!=='undefined')module.exports=B;
})(typeof self!=='undefined'?self:globalThis);

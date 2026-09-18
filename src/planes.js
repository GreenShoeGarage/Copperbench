/* COPPERBENCH board planes. MIT, Green Shoe Garage, 2026.
   A managed plane is an ordinary, manufacturable copper zone whose outline
   follows the board. Net identity is never a substitute for copper contact.
   Connection plans are pure, cancellable-worker proposals. No input is mutated. */
(function(root){'use strict';const C=root.CB,G=C.G,P=C.Planes={};
P.list=d=>d.zones.filter(z=>z.boardPlane===true);
P.get=(d,layer)=>P.list(d).find(z=>z.layer===layer)||null;
P.sync=function(d){const points=G.outline(d);for(const z of P.list(d)){if(JSON.stringify(z.points)!==JSON.stringify(points)){z.points=C.clone(points);z.fill=null;}}return d;};
P.set=function(d,layer,net,options={}){
 if(!['top','bottom'].includes(layer))throw Error('Choose the top or bottom copper face.');
 if(net&&!d.nets.some(n=>n.id===net))throw Error('Choose an existing electrical net.');
 const old=P.get(d,layer);if(!net){if(old)d.zones=d.zones.filter(z=>z.id!==old.id);return null;}
 const z=old||{id:C.uid('plane'),boardPlane:true,layer,thermal:true,gap:.3,spoke:.5,step:.25};
 z.net=net;z.points=C.clone(G.outline(d));z.fill=null;
 for(const k of ['thermal','gap','spoke','step'])if(options[k]!==undefined)z[k]=options[k];
 if(!old)d.zones.push(z);d.schema=C.SCHEMA;d.version=C.VERSION;
 return z;
};
P.groundPreset=function(d,both=false){const n=d.nets.find(n=>/^(gnd|ground)$/i.test(n.name))?.id||C.newNet(d,'GND');P.set(d,'top',both?n:null);P.set(d,'bottom',n);return n;};
P.refill=function(d){P.sync(d);for(const r of C.R.fillAll(d)){const z=d.zones.find(z=>z.id===r.id);if(z)z.fill=r.fill;}return d;};
P.status=function(d,conn=G.connectivity(d)){
 const pads=C.pads(d);return P.list(d).map(z=>{
  const groups=conn.zoneGroups?.[z.id]||{},roots=Object.keys(groups).sort((a,b)=>groups[b]-groups[a]),main=roots[0]||null;
  const rows=pads.filter(p=>p.net===z.net).map(p=>{const group=conn.padGroups[p.id]===undefined?null:String(conn.padGroups[p.id]);let state=!z.fill?'stale':!roots.length?'empty':group===main?'connected':roots.includes(group)?'isolated':p.layers!=='both'&&p.layers!==z.layer?'needs-via':'unconnected';return{id:p.id,ref:p.ref,pin:p.pin,layer:p.layers,state};});
  return{id:z.id,layer:z.layer,net:z.net,name:C.netName(d,z.net),state:!z.fill?'stale':!roots.length?'empty':roots.length>1?'split':'filled',area:z.fill?.area||0,regions:roots.length,main,roots,rows,connected:rows.filter(p=>p.state==='connected').length,total:rows.length,removedIslands:z.fill?.removedIslands||0};
 });
};
P.findings=function(d,conn){const out=[],seen=new Set;for(const a of P.status(d,conn)){
 if(a.state==='split')out.push({severity:'error',code:'plane-split',message:`${a.layer} ${a.name} plane has ${a.regions} electrically separate copper regions. Bridge or remove stranded copper; matching net names do not connect it.`,objects:[a.id]});
 for(const pad of a.rows)if(['isolated','needs-via','unconnected'].includes(pad.state)){
  const key=a.id+pad.id;if(seen.has(key))continue;seen.add(key);
  out.push({severity:'warning',code:'plane-pad-unconnected',message:`${pad.ref}.${pad.pin} is not connected to the main ${a.layer} ${a.name} plane region. ${pad.state==='needs-via'?'A surface-mount lead on the other face needs a copper path and a via.':'Inspect the actual filled copper.'}`,objects:[pad.id.split(':')[0],a.id]});
 }
 }return out;};
function rowFor(d,id,layer){return P.status(d).find(s=>s.layer===layer)?.rows.find(p=>p.id===id);}
function nearTargets(d,z,p,limit=6){const conn=G.connectivity(d),status=P.status(d,conn).find(s=>s.id===z.id);if(!status?.main)return[];
 const items=G.copper(d).filter(a=>a.owner===z.id),targets=[];
 for(const [rectangleIndex,a] of items.entries()){ // Locate target rectangles in the main electrical region, not an orphan patch.
  const b=a.box,x=C.clamp(p.x,b.minX+.02,b.maxX-.02),y=C.clamp(p.y,b.minY+.02,b.maxY-.02);
  const q={x:C.q(x),y:C.q(y),net:z.net,layers:z.layer};
  if(G.dist(q,p)>14)continue;
  // Use the actual electrical root of this filled rectangle, including split planes.
  if(conn.zoneRoots?.[z.id]?.[rectangleIndex]!==status.main)continue;
  if(!targets.some(t=>G.dist(t,q)<.3))targets.push(q);
 }
 return targets.sort((a,b)=>G.dist(a,p)-G.dist(b,p)).slice(0,limit);
}
function attemptRoute(d,p,target,width){const result=C.R.route(d,p,target,{width,layer:p.layers==='both'?target.layers:p.layers,vias:false,step:.3,maxNodes:10000});if(result.error||!result.traces.length)return null;const next=C.clone(d);next.traces.push(...result.traces);next.vias.push(...result.vias);return next;}
P.planConnections=function(input,ids,layer,options={},progress=()=>{}){
 let d=C.clone(input);P.sync(d);const z=P.get(d,layer);if(!z)throw Error('Assign a net to that board face first.');
 ids=[...new Set(ids||[])];if(!ids.length||ids.length>128)throw Error('Pick between one and 128 component leads.');
 const originalPads=ids.map(id=>C.getPad(d,id));if(originalPads.some(p=>!p))throw Error('A selected lead no longer exists.');
 for(const p of originalPads)if(p.net&&p.net!==z.net)throw Error(`${p.ref}.${p.pin} belongs to ${C.netName(d,p.net)}, not ${C.netName(d,z.net)}. Nothing was changed. Edit circuit intent explicitly; planes never merge nets automatically.`);
 const width=Number(options.width||d.settings.traceWidth);if(!Number.isFinite(width)||width<d.profile.minTrace||width>25)throw Error('Choose a trace width within the fabrication rules.');
 const size=C.V.sizeCheck(d,C.V.defaults(d));if(!size.ok)throw Error(size.reason);
 const beforeTraces=new Set(d.traces.map(t=>t.id)),beforeVias=new Set(d.vias.map(v=>v.id)),assigned=[];
 for(const p of originalPads)if(!p.net){p.sourcePad.net=z.net;assigned.push(p.id);}
 // Check a newly connected lead itself, not only the proposed stub and via.
 // Managed fills are derived obstacles; hard copper and keepouts are not.
 for(const id of ids){const p=C.getPad(d,id);for(const face of (p.layers==='both'?['top','bottom']:[p.layers])){
  const poly=G.padPoly(p),obs=G.obstacles(d,z.net,face);
  if(obs.items.some(a=>G.polyDist(poly,a.poly)<d.profile.clearance-C.EPS))throw Error(`${p.ref}.${p.pin}: lead clearance conflicts with existing copper, a hole or a keepout. Nothing was changed.`);
 }}
 P.refill(d);const steps=[];
 for(let index=0;index<ids.length;index++){
  const id=ids[index];let p=C.getPad(d,id),row=rowFor(d,id,layer);
  if(row?.state==='connected'){steps.push({id,kind:'direct',message:`${p.ref}.${p.pin}: connected through existing copper / pad contact.`});progress({complete:index+1,total:ids.length});continue;}
  let accepted=null,kind='stub';
  // Reuse a nearby, already plane-connected through via before drilling another.
  const conn=G.connectivity(d),status=P.status(d,conn).find(a=>a.layer===layer);
  const existing=d.vias.filter(v=>v.net===z.net&&(conn.objectGroups[v.id]||[]).includes(status?.main)&&G.dist(v,p)<14).sort((a,b)=>G.dist(a,p)-G.dist(b,p));
  for(const v of existing.slice(0,3)){let next=attemptRoute(d,p,{...v,layers:p.layers==='both'?layer:p.layers},width);if(next){P.refill(next);if(rowFor(next,id,layer)?.state==='connected'){accepted=next;kind='reused-via';break;}}}
  if(!accepted&&(p.layers==='both'||p.layers===layer)){
   for(const target of nearTargets(d,P.get(d,layer),p)){let next=attemptRoute(d,p,target,width);if(next){P.refill(next);if(rowFor(next,id,layer)?.state==='connected'){accepted=next;break;}}}
  }
  if(!accepted&&p.layers!=='both'&&p.layers!==layer){
   // No via-in-pad: candidate copper is separated from the selected solder pad.
   const part=d.parts.find(a=>a.id===p.partId),outward=Math.atan2(p.y-part.y,p.x-part.x),start=Math.hypot(p.w,p.h)/2+d.settings.viaDiameter/2+.25;
   let filledAttempts=0;
   search:for(const extra of [0,.7,1.5,3,5])for(let i=0;i<16;i++){
    const a=outward+(i%2?1:-1)*Math.ceil(i/2)*Math.PI/8,dist=start+extra,point={x:C.q(p.x+Math.cos(a)*dist),y:C.q(p.y+Math.sin(a)*dist)};
    if(G.pointPolyDist(point,G.padPoly(p))<d.settings.viaDiameter/2+.15)continue;
    const proposal=C.V.propose(d,point,{net:z.net});if(!proposal.ok)continue;
    // Keep a via drill away from every SMT solder pad, including same-net pads.
    if(C.pads(d).some(a=>!a.drill&&G.pointPolyDist(point,G.padPoly(a))<proposal.via.drill/2+.15))continue;
    const points=[{x:p.x,y:p.y},point];if(!G.pathClear(d,points,width,z.net,p.layers).ok)continue;
    const next=C.clone(d);next.vias.push(proposal.via);next.traces.push({id:C.uid('t'),net:z.net,layer:p.layers,width,points,locked:false});P.refill(next);filledAttempts++;
    if(rowFor(next,id,layer)?.state==='connected'){accepted=next;kind='new-via';break search;}
    if(filledAttempts>=8)break search;
   }
  }
  if(!accepted)throw Error(`${p.ref}.${p.pin}: no verified local connection to the main ${layer} plane was found. Nothing was changed. Move the part, clear a nearby path, or route manually; this local helper is not an exhaustive autorouter.`);
  d=accepted;steps.push({id,kind,message:`${p.ref}.${p.pin}: ${kind==='new-via'?'short trace + new through via':kind==='reused-via'?'short route to an existing via':'short copper connection'}.`});progress({complete:index+1,total:ids.length});
 }
 // Later changes in a multi-lead plan must not invalidate earlier attachments.
 for(const id of ids)if(rowFor(d,id,layer)?.state!=='connected')throw Error('A later attachment disconnected an earlier lead. No changes were committed; try individual leads.');
 C.validateDoc(d);
 return{planePlan:true,document:d,layer,net:z.net,assigned,steps,traces:d.traces.filter(t=>!beforeTraces.has(t.id)),vias:d.vias.filter(v=>!beforeVias.has(v.id)),failures:[]};
};
if(typeof module!=='undefined')module.exports=P;
})(typeof self!=='undefined'?self:globalThis);

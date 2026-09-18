/* Through-via creation and validation. Coordinates are board-space millimetres.
   A via is copper on BOTH faces plus ONE plated drill, never a mounting hole.
   Proposals are pure; callers commit an accepted proposal as one undoable edit. */
(function(root){'use strict';const C=root.CB,G=C.G,V=C.V={};
V.presets=[{id:'compact',name:'Compact',diameter:.7,drill:.3},{id:'standard',name:'Standard',diameter:.9,drill:.4},{id:'large',name:'Large',diameter:1.2,drill:.6}];
V.defaults=d=>({diameter:d.settings.viaDiameter,drill:d.settings.viaDrill,tented:!!d.settings.viaTented});
V.sizeCheck=function(d,v){
 if(!Number.isFinite(v.diameter)||!Number.isFinite(v.drill)||v.diameter<=0||v.drill<=0||v.diameter>20||v.drill>20)return{ok:false,code:'via-size',reason:'Enter positive via pad and drill diameters, at most 20 mm.'};
 if(v.diameter<=v.drill)return{ok:false,code:'via-ring',reason:'The copper pad diameter must be larger than the drill.'};
 if(v.drill<d.profile.minDrill-1e-8)return{ok:false,code:'via-drill',reason:`Drill ${v.drill} mm is below the profile minimum of ${d.profile.minDrill} mm.`};
 const ring=(v.diameter-v.drill)/2;
 if(ring<d.profile.minRing-1e-8)return{ok:false,code:'via-ring',reason:`Annular ring ${C.q(ring)} mm is below the profile minimum of ${d.profile.minRing} mm.`};
 return{ok:true,ring:C.q(ring)};
};
V.propose=function(d,point,options={},ignoreId=null){
 const v={id:ignoreId||C.uid('v'),x:C.q(point.x),y:C.q(point.y),...V.defaults(d),...options};delete v.auto;
 if(!Number.isFinite(v.x)||!Number.isFinite(v.y))return{ok:false,code:'via-position',reason:'Choose a finite board position.'};
 const size=V.sizeCheck(d,v);if(!size.ok)return size;
 const managed=new Set(d.zones.filter(z=>z.boardPlane).map(z=>z.id)),copper=G.copper(d).filter(o=>o.owner!==ignoreId); 
 if(options.net===undefined||options.net==='auto'){
  const touching=copper.filter(o=>G.pointPolyDist(v,o.poly)<v.diameter/2-1e-8);
  const nets=[...new Set(touching.map(o=>o.net).filter(Boolean))];
  if(nets.length>1)return{ok:false,code:'via-net-conflict',reason:'This via would join different nets. Move it or edit the circuit intent explicitly.'};
  v.net=nets[0]||null;
 }else v.net=options.net||null;
 if(v.net&&!d.nets.some(n=>n.id===v.net))return{ok:false,code:'via-net',reason:'Choose an existing net.'};
 // Unassigned copper is NOT one shared net. It remains an obstacle.
 for(const layer of ['top','bottom']){
  const items=copper.filter(o=>!managed.has(o.owner)&&(!v.net||o.net!==v.net)&&G.layerMatch(o.layer,layer));
  for(const h of G.holes(d).filter(h=>!h.plated)){const[a,b]=G.holeEndpoints(h);items.push(G.primitive('hole','both',null,h.id,G.capsule(a,b,h.drill)));}
  for(const k of C.keepouts(d))if(G.layerMatch(k.layer,layer))items.push(G.primitive('keepout',k.layer,null,k.id,k.points));
  const result=G.pathClear(d,[v,v],v.diameter,v.net,layer,{items,index:new G.Spatial(items)});
  if(!result.ok)return{ok:false,code:'via-clearance',reason:`${layer==='top'?'Top':'Bottom'} face: ${result.reason}. No via was placed.`,owner:result.owner};
 }
 for(const h of G.holes(d)){
  if(h.id===ignoreId)continue;const[a,b]=G.holeEndpoints(h);
  if(G.segDist(v,a,b)<(v.drill+h.drill)/2+d.profile.minHoleGap-1e-8)return{ok:false,code:'via-hole-spacing',reason:'The via drill is too close to another drill or slot. Move it away from the hole.',owner:h.id};
 }
 return{ok:true,via:{id:v.id,x:v.x,y:v.y,net:v.net,diameter:C.q(v.diameter),drill:C.q(v.drill),tented:!!v.tented,locked:!!v.locked},ring:size.ring};
};
V.add=function(d,point,options={}){const result=V.propose(d,point,options);if(!result.ok)throw Error(result.reason);d.vias.push(result.via);return result.via;};
V.edit=function(d,id,changes){const old=d.vias.find(v=>v.id===id);if(!old)throw Error('Via not found.');if(old.locked&&Object.keys(changes).some(k=>k!=='locked'))throw Error('Unlock this via before editing it.');const next={...old,...changes};if(Object.keys(changes).some(k=>['x','y','diameter','drill','net'].includes(k))){const result=V.propose(d,next,next,id);if(!result.ok)throw Error(result.reason);}Object.assign(old,changes);return old;};
// Nearest point on a segment, for clicking directly onto existing copper.
V.onTrace=function(trace,p){let best=null;for(let i=1;i<trace.points.length;i++){const a=trace.points[i-1],b=trace.points[i],dx=b.x-a.x,dy=b.y-a.y,l=dx*dx+dy*dy,t=l?C.clamp(((p.x-a.x)*dx+(p.y-a.y)*dy)/l,0,1):0,q={x:C.q(a.x+t*dx),y:C.q(a.y+t*dy)},dist=G.dist(p,q);if(!best||dist<best.dist)best={...q,dist};}return best;};
if(typeof module!=='undefined')module.exports=V;
})(typeof self!=='undefined'?self:globalThis);

/* Focused picking and non-destructive edit previews. View state is never exported. */
(function(){
 'use strict';const C=window.CB,G=C.G,P=C.Renderer.prototype,oldHit=P.hit,oldOverlays=P.overlays;
 P.hitAll=function(x,y){
  this.setup();const s=this.state,d=this.doc,pt=this.unproject(x,y),tol=7/this.scale,out=[];
  const add=(type,id,object,extra={})=>{if(!out.some(a=>a.type===type&&a.id===id))out.push({type,id,object,...extra});};
  const filter=s.selectionFilter||'all';
  if(filter==='markings')for(const m of C.Edit.markGroups(d,s.side)){
   const b=m.bounds;
   if(pt.x>=b.minX-tol&&pt.x<=b.maxX+tol&&pt.y>=b.minY-tol&&pt.y<=b.maxY+tol)add('mark',m.id,m.object,{mark:m});
  }
  if(['all','parts','copper'].includes(filter)){
   const pads=C.pads(d).filter(p=>G.layerMatch(p.layers,s.side)).map(p=>({p,dist:G.dist(this.project(p),{x,y})})).sort((a,b)=>a.dist-b.dist);
   for(const {p,dist}of pads)if(dist<Math.max(7,Math.min(p.w,p.h)*this.scale/2+3))add('pad',p.id,p);
   if(filter!=='copper')for(const label of this.polarityHitLabels||[])if(Math.abs(x-label.x)<=label.w/2&&Math.abs(y-label.y)<=label.h/2){const p=pads.find(a=>a.p.id===label.padId)?.p;if(p)add('pad',p.id,p);}
  }
  if(['all','copper'].includes(filter))for(const v of [...d.vias].reverse())if(G.dist(pt,v)<Math.max(v.diameter/2,5/this.scale))add('via',v.id,v);
  if(['all','parts'].includes(filter))for(const p of [...d.parts].reverse().filter(p=>p.side===s.side||p.platform)){
   const poly=(p.platform?.outline||G.rect(-p.body.w/2,-p.body.h/2,p.body.w,p.body.h)).map(a=>C.world(p,a));
   if(p.platform?poly.some((a,i)=>G.segDist(pt,a,poly[(i+1)%poly.length])<tol):G.inside(pt,poly)||G.inside({x,y},poly.map(a=>this.project(a,p.body.z))))add('part',p.id,p);
  }
  if(['all','markings'].includes(filter))for(const a of [...d.art].reverse().filter(a=>a.layer===s.side)){
   const points=a.kind==='text'?C.textPaths(a.text,a.size).flat():a.kind==='image'?(a.rects||[]).flatMap(r=>G.rect(r.x,r.y,r.w,r.h)):a.points||G.rect(0,0,a.w||1,a.h||1),b=G.bounds(points.map(p=>C.artPoint(a,p)));
   if(pt.x>=b.minX-tol&&pt.x<=b.maxX+tol&&pt.y>=b.minY-tol&&pt.y<=b.maxY+tol)add('art',a.id,a);
  }
  if(['all','copper'].includes(filter))for(const t of [...d.traces].reverse().filter(t=>t.layer===s.side))if(C.Edit.segment(t,pt).distance<=t.width/2+tol/2)add('trace',t.id,t);
  if(['all','parts'].includes(filter))for(const h of C.mountingHoles?.(d)||[])if(G.dist(pt,h)<h.drill/2+tol)add('part',h.partId,d.parts.find(p=>p.id===h.partId));
  if(['all','board'].includes(filter)){
   for(const h of d.holes)if(G.segDist(pt,...G.holeEndpoints(h))<h.drill/2+tol)add('hole',h.id,h);
   for(const [type,items]of [['keepout',d.keepouts],['cutout',d.cutouts],['zone',d.zones.filter(z=>G.layerMatch(z.layer,s.side))]])for(const a of [...items].reverse())if(G.inside(pt,a.points))add(type,a.id,a);
   if(G.inside(pt,this.outline))add('board','board',d.board);
  }
  return out;
 };
 P.hit=function(x,y){if(this.state.tool!=='select'||this.state.view==='fabrication')return oldHit.call(this,x,y);return this.hitAll(x,y)[0]||null;};
 P.overlays=function(){
  oldOverlays.call(this);const s=this.state,c=this.ctx;
  if(s.view==='fabrication')return;
  const t=this.doc.traces.find(t=>s.selection?.length===1&&s.selection[0]===t.id);
  if(t&&!t.locked&&s.tool==='select'){
   const i=Math.min(s.editSegment||0,t.points.length-2),a=t.points[i],b=t.points[i+1],mid=this.project({x:(a.x+b.x)/2,y:(a.y+b.y)/2});
   c.save();c.fillStyle='#fff2b3';c.strokeStyle='#235840';c.lineWidth=1.5;c.beginPath();c.rect(mid.x-4,mid.y-4,8,8);c.fill();c.stroke();c.restore();
  }
  if(s.markTarget){const m=C.Edit.markGroups(this.doc,s.side).find(m=>m.id===s.markTarget.id);if(m){const b=m.bounds,p=G.rect(b.minX-.4,b.minY-.4,b.maxX-b.minX+.8,b.maxY-b.minY+.8);this.line([...p,p[0]],'#fff0a3',.15,[3,3]);}}
  const plan=s.editPreview||s.editGhost;
  if(!plan)return;
  const d=plan.document,color=plan.ok===false?'#ff8a80':'#fff0a3';
  if(d){
   // Muted dashed original beneath the bright proposal: both are visual only.
   for(const id of plan.changed||[]){const before=this.doc.traces.find(t=>t.id===id);if(before){this.line(before.points,'#244f48',before.width+.24,[],.06);this.line(before.points,'#70998d',before.width,[4,4],.07);}}
   for(const id of plan.changed||[]){
    const t=d.traces.find(t=>t.id===id);if(t)this.line(t.points,color,t.width+.10,[],.08);
    const v=d.vias.find(v=>v.id===id);if(v)this.polygon(G.circle(v.x,v.y,v.diameter/2),null,color,2);
    const p=d.parts.find(p=>p.id===id);if(p){
     if(plan.copper===false){for(const m of C.Edit.markGroups(d,s.side).filter(m=>m.partId===id))for(const stroke of m.strokes)this.line(stroke.points,color,stroke.width+.05,[],.06);}
     else {const poly=G.rect(-p.body.w/2,-p.body.h/2,p.body.w,p.body.h).map(a=>C.world(p,a));this.line([...poly,poly[0]],color,.2,[4,3]);for(const pad of C.pads(d).filter(a=>a.partId===id))this.polygon(G.padPoly(pad),null,color,1.5);}
    }
   }
  }else if(plan.point){const p=this.project(plan.point);c.save();c.strokeStyle=color;c.lineWidth=2;c.beginPath();c.arc(p.x,p.y,9,0,Math.PI*2);c.moveTo(p.x-13,p.y);c.lineTo(p.x+13,p.y);c.moveTo(p.x,p.y-13);c.lineTo(p.x,p.y+13);c.stroke();c.restore();}
 };
})();

/* Dependency-free orthographic 3D renderer. Actual shaded, extruded component
   meshes are projected onto the editing canvas. All picking uses the board plane. */
(function(root){'use strict';const C=root.CB,G=C.G;
const shade=(hex,f)=>{let h=hex.replace('#','');if(h.length===3)h=h.split('').map(c=>c+c).join('');let n=parseInt(h,16),r=C.clamp((n>>16)*f,0,255),g=C.clamp(((n>>8)&255)*f,0,255),b=C.clamp((n&255)*f,0,255);return`rgb(${r|0},${g|0},${b|0})`;};
class Renderer{
 constructor(canvas,state){this.canvas=canvas;this.ctx=canvas.getContext('2d',{alpha:true});this.getState=state;this.w=0;this.h=0;this.scale=8;this.panX=0;this.panY=0;this.queue=[];this.pending=false;}
 resize(){const r=this.canvas.getBoundingClientRect(),dpr=Math.min(root.devicePixelRatio||1,2);if(this.w!==r.width||this.h!==r.height||this.dpr!==dpr){this.w=r.width;this.h=r.height;this.dpr=dpr;this.canvas.width=Math.round(r.width*dpr);this.canvas.height=Math.round(r.height*dpr);}this.ctx.setTransform(dpr,0,0,dpr,0,0);}
 setup(){const s=this.getState();this.doc=s.doc;this.state=s;this.tilt=(s.view==='bench'?s.tilt:0)*Math.PI/180;this.yaw=(s.view==='bench'?s.yaw||0:0)*Math.PI/180;this.flip=s.side==='bottom'?-1:1;this.cx=this.w/2+this.panX+20;this.cy=this.h/2+this.panY+14;this.outline=G.outline(this.doc);}
 fit(){this.resize();this.setup();let d=this.doc,angle=this.tilt;this.scale=Math.max(.3,Math.min((this.w-120)/d.board.width,(this.h-175)/(d.board.height*Math.cos(angle)+7*Math.sin(angle))));this.panX=0;this.panY=0;this.draw();}
 project(p,z=0){const d=this.doc,x=(p.x-d.board.width/2)*this.flip,y=p.y-d.board.height/2,u=x*Math.cos(this.yaw)-y*Math.sin(this.yaw),v=x*Math.sin(this.yaw)+y*Math.cos(this.yaw);return{x:this.cx+u*this.scale,y:this.cy+(v*Math.cos(this.tilt)-z*Math.sin(this.tilt))*this.scale,depth:v*Math.sin(this.tilt)+z*Math.cos(this.tilt)};}
 unproject(x,y){this.setup();let u=(x-this.cx)/this.scale,v=(y-this.cy)/(this.scale*Math.cos(this.tilt)),a=u*Math.cos(this.yaw)+v*Math.sin(this.yaw),b=-u*Math.sin(this.yaw)+v*Math.cos(this.yaw);return{x:a*this.flip+this.doc.board.width/2,y:b+this.doc.board.height/2};}
 panBy(dx,dy){if(!Number.isFinite(dx)||!Number.isFinite(dy))return;this.panX+=dx;this.panY+=dy;this.request();}
 zoom(f,x=this.w/2,y=this.h/2){let old=this.unproject(x,y);this.scale=C.clamp(this.scale*f,.25,130);this.setup();let now=this.project(old);this.panX+=x-now.x;this.panY+=y-now.y;this.draw();}
 path(points,close=true,z=0,ctx=this.ctx){ctx.beginPath();points.forEach((p,i)=>{let q=this.project(p,p.z??z);if(!i)ctx.moveTo(q.x,q.y);else ctx.lineTo(q.x,q.y);});if(close)ctx.closePath();}
 polygon(points,fill,stroke=null,width=1,z=0,ctx=this.ctx){if(!points.length)return;this.path(points,true,z,ctx);if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=width;ctx.stroke();}}
 line(points,color,width=.2,dash=[],z=.02,ctx=this.ctx){if(points.length<2)return;this.path(points,false,z,ctx);ctx.strokeStyle=color;ctx.lineWidth=Math.max(.5,width*this.scale);ctx.lineCap='round';ctx.lineJoin='round';ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([]);}
 fillRects(rects,color){const c=this.ctx;c.beginPath();for(const r of rects){const points=G.rect(r.x,r.y,r.w,r.h);points.forEach((p,i)=>{const q=this.project(p);if(i)c.lineTo(q.x,q.y);else c.moveTo(q.x,q.y);});c.closePath();}c.fillStyle=color;c.fill();}
 request(){if(this.pending)return;this.pending=true;requestAnimationFrame(()=>{this.pending=false;this.draw();});}
 draw(){this.resize();if(!this.w||!this.h)return;this.setup();const c=this.ctx,s=this.state,d=this.doc;c.clearRect(0,0,this.w,this.h);c.globalAlpha=1;this.queue=[];this.polarityHitLabels=[];
  if(s.view==='fabrication'){this.fabrication();this.overlays();return;}
  const theme=document.documentElement.dataset.theme,bench=s.view==='bench',colors=d.board.color==='purple'?['#61477b','#453257']:d.board.color==='blue'?['#29587d','#203e58']:['#39775b','#20533e'];
  // Cast board shadow onto the mat, followed by the actual substrate side walls.
  c.save();c.shadowColor=theme==='dark'?'#000a':'#1c3d3548';c.shadowBlur=30;c.shadowOffsetX=8;c.shadowOffsetY=18;this.polygon(this.outline,colors[1],null,0,-d.board.thickness);c.restore();
  for(let i=0;i<this.outline.length;i++){let a=this.outline[i],b=this.outline[(i+1)%this.outline.length];this.polygon([{...a,z:0},{...b,z:0},{...b,z:-d.board.thickness},{...a,z:-d.board.thickness}],i%2?'#b6a273':'#bbaa7c');}
  const gr=c.createLinearGradient(0,0,this.w,this.h);gr.addColorStop(0,bench?colors[0]:'#153e33');gr.addColorStop(1,bench?colors[1]:'#102e29');this.polygon(this.outline,gr,bench?'#5c957a':'#2c5e4b',1);
  c.save();this.path(this.outline);c.clip();
  if(s.grid){let grid=d.settings.grid;while(grid*this.scale<9)grid*=2;c.fillStyle=bench?'#c7ddbf24':'#b4d4c529';for(let x=Math.ceil(0/grid)*grid;x<=d.board.width;x+=grid)for(let y=0;y<=d.board.height;y+=grid){let p=this.project({x,y},.005);c.fillRect(p.x-.55,p.y-.55,1.1,1.1);}}
  const active=s.side,inactive=active==='top'?'bottom':'top',topColor=bench?'#79a772':'#f4a366',botColor=bench?'#689699':'#65bcd0',cuColor=l=>l==='top'?topColor:botColor;
  if(!bench||s.xray){c.globalAlpha=bench?.17:.34;for(const z of d.zones.filter(z=>z.layer===inactive&&s.showPlanes!==false))this.fillRects(z.fill?.rects||[],cuColor(z.layer));for(const t of d.traces.filter(t=>t.layer===inactive))this.line(t.points,cuColor(t.layer),t.width);c.globalAlpha=1;}
  for(const z of d.zones.filter(z=>z.layer===active&&s.showPlanes!==false)){c.globalAlpha=bench?.62:.7;this.fillRects(z.fill?.rects||[],cuColor(z.layer));c.globalAlpha=1;if(!z.fill)this.line([...z.points,z.points[0]],'#deb071',.12,[5,5]);}
  for(const t of d.traces.filter(t=>t.layer===active)){let highlight=t.net&&t.net===s.highlightNet;this.line(t.points,highlight?'#fff1a4':cuColor(t.layer),t.width);if(bench&&this.scale>6)this.line(t.points,highlight?'#fff7dc':'#bad2a735',Math.max(.05,t.width*.2));}
  const silks=C.silkStrokes(d).filter(a=>a.layer===active),images=C.silkRects(d).filter(a=>a.layer===active);for(const a of silks)this.line(a.points,bench?'#e5eccb':'#d8e7dc',a.width);for(const a of images)this.polygon(a.poly,'#e5eccb');
  for(const p of C.pads(d).filter(p=>G.layerMatch(p.layers,active))){let grad=c.createLinearGradient(this.project(p).x-4,this.project(p).y-4,this.project(p).x+8,this.project(p).y+8);grad.addColorStop(0,'#f7daa0');grad.addColorStop(.45,'#d8b264');grad.addColorStop(1,'#a97b36');this.polygon(G.padPoly(p,d.profile.maskExpansion+.06),bench?colors[1]:'#102e29');this.polygon(G.padPoly(p),grad,'#eed393',.55);if(s.selectedPads?.includes(p.id)||s.hoverPad===p.id||s.highlightNet&&s.highlightNet===p.net)this.polygon(G.padPoly(p,.18),null,'#fff2b7',1.7);}
  for(const v of d.vias){this.polygon(G.circle(v.x,v.y,v.diameter/2,24),v.tented&&bench?colors[1]:'#d7b774');this.polygon(G.circle(v.x,v.y,v.drill/2,24),'#10261d');}
  for(const h of G.holes(d)){let[a,b]=G.holeEndpoints(h);this.line([a,b],h.plated?'#0a211b':'#11251d',h.drill);if(!h.slot)this.polygon(G.circle(h.x,h.y,h.drill/2,32),'#10241b','#819275',.5);}
  for(const cut of d.cutouts)this.polygon(cut.points,theme==='dark'?'#17291f':'#e3e9df','#a49775',1);
  for(const k of d.keepouts){c.globalAlpha=.18;this.polygon(k.points,'#e86762');c.globalAlpha=.8;this.line([...k.points,k.points[0]],'#ed9a80',.16,[4,4]);c.globalAlpha=1;}
  c.restore();
  if(s.airwires&&s.connectivity){for(const a of s.connectivity.air){let high=s.highlightNet===a.net;this.line([a.a,a.b],high?'#ffdfa0':bench?'#c9d2a5ae':'#a0af86',high?.12:.08,[3,5],.07);}}
  if(bench){for(const p of d.parts.filter(p=>p.side===active||p.platform))this.component(p,s.xray||['trace','connect','via','plane-connect'].includes(s.tool)?.25:1);this.flush();}else this.partOutlines();
  this.carrierClearances();this.platformLabels();this.functionalLabels();this.polarityLabels();this.overlays();
 }
 // Screen-space bounds include the projected height of the component. Keeping
 // tags outside only the footprint is insufficient when the camera is tilted.
 polarityBodyBounds(){
  const s=this.state,bench=s.view==='bench',out=[];
  for(const p of this.doc.parts){
   if(p.side!==s.side&&!p.platform)continue;
   const pts=G.rect(-p.body.w/2,-p.body.h/2,p.body.w,p.body.h);
   const projected=pts.flatMap(a=>[this.project(C.world(p,a),0),this.project(C.world(p,a),bench?p.body.z+.3:0)]);
   out.push({...G.bounds(projected),owner:p.id});
  }
  return out;
 }
 polarityLabels(){
  const c=this.ctx,s=this.state;this.polarityHitLabels=[];
  const bodies=this.polarityBodyBounds(),padBoxes=C.pads(this.doc).filter(p=>G.layerMatch(p.layers,s.side)).map(p=>G.bounds(G.padPoly(p).map(a=>this.project(a,.07)))),occupied=[];
  const blocked=(x,y,w,h)=>{const box={minX:x-w/2-3,maxX:x+w/2+3,minY:y-h/2-3,maxY:y+h/2+3};return bodies.some(b=>G.boxOverlap(box,b))||padBoxes.some(b=>G.boxOverlap(box,b))||occupied.some(b=>G.boxOverlap(box,b));};
  const routing=['trace','connect','via','plane-connect'].includes(s.tool);
  for(const p of this.doc.parts){
   if(p.side!==s.side&&!p.pads.some(a=>a.drill))continue;
   const active=routing||s.selection?.includes(p.id)||s.hoverPad?.startsWith(p.id+':')||s.selectedPads?.some(id=>id.startsWith(p.id+':'));
   // Idle view contains the real small silkscreen only, not a second label layer.
   // Its visible, unobscured glyphs remain hoverable/clickable as pin targets.
   if(!active){
    if(p.side!==s.side)continue;
    for(const m of C.polarityMarks(p).filter(m=>m.visible)){
     const q=this.project(m.center,.07),w=Math.max(8,m.size*this.scale*.67+3),h=Math.max(10,m.size*this.scale*Math.cos(this.tilt)+3);
     if(!blocked(q.x,q.y,w,h))this.polarityHitLabels.push({padId:m.padId,role:m.role,label:m.label,text:m.short,x:q.x,y:q.y,w,h,mode:'silk'});
    }
    continue;
   }
   // Do not let a custom print size/offset turn editor tags into billboards.
   const marks=C.polarityMarks({...p,polaritySilk:C.POLARITY_DEFAULTS});
   const anchors=marks.map(m=>this.project(m.center,.07));
   // Fan a multi-terminal row along its tangent instead of stacking badges
   // farther and farther away from a small RGB LED when zoomed out.
   if(anchors.length>2){
    let a=anchors[0],b=anchors.reduce((best,q)=>G.dist(q,a)>G.dist(best,a)?q:best,a),len=G.dist(a,b);
    if(len>.001){
     const ux=(b.x-a.x)/len,uy=(b.y-a.y)/len;
     if(anchors.every(q=>Math.abs((q.x-a.x)*uy-(q.y-a.y)*ux)<.1)){
      const cx=anchors.reduce((v,q)=>v+q.x,0)/anchors.length,cy=anchors.reduce((v,q)=>v+q.y,0)/anchors.length,sorted=anchors.map((q,i)=>({q,i,t:q.x*ux+q.y*uy})).sort((a,b)=>a.t-b.t),step=Math.max(19,(sorted.at(-1).t-sorted[0].t)/(sorted.length-1));
      sorted.forEach(({i},j)=>{const t=(j-(sorted.length-1)/2)*step;anchors[i]={x:cx+ux*t,y:cy+uy*t};});
     }
    }
   }
   for(const [markIndex,m] of marks.entries()){
    const q=anchors[markIndex],pin=this.project(m.pad,.07),w=14,h=14;
    let dx=q.x-pin.x,dy=q.y-pin.y,len=Math.hypot(dx,dy)||1;dx/=len;dy/=len;
    const own=bodies.find(b=>b.owner===p.id);let distance=Math.max(len,12);
    if(own){
     const exits=[];
     if(Math.abs(dx)>.0001)exits.push(((dx>0?own.maxX+w/2+4:own.minX-w/2-4)-pin.x)/dx);
     if(Math.abs(dy)>.0001)exits.push(((dy>0?own.maxY+h/2+4:own.minY-h/2-4)-pin.y)/dy);
     const positive=exits.filter(v=>v>=0);if(positive.length)distance=Math.max(distance,Math.min(...positive));
    }
    let target=null;
    for(let extra=0;extra<=42&&!target;extra+=14){
     const x=pin.x+dx*(distance+extra),y=pin.y+dy*(distance+extra);
     if(x<9||y<9||x>this.w-9||y>this.h-9||blocked(x,y,w,h))continue;
     target={x,y};
    }
    // A crowded/zoomed-out board must not get labels painted over components.
    // Pads and the inspector remain available if a safe tag cannot be placed.
    if(!target)continue;
    const {x,y}=target;c.save();
    // Only a short outward stem is drawn: no line through a component body.
    const stem=Math.min(7,Math.max(0,Math.hypot(x-pin.x,y-pin.y)-w/2));
    c.strokeStyle='#e4eed5';c.lineWidth=.8;c.beginPath();c.moveTo(x-dx*(w/2+stem),y-dy*(h/2+stem));c.lineTo(x-dx*w/2,y-dy*h/2);c.stroke();
    c.fillStyle='#183c30e8';c.strokeStyle='#c6d9bca6';c.lineWidth=.6;c.beginPath();c.roundRect(x-6,y-6.5,12,13,3);c.fill();c.stroke();
    c.font='600 9px system-ui,sans-serif';c.fillStyle='#fffbe4';c.textAlign='center';c.textBaseline='middle';c.fillText(m.short,x,y);
    occupied.push({minX:x-w/2,maxX:x+w/2,minY:y-h/2,maxY:y+h/2});
    this.polarityHitLabels.push({padId:m.padId,role:m.role,label:m.label,text:m.short,x,y,w,h,fontSize:9,mode:'tag'});c.restore();
   }
  }
 }
 partOutlines(){let c=this.ctx;for(const p of this.doc.parts){c.globalAlpha=p.side===this.state.side?.75:.2;let poly=G.rect(-p.body.w/2,-p.body.h/2,p.body.w,p.body.h).map(a=>C.world(p,a));this.line([...poly,poly[0]],'#a6caba',.09,[3,3]);let q=this.project(p);c.font='10px system-ui';c.fillStyle='#d5dfbd';c.textAlign='center';c.fillText(p.ref,q.x,q.y-4);c.globalAlpha=1;}if(this.scale>9)for(const p of C.pads(this.doc).filter(p=>G.layerMatch(p.layers,this.state.side))){let q=this.project(p);c.font=Math.min(12,this.scale*.7)+'px system-ui';c.textAlign='center';c.fillStyle='#173c2e';if(!p.drill)c.fillText(p.pin,q.x,q.y+3);}}
 face(vertices,color,alpha=1){const depth=vertices.reduce((s,p)=>s+this.project(p,p.z||0).depth,0)/vertices.length;this.queue.push({vertices,color,alpha,depth});}
 local(p,a,z){return{...C.world(p,a),z};}
 extrude(p,poly,z0,z1,color,alpha=1){let bottom=poly.map(a=>this.local(p,a,z0)),top=poly.map(a=>this.local(p,a,z1));for(let i=0;i<poly.length;i++){let j=(i+1)%poly.length,dx=poly[j].x-poly[i].x,dy=poly[j].y-poly[i].y,l=Math.hypot(dx,dy)||1,f=.65+.22*(dy-dx)/l;this.face([bottom[i],bottom[j],top[j],top[i]],shade(color,f),alpha);}this.face(top,shade(color,1.08),alpha);}
 box(p,x,y,w,h,z0,z1,color,alpha=1){this.extrude(p,G.rect(x,y,w,h),z0,z1,color,alpha);}
 cylinder(p,x,y,r,z0,z1,color,alpha=1,n=24){this.extrude(p,G.circle(x,y,r,n),z0,z1,color,alpha);}
 axial(p,x0,x1,r,z,color,alpha=1){let n=20,ring=x=>Array.from({length:n},(_,i)=>this.local(p,{x,y:Math.cos(i/n*Math.PI*2)*r},z+Math.sin(i/n*Math.PI*2)*r));let a=ring(x0),b=ring(x1);for(let i=0;i<n;i++){let j=(i+1)%n;this.face([a[i],b[i],b[j],a[j]],shade(color,.67+.34*Math.sin((i+.5)/n*Math.PI*2)),alpha);}this.face(a,shade(color,.7),alpha);this.face(b,shade(color,.85),alpha);}
 surfaceLine(p,a,b,z,width,color,alpha=1){let va=this.local(p,a,z),vb=this.local(p,b,z);this.queue.push({line:[va,vb],color,alpha,width,depth:(this.project(va,z).depth+this.project(vb,z).depth)/2+.001});}
 text(p,text,x,y,z,size,color,alpha=1){let pos=this.local(p,{x,y},z);this.queue.push({text,p,x,y,z,size,color,alpha,depth:this.project(pos,z).depth+.01});}
 platformComponent(p,alpha=1){
  const f=C.Platforms?.families.find(a=>a.id===p.platform.family),w=p.body.w,h=p.body.h;
  const sign=p.platform.role==='addon'?-1:1,ref=(x,y)=>({x:(x-w/2)*sign,y:y-h/2});
  if(p.platform.showHost){
   this.extrude(p,p.platform.outline,-.28,-.07,f?.color||'#39775b',alpha*.22);
   for(let i=0;i<p.platform.outline.length;i++)this.surfaceLine(p,p.platform.outline[i],p.platform.outline[(i+1)%p.platform.outline.length],.08,.2,'#b7d3c0',alpha*.8);
   const rb=(x,y,bw,bh,color)=>{const a=ref(x,y);this.box(p,a.x-(sign<0?bw:0),a.y,bw,bh,.1,.75,color,alpha*.24);};
   if(p.carrier){const edge=p.carrier.usbEdge;if(edge==='top')rb(w/2-4,-1,8,6,'#bfcac8');else if(edge==='bottom')rb(w/2-4,h-5,8,6,'#bfcac8');else rb(-1,h/2-4,6,8,'#bfcac8');rb(w*.32,h*.34,w*.36,h*.24,'#202e2a');if(p.carrier.wireless==='pcb'){const rr=p.carrier.regions.find(r=>r.kind==='antenna');if(rr)for(let i=0;i<4;i++)this.surfaceLine(p,{x:rr.x+1,y:rr.y+rr.h-2-i},{x:rr.x+rr.w-1,y:rr.y+rr.h-2-i},.2,.22,'#d7b574',alpha*.5);}const name=f?.short||'CONTROLLER';this.text(p,name,-w*.35,0,.9,Math.min(1.2,w/Math.max(10,name.length)), '#e4efcf',alpha*.85);}
   else if(p.platform.family==='pi40'){rb(22,18,13,13,'#263c31');rb(46,19,12,15,'#a8b6b1');rb(43,38,15,10,'#a8b6b1');rb(6,39,8,7,'#a8b6b1');}
   else {rb(0,h/2-4,7,8,'#bfcac8');rb(w*.35,h*.38,w*.22,h*.25,'#2b3836');if(p.platform.family==='mkr')rb(w-14,6,11,12,'#aebcba');else rb(0,h-15,9,8,'#303c3b');}
  }
  const groups={};for(const a of p.pads)(groups[a.bank||'HEADER']??=[]).push(a);
  const face=p.side===this.state.side,top=face?2.2:.5;
  for(const pads of Object.values(groups)){const b=G.bounds(pads);this.box(p,b.minX-1.1,b.minY-1.1,b.maxX-b.minX+2.2,b.maxY-b.minY+2.2,.05,top,'#283a34',alpha);}
  for(const a of p.pads){this.box(p,a.x-.53,a.y-.53,1.06,1.06,top,top+.09,a.shape==='rect'?'#f7d580':'#c5ab65',alpha);if(face)this.box(p,a.x-.26,a.y-.26,.52,.52,top+.10,top+.12,'#10261e',alpha);}
 }
 platformLabels(){
  if(this.scale<5||this.state.view==='fabrication')return;
  const c=this.ctx;c.save();c.font='9px ui-monospace,monospace';c.textAlign='center';c.fillStyle='#f3edce';
  for(const p of this.doc.parts.filter(p=>p.platform?.showPins))for(const a of p.pads){
   if(p.carrier?.vertical){const name=(a.signal||a.number).split(' / ')[0].replace('GPIO','G').replace('3V3_OUT','3V3').replace('3V3_EN','3EN');const local={x:a.x+(a.x<0?2.3:-2.3),y:a.y},v=this.project(C.world(p,local),.05),pin=this.project(C.world(p,a),.05);c.textAlign=v.x>pin.x?'left':'right';if(name.length<9||this.scale>8)c.fillText(name,v.x,v.y+3);c.textAlign='center';continue;}
   const n=p.platform.family==='pi40'?a.number:(a.signal||a.number).split(' / ')[0];
   const q=C.world(p,a),insideY=a.y<0?a.y+2.6:a.y-2.6;
   // Pi has two tightly-spaced rows: captions sit on opposite sides of the header.
   const y=p.platform.family==='pi40'?a.y+(Number(a.number)%2?2.4:-2.4):insideY;
   const v=this.project(C.world(p,{x:a.x,y}),.05);
   if(n.length>6&&this.scale<8)continue;c.fillText(n,v.x,v.y+3);
  }c.restore();
 }

 carrierClearances(){
  if(!C.Carriers||this.state.view==='fabrication')return;const c=this.ctx;
  for(const p of this.doc.parts.filter(p=>p.carrier?.showClearances))for(const r of C.Carriers.regions(p)){
   const col=r.enforced?'#ffbd9c':'#e4c789';c.save();c.globalAlpha=.07;this.polygon(r.points,col);c.globalAlpha=.9;this.line([...r.points,r.points[0]],col,.12,[5,4],.1);
   const q=this.project(r.points[0],.12);c.font='600 10px system-ui';c.fillStyle=col;c.textAlign='left';c.fillText(r.kind==='antenna'?(r.enforced?'RF · copper guard':'RF · guard disabled'):r.name,q.x+3,q.y-5);c.restore();
  }
 }

 makerComponent(p,alpha=1){
  const {kind:k,w,h,z}=p.body,box=(x,y,bw,bh,a,b,color)=>this.box(p,x,y,bw,bh,a,b,color,alpha),cyl=(x,y,r,a,b,color)=>this.cylinder(p,x,y,r,a,b,color,alpha),line=(a,b,zz,ww,color)=>this.surfaceLine(p,a,b,zz,ww,color,alpha);
  const label=(txt,zz=z+.08,size=Math.min(1.1,w/8))=>this.text(p,txt,-w*.35,0,zz,size,'#e9eadb',alpha);
  if(['socket','shrouded','rightangle','jst'].includes(k)){
   const white=k==='jst',col=white?'#e5e0cb':'#2c3734';box(-w/2,-h/2,w,h,.1,k==='rightangle'?2.5:z,col);
   if(k==='jst'||k==='shrouded'){box(-w/2+.5,-h/2+.5,w-1,h-1,z,z+.05,white?'#6f7d74':'#121d18');box(-w/2,-h/2,w,.55,z,z+.6,col);box(-w/2,-h/2,.55,h,z,z+.6,col);box(w/2-.55,-h/2,.55,h,z,z+.6,col);box(-w/2,h/2-.55,Math.max(.4,w*.34),.55,z,z+.6,col);box(w*.16,h/2-.55,Math.max(.4,w*.34),.55,z,z+.6,col);}
   for(const a of p.pads.filter(a=>!String(a.number).startsWith('MP'))){if(k==='rightangle'){line({x:a.x,y:a.y},{x:a.x,y:h/2+1},3,.62,'#cfb467');}else{box(a.x-.43,a.y-.43,.86,.86,z+.1,z+.16,k==='socket'?'#bba05a':'#cbb368');if(k==='socket')box(a.x-.25,a.y-.25,.5,.5,z+.17,z+.18,'#07100e');}}
   const a=p.pads[0];if(a)this.text(p,'1',a.x-.35,a.y-.85,z+.8,.8,white?'#394b3c':'#f1d997',alpha);return true;
  }
  if(k==='usb'){box(-w/2,-h/2,w,h,.1,z,'#bfc9c9');box(-w/2+.4,h/2-.08,w-.8,.10,.55,z-.35,'#253132');box(-w*.3,h/2-.15,w*.6,.11,1.25,1.65,'#b8b6a1');line({x:-w*.3,y:0},{x:w*.3,y:0},z+.06,.15,'#7e908c');return true;}
  if(k==='barrel'){box(-w/2,-h/2,w,h,.3,z,'#253b35');box(-w/2+.7,h/2-.05,w-1.4,.1,1,z-1,'#080f0c');box(-.5,h/2-.08,1,.15,3,7,'#bea66a');return true;}
  if(k==='dipswitch'){box(-w/2,-h/2,w,h,.3,z,'#a9433c');for(let i=0;i<p.pads.length/2;i++){const x=(i-(p.pads.length/2-1)/2)*2.54;box(x-.8,-h*.33,1.6,h*.66,z,z+.04,'#482a28');box(x-.62,-h*.24,1.24,h*.3,z+.06,z+.5,'#e9e3d1');this.text(p,String(i+1),x-.3,h*.36,z+.08,.7,'#fff5e0',alpha);}return true;}
  if(k==='slide'){box(-w/2,-h/2,w,h,.2,z*.5,'#aebcba');box(-w*.3,-h*.25,w*.6,h*.5,z*.5,z*.51,'#1e2b25');box(-w*.22,-h*.2,w*.22,h*.4,z*.51,z,'#26332b');return true;}
  if(['trimmer','pot','encoder'].includes(k)){box(-w/2,-h/2,w,h,.2,k==='trimmer'?z-1:6,k==='trimmer'?'#336d95':'#aabbb6');cyl(0,0,k==='trimmer'?w*.3:3,k==='trimmer'?z-1:6,z,k==='trimmer'?'#c8b170':'#d1d3c6');line({x:-w*.22,y:0},{x:w*.22,y:0},z+.06,.35,'#526159');return true;}
  if(k==='to220'){box(-w/2,-h/2,w,h,.8,z*.62,'#303b34');box(-w/2+.4,-.7,w-.8,1.4,z*.62,z,'#afbcb5');box(-1,-.73,2,1.5,z-4,z-2,'#233b32');label(p.value,z*.62+.1,.85);return true;}
  if(k==='sot223'){box(-w/2,-h/2,w,h,.3,z,'#293b31');label('1117');return true;}
  if(k==='relay'){box(-w/2,-h/2,w,h,.4,z,'#336ea0');label('SPDT',z+.07,1.6);return true;}
  if(k==='fuse'){box(-w/2,-h/2,w,h,.3,2.2,'#283c2e');this.axial(p,-10,10,2.5,5.5,'#9ebbb0',alpha);for(const x of [-11.5,8]){this.axial(p,x,x+3.5,2.7,5.5,'#c9d2c9',alpha);box(x,-3,3.5,6,2,5,'#b9c7c0');}return true;}
  if(k==='loop'){const xs=p.pads.map(a=>a.x),a={x:Math.min(...xs),y:0},b={x:Math.max(...xs),y:0};line(a,b,z,.8,'#d2b368');for(const v of [a,b]){const q0=this.local(p,v,.4),q1=this.local(p,v,z);this.queue.push({line:[q0,q1],color:'#c8b169',alpha,width:.8,depth:this.project(q1,z).depth});}return true;}
  if(k==='jumper'){return true;}
  if(k==='smd-diode'){box(-w/2,-h/2,w,h,.15,z,'#354238');box(-w*.4,-h/2,.35,h,z,z+.04,'#ddd4ac');return true;}
  if(k==='smdled'||k==='rgbled'){box(-w/2,-h/2,w,h,.1,z,'#e1dfc7');cyl(0,0,Math.min(w,h)*.32,z,z+.05,k==='smdled'?'#e2bf64':'#aaa887');if(k==='rgbled'){for(const [x,y,col]of[[-.4,-.3,'#bd5746'],[.4,-.3,'#53856b'],[0,.4,'#526fa0']])box(x-.18,y-.18,.36,.36,z+.08,z+.14,col);label('>',z+.15,.9);}return true;}
  return false;
 }
 functionalLabels(){
  const s=this.state,c=this.ctx;if(s.view==='fabrication'||this.scale<4)return;
  for(const p of this.doc.parts){if(p.platform||p.pinNamesVisible===false||!s.selection?.includes(p.id)||p.side!==s.side&&!p.pads.some(a=>a.drill))continue;
   const occupied=[];for(let i=0;i<p.pads.length;i++){const a=p.pads[i];if(!a.signal||C.polarityRole(p,a))continue;
    const pin=this.project(C.world(p,a),.08),edge={x:a.x,y:a.y};
    if(Math.abs(a.x)/Math.max(.1,p.body.w)>Math.abs(a.y)/Math.max(.1,p.body.h)){edge.x=Math.sign(a.x||1)*(p.body.w/2+2.2);}else{edge.y=Math.sign(a.y||1)*(p.body.h/2+2.2);}
    const q=this.project(C.world(p,edge),.08),text=a.number+' · '+a.signal;c.save();c.font='600 10px system-ui,sans-serif';const w=Math.min(210,c.measureText(text).width+10),h=17;
    let x=q.x,y=q.y;const right=q.x>=pin.x;x+=(right?1:-1)*w/2;
    for(let tries=0;tries<50&&occupied.some(b=>Math.abs(b.x-x)<(b.w+w)/2+2&&Math.abs(b.y-y)<h+2);tries++)y+=19;
    occupied.push({x,y,w});c.strokeStyle='#c9dcb8';c.lineWidth=.8;c.beginPath();c.moveTo(pin.x,pin.y);c.lineTo(x+(right?-1:1)*w/2,y);c.stroke();c.fillStyle='#162d24';c.fillRect(x-w/2,y-h/2,w,h);c.fillStyle='#f5efdb';c.textAlign='center';c.textBaseline='middle';c.fillText(text,x,y,w-8);c.restore();
   }
  }
 }
 component(p,alpha=1){if(p.platform&&p.body.kind==='platform'){this.platformComponent(p,alpha);return;}const b=p.body,w=b.w,h=b.h,z=b.z,kind=b.kind;let leads=p.pads;
  for(const a of leads){let v={x:a.x,y:a.y};if(kind==='header'||kind==='terminal')continue;let inner={x:C.clamp(a.x,-w/2,w/2),y:C.clamp(a.y,-h/2,h/2)},wi=Math.min(a.h,.65);this.surfaceLine(p,v,inner,.55,wi,'#bac6c7',alpha);this.surfaceLine(p,{x:v.x,y:v.y+.06},{x:inner.x,y:inner.y+.06},.62,wi*.28,'#ffffff',alpha);}
  if(this.makerComponent(p,alpha))return;
  if(kind==='resistor'||kind==='diode'){this.axial(p,-w/2,w/2,h/2,1.6,kind==='resistor'?'#c2a173':'#c47f48',alpha);const bands=kind==='resistor'?['#754826','#372c27','#ac492e','#bd9a42']:['#24211e'];bands.forEach((c,i)=>{let x=kind==='resistor'?-w*.32+i*w*.19:((p.pads.find(a=>C.polarityRole(p,a)==='cathode')?.x??-1)<0?-w*.36:w*.36-.4);this.axial(p,x,x+.4,h/2+.015,1.6,c,alpha);});for(const a of leads)this.surfaceLine(p,{x:a.x,y:a.y},{x:Math.sign(a.x)*w/2,y:0},1.55,.38,'#d5dcda',alpha);}
  else if(kind==='led'){this.cylinder(p,0,0,w/2+.2,.25,1,'#dba242',alpha);let rings=[[1,w/2],[z*.7,w/2],[z*.88,w*.39],[z*.98,w*.2],[z,0]],n=24;for(let r=0;r<rings.length-1;r++){let [za,ra]=rings[r],[zb,rb]=rings[r+1];for(let i=0;i<n;i++){let a=i/n*Math.PI*2,b=(i+1)/n*Math.PI*2;this.face([this.local(p,{x:Math.cos(a)*ra,y:Math.sin(a)*ra},za),this.local(p,{x:Math.cos(b)*ra,y:Math.sin(b)*ra},za),this.local(p,{x:Math.cos(b)*rb,y:Math.sin(b)*rb},zb),this.local(p,{x:Math.cos(a)*rb,y:Math.sin(a)*rb},zb)],shade(p.appearance||'#ec733a',.75+.38*Math.cos(a-.6)),alpha);}}this.surfaceLine(p,{x:-.9,y:-.4},{x:-.9,y:.4},z*.91,.3,'#fff2c5',alpha);}
  else if(kind==='capacitor'){this.cylinder(p,0,0,w/2,.35,z,'#274b62',alpha,32);this.cylinder(p,0,0,w*.455,z,z+.09,'#b9c5c8',alpha,32);this.surfaceLine(p,{x:-w*.26,y:0},{x:w*.26,y:0},z+.12,.10,'#697b80',alpha);this.surfaceLine(p,{x:0,y:-w*.26},{x:0,y:w*.26},z+.12,.10,'#697b80',alpha);const negative=p.pads.find(a=>C.polarityRole(p,a)==='negative'),stripe=(negative?.x??1)<0?-w*.31-.5:w*.31;this.box(p,stripe,-.4,.5,.8,.9,z-.25,'#bfd0cb',alpha);}
  else if(kind==='disc'){let poly=G.circle(0,0,w/2,28),front=poly.map(a=>this.local(p,{x:a.x,y:-.7},z/2+a.y)),back=poly.map(a=>this.local(p,{x:a.x,y:.7},z/2+a.y));this.face(front,'#b76835',alpha);this.face(back,'#dba166',alpha);for(let i=0;i<poly.length;i++)this.face([front[i],back[i],back[(i+1)%poly.length],front[(i+1)%poly.length]],'#c4884c',alpha);}
  else if(kind==='header'){this.box(p,-w/2,-h/2,w,h,.1,2.25,'#252e2a',alpha);for(const a of leads){this.box(p,a.x-.32,a.y-.32,.64,.64,2.25,z,'#d0b665',alpha);}}
  else if(kind==='terminal'){this.box(p,-w/2,-h/2,w,h,.25,z,'#347b69',alpha);for(const a of leads){this.cylinder(p,a.x,0,1.55,z,z+.06,'#bdc8bf',alpha);this.surfaceLine(p,{x:a.x-1,y:-.45},{x:a.x+1,y:.45},z+.08,.3,'#455451',alpha);this.box(p,a.x-1.35,-h/2-.025,2.7,.04,1.2,4.4,'#192e28',alpha);}}
  else if(kind==='switch'){this.box(p,-w/2,-h/2,w,h,.4,2.1,'#a4ada7',alpha);this.box(p,-w/2+.4,-h/2+.4,w-.8,h-.8,2.1,2.5,'#d1d6ce',alpha);this.cylinder(p,0,0,1.75,2.5,z,'#303b31',alpha);}
  else if(kind==='testpoint'){this.cylinder(p,0,0,w/2,.1,z,'#d2b359',alpha);}
  else if(kind==='smd-resistor'||kind==='smd-cap'){this.box(p,-w/2,-h/2,w,h,.1,z,kind==='smd-cap'?'#b89966':'#303735',alpha);this.box(p,-w/2,-h/2,w*.18,h,.1,z+.025,'#c2cdcb',alpha);this.box(p,w*.32,-h/2,w*.18,h,.1,z+.025,'#c2cdcb',alpha);if(kind==='smd-resistor')this.text(p,'102',-w*.24,0,z+.04,.48,'#eceddd',alpha);}
  else {this.extrude(p,G.roundRect(-w/2,-h/2,w,h,Math.min(.35,w/8)),.55,z,kind==='transistor'?'#303631':'#303d36',alpha);this.cylinder(p,-w*.27,-h*.34,Math.min(.42,w*.12),z,z+.04,'#66746a',alpha);this.text(p,p.value,-w*.30,0,z+.05,Math.min(1.1,w/(Math.max(p.value.length,1)*.56)),'#aab6a7',alpha);}
 }
 flush(){
  // Per-pixel depth testing prevents a large package face from painting over its
  // own screws, markings or leads. No WebGL, downloaded models or GPU are required.
  const c=this.ctx, projected=[],texts=[];
  for(const f of this.queue){if(f.text){texts.push(f);continue;}let ps=(f.vertices||f.line).map(p=>this.project(p,p.z||0));projected.push({...f,ps});}
  if(projected.length){let all=projected.flatMap(f=>f.ps),bb=G.bounds(all),x0=Math.max(0,Math.floor(bb.minX-4)),y0=Math.max(0,Math.floor(bb.minY-4)),x1=Math.min(this.w,Math.ceil(bb.maxX+4)),y1=Math.min(this.h,Math.ceil(bb.maxY+4)),aa=(x1-x0)*(y1-y0)<450000?2:1,W=Math.max(0,Math.ceil((x1-x0)*aa)),H=Math.max(0,Math.ceil((y1-y0)*aa));
   if(W&&H){let image=new ImageData(W,H),pixels=image.data,depth=new Float32Array(W*H);depth.fill(-Infinity);const rgb=color=>{if(color.startsWith('#')){let hex=color.slice(1);if(hex.length===3)hex=hex.split('').map(x=>x+x).join('');let n=parseInt(hex,16);return[n>>16&255,n>>8&255,n&255];}return(color.match(/[\d.]+/g)||[0,0,0]).slice(0,3).map(Number);};
    const write=(x,y,z,color,alpha)=>{let i=y*W+x;if(z<depth[i]-.0001)return;depth[i]=z;let k=i*4;pixels[k]=color[0];pixels[k+1]=color[1];pixels[k+2]=color[2];pixels[k+3]=Math.round(alpha*255);};
    for(const f of projected){let color=rgb(f.color),alpha=f.alpha??1,ps=f.ps.map(p=>({x:(p.x-x0)*aa,y:(p.y-y0)*aa,z:p.depth}));
     if(f.vertices){for(let i=1;i<ps.length-1;i++){let a=ps[0],b=ps[i],d=ps[i+1],den=(b.y-d.y)*(a.x-d.x)+(d.x-b.x)*(a.y-d.y);if(Math.abs(den)<1e-8)continue;let minX=Math.max(0,Math.floor(Math.min(a.x,b.x,d.x))),maxX=Math.min(W-1,Math.ceil(Math.max(a.x,b.x,d.x))),minY=Math.max(0,Math.floor(Math.min(a.y,b.y,d.y))),maxY=Math.min(H-1,Math.ceil(Math.max(a.y,b.y,d.y)));
      for(let y=minY;y<=maxY;y++)for(let x=minX;x<=maxX;x++){let px=x+.5,py=y+.5,u=((b.y-d.y)*(px-d.x)+(d.x-b.x)*(py-d.y))/den,v=((d.y-a.y)*(px-d.x)+(a.x-d.x)*(py-d.y))/den,w=1-u-v;if(u>=-1e-7&&v>=-1e-7&&w>=-1e-7)write(x,y,u*a.z+v*b.z+w*d.z,color,alpha);}
     }}else{let[a,b]=ps,r=Math.max(.6,f.width*this.scale*aa/2),dx=b.x-a.x,dy=b.y-a.y,len=dx*dx+dy*dy;for(let y=Math.max(0,Math.floor(Math.min(a.y,b.y)-r));y<=Math.min(H-1,Math.ceil(Math.max(a.y,b.y)+r));y++)for(let x=Math.max(0,Math.floor(Math.min(a.x,b.x)-r));x<=Math.min(W-1,Math.ceil(Math.max(a.x,b.x)+r));x++){let t=len?C.clamp(((x+.5-a.x)*dx+(y+.5-a.y)*dy)/len,0,1):0;if((x+.5-a.x-t*dx)**2+(y+.5-a.y-t*dy)**2<=r*r)write(x,y,a.z+(b.z-a.z)*t+.002,color,alpha);}}
    }
    if(!this.meshCanvas)this.meshCanvas=document.createElement('canvas');this.meshCanvas.width=W;this.meshCanvas.height=H;this.meshCanvas.getContext('2d').putImageData(image,0,0);c.drawImage(this.meshCanvas,x0,y0,W/aa,H/aa);
   }
  }
  for(const f of texts){let p=this.local(f.p,{x:f.x,y:f.y},f.z),a=this.project(p,f.z),px=this.project(this.local(f.p,{x:f.x+1,y:f.y},f.z),f.z),py=this.project(this.local(f.p,{x:f.x,y:f.y+1},f.z),f.z);c.save();c.globalAlpha=f.alpha??1;c.transform((px.x-a.x)/this.scale,(px.y-a.y)/this.scale,(py.x-a.x)/this.scale,(py.y-a.y)/this.scale,a.x,a.y);c.font=`${Math.max(3,f.size*this.scale)}px ui-monospace,monospace`;c.fillStyle=f.color;c.textAlign='left';c.fillText(f.text,0,0);c.restore();}
  c.globalAlpha=1;this.queue=[];this.polarityHitLabels=[];
 }
 overlays(){let c=this.ctx,s=this.state,d=this.doc;if(s.marquee){let b=G.bounds([s.marquee.a,s.marquee.b]),p=G.rect(b.minX,b.minY,b.maxX-b.minX,b.maxY-b.minY);c.save();c.globalAlpha=.15;this.polygon(p,'#f8df9b');c.restore();this.line([...p,p[0]],'#ffe6a5',.12,[4,4]);}
  for(const id of s.selection||[]){let p=d.parts.find(p=>p.id===id);if(p){let poly=G.rect(-p.body.w/2-.9,-p.body.h/2-.9,p.body.w+1.8,p.body.h+1.8).map(a=>C.world(p,a));this.line([...poly,poly[0]],'#f4cd7c',.15,[4,3],.1);for(const v of poly){let q=this.project(v);c.fillStyle='#f6deaa';c.fillRect(q.x-2,q.y-2,4,4);}}let t=d.traces.find(t=>t.id===id);if(t){this.line(t.points,'#fff2b3',t.width+.12,[],.03);for(const v of t.points){let q=this.project(v);c.beginPath();c.arc(q.x,q.y,3.5,0,Math.PI*2);c.fillStyle='#194b39';c.fill();c.strokeStyle='#ffdf8f';c.lineWidth=1.5;c.stroke();}}let a=d.art.find(a=>a.id===id);if(a){let ps=a.kind==='text'?C.textPaths(a.text,a.size).flat():a.kind==='image'?(a.rects||[]).flatMap(r=>G.rect(r.x,r.y,r.w,r.h)):a.points||G.rect(0,0,a.w||2,a.h||2),b=G.bounds(ps),poly=G.rect(b.minX-.5,b.minY-.5,b.maxX-b.minX+1,b.maxY-b.minY+1).map(v=>C.artPoint(a,v));this.line([...poly,poly[0]],'#f6df9b',.13,[4,3]);}let sh=[...d.zones,...d.keepouts,...d.cutouts].find(a=>a.id===id);if(sh){this.line([...sh.points,sh.points[0]],'#f5d492',.18,[4,4]);for(const v of sh.points){let q=this.project(v);c.fillStyle='#e5cc93';c.fillRect(q.x-2.5,q.y-2.5,5,5);}}let h=[...d.holes,...d.vias].find(a=>a.id===id);if(h)this.line([...G.circle(h.x,h.y,(h.diameter||h.drill)/2+.6,32),G.circle(h.x,h.y,(h.diameter||h.drill)/2+.6,32)[0]],'#f5d492',.16,[4,3]);}
  if(s.selection?.includes('board')){this.line([...this.outline,this.outline[0]],'#ffdaa0',.18,[6,4]);if(d.board.shape==='polygon')for(const v of d.board.points){let p=this.project(v);c.fillStyle='#ffe2a7';c.fillRect(p.x-3,p.y-3,6,6);}}
  for(const pid of s.selectedPads||[]){let p=C.getPad(d,pid);if(p)this.polygon(G.padPoly(p,.35),null,'#fff0a9',2);}
  if(s.drawing?.points?.length){let pts=[...s.drawing.points];if(s.cursor)pts.push(s.cursor);if(s.tool==='trace'){let path=s.tracePreview||pts;this.line(path,s.traceLegal===false?'#ff8378':'#ffe7a4',d.settings.traceWidth,[],.04);}else this.line(pts,'#f8d79b',.2,[5,4]);pts.forEach(p=>{let q=this.project(p);c.fillStyle='#fff4cb';c.fillRect(q.x-2,q.y-2,4,4);});}
  if((s.tool==='via'||s.viaPending)&&s.cursor){const v=s.viaPreview?.via||{...C.V.defaults(d),...s.cursor},ok=s.viaPreview?.ok,color=ok?'#9decbb':'#ff8a80';c.save();c.setLineDash([4,4]);this.polygon(G.circle(v.x,v.y,v.diameter/2+d.profile.clearance),null,color,1);c.setLineDash([]);c.globalAlpha=.7;this.polygon(G.circle(v.x,v.y,v.diameter/2),color);this.polygon(G.circle(v.x,v.y,v.drill/2),'#142e26');c.globalAlpha=1;const q=this.project(v);c.fillStyle=color;c.font='bold 11px system-ui';c.fillText(ok?'TOP ↔ BOTTOM':'BLOCKED',q.x+12,q.y-12);c.restore();}
  if(s.routePreview){for(const t of s.routePreview.traces)this.line(t.points,t.layer===s.side?'#ffe5a0':'#a5e9f6',t.width+.04,[7,3]);for(const v of s.routePreview.vias)this.polygon(G.circle(v.x,v.y,v.diameter/2),null,'#fff0b0',2);}
  if(s.placing&&s.cursor){let p=C.makePart(d,s.placing,s.cursor.x,s.cursor.y);p.rotation=s.placeRotation||0;p.side=p.defaultSide||s.side;this.component(p,.55);this.flush();}
  if(s.measure?.a&&s.cursor){this.line([s.measure.a,s.cursor],'#ffe5a0',.1,[5,5]);let a=this.project(s.cursor);c.fillStyle='#1f503a';c.fillRect(a.x+8,a.y-23,85,22);c.font='11px system-ui';c.fillStyle='#fff';c.fillText(G.dist(s.measure.a,s.cursor).toFixed(3)+' mm',a.x+14,a.y-8);}
 }
 fabrication(){const c=this.ctx,s=this.state,d=this.doc,active=s.fabLayers||[],theme=document.documentElement.dataset.theme;this.polygon(this.outline,theme==='dark'?'#1a211e':'#fffef9','#8d9f8d',1);if(!s.fabData)return;const colors={'F_Cu':'#c66f3c','B_Cu':'#3b91b0','F_Mask':'#699460','B_Mask':'#7d6e9d','F_Silkscreen':'#e3b85f','B_Silkscreen':'#837058','Edge_Cuts':'#233f31','PTH':'#141d17','NPTH':'#d64435'};
 for(const [filename,data] of Object.entries(s.fabData)){if(!active.includes(filename))continue;let off=document.createElement('canvas');off.width=this.canvas.width;off.height=this.canvas.height;let ctx=off.getContext('2d');ctx.setTransform(this.dpr,0,0,this.dpr,0,0);let key=Object.keys(colors).find(k=>filename.includes(k)),color=colors[key]||'#b17249';let from=p=>({x:p.x,y:d.board.height-p.y});
 for(const o of data.objects){ctx.globalCompositeOperation=o.polarity==='clear'?'destination-out':'source-over';ctx.fillStyle=color;ctx.strokeStyle=color;ctx.lineJoin='round';ctx.lineCap='round';if(o.kind==='region'){for(const cont of o.contours){ctx.beginPath();cont.map(from).forEach((p,i)=>{let q=this.project(p);if(!i)ctx.moveTo(q.x,q.y);else ctx.lineTo(q.x,q.y);});ctx.closePath();ctx.fill('evenodd');}}else if(o.kind==='line'){this.line([from(o.a),from(o.b)],color,o.width,[],0,ctx);}else if(o.kind==='flash'){let p=from(o);if(o.shape==='C')this.polygon(G.circle(p.x,p.y,o.sizes[0]/2,48),color,null,0,0,ctx);else if(o.shape==='R')this.polygon(G.rect(p.x-o.sizes[0]/2,p.y-o.sizes[1]/2,o.sizes[0],o.sizes[1]),color,null,0,0,ctx);else this.polygon(G.padPoly({x:p.x,y:p.y,w:o.sizes[0],h:o.sizes[1],shape:'oval'}),color,null,0,0,ctx);}else if(o.kind==='hole'||o.kind==='slot'){this.line([from(o.a),from(o.b)],color,o.diameter,[],0,ctx);if(o.kind==='hole')this.polygon(G.circle(o.a.x,d.board.height-o.a.y,o.diameter/2,40),color,null,0,0,ctx);}}
 c.save();c.globalAlpha=filename.includes('Mask')?.35:.88;c.drawImage(off,0,0,this.w,this.h);c.restore();}
 }
 hit(x,y){this.setup();let s=this.state,d=this.doc,point=this.unproject(x,y),tol=7/this.scale;let pads=C.pads(d).filter(p=>G.layerMatch(p.layers,s.side));let pp=pads.map(p=>({p,dist:Math.hypot(this.project(p).x-x,this.project(p).y-y)})).sort((a,b)=>a.dist-b.dist);if(pp[0]&&pp[0].dist<Math.max(7,Math.min(pp[0].p.w,pp[0].p.h)*this.scale/2+3))return{type:'pad',id:pp[0].p.id,object:pp[0].p};
 if(s.view!=='fabrication'){const label=(this.polarityHitLabels||[]).find(a=>Math.abs(x-a.x)<=a.w/2&&Math.abs(y-a.y)<=a.h/2),pad=label&&pads.find(a=>a.id===label.padId);if(pad)return{type:'pad',id:pad.id,object:pad};}
 for(const v of [...d.vias].reverse())if(G.dist(point,v)<Math.max(v.diameter/2,5/this.scale))return{type:'via',id:v.id,object:v};
 if(s.tool==='select')for(const p of [...d.parts].reverse().filter(p=>p.side===s.side||p.platform)){if(p.platform){const edge=p.platform.outline.map(a=>C.world(p,a));if(edge.some((a,i)=>G.segDist(point,a,edge[(i+1)%edge.length])<tol))return{type:'part',id:p.id,object:p};continue;}let poly=G.rect(-p.body.w/2,-p.body.h/2,p.body.w,p.body.h).map(a=>C.world(p,a)),top=poly.map(a=>this.project(a,p.body.z));if(G.inside({x,y},top)||G.inside(point,poly))return{type:'part',id:p.id,object:p};}
 for(const a of [...d.art].reverse().filter(a=>a.layer===s.side&&s.tool!=='trace'&&s.tool!=='via')){let ps=a.kind==='text'?C.textPaths(a.text,a.size).flat():a.kind==='image'?(a.rects||[]).flatMap(r=>G.rect(r.x,r.y,r.w,r.h)):a.points||G.rect(0,0,a.w||1,a.h||1),box=G.bounds(ps.map(p=>C.artPoint(a,p)));if(point.x>=box.minX-tol&&point.x<=box.maxX+tol&&point.y>=box.minY-tol&&point.y<=box.maxY+tol)return{type:'art',id:a.id,object:a};}
 for(const t of [...d.traces].reverse().filter(t=>t.layer===s.side))if(t.points.slice(1).some((b,i)=>G.segDist(point,t.points[i],b)<=t.width/2+tol/2))return{type:'trace',id:t.id,object:t};
 for(const h of (C.mountingHoles?C.mountingHoles(d):[]))if(G.dist(point,h)<h.drill/2+tol)return{type:'part',id:h.partId,object:d.parts.find(p=>p.id===h.partId)};
 for(const h of [...d.holes,...d.vias])if(G.dist(point,h)<(h.diameter||h.drill)/2+tol)return{type:d.vias.includes(h)?'via':'hole',id:h.id,object:h};
 for(const [type,arr] of [['keepout',d.keepouts],['cutout',d.cutouts],['zone',d.zones]])for(const a of [...arr].reverse())if(G.inside(point,a.points))return{type,id:a.id,object:a};return G.inside(point,this.outline)?{type:'board',id:'board',object:d.board}:null;
 }
 static preview(canvas,part){const d=C.blank();d.board.width=Math.max(12,part.body.w+8);d.board.height=Math.max(11,part.body.h+6);let p=C.clone(part);p.x=d.board.width/2;p.y=d.board.height/2;p.rotation=p.rotation||0;p.side=p.side||p.defaultSide||'top';d.parts=[p];const s={doc:d,view:'bench',side:'top',tilt:38,yaw:-14};let r=new Renderer(canvas,()=>s);r.resize();r.setup();r.cx=r.w/2;r.cy=r.h*.61;r.scale=Math.min((r.w-14)/(d.board.width),(r.h-13)/(d.board.height*.77+part.body.z*.63));r.ctx.clearRect(0,0,r.w,r.h);r.component(p,1);r.flush();}
}
C.Renderer=Renderer;
})(typeof self!=='undefined'?self:globalThis);

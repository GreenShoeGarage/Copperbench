/* COPPERBENCH representative module bodies and editable-block ghosts. MIT.
   Illustration only: never consumed by manufacturing exporters. */
(function(root){'use strict';const C=root.CB,G=C.G,R=C.Renderer;
const component=R.prototype.component;
R.prototype.component=function(p,alpha=1){
 if(!p.module||p.body.kind!=='module')return component.call(this,p,alpha);
 const m=p.module,w=p.body.w,h=p.body.h,gap=m.stackGap,z=gap+1.6;
 const box=(x,y,bw,bh,a,b,color)=>this.box(p,x,y,bw,bh,a,b,color,alpha);
 // Mating sockets and a narrow exposed pin are separate from the host body.
 for(const a of p.pads){box(a.x-.9,a.y-.9,1.8,1.8,.1,Math.max(.2,gap-.5),'#25392f');box(a.x-.24,a.y-.24,.48,.48,Math.max(.2,gap-.5),z+.8,'#d2b271');}
 if(!m.showBody)return;
 box(-w/2,-h/2,w,h,gap,z,'#256b63');
 for(const a of p.pads){this.cylinder(p,a.x,a.y,.85,z,z+.08,a.shape==='rect'?'#ffce79':'#bba668',alpha);this.cylinder(p,a.x,a.y,.25,z+.09,z+.11,'#12291e',alpha);}
 for(const a of m.holePattern||[]){this.cylinder(p,a.x,a.y,a.drill/2+.65,z,z+.03,'#cec195',alpha);this.cylinder(p,a.x,a.y,a.drill/2,z+.04,z+.06,'#17382c',alpha);}
 const line=(a,b,zz,width,color)=>this.surfaceLine(p,a,b,zz,width,color,alpha);
 const cap=(x,y)=>{box(x,y,1.4,2,z,z+1.1,'#c49e65');box(x-.15,y,1.7,.35,z+1.1,z+1.15,'#bdc5bd');box(x-.15,y+1.65,1.7,.35,z+1.1,z+1.15,'#bdc5bd');};
 if(m.kind==='display'){
  box(-w/2+2,-h/2+6,w-4,h-11,z,z+2,'#233137');box(-w/2+3,-h/2+7,w-6,h-13,z+2,z+2.08,'#071e28');
  this.text(p,'COPPER',-w/2+5,-2,z+2.11,2.4,'#68e4e2',alpha);this.text(p,'BENCH',-w/2+5,3,z+2.11,2.4,'#68e4e2',alpha);
 }else if(m.kind==='sensor'){
  box(-2,-2,4,4,z,z+1.1,'#314442');box(-1.5,-1.5,3,3,z+1.1,z+1.3,'#b7bbb0');this.cylinder(p,.5,-.5,.25,z+1.3,z+1.35,'#27322d',alpha);cap(-w/2+2,0);cap(w/2-3,0);this.text(p,'BME280',-w/2+2,4,z+.2,1.1,'#eef0d6',alpha);
 }else if(m.kind==='rtc'){
  box(-5,-3.5,10,7,z,z+2.1,'#273735');for(let i=0;i<8;i++){line({x:-5.4,y:-3+i*.85},{x:-4.6,y:-3+i*.85},z+1,.3,'#bec9bd');line({x:4.6,y:-3+i*.85},{x:5.4,y:-3+i*.85},z+1,.3,'#bec9bd');}this.text(p,'DS3231',-3.8,.5,z+2.12,1.1,'#e3e5d3',alpha);cap(w/2-3,-1);
 }else if(m.kind==='motor'){
  box(-4,-4.5,8,9,z,z+2,'#23312e');for(let i=0;i<12;i++){line({x:-4.7,y:-4+i*.72},{x:-3.8,y:-4+i*.72},z+1,.25,'#d3d8c9');line({x:3.8,y:-4+i*.72},{x:4.7,y:-4+i*.72},z+1,.25,'#d3d8c9');}box(-4,-h/2+1,8,5,z,z+4,'#478bb3');for(const x of [-2,2])this.cylinder(p,x,-h/2+3.5,1.1,z+4,z+4.1,'#b7c7c5',alpha);this.text(p,'TB6612',-3.6,0,z+2.04,1.1,'#e6e7cb',alpha);cap(-3,h/2-6);cap(2,h/2-6);
 }else{
  box(-2.5,-2.8,5,5.6,z,z+3,'#58645d');this.text(p,'3V3',-1.7,.5,z+3.05,1,'#dbe4d8',alpha);cap(-w/2+1,h/2-5);cap(w/2-2.5,h/2-5);
 }
};
const overlays=R.prototype.overlays;
R.prototype.overlays=function(){overlays.call(this);const s=this.state;if(!s.blockPlacing||!s.cursor||s.view==='fabrication')return;const t=C.Blocks.preview(s.blockPlacing.template,s.cursor.x,s.cursor.y,s.blockPlacing.rotation||0,!!s.blockPlacing.flip),c=this.ctx;c.save();c.globalAlpha=.65;for(const tr of t.traces)this.line(tr.points,tr.layer==='top'?'#f5b560':'#74b9e2',tr.width);for(const p of t.parts){const pts=G.rect(-p.body.w/2,-p.body.h/2,p.body.w,p.body.h).map(a=>C.world(p,a));this.polygon(pts,'#bde1b740','#dff6c4',1);for(const a of p.pads){const v=C.world(p,a);this.polygon(G.circle(v.x,v.y,Math.max(a.w,a.h)/2,16),'#eac486');}}
 for(const v of t.vias)this.polygon(G.circle(v.x,v.y,v.diameter/2,16),'#eac486');const b=C.Blocks.bounds(t),pts=G.rect(b.minX-1,b.minY-1,b.maxX-b.minX+2,b.maxY-b.minY+2);this.line([...pts,pts[0]],'#e9fbd4',.15,[4,4]);c.restore();};
})(typeof self!=='undefined'?self:globalThis);

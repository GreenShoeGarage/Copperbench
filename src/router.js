/* Cancellable-worker routing and conservative cell-to-vector copper fill.
   Two-layer A*, eight planar directions, legal through-via transitions. */
(function(root){'use strict';const C=root.CB,G=C.G,R=C.R={};
class Heap{constructor(){this.a=[];}push(v){let a=this.a,i=a.length;a.push(v);while(i){let p=(i-1)>>1;if(a[p].f<=v.f)break;a[i]=a[p];i=p;}a[i]=v;}pop(){let a=this.a,top=a[0],v=a.pop();if(a.length){let i=0;while(2*i+1<a.length){let c=2*i+1;if(c+1<a.length&&a[c+1].f<a[c].f)c++;if(a[c].f>=v.f)break;a[i]=a[c];i=c;}a[i]=v;}return top;}get length(){return this.a.length;}}
R.route=function(d,a,b,opts={}){
 const width=+opts.width||d.settings.traceWidth,net=a.net,active=opts.layer||'top',allowVias=opts.vias!==false,step=C.clamp(opts.step||.4,.2,1),layers=['top','bottom'];
 if(!net||net!==b.net)throw Error('Routing endpoints must belong to the same assigned net.');
 const obs=layers.map(l=>G.obstacles(d,net,l)),allowed=p=>p.layers==='both'?[0,1]:[p.layers==='bottom'?1:0],starts=allowed(a),ends=allowed(b),pref=active==='top'?0:1;
 // Prefer the selected side, then a direct route on the other side if both endpoints permit it.
 for(const l of [pref,1-pref].filter(l=>starts.includes(l)&&ends.includes(l))){let dx=b.x-a.x,dy=b.y-a.y,diag=Math.min(Math.abs(dx),Math.abs(dy)),bend={x:a.x+Math.sign(dx)*diag,y:a.y+Math.sign(dy)*diag};for(const p of [[a,b],[a,bend,b],[a,{x:b.x-Math.sign(dx)*diag,y:b.y-Math.sign(dy)*diag},b]]){let pts=p.filter((v,i)=>!i||G.dist(v,p[i-1])>.0001);if(G.pathClear(d,pts,width,net,layers[l],obs[l]).ok)return{traces:[{id:C.uid('t'),net,layer:layers[l],width,points:pts.map(v=>({x:C.q(v.x),y:C.q(v.y)})),locked:false}],vias:[],visited:0};}}
 const outline=G.outline(d),cutouts=d.cutouts.map(c=>c.points),nx=Math.ceil(d.board.width/step)+1,ny=Math.ceil(d.board.height/step)+1,origin={x:a.x-Math.round(a.x/step)*step,y:a.y-Math.round(a.y/step)*step},sx=Math.round(a.x/step),sy=Math.round(a.y/step);
 const key=(x,y,l)=>(l*ny+y)*nx+x,position=(x,y)=>({x:x*step+origin.x,y:y*step+origin.y}),passCache=[new Map,new Map],viaCache=new Map;
 const clearAt=(p,l,r)=>{if(p.x<0||p.y<0||p.x>d.board.width||p.y>d.board.height||!G.inside(p,outline))return false;for(let i=0;i<outline.length;i++)if(G.segDist(p,outline[i],outline[(i+1)%outline.length])<r+d.profile.edge+C.EPS)return false;for(const c of cutouts)if(G.pointPolyDist(p,c)<r+d.profile.edge||G.inside(p,c))return false;let box={minX:p.x,minY:p.y,maxX:p.x,maxY:p.y};for(const j of obs[l].index.query(box,r+d.profile.clearance+C.EPS))if(G.pointPolyDist(p,obs[l].items[j].poly)<r+d.profile.clearance+C.EPS)return false;return true;};
 const pass=(x,y,l)=>{let k=y*nx+x,c=passCache[l];if(c.has(k))return c.get(k);let ok=clearAt(position(x,y),l,width/2);c.set(k,ok);return ok;};
 const viaPass=(x,y)=>{let k=y*nx+x;if(viaCache.has(k))return viaCache.get(k);let ok=clearAt(position(x,y),0,d.settings.viaDiameter/2)&&clearAt(position(x,y),1,d.settings.viaDiameter/2);viaCache.set(k,ok);return ok;};
 let open=new Heap,best=new Map,parents=new Map,closed=new Set,goal=null,visited=0;for(const l of starts){let k=key(sx,sy,l),h=G.dist(a,b);open.push({x:sx,y:sy,l,k,g:l===pref?0:.05,f:h+(l===pref?0:.05),dir:-1});best.set(k,0);}
 const dirs=[[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]];
 while(open.length&&visited<(opts.maxNodes||80000)){
  let cur=open.pop();if(closed.has(cur.k))continue;closed.add(cur.k);visited++;let p=position(cur.x,cur.y);
  if(ends.includes(cur.l)&&G.dist(p,b)<=step*1.8&&G.pathClear(d,[p,b],width,net,layers[cur.l],obs[cur.l]).ok){goal=cur;break;}
  for(let dir=0;dir<dirs.length+(allowVias?1:0);dir++){
   let via=dir===8,x=cur.x+(via?0:dirs[dir][0]),y=cur.y+(via?0:dirs[dir][1]),l=via?1-cur.l:cur.l;if(x<0||y<0||x>=nx||y>=ny)continue;let k=key(x,y,l);if(closed.has(k))continue;if(via?!viaPass(x,y):!pass(x,y,l))continue;
   if(!via){let mid={x:(p.x+position(x,y).x)/2,y:(p.y+position(x,y).y)/2};if(!clearAt(mid,l,width/2+step*.16))continue;}
   let g=cur.g+(via?6:dir<4?step:step*Math.SQRT2)+(cur.dir!==dir&&!via?.04:0);if(g>=(best.get(k)??Infinity))continue;best.set(k,g);parents.set(k,cur);let h=G.dist(position(x,y),b)+(ends.includes(l)?0:5);open.push({x,y,l,k,g,f:g+h,dir});
  }
 }
 if(!goal)return{traces:[],vias:[],visited,error:visited>=(opts.maxNodes||80000)?'Search limit reached. Try a different placement, a coarser route grid, or manual routing.':'No compliant path found at this width. Move a part, reduce width within the rules, or allow vias.'};
 let path=[],cur=goal;while(cur){path.push({...position(cur.x,cur.y),l:cur.l});cur=parents.get(cur.k);}path.reverse();path[0]={x:a.x,y:a.y,l:path[0].l};path.push({x:b.x,y:b.y,l:path[path.length-1].l});let traces=[],vias=[],points=[path[0]],l=path[0].l;
 const finish=()=>{let simple=[];for(const p of points){while(simple.length>1&&Math.abs(G.cross(simple[simple.length-2],simple[simple.length-1],p))<.00001)simple.pop();if(!simple.length||G.dist(simple[simple.length-1],p)>.0001)simple.push({x:C.q(p.x),y:C.q(p.y)});}if(simple.length>1)traces.push({id:C.uid('t'),net,layer:layers[l],width,points:simple,locked:false});};
 for(const p of path.slice(1)){if(p.l!==l){finish();vias.push({id:C.uid('v'),net,x:C.q(p.x),y:C.q(p.y),diameter:d.settings.viaDiameter,drill:d.settings.viaDrill,tented:false});l=p.l;points=[p];}else points.push(p);}finish();
 // Exact final segment checks are independent of the search occupancy approximation.
 for(const t of traces)if(!G.pathClear(d,t.points,t.width,net,t.layer,obs[t.layer==='top'?0:1]).ok)return{traces:[],vias:[],visited,error:'A candidate failed exact clearance validation. No copper was committed; try a finer routing grid.'};
 return{traces,vias,visited};
};
R.routeGroup=function(doc,padIds,opts={},progress=()=>{}){let d=C.clone(doc),pads=C.pads(d).filter(p=>padIds.includes(p.id)),traces=[],vias=[],failures=[],done=[];if(pads.length<2)throw Error('Select at least two pins.');const net=pads[0].net;if(!net||pads.some(p=>p.net!==net))throw Error('All selected pins must share one net.');let remaining=pads.slice(1);done.push(pads[0]);while(remaining.length){let best=null;for(let i=0;i<remaining.length;i++)for(const a of done){let dist=G.dist(a,remaining[i]);if(!best||dist<best.dist)best={a,b:remaining[i],i,dist};}let conn=G.connectivity(d),already=conn.padGroups[best.a.id]!==undefined&&conn.padGroups[best.a.id]===conn.padGroups[best.b.id],result=already?{traces:[],vias:[]}:R.route(d,best.a,best.b,opts);if(result.error)failures.push({from:best.a.id,to:best.b.id,message:result.error});else{traces.push(...result.traces);vias.push(...result.vias);d.traces.push(...result.traces);d.vias.push(...result.vias);}done.push(...remaining.splice(best.i,1));progress({complete:done.length-1,total:pads.length-1});}return{traces,vias,failures};};
R.fillZone=function(d,z){
 if(!z.net)throw Error('Assign a net before filling a zone.');if(!G.simple(z.points))throw Error('Zone must be a simple closed polygon.');
 const step=C.clamp(Math.min(z.step||.25,z.thermal===false?1:(z.spoke||.5)/2.1),.1,1),b=G.bounds(z.points),x0=Math.floor(Math.max(0,b.minX)/step)*step,y0=Math.floor(Math.max(0,b.minY)/step)*step,nx=Math.ceil((Math.min(d.board.width,b.maxX)-x0)/step),ny=Math.ceil((Math.min(d.board.height,b.maxY)-y0)/step),n=nx*ny;
 if(n>650000)throw Error('Zone is too large for this fill resolution. Increase the zone cell size or use smaller zones.');
 const mask=new Uint8Array(n),outline=G.outline(d),r=step/Math.SQRT2,ob=G.obstacles(d,z.net,z.layer),copper=G.copper(d,false).filter(p=>p.net===z.net&&G.layerMatch(p.layer,z.layer)),ownIndex=new G.Spatial(copper),thermals=copper.filter(p=>p.kind==='pad'||p.kind==='via'),thermalIndex=new G.Spatial(thermals),seeds=new Uint8Array(n);let allowed=0;
 for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
  let p={x:x0+(x+.5)*step,y:y0+(y+.5)*step},k=y*nx+x,box={minX:p.x-r,minY:p.y-r,maxX:p.x+r,maxY:p.y+r};
  if(!G.inside(p,z.points)||!G.inside(p,outline))continue;let clear=true;for(let i=0;i<z.points.length;i++)if(G.segDist(p,z.points[i],z.points[(i+1)%z.points.length])<r){clear=false;break;}if(!clear)continue;
  for(let i=0;i<outline.length;i++)if(G.segDist(p,outline[i],outline[(i+1)%outline.length])<r+d.profile.edge+C.EPS){clear=false;break;}if(!clear)continue;
  for(const c of d.cutouts)if(G.inside(p,c.points)||G.pointPolyDist(p,c.points)<r+d.profile.edge+C.EPS){clear=false;break;}if(!clear)continue;
  for(const j of ob.index.query(box,d.profile.clearance)){if(G.pointPolyDist(p,ob.items[j].poly)<r+d.profile.clearance+C.EPS){clear=false;break;}}if(!clear)continue;
  if(z.thermal!==false)for(const j of thermalIndex.query(box,z.gap||.3)){let o=thermals[j];if(G.pointPolyDist(p,o.poly)<(z.gap||.3)+r){let center=o.pad||o.via,t=G.rotate({x:p.x-center.x,y:p.y-center.y},-(center.rotation||0)),half=(z.spoke||.5)/2-step/2;if(Math.abs(t.x)>half&&Math.abs(t.y)>half){clear=false;break;}}}if(!clear)continue;
  mask[k]=1;allowed++;let cell=G.rect(x0+x*step,y0+y*step,step,step);for(const j of ownIndex.query(G.bounds(cell)))if(G.polyDist(cell,copper[j].poly)<C.EPS){seeds[k]=1;break;}
 }
 let visited=new Uint8Array(n),queue=new Int32Array(n),removedIslands=0,retained=0;for(let i=0;i<n;i++){if(!mask[i]||visited[i])continue;let head=0,tail=1,connected=!!seeds[i];queue[0]=i;visited[i]=1;while(head<tail){let k=queue[head++],x=k%nx,y=Math.floor(k/nx);for(const j of [x? k-1:-1,x<nx-1?k+1:-1,y?k-nx:-1,y<ny-1?k+nx:-1])if(j>=0&&mask[j]&&!visited[j]){visited[j]=1;queue[tail++]=j;connected=connected||!!seeds[j];}}if(!connected){removedIslands++;for(let j=0;j<tail;j++)mask[queue[j]]=0;}else retained+=tail;}
 // Merge equal horizontal runs vertically; every output rectangle is exact vector geometry.
 let rects=[],active=new Map;for(let y=0;y<ny;y++){let next=new Map;for(let x=0;x<nx;x++){if(!mask[y*nx+x])continue;let start=x;while(x+1<nx&&mask[y*nx+x+1])x++;let key=start+':'+x,old=active.get(key);if(old){old.h=C.q(old.h+step);next.set(key,old);}else{let rect={x:C.q(x0+start*step),y:C.q(y0+y*step),w:C.q((x-start+1)*step),h:C.q(step)};rects.push(rect);next.set(key,rect);}}active=next;}
 return{rects,step,removedIslands,cells:retained,area:C.q(retained*step*step),method:'Conservative vectorized cell fill; isolated islands removed'};
};
R.fillAll=function(doc,progress=()=>{}){let d=C.clone(doc);d.zones.forEach(z=>z.fill=null);for(let i=0;i<d.zones.length;i++){d.zones[i].fill=R.fillZone(d,d.zones[i]);progress({complete:i+1,total:d.zones.length});}return d.zones.map(z=>({id:z.id,fill:z.fill}));};
if(typeof module!=='undefined')module.exports=R;
})(typeof self!=='undefined'?self:globalThis);

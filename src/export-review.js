/* Review generated text. Ink survival is sampled, not an area or print-quality
 * certificate. Uses the app's reader; independent CAM qualification is separate.
 */
(function(root){
 'use strict';const C=root.CB,G=C.G,Review=C.Review={};
 function polygons(o){
  if(o.kind==='region')return o.contours;
  if(o.kind==='line')return[G.capsule(o.a,o.b,o.width)];
  if(o.shape==='C')return[G.circle(o.x,o.y,o.sizes[0]/2)];
  const w=o.sizes[0],h=o.sizes[1]||w;
  if(o.shape==='R')return[G.rect(o.x-w/2,o.y-h/2,w,h)];
  return[G.capsule({x:o.x-(w>h?(w-h)/2:0),y:o.y-(h>w?(h-w)/2:0)},
    {x:o.x+(w>h?(w-h)/2:0),y:o.y+(h>w?(h-w)/2:0)},Math.min(w,h))];
 }
 Review.inkTester=function(parsed){
  const records=parsed.objects.map((o,i)=>{const polys=polygons(o);return {i,o,polys,box:G.bounds(polys.flat())};}),index=new G.Spatial(records,8);
  return point=>{let ink=false;const b={minX:point.x,minY:point.y,maxX:point.x,maxY:point.y};
   for(const i of index.query(b).sort((a,b)=>a-b)){const r=records[i];if(r.polys.some(poly=>G.inside(point,poly)))ink=r.o.polarity==='dark';}return ink;};
 };
 Review.inspect=function(doc,files,options={}){
  const report={projectId:doc.id,title:doc.title,appVersion:C.VERSION,schema:doc.schema,
   designUpdated:doc.updated,board:{width:doc.board.width,height:doc.board.height,copperLayers:2},files:[],silkscreen:[],errors:[],warnings:[],
   qualification:{readback:'COPPERBENCH generated subset',independentCAM:'not established by this report',manufacturer:'not established',physical:'not established'}};
  const parsed={};
  for(const [name,text]of Object.entries(files)){
   try{const r=name.endsWith('.drl')?C.M.readDrill(text):C.M.readGerber(text);parsed[name]=r;
    report.files.push({name,characters:text.length,objects:r.objects.length,darkObjects:r.objects.filter(x=>x.polarity==='dark').length,
      drills:name.endsWith('.drl')?r.objects.filter(x=>x.kind==='hole').length:0,slots:name.endsWith('.drl')?r.objects.filter(x=>x.kind==='slot').length:0});
   }catch(e){report.errors.push(name+': '+e.message);}
  }
  for(const name of ['board-F_Cu.gbr','board-B_Cu.gbr','board-F_Mask.gbr','board-B_Mask.gbr','board-F_Silkscreen.gbr','board-B_Silkscreen.gbr','board-Edge_Cuts.gbr'])
   if(!parsed[name])report.errors.push('Missing or unreadable required file: '+name);
  const holes=G.holes(doc);
  for(const [plated,stem]of [[true,'PTH'],[false,'NPTH']]){
   const expected=holes.filter(h=>h.plated===plated),r=parsed['board-'+stem+'.drl'],actual=r?.objects||[];
   if(expected.length!==actual.length)report.errors.push(stem+' drill count differs from the design: '+actual.length+' / '+expected.length+'.');
   if(expected.length===actual.length){const remaining=[...actual];for(const h of expected){const [a,b]=G.holeEndpoints(h),world=p=>({x:p.x,y:doc.board.height-p.y}),index=remaining.findIndex(o=>Math.abs(o.diameter-h.drill)<.00001&&((G.dist(world(a),o.a)<.00001&&G.dist(world(b),o.b)<.00001)||(G.dist(world(b),o.a)<.00001&&G.dist(world(a),o.b)<.00001)));if(index<0){report.errors.push(stem+' drill coordinates or diameters differ from the design.');break;}remaining.splice(index,1);}}
  }
  const edge=parsed['board-Edge_Cuts.gbr'];if(edge){const source=G.bounds(G.outline(doc)),pts=edge.objects.filter(o=>o.kind==='line').flatMap(o=>[o.a,o.b]),b=G.bounds(pts);
   if(!pts.length||Math.abs(b.minX-source.minX)>.00001||Math.abs(b.maxX-source.maxX)>.00001||Math.abs(b.minY-(doc.board.height-source.maxY))>.00001||Math.abs(b.maxY-(doc.board.height-source.minY))>.00001)report.errors.push('Exported outline bounds differ from the design.');}
  const strokes=C.silkStrokes(doc),shapes=C.silkRects(doc),cap=Math.max(200,Math.min(12000,options.samples||6000));
  for(const layer of ['top','bottom']){
   const ss=strokes.filter(s=>s.layer===layer),rs=shapes.filter(s=>s.layer===layer),r=parsed['board-'+(layer==='top'?'F':'B')+'_Silkscreen.gbr'];
   const status={layer,sourceStrokes:ss.length,sourceShapes:rs.length,samples:0,surviving:0,clipped:0,partialOwners:[],fullyClippedOwners:[],sampling:'centreline and interior sample points; not exact ink area'};
   report.silkscreen.push(status);if(!r)continue;
   const dark=r.objects.filter(x=>x.polarity==='dark').length;
   if(ss.length+rs.length&&!dark)report.errors.push(layer+' silkscreen has print-enabled source artwork but no dark export geometry.');
   const test=Review.inkTester(r),candidates=[];
   for(const s of ss)for(let i=1;i<s.points.length;i++){
    const a=s.points[i-1],b=s.points[i],n=Math.min(32,Math.max(2,Math.ceil(G.dist(a,b)/.3)));
    for(let j=0;j<=n;j++)candidates.push({owner:s.owner,point:{x:a.x+(b.x-a.x)*j/n,y:a.y+(b.y-a.y)*j/n}});
   }
   for(const s of rs){const box=G.bounds(s.poly);for(const fx of [.2,.5,.8])for(const fy of [.2,.5,.8]){const point={x:box.minX+(box.maxX-box.minX)*fx,y:box.minY+(box.maxY-box.minY)*fy};if(G.inside(point,s.poly))candidates.push({owner:s.owner,point});}}
   const owners=new Map,step=Math.max(1,Math.ceil(candidates.length/cap));
   for(let i=0;i<candidates.length;i+=step){const a=candidates[i],visible=test({x:a.point.x,y:doc.board.height-a.point.y});status.samples++;if(visible)status.surviving++;else status.clipped++;
    const k=a.owner||'unidentified',v=owners.get(k)||{sampled:0,visible:0};v.sampled++;if(visible)v.visible++;owners.set(k,v);}
   for(const [id,o]of owners){if(!o.visible)status.fullyClippedOwners.push(id);else if(o.visible<o.sampled)status.partialOwners.push(id);}
   if(status.samples&&!status.surviving)report.warnings.push(layer+' silkscreen: none of the sampled artwork survives clipping. Inspect the exported layer.');
   else if(status.clipped)report.warnings.push(layer+' silkscreen: '+status.clipped+' / '+status.samples+' sampled points are clipped. Inspect the exported layer.');
  }
  report.valid=report.errors.length===0;return report;
 };
 if(typeof module!=='undefined')module.exports=Review;
})(typeof self!=='undefined'?self:globalThis);

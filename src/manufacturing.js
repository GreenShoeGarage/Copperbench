/* Gerber X2 / RS-274X and Excellon exporters, plus a separate read-back interpreter.
   Source: Ucamco public Gerber specification; OSH Park drill/slot documentation.
   Coordinates are never mirrored for the bottom layer; only the editor's view is flipped. */
(function(root){'use strict';const C=root.CB,G=C.G,M=C.M={};
class GerberWriter{
 constructor(doc,func,x2=true,polarity='Positive'){this.doc=doc;this.ap=new Map;this.defs=[];this.commands=[];this.next=10;this.func=func;this.x2=x2;this.polarity=polarity;this.aperture('C',[.1]);}
 coord(p){return'X'+Math.round(p.x*1e6)+'Y'+Math.round((this.doc.board.height-p.y)*1e6);}
 aperture(shape,sizes){let key=shape+':'+sizes.map(x=>Number(x).toFixed(6)).join('X');if(!this.ap.has(key)){let n=this.next++;this.ap.set(key,n);this.defs.push('%ADD'+n+shape+','+sizes.map(x=>Number(x).toFixed(6)).join('X')+'*%');}let n=this.ap.get(key);this.commands.push('D'+n+'*');return n;}
 polarityTo(p){this.commands.push('%LP'+(p==='clear'?'C':'D')+'*%');}
 line(points,width){if(points.length<2)return;this.aperture('C',[width]);this.commands.push(this.coord(points[0])+'D02*');for(const p of points.slice(1))this.commands.push(this.coord(p)+'D01*');}
 circle(x,y,d){this.aperture('C',[d]);this.commands.push(this.coord({x,y})+'D03*');}
 pad(p,extra=0){if(p.shape==='circle'){this.circle(p.x,p.y,Math.max(p.w,p.h)+2*extra);return;}let a=((p.rotation||0)%180+180)%180;if(p.shape==='rect'&&(Math.abs(a)<.0001||Math.abs(a-90)<.0001)){this.aperture('R',a<1?[p.w+2*extra,p.h+2*extra]:[p.h+2*extra,p.w+2*extra]);this.commands.push(this.coord(p)+'D03*');}else this.region([G.padPoly(p,extra)]);}
 region(contours){this.commands.push('G36*');for(const p of contours){if(p.length<3)continue;this.commands.push(this.coord(p[0])+'D02*');for(const v of p.slice(1))this.commands.push(this.coord(v)+'D01*');this.commands.push(this.coord(p[0])+'D01*');}this.commands.push('G37*');}
 finish(){return['G04 COPPERBENCH '+C.VERSION+' - inspect before ordering*','%FSLAX46Y46*%','%MOMM*%',...(this.x2?['%TF.GenerationSoftware,GreenShoeGarage,COPPERBENCH,'+C.VERSION+'*%','%TF.FileFunction,'+this.func+'*%','%TF.FilePolarity,'+this.polarity+'*%']:[]),...this.defs,'%LPD*%','G01*',...this.commands,'M02*',''].join('\n');}
}
M.GerberWriter=GerberWriter;
// Gerber section 4.10: separate contours are UNIONED, never XORed. A nested
// clear rectangle + board contour clears the entire legend (the v1.3.0 defect).
// Decompose the exterior into non-self-intersecting horizontal trapezoids. This
// is analytic geometry between outline vertices, not a pixel/grid approximation.
M.exteriorRegions=function(outline,bounds){
 const ys=[...new Set([bounds.minY,...outline.map(p=>p.y),bounds.maxY])].sort((a,b)=>a-b),result=[];
 const edges=outline.map((a,i)=>[a,outline[(i+1)%outline.length]]).filter(([a,b])=>a.y!==b.y);
 const xAt=(edge,y)=>edge===null?bounds.minX:edge==='right'?bounds.maxX:edge[0].x+(y-edge[0].y)*(edge[1].x-edge[0].x)/(edge[1].y-edge[0].y);
 const add=(left,right,y0,y1)=>{
  let poly=[{x:xAt(left,y0),y:y0},{x:xAt(right,y0),y:y0},{x:xAt(right,y1),y:y1},{x:xAt(left,y1),y:y1}].map(p=>({x:Math.round(p.x*1e6)/1e6,y:Math.round(p.y*1e6)/1e6}));
  poly=poly.filter((p,i)=>p.x!==poly[(i+poly.length-1)%poly.length].x||p.y!==poly[(i+poly.length-1)%poly.length].y);
  if(poly.length>=3&&Math.abs(G.area(poly))>1e-10)result.push(poly);
 };
 for(let i=1;i<ys.length;i++){
  const y0=ys[i-1],y1=ys[i];if(y1-y0<1e-7)continue;const mid=(y0+y1)/2;
  const hits=edges.filter(([a,b])=>mid>Math.min(a.y,b.y)&&mid<Math.max(a.y,b.y)).sort((a,b)=>xAt(a,mid)-xAt(b,mid));
  if(hits.length%2)throw Error('Cannot clip silkscreen against an invalid board outline.');
  let left=null;for(let j=0;j<hits.length;j+=2){add(left,hits[j],y0,y1);left=hits[j+1];}add(left,'right',y0,y1);
 }
 return result;
};
M.silkBounds=function(doc,strokes,images){
 // Include the actual artwork, even far outside the board. Fixed 100 mm frames
 // miss larger/off-board images. Stream the bounds to avoid argument-size limits.
 const b={minX:0,minY:0,maxX:doc.board.width,maxY:doc.board.height};
 const add=(p,r=0)=>{b.minX=Math.min(b.minX,p.x-r);b.minY=Math.min(b.minY,p.y-r);b.maxX=Math.max(b.maxX,p.x+r);b.maxY=Math.max(b.maxY,p.y+r);};
 for(const p of G.outline(doc))add(p);for(const s of strokes)for(const p of s.points)add(p,s.width/2);for(const im of images)for(const p of im.poly)add(p);
 return {minX:b.minX-1,minY:b.minY-1,maxX:b.maxX+1,maxY:b.maxY+1};
};
M.files=function(doc,{x2=true,paste=false}={}){
 const files={},pads=C.pads(doc),silk=C.silkStrokes(doc),images=C.silkRects(doc),base='board',stem={top:'F',bottom:'B'},exterior=M.exteriorRegions(G.outline(doc),M.silkBounds(doc,silk,images));
 for(const layer of ['top','bottom']){
  const st=stem[layer],where=layer==='top'?'Top':'Bot',cu=new GerberWriter(doc,'Copper,'+(layer==='top'?'L1':'L2')+','+where,x2);
  for(const z of doc.zones.filter(z=>z.layer===layer)){if(!z.fill)throw Error('Refill all copper zones before generating manufacturing files.');for(const r of z.fill.rects)cu.region([G.rect(r.x,r.y,r.w,r.h)]);}
  for(const t of doc.traces.filter(t=>t.layer===layer))cu.line(t.points,t.width);
  for(const p of pads.filter(p=>G.layerMatch(p.layers,layer)))cu.pad(p);
  for(const v of doc.vias)cu.circle(v.x,v.y,v.diameter);
  files[base+'-'+st+'_Cu.gbr']=cu.finish();
  const mask=new GerberWriter(doc,'Soldermask,'+where,x2,'Negative');for(const p of pads.filter(p=>G.layerMatch(p.layers,layer)))mask.pad(p,doc.profile.maskExpansion);for(const v of doc.vias.filter(v=>!v.tented))mask.circle(v.x,v.y,v.diameter+2*doc.profile.maskExpansion);for(const h of G.holes(doc).filter(h=>!h.plated)){let[a,b]=G.holeEndpoints(h);mask.line([a,b],h.drill+.1);if(!h.slot)mask.circle(h.x,h.y,h.drill+.1);}files[base+'-'+st+'_Mask.gbr']=mask.finish();
  const legend=new GerberWriter(doc,'Legend,'+where,x2);for(const s of silk.filter(s=>s.layer===layer))legend.line(s.points,s.width);for(const im of images.filter(im=>im.layer===layer))legend.region([im.poly]);
  // Subtract openings/cutouts and explicit exterior pieces. Each clear region
  // has only one contour, so every compliant Gerber reader retains on-board ink.
  legend.polarityTo('clear');for(const p of pads.filter(p=>G.layerMatch(p.layers,layer)))legend.pad(p,doc.profile.maskExpansion+.05);for(const v of doc.vias.filter(v=>!v.tented))legend.circle(v.x,v.y,v.diameter+2*doc.profile.maskExpansion+.1);for(const h of G.holes(doc).filter(h=>!h.plated)){let[a,b]=G.holeEndpoints(h);legend.line([a,b],h.drill+.1);if(!h.slot)legend.circle(h.x,h.y,h.drill+.1);}for(const cut of doc.cutouts)legend.region([cut.points]);for(const poly of exterior)legend.region([poly]);legend.polarityTo('dark');files[base+'-'+st+'_Silkscreen.gbr']=legend.finish();
  if(paste){const pa=new GerberWriter(doc,'Paste,'+where,x2);for(const p of pads.filter(p=>p.layers===layer&&!p.drill))pa.pad(p);files[base+'-'+st+'_Paste.gbr']=pa.finish();}
 }
 const edge=new GerberWriter(doc,'Profile,NP',x2),out=G.outline(doc);edge.line([...out,out[0]],.05);for(const c of doc.cutouts)edge.line([...c.points,c.points[0]],.05);files[base+'-Edge_Cuts.gbr']=edge.finish();
 const holes=G.holes(doc);for(const plated of [true,false]){const hs=holes.filter(h=>h.plated===plated);if(hs.length)files[base+(plated?'-PTH':'-NPTH')+'.drl']=M.drill(doc,hs,plated);}
 return files;
};
M.silkInventory=doc=>{const strokes=C.silkStrokes(doc),images=C.silkRects(doc);return ['top','bottom'].map(layer=>({layer,strokes:strokes.filter(x=>x.layer===layer).length,shapes:images.filter(x=>x.layer===layer).length}));};
M.drill=function(doc,holes,plated){let sizes=[...new Set(holes.map(h=>h.drill.toFixed(6)))].sort((a,b)=>a-b),lines=['M48','; COPPERBENCH '+C.VERSION,'; TYPE='+(plated?'PLATED':'NON_PLATED'),'; FILE_FORMAT=4:6','METRIC,TZ',...sizes.map((s,i)=>'T'+String(i+1).padStart(2,'0')+'C'+s),'%','G90','G05'];const xy=p=>'X'+p.x.toFixed(6)+'Y'+(doc.board.height-p.y).toFixed(6);sizes.forEach((s,i)=>{lines.push('T'+String(i+1).padStart(2,'0'));for(const h of holes.filter(h=>h.drill.toFixed(6)===s)){if(h.slot){let[a,b]=G.holeEndpoints(h);lines.push(xy(a)+'G85'+xy(b),'G05');}else lines.push(xy(h));}});lines.push('M30','');return lines.join('\n');};
// Read back the *text*, not the project. Supported generator subset is deliberately strict.
M.readGerber=function(text){let apertures={},selected=null,x=0,y=0,unit=1,decimal=6,region=null,contour=null,pol='dark',objects=[],func='',done=false;
 const tokens=text.match(/%[^%]*%|[^*%]+\*/g)||[];
 for(let token of tokens){token=token.trim();if(!token)continue;
 if(token.startsWith('%')){let t=token.slice(1,-1).replace(/\*$/,'').trim();if(t.startsWith('FS')){let m=t.match(/X(\d)(\d)Y(\d)(\d)/);if(!m||m[2]!==m[4]||!t.startsWith('FSL'))throw Error('Unsupported Gerber coordinate format.');decimal=+m[2];}
 else if(t==='MOMM')unit=1;else if(t==='MOIN')unit=25.4;else if(t.startsWith('ADD')){let m=t.match(/^ADD(\d+)([CRO]),([\d.X+-]+)$/);if(!m)throw Error('Unsupported aperture.');apertures[+m[1]]={shape:m[2],sizes:m[3].split('X').map(v=>+v*unit)};}else if(t==='LPD')pol='dark';else if(t==='LPC')pol='clear';else if(t.startsWith('TF.FileFunction,'))func=t.slice(16);else if(/^T[FAOD]/.test(t)){}else throw Error('Unsupported Gerber parameter: '+t.slice(0,50));continue;}
 let t=token.replace(/\*$/,'').trim();if(/^G04/.test(t))continue;if(t==='M02'){done=true;continue;}if(t==='G01'||t==='G75')continue;if(t==='G36'){region=[];contour=null;continue;}if(t==='G37'){if(!region)throw Error('Unmatched region end.');if(!region.length||region.some(p=>p.length<4||p[0].x!==p[p.length-1].x||p[0].y!==p[p.length-1].y))throw Error('Gerber region contours must be closed.');objects.push({kind:'region',contours:region,polarity:pol});region=null;contour=null;continue;}
 if(/^D\d+$/.test(t)){let n=+t.slice(1);if(n<10)throw Error('Standalone drawing operations are not supported by this reader.');selected=apertures[n];if(!selected)throw Error('Undefined aperture');continue;}
 let m=t.match(/^(?:G01)?(?:X([+-]?\d+))?(?:Y([+-]?\d+))?D0?([123])$/);if(!m)throw Error('Unsupported Gerber command: '+t.slice(0,60));let nx=m[1]===undefined?x:+m[1]/10**decimal*unit,ny=m[2]===undefined?y:+m[2]/10**decimal*unit,op=+m[3];if(region){if(op===2){contour=[{x:nx,y:ny}];region.push(contour);}else if(op===1){if(!contour)throw Error('Region without start.');contour.push({x:nx,y:ny});}else throw Error('Flash inside region.');}else if(op===1){if(!selected||selected.shape!=='C')throw Error('Only circular stroked apertures are supported.');objects.push({kind:'line',a:{x,y},b:{x:nx,y:ny},width:selected.sizes[0],polarity:pol});}else if(op===3){if(!selected)throw Error('Flash without aperture.');objects.push({kind:'flash',x:nx,y:ny,shape:selected.shape,sizes:[...selected.sizes],polarity:pol});}x=nx;y=ny;
 }
 if(!done||region)throw Error('Incomplete Gerber file.');return{format:'Gerber',function:func,objects};
};
M.readDrill=function(text){let tools={},current=null,objects=[],units=1,done=false;for(let t of text.split(/\r?\n/).map(x=>x.trim())){if(!t||t.startsWith(';')||['M48','%','G90','G05','M71'].includes(t))continue;if(t.startsWith('METRIC')){units=1;continue;}if(t.startsWith('INCH')){units=25.4;continue;}if(t==='M30'){done=true;continue;}let tool=t.match(/^T(\d+)(?:C([\d.]+))?$/);if(tool){if(tool[2])tools[+tool[1]]=+tool[2]*units;else{current=tools[+tool[1]];if(!current)throw Error('Missing drill tool definition.');}continue;}let m=t.match(/^X([+-]?[\d.]+)Y([+-]?[\d.]+)(?:G85X([+-]?[\d.]+)Y([+-]?[\d.]+))?$/);if(!m||!current)throw Error('Unsupported or ambiguous Excellon command: '+t);if(!m[1].includes('.')||!m[2].includes('.'))throw Error('This reader requires explicit-decimal Excellon coordinates.');let a={x:+m[1]*units,y:+m[2]*units};objects.push({kind:m[3]?'slot':'hole',a,b:m[3]?{x:+m[3]*units,y:+m[4]*units}:a,diameter:current});}if(!done)throw Error('Incomplete Excellon file.');return{format:'Excellon',tools,objects};};
M.bom=function(d){const rows=[['Reference','Value','Footprint','Side','X (mm)','Y (mm)','Rotation','Footprint checked']];for(const p of d.parts)rows.push([p.ref,p.value,p.name,p.side,p.x,p.y,p.rotation,p.verified?'yes':'no']);return rows.map(r=>r.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\n');};
M.svg=function(d,layer='top'){const E=C.esc,points=p=>p.map(v=>v.x+','+v.y).join(' '),out=G.outline(d);let s=[`<svg xmlns="http://www.w3.org/2000/svg" width="${d.board.width}mm" height="${d.board.height}mm" viewBox="0 0 ${d.board.width} ${d.board.height}"><title>${E(d.title)} — ${layer}</title><g fill="none" stroke="black" stroke-width="0.05"><polygon points="${points(out)}"/>`];for(const c of d.cutouts)s.push(`<polygon points="${points(c.points)}"/>`);s.push('</g>');for(const a of C.silkStrokes(d).filter(s=>s.layer===layer))s.push(`<polyline points="${points(a.points)}" fill="none" stroke="black" stroke-width="${a.width}" stroke-linecap="round" stroke-linejoin="round"/>`);for(const r of C.silkRects(d).filter(s=>s.layer===layer))s.push(`<polygon points="${points(r.poly)}" fill="black"/>`);s.push('</svg>');return s.join('\n');};
if(typeof module!=='undefined')module.exports=M;
})(typeof self!=='undefined'?self:globalThis);

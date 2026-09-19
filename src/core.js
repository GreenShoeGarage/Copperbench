/* COPPERBENCH — canonical document model. MIT, Green Shoe Garage, 2026.
   Persisted distances are millimetres, quantized to 0.0001 mm (0.1 µm).
   Manufacturing coordinates use integer 10^-6 mm. Camera data is never exported. */
(function(root){
'use strict';
const C=root.CB=root.CB||{};
C.VERSION='1.7.1'; C.SCHEMA=5; C.EPS=.003;
C.q=v=>Math.round(Number(v)*10000)/10000;
C.uid=(prefix='id')=>prefix+'_'+(typeof crypto!=='undefined'&&crypto.randomUUID?crypto.randomUUID().replace(/-/g,'').slice(0,12):Math.random().toString(36).slice(2,14));
C.clone=o=>JSON.parse(JSON.stringify(o));
C.clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
C.esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
C.PROFILE={id:'oshpark-2l',name:'OSH Park · 2 layer',verified:'2026-09-17',revision:1,source:'https://docs.oshpark.com/services/two-layer/',minTrace:.1524,clearance:.1524,edge:.381,minDrill:.254,minRing:.127,minSlot:.508,minMaskWeb:.1016,minSilk:.127,maskExpansion:.075,minHoleGap:.127,minCutout:1.01,minWidth:6.35,minHeight:6.35,maxWidth:406.4,maxHeight:558.8};
C.keepouts=doc=>doc.keepouts;
C.blank=()=>({app:'COPPERBENCH',schema:C.SCHEMA,version:C.VERSION,id:C.uid('board'),title:'Untitled board',created:new Date().toISOString(),updated:new Date().toISOString(),board:{width:80,height:55,thickness:1.6,shape:'rounded',radius:3,points:[],color:'green'},parts:[],nets:[],traces:[],vias:[],holes:[],cutouts:[],keepouts:[],zones:[],art:[],assets:[],profile:C.clone(C.PROFILE),settings:{grid:1.27,traceWidth:.4,viaDiameter:.9,viaDrill:.4,viaTented:false,zoneStep:.25,autoPlanes:true},assumptions:[{id:C.uid('assume'),text:'Two copper layers; through vias only. This layout does not verify circuit function.',status:'open'}],evidence:[],blockInstances:[],blockLibrary:[],baseline:null});
const pad=(n,x,y,w=1.8,h=w,drill=.9,shape='circle')=>({number:String(n),x,y,w,h,drill,slot:0,shape,layers:drill?'both':'top',net:null});
const foot=(id,name,category,body,pads,extra={})=>({id,name,category,body,pads,ref:'U',value:name,source:'Parametric geometry; check against the selected component datasheet.',verified:false,...extra});
C.LIB=[];
C.LIB.push(foot('r-axial','Resistor · axial 7.62','Through-hole',{kind:'resistor',w:6,h:2.4,z:2.4},[pad(1,-3.81,0),pad(2,3.81,0)],{ref:'R',value:'1k'}));
C.LIB.push(foot('diode','Diode · DO-35 7.62','Through-hole',{kind:'diode',w:4,h:1.9,z:2.1},[pad('K',-3.81,0),pad('A',3.81,0)],{ref:'D',value:'1N4148'}));
C.LIB.push(foot('led5','LED · 5 mm','Through-hole',{kind:'led',w:5,h:5,z:7},[pad('K',-1.27,0),pad('A',1.27,0)],{ref:'D',value:'LED',appearance:'#f06945'}));
C.LIB.push(foot('cap-radial','Capacitor · radial 2.5','Through-hole',{kind:'capacitor',w:5,h:5,z:7.5},[pad('+',-1.25,0),pad('-',1.25,0)],{ref:'C',value:'10uF'}));
C.LIB.push(foot('cap-disc','Capacitor · ceramic 5.0','Through-hole',{kind:'disc',w:6,h:2.4,z:6},[pad(1,-2.5,0),pad(2,2.5,0)],{ref:'C',value:'100nF'}));
for(const n of [2,3,4,6,8,10])C.LIB.push(foot('header'+n,'Header · 1 × '+n,'Connectors',{kind:'header',w:n*2.54,h:2.54,z:5},Array.from({length:n},(_,i)=>pad(i+1,(i-(n-1)/2)*2.54,0,1.8,1.8,1,i===0?'rect':'circle')),{ref:'J',value:'1×'+n+' / 2.54'}));
for(const n of [2,3])C.LIB.push(foot('terminal'+n,'Terminal · '+n+' pin / 5.08','Connectors',{kind:'terminal',w:n*5.08,h:7.4,z:8},Array.from({length:n},(_,i)=>pad(i+1,(i-(n-1)/2)*5.08,0,2.6,2.6,1.2,i===0?'rect':'circle')),{ref:'J',value:'Terminal '+n}));
for(const n of [8,14,16,20]) {let p=[];for(let i=0;i<n/2;i++)p.push(pad(i+1,-3.81,(i-(n/2-1)/2)*2.54));for(let i=0;i<n/2;i++)p.push(pad(n/2+i+1,3.81,((n/2-1)/2-i)*2.54));C.LIB.push(foot('dip'+n,'DIP-'+n+' · 7.62 mm','Integrated circuits',{kind:'ic',w:6.6,h:(n/2)*2.54+1,z:3.6},p,{value:'DIP-'+n}));}
for(const [id,w,h,gap,pw,ph] of [['0603',1.6,.8,1.5,.8,1],['0805',2,1.25,1.9,1,1.4],['1206',3.2,1.6,3.1,1.2,1.8]]) {
 for(const typ of ['R','C']) C.LIB.push(foot(typ+id,typ+' · '+id,'Surface-mount',{kind:typ==='R'?'smd-resistor':'smd-cap',w,h,z:.7},[pad(1,-gap/2,0,pw,ph,0,'rect'),pad(2,gap/2,0,pw,ph,0,'rect')],{ref:typ,value:typ==='R'?'1k':'100nF'}));
}
for(const n of [8,14,16]){let p=[];for(let i=0;i<n/2;i++)p.push(pad(i+1,-2.65,(i-(n/2-1)/2)*1.27,1.8,.65,0,'rect'));for(let i=0;i<n/2;i++)p.push(pad(n/2+i+1,2.65,((n/2-1)/2-i)*1.27,1.8,.65,0,'rect'));C.LIB.push(foot('soic'+n,'SOIC-'+n+' · 1.27 mm','Integrated circuits',{kind:'ic',w:3.9,h:n/2*1.27+.2,z:1.75},p,{value:'SOIC-'+n}));}
C.LIB.push(foot('to92','Transistor · TO-92','Through-hole',{kind:'transistor',w:4.8,h:3.7,z:5},[pad(1,-1.27,0,1.1,1.1,.75),pad(2,0,0,1.1,1.1,.75),pad(3,1.27,0,1.1,1.1,.75)],{ref:'Q',value:'TO-92',source:'Generic straight-lead TO-92. Pin order depends on the device; verify the datasheet.'}));
C.LIB.push(foot('sot23','Transistor · SOT-23','Surface-mount',{kind:'ic',w:1.4,h:2.9,z:1.1},[pad(1,-1, -.95,1,.8,0,'rect'),pad(2,-1,.95,1,.8,0,'rect'),pad(3,1,0,1,.8,0,'rect')],{ref:'Q',value:'SOT-23'}));
C.LIB.push(foot('switch','Pushbutton · 6 mm','Switches',{kind:'switch',w:6,h:6,z:4},[pad(1,-3.25,-2.25,1.8,1.8,1),pad(2,3.25,-2.25,1.8,1.8,1),pad(3,-3.25,2.25,1.8,1.8,1),pad(4,3.25,2.25,1.8,1.8,1)],{ref:'SW',value:'Momentary',source:'Generic four-lead switch; verify mechanical drawing and internally connected pin pairs.'}));
C.LIB.push(foot('testpoint','Test point · 2 mm','Utility',{kind:'testpoint',w:1.2,h:1.2,z:1.5},[pad(1,0,0,2,2,0,'circle')],{ref:'TP',value:'Test point'}));
// Pin roles are explicit metadata, never inferred from net names or numeric pin order.
// Legacy built-ins used literal A/K and +/- pad identities; those identities remain intact.
C.POLARITY={anode:{short:'A',label:'Anode'},cathode:{short:'K',label:'Cathode'},positive:{short:'+',label:'Positive'},negative:{short:'-',label:'Negative'}};
C.polarityRole=(part,a)=>{
 if(a.polarity!==undefined)return C.POLARITY[a.polarity]?a.polarity:null;
 const id=part.libraryId||part.id,key=String(a.number).trim().toUpperCase();
 if(['diode','led5'].includes(id))return key==='A'?'anode':key==='K'?'cathode':null;
 if(id==='cap-radial')return key==='+'?'positive':key==='-'?'negative':null;
 return null;
};
// Printed geometry is independent of the small, contextual editor pin tags.
C.POLARITY_DEFAULTS=Object.freeze({visible:true,size:.9,gap:.7,x:0,y:0});
C.polarityOptions=p=>({...C.POLARITY_DEFAULTS,...p.polaritySilk});
C.polarityMarks=function(p){
 const o=C.polarityOptions(p),roles=p.pads.map((a,index)=>({a,index,role:C.polarityRole(p,a)})).filter(a=>a.role);
 if(!roles.length)return[];
 const cx=roles.reduce((v,r)=>v+r.a.x,0)/roles.length,cy=roles.reduce((v,r)=>v+r.a.y,0)/roles.length;
 const span=axis=>Math.max(...roles.map(r=>r.a[axis]))-Math.min(...roles.map(r=>r.a[axis]));
 const row=roles.length>2&&span('y')<.001,column=roles.length>2&&span('x')<.001;
 const extent=a=>{const angle=(a.rotation||0)*Math.PI/180;return{x:(Math.abs(Math.cos(angle))*a.w+Math.abs(Math.sin(angle))*a.h)/2,y:(Math.abs(Math.sin(angle))*a.w+Math.abs(Math.cos(angle))*a.h)/2};};
 const padX=Math.max(p.body.w/2,...p.pads.map(a=>Math.abs(a.x)+extent(a).x)),padY=Math.max(p.body.h/2,...p.pads.map(a=>Math.abs(a.y)+extent(a).y));
 const positions=roles.map(({a,index,role})=>{
  let dx=a.x-cx,dy=a.y-cy;if(Math.hypot(dx,dy)<.00001)dx=role==='anode'||role==='positive'?1:-1;
  let x=a.x,y=a.y,side;
  // More than two terminals in a row (e.g. RGB LEDs) get one aligned legend
  // row, not several overprinted A/K glyphs at each end of the body.
  if(row){side=cy<0?'top':'bottom';y=(cy<0?-1:1)*(padY+o.gap+o.size/2);}
  else if(column){side=cx<0?'left':'right';x=(cx<0?-1:1)*(padX+o.gap+o.size/3);}
  else if(Math.abs(dx)>=Math.abs(dy)){side=dx<0?'left':'right';x=Math.sign(dx)*(padX+o.gap+o.size/3);}
  else{side=dy<0?'top':'bottom';y=Math.sign(dy)*(padY+o.gap+o.size/2);}
  return{a,index,role,x,y,side};
 });
 // Preserve terminal order while keeping separate glyphs apart, including
 // when the user chooses a large print size. Only silk positions are changed.
 for(const side of ['left','right','top','bottom']){
  const axis=['left','right'].includes(side)?'y':'x',gap=(axis==='x'?o.size*2/3:o.size)+.41,items=positions.filter(a=>a.side===side).sort((a,b)=>a[axis]-b[axis]||a.index-b.index);
  if(items.length<2)continue;
  const before=items.reduce((v,a)=>v+a[axis],0)/items.length;
  for(let i=1;i<items.length;i++)items[i][axis]=Math.max(items[i][axis],items[i-1][axis]+gap);
  const delta=items.reduce((v,a)=>v+a[axis],0)/items.length-before;
  for(const a of items)a[axis]-=delta;
 }
 return positions.map(({a,index,role,x,y})=>{
  const center={x:x+o.x,y:y+o.y},pos=C.world(p,{x:center.x-o.size/3,y:center.y-o.size/2});
  return {...C.POLARITY[role],role,index,padId:p.id+':'+index,pad:C.world(p,a),center:C.world(p,center),local:center,x:pos.x,y:pos.y,size:o.size,rotation:p.rotation,layer:p.side,owner:p.id,width:.16,visible:o.visible};
 });
};
for(const f of C.LIB)for(const a of f.pads){const role=C.polarityRole(f,a);if(role)a.polarity=role;}
C.makePart=(doc,libraryId,x,y)=>{let f=typeof libraryId==='string'?C.LIB.find(x=>x.id===libraryId):libraryId;if(!f)throw Error('Unknown footprint');let p=C.clone(f);p.libraryId=p.id;p.id=C.uid('p');let n=1;while(doc.parts.some(x=>x.ref===f.ref+n))n++;p.ref=f.ref+n;p.x=C.q(x);p.y=C.q(y);p.rotation=0;p.side=f.defaultSide||'top';p.locked=false;p.label=C.clone(f.label||{x:0,y:f.body.h/2+2,size:1.3,visible:true});return p;};
C.world=(part,local)=>{let r=part.rotation*Math.PI/180,x=local.x*(part.side==='bottom'?-1:1),y=local.y;return{x:C.q(part.x+x*Math.cos(r)-y*Math.sin(r)),y:C.q(part.y+x*Math.sin(r)+y*Math.cos(r))};};
C.pads=doc=>doc.parts.flatMap(p=>p.pads.map((a,i)=>({...a,...C.world(p,a),id:p.id+':'+i,partId:p.id,ref:p.ref,pin:a.number,index:i,side:p.side,rotation:p.rotation+(a.rotation||0)*(p.side==='bottom'?-1:1),layers:a.drill?'both':p.side,sourcePad:a,polarityRole:C.polarityRole(p,a),polarityLabel:C.POLARITY[C.polarityRole(p,a)]?.label||null})));
C.getPad=(doc,id)=>C.pads(doc).find(p=>p.id===id);
C.netName=(doc,id)=>doc.nets.find(n=>n.id===id)?.name||'Unassigned';
C.newNet=(doc,name)=>{name=String(name||'NET_'+(doc.nets.length+1)).trim().slice(0,80);let old=doc.nets.find(n=>n.name===name);if(old)return old.id;let net={id:C.uid('n'),name,width:doc.settings.traceWidth};doc.nets.push(net);return net.id;};
C.assignPads=(doc,ids,net,allowMerge=false)=>{const pds=C.pads(doc).filter(p=>ids.includes(p.id)),old=[...new Set(pds.map(p=>p.net).filter(Boolean))];if(old.some(n=>n!==net)&&!allowMerge)throw Error('These pins belong to different nets. Explicitly merge the nets or cancel.');if(allowMerge){for(const n of old.filter(n=>n!==net)){doc.parts.forEach(p=>p.pads.forEach(a=>{if(a.net===n)a.net=net}));for(const group of [doc.traces,doc.vias,doc.zones])group.forEach(x=>{if(x.net===n)x.net=net});doc.nets=doc.nets.filter(x=>x.id!==n);}}for(const p of pds)p.sourcePad.net=net;return net;};
C.reference=(doc,id)=>{const p=C.getPad(doc,id);return p?p.ref+'.'+p.pin:id;};
C.snapshot=doc=>{const s=C.clone(doc);s.baseline=null;return s;};
C.compare=(doc,base)=>{if(!base)return[];let out=[];for(const key of ['parts','traces','vias','holes','cutouts','keepouts','zones','art','nets']){let a=new Map((base[key]||[]).map(x=>[x.id,JSON.stringify(x)])),b=new Map((doc[key]||[]).map(x=>[x.id,JSON.stringify(x)]));for(let [id,v] of b)if(!a.has(id))out.push({kind:'Added',group:key,id});else if(v!==a.get(id))out.push({kind:'Changed',group:key,id});for(let id of a.keys())if(!b.has(id))out.push({kind:'Removed',group:key,id});}if(JSON.stringify(doc.board)!==JSON.stringify(base.board))out.push({kind:'Changed',group:'board',id:'board'});if(JSON.stringify(doc.profile)!==JSON.stringify(base.profile))out.push({kind:'Changed',group:'rules',id:'profile'});return out;};
C.validateDoc=function(input){
 const d=C.clone(input);if(!d||d.app!=='COPPERBENCH'||![1,2,3,4,5].includes(d.schema))throw Error('Unsupported document. Use a COPPERBENCH schema-1, schema-2, schema-3, schema-4 or schema-5 JSON project.');
 d.schema=C.SCHEMA;d.version=C.VERSION; // Older readers must reject schema 5 rather than losing circuit-block records and personal libraries.
 const ids=new Set(), checkId=x=>{if(typeof x.id!=='string'||!x.id||ids.has(x.id))throw Error('Missing or duplicate object identity.');ids.add(x.id);};
 const num=(v,a=-10000,b=10000)=>{if(typeof v!=='number'||!Number.isFinite(v)||v<a||v>b)throw Error('Invalid or out-of-range geometry.');};
 const xy=p=>{num(p.x);num(p.y);}; const pts=p=>{if(!Array.isArray(p)||p.length>30000)throw Error('Too many or missing polygon vertices.');p.forEach(xy);};
 if(typeof d.title!=='string'||d.title.length>150)throw Error('Invalid project title.');
 if(!d.board||!d.profile||!d.settings)throw Error('Missing board, rules, or settings.');
 num(d.board.width,1,600);num(d.board.height,1,600);num(d.board.thickness,.2,10);num(d.board.radius,0,300);if(!['rect','rounded','circle','polygon'].includes(d.board.shape))throw Error('Unsupported board shape.');pts(d.board.points||[]);
 for(const k of ['parts','nets','traces','vias','holes','cutouts','keepouts','zones','art','assets']){if(!Array.isArray(d[k])||d[k].length>10000)throw Error('Invalid or oversized '+k+' collection.');d[k].forEach(checkId);}
 for(const k of ['minTrace','clearance','edge','minDrill','minRing','minSlot','minMaskWeb','minSilk','maskExpansion','minHoleGap','minCutout'])num(d.profile[k],k==='maskExpansion'?0:.001,10);
 for(const k of ['minWidth','minHeight','maxWidth','maxHeight'])num(d.profile[k],1,1000);
 for(const n of d.nets){if(typeof n.name!=='string'||n.name.length>80)throw Error('Invalid net name.');num(n.width,.01,25);}
 for(const k of ['grid','traceWidth','viaDiameter','viaDrill','zoneStep'])num(d.settings[k],.01,25);
 if(d.settings.autoPlanes===undefined)d.settings.autoPlanes=true;else if(typeof d.settings.autoPlanes!=='boolean')throw Error('Invalid automatic plane refill setting.');
 if(d.settings.viaTented===undefined)d.settings.viaTented=false;else if(typeof d.settings.viaTented!=='boolean')throw Error('Invalid via tenting setting.');
 const netIds=new Set(d.nets.map(n=>n.id)),net=n=>{if(n!==null&&n!==undefined&&!netIds.has(n))throw Error('Geometry references a missing net.');};
 const side=s=>{if(!['top','bottom','both'].includes(s))throw Error('Invalid layer or board side.');};
 for(const p of d.parts){xy(p);num(p.rotation,-36000,36000);side(p.side);if(p.side==='both')throw Error('A part must be on one board face.');if(typeof p.ref!=='string'||typeof p.value!=='string'||!p.body||!Array.isArray(p.pads)||p.pads.length>256)throw Error('Invalid part or footprint.');num(p.body.w,.05,500);num(p.body.h,.05,500);num(p.body.z,.01,150);p.pads.forEach(a=>{xy(a);num(a.w,.01,200);num(a.h,.01,200);num(a.drill,0,50);num(a.slot||0,0,200);if(a.rotation!==undefined)num(a.rotation,-36000,36000);if(a.shape==='circle'&&Math.abs(a.w-a.h)>.0001)throw Error('A circular pad must have equal width and height. Use oval for unequal dimensions.');if(!['circle','rect','oval'].includes(a.shape))throw Error('Unsupported pad shape.');net(a.net);if(a.polarity!==undefined&&!['none','anode','cathode','positive','negative'].includes(a.polarity))throw Error('Invalid pad polarity role.');});if(p.polaritySilk){if(typeof p.polaritySilk!=='object'||Array.isArray(p.polaritySilk))throw Error('Invalid polarity marking options.');const o=C.polarityOptions(p);if(typeof o.visible!=='boolean')throw Error('Invalid polarity visibility.');num(o.size,.6,10);num(o.gap,.2,20);num(o.x,-100,100);num(o.y,-100,100);}if(p.label){xy(p.label);num(p.label.size,.2,30);}}
 for(const t of d.traces){pts(t.points);if(t.points.length<2)throw Error('Trace requires two points.');num(t.width,.01,25);side(t.layer);if(t.layer==='both')throw Error('Trace cannot span both layers.');net(t.net);}
 for(const v of d.vias){xy(v);num(v.diameter,.01,20);num(v.drill,.01,20);net(v.net);if(v.tented!==undefined&&typeof v.tented!=='boolean')throw Error('Invalid via tenting flag.');}
 for(const h of d.holes){if(h.plated)throw Error('Standalone holes must be non-plated. Use a through-hole footprint for plated pads.');xy(h);num(h.drill,.01,100);num(h.slot||0,0,200);num(h.rotation||0,-36000,36000);}
 for(const k of ['cutouts','keepouts','zones'])for(const a of d[k]){pts(a.points);if(a.points.length<3)throw Error(k+' requires a closed polygon.');if(a.layer)side(a.layer);if(k==='zones'){net(a.net);num(a.step||.25,.1,1);num(a.gap||.3,.05,5);num(a.spoke||.4,.05,5);}}
 const planeSides=new Set;for(const z of d.zones){if(z.boardPlane!==undefined&&typeof z.boardPlane!=='boolean')throw Error('Invalid board-plane marker.');if(z.boardPlane){if(!['top','bottom'].includes(z.layer)||planeSides.has(z.layer)||!z.net)throw Error('Each board face can have only one managed plane with an assigned net.');planeSides.add(z.layer);}}
 for(const a of d.art){if(!['text','image','poly','line','rect','circle'].includes(a.kind))throw Error('Unsupported silkscreen object.');xy(a);if(['rect','circle'].includes(a.kind)){num(a.w,.0001,600);num(a.h,.0001,600);}if(a.layer==='both')throw Error('Artwork must be on one face.');num(a.rotation||0,-36000,36000);side(a.layer);num(a.width||.2,.01,25);if(a.kind==='text'){num(a.size,.2,100);if(typeof a.text!=='string'||a.text.length>500)throw Error('Invalid silkscreen text.');}if(a.points)pts(a.points);if(a.rects){if(a.rects.length>50000)throw Error('Image has too much geometry.');for(const r of a.rects){num(r.x);num(r.y);num(r.w,.0001,600);num(r.h,.0001,600);}}}
 for(const a of d.assets)if(typeof a.data!=='string'||a.data.length>16000000||!/^data:image\/(png|jpeg|webp|gif);base64,/.test(a.data))throw Error('Only embedded raster image assets are accepted.');
 d.assumptions=Array.isArray(d.assumptions)?d.assumptions:[];d.evidence=Array.isArray(d.evidence)?d.evidence:[];if(d.baseline){if(d.baseline.document)d.baseline.document=C.validateDoc({...d.baseline.document,baseline:null});else d.baseline=null;}
 return d;
};
C.wizard=function(o){let p=[],n=Math.round(C.clamp(+o.count||2,1,64)),rows=o.rows===2?2:1,pitch=+o.pitch||2.54,rowGap=+o.rowGap||7.62,cols=Math.ceil(n/rows);for(let i=0;i<n;i++){let row=Math.floor(i/cols),col=i%cols;p.push(pad(i+1,(row===1?cols-1-col:col)*pitch-(cols-1)*pitch/2,rows===1?0:(row?1:-1)*rowGap/2,+o.padW||1.8,+o.padH||1.8,o.smd?0:(+o.drill||.9),o.padShape||'circle'));}return foot(C.uid('custom'),o.name||'Custom footprint','Custom',{kind:o.bodyKind||'ic',w:+o.bodyW||Math.max(3,cols*pitch),h:+o.bodyH||Math.max(3,rowGap-1),z:+o.bodyZ||3},p,{ref:o.ref||'U',value:o.name||'Custom',source:o.source||'User-defined; not checked against a datasheet.'});};
C.example=function(which='starter'){
 const d=C.blank();d.title=which==='smd'?'SMD signal breakout':which==='mixed'?'Two-sided sensor carrier':'Little light · learning board';d.board.width=which==='mixed'?82:70;d.board.height=which==='mixed'?56:46;
 function part(lib,x,y,rot=0,val){let p=C.makePart(d,lib,x,y);p.rotation=rot;if(val)p.value=val;d.parts.push(p);return p;}
 function net(name,pairs){let id=C.newNet(d,name);for(const [p,i] of pairs)p.pads[i].net=id;return id;}
 const j=part('terminal2',12,23,90,'5V IN'),r=part('r-axial',31,13,0,'330R'),led=part('led5',49,16,90,'AMBER'),c=part('cap-radial',31,30,0,'10uF'),tp=part('testpoint',53,32,0,'GND');
 net('+5V',[[j,0],[r,0],[c,0]]);net('LED_A',[[r,1],[led,1]]);net('GND',[[j,1],[led,0],[c,1],[tp,0]]);
 for(const [x,y] of [[4,4],[d.board.width-4,4],[4,d.board.height-4],[d.board.width-4,d.board.height-4]])d.holes.push({id:C.uid('h'),x,y,drill:3.2,slot:0,rotation:0,plated:false});
 d.art.push({id:C.uid('a'),kind:'text',text:which==='starter'?'LITTLE LIGHT':'COPPERBENCH',x:23,y:6,size:2.2,width:.25,rotation:0,layer:'top',mirror:false});
 d.art.push({id:C.uid('a'),kind:'text',text:'GSG / REV A',x:25,y:d.board.height-5,size:1.4,width:.2,rotation:0,layer:'top',mirror:false});
 if(which==='smd'){d.parts=[];d.nets=[];let u=part('soic8',34,22,0,'GENERIC IC'),a=part('header4',14,23,90,'INPUT'),b=part('header4',54,23,90,'OUTPUT'),rr=part('R0805',34,10,0,'4k7'),cc=part('C0805',34,35,0,'100nF');for(let i=0;i<4;i++){net('IN_'+(i+1),[[a,i],[u,i]]);net('OUT_'+(i+1),[[b,i],[u,7-i]]);}net('BIAS',[[rr,0],[cc,0]]);}
 if(which==='mixed'){let u=part('dip8',65,24,0,'SOCKET'),r2=part('R1206',58,42,0,'10k');r2.side='bottom';net('SENSE',[[u,0],[r2,0]]);d.art.push({id:C.uid('a'),kind:'text',text:'BOTTOM',x:68,y:49,size:1.5,width:.2,rotation:0,layer:'bottom',mirror:false});}
 d.assumptions.push({id:C.uid('assume'),text:'Demonstration only. Library geometries and pin functions must be checked against purchased parts.',status:'open'});return d;
};
if(typeof module!=='undefined')module.exports=C;
})(typeof self!=='undefined'?self:globalThis);

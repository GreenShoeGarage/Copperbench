/* COPPERBENCH platform interfaces, revision 1.
 * Source-derived NOMINAL mating geometry, not fabricated/certified hardware.
 * All design coordinates below are the new PCB's TOP VIEW. USB is at the left
 * for Arduino templates; Pi GPIO is along the top, physical pin 1 lower-left.
 * Add-on parts mirror their LOCAL x coordinates AND start on the bottom face:
 * world coordinates therefore match the top-view drawing (exactly one mirror).
 * Host illustrations and pin captions are editor-only, never copper or silk.
 * See docs/FORM_FACTORS.md for sources, limits, and per-family qualification.
 */
(function(root){'use strict';
const C=root.CB,G=C.G,P=C.Platforms={revision:1};
const point=(x,y)=>({x:C.q(x),y:C.q(y)});
const sources={
 pi:['https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-mechanical-drawing.pdf','https://datasheets.raspberrypi.com/hat/hat-plus-specification.pdf','https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#gpio-and-the-40-pin-header'],
 uno:['https://docs.arduino.cc/resources/pinouts/A000066-full-pinout.pdf','https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf','https://raw.githubusercontent.com/KiCad/kicad-footprints/master/Module.pretty/Arduino_UNO_R3.kicad_mod'],
 mkr:['https://docs.arduino.cc/resources/pinouts/ABX00012-full-pinout.pdf','https://docs.arduino.cc/resources/datasheets/ABX00023-datasheet.pdf']
};
// Names describe signals, not implicit net assignments. Repeated GND/power
// contacts and aliased signals stay electrically unassigned until the user acts.
const piSignals=[
 '3V3','5V','GPIO2 / SDA1','5V','GPIO3 / SCL1','GND','GPIO4','GPIO14 / TXD',
 'GND','GPIO15 / RXD','GPIO17','GPIO18','GPIO27','GND','GPIO22','GPIO23',
 '3V3','GPIO24','GPIO10 / MOSI','GND','GPIO9 / MISO','GPIO25','GPIO11 / SCLK','GPIO8 / CE0',
 'GND','GPIO7 / CE1','ID_SD / GPIO0','ID_SC / GPIO1','GPIO5','GND','GPIO6','GPIO12',
 'GPIO13','GND','GPIO19','GPIO16','GPIO26','GPIO20','GND','GPIO21'
];
const pin=(number,signal,x,y,bank,first=false)=>({
 number:String(number),signal,bank,x:C.q(x),y:C.q(y),w:1.8,h:1.8,drill:1,
 slot:0,shape:first?'rect':'circle',layers:'both',net:null,
 pinType:signal==='NC'?'nc':signal==='GND'?'ground':['3V3','5V','VIN','IOREF'].includes(signal)?'power':signal.startsWith('ID_')?'reserved':'signal'
});
const piPads=piSignals.map((s,i)=>pin(i+1,s,8.37+Math.floor(i/2)*2.54,i%2===0?4.77:2.23,'GPIO',i===0));
const unoPads=[];
function bank(names,x,y,label,start=1){names.forEach((s,i)=>unoPads.push(pin(label+'.'+(start+i),s,x+i*2.54,y,label,i===0)));}
bank(['NC','IOREF','RESET','3V3','5V','GND','GND','VIN'],27.94,50.8,'POWER');
bank(['A0 / D14','A1 / D15','A2 / D16','A3 / D17','A4 / D18 / SDA','A5 / D19 / SCL'],50.8,50.8,'ANALOG');
// Exact 160 mil discontinuity from D8 to D7; do not snap this row to 2.54 mm.
bank(['SCL / D19','SDA / D18','AREF','GND','D13 / SCK','D12 / MISO','D11 / MOSI','D10 / SS','D9','D8'],18.796,2.54,'DIGITAL10');
bank(['D7','D6','D5','D4','D3','D2','D1 / TX','D0 / RX'],45.72,2.54,'DIGITAL8');
const mkrPads=[];
const mkrBottom=['AREF','A0 / DAC0','A1','A2','A3','A4','A5','A6','D0','D1','D2','D3','D4','D5'];
const mkrTop=['5V','VIN','3V3','GND','RESET','D14 / TX','D13 / RX','D12 / SCL','D11 / SDA','D10 / MISO','D9 / SCK','D8 / MOSI','D7','D6'];
// Nominal WiFi 1010 envelope offset from the dimensioned Arduino user manual;
// 2.54 mm pitch, 20.32 mm row spacing. Absolute edge offsets need actual-board review.
mkrBottom.forEach((s,i)=>mkrPads.push(pin(i+1,s,21.92+i*2.54,22.76,'ANALOG',i===0)));
mkrTop.forEach((s,i)=>mkrPads.push(pin(28-i,s,21.92+i*2.54,2.44,'DIGITAL',i===0)));
P.families=[
 {id:'pi40',title:'Raspberry Pi 40-pin',short:'PI 40',tag:'HAT-layout / carrier',width:65,height:56,shape:'rounded',radius:3,
  pads:piPads,holes:[[3.5,3.5],[61.5,3.5],[3.5,52.5],[61.5,52.5]].map(([x,y])=>({...point(x,y),drill:2.7})),
  color:'#39775b',source:sources.pi,logic:'3.3 V GPIO; 5 V supply contacts are not 5 V-tolerant GPIO.',
  note:'40-pin Raspberry Pi SBC interface only. Not Pico, Compute Module, or the original 26-pin header. A 65 × 56 mm legacy-style outline is a starting shape, not HAT/HAT+ certification.',
  review:['Review connector gender, 1.0 mm drill and 1.8 mm pads against the connector drawing.','Check the selected Pi model, spacer height, cooling, PoE connector and cable clearances. Host illustration is not a clearance model.','HAT+ requires more than this footprint: review ID EEPROM / ID_SD / ID_SC and standby/power rules. No EEPROM or power circuitry is inserted.','Check for 5 V into GPIO, back-powering, supply-current limits, and startup pin states.']},
 {id:'uno-r3',title:'Arduino Uno R3',short:'UNO R3',tag:'Shield / carrier',width:68.58,height:53.34,shape:'polygon',radius:0,
  points:[[0,0],[64.516,0],[66.04,1.524],[66.04,12.954],[68.58,15.494],[68.58,48.26],[66.04,50.8],[66.04,53.34],[0,53.34]].map(([x,y])=>point(x,y)),
  pads:unoPads,holes:[[15.24,2.54],[13.97,50.8],[66.04,17.78],[66.04,45.72]].map(([x,y])=>({...point(x,y),drill:3.2})),
  color:'#187d83',source:sources.uno,logic:'Uno R3 / ATmega328P reference: 5 V I/O. Check IOREF and power direction.',
  note:'32 perimeter contacts (8 power + 6 analog + 10 + 8 digital). USB-left top view. The 4.064 mm D8–D7 gap is intentional. No ICSP 2×3 header or R4-specific features are included.',
  review:['Verify the selected Uno R3 or clone against the nominal header and mounting-hole coordinates before ordering.','Choose male / stackable shield headers; check tail length, spacer height, USB-B and barrel-jack clearance.','ICSP is not included. Add and verify it separately when your shield requires an ICSP SPI connection.','No blanket electrical/mechanical compatibility claim for Uno R4, Uno Q, Mega, or third-party clones.']},
 {id:'mkr',title:'Arduino MKR 28-pin',short:'MKR 28',tag:'Shield / carrier',width:61.5,height:25,shape:'rounded',radius:2,
  pads:mkrPads,holes:[[2.31,2.31],[59.19,2.31],[2.31,22.69],[59.19,22.69]].map(([x,y])=>({...point(x,y),drill:2.25})),
  color:'#187d83',source:sources.mkr,logic:'MKR reference: 3.3 V I/O, not 5 V tolerant. Verify variant power-pin behavior.',
  note:'Two 14-way rows, 2.54 mm pitch, 20.32 mm apart. Nominal 61.5 × 25 mm WiFi 1010 reference envelope. Board-to-edge and hole offsets are review-required, not universal across MKR variants.',
  review:['Confirm the exact MKR variant. Connector pattern does not guarantee body size, hole locations, antenna clearance or pin behavior.','Verify nominal 21.92 / 2.44 mm header offsets and optional 2.25 mm mounting holes on the real board.','Check 3.3 V GPIO, USB / VIN / 5V power direction, battery connector access and RF antenna keepout.','Select mating sockets for a carrier or stacking headers for a shield; verify drill and engagement length.']}
];
P.get=id=>{const f=P.families.find(x=>x.id===id);if(!f)throw Error('Unknown platform family: '+id);return f;};
P.footprint=function(id,role='addon'){
 const f=P.get(id);if(!['addon','carrier'].includes(role))throw Error('Unknown mating role.');
 const sign=role==='addon'?-1:1;
 const local=a=>({...a,x:C.q((a.x-f.width/2)*sign),y:C.q(a.y-f.height/2)});
 return {id:'platform-'+id+'-'+role,name:f.title+' · '+(role==='addon'?(id==='pi40'?'HAT-layout header':'Shield headers'):'Carrier sockets'),category:'Platforms',ref:'J',
 value:f.title+' '+(role==='addon'?'mating headers':'mating sockets'),verified:false,source:f.source.join('\n'),defaultSide:role==='addon'?'bottom':'top',
 body:{kind:'platform',w:f.width,h:f.height,z:2.6},pads:f.pads.map(local),mountingHoles:[],
 platform:{schema:1,family:id,revision:P.revision,role,showHost:true,showPins:true,
  outline:(f.points||G.roundRect(0,0,f.width,f.height,f.radius)).map(local),
  holePattern:f.holes.map(local),geometryStatus:'nominal-review-required',sourceDate:'2026-09-17'},
 label:{x:0,y:0,size:1.3,visible:false}};
};
for(const family of P.families)for(const role of ['addon','carrier'])C.LIB.push(P.footprint(family.id,role));
P.setHoles=function(part,enabled){if(!part.platform)throw Error('Select a platform interface.');part.mountingHoles=enabled?C.clone(part.platform.holePattern):[];part.verified=false;};
// Mounting holes move, rotate and flip WITH the compound interface. Unlike host
// ghost geometry these are real NPTH geometry and therefore enter every exporter.
C.mountingHoles=doc=>doc.parts.flatMap(p=>(p.mountingHoles||[]).map((h,i)=>({...h,...C.world(p,h),id:p.id+':mount'+i,partId:p.id,plated:false,slot:0,rotation:0})));
P.template=function(id,{role='addon',holes=true,margin=role==='carrier'?10:0}={}){
 const f=P.get(id);if(!Number.isFinite(margin)||margin<0||margin>100)throw Error('Template margin must be 0–100 mm.');
 const d=C.blank();d.title=f.title+(role==='addon'?(id==='pi40'?' HAT-layout starter':' shield starter'):' carrier starter');
 d.board={...d.board,width:C.q(f.width+margin*2),height:C.q(f.height+margin*2),shape:margin?'rounded':f.shape,radius:margin?3:f.radius,points:margin?[]:C.clone(f.points||[]),color:id==='pi40'?'green':'blue'};
 const p=C.makePart(d,'platform-'+id+'-'+role,f.width/2+margin,f.height/2+margin);p.locked=true;P.setHoles(p,holes);d.parts.push(p);
 d.settings.grid=1.27;d.settings.traceWidth=.4;d.platformTemplate={schema:1,family:id,revision:P.revision,role,margin};
 d.assumptions.push(...[f.logic,f.note,...f.review].map(text=>({id:C.uid('a'),text,status:'open'})));
 d.evidence.push({id:C.uid('e'),text:'Nominal mating geometry transcribed from published pinouts/dimensioned references; no physical fit or manufacturer acceptance verified.',source:f.source.join('\n')});
 return C.validateDoc(d);
};
P.describePad=p=>(p.signal?p.signal+' · ':'')+'Pin '+p.pin;
P.pinCSV=function(part){
 const esc=s=>{let v=String(s??'');if(typeof s==='string'&&/^[=+@-]/.test(v))v="'"+v;return '"'+v.replace(/"/g,'""')+'"';};
 const rows=[['Reference','Contact','Signal','Bank','Type','X mm (top view)','Y mm (top view)','Connector face','Assigned net ID'],
 ...part.pads.map(a=>{const pos=C.world(part,a);return[part.ref,a.number,a.signal||'',a.bank||'',a.pinType||'',pos.x,pos.y,part.side,a.net||''];})];
 return rows.map(row=>row.map(esc).join(',')).join('\r\n')+'\r\n';
};
// Do not assume an import is trustworthy just because its base schema matches.
const baseValidate=C.validateDoc;
C.validateDoc=function(input){
 const d=baseValidate(input),str=(v,max)=>typeof v==='string'&&v.length<=max;
 for(const p of d.parts){
  for(const a of p.pads){if(a.signal!==undefined&&!str(a.signal,160))throw Error('Invalid pin signal label.');if(a.bank!==undefined&&!str(a.bank,80))throw Error('Invalid connector bank label.');}
  const checkPoints=(a,label,max,drill=false)=>{if(!Array.isArray(a)||a.length>max)throw Error('Invalid '+label);for(const q of a){if(!Number.isFinite(q.x)||!Number.isFinite(q.y)||Math.abs(q.x)>1000||Math.abs(q.y)>1000)throw Error('Invalid '+label+' coordinates.');if(drill&&(!Number.isFinite(q.drill)||q.drill<.1||q.drill>30||q.slot))throw Error('Invalid platform mounting-hole diameter.');}};
  if(p.mountingHoles!==undefined)checkPoints(p.mountingHoles,'mounting holes',32,true);
  if(p.platform){const t=p.platform;if(t.schema!==1||!str(t.family,80)||!['addon','carrier'].includes(t.role))throw Error('Unsupported platform metadata version / role.');checkPoints(t.outline,'host reference outline',256);checkPoints(t.holePattern,'reference mounting holes',32,true);if(t.outline.length<3)throw Error('Host reference outline needs three points.');for(const k of ['showHost','showPins'])if(typeof t[k]!=='boolean')throw Error('Invalid platform display option.');}
 }
 return d;
};
// Informational mechanical/electrical review stays separate from ordinary DRC.
const baseFindings=G.findings;
G.findings=function(doc){const f=baseFindings(doc);for(const p of doc.parts.filter(p=>p.platform)){
 const family=P.families.find(x=>x.id===p.platform.family);
 f.push({id:'platform-'+p.id,severity:'warning',code:'platform-review',message:p.ref+': verify host variant, orientation, mating connector and standoff / cable / RF clearances.',objects:[p.id],evidence:family?family.logic+' '+family.note:'Unknown family; using embedded geometry.',confidence:'unverified'});
 if(p.pads.some(a=>a.pinType==='nc'&&a.net))f.push({id:'nc-'+p.id,severity:'warning',code:'platform-nc',message:p.ref+': a reserved NC contact has been assigned to a net.',objects:[p.id],evidence:'Review the official host pinout before routing.',confidence:'certain'});
 }return f;
};
if(typeof module!=='undefined')module.exports=P;
})(typeof self!=='undefined'?self:globalThis);

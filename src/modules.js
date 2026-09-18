/* COPPERBENCH module interfaces.
 * Header/hole coordinates adapted from Adafruit Industries' published Eagle
 * board files, CC BY-SA 3.0. See MODULE-NOTICES.txt and docs/MODULES_AND_BLOCKS.md.
 * Engine and original representative rendering code: MIT.
 * Only the mating header contacts and enabled mounting holes are fabricated.
 */
(function(root){'use strict';
const C=root.CB,G=C.G,M=C.Modules={revision:1,sourceDate:'2026-09-18'};
const source=(repo,file,sha)=>({url:'https://github.com/adafruit/'+repo+'/blob/master/'+encodeURIComponent(file),repo:'adafruit/'+repo,file,blob:sha,license:'CC-BY-SA-3.0',attribution:'Adafruit Industries; Limor Fried / Ladyada and contributors'});
const row=(bank,n,x,y,dx,dy,signals)=>Array.from({length:n},(_,i)=>({number:bank+'.'+(i+1),bank,sourceX:C.q(x+i*dx),sourceY:C.q(y+i*dy),signal:signals[i]}));
M.models=[
 {id:'bme280-original',name:'Adafruit BME280 · original non-QT',short:'BME280',product:'2652 · original non-QT PCB',kind:'sensor',w:17.78,h:19.05,height:3,
 source:source('Adafruit-BME280-Breakout-PCB','Adafruit BME280.brd','e8be40064f9f7a22b5dc45d40247c0025515ec48'),
 pins:row('JP2',7,1.27,2.54,2.54,0,['VIN','3Vo / REGULATOR OUTPUT','GND','SCK / SCL','SDO / ADDRESS','SDI / SDA','CS']),holes:[[2.54,16.51,2.2],[15.24,16.51,2.2]],
 notes:['Original seven-contact board, NOT the later STEMMA QT/BMP280-layout revision.','3Vo is a regulator output; do not confuse it with VIN. Review I²C/SPI mode, address selection and pull-ups.','Header centers and mounting centers reference the named CAD file. Mating header drills are a COPPERBENCH choice, not the module manufacturer land pattern.']},
 {id:'ds3231-original',name:'Adafruit DS3231 RTC · original',short:'DS3231',product:'3013 · original eight-pin PCB, revision A',kind:'rtc',w:22.86,h:17.78,height:4,
 source:source('Adafruit-DS3231-Precision-RTC-Breakout-PCB','Adafruit DS3231 RTC Breakout.brd','7f3413130a6e2a703acb3a75ffbb69ada47d840a'),
 pins:row('JP1',8,2.54,2.54,2.54,0,['VIN / VCC','GND','SCL','SDA','VBAT','32KHZ','SQW','RESET']),holes:[[2.54,15.24,2.5],[20.32,15.24,2.5]],
 notes:['Original eight-contact board, NOT the later STEMMA QT revision.','The CR1220 holder is on the reverse of this PCB. Verify underside space and battery access; the drawing is not a collision model.','VBAT is a backup-battery connection, not a charging output. Review the vendor power and backup-battery guidance.']},
 {id:'oled-096-qt',name:'Adafruit 0.96″ OLED · STEMMA QT',short:'128 × 64 OLED',product:'326 · 0.96in 128x64 OLED STEMMA QT PCB',kind:'display',w:29.21,h:31.75,height:3,mirrorX:true,
 source:source('Adafruit-128x64-Monochrome-OLED-PCB','Adafruit 0.96in 128x64 OLED STEMMA QT.brd','3e15e053ae726248d45ce16f08d1e68f96068661'),
 pins:row('JP2',8,23.495,29.21,-2.54,0,['SDA / MOSI','SCL / SCK','DC / SA0','RESET','CS','3V / REGULATOR OUTPUT','VIN','GND']),holes:[[2.54,29.21,2.5],[26.67,29.21,2.5],[2.54,2.54,2.5],[26.67,2.54,2.5]],
 notes:['Display-face-up interface: source Eagle X is reflected because the display is on the reverse of the source electronics face. Pin identities are retained.','Eight-pin header only. The two on-module JST-SH sockets are NOT additional mating pads on your carrier. Leave room for cables.','Review the module solder-jumper settings for I²C or SPI, reset and address. 3V is not the VIN contact.']},
 {id:'tb6612',name:'Adafruit TB6612 motor-driver breakout',short:'TB6612',product:'2448 · Adafruit TB6612.brd',kind:'motor',w:20.32,h:26.67,height:5,
 source:source('Adafruit-TB6612-Motor-Driver-Breakout-PCB','Adafruit TB6612.brd','17df1afba1d4e98543dde18b57d9bcaed180659d'),
 pins:[...row('JP1',10,2.54,24.765,0,-2.54,['VM / PWRIN','VCC / LOGIC','GND','PWMB','BIN2','BIN1','STBY','AIN1','AIN2','PWMA']),...row('JP3',6,17.78,6.985,0,2.54,['MA1','MA2','GND','GND','MB2','MB1'])],holes:[[16.51,24.13,2.5],[16.51,2.54,2.5]],internalGroups:[['JP1.3','JP3.3','JP3.4']],
 notes:['Mates to JP1 and JP3 only; the module motor-power screw terminal is not fabricated on the carrier.','VM/PWRIN and VCC logic supply are different contacts. No current capability is assigned to these carrier traces or connectors.','Review motor stall current, thermal limits, supply transients, standby behavior and wire/terminal clearance with the vendor guide.']},
 {id:'mpm3610-33',name:'Adafruit MPM3610 · 3.3 V module',short:'MPM3610 · 3V3',product:'4683 · 3.3 V output · revision A PCB',kind:'converter',w:10.16,h:17.145,height:4,
 source:source('Adafruit-MPM3610-PCB','Adafruit MPM3610.brd','3127bb5a8e53b0ef52141bac69a74f3eaf23193d'),
 pins:row('JP1',4,8.89,2.54,-2.54,0,['EN','VIN','3V3 / OUTPUT','GND']),holes:[[5.08,14.605,2.5]],
 notes:['This entry names the 3.3 V assembled module, not the 5 V feedback-resistor variant and not a bare MPM3610 IC.','Verify the purchased module output and permitted input range before connecting it. EN is a control input, not a power contact.','Review cooling, load transients and connector/trace ratings. No simulation or current-carrying guarantee is provided.']}
];
M.local=(m,p)=>({x:C.q((p.x-m.w/2)*(m.mirrorX?-1:1)),y:C.q(m.h/2-p.y)});
for(const m of M.models){
 const f={id:'module-'+m.id,name:m.name,category:'Modules',ref:'M',value:m.short,verified:false,defaultSide:'top',source:m.source.url,
 body:{kind:'module',w:m.w,h:m.h,z:6+1.6+m.height},label:{x:0,y:m.h/2+2,size:1.2,visible:false},mountingHoles:[],
 pads:m.pins.map((p,i)=>({...M.local(m,{x:p.sourceX,y:p.sourceY}),number:p.number,bank:p.bank,signal:p.signal,w:1.8,h:1.8,drill:1,slot:0,shape:i===0?'rect':'circle',layers:'both',net:null})),
 internalGroups:C.clone(m.internalGroups||[]),
 module:{schema:1,model:m.id,product:m.product,kind:m.kind,source:C.clone(m.source),sourceDate:M.sourceDate,showBody:true,stackGap:6,componentHeight:m.height,reviewed:false,
  geometryStatus:'Source-referenced header centers; nominal mating pad sizes and host envelope. Not physically fit-tested.',
  sourceFace:m.mirrorX?'Display face (source X reflected)':'Source Eagle top/component face',
  holePattern:m.holes.map(([x,y,drill])=>({...M.local(m,{x,y}),drill,slot:0,rotation:0})),notes:C.clone(m.notes)}};
 C.LIB.push(f);
}
M.entries=()=>C.LIB.filter(p=>p.module);
M.setHoles=(part,enabled)=>{if(!part.module)throw Error('Select a module interface.');part.mountingHoles=enabled?C.clone(part.module.holePattern):[];};
M.template=function(id,holes=false){const f=M.entries().find(p=>p.id===id);if(!f)throw Error('Unknown module interface.');const d=C.blank();d.title=f.name+' carrier';d.board.width=C.q(f.body.w+14);d.board.height=C.q(f.body.h+14);const p=C.makePart(d,f,d.board.width/2,d.board.height/2);p.locked=true;M.setHoles(p,holes);d.parts.push(p);d.assumptions.push({id:C.uid('assume'),text:'Module is source-referenced, not physically fit-tested. Verify revision, header mating, drills, stack height, component clearance and power requirements.',status:'open'});return d;};
M.example=function(){const d=C.blank();d.title='Module mounting sampler · unconnected';d.board.width=132;d.board.height=68;for(const [i,f]of M.entries().entries()){const p=C.makePart(d,f,14+i*25,32);d.parts.push(p);}return d;};
const validate=C.validateDoc;C.validateDoc=function(input){const d=validate(input);for(const p of d.parts){const m=p.module;if(!m)continue;if(m.schema!==1||typeof m.model!=='string'||typeof m.product!=='string'||!m.source||!/^https:\/\//.test(m.source.url)||typeof m.source.blob!=='string'||!m.source.blob.match(/^[0-9a-f]{40}$/)||!Array.isArray(m.notes)||m.notes.length>30||m.notes.some(n=>typeof n!=='string'||n.length>1000))throw Error('Invalid module identity or reference.');if(typeof m.showBody!=='boolean'||typeof m.reviewed!=='boolean'||typeof m.stackGap!=='number'||!Number.isFinite(m.stackGap)||m.stackGap<0||m.stackGap>50||typeof m.componentHeight!=='number'||!Number.isFinite(m.componentHeight)||m.componentHeight<0||m.componentHeight>50)throw Error('Invalid module fit/display options.');if(!Array.isArray(m.holePattern)||m.holePattern.length>20)throw Error('Invalid module mounting pattern.');for(const h of m.holePattern)if(!Number.isFinite(h.x)||!Number.isFinite(h.y)||Math.abs(h.x)>500||Math.abs(h.y)>500||!Number.isFinite(h.drill)||h.drill<=0||h.drill>20)throw Error('Invalid module hole geometry.');}return d;};
const find=G.findings;G.findings=function(d){const f=find(d);for(const p of d.parts.filter(p=>p.module)){const m=p.module;if(!m.reviewed)f.push({id:'module-review-'+p.id,severity:'warning',code:'module-fit-review',message:p.ref+': review the exact '+m.product+' module and mating connector.',objects:[p.id],confidence:'review-required',evidence:m.geometryStatus+' '+m.notes.join(' ')});const poly=G.rect(-p.body.w/2,-p.body.h/2,p.body.w,p.body.h).map(q=>C.world(p,q));for(const o of d.parts.filter(o=>o.id!==p.id&&o.side===p.side&&o.body.z>m.stackGap)){const q=G.rect(-o.body.w/2,-o.body.h/2,o.body.w,o.body.h).map(q=>C.world(o,q));if(G.polyDist(poly,q)<C.EPS)f.push({id:'module-height-'+p.id+'-'+o.id,severity:'warning',code:'module-height',message:o.ref+' overlaps '+p.ref+' and exceeds its assumed '+m.stackGap+' mm underside gap.',objects:[p.id,o.id],confidence:'approximate',evidence:'Axis-aligned local body envelope projected onto the board. Underside components, cables and sockets require physical review.'});}}return f;};
if(typeof module!=='undefined')module.exports=M;
})(typeof self!=='undefined'?self:globalThis);

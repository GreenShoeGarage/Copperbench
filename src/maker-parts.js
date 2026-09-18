/* COPPERBENCH Everyday Maker Parts, v1.4.
 * Footprints are embedded in each placed part. Library revisions never rewrite
 * saved geometry. Pin names are NOT nets; internalGroups detect conflicts only.
 * Nominal reference land patterns require manufacturer/actual-part review.
 * See docs/MAKER_PARTS.md for source scope, transformations and limitations.
 */
(function(root){'use strict';
const C=root.CB,G=C.G,M=C.Maker={revision:1,sourceDate:'2026-09-18'};
const sources=M.sources={
 ne555:'https://www.ti.com/lit/ds/symlink/ne555.pdf',lm358:'https://www.ti.com/lit/ds/symlink/lm358.pdf',
 hc595:'https://www.ti.com/lit/ds/symlink/sn74hc595.pdf',uln:'https://www.ti.com/lit/ds/symlink/uln2803c.pdf',
 mcp:'https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-MCP23S17-16-Bit-IO-Expander-with-Serial-Interface-DS20001952.pdf',
 lm1117:'https://www.ti.com/lit/ds/symlink/lm1117.pdf',lm7805:'https://www.ti.com/lit/ds/symlink/lm340.pdf',
 npn:'https://www.onsemi.com/pdf/datasheet/2n3904-d.pdf',pnp:'https://www.onsemi.com/pdf/datasheet/2n3906-d.pdf',
 ph:'https://www.jst-mfg.com/product/pdf/eng/ePH.pdf',xh:'https://www.jst-mfg.com/product/pdf/eng/eXH.pdf',sh:'https://www.jst-mfg.com/product/pdf/eng/eSH.pdf',
 qwiic:'https://learn.adafruit.com/introducing-adafruit-stemma-qt',
 usb:'https://gct.co/connector/usb4085',usbLand:'https://github.com/KiCad/kicad-footprints/blob/master/Connector_USB.pretty/USB_C_Receptacle_GCT_USB4085.kicad_mod',
 uno:'https://docs.arduino.cc/resources/pinouts/A000066-full-pinout.pdf'
};
const pad=(number,x,y,w=1.8,h=w,drill=.9,signal='',extra={})=>({number:String(number),x:C.q(x),y:C.q(y),w,h,drill,slot:0,shape:drill?'circle':'rect',layers:drill?'both':'top',net:null,signal,...extra});
const body=(kind,w,h,z)=>({kind,w,h,z});
function add(id,name,category,family,variant,b,pads,opts={}){
 const {manufacturer='',mpn='',refs=[],notes=[],...rest}=opts;
 const f={id:'maker-'+id,name,category,ref:'J',value:name.split(' · ')[0],body:b,pads,verified:false,
 source:refs.length?refs.join('\n'):'COPPERBENCH parametric template. No manufacturer footprint is claimed.',
 catalog:{schema:1,family,variant,manufacturer,mpn,sourceDate:M.sourceDate,sources:refs,notes,
 geometryStatus:refs.length?'reference-review-required':'parametric-review-required',pinNamesEdited:false,reviewed:false},...rest};
 C.LIB.push(f);return f;
}
const pins=(n,pitch=2.54,rows=1)=>Array.from({length:n*rows},(_,i)=>pad(i+1,(Math.floor(i/rows)-(n-1)/2)*pitch,(i%rows-(rows-1)/2)*pitch,1.8,1.8,1,'Pin '+(i+1),{shape:i===0?'rect':'circle'}));
const generic=['Nominal parametric pattern, not a universal manufacturer footprint. Match pitch, hole diameter, pin order, body and mating clearance to the actual component.'];
// Family variants: select the mechanical version before placing, never stretch it.
for(const n of [2,3,4,5,6,8,10,12,16,20])for(const kind of ['header','socket','rightangle']){
 add(`${kind}-1x${n}`,`${kind==='header'?'Male header':kind==='socket'?'Female socket':'Right-angle header'} · 1×${n} · 2.54 mm`,'Connectors','Headers & sockets',`1×${n} ${kind} / 2.54 mm`,body(kind,n*2.54,kind==='rightangle'?7:2.54,kind==='socket'?8.5:6),pins(n),{notes:generic});
}
for(const n of [3,4,5,6,8,10,20])for(const kind of ['header','socket','shrouded']){
 add(`${kind}-2x${n}`,`${kind==='header'?'Dual header':kind==='socket'?'Dual socket':'Keyed shrouded header'} · 2×${n}`,'Connectors','Dual-row headers',`2×${n} ${kind} / 2.54 mm`,body(kind,n*2.54+(kind==='shrouded'?5:0),kind==='shrouded'?8.8:5.08,kind==='socket'?8.5:8),pins(n,2.54,2),{notes:[...generic,'Odd/even numbering across the rows. Verify pin 1 and key / mating direction.']});
}
for(const pitch of [3.5,5.08])for(const n of [2,3,4,5,6,8])add(`terminal-${pitch}-${n}`,`Screw terminal · ${n} poles · ${pitch} mm`,'Connectors','Screw terminals',`${n} poles / ${pitch} mm`,body('terminal',n*pitch,7.5,9),pins(n,pitch).map(p=>({...p,w:pitch===3.5?2.2:2.6,h:pitch===3.5?2.2:2.6,drill:1.2})),{notes:[...generic,'Cable enters the front of the representative housing; allow screwdriver and cable access.']});
for(const [series,pitch,depth,drill] of [['PH',2,4.5,.7],['XH',2.5,5.75,.9]])for(const n of [2,3,4,5,6]){
 add(`jst-${series.toLowerCase()}-${n}`,`JST ${series} · ${n} pins · top entry`,'Connectors','JST cable connectors',`${series} ${n}-pin / ${pitch} mm`,body('jst',(n-1)*pitch+(series==='PH'?3.9:5),depth,series==='PH'?6:7),pins(n,pitch).map(p=>({...p,w:1.6,h:1.6,drill:series==='XH'&&n===2?1:drill})),{
 manufacturer:'JST',mpn:series==='PH'?`B${n}B-PH-K-S`:`B${n}B-XH-A`,refs:[sources[series.toLowerCase()]],notes:['Top-entry nominal no-boss reference. Pin 1 is the marked end; review housing/key orientation against the selected drawing.','PH is 2.00 mm; XH is 2.50 mm (not 2.54 mm). No battery polarity is assumed.']});
}
function shPads(n){return Array.from({length:n},(_,i)=>pad(i+1,i-(n-1)/2,-2.025,.6,1.55,0,'Pin '+(i+1))).concat([pad('MP1',-(n-1)/2-1.3,1.1,1.2,1.8,0,'Mount tab'),pad('MP2',(n-1)/2+1.3,1.1,1.2,1.8,0,'Mount tab')]);}
for(const n of [2,3,4,6])add(`jst-sh-${n}`,`JST SH · ${n} pins · side entry`,'Connectors','JST cable connectors',`SH ${n}-pin / 1 mm / side entry`,body('jst',n+2,4.25,2.95),shPads(n),{manufacturer:'JST',mpn:`SM${String(n).padStart(2,'0')}B-SRSS-TB`,refs:[sources.sh],notes:['Nominal side-entry surface-mount land pattern. Mount tabs are independently selectable; they are not signal contacts.','Review the exact drawing, retention pad position and cable-facing direction.']});
const qt=add('qwiic','Qwiic / STEMMA QT · JST SH 4-pin','Connectors','Sensor connectors','Qwiic / STEMMA QT · side entry',body('jst',6,4.25,2.95),shPads(4),{manufacturer:'JST',mpn:'SM04B-SRSS-TB',refs:[sources.sh,sources.qwiic],notes:['Interface-label preset only: 1 GND, 2 VCC, 3 SDA, 4 SCL. No pull-ups, level shifters or voltage regulator are added.','Confirm voltage, pull-ups and the mating cable. The name does not assign nets.']});
['GND','VCC','SDA','SCL'].forEach((s,i)=>qt.pads[i].signal=s);
// USB4085: chosen because a complete inspectable reference geometry is available.
// Recenter KiCad datum (2.975,4.025). Widen no holes; 0.68 mm signal pads provide
// 0.17 mm spacing at 0.85 mm pitch. Slot dimensions retain source geometry.
const ua=['A1','A4','A5','A6','A7','A8','A9','A12'],ub=['B12','B9','B8','B7','B6','B5','B4','B1'];
const us={A1:'GND',A4:'VBUS',A5:'CC1',A6:'D+',A7:'D-',A8:'SBU1',A9:'VBUS',A12:'GND',B12:'GND',B9:'VBUS',B8:'SBU2',B7:'D-',B6:'D+',B5:'CC2',B4:'VBUS',B1:'GND'};
const usbPads=[...ua.map((n,i)=>pad(n,i*.85-2.975,-4.025,.68,.68,.4,us[n])),...ub.map((n,i)=>pad(n,i*.85-2.975,-2.675,.68,.68,.4,us[n]))];
for(const [i,x,y,travel] of [[1,-1.35,.98,1.5],[2,7.3,.98,1.5],[3,-1.35,4.36,.8],[4,7.3,4.36,.8]])usbPads.push(pad('SH'+i,x-2.975,y-4.025,travel+.9,.9,.6,'Shell',{shape:'oval',slot:travel,rotation:90}));
add('usb-c-usb4085','USB-C · GCT USB4085 · through-hole','Connectors','Power input connectors','USB-C / USB4085 / 16 contacts',body('usb',8.95,9.17,3.31),usbPads,{manufacturer:'GCT',mpn:'USB4085',refs:[sources.usb,sources.usbLand],internalGroups:[['SH1','SH2','SH3','SH4']],notes:['Connector only. CC1/CC2 configuration, power-role control, protection, decoupling and data routing are YOUR circuit. No USB power-delivery behavior is supplied.','Fine 0.85 mm contact pitch; 0.4 mm drills. The reference has 0.6 mm-wide plated shell slots; check manufacturer slot capability.','Reference land geometry recentered; signal pads reduced from 0.70 to 0.68 mm. Independently review this modification.','The mating face is local +Y. Suggested PCB edge is local Y = 2.075 mm. Representative body is not an enforced cable keepout.']});
add('barrel-generic','DC barrel jack · switched · reference','Connectors','Power input connectors','Barrel jack / 3 terminals / nominal',body('barrel',9,14,11),[pad('1',0,-6,3.4,3.4,2.8,'Center'),pad('2',0,0,3.4,3.4,2.8,'Sleeve'),pad('3',5,0,3.4,3.4,2.8,'Sleeve switch')],{notes:[...generic,'Generic switched-jack template, not a PJ-102AH compatibility claim. Center-positive is NOT assumed. Verify switch contact continuity with the actual jack.']});
add('battery-wire','Battery wire pads · labeled + / −','Connectors','Power input connectors','Battery solder pads / 5.08 mm',body('testpoint',7,3,.1),[pad('+',-2.54,0,3,3,1.5,'Battery +',{polarity:'positive'}),pad('-',2.54,0,3,3,1.5,'Battery -',{polarity:'negative'})],{notes:['Wire attachment only, not battery management or a charging circuit. Verify polarity, strain relief, fuse and wire size.']});
// Tactile controls. Generic patterns are explicitly not branded equivalents.
for(const n of [2,4,6,8]){
 const a=pins(n,2.54,2).map(p=>({...p,y:p.y*3,drill:.8,w:1.7,h:1.7,signal:'SW'+(Math.floor((+p.number-1)/2)+1)+' '+((+p.number)%2?'A':'B')}));
 add('dip-switch-'+n,`DIP switch · ${n} positions`,'Controls','Switches',`${n}-position DIP / 7.62 mm rows`,body('dipswitch',n*2.54+2,6.8,4),a,{ref:'SW',notes:[...generic,'Pairs are numbered 1–2, 3–4, etc. These contacts are NOT shorted in the design model; switch state is not simulated.']});
}
add('slide-spdt','Slide switch · SPDT · 2.54 mm','Controls','Switches','SPDT slide / three pins',body('slide',8.6,4,5),pins(3).map((p,i)=>({...p,signal:['Throw 1','Common','Throw 2'][i]})),{ref:'SW',notes:[...generic,'Center pin is the common in this template. Verify the purchased switch; no position-dependent connection is modeled.']});
for(const size of [6,12])add('button-'+size,`Pushbutton · ${size} mm · 4 leads`,'Controls','Switches',`${size} mm momentary / 4 leads`,body('switch',size,size,5),[pad(1,-size/2-.25,-size*.375,1.8,1.8,.9,'Contact A1'),pad(2,-size/2-.25,size*.375,1.8,1.8,.9,'Contact A2'),pad(3,size/2+.25,-size*.375,1.8,1.8,.9,'Contact B1'),pad(4,size/2+.25,size*.375,1.8,1.8,.9,'Contact B2')],{ref:'SW',internalGroups:[['1','2'],['3','4']],notes:[...generic,'Assumed common pairs: left pair 1–2, right pair 3–4. Verify actual switch with a continuity meter. A/B is momentary, not automatically joined.']});
add('trimmer','Trimmer potentiometer · triangular','Controls','Potentiometers & encoders','Trimmer / 2.54 mm triangular',body('trimmer',6.5,6.5,5),[pad(1,-2.54,1.27,1.8,1.8,.8,'End 1'),pad(2,0,-1.27,1.8,1.8,.8,'Wiper'),pad(3,2.54,1.27,1.8,1.8,.8,'End 2')],{ref:'RV',value:'10k',notes:[...generic,'Terminal 2 is the wiper. Rotation direction depends on the selected device.']});
add('rotary-pot','Rotary potentiometer · 16 mm reference','Controls','Potentiometers & encoders','Rotary / 16 mm / 5 mm pitch',body('pot',16,16,20),[pad(1,-5,7.5,2.6,2.6,1.2,'End 1'),pad(2,0,7.5,2.6,2.6,1.2,'Wiper'),pad(3,5,7.5,2.6,2.6,1.2,'End 2')],{ref:'RV',value:'10k',notes:[...generic,'No chassis tabs or mechanical fixing holes are assumed. Verify panel fit and shaft clearance.']});
add('encoder','Rotary encoder · push switch · reference','Controls','Potentiometers & encoders','Encoder / A-C-B / push switch',body('encoder',12,12,20),[pad('A',-2.5,-7.5,2,2,1,'Encoder A'),pad('C',0,-7.5,2,2,1,'Encoder common'),pad('B',2.5,-7.5,2,2,1,'Encoder B'),pad('SW1',-2.5,7,2,2,1,'Push switch 1'),pad('SW2',2.5,7,2,2,1,'Push switch 2')],{ref:'SW',mountingHoles:[{x:-6.5,y:0,drill:2},{x:6.5,y:0,drill:2}],notes:[...generic,'Generic encoder pattern; not all EC11 devices share it. Two round fixing holes are included; verify tabs, switch spacing and required slots.']});
// Passive bodies and polarity are meaningful independently of value.
for(const pitch of [5.08,10.16,12.7,15.24])add('resistor-'+pitch,`Axial resistor · ${pitch} mm pitch`,'Passives','Axial resistors',`${pitch} mm lead spacing`,body('resistor',Math.min(pitch-2,9),2.8,2.8),[pad(1,-pitch/2,0),pad(2,pitch/2,0)],{ref:'R',value:'1k',notes:generic});
for(const [dia,pitch,height] of [[6.3,2.5,11],[8,3.5,12],[10,5,16],[12.5,5,20],[16,7.5,25]])add('electrolytic-'+dia,`Polarized capacitor · Ø${dia} · ${pitch} mm pitch`,'Passives','Polarized capacitors',`Ø${dia} / pitch ${pitch} / height ${height}`,body('capacitor',dia,dia,height),[pad(1,-pitch/2,0,2,2,.9,'Positive',{polarity:'positive',shape:'rect'}),pad(2,pitch/2,0,2,2,.9,'Negative',{polarity:'negative'})],{ref:'C',value:'100uF',notes:[...generic,'Value and voltage do not determine a unique can size. Verify diameter, height and lead pitch.']});
for(const [id,name,pitch,w,h] of [['rectifier','Rectifier diode',10.16,5.2,2.7],['schottky','Schottky diode',10.16,5.2,2.7],['zener','Zener diode',7.62,3.9,1.9]])add(id,`${name} · axial reference`,'Power','Diodes & protection',`${name} / ${pitch} mm pitch`,body('diode',w,h,2.8),[pad(1,-pitch/2,0,1.8,1.8,.9,'Cathode',{polarity:'cathode'}),pad(2,pitch/2,0,1.8,1.8,.9,'Anode',{polarity:'anode'})],{ref:'D',notes:[...generic,'Select and verify the exact diode, voltage, current and thermal requirements. A/K identifies terminals, not fixed supply signs.']});
add('tvs-sma','TVS diode · SMA · unidirectional reference','Power','Diodes & protection','SMA unidirectional / nominal',body('smd-diode',4.5,2.8,2.3),[pad(1,-2.4,0,2,2,0,'Cathode',{polarity:'cathode'}),pad(2,2.4,0,2,2,0,'Anode',{polarity:'anode'})],{ref:'D',notes:[...generic,'Unidirectional terminal convention only. Select clamp voltage and surge rating from the chosen manufacturer.']});
add('ptc','Resettable fuse · radial reference','Power','Fuses', 'Radial PTC / 5.08 mm pitch',body('disc',7,2,8),pins(2,5.08),{ref:'F',notes:[...generic,'No hold/trip current is implied. Verify operating temperature, fault current and voltage.']});
add('fuse-holder','Fuse holder · 5×20 mm · reference','Power','Fuses','5×20 mm cartridge / nominal 22.5 mm terminals',body('fuse',26,8,9),pins(2,22.5).map(p=>({...p,w:3,h:3,drill:1.4})),{ref:'F',notes:[...generic,'Generic holder only. Verify contact construction and hole pattern. No mains clearance or safety approval is implied.']});
for(const [id,mpn,key,signals] of [['2n3904','2N3904','npn',['Emitter','Base','Collector']],['2n3906','2N3906','pnp',['Emitter','Base','Collector']]])add(id,`${mpn} · onsemi TO-92`,'Power','Transistors & drivers',`${mpn} / straight leads`,body('transistor',4.8,3.7,5),[-1.27,0,1.27].map((x,i)=>pad(i+1,x,0,1.1,1.1,.75,signals[i])),{ref:'Q',value:mpn,manufacturer:'onsemi',mpn,refs:[sources[key]],notes:['Datasheet terminal order: 1 emitter, 2 base, 3 collector. Straight-lead nominal pattern; verify flat-face orientation and lead-form option.']});
add('mosfet-to220','N-channel MOSFET · G-D-S · TO-220 reference','Power','Transistors & drivers','N-MOSFET / TO-220 / G-D-S',body('to220',10.16,4.6,16),[-2.54,0,2.54].map((x,i)=>pad(i+1,x,0,2,2,1.1,['Gate','Drain / tab','Source'][i])),{ref:'Q',notes:[...generic,'G-D-S is this template’s convention, not every MOSFET. Choose a device with specified on-resistance at your actual gate voltage; no logic-level suitability is claimed.']});
add('relay-spdt','Relay · SPDT · reference','Power','Transistors & drivers','SPDT relay / 5-pin nominal',body('relay',19,15.5,15),[pad('A1',-6,-6,2.5,2.5,1.3,'Coil 1'),pad('A2',-6,6,2.5,2.5,1.3,'Coil 2'),pad('COM',-8,0,2.5,2.5,1.3,'Common'),pad('NC',6,-6,2.5,2.5,1.3,'Normally closed'),pad('NO',6,6,2.5,2.5,1.3,'Normally open')],{ref:'K',notes:[...generic,'Generic relay pattern, NOT a specific Songle/Omron replacement. No switched connectivity, coil suppression or safe mains spacing is automatically supplied.']});
for(const voltage of ['3.3','5.0'])add('lm1117-'+voltage,`LM1117-${voltage} · SOT-223`,'Power','Regulators',`LM1117 fixed ${voltage} V / SOT-223`,body('sot223',6.5,3.5,1.8),[pad(1,-2.3,3.1,1.2,2,0,'GND'),pad(2,0,3.1,1.2,2,0,'VOUT'),pad(3,2.3,3.1,1.2,2,0,'VIN'),pad('TAB',0,-3.1,3.8,2,0,'VOUT / tab')],{ref:'U',value:'LM1117-'+voltage,manufacturer:'Texas Instruments',mpn:'LM1117MP-'+voltage,refs:[sources.lm1117],internalGroups:[['2','TAB']],notes:['Fixed-voltage version: 1 GND, 2 VOUT, 3 VIN; tab is VOUT. Not the adjustable-version pin naming.','Regulator only. Add the required input/output capacitors and verify stability, dropout and dissipation.']});
add('lm7805','LM7805 · TO-220 · upright','Power','Regulators','LM7805 / TO-220 / 5 V',body('to220',10.16,4.6,16),[-2.54,0,2.54].map((x,i)=>pad(i+1,x,0,2,2,1.1,['INPUT','GND / tab','OUTPUT'][i])),{ref:'U',value:'LM7805',manufacturer:'Texas Instruments',mpn:'LM7805CT',refs:[sources.lm7805],notes:['Front-face pin order: input, ground, output. Tab is ground. Nominal upright lead pattern; heatsink clearance is not modeled.','Device only; verify capacitor recommendations, input headroom and thermal dissipation.']});
// Named ICs retain the manufacturer pin numbers and exact package family.
function dip(n){return Array.from({length:n},(_,i)=>pad(i+1,i<n/2?-3.81:3.81,(i<n/2?i:n-1-i)*2.54-(n/2-1)*1.27,1.8,1.8,.9,'',{shape:i===0?'rect':'circle'}));}
function soic(n,wide=false){return Array.from({length:n},(_,i)=>pad(i+1,i<n/2?-(wide?4.7:2.65):(wide?4.7:2.65),(i<n/2?i:n-1-i)*1.27-(n/2-1)*.635,wide?2.1:1.8,.65,0));}
const ics=[
 ['ne555','NE555','NE555P','NE555D',['GND','TRIG','OUT','RESET_N','CONT','THRES','DISCH','VCC'],sources.ne555],
 ['lm358','LM358','LM358P','LM358D',['OUT1','IN1-','IN1+','V-','IN2+','IN2-','OUT2','V+'],sources.lm358],
 ['sn74hc595','SN74HC595','SN74HC595N','SN74HC595D',['QB','QC','QD','QE','QF','QG','QH','GND','QH_SERIAL','SRCLR_N','SRCLK','RCLK','OE_N','SER','QA','VCC'],sources.hc595]
];
for(const [id,name,pdip,psoic,signals,source] of ics)for(const kind of ['dip','soic'])add(id+'-'+kind,`${name} · ${kind==='dip'?'PDIP':'SOIC'}-${signals.length}`,'Named ICs','Named integrated circuits',`${name} / ${kind.toUpperCase()}-${signals.length}`,body('ic',kind==='dip'?6.6:3.9,signals.length/2*(kind==='dip'?2.54:1.27)+.8,kind==='dip'?3.6:1.75),(kind==='dip'?dip(signals.length):soic(signals.length)).map((p,i)=>({...p,signal:signals[i]})),{ref:'U',value:name,manufacturer:'Texas Instruments',mpn:kind==='dip'?pdip:psoic,refs:[source],notes:['Named pin mapping, nominal land pattern. _N denotes active-low. No decoupling or supporting circuit is inserted.']});
const mcpSignals=[...Array.from({length:8},(_,i)=>'GPB'+i),'VDD','VSS','NC','SCL','SDA','NC','A0','A1','A2','RESET_N','INTB','INTA',...Array.from({length:8},(_,i)=>'GPA'+i)];
add('mcp23017','MCP23017-E/SP · SPDIP-28','Named ICs','Named integrated circuits','MCP23017 / narrow 7.62 mm SPDIP-28',body('ic',6.6,35.5,3.8),dip(28).map((p,i)=>({...p,signal:mcpSignals[i],pinType:mcpSignals[i]==='NC'?'nc':'signal'})),{ref:'U',value:'MCP23017',manufacturer:'Microchip',mpn:'MCP23017-E/SP',refs:[sources.mcp],notes:['MCP23017 I2C version, not the MCP23S17 SPI part. NC pins 11 and 14.','DS20001952E: GPA7 and GPB7 are output-only for MCP23017. Verify device revision, address pins, reset and pull-ups.']});
const ulnSignals=[...Array.from({length:8},(_,i)=>(i+1)+'B / IN'),'GND','NC','NC','COM',...Array.from({length:8},(_,i)=>(8-i)+'C / OUT')];
add('uln2803c','ULN2803CDW · SOIC-20 wide','Named ICs','Named integrated circuits','ULN2803C / DW-20 wide',body('ic',7.5,12.8,2.65),soic(20,true).map((p,i)=>({...p,signal:ulnSignals[i],pinType:ulnSignals[i]==='NC'?'nc':'signal'})),{ref:'U',value:'ULN2803C',manufacturer:'Texas Instruments',mpn:'ULN2803CDW',refs:[sources.uln],notes:['C variant uses 20 pins: GND 9, NC 10/11, COM 12. Do not substitute an 18-pin ULN2803A footprint.','COM is the shared clamp-diode terminal, not ground. Review inductive-load and dissipation requirements.']});
// Indicators and debugging.
add('led3','LED · 3 mm · A/K','Indicators','LEDs', '3 mm LED / 2.54 mm pitch',body('led',3,3,5),[pad(1,-1.27,0,1.8,1.8,.9,'Cathode',{polarity:'cathode'}),pad(2,1.27,0,1.8,1.8,.9,'Anode',{polarity:'anode'})],{ref:'D',notes:generic});
for(const [code,w,h,px] of [['0603',1.6,.8,.85],['0805',2,1.25,1.1],['1206',3.2,1.6,1.6]])add('led-'+code,`LED · ${code} · A/K`,'Indicators','LEDs',`${code} SMD LED`,body('smdled',w,h,.9),[pad(1,-px,0,code==='1206'?1.5:1.1,h+.3,0,'Cathode',{polarity:'cathode'}),pad(2,px,0,code==='1206'?1.5:1.1,h+.3,0,'Anode',{polarity:'anode'})],{ref:'D',notes:[...generic,'Check manufacturer cathode index; package marking conventions vary.']});
for(const common of ['anode','cathode'])add('rgb-'+common,`RGB LED · common ${common} · 5 mm`,'Indicators','LEDs',`5 mm RGB / common ${common}`,body('led',5,5,8),[-1.905,-.635,.635,1.905].map((x,i)=>pad(i+1,x,0,1.05,1.05,.7,['Red','Common '+common,'Green','Blue'][i],{polarity:i===1?common:(common==='anode'?'cathode':'anode')})),{ref:'D',notes:[...generic,'Template order R, common, G, B. Verify the exact LED datasheet: four-lead RGB pin orders vary. Separate current limiting is not inserted.']});
add('addressable-led','Addressable RGB LED · 5050 reference','Indicators','LEDs','5050 / VDD-DOUT-GND-DIN reference',body('rgbled',5,5,1.6),[pad(1,-2.5,-1.6,1.6,1.1,0,'VDD'),pad(2,-2.5,1.6,1.6,1.1,0,'DOUT'),pad(3,2.5,1.6,1.6,1.1,0,'GND'),pad(4,2.5,-1.6,1.6,1.1,0,'DIN')],{ref:'D',notes:[...generic,'Generic four-pad reference, not a claim for every WS2812/SK6812 revision. Verify pin order, data direction, signal levels and bypass capacitors.']});
for(const n of [2,3])add('solder-jumper-'+n,`Solder jumper · ${n} pads · open`,'Debug & assembly','Jumpers & test points',`${n}-pad open solder jumper`,body('jumper',n*1.7,2,.08),Array.from({length:n},(_,i)=>pad(i+1,(i-(n-1)/2)*1.7,0,1.3,2,0,n===3&&i===1?'Common':'Pad '+(i+1))),{ref:'JP',notes:['Open copper pads, 0.4 mm gap; no solder bridge or implicit net connection is modeled. Assign deliberately and bridge only during assembly.']});
add('jumper-header','Removable jumper · 2.54 mm · open','Debug & assembly','Jumpers & test points','2-pin header / optional shunt',body('header',5.08,2.54,6),pins(2),{ref:'JP',notes:['Header only. No shunt is modeled as a PCB connection. Verify jumper state during assembly.']});
for(const pitch of [2.54,5.08])add('test-loop-'+pitch,`Wire loop test point · ${pitch} mm`,'Debug & assembly','Jumpers & test points',`Loop / ${pitch} mm pitch`,body('loop',pitch+2,2,5),pins(2,pitch).map((p,i)=>({...p,signal:'Same loop '+(i+1)})),{ref:'TP',internalGroups:[['1','2']],notes:['Both terminals of an installed continuous wire loop are electrically common. Different assigned nets are an error. PCB copper still needs explicit routing.']});
add('ground-clip','Ground clip pad · large','Debug & assembly','Jumpers & test points','Large clip / Ø5 mm pad',body('testpoint',5,5,.15),[pad(1,0,0,5,5,2,'Clip / GND')],{ref:'TP',notes:['GND is a suggestion, not an automatic net assignment. A plated hole and exposed pad are exported; check clip access.']});
M.entries=()=>C.LIB.filter(p=>p.catalog);
M.families=()=>[...new Set(M.entries().map(p=>p.catalog.family))];
M.matches=(part,query)=>[part.name,part.value,part.category,part.catalog?.family,part.catalog?.variant,part.catalog?.manufacturer,part.catalog?.mpn,...part.pads.map(a=>a.signal||'')].join(' ').toLowerCase().includes(String(query||'').toLowerCase());
M.setPinNames=(part,names)=>{if(!Array.isArray(names)||names.length!==part.pads.length||names.some(s=>typeof s!=='string'||s.length>160))throw Error('Each pin needs a text label of at most 160 characters.');part.pads.forEach((p,i)=>p.signal=names[i]);part.verified=false;if(part.catalog){part.catalog.pinNamesEdited=true;part.catalog.reviewed=false;}};
// Uno ICSP reference is transcribed from Adafruit's ARDUINOR3_ICSP board
// numerical coordinates. Eagle Y-up is converted with y=53.34-y.
// Append-only pin IDs protect existing route/net references; no host nets are merged.
M.unoICSP=[['MISO / D12',63.627,22.86],['5V',66.167,22.86],['SCK / D13',63.627,25.4],['MOSI / D11',66.167,25.4],['RESET',63.627,27.94],['GND',66.167,27.94]];
M.hasICSP=p=>p.pads.some(a=>a.bank==='ICSP');
M.setICSP=function(doc,p,enabled){
 if(p.platform?.family!=='uno-r3')throw Error('Select an Arduino Uno R3 interface.');
 if(enabled===M.hasICSP(p))return;
 if(p.pads.length!==32+(M.hasICSP(p)?6:0))throw Error('This interface was customized. Add a separate 2×3 header instead of modifying its pin identities.');
 if(enabled){const sign=p.platform.role==='addon'?-1:1;
  p.pads.push(...M.unoICSP.map(([name,x,y],i)=>pad('ICSP.'+(i+1),(x-34.29)*sign,y-26.67,1.8,1.8,1,name,{bank:'ICSP',shape:i===0?'rect':'circle'})));
 }else{
  const targets=C.pads(doc).filter(a=>a.partId===p.id&&a.bank==='ICSP');
  if(p.pads.slice(32).some(a=>a.net))throw Error('Unassign ICSP nets before removing the header. Existing routing is never deleted automatically.');
  const targetIds=new Set(targets.map(a=>a.id));const otherCopper=G.copper(doc).filter(item=>!targetIds.has(item.owner));
  if(targets.some(a=>otherCopper.some(item=>G.polyDist(G.padPoly(a),item.poly)<.00001)))throw Error('Copper touches an ICSP pad. Remove or reroute it before removing the header.');
  p.pads.splice(32,6);
 }
 p.platform.icsp=enabled;p.verified=false;
};
// Keep the original six platform library items and default templates unchanged.
const originalTemplate=C.Platforms.template;
C.Platforms.template=function(id,opts={}){const d=originalTemplate(id,opts);if(opts.icsp){M.setICSP(d,d.parts[0],true);d.title+=' + ICSP';d.assumptions.push({id:C.uid('a'),text:'Optional Uno ICSP coordinates and 1 mm drills require physical fit review. SPI aliases do not create connections to perimeter pins.',status:'open'});}return C.validateDoc(d);};
M.demo=function(){
 const d=C.blank();d.title='Everyday maker parts — layout sampler';d.board.width=145;d.board.height=102;
 const layout=[['usb-c-usb4085',18,17],['qwiic',43,16],['ne555-dip',68,20],['lm1117-3.3',99,17],['jst-ph-4',125,17],['dip-switch-4',18,49],['trimmer',44,49],['encoder',74,50],['relay-spdt',112,50],['fuse-holder',27,80],['led3',55,83],['led-0805',69,83],['test-loop-5.08',88,83],['terminal-5.08-3',118,83]];
 for(const[id,x,y]of layout)d.parts.push(C.makePart(d,'maker-'+id,x,y));
 d.art.push({id:C.uid('a'),kind:'text',text:'EVERYDAY MAKER PARTS',x:9,y:94,size:2,width:.2,rotation:0,layer:'top'});
 d.assumptions.push({id:C.uid('a'),text:'Unconnected parts sampler, not a functional circuit. Review each actual part and its power/assembly requirements before fabrication.',status:'open'});return d;
};
// Safety checks do not add invisible copper or create nets by label.
const baseValidate=C.validateDoc;
C.validateDoc=function(input){const d=baseValidate(input);for(const p of d.parts){
 if(p.catalog){const m=p.catalog;if(m.schema!==1||typeof m.family!=='string'||m.family.length>100||typeof m.variant!=='string'||m.variant.length>180)throw Error('Invalid maker catalog identity.');for(const key of ['sources','notes'])if(!Array.isArray(m[key])||m[key].length>30||m[key].some(s=>typeof s!=='string'||s.length>3000))throw Error('Invalid maker source notes.');if(m.sources.some(s=>!/^https:\/\/[^\s]+$/.test(s)))throw Error('Maker source links must be HTTPS.');if(new Set(p.pads.map(a=>String(a.number))).size!==p.pads.length)throw Error('Maker footprint pin numbers must be unique.');}
 if(p.internalGroups!==undefined){if(!Array.isArray(p.internalGroups)||p.internalGroups.length>64)throw Error('Invalid internal terminal groups.');for(const group of p.internalGroups)if(!Array.isArray(group)||group.length<2||group.length>256||new Set(group).size!==group.length||group.some(n=>typeof n!=='string'||!p.pads.some(a=>String(a.number)===n)))throw Error('Internal group refers to missing or repeated pin numbers.');}
 if(p.platform?.icsp!==undefined&&(typeof p.platform.icsp!=='boolean'||p.platform.family!=='uno-r3'||p.platform.icsp!==M.hasICSP(p)))throw Error('Invalid Uno ICSP metadata.');
 if(p.pinNamesVisible!==undefined&&typeof p.pinNamesVisible!=='boolean')throw Error('Invalid pin label visibility.');
 }return d;};
const baseFindings=G.findings;
G.findings=function(d){const f=baseFindings(d);for(const p of d.parts){
 for(const group of p.internalGroups||[]){const nets=[...new Set(p.pads.filter(a=>group.includes(String(a.number))).map(a=>a.net).filter(Boolean))];if(nets.length>1)f.push({id:'terminal-conflict-'+p.id+'-'+group.join('-'),severity:'error',code:'internal-terminal-conflict',message:p.ref+': internally common terminals '+group.join(', ')+' have different nets.',objects:[p.id],evidence:'Embedded internalGroups metadata. No invisible PCB connection or automatic net merge is inserted.',confidence:'certain'});}
 if(p.catalog){if(!p.verified)f.push({id:'maker-review-'+p.id,severity:'warning',code:'maker-review',message:p.ref+': review the selected '+p.catalog.variant+' geometry, pin map and assembly clearances.',objects:[p.id],evidence:p.catalog.geometryStatus+'; representative body; no physical fit test.',confidence:'unverified'});
 if(p.pads.some(a=>a.pinType==='nc'&&a.net))f.push({id:'maker-nc-'+p.id,severity:'warning',code:'maker-nc',message:p.ref+': an NC terminal is assigned to a net.',objects:[p.id],evidence:'Review the selected manufacturer pinout. NC must not be inferred from another device variant.',confidence:'certain'});
 } }return f;};
if(typeof module!=='undefined')module.exports=M;
})(typeof self!=='undefined'?self:globalThis);

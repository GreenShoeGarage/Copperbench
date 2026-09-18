/* Developer-only deterministic catalog builder. MIT. No network access. */
const fs=require('fs'),path=require('path'),root=path.resolve(__dirname,'..');
for(const s of ['core','geometry','vias','font','platforms','maker-parts','carriers','router','planes','blocks'])require(path.join(root,'src',s+'.js'));
const C=global.CB;let serial=0;C.uid=p=>p+'-catalog-'+(++serial);
const all=[];
function make(id,name,description,notes,setup){
 const d=C.blank();d.title=name;d.board.width=100;d.board.height=80;const center={x:50,y:40};
 const part=(lib,x,y,rotation=0,value)=>{const p=C.makePart(d,lib,x+center.x,y+center.y);p.rotation=rotation;if(value)p.value=value;p.label.size=1;p.label.y=p.body.h/2+1.2;d.parts.push(p);return p;};
 const net=(name,pairs)=>{const id=C.newNet(d,name);for(const [p,n] of pairs)p.pads[n-1].net=id;return id;};
 const exposed=setup(part,net);let failures=0;
 for(const n of d.nets){const pads=C.pads(d).filter(p=>p.net===n.id);const joined=[pads.shift()];while(pads.length){let best=null;for(const a of joined)for(const b of pads){const dist=C.G.dist(a,b);if(!best||dist<best.dist)best={a,b,dist};}try{const r=C.R.route(d,best.a,best.b,{width:.4,layer:'top',vias:true,step:.4,maxVisited:16000});d.traces.push(...r.traces);d.vias.push(...r.vias);}catch(e){failures++;}joined.push(best.b);pads.splice(pads.indexOf(best.b),1);}}
 const t=C.Blocks.capture(d,[...d.parts,...d.traces,...d.vias].map(p=>p.id),{name,description,notes,origin:center,ports:exposed.map((n,i)=>({key:n,name:n,net:d.nets.find(q=>q.name===n).id,kind:/GND|RETURN/.test(n)?'ground':/VCC|VIN|VOUT/.test(n)?'power':'signal'}))});t.id='block-'+id;t.revision=1;
 const errors=C.G.findings(d).filter(f=>f.severity==='error');console.log(id,'parts',t.parts.length,'traces',t.traces.length,'vias',t.vias.length,'route failures',failures,'errors',errors.map(e=>e.code));if(errors.length)throw Error('Catalog geometry error: '+JSON.stringify(errors));
 all.push(t);
}
make('led','LED indicator','A resistor, a 5 mm LED and a two-pin interface. DRIVE → resistor → anode; cathode → RETURN.',[
 'Example only: 1 kΩ series resistor and generic LED. Check LED forward voltage, GPIO drive limits and resistor power at the actual supply.','No supply voltage or safe current is inferred from a net name. Verify the purchased LED polarity and lead pitch.'
],(p,n)=>{const j=p('header2',-12,0,90,'DRIVE / RETURN'),r=p('r-axial',-2,-6,0,'1k'),led=p('led5',9,3,0,'LED');n('DRIVE',[[j,1],[r,1]]);n('LED_A',[[r,2],[led,2]]);n('RETURN',[[led,1],[j,2]]);return ['DRIVE','RETURN'];});
make('button','Button with pull-up','An active-low pushbutton with a 10 kΩ pull-up and a three-pin interface.',[
 '10 kΩ is a starting value, not a universal requirement. Verify logic voltage, input thresholds and debounce in the receiving circuit.','Generic four-lead switch assumes left pair 1–2 and right pair 3–4 are common; verify the actual switch with a meter. Switch state is not simulated.'
],(p,n)=>{const j=p('header3',-12,0,90,'VCC / SIGNAL / GND'),r=p('R0805',-4,-7,90,'10k'),s=p('maker-button-6',4,0,0,'Momentary NO');n('VCC',[[j,1],[r,1]]);n('SIGNAL',[[j,2],[r,2],[s,1],[s,2]]);n('GND',[[j,3],[s,3],[s,4]]);return ['VCC','SIGNAL','GND'];});
make('i2c','I²C pull-up pair','Two 4.7 kΩ pull-ups, a 100 nF capacitor, and an explicit VCC / GND / SCL / SDA interface.',[
 'Review the combined pull-up resistance of every device on the bus, bus capacitance, speed and voltage before using 4.7 kΩ.','This is not a voltage level shifter. VCC must suit all connected bus devices; firmware and addressing are outside this layout.'
],(p,n)=>{const j=p('header4',-9,0,90,'VCC / GND / SCL / SDA'),r1=p('R0805',0,-4,90,'4.7k'),r2=p('R0805',6,-4,90,'4.7k'),c=p('C0805',6,4,0,'100nF');n('VCC',[[j,1],[r1,1],[r2,1],[c,1]]);n('GND',[[j,2],[c,2]]);n('SCL',[[j,3],[r1,2]]);n('SDA',[[j,4],[r2,2]]);return ['VCC','GND','SCL','SDA'];});
make('decoupling','Supply decoupling pair','A 100 nF ceramic and a 10 µF polarized capacitor across a two-pin supply interface.',[
 'Move the ceramic capacitor close to the actual IC supply pin and keep its return loop short. A prearranged group does not guarantee effective decoupling.','Select capacitor voltage rating, dielectric, ESR, ripple capability and actual footprint; the radial capacitor is a nominal template.'
],(p,n)=>{const j=p('header2',0,-7,0,'VCC / GND'),c=p('C0805',-5,0,0,'100nF'),e=p('cap-radial',5,0,0,'10uF');n('VCC',[[j,1],[c,1],[e,1]]);n('GND',[[j,2],[c,2],[e,2]]);return ['VCC','GND'];});
make('dc-input','Fused, series-diode DC input','A low-voltage DC input template with a resettable fuse, series Schottky diode and bulk capacitor.',[
 'Unqualified low-voltage topology template. Select exact fuse, diode and capacitor ratings for supply voltage, fault current, load, temperature and voltage drop.','Not a mains circuit, surge suppressor, battery charger, regulator, or safety-certified protection design. Trace width is 0.4 mm, NOT a current rating.','Generic PTC and Schottky footprints require actual-part review before ordering. The diode anode faces the input; its cathode feeds VOUT.'
],(p,n)=>{const a=p('header2',-20,0,90,'VIN / RETURN'),f=p('maker-ptc',-10,-7,0,'Select PTC'),di=p('maker-schottky',4,-7,180,'Select Schottky'),c=p('cap-radial',10,4,0,'10uF'),b=p('header2',19,0,90,'VOUT / RETURN');n('VIN',[[a,1],[f,1]]);n('FUSED',[[f,2],[di,2]]);n('VOUT',[[di,1],[c,1],[b,1]]);n('RETURN',[[a,2],[c,2],[b,2]]);return ['VIN','VOUT','RETURN'];});
make('rc-filter','RC input filter','A series 1 kΩ resistor and a 100 nF shunt capacitor, with INPUT / OUTPUT / GND ports.',[
 'Starting values only. Check bandwidth, source impedance, ADC acquisition time, input protection and the load; this is not an anti-aliasing certification.','The PCB layout does not simulate the signal or infer its voltage. Adjust the values and placement for the real receiving circuit.'
],(p,n)=>{const j=p('header3',-10,0,90,'INPUT / OUTPUT / GND'),r=p('R0805',0,-4,0,'1k'),c=p('C0805',4,3,90,'100nF');n('INPUT',[[j,1],[r,1]]);n('OUTPUT',[[j,2],[r,2],[c,1]]);n('GND',[[j,3],[c,2]]);return ['INPUT','OUTPUT','GND'];});
fs.writeFileSync(path.join(root,'src/block-catalog.js'),'/* Generated by tools/build_blocks.js; editable example circuit data. MIT. */\n(function(root){root.CB.BLOCK_CATALOG='+JSON.stringify(all,null,2)+';})(typeof self!=="undefined"?self:globalThis);\n');

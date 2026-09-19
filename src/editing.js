/* COPPERBENCH v1.7 editing transactions. No renderer coordinates or DOM required.
 * Every proposal operates on a clone; the application must check its revision
 * before accepting. Hard-copper connectivity is preserved, not just net names.
 */
(function(root) {
  'use strict';
  const C = root.CB, G = C.G, Edit = C.Edit = {};
  const EPS = .0002;
  const physical = new Set(['short','clearance','copper-edge','keepout','hole-copper',
    'hole-spacing','hole-edge','trace-width','via-ring','pad-ring','drill','slot']);
  const reject = reason => ({ok:false, reason});
  const xy = p => ({x:C.q(p.x), y:C.q(p.y)});
  const same = (a,b) => G.dist(a,b) < EPS;
  const hard = d => { const out=C.clone(d); out.zones=[]; return out; };
  const key = f => f.code+'|'+[...(f.objects||[])].sort().join('|');
  const affected = (id, ids) => ids.has(id) || ids.has(id.split(':')[0]);

  Edit.cleanPoints = function(points) {
    const result=[];
    for (const input of points) {
      const p=xy(input);
      if(result.length && same(result[result.length-1],p)) continue;
      while(result.length>1) {
        const a=result[result.length-2], b=result[result.length-1];
        // Do NOT erase a reversal or fold. Collinear is not enough.
        if(Math.abs(G.cross(a,b,p))>1e-8 ||
          (b.x-a.x)*(p.x-b.x)+(b.y-a.y)*(p.y-b.y)<0) break;
        result.pop();
      }
      result.push(p);
    }
    return result;
  };

  Edit.segment = function(trace, point) {
    let best={index:0,distance:Infinity};
    for(let i=0;i<trace.points.length-1;i++) {
      const d=G.segDist(point,trace.points[i],trace.points[i+1]);
      if(d<best.distance)best={index:i,distance:d};
    }
    return best;
  };

  // Only traces/vias: no plane or wide component pad may turn this selection
  // into an implicit whole-net selection. A separate explicit whole-net action exists.
  Edit.connectedCopper = function(doc,id) {
    const d=hard(doc); d.parts=[];
    const conn=G.connectivity(d), roots=new Set(conn.objectGroups[id]||[]);
    return [...d.traces,...d.vias].filter(o=>(conn.objectGroups[o.id]||[]).some(r=>roots.has(r))).map(o=>o.id);
  };

  function preserveConnections(before,after,removed=new Set()) {
    const a=G.connectivity(hard(before)), b=G.connectivity(hard(after)), groups=new Map;
    for(const [id,roots] of Object.entries(a.objectGroups)) {
      if(removed.has(id))continue;
      for(const r of roots) {if(!groups.has(r))groups.set(r,[]); groups.get(r).push(id);}
    }
    for(const ids of groups.values()) {
      if(ids.length<2)continue;
      let common=new Set(b.objectGroups[ids[0]]||[]);
      for(const id of ids.slice(1))common=new Set((b.objectGroups[id]||[]).filter(r=>common.has(r)));
      if(!common.size)return 'This edit would disconnect existing copper. Keep the junction or use an explicit Move instead.';
    }
    return '';
  }

  Edit.validate = function(before,after,changed,options={}) {
    try {
      C.validateDoc(after);
      const ids=new Set(changed), old=hard(before), next=hard(after);
      const prior=new Set(G.findings(old).filter(f=>f.severity==='error').map(key));
      const failure=G.findings(next).find(f=>f.severity==='error' &&
        (physical.has(f.code) || !prior.has(key(f)) && !['unrouted','zone-stale'].includes(f.code)) &&
        (!prior.has(key(f)) || (f.objects||[]).some(id=>affected(id,ids))));
      if(failure)return reject(failure.message+(failure.evidence?' '+failure.evidence:''));
      if(options.preserve!==false) {
        const reason=preserveConnections(before,after,new Set(options.removed||[]));
        if(reason)return reject(reason);
      }
      for(const z of after.zones)z.fill=null;
      C.Blocks?.sync(after); C.Planes?.sync(after);
      return {ok:true,document:after,changed:[...ids],warnings:after.zones.length?
        ['Copper pours need refilling; plane contacts are checked after refill.']:[]};
    } catch(e) {return reject(e.message);}
  };

  Edit.trace = function(doc,id,operation) {
    try {
      const d=C.clone(doc), t=d.traces.find(t=>t.id===id);
      if(!t)return reject('Select a copper trace first.');
      if(t.locked)return reject('Unlock this trace before editing it.');
      const p=t.points, i=Number(operation.index), n=p.length;
      if(operation.kind!=='clean' && operation.kind!=='replace' &&
        (!Number.isInteger(i)||i<0||i>=n))return reject('Choose an existing trace point or segment.');
      if(operation.kind==='vertex')p[i]=xy(operation.point);
      else if(operation.kind==='insert') {
        if(i>=n-1)return reject('Choose a segment, not the final endpoint.');
        p.splice(i+1,0,xy(operation.point));
      } else if(operation.kind==='remove') {
        if(i===0||i===n-1)return reject('Endpoints are protected. Remove an interior corner or explicitly remove the copper.');
        p.splice(i,1);
      } else if(operation.kind==='slide') {
        if(i>=n-1)return reject('Choose a trace segment.');
        const a=p[i],b=p[i+1],len=G.dist(a,b);
        if(len<EPS)return reject('Clean up this zero-length segment first.');
        const nx=-(b.y-a.y)/len,ny=(b.x-a.x)/len;
        const shift=(operation.point.x-(a.x+b.x)/2)*nx+(operation.point.y-(a.y+b.y)/2)*ny;
        const aa=xy({x:a.x+nx*shift,y:a.y+ny*shift}),bb=xy({x:b.x+nx*shift,y:b.y+ny*shift});
        t.points=[...p.slice(0,i),...(i===0?[p[0]]:[]),aa,bb,...(i===n-2?[p[n-1]]:[]),...p.slice(i+2)];
      } else if(operation.kind==='replace') {
        const a=Number(operation.start),b=Number(operation.end);
        if(!Number.isInteger(a)||!Number.isInteger(b)||a<0||b>=n||b<=a)return reject('Choose ordered start and end points.');
        if(!Array.isArray(operation.points)||operation.points.length>100)return reject('Use at most 100 replacement waypoints.');
        t.points=[...p.slice(0,a+1),...operation.points.map(xy),...p.slice(b)];
      } else if(operation.kind==='clean')t.points=Edit.cleanPoints(p);
      else return reject('Unknown trace operation.');
      if(operation.kind!=='insert'&&operation.kind!=='vertex')t.points=Edit.cleanPoints(t.points);
      if(t.points.length<2)return reject('An edit must leave a trace with two distinct points.');
      if(JSON.stringify(t.points)===JSON.stringify(doc.traces.find(t=>t.id===id).points))return reject('No geometry change is needed.');
      if(operation.previewOnly)return {ok:true,document:d,changed:[id]};
      const result=Edit.validate(doc,d,[id]);
      if(result.ok)result.label=({vertex:'Moved trace corner',insert:'Inserted trace corner',remove:'Removed trace corner',slide:'Slid trace segment',replace:'Replaced trace section',clean:'Cleaned trace'})[operation.kind];
      return result;
    }catch(e){return reject(e.message);}
  };

  Edit.width = function(doc,id,width,scope='trace',segment=0) {
    try {
      if(!Number.isFinite(width)||width<doc.profile.minTrace||width>25)return reject('Choose a width between the profile minimum and 25 mm.');
      const d=C.clone(doc),t=d.traces.find(t=>t.id===id);
      if(!t)return reject('Select a trace first.');
      if(scope==='net'&&!t.net)return reject('Assign a net before changing whole-net width.');
      if(!['trace','segment','connected','net'].includes(scope))return reject('Unknown width scope.');
      const changed=[]; let removed=[];
      if(scope==='segment') {
        if(t.locked)return reject('Unlock the route before changing it.');
        if(!Number.isInteger(segment)||segment<0||segment>=t.points.length-1)return reject('Choose an existing segment.');
        const records=[],start=t.points.slice(0,segment+1),end=t.points.slice(segment+1);
        if(start.length>1)records.push({...C.clone(t),id:C.uid('t'),points:start});
        records.push({...C.clone(t),points:t.points.slice(segment,segment+2),width:C.q(width)});
        if(end.length>1)records.push({...C.clone(t),id:C.uid('t'),points:end});
        d.traces.splice(d.traces.indexOf(t),1,...records);changed.push(...records.map(x=>x.id));
        for(const b of d.blockInstances||[])if(b.members.includes(id))b.members.push(...changed.filter(x=>x!==id));
        // The old polyline is now several owners; fixed neighbouring terminals
        // must still share their original electrical component.
        removed=[id];
      } else {
        const ids=scope==='net'?d.traces.filter(x=>x.net===t.net).map(x=>x.id):scope==='connected'?Edit.connectedCopper(d,id):[id];
        const selected=d.traces.filter(x=>ids.includes(x.id));
        if(selected.some(x=>x.locked))return reject('The selected scope includes locked copper. Unlock it or choose a smaller scope.');
        selected.forEach(x=>{x.width=C.q(width);changed.push(x.id);});
      }
      const result=Edit.validate(doc,d,changed,{removed});
      if(result.ok)result.label='Changed '+scope+' width';return result;
    }catch(e){return reject(e.message);}
  };

  Edit.moveConnected = function(doc,id,target) {
    try {
      const d=C.clone(doc),part=d.parts.find(p=>p.id===id),via=d.vias.find(v=>v.id===id),o=part||via;
      if(!o)return reject('Connected drag supports one component or one via.');
      if(o.locked)return reject('Unlock this object before dragging it.');
      if(!Number.isFinite(target.x)||!Number.isFinite(target.y))return reject('Enter finite coordinates.');
      if(same(o,target))return reject('No position change is needed.');
      const anchors=part?C.pads(doc).filter(p=>p.partId===id):[{...via,layers:'both',w:via.diameter,h:via.diameter,shape:'circle'}];
      if(anchors.some(a=>a.net&&d.zones.some(z=>z.net===a.net&&G.layerMatch(a.layers,z.layer))))
        return reject('A moved terminal shares a net with a copper pour. Use Move, then refill/reconnect the plane. Plane-attached dragging is not supported yet.');
      const attached=[];
      for(const t of doc.traces) {
        const hits=anchors.filter(a=>a.net===t.net&&G.layerMatch(a.layers,t.layer)&&
          t.points.slice(1).some((p,i)=>G.segPolyDist(t.points[i],p,G.padPoly(a))<=t.width/2+.00001));
        if(!hits.length)continue;
        if(t.locked)return reject('An attached trace is locked. Unlock it before connected dragging.');
        const links=[];
        for(const a of hits) {
          const ends=[0,t.points.length-1].filter(i=>same(t.points[i],a));
          if(!ends.length)return reject('A terminal touches the middle or edge of a route. Connected drag currently requires centered trace endpoints.');
          for(let i=1;i<t.points.length-1;i++)if(same(t.points[i],a))return reject('An interior trace junction is not supported by connected drag.');
          ends.forEach(i=>links.push({end:i,anchor:a.id}));
        }
        attached.push({id:t.id,links});
      }
      if(attached.length>24)return reject('Too many attached routes for this local operation. Move fewer connections or use Move.');
      // A via may directly touch a pad or another via. Do not silently pull it
      // away: the preserved connectivity check below will reject that move.
      o.x=C.q(target.x);o.y=C.q(target.y);
      const updated=part?C.pads(d).filter(p=>p.partId===id):[{...via,layers:'both'}];
      const lookup=new Map(updated.map(a=>[a.id,a]));
      const changed=[id], routeIds=new Set(attached.map(a=>a.id));
      const work=hard(d);work.traces=work.traces.filter(t=>!routeIds.has(t.id));
      const bridge=(a,b,t)=>{
        if(same(a,b))return [xy(a)];
        const plan=C.R.route(work,{...a,net:t.net,layers:t.layer},{...b,net:t.net,layers:t.layer},
          {width:t.width,layer:t.layer,vias:false,maxNodes:6000});
        if(plan.error||plan.traces.length!==1||plan.vias.length)throw Error(plan.error||'No same-layer route was found.');
        return plan.traces[0].points;
      };
      for(const attachment of attached) {
        const t=d.traces.find(t=>t.id===attachment.id), points=C.clone(t.points);
        const first=attachment.links.find(a=>a.end===0),last=attachment.links.find(a=>a.end===points.length-1);
        const a=first?lookup.get(first.anchor):points[0], b=last?lookup.get(last.anchor):points[points.length-1];
        if(points.length===2)t.points=bridge(a,b,t);
        else {
          const start=first?bridge(a,points[1],t):points.slice(0,2);
          const finish=last?bridge(points[points.length-2],b,t):points.slice(-2);
          t.points=Edit.cleanPoints([...start,...points.slice(2,-1),...finish.slice(1)]);
        }
        work.traces.push(C.clone(t));changed.push(t.id);
      }
      const result=Edit.validate(doc,d,changed);
      if(result.ok){result.label='Dragged connected '+(part?part.ref:'via');result.adjusted=attached.length;}
      return result;
    }catch(e){return reject(e.message);}
  };

  Edit.markGroups = function(doc,side) {
    const groups=new Map;
    for(const stroke of C.silkStrokes(doc)) {
      if(side&&stroke.layer!==side)continue;
      const part=doc.parts.find(p=>p.id===stroke.owner);
      if(!part)continue;
      const kind=stroke.polarity?'polarity':'reference',id=part.id+'/'+kind;
      if(!groups.has(id))groups.set(id,{id,kind,partId:part.id,object:part,points:[],strokes:[],layer:stroke.layer});
      const group=groups.get(id);group.points.push(...stroke.points);group.strokes.push(stroke);
    }
    return [...groups.values()].map(g=>({...g,bounds:G.bounds(g.points)}));
  };
  Edit.moveMark = function(doc,partId,kind,delta) {
    try {
      const d=C.clone(doc),p=d.parts.find(p=>p.id===partId);
      if(!p||!['reference','polarity'].includes(kind))return reject('Select a printed component marking.');
      if(p.locked)return reject('Unlock this part before moving its marking.');
      const local=G.rotate(delta,-p.rotation);
      if(p.side==='bottom')local.x=-local.x;
      if(kind==='reference'){p.label??={x:0,y:4,size:1.3,visible:true};p.label.x=C.q(p.label.x+local.x);p.label.y=C.q(p.label.y+local.y);}
      else {p.polaritySilk=C.polarityOptions(p);p.polaritySilk.x=C.q(p.polaritySilk.x+local.x);p.polaritySilk.y=C.q(p.polaritySilk.y+local.y);}
      C.validateDoc(d);return {ok:true,document:d,changed:[p.id],label:'Positioned '+kind+' marking',copper:false};
    }catch(e){return reject(e.message);}
  };
  if(typeof module!=='undefined')module.exports=Edit;
})(typeof self!=='undefined'?self:globalThis);

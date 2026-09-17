/* Explicitly regenerate the checked-in starter projects. Not run by tests. */
'use strict';
const fs=require('node:fs'),path=require('node:path');
for(const file of ['core','geometry','font','platforms'])require('../src/'+file+'.js');
const C=globalThis.CB;
for(const family of C.Platforms.families)for(const role of ['addon','carrier']){
 let count=0;C.uid=prefix=>`${family.id}-${role}-${prefix||'id'}-${++count}`;
 const d=C.Platforms.template(family.id,{role});d.created=d.updated='2026-09-17T00:00:00.000Z';
 const filename=family.id+'-'+(role==='addon'?(family.id==='pi40'?'hat':'shield'):'carrier')+'.json';
 fs.writeFileSync(path.join(__dirname,'../examples',filename),JSON.stringify(d,null,2)+'\n');
 console.log(filename);
}

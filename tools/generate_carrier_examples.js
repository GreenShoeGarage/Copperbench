#!/usr/bin/env node
/* Optional deterministic regeneration of the v1.5 blank carrier starters. */
'use strict';
const fs=require('node:fs'),path=require('node:path');
for(const n of ['core','geometry','vias','font','platforms','maker-parts','carriers','router','planes'])require('../src/'+n+'.js');
const C=globalThis.CB,dir=path.join(__dirname,'../examples/carriers');fs.mkdirSync(dir,{recursive:true});
for(const f of C.Carriers.families)for(const role of ['carrier','addon']){let seq=0;C.uid=(prefix='id')=>f.id+'-'+role+'-'+prefix+'-'+String(++seq).padStart(3,'0');const d=C.Platforms.template(f.id,{role,margin:10,holes:true});d.created=d.updated='2026-09-18T00:00:00.000Z';fs.writeFileSync(path.join(dir,f.id+'-'+role+'.json'),JSON.stringify(d,null,2)+'\n');}
console.log('Generated 18 controller header starters. No circuit functionality is implied.');

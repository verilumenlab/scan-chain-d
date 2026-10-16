const fs=require('fs');
const path=require('path');
const root='C:/Users/Mohit/.cursor/projects/d-scan-chain-dianosis-agent/agent-transcripts';
const patterns=[
  'Cannot read properties',
  'toFixed is not a function',
  'Recharts label formatter crash',
  'Unhandled Runtime Error',
  'Minified React error',
  'Type error:',
  'error TS',
];
const hits=[];
function walk(d){
  for(const e of fs.readdirSync(d,{withFileTypes:true})){
    const p=path.join(d,e.name);
    if(e.isDirectory()) walk(p);
    else if(e.name.endsWith('.jsonl')){
      const t=fs.readFileSync(p,'utf8');
      for(const pat of patterns){
        let idx=0;
        while((idx=t.indexOf(pat,idx))!==-1){
          hits.push({file:p.replace(/\\/g,'/').replace(root+'/',''),pat,ctx:t.slice(Math.max(0,idx-80),idx+220)});
          idx+=pat.length;
        }
      }
    }
  }
}
walk(root);
console.log('HITS',hits.length);
for(const h of hits) console.log('\n['+h.file+'] '+h.pat+'\n'+h.ctx.replace(/\n/g,' '));

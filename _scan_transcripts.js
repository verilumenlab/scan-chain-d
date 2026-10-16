const fs=require('fs');
const path=require('path');
const base='C:/Users/Mohit/.cursor/projects/d-scan-chain-dianosis-agent/agent-transcripts/118b7b7b-9b3f-4a00-a2ec-6b3ea70ad157';
const needles=['Cannot read','TypeError','toFixed','formatter','Unhandled Runtime','Something went wrong','Minified React error','labelFormatter','Tooltip'];
function walk(dir,out){
  for (const ent of fs.readdirSync(dir,{withFileTypes:true})){
    const fp=path.join(dir,ent.name);
    if(ent.isDirectory()) walk(fp,out);
    else if(ent.name.endsWith('.jsonl')){
      const lines=fs.readFileSync(fp,'utf8').split('\n');
      lines.forEach((line,i)=>{
        if(!needles.some(n=>line.includes(n))) return;
        if(!/SuspectedCells|Failing Scan|cells_table|SuspectedCellsPanel|Recharts|BarChart|Tooltip/i.test(line) && !/Cannot read|Unhandled Runtime|Minified React/.test(line)) return;
        let snippet=line;
        try{
          const j=JSON.parse(line);
          snippet=JSON.stringify(j);
        }catch{}
        for(const n of needles){
          let idx=0;
          while((idx=snippet.indexOf(n,idx))!==-1){
            out.push({file:path.relative(base,fp),line:i+1,needle:n,ctx:snippet.slice(Math.max(0,idx-100),idx+180)});
            idx+=n.length;
          }
        }
      });
    }
  }
}
const out=[];
walk(base,out);
console.log(JSON.stringify(out,null,2));

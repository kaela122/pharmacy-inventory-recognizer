// Mirrors backend/app/automata/definitions.py so the form can validate live.
const LETTERS = ["M","S","C"];
const isDigit = (c:string) => c>="0" && c<="9";
const inAlpha = (c:string) => LETTERS.includes(c) || isDigit(c);
export const ACCEPT="q4", DEAD="qDead", START="q0";

export function step(s:string, c:string):string{
  if(!inAlpha(c)) return DEAD;
  switch(s){
    case "q0": return LETTERS.includes(c) ? "q1" : DEAD;
    case "q1": return isDigit(c) ? "q2" : DEAD;
    case "q2": return isDigit(c) ? "q3" : DEAD;
    case "q3": return isDigit(c) ? "q4" : DEAD;
    default:   return DEAD;
  }
}
export interface DFAResult{ steps:{c:string;from:string;to:string;ok:boolean}[]; final:string; accepted:boolean; invalid:string[]; }
export function runDFA(code:string):DFAResult{
  let s=START; const steps=[]; const invalid:string[]=[];
  for(const c of code){ const ok=inAlpha(c); if(!ok&&!invalid.includes(c))invalid.push(c);
    const t=step(s,c); steps.push({c,from:s,to:t,ok}); s=t; }
  return { steps, final:s, accepted:s===ACCEPT, invalid };
}
const NAME:Record<string,string> = { M:"Medicine", S:"Supplement", C:"Consumable" };
export function dfaReason(code:string, r:DFAResult):string{
  if(r.accepted) return "valid "+(NAME[code[0]]||"")+" code";
  if(r.invalid.length) return "symbol(s) not in alphabet: "+r.invalid.map(x=>`'${x}'`).join(", ");
  const n=code.length;
  if(!n) return "empty — need a letter + 3 digits";
  if(!LETTERS.includes(code[0])) return "must start with M, S or C";
  for(let i=1;i<Math.min(n,4);i++) if(!isDigit(code[i])) return `symbol ${i+1} must be a digit, found '${code[i]}'`;
  if(n<4) return `too short (${n}) — need exactly 4`;
  return `too long (${n}) — need exactly 4`;
}
export const catName = (letter:string)=> NAME[letter] || "";
export const peso = (n:number)=> "₱"+Number(n).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});

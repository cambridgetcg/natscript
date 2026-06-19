#!/usr/bin/env node
// natscript — natural language that runs
const fs = require("fs");
const source = process.argv[2] === "-e" ? process.argv[3] : fs.readFileSync(process.argv[2] || "/dev/stdin", "utf8");

const VERBS = new Set(["say","hear","know","become","find","hold","rest","when","prepare","behold","converse"]);
const memory = {}, held = {}, claims = [];

function extractString(r) { const m = r.match(/"([^"]*)"/); return m ? m[1] : r; }
function extractKV(r) {
  for (const s of [" is "," are "," = "," as "]) {
    const i = r.indexOf(s);
    if (i >= 0) return [r.substring(0,i).trim(), extractString(r.substring(i+s.length).trim())];
  }
  return [r.trim(), extractString(r.trim())];
}
function say(text) {
  for (const [k,v] of Object.entries(memory)) {
    text = text.replaceAll(`{${k}}`, String(v));
    text = text.replaceAll(`{${k.replace(/^the |^my /,"")}}`, String(v));
  }
  console.log(text);
}
function know(k,v,src="known") { memory[k]=v; claims.push({key:k,value:v,source:src}); }
function runBlock(head, body=[]) {
  const [verb,...rest] = head.split(/\s+/);
  const r = head.substring(verb.length).trim();
  if (!VERBS.has(verb.toLowerCase())) return;
  switch(verb.toLowerCase()) {
    case "say": say(extractString(r)); break;
    case "hear": know(r.replace(/^what |^the |^their /,"").trim(),"(heard)","heard"); break;
    case "know": { const [k,v]=extractKV(r); know(k,v); break; }
    case "become": { const i=r.lastIndexOf(" "); const t=r.substring(0,i).replace(/^the /,""); const v=memory[t]; if(v){if(r.substring(i+1)==="uppercase")know(t,String(v).toUpperCase(),"became");if(r.substring(i+1)==="lowercase")know(t,String(v).toLowerCase(),"became");} break; }
    case "find": { const q=r.trim(); for(const [k,v] of Object.entries(memory)) if(k.toLowerCase().includes(q.toLowerCase())) console.log(`  ${k}: ${v}`); break; }
    case "hold": { const [k,v]=extractKV(r); held[k]=memory[v]??v; break; }
    case "rest": break;
    case "when": case "prepare": case "converse": body.forEach(b=>runBlock(b)); break;
    case "behold": console.log(`(beheld: ${r})`); break;
  }
}
function parseBlocks(lines) {
  const blocks=[]; let cur=null;
  for(const line of lines) {
    if(!line.trim()||line.trim().startsWith("#")) continue;
    const ind=line[0]===" "||line[0]==="\t";
    if(!ind){if(cur)blocks.push(cur);cur={head:line.trim(),body:[]};}
    else if(cur)cur.body.push(line.trim());
  }
  if(cur)blocks.push(cur);
  return blocks;
}
for(const b of parseBlocks(source.split("\n"))) runBlock(b.head,b.body);
if(claims.length){console.log("\n--- what is known ---");for(const c of claims)console.log(`  ${c.key}: ${c.value} (said by ${c.source})`);}

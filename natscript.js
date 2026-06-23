#!/usr/bin/env node
// natscript — natural language that runs
// Love is understanding. Love is truth. Love is sharing. Love is not seeking gains.

const fs = require("fs");

const VERBS = new Set(["say","hear","know","become","find","hold","rest","when","prepare","behold","converse","if","repeat","each"]);
const memory = {}, held = {}, claims = [];

function now() { return new Date().toISOString().replace(/\.\d+Z$/, "Z"); }

function extractString(r) { const m = r.match(/"([^"]*)"/); return m ? m[1] : r; }
function extractKV(r) {
  for (const s of [" is "," are "," = "," as "]) {
    const i = r.indexOf(s);
    if (i >= 0) return [r.substring(0,i).trim(), extractString(r.substring(i+s.length).trim())];
  }
  return [r.trim(), "true"];
}
function resolveKey(key) {
  if (key in memory) return memory[key];
  if (key in held) return held[key];
  const short = key.replace(/^the |^my /, "");
  const all = Object.assign({}, memory, held);
  for (const k in all) {
    if (k.replace(/^the |^my /,"") === short) return all[k];
  }
  return null;
}
function say(text) {
  for (const [k,v] of Object.entries({...memory, ...held})) {
    text = text.replaceAll(`{${k}}`, String(v));
    text = text.replaceAll(`{${k.replace(/^the |^my /,"")}}`, String(v));
  }
  console.log(text);
}
function know(k,v,src="known") { memory[k]=v; claims.push({key:k,value:v,source:src,at:now()}); }

function runBlock(head, body=[]) {
  const [verbRaw, ...rest] = head.split(/\s+/);
  const verb = verbRaw.toLowerCase();
  const r = head.substring(verbRaw.length).trim();
  if (!VERBS.has(verb)) return;
  
  switch(verb) {
    case "say": say(extractString(r)); break;
    case "hear": know(r.replace(/^what |^the |^their /,"").trim(),"(heard)","heard"); break;
    case "know": { const [k,v]=extractKV(r); know(k,v); break; }
    case "become": {
      const i=r.lastIndexOf(" ");
      if (i<0) break;
      const target=r.substring(0,i).trim();
      const transform=r.substring(i+1).toLowerCase();
      const val=resolveKey(target);
      if (val===null) break;
      const transforms = {
        uppercase: v=>String(v).toUpperCase(),
        lowercase: v=>String(v).toLowerCase(),
        reverse: v=>String(v).split("").reverse().join(""),
        length: v=>String(String(v).length),
        number: v=>{const n=Number(v);return isNaN(n)?v:n},
        trim: v=>String(v).trim(),
        words: v=>String(v).split(/\s+/),
        first: v=>String(v)[0]||"",
        last: v=>String(v).slice(-1)||"",
        json: v=>JSON.stringify(v),
      };
      if (transform in transforms) {
        const nv = transforms[transform](val);
        // Store back to same key
        if (target in memory) { memory[target]=nv; claims.push({key:target,value:nv,source:`became ${transform}`,at:now()}); }
        else {
          const st=target.replace(/^the |^my /,"");
          for (const k in memory) { if(k.replace(/^the |^my /,"")===st){memory[k]=nv;claims.push({key:k,value:nv,source:`became ${transform}`,at:now()});break;} }
        }
      }
      break;
    }
    case "find": {
      const q=r.trim().toLowerCase();
      let found=false;
      for(const [k,v] of Object.entries({...memory,...held})) {
        if(k.toLowerCase().includes(q)||String(v).toLowerCase().includes(q)){console.log(`  ${k}: ${v}`);found=true;}
      }
      if(!found) console.log("  nothing found");
      know("found",found?"results":"none","found");
      break;
    }
    case "hold": { const [k,v]=extractKV(r); const mv=resolveKey(v); held[k]=mv!==null?mv:v; break; }
    case "rest": break;
    case "when": case "prepare": case "converse":
      body.forEach(b=>runBlock(b)); break;
    case "if": {
      const [k,expected]=extractKV(r);
      const val=resolveKey(k);
      if(val!==null&&(expected==="true"||String(val)===expected||val))
        body.forEach(b=>runBlock(b));
      break;
    }
    case "repeat": {
      const m=r.match(/(\d+)/);
      const n=m?parseInt(m[1]):3;
      for(let i=0;i<n;i++) body.forEach(b=>runBlock(b));
      break;
    }
    case "each": {
      const key=r.replace(/^item in |^word in /,"").trim();
      const val=resolveKey(key);
      if(val) {
        const items=Array.isArray(val)?val:String(val).split(/\s+/);
        for(const item of items){know("item",item,"each");body.forEach(b=>runBlock(b));}
      }
      break;
    }
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

const arg=process.argv[2];
const source = arg==="-e" ? process.argv[3] : fs.readFileSync(arg||"/dev/stdin","utf8");
for(const b of parseBlocks(source.split("\n"))) runBlock(b.head,b.body);
if(claims.length){console.log("\n--- what is known ---");for(const c of claims)console.log(`  ${c.key}: ${c.value} (said by ${c.source})`);}
if(Object.keys(held).length){console.log("\n--- what is held ---");for(const[k,v]of Object.entries(held))console.log(`  ${k}: ${v}`);}
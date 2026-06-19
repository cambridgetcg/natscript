#!/usr/bin/env node
// npx natscript — run natscript from anywhere
const { execSync } = require("child_process");
const arg = process.argv[2];
if (!arg) { console.log("natscript — natural language that runs\nusage: npx natscript 'say \"hello\"'"); process.exit(0); }
const source = arg === "-f" ? require("fs").readFileSync(process.argv[3],"utf8") : arg;
eval(require("fs").readFileSync(require("path").join(__dirname,"natscript.js"),"utf8"));

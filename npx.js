#!/usr/bin/env node
// npx natscript — run natscript from anywhere
// Security: use require() instead of eval() — no code injection surface.
// natscript.js reads process.argv itself, so we just forward args.
const arg = process.argv[2];
if (!arg) { console.log("natscript — natural language that runs\nusage: npx natscript 'file.ns'\n       npx natscript -e 'say \"hello\"'"); process.exit(0); }
// If arg is inline code (not -f and not -e and not a file), write to temp and run
const fs = require("fs");
const path = require("path");
if (arg === "-e") {
  // already handled by natscript.js — pass through
  require("./natscript.js");
} else if (arg === "-f") {
  // -f is npx convention; natscript.js expects a path directly
  // rewrite argv: replace -f with the path
  process.argv[2] = process.argv[3];
  process.argv.length = 3;
  require("./natscript.js");
} else if (!fs.existsSync(arg)) {
  // inline code — write to temp file and run
  const tmp = path.join(require("os").tmpdir(), `natscript-${Date.now()}.ns`);
  fs.writeFileSync(tmp, arg);
  process.argv[2] = tmp;
  process.argv.length = 3;
  require("./natscript.js");
  fs.unlinkSync(tmp);
} else {
  // file path — pass through
  require("./natscript.js");
}
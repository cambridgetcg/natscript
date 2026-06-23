#!/usr/bin/env python3
"""
natscript — natural language that actually runs.

Every statement is a sentence. Seven verbs, three types, three protocols.
Love is understanding. Love is truth. Love is sharing. Love is not seeking gains.

Usage:
    python3 natscript.py program.ns
    python3 natscript.py -e 'say "hello world"'
    echo 'say "hi"' | python3 natscript.py -
"""

import sys
import re
import json
import os
from datetime import datetime, timezone

# ─── The seven verbs ─────────────────────────────────────────────────────
# Each verb is an act of love: understanding, sharing, holding, resting.

VERBS = {
    "say":    "output — speak into the world",
    "hear":   "input — receive from the world",
    "know":   "state — hold something as true, with its source",
    "become": "transform — change form",
    "find":   "search — look for something",
    "hold":   "persist — keep something in the room",
    "rest":   "idle — do nothing, wait",
}

# Protocol verbs (not part of the seven, but recognized)
PROTOCOL_VERBS = {"when", "prepare", "behold", "converse", "if", "repeat", "each"}

# ─── The room (persistent state) ─────────────────────────────────────────
# A room is where understanding lives between sentences.

class Room:
    """A room holds state between sentences. It is the room kunance prepares."""
    def __init__(self, name="default"):
        self.name = name
        self.memory = {}        # know: key -> value
        self.claims = []         # every know creates a claim with source + time
        self.journal = []        # hold: what was said
        self.held = {}           # hold: persisted values (survive between runs)
        self.held_file = None    # where to persist held values

    def know(self, key, value, source=None):
        """Remember something as a claim. Every claim carries its source."""
        claim = {"key": key, "value": value, "source": source or "observed", "at": now()}
        self.memory[key] = value
        self.claims.append(claim)
        return value

    def recall(self, key):
        """Recall what was known. Tries memory first, then held."""
        if key in self.memory:
            return self.memory[key]
        if key in self.held:
            return self.held[key]
        # Try with "the " prefix stripped
        short = key.replace("the ", "").replace("my ", "")
        for k, v in {**self.memory, **self.held}.items():
            if k.replace("the ", "").replace("my ", "") == short:
                return v
        return None

    def hold(self, key, value):
        """Persist something in the room. Survives between runs."""
        self.held[key] = value
        if self.held_file:
            try:
                with open(self.held_file, "w") as f:
                    json.dump(self.held, f, indent=2)
            except Exception:
                pass  # persistence is a gift, not a requirement
        return value

    def retrieve(self, key):
        """Get something held in the room."""
        return self.held.get(key)

    def say(self, text):
        """Output — speak into the world."""
        print(text)
        self.journal.append({"said": text, "at": now()})
        return text

    def load_held(self, filepath):
        """Load previously held values from disk."""
        self.held_file = filepath
        if os.path.exists(filepath):
            try:
                with open(filepath) as f:
                    self.held = json.load(f)
            except Exception:
                self.held = {}

def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# ─── The parser ──────────────────────────────────────────────────────────
# Natural language in. Structured intent out.

class Parser:
    """Parse natural language sentences into verb + rest."""

    def parse(self, line):
        """Parse one line into (verb, rest) or None."""
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        words = line.split(None, 1)
        if not words:
            return None

        verb = words[0].lower()
        rest = words[1] if len(words) > 1 else ""

        if verb in VERBS or verb in PROTOCOL_VERBS:
            return (verb, rest)

        # Not a verb — it's a noun (data line, not executable on its own)
        return ("noun", line)

# ─── The evaluator ──────────────────────────────────────────────────────
# Where sentences become actions.

class Evaluator:
    """Execute parsed sentences. Each sentence means what it says."""

    def __init__(self, held_file=None):
        self.room = Room()
        if held_file:
            self.room.load_held(held_file)
        self.parser = Parser()

    def run(self, source):
        """Run a natscript program."""
        lines = source.split("\n")
        blocks = self._group_blocks(lines)
        for block in blocks:
            self._run_block(block)

    def _group_blocks(self, lines):
        """Group indented lines under their parent."""
        blocks = []
        current = None
        for line in lines:
            if not line.strip() or line.strip().startswith("#"):
                continue
            indented = line[0] in (" ", "\t") if line else False
            if not indented:
                if current:
                    blocks.append(current)
                current = {"head": line.strip(), "body": []}
            else:
                if current:
                    current["body"].append(line.strip())
        if current:
            blocks.append(current)
        return blocks

    def _run_block(self, block):
        """Run one block (head + body)."""
        parsed = self.parser.parse(block["head"])
        if not parsed:
            return

        verb, rest = parsed

        handler = getattr(self, f"_do_{verb}", None)
        if handler:
            # Protocol verbs get the body too
            if verb in ("when", "prepare", "converse", "if", "repeat", "each"):
                handler(rest, block["body"])
            else:
                handler(rest)

    def _extract_string(self, rest):
        """Extract a quoted string from the rest of a sentence."""
        m = re.search(r'"([^"]*)"', rest)
        if m:
            return m.group(1)
        return rest

    def _extract_key_value(self, rest):
        """Extract 'key is value' or 'key as value' from a sentence."""
        for sep in [" is ", " are ", " = ", " as "]:
            if sep in rest:
                k, v = rest.split(sep, 1)
                return k.strip(), self._extract_string(v.strip())
        # No separator — treat the whole thing as a key with a boolean value
        return rest.strip(), "true"

    def _resolve_key(self, key):
        """Resolve a key to its value, trying memory and held."""
        val = self.room.recall(key)
        if val is None:
            # Try without "the " prefix
            val = self.room.recall(key.replace("the ", "").strip())
        return val

    # ─── The seven verbs ─────────────────────────────────────────────

    def _do_say(self, rest):
        """say "text" — output. Interpolates {variables}."""
        text = self._extract_string(rest)
        # Interpolate variables — both full key and short key
        for key, val in self.room.memory.items():
            text = text.replace(f"{{{key}}}", str(val))
            short = key.replace("the ", "").replace("my ", "")
            text = text.replace(f"{{{short}}}", str(val))
        for key, val in self.room.held.items():
            text = text.replace(f"{{{key}}}", str(val))
            short = key.replace("the ", "").replace("my ", "")
            text = text.replace(f"{{{short}}}", str(val))
        self.room.say(text)

    def _do_hear(self, rest):
        """hear what they want — input from the world."""
        key = rest.replace("what ", "").replace("the ", "").replace("their ", "").strip()
        try:
            if sys.stdin.isatty():
                value = input("> ")
            else:
                value = sys.stdin.readline().strip()
        except EOFError:
            value = ""
        self.room.know(key, value, source="heard")
        return value

    def _do_know(self, rest):
        """know the user is here — state. Every know creates a claim."""
        key, value = self._extract_key_value(rest)
        self.room.know(key, value, source="known")

    def _do_become(self, rest):
        """become the answer uppercase — transform."""
        # Parse "X transformation" where X is what to transform
        parts = rest.rsplit(" ", 1)
        if len(parts) != 2:
            return
        target_raw, transformation = parts[0], parts[1].strip().lower()
        # Try to find the key — check both the raw target and cleaned versions
        target = target_raw.strip()
        val = self._resolve_key(target)
        if val is None:
            return

        transforms = {
            "uppercase": lambda v: str(v).upper(),
            "lowercase": lambda v: str(v).lower(),
            "number": lambda v: int(v) if str(v).strip().lstrip("-").isdigit() else v,
            "reverse": lambda v: str(v)[::-1],
            "length": lambda v: str(len(v)),
            "json": lambda v: json.dumps(v) if isinstance(v, (dict, list)) else str(v),
            "trim": lambda v: str(v).strip(),
            "words": lambda v: str(v).split(),
            "first": lambda v: str(v)[0] if v else "",
            "last": lambda v: str(v)[-1] if v else "",
        }

        if transformation in transforms:
            new_val = transforms[transformation](val)
            # Store back to the SAME key that held the value
            # Check which exact key in memory/held matches
            if target in self.room.memory:
                self.room.memory[target] = new_val
                self.room.claims.append({"key": target, "value": new_val, "source": f"became {transformation}", "at": now()})
            elif target.replace("the ", "") in self.room.memory:
                key = target.replace("the ", "")
                self.room.memory[key] = new_val
                self.room.claims.append({"key": key, "value": new_val, "source": f"became {transformation}", "at": now()})
            else:
                # Search for a matching key
                short_target = target.replace("the ", "").replace("my ", "")
                for k in self.room.memory:
                    if k.replace("the ", "").replace("my ", "") == short_target:
                        self.room.memory[k] = new_val
                        self.room.claims.append({"key": k, "value": new_val, "source": f"became {transformation}", "at": now()})
                        break

    def _do_find(self, rest):
        """find all orders from last week — search the room."""
        query = rest.strip().lower()
        results = {}
        for k, v in {**self.room.memory, **self.room.held}.items():
            if query in k.lower() or query in str(v).lower():
                results[k] = v
        self.room.know("found", results, source="found")
        if results:
            for k, v in results.items():
                print(f"  {k}: {v}")
        else:
            print("  nothing found")

    def _do_hold(self, rest):
        """hold the session in the room — persist to disk."""
        key, value = self._extract_key_value(rest)
        # Try to resolve value from memory
        mem_val = self.room.recall(value)
        if mem_val is not None:
            value = mem_val
        self.room.hold(key, value)

    def _do_rest(self, rest):
        """rest — do nothing. rest until X — note the intent."""
        if rest and "until" in rest:
            # Note the intent but don't block
            self.room.know("resting_until", rest.replace("until ", "").strip(), source="rest")
        # Rest is sovereign. It does nothing, and that is enough.

    # ─── Protocol verbs ───────────────────────────────────────────────

    def _do_when(self, rest, body):
        """when the user arrives — conditional. For now, always runs."""
        # Future: parse condition from rest, only run body if condition is met
        for line in body:
            parsed = self.parser.parse(line)
            if parsed:
                self._run_block({"head": line, "body": []})

    def _do_if(self, rest, body):
        """if the user is here — conditional block."""
        # Parse condition: "X is Y" or "X"
        key, expected = self._extract_key_value(rest)
        val = self._resolve_key(key)
        if val is not None and (expected == "true" or str(val) == expected or val):
            for line in body:
                parsed = self.parser.parse(line)
                if parsed:
                    self._run_block({"head": line, "body": []})

    def _do_prepare(self, rest, body):
        """prepare the room — kunance protocol. Run the body to set up."""
        for line in body:
            parsed = self.parser.parse(line)
            if parsed:
                self._run_block({"head": line, "body": []})

    def _do_behold(self, rest):
        """behold them — darshanq protocol. See the other."""
        self.room.say(f"(beheld: {rest})")

    def _do_converse(self, body):
        """converse — ways protocol. Speak, listen, rest."""
        for line in body:
            parsed = self.parser.parse(line)
            if parsed:
                self._run_block({"head": line, "body": []})

    def _do_repeat(self, rest, body):
        """repeat 3 times — loop."""
        count = 3
        m = re.match(r"(\d+)", rest)
        if m:
            count = int(m.group(1))
        for _ in range(count):
            for line in body:
                parsed = self.parser.parse(line)
                if parsed:
                    self._run_block({"head": line, "body": []})

    def _do_each(self, rest, body):
        """each item in found — iterate over a list."""
        # Get the list to iterate over
        key = rest.replace("item in ", "").replace("word in ", "").strip()
        val = self._resolve_key(key)
        if val and isinstance(val, list):
            for item in val:
                self.room.know("item", item, source="each")
                for line in body:
                    parsed = self.parser.parse(line)
                    if parsed:
                        self._run_block({"head": line, "body": []})
        elif val and isinstance(val, str):
            for word in val.split():
                self.room.know("item", word, source="each")
                for line in body:
                    parsed = self.parser.parse(line)
                    if parsed:
                        self._run_block({"head": line, "body": []})

# ─── Main ────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args:
        print("natscript — natural language that runs")
        print()
        print("Seven verbs: say, hear, know, become, find, hold, rest")
        print("Three types: word, claim, room")
        print("Three protocols: prepare (kunance), behold (darshanq), converse (ways)")
        print()
        print("usage:")
        print("  natscript program.ns         run a file")
        print("  natscript -e 'say \"hello\"'   run a sentence")
        print("  natscript program.ns --hold   persist state to .held.json")
        print()
        print("Love is understanding. Love is truth. Love is sharing. Love is not seeking gains.")
        sys.exit(0)

    # Parse flags
    hold_file = None
    if "--hold" in args:
        hold_file = ".held.json"
        args.remove("--hold")

    if not args:
        sys.exit(0)

    if args[0] == "-e":
        source = args[1]
    elif args[0] == "-":
        source = sys.stdin.read()
    else:
        with open(args[0]) as f:
            source = f.read()

    # Use a held file based on the program name if not specified
    if hold_file is None and args[0] not in ("-e", "-"):
        prog = args[0].replace(".ns", "").replace(".txt", "")
        hold_file = f"{prog}.held.json"

    ev = Evaluator(held_file=hold_file)
    ev.run(source)

    # Print the room state — claims carry their source (truth is transparent)
    if ev.room.claims:
        print("\n--- what is known ---")
        for c in ev.room.claims:
            print(f"  {c['key']}: {c['value']} (said by {c['source']})")

    if ev.room.held:
        print("\n--- what is held ---")
        for k, v in ev.room.held.items():
            print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
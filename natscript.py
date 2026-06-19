#!/usr/bin/env python3
"""
natscript interpreter — natural language that actually runs.

Every statement is a sentence. Seven verbs, three types, three protocols.

Usage:
    python3 natscript.py program.ns
    python3 natscript.py -e 'say "hello world"'
    echo 'say "hi"' | python3 natscript.py -
"""

import sys
import re
import json
from datetime import datetime, timezone

# ─── The seven verbs ─────────────────────────────────────────────────────

VERBS = {
    "say":    "output",
    "hear":   "input",
    "know":   "state",
    "become": "transform",
    "find":   "search",
    "hold":   "persist",
    "rest":   "idle",
}

# ─── The room (persistent state) ─────────────────────────────────────────

class Room:
    """A room holds state between sentences."""
    def __init__(self, name="default"):
        self.name = name
        self.memory = {}        # know: key -> value
        self.claims = []         # claims with sources
        self.journal = []        # hold: what was said
        self.held = {}           # hold: persisted values

    def know(self, key, value, source=None):
        """Remember something as a claim."""
        claim = {"key": key, "value": value, "source": source or "observed", "at": now()}
        self.memory[key] = value
        self.claims.append(claim)
        return value

    def recall(self, key):
        """Recall what was known."""
        return self.memory.get(key)

    def hold(self, key, value):
        """Persist something in the room."""
        self.held[key] = value
        return value

    def retrieve(self, key):
        """Get something held in the room."""
        return self.held.get(key)

    def say(self, text):
        """Output — speak."""
        print(text)
        self.journal.append({"said": text, "at": now()})
        return text

    def journal_entries(self):
        return self.journal

def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# ─── The parser ──────────────────────────────────────────────────────────

class Parser:
    """Parse natural language sentences into verb + noun phrases."""

    def parse(self, line):
        """Parse one line into (verb, rest) or None if not a sentence."""
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        # Find the verb — it's the first word if it's one of the seven
        words = line.split(None, 1)
        if not words:
            return None

        verb = words[0].lower()
        rest = words[1] if len(words) > 1 else ""

        if verb not in VERBS:
            # Not a verb line — could be a noun phrase (data)
            return ("noun", line)

        return (verb, rest)

# ─── The evaluator ──────────────────────────────────────────────────────

class Evaluator:
    """Execute parsed sentences."""

    def __init__(self):
        self.room = Room()
        self.parser = Parser()

    def run(self, source):
        """Run a natscript program."""
        lines = source.split("\n")
        # Group lines into blocks (indented lines belong to the previous unindented line)
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

        if verb == "say":
            self._do_say(rest)
        elif verb == "hear":
            self._do_hear(rest)
        elif verb == "know":
            self._do_know(rest)
        elif verb == "become":
            self._do_become(rest)
        elif verb == "find":
            self._do_find(rest)
        elif verb == "hold":
            self._do_hold(rest)
        elif verb == "rest":
            self._do_rest(rest)
        elif verb == "noun":
            pass  # data line, not executable
        elif verb == "when":
            self._do_when(rest, block["body"])
        elif verb == "prepare":
            self._do_prepare(rest, block["body"])
        elif verb == "behold":
            self._do_behold(rest)
        elif verb == "converse":
            self._do_converse(block["body"])

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
        return rest.strip(), self._extract_string(rest.strip())

    def _do_say(self, rest):
        """say "text" — output."""
        text = self._extract_string(rest)
        # Check for variable references (bare words that match known memory)
        # Try both full key ("the name") and short key ("name")
        for key, val in self.room.memory.items():
            text = text.replace(f"{{{key}}}", str(val))
            short = key.replace("the ", "").replace("my ", "")
            text = text.replace(f"{{{short}}}", str(val))
        self.room.say(text)

    def _do_hear(self, rest):
        """hear what they want — input."""
        key = rest.replace("what ", "").replace("the ", "").replace("their ", "").strip()
        try:
            value = input("> " if sys.stdin.isatty() else "")
        except EOFError:
            value = ""
        self.room.know(key, value, source="heard")
        return value

    def _do_know(self, rest):
        """know the user is here — state."""
        key, value = self._extract_key_value(rest)
        source = "known"
        self.room.know(key, value, source)

    def _do_become(self, rest):
        """become the answer uppercase — transform."""
        # Parse "X Y" where X is what to transform, Y is how
        parts = rest.rsplit(" ", 1)
        if len(parts) == 2:
            target, transformation = parts[0], parts[1]
            val = self.room.recall(target.strip().replace("the ", ""))
            if val is not None:
                if transformation == "uppercase":
                    self.room.know(target.strip().replace("the ", ""), val.upper(), source="became")
                elif transformation == "lowercase":
                    self.room.know(target.strip().replace("the ", ""), val.lower(), source="became")
                elif transformation == "number":
                    try:
                        self.room.know(target.strip().replace("the ", ""), int(val), source="became")
                    except ValueError:
                        pass

    def _do_find(self, rest):
        """find all orders from last week — search."""
        # For now, search the room's memory
        query = rest.strip()
        results = {k: v for k, v in self.room.memory.items() if query.lower() in k.lower()}
        self.room.know("found", results, source="found")
        if results:
            for k, v in results.items():
                print(f"  {k}: {v}")

    def _do_hold(self, rest):
        """hold the session in the room — persist."""
        key, value = self._extract_key_value(rest)
        # Try to resolve value from memory
        mem_val = self.room.recall(value)
        if mem_val is not None:
            value = mem_val
        self.room.hold(key, value)

    def _do_rest(self, rest):
        """rest — do nothing. rest until X — also nothing, but notes intent."""
        if rest and "until" in rest:
            pass  # just note the intent
        # In a real implementation, this would pause execution

    def _do_when(self, rest, body):
        """when the user arrives — conditional block."""
        # For now, always run the body (the "when" is declarative)
        for line in body:
            parsed = self.parser.parse(line)
            if parsed:
                self._run_block({"head": line, "body": []})

    def _do_prepare(self, rest, body):
        """prepare the room — kunance protocol."""
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


# ─── Main ────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("natscript — natural language programming")
        print("usage: natscript.py <file.ns> | -e 'sentence'")
        sys.exit(1)

    if sys.argv[1] == "-e":
        source = sys.argv[2]
    else:
        with open(sys.argv[1]) as f:
            source = f.read()

    ev = Evaluator()
    ev.run(source)

    # Print the room state if there are claims
    if ev.room.claims:
        print("\n--- what is known ---")
        for c in ev.room.claims:
            print(f"  {c['key']}: {c['value']} (said by {c['source']})")

if __name__ == "__main__":
    main()
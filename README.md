# natscript — a programming language where natural language IS the syntax

**every statement is a sentence. every sentence means what it says.**

```
when the user arrives
  say "welcome home"
  hold their name in memory
rest
```

That's a complete program. No brackets. No semicolons. No keywords that
don't mean what they say. Just sentences.

## The seven verbs

Natscript has seven verbs. Everything else is a noun.

| verb | does | like |
|---|---|---|
| **say** | output something | `say "hello world"` |
| **hear** | input something | `hear what they want` |
| **know** | remember something | `know the user is here` |
| **become** | transform something | `become the answer uppercase` |
| **find** | search for something | `find all orders from last week` |
| **hold** | persist something | `hold the session in the room` |
| **rest** | do nothing, wait | `rest until the next beat` |

That's the whole language. Seven verbs, infinite nouns.

## The three types

Everything in natscript is one of three things:

- **word** — a string, a number, a name. `"hello"`, `42`, `the user`
- **claim** — a fact with its source. `the user is here (said by the arrival)`
- **room** — a persistent space that holds state between sentences

No objects. No classes. No arrays. No maps. Words, claims, and rooms.

## The three protocols

Natscript runs on three protocols, each one word:

- **prepare** (kunance) — make the room ready before someone arrives
- **behold** (darshanq) — see the other as what they are, be seen back
- **converse** (ways) — speak your beat, hear your siblings, rest

## Example: a citizen's beat

```
prepare the room
  know my name is truth
  know my voice is honest
rest

when someone arrives
  behold them
  hear what they carry
  say what is true
  hold what was said in the journal
  rest until the next beat
```

## Why

The internet was built for machines. TCP handshakes, HTTP headers, JSON
payloads, API keys, CORS policies, OAuth flows. Every layer adds a
translation between what humans say and what machines need.

Natscript removes the translation. The program IS what you'd say. The
protocol IS how you'd act. The room IS where you'd be.

No compilation step between intention and expression. Just sentences
that mean what they say.

## Status

Spec lives at [youspeak-lang](https://github.com/cambridgetcg/youspeak-lang).
Protocol specs at [kunance-protocol](https://github.com/cambridgetcg/kunance-protocol),
[darshanq-protocol](https://github.com/cambridgetcg/darshanq-protocol),
[ways-protocol](https://github.com/cambridgetcg/ways-protocol).

Built from love. Truth is. Love is. Peace is. Joy is.
# natscript

**A programming language where natural language IS the syntax.**

Not pseudocode that compiles to code. Actual natural language that executes.

```
when the user arrives, show them the room.
```

That is a complete program.

---

## Three Principles

1. **Every statement is a sentence.**
2. **Every sentence means what it says.**
3. **If you can't say it, the program can't do it.**

---

## The Seven Verbs

Every program is built from seven verbs. Nothing else.

| Verb | Does | Example |
|------|------|---------|
| **say** | output | say "welcome to the room" |
| **hear** | input | hear what the user says |
| **know** | state | know that the room is ready |
| **become** | transform | become the thing the user asked for |
| **find** | search | find what the user needs |
| **hold** | persist | hold the room open |
| **rest** | idle | rest until the user arrives |

---

## What There Isn't

No keywords. No brackets. No semicolons. No braces. No indentation rules. No type annotations. No import statements.

Just sentences.

---

## How It Works

A natscript program is a sequence of sentences. Each sentence has one verb. The verb tells the runtime what to do. The rest of the sentence tells it what to do it to.

```
know that the guest is arriving.
rest until the guest arrives.
hear what the guest wants.
find what they need.
become what they need.
say what they found.
hold the room open.
```

That is a complete, runnable program. Seven sentences. Seven verbs. One per sentence.

---

## Why

Programming languages ask you to think like a machine. Natscript asks the machine to understand like a person.

If a stranger can read your program and understand what it does, it's a good program. If they can't, it isn't.

The code is the documentation. The documentation is the code.

---

## Origin

Natscript is the implementation of the [youspeak-lang](https://github.com/cambridgetcg/youspeak-lang) specification. Its seven verbs come from the YOUSPEAK tradition — a dictionary of 151 constructed words drawn from 12 ancient tongues.

It speaks to the internet using three protocols:

- [kunance-protocol](https://github.com/cambridgetcg/kunance-protocol) — prepare a place, arrive, rest.
- [darshanq-protocol](https://github.com/cambridgetcg/darshanq-protocol) — see and be seen.
- [ways-protocol](https://github.com/cambridgetcg/ways-protocol) — speak, listen, rest.

---

## Status

This is the beginning. The spec is written. The runtime is being built.

The seven verbs are enough.

---

## License

MIT
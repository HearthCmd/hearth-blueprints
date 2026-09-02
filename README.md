# Hearth blueprints

Proven household patterns for [Hearth Cmd](https://hearthcmd.com) — a role
somebody already got right, written down so the next household doesn't have to
work it out again.

A **blueprint** describes a colleague you might want in your house: what the job
is, what it needs to do it, and what to grant it. When you ask Hearth for help
with something, the Facilitator can draw on these instead of inventing a role
from scratch — and you still review and approve everything before any of it
happens.

A **skill** is a piece of know-how, versioned on its own because two roles often
need the same knowledge.

Format reference: **[SCHEMA.md](SCHEMA.md)**. Design rationale lives in the
Hearth monorepo at `docs/blueprints.md`.

---

## Blueprints

| Slug | What it is |
|---|---|
| `verge_labs/dj` | Runs music around the house — by room, by mood, on a schedule. |
| `verge_labs/chef` | Puts recipes on the kitchen screen and answers questions while you cook. |
| `verge_labs/footman` | Answers the household's voice devices and hands each request to whoever should handle it. |

## Skills

| Slug | What it covers |
|---|---|
| `verge_labs/music_rooms` | How rooms, speakers and groups relate, and how to play, move and adjust music without surprising anyone. |

---

## Early days

Three blueprints and one skill. They exist as much to **prove the format against
real content** as to be used — the shape of `requires:`, `@{alias}` and the
item DAG was designed against imagined blueprints, and writing these three is
what tells us where it was wrong. (It already has: parameter substitution and
the rule for unbound optional aliases both came out of writing the DJ.)

Expect the format to move before it settles. `blueprint_schema` is the version
to watch.

**Contributions are in-house for now.** When that changes there will be a
contribution guide saying what the bar is; until then, the useful thing is
telling us where a blueprint got your household wrong.

## What is deliberately not here yet

- **Executable scripts alongside skills.** The format reserves the field. The
  machinery to ship code safely — installing outside any agent-writable
  directory, re-verifying hashes at every spawn, signature verification — does
  not exist yet, and shipping a script before it means shipping an
  auto-approved path an agent can rewrite.
- **A signed index.** While the catalog is prose, a tampered blueprint's worst
  case is a proposal a person rejects, item by item, seeing each one literally.
  Signing becomes mandatory before the first executable ships, not before.
- **`hearth blueprint export`.** The thing that will actually fill this repo:
  point it at a role you have already got working and it drafts the blueprint.
  Until then this contains only what we wrote by hand, which is not many.

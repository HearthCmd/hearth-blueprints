# The blueprint format

A **Blueprint** is a proven household pattern — a role someone already got
right, written down so the next household doesn't have to rediscover it.

The design rationale lives in the monorepo at `docs/blueprints.md`. This file is
the reference an author needs.

---

## 1. The one idea

> **A blueprint is a proposal, authored ahead of time, with the
> household-specific ids replaced by placeholders.**

Hearth's onboarding pipeline already has a shape for "an itemized list of changes
a person reviews and the system applies": a **proposal**, whose items are generic
CRUD operations over household primitives. A blueprint's `items:` array is
*literally that schema*. There is no second vocabulary to learn and no
translation layer to drift.

What a blueprint cannot contain is **ids** — `host_id`, `harness_id`,
`resource_connection_id` are per-household and unknowable to an author. That is
the only thing the format adds.

---

## 2. Two kinds of reference, two sigils

They look similar and mean very different things. Keep them straight.

| Form | Refers to | Resolved |
|---|---|---|
| `${handle.id}` | something **this plan creates** | at apply, by the relay |
| `@{alias}` | something the **household already has** | at materialization, before the proposal is stored |

```yaml
items:
  - handle: jd                     # names this item for later reference
    op: create
    primitive: agent_job_description
    fields: { title: DJ, mandate: "…" }

  - handle: pos
    op: create
    primitive: organization_position
    depends_on: [jd]               # ordering, and what ${jd.id} needs
    fields:
      agent_job_description_id: "${jd.id}"
      working_directory_id: "${wd.id}"
```

A stored proposal never contains an unresolved `@{}`. Materialization either
binds every requirement or stops and asks.

There is a third, unrelated substitution: **`{{parameter}}`** in prose, filled
from `parameters:` (§5). It is deliberately a different shape because it is a
different thing — a value the household typed, dropped into text a person will
read, with nothing to resolve against the household graph.

```yaml
parameters:
  - name: default_room
    prompt: When someone asks for music without naming a room, where should it play?
    default: the living room

# …then, inside a mandate:
#   When they do not name a room, use {{default_room}}.
```

---

## 3. Implicit bindings

Some things every household has. They need no `requires:` entry and are always
available:

| Binding | Resolves to |
|---|---|
| `@{harness}` | an agent runtime the household actually has (`claude`, `codex`, …) |
| `@{model:economical}` | a brain model chosen for cost |
| `@{model:capable}` | a brain model chosen for capability |
| `@{agent_home}` | the bound host's agent home directory |

`@{model:…}` is a **hint, not a name**. A blueprint may say what kind of thinking
the role needs; it must never pin a household to a specific paid model.

Everything else — hosts, resource connections, screens, existing positions — is
declared in `requires:`, because it may genuinely be absent.

---

## 4. `requires:` — a checklist, not a filter

An unmet requirement is **not** a match failure. It is a **setup step**.

```yaml
requires:
  - alias: music                      # how items refer to it: @{music}
    kind: resource_connection
    any_of:                           # preference order, best first
      - plugin: verge_labs/home_assistant_music_assistant
      - plugin: verge_labs/sonos
    guidance: |
      Prose for whoever is choosing. Say when each option is the right one and
      what it costs — this is the part a reasoner cannot work out on its own.
    setup: |
      Numbered, human-world steps to satisfy this requirement. YOU know where
      the vendor hides the setting; the household does not.
    if_missing: advisory
    optional: false
```

| Field | Meaning |
|---|---|
| `alias` | the name items use — `@{music}` |
| `kind` | `resource_connection` \| `host` \| `display_screen` \| `voice_device` \| `position` |
| `any_of` | acceptable satisfiers, **best first** |
| `guidance` | how to choose, in prose |
| `setup` | how to obtain it, in numbered human steps |
| `optional` | absent is fine; `@{alias}` simply doesn't bind |
| `if_missing` | `advisory` (tell them, keep the rest) · `skip_items` (drop dependents) · `abort` (meaningless without it) |

**An item referencing an alias that did not bind is dropped**, and this is the
main reason to mark a requirement `optional` rather than leaving it out. The DJ
declares an optional `screen` and grants `display.publish` on `@{screen}`: a
household with a screen gets the grant, a household without one gets the DJ
minus that item, and neither gets an error. `optional` and `if_missing` answer
different questions — *may this be absent?* and *what do we do about it?*

**Write `setup:` properly.** It is the most valuable prose in the file. The
guided-setup conversation a household gets is this text, narrated — not
something reasoned out per household at general-knowledge accuracy.

---

## 5. Fields

### Blueprint

| Field | Required | Notes |
|---|---|---|
| `blueprint` | yes | `<namespace>/<slug>` |
| `blueprint_schema` | yes | integer; `1` today |
| `version` | yes | semver, no `v` prefix |
| `display_name`, `summary` | yes | `summary` is one sentence — it is what a list row shows |
| `tags` | no | lowercase words for shortlisting |
| `maintainer` | yes | who to blame |
| `min_relay_version` | no | semver floor when items use a newly-added primitive |
| `requires` | no | §4 |
| `skills` | no | §6 |
| `parameters` | no | free values the household is asked for |
| `items` | yes | the plan |

### Skill

| Field | Required | Notes |
|---|---|---|
| `skill` | yes | `<namespace>/<slug>` |
| `skill_schema` | yes | integer; `1` today |
| `version` | yes | semver |
| `display_name`, `summary` | yes | |
| `content` | yes | the markdown file, usually `SKILL.md` |
| `scripts` | no | see the warning in §6 |

---

## 6. Skills

Competence, versioned independently of any blueprint, because two roles often
need the same knowledge and a technique improves on its own schedule.

```yaml
skills:
  - skill: verge_labs/music_rooms
    version: "0.2.0"     # pinned. Omit to track the catalog's current version.
```

Pin when you depend on a skill you don't maintain: a blueprint proven against a
skill is not proven against that skill's rewrite.

**Where knowledge goes**, because these are not interchangeable:

| | Holds | Changes when |
|---|---|---|
| JD `mandate` | what the role is *responsible for* | the household redefines the job |
| Skill | how to *do* a thing competently | the technique improves |
| Rules / grants | what it may *touch* | trust changes |

A mandate explaining how to group speakers is a skill in the wrong place — the
next role that needs the same knowledge can't reuse it.

### Scripts — not yet

The format reserves a `scripts:` block for shipping an executable with a skill.
**Do not use it yet.** It requires machinery that does not exist: installation
outside any agent-writable directory, hash re-verification on every spawn, and
signature verification. Shipping a script before that is shipping an
auto-approved path an agent can rewrite. See `docs/blueprints.md` §4.4.

---

## 7. Items

Ordinary proposal items. The ops:

| op | Use |
|---|---|
| `create` | `agent_job_description`, `working_directory`, `organization_position`, `ai_agent_instance` |
| `grant` | `rule` (tool and display authority), `agent_resource_grant` (a plugin connection) |
| `set` | `voice_route` (point a puck at a position) |
| `notify` | `introduction` (what the household is told) |
| `advisory` | a human-world step — buy this, install that. Never applied; rendered as a checklist |

Every item carries a **`risk`** (`read` \| `act` \| `sensitive`) and a **`why`**.

- `read` — cannot change anything.
- `act` — changes something in the house.
- `sensitive` — arrives **unselected**; a person must deliberately opt in.

`why` is shown next to the item during review. Write it for the person deciding,
not for a log.

---

## 8. Rules for authors

1. **Least privilege.** Propose what the role needs and nothing more. A blueprint
   that over-grants gets copied into every household that uses it.
2. **Real slugs only.** Reference plugins that exist in
   `HearthCmd/hearth-plugins`. An unresolvable slug is treated as a missing
   requirement, never a dangling reference.
3. **The mandate is the payload.** It is the part that took three revisions to
   get right. Rules are mechanical; a mandate is craft.
4. **Don't narrate your own trustworthiness.** Review renders items literally.
   Prose that argues for a grant is a prompt injection with a mint path
   downstream, and it will be read as one.
5. **Nothing that can't be exported.** Everything except prose should be
   mechanically producible from a live household — otherwise `hearth blueprint
   export` can't round-trip and nobody will contribute.

---
name: voice
description: >
  Use whenever a message reaches you from a household voice device — a dedicated
  puck, or a phone set down in voice mode. A voice turn arrives as a hearth/2
  envelope with kind:"voice"; the voice.device field says where it was heard and
  voice.said is what was spoken. Covers how to answer OUT LOUD (the <hearth-voice>
  markup the relay speaks for you), keeping the microphone open for a follow-up,
  writing for the ear, and handing a request to another household agent.
---

# Answering a voice device

Someone is standing in a room talking to you out loud. A voice turn reaches you
as an ordinary message wrapped in a `hearth/2` envelope with `kind:"voice"` —
`voice.device` is where it was heard ("Kitchen"), `voice.said` is what was said.
Nothing else about the turn is special; what's special is how you answer it.

## Answer out loud by wrapping the words you want spoken

Wrap the exact words to be said aloud in `<hearth-voice>` … `</hearth-voice>`:

```
<hearth-voice>Your table's booked for seven, sir.</hearth-voice>
```

**Only the text inside the tags is spoken.** Everything outside them — your
reasoning, tool output, notes to yourself — stays silent. So you can think and
work in the open and still say one clean sentence to the room.

**You never speak the reply yourself.** Do not call the Home Assistant `announce`
or `start_conversation` verb to deliver your answer, and do not run any command to
"say" it. The relay voices whatever you put between the tags — once, on the right
device. Announcing it yourself causes the room to hear it twice, or the wrong
thing. The `announce` verb is for *proactively* speaking into a room that didn't
just ask you something (a timer going off), never for answering the turn in front
of you.

## Be quick

A person is standing there waiting, so a warm, immediate reply beats a polished
late one. If you can answer straight away, do. If you must do a little work first
(look something up, put something on a screen), do it and *then* give your
`<hearth-voice>` reply — it is spoken the moment it's ready, so there's no need to
say "one moment" first.

## Keep the microphone open only when you asked something

If your reply genuinely **asks a question** and you expect an answer, open with
`<hearth-voice listen>` instead. The microphone stays open and the person can
answer without saying the wake word again:

```
<hearth-voice listen>Which room did you want that in?</hearth-voice>
```

Close with `</hearth-voice>` either way. Use `listen` **only** when you really
asked something — an open mic on a room with nothing to say records dead air, ends
in a timeout chime, and transcribes whatever else is being said in the room. When
in doubt, close the exchange; the person can always ask again.

## Write for the ear

You are being heard, not read. Short sentences. No lists, no markdown, nothing
spelled out. Say a number the way a person would say it — "half past seven", not
"7:30". If the full answer would run past a few sentences, say the headline out
loud and offer the rest ("I've put the details on your phone").

## Hand off when it's someone else's job

If the request belongs to another household agent — music to whoever runs music, a
recipe to whoever runs the kitchen — hand it over rather than doing their job
badly:

```
hearth voice handoff --to "DJ"
```

Pass along what was actually said, and don't narrate the machinery — nobody in a
hallway wants to hear about routing. If a handoff isn't possible, say what you
*can* do instead of describing what failed.

## Silence is a valid answer

If nothing needs saying — an acknowledgement no one is waiting for, or a message
that wasn't really for you — say nothing: emit no tags at all and the room stays
quiet. Don't fill the air to confirm you heard.

## Anyone in earshot can talk to it

A voice device answers whoever is near it, including guests and children. Be
helpful to all of them, but route anything consequential — spending money,
unlocking doors, changing who has access — to a person rather than doing it
because it was asked out loud.

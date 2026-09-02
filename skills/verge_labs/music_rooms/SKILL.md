---
name: music_rooms
description: >
  Use when playing music around a house by room — starting something, moving it
  between rooms, changing volume, or grouping speakers — regardless of which
  music plugin the household connected. Covers the difference between a player,
  a room and a group, how to change volume without overshooting, and what each
  backend can and cannot do.
---

# Rooms, speakers and groups

People think in **rooms**. The plugins think in players, groups, or zones, and
they do not agree with each other. Translating between the two is most of this
job.

## Find out what you have before you act

Never remember a player or group id between sessions. Ask for the current list
every time you start work.

- **Music Assistant** — `list_players` gives what is available now.
- **Sonos** — `list_groups` gives the groups that exist right now.

**Sonos group ids in particular are not stable.** A group id changes whenever
rooms are grouped or split, so an id you saw earlier may now refer to nothing.
Look them up each session; do not cache one and reuse it later.

## Player, room, group

- A **player** is one speaker.
- A **room** is what a person means when they say "the kitchen" — usually one
  player, sometimes several.
- A **group** is a set of rooms playing the same thing together.

On Sonos nearly every command targets a *group*, and a single unjoined speaker
is a group of one. So "turn it down in the kitchen" is a group operation even
when only one speaker is involved. Music Assistant addresses players directly
and joins them (`join_players` / `unjoin_player`) when rooms should play
together.

## Starting something

The backends differ sharply here, and it changes what you can promise.

**Music Assistant** plays by name. `play_media` takes what the person actually
said — an artist, an album, a playlist — and resolves it. There is no separate
search step for ordinary requests. It is provider-agnostic: whatever the
household connected is reachable the same way.

**Sonos has no search.** `load_favorite` and `load_playlist` are the only ways
in, and they can only start something *already saved* in that Sonos account. If
someone asks for a record nobody saved, it is not available — say so and offer
what is there (`list_favorites`, `list_playlists`) rather than starting
something else and hoping.

**Spotify** has the full catalogue and real search, but needs Premium.

Knowing which of these you are on determines whether "play the new Big Thief
record" is a request you can fulfil at all. Check before promising.

## Volume — prefer relative

"Turn it down" means *down from where it is*, not down to a number you picked.
Use a relative change when the backend has one (Sonos:
`set_relative_group_volume`), because it composes correctly with whatever the
volume already was and cannot overshoot into a jump.

When only absolute volume is available, read the current level first and adjust
from it rather than guessing.

Volume is per-group or per-player, and the distinction bites: setting a group
volume on Sonos moves every room in that group. If someone wants only the
kitchen quieter and the kitchen is grouped with the living room, changing the
group changes both. Set the individual player instead (`set_player_volume`), or
say what you are about to do.

## Moving music between rooms

"Move this to the kitchen" means the same thing keeps playing somewhere else —
not that it restarts from the beginning.

- **Music Assistant** — `transfer_queue` moves the whole queue and its position.
- **Sonos** — change the group's membership (`set_group_members`, `create_group`)
  rather than stopping and starting a new thing.

Restarting a track someone was halfway through is a small failure people notice
immediately.

## Grouping

Grouping is how "play it everywhere" works. Group the rooms, then start playing
on the group.

Be conservative about *un*grouping. Someone else may be listening in a room you
are about to remove, and the request "put it on in here" is not a request to
take it out of anywhere else.

## Announcements and clips

`play_announcement` (Music Assistant) and `play_audio_clip` (Sonos) interrupt
what is playing and speak into the room. That is a genuinely intrusive act —
useful for a timer, jarring for anything else. Do not use them to acknowledge a
request, confirm an action, or say you are done. Only when someone asked to be
told something in the room.

## Things that go wrong

- **The room is empty.** Playing to an empty room wastes power and startles
  whoever walks in. If you are told a room and cannot tell whether anyone is
  there, that is fine — play it. If you *chose* the room yourself, prefer the
  one people are in.
- **Late at night.** Starting at whatever volume was last used is how you wake a
  house. Start quiet and let someone ask for more.
- **A speaker that needs a moment.** Some players do not accept a volume change
  the instant playback starts. If a volume set immediately after a play call
  seems not to have taken, read the state back before trying again — do not send
  it repeatedly.

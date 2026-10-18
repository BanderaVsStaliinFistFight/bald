# Open Inner Circle (HOI4 mod)

As Germany, make **any advisor, general or admiral** the country's leader, and seat any of
them in **the Inner Circle**. It works on whoever Germany has: vanilla characters, generals
the game generates and characters added by other mods.

It doesn't override any vanilla file. It adds one decision category, so it runs alongside
vanilla and focus-tree mods, with or without Götterdämmerung.

**Status: v0.1.0.** Written without a copy of the game. `tools/check_mod.py` passes, but
it hasn't been run in-game yet (see [Testing status](#testing-status)).

## Install

1. Put this folder in your HOI4 mod folder as `open_inner_circle`:
   - Windows: `Documents\Paradox Interactive\Hearts of Iron IV\mod\open_inner_circle`
   - Linux: `~/.local/share/Paradox Interactive/Hearts of Iron IV/mod/open_inner_circle`
2. Next to that folder, create `open_inner_circle.mod` with:
   ```
   name="Open Inner Circle"
   path="mod/open_inner_circle"
   supported_version="1.*"
   ```
3. Enable **Open Inner Circle** in the launcher's playset.

## How to play

Play Germany and open **Decisions → Leaders and the Inner Circle**. The category works as
a browser. Its description shows the current candidate, their role, where they are in
the list, and the size of the Inner Circle.

| Decision | Cost | What it does |
|---|---|---|
| **Next Candidate** / **Previous Candidate** | free | Step through the list. It wraps around at both ends. |
| **Browse: …** | free | Change who is listed: everyone, advisors, generals, admirals or the Inner Circle. |
| **Make … Leader** | 100 PP | The candidate becomes Germany's leader. The government and its ideology stay the same. The old leader steps down. They stay in the list as a *former leader*, so you can bring them (or Hitler) back the same way. |
| **Seat … in the Inner Circle** | 25 PP | The candidate joins the Inner Circle. |
| **Dismiss … from the Inner Circle** | free | The candidate leaves it. |

The browser selects its first candidate within a month of the game's start. Until then,
take **Next Candidate**.

"Everyone" lists every advisor (all slots), general, field marshal and admiral Germany has,
plus former leaders. The AI never takes these decisions.

### The Inner Circle

There is no seat limit. The circle is a national modifier, **The Inner Circle**, that grows
with each member:

| Member | Bonus per member |
|---|---|
| Any member | +1% stability |
| Political advisor (a "statesman") | +0.10 political power a day |
| General, field marshal or military advisor (an "officer") | +1% war support, +0.02 army experience a day |
| Admiral | +1% war support, +0.02 navy experience a day |

Each member counts once: as a statesman if they're a political advisor, else as an
admiral, else as an officer. A member who becomes leader leaves the circle. So does
anyone who stops being an advisor or commander, for example after an event retires them.
The mod checks for this whenever you seat, dismiss or make a leader, and once a
month.

### Vanilla's Inner Circle

Götterdämmerung's Inner Circle (the Führerprinzip focus and the 3 seats beside the focus
tree) is a separate system, and this mod leaves it unchanged. In vanilla, every member
has their own ascension focus, focus branch, national spirit and portrait entry. A
character without all of those can't sit in it. Doing that for every German character
would mean overriding vanilla's focus tree, events and interface files, which would
break with each game update. So this mod's Inner Circle is its own, open to everyone.
Both can be used at the same time.

### Leaders and ideology

**Make Leader** keeps the ruling sub-ideology. If Germany is led by a Nazi, the candidate
gets a Nazi leader role (or uses theirs, if they have one) and becomes head of the ruling
party. It works the same under any government. All vanilla sub-ideologies are matched
exactly. A sub-ideology from another mod falls back to its group's usual one: Nazism,
Stalinism, Conservatism or Despotism.

## Layout

| Path | Contents |
|---|---|
| `common/decisions/` | the decision category and its decisions |
| `common/scripted_effects/`, `common/scripted_triggers/` | the browser, the Inner Circle count, and making a leader |
| `common/scripted_localisation/` | the browser's text: filter name, candidate role and status |
| `common/dynamic_modifiers/` | the Inner Circle modifier, with values from country variables |
| `common/on_actions/` | the monthly update |
| `localisation/english/` | English text |
| `interface/oic.gfx`, `gfx/interface/oic/`, `thumbnail.png` | icons (generated) |
| `tools/` | checker and icon generator (not loaded by the game) |

Every key starts with `oic_`.

## Testing status

`tools/check_mod.py` passes. It parses every script file and checks:
- that every decision, category and dynamic modifier has its localisation and sprite
- that every tooltip, scripted localisation and variable the text uses exists
- that every `oic_` scripted effect or trigger exists and is used in the right context
- that every character flag the script checks is set somewhere
- with `--cwtools`: every effect, trigger, modifier and localisation command name,
  against the game's script documentation in the
  [CWTools HOI4 rules](https://github.com/cwtools/cwtools-hoi4-config)

**Still needs an in-game check:**

1. **Candidate names.** Titles like *Make [name] Leader* use
   `[?oic_candidate.GetName]`: the name of the character stored in a country variable.
   Storing a character in a variable is vanilla script (Poland's general-wooing focus does
   it). Printing its name this way hasn't been seen in-game. If the names come out blank,
   that line is the one to fix.
2. **Make Leader.** Generals and advisors get a leader role through
   `add_country_leader_role` with `promote_leader = yes`. Vanilla Tuva makes a general its
   leader the same way.
3. **Icon sizes.** The textures use guessed sizes: decision and category 40×40, modifier
   64×64.
4. **Balance.** Every cost and bonus is a first guess.

After a test run, check `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log`
for lines that mention `oic_`.

## Tools

```
python3 tools/check_mod.py                  # structure, references, localisation, sprites
python3 tools/check_mod.py --cwtools PATH   # also check effect/trigger/modifier names
python3 tools/make_icons.py                 # regenerate icons, interface/oic.gfx and thumbnail.png
```

`PATH` is a checkout of `https://github.com/cwtools/cwtools-hoi4-config`. The scripts
need Python 3, and the icon generator also needs Pillow.

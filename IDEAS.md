# Adeptus Astartes — HOI4 Mod Design Ideas

> Status: **v0.1.2**: the minimum viable version below, plus the full orbital layer, with
> the Astartes tech tab built on the game's research screen layout (see README).
> See [README.md](README.md). Every number here is still a placeholder to balance later.

## Pitch

Any nation can start the **Astartes Project**: it engineers transhuman super-soldiers, puts
them in power armour and fields a small, elite Space Marine Chapter.

The mod is made of **technologies and decisions only**:

- no focus trees, no events, no new countries, no map changes
- it works alongside vanilla and any focus-tree mod, because it doesn't touch them
- decisions may apply national spirits, dynamic modifiers and flags as *effects*, and
  technologies unlock a small set of new battalions and equipment. Those are supporting
  files, not separate systems.

## Design pillars

1. **Few but mighty.** One Astartes battalion stands for one Codex *company* of 100
   Battle-Brothers. Battalions need very little manpower but very expensive equipment.
   Their numbers are limited by the special-forces cap.
2. **Long build-up.** The gene-seed tree is a deep research investment. The first real
   battalions arrive around 1939–40.
3. **One defining choice.** You choose a gene-seed lineage, which sets your Chapter's
   playstyle *and* its flaw.
4. **Gene-seed is the currency.** Expansion is paid for with a stockpile that decisions
   create and spend. More manpower doesn't speed it up.

## Core loop

```
 Establish the Astartes Project (decision)
            │  reveals the Astartes tech tab, +5 gene-seed
            ▼
 Research the Gene-Seed branch ─────────────► Black Carapace (1939)
            │                                        │
 Gene-Forge decisions ──► GENE-SEED STOCK ──► Found a Chapter (decision)
            ▲                                        │  +10 special-forces min,
            │                                        │  unlocks Tactical Squads
            │                                        ▼
 Recover Progenoids (decision) ◄──── Astartes companies fight at the front
                                             │
                    Operations decisions (Drop Pod Assault, Orbital Bombardment…)
```

## Timeline of a typical game

| Year | Milestone |
|---|---|
| 1936 | Establish the Project. Research Gene-Seed Sequencing. Build the first Gene-Forge. |
| 1937 | Stockpile Mk II power armour. Field Neophyte Scout companies, the first payoff. |
| 1938 | Choose a gene-seed lineage. Unlock the Apothecarion. |
| 1939 | Black Carapace → **Found the First Chapter**. The first Tactical companies deploy. |
| 1940–41 | Assault and Devastator Squads, Drop Pods, Dreadnoughts. |
| 1942–43 | Terminators, Strike Cruiser, Second Founding. |
| 1944+ | Battle Barge, Primaris Programme (late-game stretch). |

---

## Technologies

All technologies sit in a new **Astartes** tab. The tab stays hidden until the
project is established (`allow_branch = { has_country_flag = sm_project_founded }`).
The tab has three branches.

### Branch 1 — Gene-Seed (20 techs)

The **spine** must be researched in order. **Side organs** are optional: they become
available once their tier's spine tech is done. That keeps a fast path of 5 techs to
Black Carapace, with 15 optional techs for depth. Effects apply to all `sm_*` Astartes
battalions unless stated otherwise.

| Year | Spine tech | Side organs (optional) |
|---|---|---|
| 1936 | **Gene-Seed Sequencing**: unlocks the Gene-Forge decisions | — |
| 1936 | **Secondary Heart**: +org recovery | **Biscopea** (+soft attack) · **Haemastamen** (+max org) |
| 1937 | **Ossmodula**: +HP; unlocks *Neophyte Scouts* | **Catalepsean Node** (smaller night-attack penalty) · **Preomnor** (less attrition) · **Omophagea** (+unit experience gain) |
| 1938 | **Larraman's Organ**: casualty trickleback; unlocks *Apothecarion* | **Multi-lung** (smaller river-crossing and naval-invasion penalties) · **Occulobe** (+recon) · **Lyman's Ear** (+initiative) · **Sus-an Membrane** (less experience loss; required for Dreadnoughts) |
| 1939 | **Black Carapace**: required to *Found the First Chapter* | **Melanochrome** (hot-climate acclimatisation) · **Mucranoid** (cold-climate acclimatisation) · **Oolitic Kidney** (less out-of-supply penalty) · **Neuroglottis** (+attack in forest, jungle and marsh) · **Betcher's Gland** (+small hard attack and piercing) · **Progenoid Glands** (doubles gene-seed from *Recover Progenoids*) |

Late gene-tech (stretch):

| Year | Tech | Effect |
|---|---|---|
| 1941 | Accelerated Implantation | −training time for Astartes battalions |
| 1942 | Gene-Seed Purification | halves your lineage's flaw penalties |
| 1944 | Belisarian Furnace · Sinew Coils · Magnificat | small stat buffs each; all three lead to ↓ |
| 1945 | **Primaris Programme** | unlocks *Primaris Intercessor* battalions |

### Branch 2 — Wargear

**Power armour** is one equipment line, upgraded mark by mark like Infantry Equipment I/II/III.
Mk II arrives *before* Black Carapace, so you can build up a stockpile before you found
the Chapter.

| Year | Mark | Character |
|---|---|---|
| 1937 | Mk II "Crusade" | baseline |
| 1939 | Mk III "Iron" | +defence, +armour, −speed |
| 1940 | Mk IV "Maximus" | balanced, +reliability |
| 1940 | Mk V "Heresy" *(side tech)* | emergency pattern: much cheaper, −reliability |
| 1942 | Mk VI "Corvus" | +speed, +recon |
| 1944 | Mk VII "Aquila" | best stats, cheapest per unit |
| 1946 | Mk VIII "Errant" *(stretch)* | — |

**Weapons** techs only buff existing Astartes battalions. They add no new equipment,
which keeps the asset count low.

| Year | Tech | Effect |
|---|---|---|
| 1937 | Bolt Shell Metallurgy → **Boltgun** | +soft attack |
| 1938 | **Heavy Bolter** | +soft attack (extra for Devastators); unlocks *Devastator Squads* |
| 1939 | **Chainswords** → 1941 **Power Weapons** | +breakthrough |
| 1939 | **Flamers** | +attack in urban and forest terrain |
| 1940 | **Meltagun** | +hard attack, +piercing |
| 1941 | **Plasma Gun** | +soft and hard attack, −reliability ("gets hot") |
| 1941 | **Lascannon** | +piercing, +Devastator hard attack |
| 1942 | **Storm Bolter** | +Terminator soft attack |

**Heavy assets**

| Year | Tech | Unlocks |
|---|---|---|
| 1940 | Jump Packs | *Assault Squads* |
| 1940 | Rhino Chassis | Rhino-mounted Tactical Squads (mechanised variant) |
| 1941 | Sarcophagus Interment *(needs Sus-an Membrane)* | *Dreadnoughts* |
| 1942 | Tactical Dreadnought Armour | *Terminator Squads* |
| 1941 | Predator / Whirlwind *(stretch)* | armour / rocket-artillery battalions |
| 1943 | Land Raider *(stretch)* | heavy armour battalion |
| 1941 | Thunderhawk Gunship *(stretch)* | CAS/transport aircraft |
| 1941 | Psychic Hoods *(stretch)* | *Librarius* support company |

**Void assets** enable decisions only. They add no ships or units to the map, which keeps
the orbital fantasy inside "techs + decisions".

| Year | Tech | Enables |
|---|---|---|
| 1940 | Drop Pods | *Drop Pod Assault* |
| 1942 | Strike Cruiser | *Lance Strike*; Drop Pod Assault cooldown −50% |
| 1944 | Battle Barge | *Orbital Bombardment* |
| 1946 | Cyclonic Torpedoes *(joke / stretch)* | *Exterminatus* |

### Branch 3 — Codex Doctrine (pick one, `XOR`)

This is a small doctrine tree that sits beside the vanilla land doctrines. Researching one
path's first tech locks out the other three.

| Path | Theme | Techs |
|---|---|---|
| **Codex Adherent** | balanced combined arms | Combat Squads (+org) → Battle Company Doctrine (+planning speed) → Chapter Master's Council (+command power gain) |
| **Lightning Strike** | speed and breakthrough | Hit-and-Run (+speed) → Bike Squadrons (+breakthrough) → Hunt the Fleeing (+attack against retreating units) |
| **Siegecraft** | defence, entrenchment, breaking forts | Bastion Doctrine (+entrenchment) → Siege Masters (smaller penalty when attacking forts) → The Last Wall (+defence) |
| **Shadow War** | recon, night, deep strikes | Infiltrators (+recon) → Decapitation Strike (+night attack) → Omega Doctrine (out-of-supply grace) |

### What the techs unlock: formations

Each formation matches a company in the Codex structure of a Chapter:

| Unit | Kind | Unlocked by | Codex company | Role |
|---|---|---|---|---|
| Neophyte Scouts | recon support company | Ossmodula | 10th | early payoff; doesn't need Black Carapace |
| Apothecarion | support company (like a field hospital) | Larraman's Organ | — | trickleback; boosts *Recover Progenoids* |
| Techmarine Cadre | support company (like maintenance) | Mk III | — | reliability, equipment capture |
| Chaplaincy | support company | Found the First Chapter | — | +org, +morale |
| Librarius | support company | Psychic Hoods (1941) | — | +initiative, +recon |
| Tactical Squad | line battalion | Found the First Chapter | 2nd–7th | the core unit |
| Assault Squad | line battalion | Jump Packs | 8th | breakthrough, speed |
| Devastator Squad | line battalion | Heavy Bolter | 9th | firepower, low defence |
| Terminator Squad | line battalion | Tactical Dreadnought Armour | 1st | very slow, very tough |
| Dreadnought | armour-type battalion | Sarcophagus Interment | — | breakthrough, armour |

---

## Decisions

There are five decision categories. The category header always shows the current
**gene-seed** stock, using scripted localisation.

### Gene-seed (the resource)

- Stored in the country variable `sm_geneseed`.
- Decisions spend it through `custom_cost_trigger` / `custom_cost_text`.
- Sources: Gene-Forge harvests and Recover Progenoids.
- Sinks: founding Chapters, relic wargear and drop pod operations.

### 1. The Astartes Project (visible from game start)

| Decision | Cost | Requires | Effect |
|---|---|---|---|
| **Establish the Astartes Project** | 100 PP | nothing: any nation can start it | sets `sm_project_founded` (reveals tech tab); research bonus for Gene-Seed Sequencing; +5 gene-seed |
| **Requisition a Gene-Forge** *(state-targeted, max 3)* | 50 PP + 3 civ. factories for 120 days | core state, infrastructure ≥ 5; Gene-Seed Sequencing | state becomes a Gene-Forge (flag + dynamic modifier) |
| **Harvest Gene-Seed** *(repeatable, 60-day cooldown)* | 25 PP | ≥ 1 Gene-Forge | +2 gene-seed, +2 per Gene-Forge |
| **Recover Progenoids** *(repeatable, 90-day cooldown)* | — | at war; Chapter founded | +3 gene-seed (×2 with Progenoid Glands, +1 if a division template has an Apothecarion) |
| **Aspirant Trials** *(repeatable, 120-day cooldown)* | 10k manpower | project founded | −10% Astartes training time for 120 days |

### 2. Chapter Founding (visible after Ossmodula)

| Decision | Cost | Requires | Effect |
|---|---|---|---|
| **Choose Gene-Seed Lineage** *(9 options, pick one; see table below)* | 75 PP | Ossmodula | permanent lineage spirit; unlocks that lineage's flaw mission |
| **Found the First Chapter** | 20 gene-seed, 150 PP, 5k manpower | Black Carapace, a lineage, Mk II | grants the Tactical Squad and Chaplaincy techs; +10 to the special-forces minimum (`special_forces_min`; one battalion per company); creates a "1st Company" division template |
| **Appoint a Chapter Master** | 50 PP | Chapter founded | creates a field marshal with Astartes traits |
| **Ordain a Captain / Chaplain / Librarian** *(max 3 each)* | 25 PP | Chapter founded | creates a corps commander with a matching trait |
| **Second Founding** *(repeatable, max 3)* | 40 gene-seed, 200 PP | 1942+, previous Chapter founded | +10 special-forces minimum; successor Chapter spirit |
| **Grant a Successor Chapter** *(targeted at a subject or faction member)* | 30 gene-seed, 100 PP | Second Founding done | target gets `sm_project_founded`, a research bonus for Black Carapace and +10 gene-seed |

#### Gene-seed lineages

| Lineage | Bonus | Flaw (mechanism) |
|---|---|---|
| **Ultramarines** | +planning speed, +org; small power armour defence and soft-attack bonus | "Codex Purity": no flaw, but the smallest combat bonuses |
| **Dark Angels** | +defence; cheaper Terminators (Deathwing) and Rhinos (Ravenwing) | *Hunt for the Fallen*: recurring mission |
| **Space Wolves** | +attack in snow and winter, +soft attack | *Curse of the Wulfen*: recurring mission |
| **Blood Angels** | +breakthrough; cheaper Assault Squads | *Red Thirst*: recurring mission → *Black Rage* |
| **Imperial Fists** | +power armour defence; +dig-in speed and fort construction speed nationwide | No working Betcher's Gland: −10% power armour piercing, which cancels that organ (permanent) |
| **White Scars** | +speed; Lightning Strike doctrine 50% cheaper | −defence for Astartes battalions |
| **Raven Guard** | +recon, +night attack, out-of-supply grace | *Degraded Stock*: −25% gene-seed from all sources |
| **Salamanders** | flamer and melta techs twice as strong; +reliability | slower Chapter growth: Second Founding costs +50% |
| **Iron Hands** | +armour, +reliability; cheaper Dreadnoughts | *Weakness of Flesh*: −org recovery |

### 3. Forge & Armoury (visible after Chapter founded)

| Decision | Cost | Requires | Effect |
|---|---|---|---|
| **Forge Pact** *(repeatable, 180-day cooldown)* | 75 PP + 5 civ. factories for 90 days | Mk II | at the end, adds power armour to the stockpile |
| **Recover Relic Wargear** *(mission, 120 days)* | 10 gene-seed | Tactical Dreadnought Armour | success adds Terminator armour to the stockpile and a temporary +attack spirit |
| **Bless the Machine Spirits** *(180-day cooldown)* | 50 PP | Techmarine Cadre | +reliability for Astartes vehicles for 90 days |
| **Techmarine Exchange** *(targeted at another Astartes nation)* | 50 PP | both have founded a Chapter | both get a research bonus in the Astartes tab |

### 4. Crusade (operations; visible after Chapter founded)

Each operation's cooldown is shared across all target states.

| Decision | Cost | Requires | Effect |
|---|---|---|---|
| **Declare a Crusade** *(targeted at a country)* | 100 PP | different ideology from the target; war support ≥ 50% | wargoal against the target; +war support |
| **Drop Pod Assault** *(targeted at an enemy state; 60-day cooldown)* | 5 gene-seed, 30 command power | Drop Pods | damages forts and AA in the state; enemy divisions there lose 30% organisation; +5% attack and breakthrough for 14 days |
| **Lance Strike** *(targeted at an enemy state; 30-day cooldown)* | 50 command power | Strike Cruiser | damages arms factories and infrastructure in the state |
| **Orbital Bombardment** *(targeted at an enemy state; 180-day cooldown)* | 100 command power | Battle Barge | heavy damage to factories, infrastructure, air bases and forts; enemy divisions there lose 50% organisation and 15% strength |
| **Purge the Heretic** *(targeted at an occupied state)* | 25 PP | Chapter founded | −resistance, +compliance growth |
| **Exterminatus** *(stretch, once per game)* | 50 gene-seed, 200 PP | Cyclonic Torpedoes | devastates a state; large world-tension and war-support penalties |

### 5. Gene-Seed Flaws (missions)

These missions are the risk side of the lineage choice. They are **missions** that activate
on a trigger (for example, at war and with a 180-day cooldown since the last one). The
player has a limited time to pay them off; if the timer runs out, a penalty applies.

| Mission | Lineage | Resolve with | If the timer runs out |
|---|---|---|---|
| **Hunt for the Fallen** | Dark Angels | 50 PP within 60 days | −stability, −10 gene-seed |
| **Curse of the Wulfen** | Space Wolves | 5 gene-seed within 45 days | "Wulfen" spirit for 90 days: +attack, −org, no Recover Progenoids |
| **Red Thirst** | Blood Angels | 50 PP + 5 gene-seed within 60 days | "Black Rage" for 120 days: +breakthrough, −defence, more casualties |
| **Degraded Stock** | Raven Guard | 75 PP within 90 days | −1 Gene-Forge yield until the next *Harvest* |

The late tech *Gene-Seed Purification* halves these penalties.

---

## Balance guardrails

- **Special-forces cap.** Astartes battalions use `special_forces = yes`, so they count
  against the vanilla cap. Each founding decision raises the special-forces minimum by 10. The cap is shared with
  vanilla marines, mountaineers and paratroopers (see open question 4).
- **Cost profile.** About 100 manpower per battalion, but power armour costs roughly
  8–10× an infantry equipment set. The real brake is equipment, not manpower.
- **Stat target.** One Astartes company ≈ 3 infantry battalions in combat, at about
  4–5× the production cost. Power armour gets enough armour value that infantry without
  anti-tank weapons can't fully pierce it.
- **Gating.** Tactical Squads are unlocked only through the *Found the First Chapter*
  decision, which grants the tech with `set_technology`. Researching ahead alone can't
  skip the decision.
- **AI.** Low `ai_will_do` by default. Majors with ≥ 4 research slots pursue the project at
  a moderate weight.

---

## Minimum viable version (built as v0.1.0)

This is what v0.1.0 contains. It also includes the whole orbital layer, which wasn't in the
original minimum plan:

- **Techs (21 in the tab, 1 granted by decision):** the 5 Gene-Seed spine techs, 5 side
  organs (Biscopea, Haemastamen, Occulobe, Betcher's Gland, Progenoid Glands), power
  armour Mk II–IV, Boltgun, Heavy Bolter, Drop Pods, Strike Cruiser, Battle Barge, and the
  Codex Adherent path. The decision-only tech is Chapter Founding, which unlocks Tactical
  Squads.
- **Decisions (13):** Establish Project, Gene-Forge, Harvest, Recover Progenoids, Choose
  Lineage (Ultramarines, Blood Angels, Imperial Fists), Found the First Chapter, the Red
  Thirst mission and Sate the Red Thirst, Drop Pod Assault, Lance Strike and Orbital
  Bombardment.
- **Supporting files:** 3 subunits (Tactical Squad, Neophyte Scouts, Apothecarion), one
  equipment line, the Astartes tech tab, decision categories, localisation and generated
  placeholder icons.

---

## Implementation notes

- Prefix every key with `sm_` to avoid clashes with other mods.
- Files:
  - `common/technology_tags/sm_astartes_tags.txt` (new folder and categories)
  - `interface/countrytechtreeview.gui` (research screen with the Astartes tab; generated)
  - `common/technologies/sm_astartes.txt`
  - `common/decisions/sm_astartes_decisions.txt` and `common/decisions/categories/sm_astartes_categories.txt`
  - `common/units/sm_astartes.txt` and `common/units/equipment/sm_power_armour.txt`
  - `common/ideas/sm_astartes_spirits.txt` (spirits applied *by* decisions)
  - `common/dynamic_modifiers/sm_astartes_modifiers.txt` (Gene-Forge and Drop Pod modifiers)
  - `localisation/english/sm_astartes_l_english.yml`
  - `interface/sm_astartes.gfx` and
    `gfx/interface/sm_astartes/` (placeholder icons)
  - `tools/check_mod.py` (static checks), `tools/make_placeholder_icons.py` and
    `tools/patch_techtree_gui.py` (builds the tech-screen override)
- Target tech modifiers at subunit names (`sm_tactical_squad = { … }`). That avoids
  adding a new unit category to vanilla's unit tags.
- Lineage bonuses use `equipment_bonus` on the `sm_power_armour` archetype, so they buff
  only Astartes battalions.
- **The tech tab needs one vanilla override.** v0.1.0 kept the tech folder's window in its
  own `interface/sm_astartes_techtree.gui`, and the research screen stopped opening. The
  folder's window (with a `sm_geneseed_sequencing_tree` gridbox) and its
  `sm_astartes_folder_tab` button have to go inside the vanilla `countrytechtreeview`
  window, so the mod overrides `interface/countrytechtreeview.gui`.
  Each folder also needs its own `techtree_<folder>_item` tech box template.
  `tools/patch_techtree_gui.py` builds that override from the vanilla file. It's the mod's
  only override.

---

## Decisions so far

- **Who can use it:** any nation, with no size requirement.
- **New units:** yes. Space Marines are new battalions with their own power armour
  equipment.
- **Tone:** keep the void and orbital layer.
- **Cap (default, open to change):** Astartes share the vanilla special-forces cap, and each
  Chapter raises its minimum by 10.

## Open questions

1. **Names.** Straight 40k names (Ultramarines, Black Carapace, Thunderhawk…) or
   "inspired-by" names? This matters if it goes on the Steam Workshop. v0.1.0 uses the
   straight names.
2. **Target version and DLC.** Which game version, and are No Step Back, By Blood Alone or
   Götterdämmerung assumed? v0.1.0 declares `supported_version="1.*"` and uses no DLC
   features.

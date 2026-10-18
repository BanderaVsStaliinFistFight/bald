# Adeptus Astartes (HOI4 mod)

Any nation can start the **Astartes Project**, research gene-seed and power armour, and
found a Chapter of Space Marines: a few elite, very expensive battalions. Orbital
operations (Drop Pod Assault, Lance Strike, Orbital Bombardment) come late in the tree.

The mod is **technologies and decisions only**. It has no focus trees, events, new
countries or map changes, and doesn't override any vanilla file, so it runs alongside
vanilla and focus-tree mods. The full design is in [IDEAS.md](IDEAS.md).

**Status: v0.1.0, first playable build. It hasn't been tested in-game yet**, so see
[Testing status](#testing-status).

## Install

1. Put this folder in your HOI4 mod folder as `adeptus_astartes`:
   - Windows: `Documents\Paradox Interactive\Hearts of Iron IV\mod\adeptus_astartes`
   - Linux: `~/.local/share/Paradox Interactive/Hearts of Iron IV/mod/adeptus_astartes`
2. Next to that folder, create `adeptus_astartes.mod` with:
   ```
   name="Adeptus Astartes"
   path="mod/adeptus_astartes"
   supported_version="1.*"
   ```
3. Enable **Adeptus Astartes** in the launcher's playset.

## How to play

1. **Decisions → The Astartes Project → Establish the Astartes Project** (100 PP).
   This reveals the **Adeptus Astartes** tech tab and gives 5 gene-seed.
2. Research **Gene-Seed Sequencing**, then requisition up to 3 **Gene-Forges** (each uses
   3 civilian factories for 120 days) and **Harvest Gene-Seed** every 60 days.
3. Research **Mk II power armour** early, so you can build up a stockpile.
4. After **Ossmodula**, choose a gene-seed lineage: Ultramarines, Blood Angels or
   Imperial Fists.
5. After **Black Carapace**, **Found the First Chapter** (150 PP, 20 gene-seed, 5k
   manpower). This unlocks Tactical Squads, raises the special-forces limit and adds a
   *1st Company* division template.
6. While at war, **Recover Progenoids** every 90 days for more gene-seed. Late techs unlock
   the orbital decisions in the **Crusade** category.

The category descriptions show your current gene-seed stockpile.

## What's in v0.1.0

| | Content |
|---|---|
| Technologies (21 in the tab + 1 granted by decision) | Gene-Seed spine (5) and side organs (5); power armour Mk II–IV; Boltgun and Heavy Bolter; Drop Pods, Strike Cruiser, Battle Barge; Codex Adherent doctrine (3) |
| Sub-units | Tactical Squad (line, special forces), Neophyte Scouts and Apothecarion (support companies) |
| Equipment | Power armour archetype with Mk II, Mk III and Mk IV |
| Decisions (13) | Establish Project, Requisition a Gene-Forge, Harvest Gene-Seed, Recover Progenoids, 3 lineage choices, Found the First Chapter, Red Thirst mission and Sate the Red Thirst, Drop Pod Assault, Lance Strike, Orbital Bombardment |
| Spirits | 3 lineages, Adeptus Astartes Chapter, The Black Rage |

All numbers are first-pass placeholders, and all icons are generated placeholders.

## Layout

| Path | Contents |
|---|---|
| `common/technology_tags/` | tech categories and the `sm_astartes_folder` tech folder |
| `common/technologies/` | all technologies |
| `common/units/`, `common/units/equipment/` | sub-units and power armour |
| `common/ideas/`, `common/dynamic_modifiers/` | spirits and modifiers applied by decisions |
| `common/decisions/` | decision categories and decisions |
| `interface/sm_astartes_techtree.gui` | window for the Astartes tech tab |
| `interface/sm_astartes.gfx`, `gfx/interface/sm_astartes/` | sprites and placeholder textures |
| `localisation/english/` | English text |
| `tools/` | checker and icon generator (not loaded by the game) |

Every key starts with `sm_`.

## Testing status

The mod was written without a copy of the game, so nothing has been run in HOI4 yet.

**Checked:** `tools/check_mod.py` passes. It parses every script file and verifies:
- cross-references between techs, units, equipment, ideas, missions and modifiers
- localisation keys and sprites
- every effect, trigger and modifier name, against the game's script documentation
  shipped with the [CWTools HOI4 rules](https://github.com/cwtools/cwtools-hoi4-config)

**Needs an in-game check, most uncertain first:**

1. **The tech tab.** Vanilla defines its tech-screen layout in
   `interface/countrytechtreeview.gui`, which I couldn't see. This mod adds its folder
   window in a separate file, `interface/sm_astartes_techtree.gui`, with a gridbox named
   `sm_geneseed_sequencing_tree`. If the tab doesn't appear, or the techs are missing or
   overlap, compare that file with a vanilla folder window (for example
   `infantry_folder`) in `countrytechtreeview.gui`. Also check whether the tab button
   needs an entry there.
2. **Icon sizes.** Placeholder textures use guessed sizes (tech 64×64, unit 48×36,
   equipment 96×48, spirit 64×64, decision 40×40).
3. **Balance.** Every cost and stat is a placeholder.

After a test run, check `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log`
for lines that mention `sm_`.

## Tools

```
python3 tools/check_mod.py                       # structure, references, localisation, sprites
python3 tools/check_mod.py --cwtools PATH        # also check effect/trigger/modifier names
python3 tools/make_placeholder_icons.py          # regenerate placeholder icons and interface/sm_astartes.gfx
```

`PATH` is a checkout of `https://github.com/cwtools/cwtools-hoi4-config`. Both scripts
need Python 3, and the icon generator also needs Pillow. To use real art, overwrite a
DDS file in `gfx/interface/sm_astartes/` and keep its filename.

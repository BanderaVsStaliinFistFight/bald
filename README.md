# Adeptus Astartes (HOI4 mod)

Any nation can start the **Astartes Project**, research gene-seed and power armour, and
found a Chapter of Space Marines: a few elite, very expensive battalions. Orbital
operations (Drop Pod Assault, Lance Strike, Orbital Bombardment) come late in the tree.

The mod is **technologies and decisions only**. It has no focus trees, events, new
countries or map changes, and doesn't override any vanilla file, so it runs alongside
vanilla and focus-tree mods. The full design is in [IDEAS.md](IDEAS.md).

**Status: v0.1.1.** The Astartes technologies are missing from the research screen in
this build. v0.1.0's Astartes tech tab stopped the research screen from opening, so the
tab is removed until it's rebuilt. See [Known issue](#known-issue-no-astartes-tech-tab).

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
   This unlocks the Astartes techs and gives 5 gene-seed. In v0.1.1 the techs aren't in
   the research screen, so use the console for now (see [Known issue](#known-issue-no-astartes-tech-tab)).
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

## What's in v0.1.1

| | Content |
|---|---|
| Technologies (21 researchable + 1 granted by decision; not in the research screen yet) | Gene-Seed spine (5) and side organs (5); power armour Mk II–IV; Boltgun and Heavy Bolter; Drop Pods, Strike Cruiser, Battle Barge; Codex Adherent doctrine (3) |
| Sub-units | Tactical Squad (line, special forces), Neophyte Scouts and Apothecarion (support companies) |
| Equipment | Power armour archetype with Mk II, Mk III and Mk IV |
| Decisions (13) | Establish Project, Requisition a Gene-Forge, Harvest Gene-Seed, Recover Progenoids, 3 lineage choices, Found the First Chapter, Red Thirst mission and Sate the Red Thirst, Drop Pod Assault, Lance Strike, Orbital Bombardment |
| Spirits | 3 lineages, Adeptus Astartes Chapter, The Black Rage |

All numbers are first-pass placeholders, and all icons are generated placeholders.

## Layout

| Path | Contents |
|---|---|
| `common/technologies/` | all technologies |
| `common/units/`, `common/units/equipment/` | sub-units and power armour |
| `common/ideas/`, `common/dynamic_modifiers/` | spirits and modifiers applied by decisions |
| `common/decisions/` | decision categories and decisions |
| `interface/sm_astartes.gfx`, `gfx/interface/sm_astartes/` | sprites and placeholder textures |
| `localisation/english/` | English text |
| `tools/` | checker, icon generator and tech-screen patcher (not loaded by the game) |

Every key starts with `sm_`.

## Known issue: no Astartes tech tab

A new tab needs two things inside the vanilla `countrytechtreeview` window of
`interface/countrytechtreeview.gui`:
- a window named after the folder, holding a gridbox named after the tree's first tech
  (`sm_geneseed_sequencing_tree`)
- a button named `sm_astartes_folder_tab` in `folder_tabs`

v0.1.0 put the window in a separate file, so the game never found it and the research
screen wouldn't open. v0.1.1 removes the tab, so the Astartes techs don't appear in the
research screen at all.

The fix is ready but needs the current vanilla `interface/countrytechtreeview.gui` from
your game install. It changes between game versions and isn't public, so the mod has to
build its override from your copy:

```
python3 tools/patch_techtree_gui.py "<HOI4 install folder>"
```

This copies a vanilla folder's frame into a new `sm_astartes_folder` window and adds the
tab after the last vanilla tab. Everything else in the file stays vanilla. Then the
folder goes back into `common/technology_tags/` and the techs get their tab positions
back (layout: commit `1cbfa9a`).

Until then, you can test the rest of the mod with the console (`~`). The `research`
command should grant a tech by name, for example:

```
research sm_geneseed_sequencing
research sm_ossmodula
research sm_black_carapace
research sm_mk2_crusade_armour
research sm_drop_pods
```

## Testing status

The mod was written without a copy of the game. `tools/check_mod.py` passes. It parses
every script file and verifies:
- cross-references between techs, units, equipment, ideas, missions and modifiers
- localisation keys and sprites
- every effect, trigger and modifier name, against the game's script documentation
  shipped with the [CWTools HOI4 rules](https://github.com/cwtools/cwtools-hoi4-config)

**Still needs an in-game check:**

1. **Icon sizes.** Placeholder textures use guessed sizes (tech 64×64, unit 48×36,
   equipment 96×48, spirit 64×64, decision 40×40).
2. **Balance.** Every cost and stat is a placeholder.

After a test run, check `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log`
for lines that mention `sm_`.

## Tools

```
python3 tools/check_mod.py                       # structure, references, localisation, sprites
python3 tools/check_mod.py --cwtools PATH        # also check effect/trigger/modifier names
python3 tools/make_placeholder_icons.py          # regenerate placeholder icons and interface/sm_astartes.gfx
python3 tools/patch_techtree_gui.py GAME_DIR     # build interface/countrytechtreeview.gui with the Astartes tab
```

`PATH` is a checkout of `https://github.com/cwtools/cwtools-hoi4-config`. `GAME_DIR` is
your HOI4 install folder; re-run the patch after a game update changes the tech screen. Both scripts
need Python 3, and the icon generator also needs Pillow. To use real art, overwrite a
DDS file in `gfx/interface/sm_astartes/` and keep its filename.

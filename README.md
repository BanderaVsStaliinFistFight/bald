# Adeptus Astartes (HOI4 mod)

Any nation can start the **Astartes Project**, research gene-seed and power armour, and
found a Chapter of Space Marines: a few elite, very expensive battalions. Orbital
operations (Drop Pod Assault, Lance Strike, Orbital Bombardment) come late in the tree.

The mod is **technologies and decisions only**. It has no focus trees, events, new
countries or map changes. Its one vanilla override is the research screen's layout, so it
runs alongside vanilla and focus-tree mods (see [The tech tab](#the-tech-tab)). The full
design is in [IDEAS.md](IDEAS.md).

**Status: v0.1.3.** v0.1.2's Astartes tab showed up in-game but was empty. v0.1.3 gives
the tab's tech grid an explicit size and shows the techs from game start. Not yet
confirmed in-game.

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
   This unlocks the Gene-Forge and Chapter Founding decisions, speeds up Gene-Seed
   Sequencing and gives 5 gene-seed. The Astartes techs are in the **40K** tab of the
   research screen from the start.
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

## What's in v0.1.3

| | Content |
|---|---|
| Technologies (21 in the tab + 1 granted by decision) | Gene-Seed spine (5) and side organs (5); power armour Mk II–IV; Boltgun and Heavy Bolter; Drop Pods, Strike Cruiser, Battle Barge; Codex Adherent doctrine (3) |
| Sub-units | Tactical Squad (line, special forces), Neophyte Scouts and Apothecarion (support companies) |
| Equipment | Power armour archetype with Mk II, Mk III and Mk IV |
| Decisions (13) | Establish Project, Requisition a Gene-Forge, Harvest Gene-Seed, Recover Progenoids, 3 lineage choices, Found the First Chapter, Red Thirst mission and Sate the Red Thirst, Drop Pod Assault, Lance Strike, Orbital Bombardment |
| Spirits | 3 lineages, Adeptus Astartes Chapter, The Black Rage |

All numbers are first-pass placeholders. The icons are generated from a helmet silhouette
(see [Icons](#icons)).

## Layout

| Path | Contents |
|---|---|
| `common/technology_tags/` | tech categories and the `sm_astartes_folder` tech folder |
| `common/technologies/` | all technologies |
| `common/units/`, `common/units/equipment/` | sub-units and power armour |
| `common/ideas/`, `common/dynamic_modifiers/` | spirits and modifiers applied by decisions |
| `common/decisions/` | decision categories and decisions |
| `interface/countrytechtreeview.gui` | research screen with the Astartes tab (generated, see below) |
| `interface/sm_astartes.gfx`, `gfx/interface/sm_astartes/` | sprites and their textures (generated) |
| `thumbnail.png` | launcher and Steam Workshop picture (generated) |
| `localisation/english/` | English text |
| `tools/` | checker, icon generator, tech-screen patcher and source art (not loaded by the game) |

Every key starts with `sm_`.

## The tech tab

The research screen only finds a tab if it's defined inside the vanilla
`countrytechtreeview` window of `interface/countrytechtreeview.gui`. So the mod ships its
own copy of that file, generated from the vanilla file of the current game (October 2026)
by `tools/patch_techtree_gui.py`. The copy adds:
- the `sm_astartes_folder` window, with the frame of the vanilla industry tab and a
  `sm_geneseed_sequencing_tree` gridbox for the Astartes tree (sized like vanilla's
  top-to-bottom grids)
- the `sm_astartes_folder_tab` button after the industry tab
- `techtree_sm_astartes_folder_item` and `techtree_sm_astartes_folder_small_item` tech
  boxes, copied from the industry and armour tabs

Everything else in the file is unchanged vanilla. v0.1.0 put the tab's window in a
separate file instead; the game never found it, and the research screen wouldn't open.

**After a game update** that changes the research screen, regenerate the file from the
updated game, or the research screen may break:

```
python3 tools/patch_techtree_gui.py "<HOI4 install folder>"
```

**Compatibility:** other mods that override `interface/countrytechtreeview.gui` conflict
with this one. Whichever loads last wins, and the other mod's tabs or the Astartes tab go
missing.

## Testing status

The mod was written without a copy of the game. `tools/check_mod.py` passes. It parses
every script file and verifies:
- cross-references between techs, units, equipment, ideas, missions and modifiers
- localisation keys and sprites
- every effect, trigger and modifier name, against the game's script documentation
  shipped with the [CWTools HOI4 rules](https://github.com/cwtools/cwtools-hoi4-config)

**Still needs an in-game check:**

1. **The tech tab.** The tab, its window and tech boxes are built from your game's file,
   but the layout and the 40K tab button haven't been seen in-game.
2. **Icon sizes.** The textures use guessed sizes (tech 64×64, unit 48×36, equipment
   96×48, spirit 64×64, decision 40×40, tab 2×86×30).
3. **Balance.** Every cost and stat is a placeholder.

After a test run, check `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log`
for lines that mention `sm_`.

## Tools

```
python3 tools/check_mod.py                       # structure, references, localisation, sprites
python3 tools/check_mod.py --cwtools PATH        # also check effect/trigger/modifier names
python3 tools/make_icons.py                      # regenerate icons, interface/sm_astartes.gfx and thumbnail.png
python3 tools/patch_techtree_gui.py GAME_DIR     # build interface/countrytechtreeview.gui with the Astartes tab
```

`PATH` is a checkout of `https://github.com/cwtools/cwtools-hoi4-config`. `GAME_DIR` is
your HOI4 install folder. The scripts need Python 3, and the icon generator also needs
Pillow.

## Icons

`tools/make_icons.py` draws every icon from `tools/art/helmet.png`, a Space Marine helmet
silhouette. The helmet's lenses and grille are recoloured per use:
- **Lineage spirits:** Ultramarines blue, Blood Angels red with gold lenses, Imperial Fists
  yellow; the Chapter spirit is silver and the Black Rage is black with red eyes.
- **Units, power armour, the 40K tab, the Chapter decisions and `thumbnail.png`** also use
  the helmet.
- **Techs** get a symbol per branch instead: a DNA helix for gene-seed, a helmet for
  power armour, bolt shells for weapons, a planet with an orbit for void assets and a
  book for the Codex. Each has a short label.

To use hand-made art for one icon, overwrite its DDS in `gfx/interface/sm_astartes/`
(keep the filename and size) and remove its entry from `SPRITES` in the script.

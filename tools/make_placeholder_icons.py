#!/usr/bin/env python3
"""Generate placeholder icons and interface/sm_astartes.gfx for the Adeptus Astartes mod.

Every sprite the mod references gets a small labelled DDS (uncompressed A8R8G8B8)
under gfx/interface/sm_astartes/. To use real art, overwrite a DDS with the same
filename; the .gfx entries don't need to change.

Usage (from the mod root):  python3 tools/make_placeholder_icons.py
Requires Pillow.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
TEXTURE_DIR = "gfx/interface/sm_astartes"
GFX_FILE = ROOT / "interface" / "sm_astartes.gfx"

# Branch colours.
GENESEED = (139, 26, 26)
WARGEAR = (47, 79, 111)
VOID = (75, 42, 107)
CODEX = (138, 109, 31)
CHAPTER = (36, 64, 110)

TECH = (64, 64)
EQUIPMENT = (96, 48)
UNIT = (48, 36)
IDEA = (64, 64)
DECISION = (40, 40)

# (sprite name, texture file stem, size, background, label, text colour)
SPRITES = [
    # Technologies: GFX_<tech>_medium
    ("GFX_sm_geneseed_sequencing_medium", "tech_geneseed_sequencing", TECH, GENESEED, "GS"),
    ("GFX_sm_secondary_heart_medium", "tech_secondary_heart", TECH, GENESEED, "HRT"),
    ("GFX_sm_ossmodula_medium", "tech_ossmodula", TECH, GENESEED, "OSS"),
    ("GFX_sm_larramans_organ_medium", "tech_larramans_organ", TECH, GENESEED, "LAR"),
    ("GFX_sm_black_carapace_medium", "tech_black_carapace", TECH, GENESEED, "BC"),
    ("GFX_sm_biscopea_medium", "tech_biscopea", TECH, GENESEED, "BIS"),
    ("GFX_sm_haemastamen_medium", "tech_haemastamen", TECH, GENESEED, "HAE"),
    ("GFX_sm_occulobe_medium", "tech_occulobe", TECH, GENESEED, "OCC"),
    ("GFX_sm_betchers_gland_medium", "tech_betchers_gland", TECH, GENESEED, "BET"),
    ("GFX_sm_progenoid_glands_medium", "tech_progenoid_glands", TECH, GENESEED, "PRO"),
    ("GFX_sm_mk2_crusade_armour_medium", "tech_mk2_crusade_armour", TECH, WARGEAR, "MkII"),
    ("GFX_sm_mk3_iron_armour_medium", "tech_mk3_iron_armour", TECH, WARGEAR, "MkIII"),
    ("GFX_sm_mk4_maximus_armour_medium", "tech_mk4_maximus_armour", TECH, WARGEAR, "MkIV"),
    ("GFX_sm_boltgun_medium", "tech_boltgun", TECH, WARGEAR, "BOLT"),
    ("GFX_sm_heavy_bolter_medium", "tech_heavy_bolter", TECH, WARGEAR, "HB"),
    ("GFX_sm_drop_pods_medium", "tech_drop_pods", TECH, VOID, "POD"),
    ("GFX_sm_strike_cruiser_medium", "tech_strike_cruiser", TECH, VOID, "SC"),
    ("GFX_sm_battle_barge_medium", "tech_battle_barge", TECH, VOID, "BB"),
    ("GFX_sm_combat_squads_medium", "tech_combat_squads", TECH, CODEX, "CS"),
    ("GFX_sm_battle_company_doctrine_medium", "tech_battle_company_doctrine", TECH, CODEX, "BCO"),
    ("GFX_sm_chapter_masters_council_medium", "tech_chapter_masters_council", TECH, CODEX, "CMC"),
    # Equipment: GFX_<equipment>_medium
    ("GFX_sm_power_armour_medium", "equipment_power_armour", EQUIPMENT, WARGEAR, "PA"),
    ("GFX_sm_power_armour_1_medium", "equipment_power_armour_1", EQUIPMENT, WARGEAR, "Mk II"),
    ("GFX_sm_power_armour_2_medium", "equipment_power_armour_2", EQUIPMENT, WARGEAR, "Mk III"),
    ("GFX_sm_power_armour_3_medium", "equipment_power_armour_3", EQUIPMENT, WARGEAR, "Mk IV"),
    # Sub-units in the division designer: GFX_unit_<sub-unit>_icon_medium
    ("GFX_unit_sm_tactical_squad_icon_medium", "unit_tactical_squad", UNIT, CHAPTER, "TAC"),
    ("GFX_unit_sm_neophyte_scouts_icon_medium", "unit_neophyte_scouts", UNIT, CHAPTER, "SCT"),
    ("GFX_unit_sm_apothecarion_icon_medium", "unit_apothecarion", UNIT, CHAPTER, "APO"),
    # National spirits: GFX_idea_<idea>
    ("GFX_idea_sm_lineage_ultramarines", "idea_lineage_ultramarines", IDEA, (31, 79, 160), "UM"),
    ("GFX_idea_sm_lineage_blood_angels", "idea_lineage_blood_angels", IDEA, (160, 24, 24), "BA"),
    ("GFX_idea_sm_lineage_imperial_fists", "idea_lineage_imperial_fists", IDEA, (201, 165, 0), "IF", (20, 20, 20)),
    ("GFX_idea_sm_adeptus_astartes_chapter", "idea_adeptus_astartes_chapter", IDEA, (90, 90, 100), "SM"),
    ("GFX_idea_sm_black_rage", "idea_black_rage", IDEA, (15, 15, 15), "RAGE", (200, 30, 30)),
    # Decisions: GFX_decision_<icon>, categories: GFX_decision_category_<icon>
    ("GFX_decision_sm_geneseed", "decision_geneseed", DECISION, GENESEED, "GS"),
    ("GFX_decision_sm_chapter", "decision_chapter", DECISION, CHAPTER, "CH"),
    ("GFX_decision_sm_orbital", "decision_orbital", DECISION, VOID, "ORB"),
    ("GFX_decision_category_sm_astartes", "decision_category_astartes", DECISION, (90, 90, 100), "SM"),
    # Same texture under the decision naming, in case categories resolve `icon` like decisions do.
    ("GFX_decision_sm_astartes", "decision_category_astartes", DECISION, (90, 90, 100), "SM"),
]

# Research-screen folder tab: two frames side by side (normal, selected), like vanilla
# folder tabs. 86x30 per frame fits vanilla's 89px tab spacing.
TAB = ("GFX_sm_astartes_folder_tab", "techtree_astartes_tab", (86, 30), CHAPTER, "40K")


def fit_font(draw, text, width, height):
    """Largest default font size whose rendering of text fits inside width x height."""
    size = height
    while size > 6:
        font = ImageFont.load_default(size=size)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        if right - left <= width and bottom - top <= height:
            return font
        size -= 1
    return ImageFont.load_default(size=6)


def make_icon(size, background, label, text_colour):
    w, h = size
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    radius = max(3, min(w, h) // 8)
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=background + (255,),
                           outline=(220, 200, 150, 255), width=max(1, min(w, h) // 24))
    font = fit_font(draw, label, int(w * 0.8), int(h * 0.55))
    draw.text((w / 2, h / 2), label, font=font, fill=text_colour + (255,), anchor="mm")
    return image


def make_tab(frame_size, background, label):
    w, h = frame_size
    image = Image.new("RGBA", (w * 2, h), (0, 0, 0, 0))
    image.paste(make_icon(frame_size, background, label, (240, 230, 210)), (0, 0))
    selected = tuple(min(255, c + 60) for c in background)
    image.paste(make_icon(frame_size, selected, label, (255, 255, 255)), (w, 0))
    return image


def main():
    out_dir = ROOT / TEXTURE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Generated by tools/make_placeholder_icons.py. Re-run it after adding sprites there.",
        "# Placeholder art: overwrite the DDS files to use real icons.",
        "spriteTypes = {",
    ]
    for entry in SPRITES:
        name, stem, size, background, label = entry[:5]
        text_colour = entry[5] if len(entry) > 5 else (240, 230, 210)
        make_icon(size, background, label, text_colour).save(out_dir / f"{stem}.dds")
        lines += [
            "\tspriteType = {",
            f'\t\tname = "{name}"',
            f'\t\ttexturefile = "{TEXTURE_DIR}/{stem}.dds"',
            "\t}",
        ]
    name, stem, size, background, label = TAB
    make_tab(size, background, label).save(out_dir / f"{stem}.dds")
    lines += [
        "\tspriteType = {",
        f'\t\tname = "{name}"',
        f'\t\ttexturefile = "{TEXTURE_DIR}/{stem}.dds"',
        "\t\tnoOfFrames = 2",
        "\t}",
    ]
    lines.append("}")
    GFX_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(SPRITES) + 1} icons to {TEXTURE_DIR} and {GFX_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

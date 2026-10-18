#!/usr/bin/env python3
"""Generate the Adeptus Astartes icons, interface/sm_astartes.gfx and thumbnail.png.

The art is built from tools/art/helmet.png, a Space Marine helmet silhouette. Its alpha
channel is the helmet, the transparent seams show the background, the enclosed grille
slots take a detail colour and the two eye lenses (separate opaque pieces) take a lens
colour. Techs get branch symbols drawn in code instead (gene-seed helix, bolt shell,
planet and orbit, Codex book), so the tree doesn't show the same helmet 21 times.

Every texture is an uncompressed A8R8G8B8 DDS in gfx/interface/sm_astartes/. To use
hand-made art for one, overwrite its DDS and drop its entry from SPRITES.

Usage (from the mod root):  python3 tools/make_icons.py
Requires Pillow.
"""

import math
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
HELMET = ROOT / "tools" / "art" / "helmet.png"
TEXTURE_DIR = "gfx/interface/sm_astartes"
GFX_FILE = ROOT / "interface" / "sm_astartes.gfx"
THUMBNAIL = ROOT / "thumbnail.png"
FONTS = (
    "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)
SS = 4  # shapes and text are drawn at 4x and scaled down, for clean edges

# Branch colours.
GENESEED = (139, 26, 26)
WARGEAR = (47, 79, 111)
VOID = (75, 42, 107)
CODEX = (138, 109, 31)
CHAPTER = (36, 64, 110)
STEEL = (88, 92, 104)

GOLD = (214, 180, 96)
BONE = (236, 226, 204)
DARK = (18, 18, 22)
RED_LENS = (235, 45, 30)
GREEN_LENS = (90, 230, 120)
GOLD_LENS = (255, 205, 70)

TECH = (64, 64)
EQUIPMENT = (96, 48)
UNIT = (48, 36)
IDEA = (64, 64)
DECISION = (40, 40)
TAB_FRAME = (86, 30)


# --- helpers -----------------------------------------------------------------------

def shade(colour, amount):
    """Lighten (amount > 0) or darken (amount < 0) a colour."""
    if amount >= 0:
        return tuple(round(c + (255 - c) * amount) for c in colour)
    return tuple(round(c * (1 + amount)) for c in colour)


@lru_cache(maxsize=None)
def font(size):
    for path in FONTS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def fit_font(draw, text, width, height):
    """Largest font size whose rendering of text fits inside width x height."""
    size = max(6, int(height * 1.4))
    while size > 6:
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font(size))
        if right - left <= width and bottom - top <= height:
            break
        size -= 1
    return font(size)


def downscale(image, size):
    return image.resize(size, Image.LANCZOS)


def tile(size, colour, radius_ratio=0.14, border=True):
    """Rounded tile with a vertical gradient, dark outline and gold inner line (at SS)."""
    w, h = size[0] * SS, size[1] * SS
    gradient = Image.new("RGBA", (w, h))
    top, bottom = shade(colour, 0.22), shade(colour, -0.45)
    gd = ImageDraw.Draw(gradient)
    for y in range(h):
        t = y / max(1, h - 1)
        gd.line([(0, y), (w, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)) + (255,))
    radius = int(min(w, h) * radius_ratio)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    image.paste(gradient, mask=mask)
    if border:
        d = ImageDraw.Draw(image)
        outline = max(SS, min(w, h) // 32)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, outline=DARK + (255,), width=outline)
        inset = outline + SS // 2
        d.rounded_rectangle((inset, inset, w - 1 - inset, h - 1 - inset), radius=max(1, radius - inset),
                            outline=GOLD + (255,), width=max(1, SS // 2 + 1))
    return image


def label(image, text, band=0.30, colour=BONE):
    """Dark band across the bottom of an SS image with the text centred in it."""
    w, h = image.size
    band_h = int(h * band)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    inset = max(SS * 2, w // 16)
    od.rectangle((inset, h - band_h - inset // 2, w - inset, h - inset), fill=(0, 0, 0, 150))
    image.alpha_composite(overlay)
    d = ImageDraw.Draw(image)
    f = fit_font(d, text, int(w * 0.8), int(band_h * 0.62))
    centre = (w / 2, h - inset - (band_h - inset // 2) / 2)
    d.text((centre[0] + SS // 2, centre[1] + SS // 2), text, font=f, fill=(0, 0, 0, 200), anchor="mm")
    d.text(centre, text, font=f, fill=colour + (255,), anchor="mm")
    return image


# --- helmet ------------------------------------------------------------------------

def components(mask):
    """Connected opaque regions of a binary mask, as (pixel count, pixel list)."""
    w, h = mask.size
    px = mask.load()
    seen = set()
    found = []
    for y in range(h):
        for x in range(w):
            if px[x, y] and (x, y) not in seen:
                stack, pixels = [(x, y)], []
                seen.add((x, y))
                while stack:
                    cx, cy = stack.pop()
                    pixels.append((cx, cy))
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and px[nx, ny] and (nx, ny) not in seen:
                            seen.add((nx, ny))
                            stack.append((nx, ny))
                found.append((len(pixels), pixels))
    return found


@lru_cache(maxsize=None)
def helmet_masks():
    """(body, lenses, grille) masks of the helmet, cropped to it and padded square.

    The parts are found on a hard-edged copy of the alpha, then take their edges from the
    source's anti-aliased alpha, so the helmet scales up smoothly."""
    soft = Image.open(HELMET).convert("RGBA").getchannel("A")
    alpha = soft.point(lambda v: 255 if v >= 128 else 0)
    # Grille: transparent pixels that the outside can't reach.
    outside = alpha.point(lambda v: 0 if v else 255)
    ImageDraw.floodfill(outside, (0, 0), 128)
    grille = outside.point(lambda v: 255 if v == 255 else 0)
    # Lenses: the two small opaque pieces in the eye band.
    left, top, right, bottom = alpha.getbbox()
    height = bottom - top
    lenses = Image.new("L", alpha.size, 0)
    lp = lenses.load()
    for count, pixels in components(alpha):
        ys = [p[1] for p in pixels]
        middle = ((min(ys) + max(ys)) / 2 - top) / height
        if 0.002 * alpha.size[0] * alpha.size[1] < count < 0.03 * alpha.size[0] * alpha.size[1] \
                and 0.3 < middle < 0.6:
            for p in pixels:
                lp[p] = 255
    grow = ImageFilter.MaxFilter(3)
    lenses = ImageChops.darker(soft, lenses.filter(grow))
    body = ImageChops.subtract(soft, lenses)
    grille = ImageChops.darker(ImageChops.invert(soft), grille.filter(grow))

    side = max(right - left, bottom - top)
    box = (left - (side - (right - left)) // 2, top - (side - (bottom - top)) // 2)
    def square(mask):
        out = Image.new("L", (side, side), 0)
        out.paste(mask.crop((left, top, right, bottom)), (left - box[0], top - box[1]))
        return out
    return square(body), square(lenses), square(grille)


def smooth_mask(mask, side):
    """Upscale an anti-aliased mask to side x side, keeping its edges smooth and crisp."""
    if side <= mask.width:
        return mask
    soft = mask.resize((side, side), Image.BICUBIC)
    return soft.point(lambda v: 0 if v < 64 else 255 if v > 192 else (v - 64) * 255 // 128)


def helmet(size, body, lens=RED_LENS, detail=None):
    """RGBA helmet scaled to size (square), lenses and grille coloured."""
    # Draw at twice the target size (at least the source size), then scale down.
    side = max(helmet_masks()[0].width, size * 2)
    body_mask, lens_mask, grille_mask = (smooth_mask(m, side) for m in helmet_masks())
    layer = Image.new("RGBA", body_mask.size, (0, 0, 0, 0))
    layer.paste(body + (255,), mask=body_mask)
    layer.paste(lens + (255,), mask=lens_mask)
    if detail:
        layer.paste(detail + (255,), mask=grille_mask)
    return layer.resize((size, size), Image.LANCZOS)


def paste_centred(image, overlay, centre):
    image.alpha_composite(overlay, (int(centre[0] - overlay.width / 2), int(centre[1] - overlay.height / 2)))


# --- symbols (drawn at SS into a box) ----------------------------------------------

def draw_helix(image, box, colour):
    d = ImageDraw.Draw(image)
    x0, y0, x1, y1 = box
    cx, amp, w = (x0 + x1) / 2, (x1 - x0) * 0.32, max(SS, int((x1 - x0) * 0.09))
    steps = 60
    strands = [[], []]
    for i in range(steps + 1):
        t = i / steps
        y = y0 + (y1 - y0) * t
        phase = t * math.pi * 3
        strands[0].append((cx + amp * math.sin(phase), y))
        strands[1].append((cx - amp * math.sin(phase), y))
    for i in range(1, 12):
        t = i / 12
        y = y0 + (y1 - y0) * t
        dx = amp * math.sin(t * math.pi * 3)
        if abs(dx) > amp * 0.25:
            d.line([(cx - dx, y), (cx + dx, y)], fill=shade(colour, -0.25) + (255,), width=max(1, w // 2))
    d.line(strands[1], fill=shade(colour, -0.1) + (255,), width=w, joint="curve")
    d.line(strands[0], fill=colour + (255,), width=w, joint="curve")


def draw_shell(image, box, colour, count=1):
    d = ImageDraw.Draw(image)
    x0, y0, x1, y1 = box
    width = (x1 - x0) / (count * 1.6 + 0.4)
    for i in range(count):
        left = x0 + width * 0.4 + i * width * 1.6 + (x1 - x0 - width * (count * 1.6 - 0.2)) / 2 - width * 0.2
        right = left + width
        nose = y0 + (y1 - y0) * 0.38
        d.rounded_rectangle((left, nose, right, y1), radius=width * 0.15, fill=colour + (255,))
        d.pieslice((left, y0, right, nose + (nose - y0)), 180, 360, fill=shade(colour, 0.25) + (255,))
        band = y1 - (y1 - y0) * 0.18
        d.rectangle((left, band, right, band + (y1 - y0) * 0.06), fill=shade(colour, -0.4) + (255,))


def draw_planet(image, box, colour):
    d = ImageDraw.Draw(image)
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = (x1 - x0) * 0.27
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=colour + (255,))
    d.chord((cx - r, cy - r, cx + r, cy + r), 300, 120, fill=shade(colour, -0.3) + (255,))
    ring = max(SS, int(r * 0.12))
    d.ellipse((x0, cy - r * 0.45, x1, cy + r * 0.45), outline=GOLD + (255,), width=ring)
    d.chord((cx - r, cy - r, cx + r, cy + r), 180, 360, fill=colour + (255,))
    pod = r * 0.22
    px, py = x1 - (x1 - x0) * 0.12, cy - r * 0.2
    d.ellipse((px - pod, py - pod, px + pod, py + pod), fill=BONE + (255,))


def draw_book(image, box, colour):
    d = ImageDraw.Draw(image)
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    lift = (y1 - y0) * 0.12
    d.polygon([(x0, y0 + lift), (cx, y0 + lift * 2), (cx, y1), (x0, y1 - lift)], fill=colour + (255,))
    d.polygon([(x1, y0 + lift), (cx, y0 + lift * 2), (cx, y1), (x1, y1 - lift)], fill=shade(colour, -0.12) + (255,))
    line = max(1, SS // 2 + 1)
    for i in range(1, 5):
        t = i / 5
        y = y0 + lift * 2 + (y1 - y0 - lift * 3) * t
        d.line([(x0 + (cx - x0) * 0.15, y - lift * (1 - t) * 0.5), (cx - (cx - x0) * 0.1, y)],
               fill=shade(colour, -0.45) + (255,), width=line)
        d.line([(x1 - (x1 - cx) * 0.15, y - lift * (1 - t) * 0.5), (cx + (x1 - cx) * 0.1, y)],
               fill=shade(colour, -0.45) + (255,), width=line)
    d.line([(cx, y0 + lift * 2), (cx, y1)], fill=GOLD + (255,), width=line * 2)


SYMBOLS = {
    "helix": lambda img, box: draw_helix(img, box, BONE),
    "shell": lambda img, box: draw_shell(img, box, GOLD),
    "shells": lambda img, box: draw_shell(img, box, GOLD, count=2),
    "planet": lambda img, box: draw_planet(img, box, shade(VOID, 0.45)),
    "book": lambda img, box: draw_book(img, box, BONE),
}


# --- icon painters (each returns the final-size RGBA image) -------------------------

def tech_icon(colour, symbol, text):
    def paint(size):
        image = tile(size, colour)
        w, h = image.size
        box = (w * 0.24, h * 0.1, w * 0.76, h * 0.64)
        if symbol == "helmet":
            paste_centred(image, helmet(int(h * 0.58), shade(STEEL, 0.35), RED_LENS), (w / 2, h * 0.38))
        else:
            SYMBOLS[symbol](image, box)
        return downscale(label(image, text), size)
    return paint


def helmet_icon(colour, body, lens, detail=None, scale=0.78, text=None, badge=None):
    def paint(size):
        image = tile(size, colour)
        w, h = image.size
        centre_y = h * (0.4 if text else 0.52)
        paste_centred(image, helmet(int(min(w, h) * (scale - (0.14 if text else 0))), body, lens, detail),
                      (w / 2, centre_y))
        if badge == "cross":
            d = ImageDraw.Draw(image)
            s, cx, cy = min(w, h) * 0.13, w * 0.8, h * 0.24
            d.rectangle((cx - s, cy - s * 0.35, cx + s, cy + s * 0.35), fill=(210, 30, 30, 255))
            d.rectangle((cx - s * 0.35, cy - s, cx + s * 0.35, cy + s), fill=(210, 30, 30, 255))
        if text:
            label(image, text)
        return downscale(image, size)
    return paint


def symbol_icon(colour, symbol):
    def paint(size):
        image = tile(size, colour)
        w, h = image.size
        SYMBOLS[symbol](image, (w * 0.2, h * 0.18, w * 0.8, h * 0.82))
        return downscale(image, size)
    return paint


def equipment_icon(text):
    def paint(size):
        image = tile(size, WARGEAR, radius_ratio=0.18)
        w, h = image.size
        paste_centred(image, helmet(int(h * 0.82), shade(STEEL, 0.35), RED_LENS), (w * 0.27, h / 2))
        d = ImageDraw.Draw(image)
        f = fit_font(d, text, int(w * 0.48), int(h * 0.42))
        d.text((w * 0.72 + SS, h / 2 + SS), text, font=f, fill=(0, 0, 0, 200), anchor="mm")
        d.text((w * 0.72, h / 2), text, font=f, fill=BONE + (255,), anchor="mm")
        return downscale(image, size)
    return paint


def tab_image(frame_size):
    """Two frames side by side, normal then selected, like vanilla folder tabs."""
    w, h = frame_size
    image = Image.new("RGBA", (w * 2, h), (0, 0, 0, 0))
    for frame, colour in enumerate((shade(CHAPTER, -0.15), shade(CHAPTER, 0.25))):
        big = tile(frame_size, colour, radius_ratio=0.25)
        bw, bh = big.size
        paste_centred(big, helmet(int(bh * 0.8), shade(STEEL, 0.5), RED_LENS), (bw * 0.26, bh / 2))
        d = ImageDraw.Draw(big)
        f = fit_font(d, "40K", int(bw * 0.42), int(bh * 0.5))
        d.text((bw * 0.66, bh / 2), "40K", font=f, fill=BONE + (255,), anchor="mm")
        image.paste(downscale(big, frame_size), (w * frame, 0))
    return image


def thumbnail(size=512):
    """Launcher / Steam Workshop picture."""
    image = tile((size, size), (24, 30, 44), radius_ratio=0.0, border=False)
    w, h = image.size
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((w * 0.12, h * 0.04, w * 0.88, h * 0.8), fill=shade(CHAPTER, 0.1) + (120,))
    image.alpha_composite(glow)
    paste_centred(image, helmet(int(h * 0.62), (31, 79, 160), RED_LENS, BONE), (w / 2, h * 0.41))
    d = ImageDraw.Draw(image)
    f = fit_font(d, "ADEPTUS ASTARTES", int(w * 0.86), int(h * 0.1))
    d.text((w / 2 + SS * 2, h * 0.84 + SS * 2), "ADEPTUS ASTARTES", font=f, fill=(0, 0, 0, 220), anchor="mm")
    d.text((w / 2, h * 0.84), "ADEPTUS ASTARTES", font=f, fill=GOLD + (255,), anchor="mm")
    f2 = fit_font(d, "TECHNOLOGIES & DECISIONS", int(w * 0.6), int(h * 0.045))
    d.text((w / 2, h * 0.93), "TECHNOLOGIES & DECISIONS", font=f2, fill=BONE + (255,), anchor="mm")
    return downscale(image, (size, size)).convert("RGB")


# --- sprites ---------------------------------------------------------------------

# (sprite name, texture file stem, size, painter)
SPRITES = [
    # Technologies: GFX_<tech>_medium
    ("GFX_sm_geneseed_sequencing_medium", "tech_geneseed_sequencing", TECH, tech_icon(GENESEED, "helix", "GS")),
    ("GFX_sm_secondary_heart_medium", "tech_secondary_heart", TECH, tech_icon(GENESEED, "helix", "HRT")),
    ("GFX_sm_ossmodula_medium", "tech_ossmodula", TECH, tech_icon(GENESEED, "helix", "OSS")),
    ("GFX_sm_larramans_organ_medium", "tech_larramans_organ", TECH, tech_icon(GENESEED, "helix", "LAR")),
    ("GFX_sm_black_carapace_medium", "tech_black_carapace", TECH, tech_icon(GENESEED, "helix", "BC")),
    ("GFX_sm_biscopea_medium", "tech_biscopea", TECH, tech_icon(GENESEED, "helix", "BIS")),
    ("GFX_sm_haemastamen_medium", "tech_haemastamen", TECH, tech_icon(GENESEED, "helix", "HAE")),
    ("GFX_sm_occulobe_medium", "tech_occulobe", TECH, tech_icon(GENESEED, "helix", "OCC")),
    ("GFX_sm_betchers_gland_medium", "tech_betchers_gland", TECH, tech_icon(GENESEED, "helix", "BET")),
    ("GFX_sm_progenoid_glands_medium", "tech_progenoid_glands", TECH, tech_icon(GENESEED, "helix", "PRO")),
    ("GFX_sm_mk2_crusade_armour_medium", "tech_mk2_crusade_armour", TECH, tech_icon(WARGEAR, "helmet", "Mk II")),
    ("GFX_sm_mk3_iron_armour_medium", "tech_mk3_iron_armour", TECH, tech_icon(WARGEAR, "helmet", "Mk III")),
    ("GFX_sm_mk4_maximus_armour_medium", "tech_mk4_maximus_armour", TECH, tech_icon(WARGEAR, "helmet", "Mk IV")),
    ("GFX_sm_boltgun_medium", "tech_boltgun", TECH, tech_icon(WARGEAR, "shell", "BOLT")),
    ("GFX_sm_heavy_bolter_medium", "tech_heavy_bolter", TECH, tech_icon(WARGEAR, "shells", "HB")),
    ("GFX_sm_drop_pods_medium", "tech_drop_pods", TECH, tech_icon(VOID, "planet", "POD")),
    ("GFX_sm_strike_cruiser_medium", "tech_strike_cruiser", TECH, tech_icon(VOID, "planet", "SC")),
    ("GFX_sm_battle_barge_medium", "tech_battle_barge", TECH, tech_icon(VOID, "planet", "BB")),
    ("GFX_sm_combat_squads_medium", "tech_combat_squads", TECH, tech_icon(CODEX, "book", "CS")),
    ("GFX_sm_battle_company_doctrine_medium", "tech_battle_company_doctrine", TECH, tech_icon(CODEX, "book", "BCO")),
    ("GFX_sm_chapter_masters_council_medium", "tech_chapter_masters_council", TECH, tech_icon(CODEX, "book", "CMC")),
    # Equipment: GFX_<equipment>_medium
    ("GFX_sm_power_armour_medium", "equipment_power_armour", EQUIPMENT, equipment_icon("PA")),
    ("GFX_sm_power_armour_1_medium", "equipment_power_armour_1", EQUIPMENT, equipment_icon("Mk II")),
    ("GFX_sm_power_armour_2_medium", "equipment_power_armour_2", EQUIPMENT, equipment_icon("Mk III")),
    ("GFX_sm_power_armour_3_medium", "equipment_power_armour_3", EQUIPMENT, equipment_icon("Mk IV")),
    # Sub-units in the division designer: GFX_unit_<sub-unit>_icon_medium
    ("GFX_unit_sm_tactical_squad_icon_medium", "unit_tactical_squad", UNIT,
     helmet_icon(CHAPTER, (31, 79, 160), RED_LENS, scale=0.9)),
    ("GFX_unit_sm_neophyte_scouts_icon_medium", "unit_neophyte_scouts", UNIT,
     helmet_icon((52, 78, 46), (98, 120, 74), GREEN_LENS, scale=0.9)),
    ("GFX_unit_sm_apothecarion_icon_medium", "unit_apothecarion", UNIT,
     helmet_icon(STEEL, (226, 226, 222), RED_LENS, scale=0.9, badge="cross")),
    # National spirits: GFX_idea_<idea>
    ("GFX_idea_sm_lineage_ultramarines", "idea_lineage_ultramarines", IDEA,
     helmet_icon((28, 36, 58), (31, 79, 160), RED_LENS, BONE)),
    ("GFX_idea_sm_lineage_blood_angels", "idea_lineage_blood_angels", IDEA,
     helmet_icon((40, 22, 22), (170, 24, 24), GOLD_LENS, GOLD)),
    ("GFX_idea_sm_lineage_imperial_fists", "idea_lineage_imperial_fists", IDEA,
     helmet_icon((40, 36, 22), (228, 186, 20), RED_LENS, DARK)),
    ("GFX_idea_sm_adeptus_astartes_chapter", "idea_adeptus_astartes_chapter", IDEA,
     helmet_icon((34, 36, 42), (168, 172, 182), GREEN_LENS, BONE)),
    ("GFX_idea_sm_black_rage", "idea_black_rage", IDEA,
     helmet_icon((96, 10, 10), (16, 16, 18), (255, 40, 30), (255, 40, 30))),
    # Decisions: GFX_decision_<icon>, categories: GFX_decision_category_<icon>
    ("GFX_decision_sm_geneseed", "decision_geneseed", DECISION, symbol_icon(GENESEED, "helix")),
    ("GFX_decision_sm_chapter", "decision_chapter", DECISION,
     helmet_icon(CHAPTER, (31, 79, 160), RED_LENS, BONE, scale=0.84)),
    ("GFX_decision_sm_orbital", "decision_orbital", DECISION, symbol_icon(VOID, "planet")),
    ("GFX_decision_category_sm_astartes", "decision_category_astartes", DECISION,
     helmet_icon(STEEL, (31, 79, 160), RED_LENS, BONE, scale=0.84)),
    # Same texture under the decision naming, in case categories resolve `icon` like decisions do.
    ("GFX_decision_sm_astartes", "decision_category_astartes", DECISION, None),
]

# Research-screen folder tab: two frames (normal, selected), 86x30 each to fit vanilla's
# 89px tab spacing.
TAB = ("GFX_sm_astartes_folder_tab", "techtree_astartes_tab")


def sprite_entry(name, stem, frames=None):
    lines = ["\tspriteType = {", f'\t\tname = "{name}"', f'\t\ttexturefile = "{TEXTURE_DIR}/{stem}.dds"']
    if frames:
        lines.append(f"\t\tnoOfFrames = {frames}")
    return lines + ["\t}"]


def main():
    out_dir = ROOT / TEXTURE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Generated by tools/make_icons.py. Re-run it after adding sprites there.",
        "spriteTypes = {",
    ]
    for name, stem, size, paint in SPRITES:
        if paint is not None:
            paint(size).save(out_dir / f"{stem}.dds")
        lines += sprite_entry(name, stem)
    tab_image(TAB_FRAME).save(out_dir / f"{TAB[1]}.dds")
    lines += sprite_entry(*TAB, frames=2)
    lines.append("}")
    GFX_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    thumbnail().save(THUMBNAIL)
    print(f"Wrote {len(SPRITES) + 1} sprites to {TEXTURE_DIR}, {GFX_FILE.relative_to(ROOT)} "
          f"and {THUMBNAIL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

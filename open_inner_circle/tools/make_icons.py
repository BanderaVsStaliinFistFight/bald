#!/usr/bin/env python3
"""Generate the Open Inner Circle icons, interface/oic.gfx and thumbnail.png.

Every icon is a gold symbol on a field-grey tile: a ring of seats around a figure for the
Inner Circle, a figure under a star for the leader, arrows for browsing. Textures are
uncompressed A8R8G8B8 DDS files in gfx/interface/oic/. To use hand-made art for one,
overwrite its DDS (keep the filename and size) and set its painter in SPRITES to None.

Usage (from the mod folder):  python3 tools/make_icons.py
Requires Pillow.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
TEXTURE_DIR = "gfx/interface/oic"
GFX_FILE = ROOT / "interface" / "oic.gfx"
THUMBNAIL = ROOT / "thumbnail.png"
SS = 4  # drawn at 4x and scaled down, for clean edges

FIELD_GREY = (62, 66, 58)
BORDER = (28, 30, 26)
GOLD = (214, 180, 96)
RED = (170, 40, 34)
GREEN = (80, 160, 80)

DECISION = (40, 40)
IDEA = (64, 64)


def tile(size, colour=FIELD_GREY):
    """A rounded square with a dark border, at SS times size."""
    w, h = size[0] * SS, size[1] * SS
    image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    radius = int(min(w, h) * 0.14)
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=BORDER)
    inset = max(SS, int(min(w, h) * 0.06))
    draw.rounded_rectangle((inset, inset, w - 1 - inset, h - 1 - inset), radius=max(1, radius - inset),
                           fill=colour)
    return image


def finish(image, size):
    return image.resize(size, Image.LANCZOS)


def bust(draw, cx, cy, height, colour):
    """A head-and-shoulders figure centred on (cx, cy), height tall."""
    head = height * 0.22
    draw.ellipse((cx - head, cy - height / 2, cx + head, cy - height / 2 + 2 * head), fill=colour)
    top = cy - height / 2 + 2 * head + height * 0.06
    shoulders = height * 0.42
    draw.chord((cx - shoulders, top, cx + shoulders, top + 2 * (cy + height / 2 - top)), 180, 360, fill=colour)


def star(draw, cx, cy, radius, colour, points=5):
    corners = []
    for i in range(points * 2):
        r = radius if i % 2 == 0 else radius * 0.45
        angle = -math.pi / 2 + i * math.pi / points
        corners.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(corners, fill=colour)


def ring_of_seats(draw, cx, cy, radius, seat, colour, seats=8):
    for i in range(seats):
        angle = -math.pi / 2 + i * 2 * math.pi / seats
        x, y = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
        draw.ellipse((x - seat, y - seat, x + seat, y + seat), fill=colour)


def inner_circle(size):
    image = tile(size)
    draw = ImageDraw.Draw(image)
    w, h = image.size
    ring_of_seats(draw, w / 2, h / 2, w * 0.30, w * 0.07, GOLD)
    bust(draw, w / 2, h / 2 + h * 0.02, h * 0.34, GOLD)
    return finish(image, size)


def leader(size):
    image = tile(size)
    draw = ImageDraw.Draw(image)
    w, h = image.size
    star(draw, w / 2, h * 0.24, w * 0.14, GOLD)
    bust(draw, w / 2, h * 0.62, h * 0.48, GOLD)
    return finish(image, size)


def seat_change(sign_colour, plus):
    def paint(size):
        image = tile(size)
        draw = ImageDraw.Draw(image)
        w, h = image.size
        ring_of_seats(draw, w * 0.44, h * 0.50, w * 0.27, w * 0.065, GOLD, seats=6)
        bust(draw, w * 0.44, h * 0.52, h * 0.26, GOLD)
        # Badge in the lower right corner.
        r = w * 0.17
        bx, by = w * 0.76, h * 0.76
        draw.ellipse((bx - r, by - r, bx + r, by + r), fill=sign_colour, outline=BORDER, width=SS)
        bar = r * 0.55
        thick = r * 0.18
        draw.rectangle((bx - bar, by - thick, bx + bar, by + thick), fill=(240, 240, 230))
        if plus:
            draw.rectangle((bx - thick, by - bar, bx + thick, by + bar), fill=(240, 240, 230))
        return finish(image, size)
    return paint


def arrow(direction):
    def paint(size):
        image = tile(size)
        draw = ImageDraw.Draw(image)
        w, h = image.size
        s = -1 if direction == "left" else 1
        tip, back = w / 2 + s * w * 0.28, w / 2 - s * w * 0.04
        draw.polygon([(tip, h / 2), (back, h * 0.22), (back, h * 0.78)], fill=GOLD)
        tail = w / 2 - s * w * 0.28
        draw.rectangle((min(tail, back), h * 0.40, max(tail, back), h * 0.60), fill=GOLD)
        return finish(image, size)
    return paint


def list_filter(size):
    image = tile(size)
    draw = ImageDraw.Draw(image)
    w, h = image.size
    for i, y in enumerate((0.28, 0.50, 0.72)):
        r = w * 0.07
        draw.ellipse((w * 0.24 - r, h * y - r, w * 0.24 + r, h * y + r), fill=GOLD)
        draw.rectangle((w * 0.38, h * y - w * 0.045, w * (0.78 - 0.08 * i), h * y + w * 0.045), fill=GOLD)
    return finish(image, size)


def thumbnail(size=512):
    """Launcher and Steam Workshop picture: the Inner Circle ring around a starred leader."""
    image = Image.new("RGBA", (size * SS, size * SS), BORDER + (255,))
    draw = ImageDraw.Draw(image)
    w = size * SS
    inset = int(w * 0.04)
    draw.rounded_rectangle((inset, inset, w - inset, w - inset), radius=int(w * 0.08), fill=FIELD_GREY)
    ring_of_seats(draw, w / 2, w / 2, w * 0.35, w * 0.05, GOLD, seats=12)
    star(draw, w / 2, w * 0.29, w * 0.065, GOLD)
    bust(draw, w / 2, w * 0.54, w * 0.30, GOLD)
    return image.resize((size, size), Image.LANCZOS).convert("RGB")


# (sprite name, texture file stem, size, painter or None to keep the existing texture)
SPRITES = [
    ("GFX_decision_category_oic_inner_circle", "decision_category_inner_circle", DECISION, inner_circle),
    # Same texture under the decision naming, in case categories resolve `icon` like decisions do.
    ("GFX_decision_oic_inner_circle", "decision_category_inner_circle", DECISION, None),
    ("GFX_decision_oic_leader", "decision_leader", DECISION, leader),
    ("GFX_decision_oic_seat", "decision_seat", DECISION, seat_change(GREEN, plus=True)),
    ("GFX_decision_oic_dismiss", "decision_dismiss", DECISION, seat_change(RED, plus=False)),
    ("GFX_decision_oic_next", "decision_next", DECISION, arrow("right")),
    ("GFX_decision_oic_previous", "decision_previous", DECISION, arrow("left")),
    ("GFX_decision_oic_filter", "decision_filter", DECISION, list_filter),
    ("GFX_idea_oic_inner_circle", "idea_inner_circle", IDEA, inner_circle),
]


def main():
    out_dir = ROOT / TEXTURE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Generated by tools/make_icons.py. Re-run it after adding sprites there.", "spriteTypes = {"]
    for name, stem, size, paint in SPRITES:
        if paint is not None:
            paint(size).save(out_dir / f"{stem}.dds")
        lines += ["\tspriteType = {", f'\t\tname = "{name}"',
                  f'\t\ttexturefile = "{TEXTURE_DIR}/{stem}.dds"', "\t}"]
    lines.append("}")
    GFX_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    thumbnail().save(THUMBNAIL)
    print(f"Wrote {len(SPRITES)} sprites to {TEXTURE_DIR}, {GFX_FILE.relative_to(ROOT)} "
          f"and {THUMBNAIL.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

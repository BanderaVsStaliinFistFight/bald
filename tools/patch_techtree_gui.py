#!/usr/bin/env python3
"""Add the Astartes tech folder and its tab to a copy of vanilla countrytechtreeview.gui.

The research screen only finds a tech folder's window, and its tab button, inside the
vanilla `countrytechtreeview` window, so a new folder needs an override of that whole file.
This script builds the override from the player's own game files, so it matches their
game version:

  * the folder window copies the frame (position, size, margins, scrollbars, background)
    of a vanilla folder and holds one gridbox named <root tech>_tree for the Astartes tree
  * the tab copies a vanilla tab button and goes after the last tab

Re-run it after a game update changes countrytechtreeview.gui.

Usage (from the mod root):
    python3 tools/patch_techtree_gui.py "<HOI4 install>/interface/countrytechtreeview.gui"
    python3 tools/patch_techtree_gui.py "<HOI4 install>"
Writes interface/countrytechtreeview.gui (or --output).
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "interface" / "countrytechtreeview.gui"

FOLDER = "sm_astartes_folder"
ROOT_TECH = "sm_geneseed_sequencing"
TAB_SPRITE = "GFX_sm_astartes_folder_tab"
# Vanilla folders whose frame we copy, in order of preference. Industry lays its years
# out top to bottom like the Astartes tree.
TEMPLATE_FOLDERS = ("industry_folder", "electronics_folder", "infantry_folder")
# Blocks of the template folder that describe its frame rather than its contents.
FRAME_BLOCKS = {"position", "size", "margin", "drag_scroll", "background"}
DEFAULT_TAB_SPACING = 89

# Content of the Astartes folder: a scroll area big enough for the tree, then the tree's
# grid. "UP" lays technology y positions out top to bottom (vanilla uses it for folders
# with years down the side). Slots are 70x70, like vanilla.
FOLDER_CONTENT = f"""containerWindowType = {{
	name = "sm_astartes_scroll_area"
	position = {{ x = 0 y = 0 }}
	size = {{
		width = 1650 height = 1250
		min = {{ width = 100%% height = 100%% }}
	}}
	clipping = no
}}

gridboxtype = {{
	name = "{ROOT_TECH}_tree"
	position = {{ x = 60 y = 40 }}
	slotsize = {{ width = 70 height = 70 }}
	format = "UP"
}}"""

TOKEN = re.compile(r'"[^"\n]*"|#[^\n]*|[{}=]|[^\s{}="#]+')


class Node:
    def __init__(self, key, start, end, value=None, children=None, close=None):
        self.key, self.start, self.end = key, start, end
        self.value, self.children, self.close = value, children, close

    @property
    def name(self):
        for child in self.children or []:
            if child.key.lower() == "name":
                return child.value
        return None

    def blocks(self, key):
        return [c for c in self.children or [] if c.children is not None and c.key.lower() == key]


def parse(text):
    tokens = [(m.group(0), m.start(), m.end()) for m in TOKEN.finditer(text)
              if not m.group(0).startswith("#")]

    def block(i, depth):
        nodes = []
        while i < len(tokens):
            tok, start, end = tokens[i]
            if tok == "}":
                if depth == 0:
                    sys.exit(f"parse error: unexpected '}}' at offset {start}")
                return nodes, i
            if i + 2 < len(tokens) and tokens[i + 1][0] == "=":
                value, value_start, value_end = tokens[i + 2]
                if value == "{":
                    children, j = block(i + 3, depth + 1)
                    if j >= len(tokens):
                        sys.exit(f"parse error: '{tok}' at offset {start} is never closed")
                    nodes.append(Node(tok, start, tokens[j][2], children=children, close=tokens[j][1]))
                    i = j + 1
                else:
                    nodes.append(Node(tok, start, value_end, value=value.strip('"')))
                    i += 3
            else:
                nodes.append(Node(tok, start, end))
                i += 1
        if depth:
            sys.exit("parse error: unclosed '{' at end of file")
        return nodes, i

    return block(0, 0)[0]


def find_windows(nodes, name):
    for node in nodes:
        if node.children is None:
            continue
        if node.key.lower() == "containerwindowtype" and node.name == name:
            yield node
        yield from find_windows(node.children, name)


def indent_of(text, pos):
    line_start = text.rfind("\n", 0, pos) + 1
    return re.match(r"[ \t]*", text[line_start:pos]).group(0)


def indent_block(block, indent):
    return "\n".join(indent + line if line else line for line in block.split("\n"))


def coordinate(node, axis):
    for position in node.blocks("position"):
        for child in position.children:
            if child.key.lower() == axis:
                try:
                    return float(child.value)
                except (TypeError, ValueError):
                    return None
    return None


def build_folder(text, template, indent):
    inner = indent + "\t"
    lines = [f'{inner}name = "{FOLDER}"']
    for child in template.children:
        key = child.key.lower()
        if key == "name":
            continue
        if child.children is None or key in FRAME_BLOCKS:
            lines.append(inner + text[child.start:child.end])
    lines.append("")
    lines.append(indent_block(FOLDER_CONTENT, inner))
    return f"containerWindowType = {{\n" + "\n".join(lines) + f"\n{indent}}}"


def build_tab(text, template, x, y, indent):
    inner = indent + "\t"
    lines = []
    for child in template.children:
        key = child.key.lower()
        if key == "name":
            lines.append(f'{inner}name = "{FOLDER}_tab"')
        elif key in ("quadtexturesprite", "spritetype"):
            lines.append(f'{inner}{child.key} = "{TAB_SPRITE}"')
        elif key == "position":
            lines.append(f"{inner}position = {{ x = {x:g} y = {y:g} }}")
        else:
            lines.append(inner + text[child.start:child.end])
    return f"buttonType = {{\n" + "\n".join(lines) + f"\n{indent}}}"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", help="vanilla countrytechtreeview.gui, or the HOI4 install folder")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="where to write the override")
    args = parser.parse_args()

    source = Path(args.source)
    if source.is_dir():
        source = source / "interface" / "countrytechtreeview.gui"
    raw = source.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    # latin-1 maps every byte to one character, so offsets are byte offsets and the
    # vanilla text round-trips unchanged whatever its encoding.
    text = raw[3:].decode("latin-1") if bom else raw.decode("latin-1")
    nodes = parse(text)

    views = list(find_windows(nodes, "countrytechtreeview"))
    if len(views) != 1:
        sys.exit(f"expected one 'countrytechtreeview' window in {source}, found {len(views)}")
    view = views[0]
    if list(find_windows([view], FOLDER)):
        sys.exit(f"{source} already contains {FOLDER}: pass the unmodified vanilla file")

    folders = {c.name: c for c in view.blocks("containerwindowtype")}
    template = next((folders[n] for n in TEMPLATE_FOLDERS if n in folders), None)
    if template is None:
        sys.exit(f"none of {', '.join(TEMPLATE_FOLDERS)} is a window inside countrytechtreeview")
    tabs_windows = list(find_windows([view], "folder_tabs"))
    if len(tabs_windows) != 1:
        sys.exit(f"expected one 'folder_tabs' window inside countrytechtreeview, found {len(tabs_windows)}")
    tabs = tabs_windows[0]
    buttons = [b for b in tabs.blocks("buttontype") if (b.name or "").endswith("_tab")]
    if not buttons:
        sys.exit("no folder tab buttons found in folder_tabs")
    tab_template = next((b for b in buttons if b.name == f"{template.name}_tab"), buttons[0])

    xs = sorted({x for x in (coordinate(b, "x") for b in buttons) if x is not None})
    gaps = Counter(round(b - a) for a, b in zip(xs, xs[1:]) if b > a)
    spacing = gaps.most_common(1)[0][0] if gaps else DEFAULT_TAB_SPACING
    tab_x = xs[-1] + spacing
    tab_y = coordinate(tab_template, "y") or 0

    folder_indent = indent_of(text, template.start)
    folder_text = build_folder(text, template, folder_indent)
    tab_indent = indent_of(text, tab_template.start)
    tab_text = build_tab(text, tab_template, tab_x, tab_y, tab_indent)

    # Apply the later insertion first so the earlier offset stays valid.
    insertions = sorted([
        (template.end, f"\n\n{folder_indent}{folder_text}"),
        (tabs.close, f"\n{tab_indent}{tab_text}\n{indent_of(text, tabs.close)}"),
    ], reverse=True)
    patched = text
    for offset, insert in insertions:
        if insert.endswith("\n" + indent_of(text, tabs.close)) and offset == tabs.close:
            # Replace the whitespace before folder_tabs' closing brace with our tab.
            line_start = patched.rfind("\n", 0, offset)
            patched = patched[:line_start] + insert + patched[offset:]
        else:
            patched = patched[:offset] + insert + patched[offset:]

    header = (f"# Generated by tools/patch_techtree_gui.py from vanilla {source.name}: adds the\n"
              f"# {FOLDER} window and tab. Re-run it after a game update instead of editing this file.\n")
    check = parse(patched)
    view_after = next(find_windows(check, "countrytechtreeview"))
    assert any(c.name == FOLDER for c in view_after.blocks("containerwindowtype"))
    assert any(b.name == f"{FOLDER}_tab" for b in next(find_windows([view_after], "folder_tabs")).blocks("buttontype"))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes((b"\xef\xbb\xbf" if bom else b"") + (header + patched).encode("latin-1"))
    print(f"Wrote {output}: folder window copied from {template.name}, "
          f"tab '{FOLDER}_tab' at x={tab_x:g} y={tab_y:g} (tab spacing {spacing}).")


if __name__ == "__main__":
    main()

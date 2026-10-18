#!/usr/bin/env python3
"""Static checks for the Adeptus Astartes mod.

Catches the mistakes that otherwise only show up in-game or in error.log:
  * unbalanced braces and unparsable script
  * references to techs, sub-units, equipment, ideas, missions or dynamic modifiers
    that the mod doesn't define (vanilla names that are allowed are listed below)
  * missing localisation keys and missing sprites
  * a tech folder without its window and tab inside the vanilla countrytechtreeview
    window of interface/countrytechtreeview.gui (that stopped the research screen
    opening in v0.1.0), without its techtree_<folder>_item tech box template, or a root
    tech without its <root tech>_tree gridbox in the folder's window
  * with --cwtools PATH: effect, trigger and modifier names checked against the
    game's script documentation shipped in the CWTools HOI4 rules
    (https://github.com/cwtools/cwtools-hoi4-config)

Usage (from the mod root):
    python3 tools/check_mod.py [--cwtools /path/to/cwtools-hoi4-config]
Exit code 1 if anything is wrong.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Vanilla names the mod is allowed to reference.
VANILLA_EQUIPMENT = {"infantry_equipment"}
VANILLA_UNIT_CATEGORIES = {
    "category_front_line", "category_light_infantry", "category_all_infantry",
    "category_army", "category_support_battalions",
}

EFFECT_BLOCKS = {"complete_effect", "remove_effect", "cancel_effect", "timeout_effect",
                 "on_research_complete"}
TRIGGER_BLOCKS = {"visible", "available", "allowed", "allowed_civil_war", "activation",
                  "target_trigger", "target_root_trigger", "custom_cost_trigger",
                  "cancel_trigger", "allow", "allow_branch", "remove_trigger"}
# Keys that change scope or control flow; their bodies keep the surrounding context.
SCOPE_KEYS = {"ROOT", "FROM", "THIS", "PREV", "NOT", "OR", "AND", "controller", "owner",
              "hidden_effect", "if", "else", "else_if", "custom_trigger_tooltip"}
# Effect/trigger parameters that are not themselves effects or triggers.
PARAM_KEYS = {"limit", "tooltip"}

TOKEN = re.compile(r'"[^"\n]*"|[{}]|<=|>=|!=|[=<>]|[^\s{}=<>"#]+')


class ParseError(Exception):
    pass


def tokenize(text):
    tokens = []
    for line_no, line in enumerate(text.splitlines(), 1):
        line = re.sub(r'#.*$', '', line) if '"' not in line else strip_comment(line)
        for match in TOKEN.finditer(line):
            tokens.append((match.group(0), line_no))
    return tokens


def strip_comment(line):
    in_string = False
    for i, ch in enumerate(line):
        if ch == '"':
            in_string = not in_string
        elif ch == '#' and not in_string:
            return line[:i]
    return line


def parse(tokens, pos=0, depth=0):
    """Return (list of (key, op, value, line), next pos). value is a str or a list."""
    items = []
    while pos < len(tokens):
        tok, line = tokens[pos]
        if tok == '}':
            if depth == 0:
                raise ParseError(f"line {line}: unexpected '}}'")
            return items, pos + 1
        if tok == '{':
            raise ParseError(f"line {line}: block without a key")
        if pos + 1 < len(tokens) and tokens[pos + 1][0] in ('=', '<', '>', '<=', '>=', '!='):
            op = tokens[pos + 1][0]
            if pos + 2 >= len(tokens):
                raise ParseError(f"line {line}: '{tok} {op}' has no value")
            value_tok = tokens[pos + 2][0]
            if value_tok == '{':
                body, pos = parse(tokens, pos + 3, depth + 1)
                items.append((tok, op, body, line))
            else:
                items.append((tok, op, value_tok.strip('"'), line))
                pos += 3
        else:
            items.append((tok, None, None, line))
            pos += 1
    if depth:
        raise ParseError("unclosed '{' at end of file")
    return items, pos


def parse_file(path, problems):
    try:
        items, _ = parse(tokenize(path.read_text(encoding="utf-8-sig")))
        return items
    except ParseError as error:
        problems.append(f"{path.relative_to(ROOT)}: {error}")
        return []


def blocks(items):
    return [(k, v, line) for k, op, v, line in items if isinstance(v, list)]


def walk(items):
    """Yield every (key, op, value, line) at any depth."""
    for key, op, value, line in items:
        yield key, op, value, line
        if isinstance(value, list):
            yield from walk(value)


def values_of(items, key):
    return [v for k, _, v, _ in walk(items) if k == key]


def top_block(items, key, problems):
    """The body of the first `key = { ... }` block, or [] (and a problem) if there is none."""
    found = values_of(items, key)
    if not found:
        problems.append(f"no '{key} = {{ ... }}' block found")
        return []
    return found[0]


def named(items, key, name, deep=True):
    """Bodies of `key = { name = "<name>" ... }` blocks (key case-insensitive)."""
    found = []
    for k, _, value, _ in (walk(items) if deep else items):
        if isinstance(value, list) and k.lower() == key and \
                any(ck.lower() == "name" and cv == name for ck, _, cv, _ in value):
            found.append(value)
    return found


def bare_tokens(block):
    return [k for k, op, _, _ in block if op is None]


def load_loc():
    keys = {}
    for path in (ROOT / "localisation").rglob("*.yml"):
        raw = path.read_bytes()
        rel = path.relative_to(ROOT)
        if not raw.startswith(b"\xef\xbb\xbf"):
            yield f"{rel}: missing UTF-8 BOM"
        lines = raw.decode("utf-8-sig").splitlines()
        if not lines or not lines[0].startswith("l_english:"):
            yield f"{rel}: first line must be 'l_english:'"
        for n, line in enumerate(lines[1:], 2):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            match = re.match(r'^ ([A-Za-z0-9_.\-]+):\d* "(.*)"\s*$', line)
            if not match:
                yield f"{rel}:{n}: malformed localisation line"
                continue
            if match.group(1) in keys:
                yield f"{rel}:{n}: duplicate key {match.group(1)}"
            keys[match.group(1)] = match.group(2)
    load_loc.keys = keys


def load_documented_names(cwtools):
    doc = json.loads((Path(cwtools) / "Config" / "script_documentation.json").read_text())
    modifiers = set()
    for entry in doc["modifiers"]:
        name = entry[0] if isinstance(entry, list) else entry.get("name", entry)
        modifiers.add(name if isinstance(name, str) else str(name))
    rules = (Path(cwtools) / "Config" / "modifiers.cwt").read_text()
    modifiers |= set(re.findall(r'^\s*([a-z_0-9<>]+)\s*=\s*\w+\s*$', rules, re.M))
    # Templated modifier names such as production_speed_<building>_factor.
    templates = [re.compile("^" + re.escape(m).replace(re.escape("<building>"), "[a-z_]+") + "$")
                 for m in modifiers if "<building>" in m]
    return set(doc["effects"]), set(doc["triggers"]), modifiers, templates


def check_context(items, context, effects, triggers, where, problems, buildings):
    """Check every statement key in an effect or trigger block against the docs."""
    known = effects if context == "effect" else triggers
    for key, op, value, line in items:
        if op is None or key in PARAM_KEYS:
            continue
        if key in SCOPE_KEYS:
            if isinstance(value, list):
                check_context(value, context, effects, triggers, where, problems, buildings)
            continue
        if key == "hidden_effect" or key in EFFECT_BLOCKS:
            check_context(value, "effect", effects, triggers, where, problems, buildings)
            continue
        if context == "trigger" and key in buildings:
            continue
        if key not in known:
            problems.append(f"{where}:{line}: '{key}' is not a documented {context}")
        if key == "custom_trigger_tooltip" and isinstance(value, list):
            check_context(value, "trigger", effects, triggers, where, problems, buildings)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cwtools", help="path to a cwtools-hoi4-config checkout")
    args = parser.parse_args()

    problems = []
    files = {p: parse_file(p, problems)
             for p in sorted((ROOT / "common").rglob("*.txt")) + sorted((ROOT / "interface").glob("*.g*"))}

    def items_in(folder):
        return [item for path, items in files.items()
                if str(path.relative_to(ROOT)).startswith(folder) for item in items]

    problems += list(load_loc())
    loc = load_loc.keys

    # Definitions.
    techs = {k: v for k, v, _ in blocks(top_block(items_in("common/technologies"), "technologies", problems))}
    # The mod's tech folder and categories are optional: v0.1.1 has none.
    tag_items = items_in("common/technology_tags")
    tech_categories = set(bare_tokens(top_block(tag_items, "technology_categories", problems))) if tag_items else set()
    folder_block = top_block(tag_items, "technology_folders", problems) if tag_items else []
    folders = set(bare_tokens(folder_block)) | {k for k, _, _ in blocks(folder_block)}
    units = {k: v for k, v, _ in blocks(top_block(items_in("common/units/sm_"), "sub_units", problems))}
    equipment = {k: v for k, v, _ in blocks(top_block(items_in("common/units/equipment"), "equipments", problems))}
    ideas = {}
    for _, category, _ in blocks(top_block(items_in("common/ideas"), "ideas", problems)):
        ideas.update({k: v for k, v, _ in blocks(category)})
    dyn_modifiers = {k: v for k, v, _ in blocks(items_in("common/dynamic_modifiers"))}
    categories = {k: v for k, v, _ in blocks(items_in("common/decisions/categories"))}
    decisions = {}
    for cat, body, line in blocks(items_in("common/decisions/sm_")):
        if cat not in categories:
            problems.append(f"decision category {cat} (line {line}) is not defined")
        decisions.update({k: v for k, v, _ in blocks(body)})
    missions = {k for k, v in decisions.items() if values_of(v, "days_mission_timeout")}
    sprites = set(values_of(items_in("interface/sm_astartes.gfx"), "name"))

    # Tech folders. The research screen only finds a folder's window and tab inside the
    # vanilla countrytechtreeview window.
    view = (named(items_in("interface/countrytechtreeview.gui"), "containerwindowtype", "countrytechtreeview")
            or [[]])[0]
    tab_rows = named(view, "containerwindowtype", "folder_tabs")
    folder_windows = {}
    for folder in sorted(folders):
        window = named(view, "containerwindowtype", folder, deep=False)
        if window:
            folder_windows[folder] = window[0]
        else:
            problems.append(f"tech folder {folder}: no '{folder}' window inside countrytechtreeview in "
                            "interface/countrytechtreeview.gui, so the research screen won't open "
                            "(generate it with tools/patch_techtree_gui.py)")
        if not (tab_rows and named(tab_rows[0], "buttontype", f"{folder}_tab")):
            problems.append(f"tech folder {folder}: no '{folder}_tab' button in folder_tabs in "
                            "interface/countrytechtreeview.gui")
        if not named(items_in("interface/countrytechtreeview.gui"), "containerwindowtype",
                     f"techtree_{folder}_item"):
            problems.append(f"tech folder {folder}: no 'techtree_{folder}_item' tech box template "
                            "in interface/countrytechtreeview.gui")

    # Technologies.
    targets = {t for v in techs.values() for t in values_of(v, "leads_to_tech")}
    for name, body in techs.items():
        for key in (name, name + "_desc"):
            if key not in loc:
                problems.append(f"technology {name}: missing localisation {key}")
        for target in values_of(body, "leads_to_tech"):
            if target not in techs:
                problems.append(f"technology {name}: leads to unknown tech {target}")
        for block in values_of(body, "categories"):
            for cat in bare_tokens(block):
                if cat not in tech_categories:
                    problems.append(f"technology {name}: unknown category {cat}")
        for block in values_of(body, "enable_subunits"):
            for unit in bare_tokens(block):
                if unit not in units:
                    problems.append(f"technology {name}: enables unknown sub-unit {unit}")
        for block in values_of(body, "enable_equipments"):
            for equip in bare_tokens(block):
                if equip not in equipment:
                    problems.append(f"technology {name}: enables unknown equipment {equip}")
        for key, _, value, _ in body:
            if key.startswith("sm_") and isinstance(value, list) and key not in units:
                problems.append(f"technology {name}: modifies unknown sub-unit {key}")
        folder_blocks = values_of(body, "folder")
        for folder in folder_blocks:
            folder_name = (values_of(folder, "name") or [None])[0]
            if folder_name not in folders:
                problems.append(f"technology {name}: unknown folder {folder_name}")
            window = folder_windows.get(folder_name)
            if name not in targets and window is not None and not named(window, "gridboxtype", f"{name}_tree"):
                problems.append(f"technology {name}: root tech needs a gridbox {name}_tree "
                                f"in the {folder_name} window")
        if folder_blocks and f"GFX_{name}_medium" not in sprites:
            problems.append(f"technology {name}: missing sprite GFX_{name}_medium")
    for key in [f"{f}_name" for f in folders] + [f"{f}_desc" for f in folders] + list(tech_categories):
        if key not in loc:
            problems.append(f"missing localisation {key}")

    # Sub-units and equipment.
    archetypes = {k for k, v in equipment.items() if "yes" in values_of(v, "is_archetype")}
    for name, body in units.items():
        for key in (name, name + "_desc"):
            if key not in loc:
                problems.append(f"sub-unit {name}: missing localisation {key}")
        if f"GFX_unit_{name}_icon_medium" not in sprites:
            problems.append(f"sub-unit {name}: missing sprite GFX_unit_{name}_icon_medium")
        for need in values_of(body, "need"):
            for equip, _, _, _ in need:
                if equip not in archetypes and equip not in VANILLA_EQUIPMENT:
                    problems.append(f"sub-unit {name}: needs unknown equipment archetype {equip}")
        for block in values_of(body, "categories"):
            for cat in bare_tokens(block):
                if cat not in VANILLA_UNIT_CATEGORIES:
                    problems.append(f"sub-unit {name}: category {cat} isn't a known vanilla category")
    for name, body in equipment.items():
        keys = [name, name + "_desc"] + ([] if name in archetypes else [name + "_short"])
        for key in keys:
            if key not in loc:
                problems.append(f"equipment {name}: missing localisation {key}")
        if f"GFX_{name}_medium" not in sprites:
            problems.append(f"equipment {name}: missing sprite GFX_{name}_medium")
        for ref in values_of(body, "archetype") + values_of(body, "parent"):
            if ref not in equipment:
                problems.append(f"equipment {name}: unknown archetype/parent {ref}")

    # Ideas, dynamic modifiers, decisions.
    for name, body in ideas.items():
        for key in (name, name + "_desc"):
            if key not in loc:
                problems.append(f"idea {name}: missing localisation {key}")
        picture = (values_of(body, "picture") or [name])[0]
        if f"GFX_idea_{picture}" not in sprites:
            problems.append(f"idea {name}: missing sprite GFX_idea_{picture}")
    for name, body in dyn_modifiers.items():
        if name not in loc:
            problems.append(f"dynamic modifier {name}: missing localisation")
        for icon in values_of(body, "icon"):
            if icon not in sprites:
                problems.append(f"dynamic modifier {name}: missing sprite {icon}")
    for name, body in categories.items():
        for key in (name, name + "_desc"):
            if key not in loc:
                problems.append(f"category {name}: missing localisation {key}")
        for icon in values_of(body, "icon"):
            if f"GFX_decision_category_{icon}" not in sprites:
                problems.append(f"category {name}: missing sprite GFX_decision_category_{icon}")
    for name, body in decisions.items():
        for key in (name, name + "_desc"):
            if key not in loc:
                problems.append(f"decision {name}: missing localisation {key}")
        for icon in values_of(body, "icon"):
            if f"GFX_decision_{icon}" not in sprites:
                problems.append(f"decision {name}: missing sprite GFX_decision_{icon}")
        for key in values_of(body, "custom_effect_tooltip") + values_of(body, "tooltip") \
                + values_of(body, "custom_cost_text"):
            if key not in loc:
                problems.append(f"decision {name}: missing localisation {key}")
        for tech in values_of(body, "has_tech") + values_of(body, "technology"):
            if tech not in techs:
                problems.append(f"decision {name}: unknown tech {tech}")
        for block in values_of(body, "set_technology"):
            for tech, _, _, _ in block:
                if tech != "popup" and tech not in techs:
                    problems.append(f"decision {name}: sets unknown tech {tech}")
        for idea in values_of(body, "add_ideas") + values_of(body, "has_idea") + values_of(body, "idea"):
            if idea not in ideas:
                problems.append(f"decision {name}: unknown idea {idea}")
        for modifier in values_of(body, "modifier"):
            if isinstance(modifier, str) and modifier not in dyn_modifiers:
                problems.append(f"decision {name}: unknown dynamic modifier {modifier}")
        for mission in values_of(body, "has_active_mission"):
            if mission not in missions:
                problems.append(f"decision {name}: unknown mission {mission}")
        for unit in values_of(body, "has_template_containing_unit"):
            if unit not in units:
                problems.append(f"decision {name}: unknown sub-unit {unit}")
        for template in values_of(body, "division_template"):
            for section in ("regiments", "support"):
                for block in values_of(template, section):
                    for unit, _, _, _ in block:
                        if unit not in units:
                            problems.append(f"decision {name}: template uses unknown sub-unit {unit}")

    if args.cwtools:
        effects, triggers, modifiers, templates = load_documented_names(args.cwtools)
        buildings = {"infrastructure", "bunker", "anti_air_building", "arms_factory",
                     "industrial_complex", "air_base", "coastal_bunker"}

        def is_modifier(key):
            return key in modifiers or any(t.match(key) for t in templates)

        for name, body in decisions.items():
            for key, _, value, _ in body:
                if key in EFFECT_BLOCKS and isinstance(value, list):
                    check_context(value, "effect", effects, triggers, f"decision {name}", problems, buildings)
                elif key in TRIGGER_BLOCKS and isinstance(value, list):
                    check_context(value, "trigger", effects, triggers, f"decision {name}", problems, buildings)
                elif key == "modifier" and isinstance(value, list):
                    problems += [f"decision {name}: unknown modifier {k}" for k, _, _, _ in value if not is_modifier(k)]
        for name, body in categories.items():
            for key, _, value, _ in body:
                if key in TRIGGER_BLOCKS and isinstance(value, list):
                    check_context(value, "trigger", effects, triggers, f"category {name}", problems, buildings)
        for name, body in techs.items():
            for key, _, value, _ in body:
                if key in TRIGGER_BLOCKS and isinstance(value, list):
                    check_context(value, "trigger", effects, triggers, f"technology {name}", problems, buildings)
                elif isinstance(value, str) and not key.startswith(("research", "start_year")) \
                        and key not in {"doctrine", "show_equipment_icon"} and not is_modifier(key):
                    problems.append(f"technology {name}: unknown modifier {key}")
        for name, body in ideas.items():
            for block in values_of(body, "modifier"):
                problems += [f"idea {name}: unknown modifier {k}" for k, _, _, _ in block if not is_modifier(k)]
        for name, body in dyn_modifiers.items():
            problems += [f"dynamic modifier {name}: unknown modifier {k}" for k, _, v, _ in body
                         if k != "icon" and isinstance(v, str) and not is_modifier(k)]

    for problem in problems:
        print(problem)
    print(f"{len(techs)} techs, {len(units)} sub-units, {len(equipment)} equipment, {len(ideas)} ideas, "
          f"{len(decisions)} decisions, {len(loc)} localisation keys, {len(sprites)} sprites: "
          f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

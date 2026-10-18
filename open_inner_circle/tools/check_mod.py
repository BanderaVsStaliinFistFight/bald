#!/usr/bin/env python3
"""Static checks for the Open Inner Circle mod.

Catches the mistakes that otherwise only show up in-game or in error.log:
  * unbalanced braces and unparsable script
  * decisions outside a defined category; missing localisation for categories, decisions,
    tooltips, scripted localisation and the dynamic modifier; missing sprites
  * localisation that calls an undefined scripted localisation, or shows a variable the
    script never sets
  * a misspelt oic_ scripted effect or trigger, or one used in the wrong context (an
    effect inside a trigger block or the other way round)
  * a character flag that is checked but never set
  * with --cwtools PATH: every effect, trigger and modifier name, and every localisation
    command, checked against the game's script documentation shipped in the CWTools HOI4
    rules (https://github.com/cwtools/cwtools-hoi4-config)

Usage (from the mod folder):
    python3 tools/check_mod.py [--cwtools /path/to/cwtools-hoi4-config]
Exit code 1 if anything is wrong.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TOKEN = re.compile(r'"[^"\n]*"|[{}]|<=|>=|!=|[=<>]|[^\s{}=<>"#]+')

# Keys that only steer control flow or scope: their bodies keep the surrounding context.
FLOW_KEYS = {"if", "else_if", "else", "hidden_effect", "AND", "OR", "NOT",
             "ROOT", "THIS", "PREV", "FROM", "custom_trigger_tooltip"}
# Iterator effects/triggers whose bodies hold more effects/triggers.
ITERATOR = re.compile(r"^(every|random|any|all)_")
# Parameters of effects, triggers and iterators that are not effects or triggers themselves.
PARAM_KEYS = {"limit", "tooltip", "random_select_amount", "display_individual_scopes",
              "include_invisible"}


class ParseError(Exception):
    pass


def strip_comment(line):
    in_string = False
    for i, ch in enumerate(line):
        if ch == '"':
            in_string = not in_string
        elif ch == '#' and not in_string:
            return line[:i]
    return line


def tokenize(text):
    tokens = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for match in TOKEN.finditer(strip_comment(line)):
            tokens.append((match.group(0), line_no))
    return tokens


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


def walk(items):
    """Yield every (key, op, value, line) at any depth."""
    for key, op, value, line in items:
        yield key, op, value, line
        if isinstance(value, list):
            yield from walk(value)


def values_of(items, key):
    return [v for k, _, v, _ in walk(items) if k == key]


def blocks(items):
    return [(k, v, line) for k, op, v, line in items if isinstance(v, list)]


def load_loc(problems):
    keys = {}
    for path in sorted((ROOT / "localisation").rglob("*.yml")):
        raw = path.read_bytes()
        rel = path.relative_to(ROOT)
        if not raw.startswith(b"\xef\xbb\xbf"):
            problems.append(f"{rel}: missing UTF-8 BOM")
        lines = raw.decode("utf-8-sig").splitlines()
        if not lines or not lines[0].startswith("l_english:"):
            problems.append(f"{rel}: first line must be 'l_english:'")
        for n, line in enumerate(lines[1:], 2):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            match = re.match(r'^ ([A-Za-z0-9_.\-]+):\d* "(.*)"\s*$', line)
            if not match:
                problems.append(f"{rel}:{n}: malformed localisation line")
                continue
            if match.group(1) in keys:
                problems.append(f"{rel}:{n}: duplicate key {match.group(1)}")
            keys[match.group(1)] = match.group(2)
    return keys


def load_documentation(cwtools):
    config = Path(cwtools) / "Config"
    doc = json.loads((config / "script_documentation.json").read_text())
    modifiers = set()
    for entry in doc["modifiers"]:
        name = entry[0] if isinstance(entry, list) else entry.get("name", entry)
        modifiers.add(name if isinstance(name, str) else str(name))
    rules = (config / "modifiers.cwt").read_text()
    modifiers |= set(re.findall(r'^\s*([a-z_0-9<>]+)\s*=\s*\w+\s*$', rules, re.M))
    commands = set(re.findall(r'^\s*(\w+)\s*=\s*\w+\s*$',
                              (config / "localisation.cwt").read_text(), re.M))
    return set(doc["effects"]), set(doc["triggers"]), modifiers, commands


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cwtools", help="path to a cwtools-hoi4-config checkout")
    args = parser.parse_args()

    problems = []
    files = {}
    for path in sorted((ROOT / "common").rglob("*.txt")) + sorted((ROOT / "interface").glob("*.gfx")):
        try:
            files[path] = parse(tokenize(path.read_text(encoding="utf-8-sig")))[0]
        except ParseError as error:
            problems.append(f"{path.relative_to(ROOT)}: {error}")
            files[path] = []

    def items_in(folder):
        return [(path, item) for path, items in files.items()
                if path.relative_to(ROOT).as_posix().startswith(folder) for item in items]

    def bodies_in(folder):
        """(name, body, 'file:line') for each top-level block in folder."""
        return [(k, v, f"{path.relative_to(ROOT).as_posix()}:{line}")
                for path, (k, op, v, line) in items_in(folder) if isinstance(v, list)]

    loc = load_loc(problems)
    sprites = set(values_of([item for _, item in items_in("interface")], "name"))

    scripted_effects = {name: (body, where) for name, body, where in bodies_in("common/scripted_effects")}
    scripted_triggers = {name: (body, where) for name, body, where in bodies_in("common/scripted_triggers")}
    scripted_loc = {}
    for key, body, where in bodies_in("common/scripted_localisation"):
        if key != "defined_text":
            problems.append(f"{where}: expected defined_text, found {key}")
            continue
        scripted_loc[(values_of(body, "name") or ["?"])[0]] = (body, where)
    dynamic_modifiers = {name: (body, where) for name, body, where in bodies_in("common/dynamic_modifiers")}
    categories = {name: (body, where) for name, body, where in bodies_in("common/decisions/categories")}
    decisions = {}
    for category, body, where in bodies_in("common/decisions/oic_"):
        if category not in categories:
            problems.append(f"{where}: decision category {category} is not defined")
        for name, decision, line in blocks(body):
            decisions[name] = (decision, f"{where.split(':')[0]}:{line}")
    on_action_effects = [(body, f"{path.relative_to(ROOT).as_posix()}:{line}")
                         for path, (k, op, v, line) in items_in("common/on_actions") if isinstance(v, list)
                         for _, _, body, line in walk(v) if _ == "effect" and isinstance(body, list)]

    # Script statements, by context. Collect (key, value, context, where) for every statement
    # that should be an effect or a trigger.
    statements = []

    def collect(items, context, where):
        for key, op, value, line in items:
            if op is None or key in PARAM_KEYS and key != "limit":
                continue
            at = f"{where.split(':')[0]}:{line}"
            if key == "limit":
                collect(value, "trigger", where)
                continue
            if key in FLOW_KEYS or key.startswith("var:"):
                if isinstance(value, list):
                    inner = "effect" if key == "hidden_effect" else context
                    collect(value, inner, where)
                if key in ("hidden_effect", "custom_trigger_tooltip") or key.startswith("var:"):
                    statements.append((key, value, context, at))
                continue
            statements.append((key, value, context, at))
            if ITERATOR.match(key) and isinstance(value, list):
                collect(value, context, where)

    for name, (body, where) in scripted_effects.items():
        collect(body, "effect", where)
    for name, (body, where) in scripted_triggers.items():
        collect(body, "trigger", where)
    for name, (body, where) in scripted_loc.items():
        for trigger in values_of(body, "trigger"):
            collect(trigger, "trigger", where)
    for body, where in on_action_effects:
        collect(body, "effect", where)
    for name, (body, where) in decisions.items():
        for key, _, value, _ in body:
            if key in ("visible", "available", "allowed"):
                collect(value, "trigger", where)
            elif key in ("complete_effect", "remove_effect", "timeout_effect"):
                collect(value, "effect", where)
    for name, (body, where) in categories.items():
        for key, _, value, _ in body:
            if key in ("visible", "available", "allowed"):
                collect(value, "trigger", where)

    # oic_ scripted effects and triggers: defined, and used in the right context.
    for key, value, context, at in statements:
        if not key.startswith("oic_"):
            continue
        if context == "effect" and key not in scripted_effects:
            kind = "a scripted trigger" if key in scripted_triggers else "not a defined scripted effect"
            problems.append(f"{at}: '{key}' is {kind}, but is used as an effect")
        if context == "trigger" and key not in scripted_triggers:
            kind = "a scripted effect" if key in scripted_effects else "not a defined scripted trigger"
            problems.append(f"{at}: '{key}' is {kind}, but is used as a trigger")

    # Character flags: every flag that is checked is set somewhere.
    every_item = [item for _, item in items_in("common")]
    set_flags = {v for v in values_of(every_item, "set_character_flag") if isinstance(v, str)}
    for flag in {v for v in values_of(every_item, "has_character_flag") if isinstance(v, str)} - set_flags:
        problems.append(f"character flag {flag} is checked but never set")

    # Variables the script writes, by bare name.
    written = set()
    for effect in ("set_variable", "add_to_variable", "set_temp_variable"):
        for block in values_of(every_item, effect):
            if isinstance(block, list):
                written |= {k.split(".")[-1] for k, _, _, _ in block}

    # Localisation.
    def need(key, what):
        if key not in loc:
            problems.append(f"{what}: missing localisation {key}")

    for name, (body, where) in categories.items():
        need(name, f"{where} category {name}")
        need(name + "_desc", f"{where} category {name}")
        for icon in values_of(body, "icon"):
            if f"GFX_decision_category_{icon}" not in sprites:
                problems.append(f"{where} category {name}: missing sprite GFX_decision_category_{icon}")
    for name, (body, where) in decisions.items():
        need(name, f"{where} decision {name}")
        need(name + "_desc", f"{where} decision {name}")
        for icon in values_of(body, "icon"):
            if f"GFX_decision_{icon}" not in sprites:
                problems.append(f"{where} decision {name}: missing sprite GFX_decision_{icon}")
    for name, (body, where) in dynamic_modifiers.items():
        need(name, f"{where} dynamic modifier {name}")
        for icon in values_of(body, "icon"):
            if icon not in sprites:
                problems.append(f"{where} dynamic modifier {name}: missing sprite {icon}")
        for key, _, value, line in body:
            if key != "icon" and isinstance(value, str) and not re.match(r"^-?[\d.]+$", value) \
                    and value not in written:
                problems.append(f"{where} dynamic modifier {name}: {key} uses variable {value}, "
                                "which the script never sets")
    for name, (body, where) in scripted_loc.items():
        for key in values_of(body, "localization_key"):
            need(key, f"{where} scripted localisation {name}")
    for key, value, context, at in statements:
        if key == "custom_effect_tooltip" and isinstance(value, str):
            need(value, at)
        if key == "custom_trigger_tooltip" and isinstance(value, list):
            for tooltip in values_of(value, "tooltip"):
                need(tooltip, at)

    commands = None
    if args.cwtools:
        effects, triggers, modifiers, commands = load_documentation(args.cwtools)
    for key, text in loc.items():
        for ref in re.findall(r"\[([^\]]+)\]", text):
            if ref.startswith("?"):
                name = ref[1:].split("|")[0].split(".")[0]
                if name not in written:
                    problems.append(f"localisation {key}: shows variable {name}, which the script never sets")
                if "." in ref and commands is not None and ref.split("|")[0].split(".")[-1] not in commands:
                    problems.append(f"localisation {key}: unknown localisation command in [{ref}]")
            elif "." in ref:
                if commands is not None and ref.split(".")[-1] not in commands:
                    problems.append(f"localisation {key}: unknown localisation command in [{ref}]")
            elif ref not in scripted_loc:
                problems.append(f"localisation {key}: [{ref}] is not a defined scripted localisation")

    if args.cwtools:
        for key, value, context, at in statements:
            if key.startswith("oic_") or key.startswith("var:"):
                continue
            known = effects if context == "effect" else triggers
            if key not in known:
                problems.append(f"{at}: '{key}' is not a documented {context}")
        for name, (body, where) in dynamic_modifiers.items():
            for key, _, _, line in body:
                if key != "icon" and key not in modifiers:
                    problems.append(f"{where}: '{key}' is not a documented modifier")

    for problem in problems:
        print(problem)
    checked = "names checked against CWTools" if args.cwtools else "run with --cwtools to check names"
    print(f"{len(problems)} problem(s); {len(decisions)} decisions, {len(scripted_effects)} scripted effects, "
          f"{len(scripted_triggers)} scripted triggers, {len(loc)} localisation keys ({checked})")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

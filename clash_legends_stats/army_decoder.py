from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPELL_NAMES = {
    0: "Lightning Spell",
    1: "Healing Spell",
    2: "Rage Spell",
    3: "Jump Spell",
    4: "Santa's Surprise",
    5: "Freeze Spell",
    9: "Poison Spell",
    10: "Earthquake Spell",
    11: "Haste Spell",
    16: "Clone Spell",
    17: "Skeleton Spell",
    22: "Birthday Boom",
    28: "Bat Spell",
    35: "Invisibility Spell",
    53: "Recall Spell",
    70: "Overgrowth Spell",
    84: "Yellow Card",
    98: "Revive Spell",
    109: "Ice Block Spell",
    120: "Totem Spell",
    123: "Angry Spell",
}

HERO_NAMES = {
    0: "Barbarian King",
    1: "Archer Queen",
    2: "Grand Warden",
    3: "Battle Machine",
    4: "Royal Champion",
    5: "Battle Copter",
    6: "Minion Prince",
    7: "Dragon Duke",
}

PET_NAMES = {
    0: "L.A.S.S.I",
    1: "Mighty Yak",
    2: "Electro Owl",
    3: "Unicorn",
    4: "Phoenix",
    7: "Poison Lizard",
    8: "Diggy",
    9: "Frosty",
    10: "Spirit Fox",
    11: "Angry Jelly",
    16: "Sneezy",
    17: "Greedy Raven",
}

EQUIPMENT_NAMES = {
    0: "Barbarian Puppet",
    1: "Rage Vial",
    2: "Archer Puppet",
    3: "Invisibility Vial",
    4: "Eternal Tome",
    5: "Life Gem",
    6: "Seeking Shield",
    7: "Royal Gem",
    8: "Earthquake Boots",
    9: "Hog Rider Puppet",
    10: "Giant Gauntlet",
    11: "Vampstache",
    12: "Haste Vial",
    13: "Rocket Spear",
    14: "Spiky Ball",
    15: "Frozen Arrow",
    16: "Monolith Arrow",
    17: "Giant Arrow",
    19: "Heroic Torch",
    20: "Healer Puppet",
    22: "Fireball",
    24: "Rage Gem",
    32: "Snake Bracelet",
    34: "Healing Tome",
    35: "Dark Crown",
    39: "Magic Mirror",
    40: "Electro Boots",
    41: "Lavaloon Puppet",
    42: "Henchmen Puppet",
    43: "Dark Orb",
    44: "Metal Pants",
    47: "Noble Iron",
    48: "Action Figure",
    49: "Meteor Staff",
    50: "Frost Flake",
    51: "Stick Horse",
    52: "Fire Heart",
    53: "Rocket Backpack",
    56: "Stun Blaster",
    57: "Flame Blower",
    59: "Electro Fangs",
}

TROOP_AND_SIEGE_NAMES = {
    0: "Barbarian",
    1: "Archer",
    2: "Goblin",
    3: "Giant",
    4: "Wall Breaker",
    5: "Balloon",
    6: "Wizard",
    7: "Healer",
    8: "Dragon",
    9: "P.E.K.K.A",
    10: "Minion",
    11: "Hog Rider",
    12: "Valkyrie",
    13: "Golem",
    15: "Witch",
    17: "Lava Hound",
    22: "Bowler",
    23: "Baby Dragon",
    24: "Miner",
    26: "Super Barbarian",
    27: "Super Archer",
    28: "Super Wall Breaker",
    29: "Super Giant",
    30: "Ice Wizard",
    45: "Battle Ram",
    47: "Royal Ghost",
    48: "Pumpkin Barbarian",
    50: "Giant Skeleton",
    51: "Wall Wrecker",
    52: "Battle Blimp",
    53: "Yeti",
    55: "Sneaky Goblin",
    56: "Super Miner",
    57: "Rocket Balloon",
    58: "Ice Golem",
    59: "Electro Dragon",
    60: "Golden Dragon",
    61: "Skeleton Barrel",
    62: "Stone Slammer",
    63: "Inferno Dragon",
    64: "Super Valkyrie",
    65: "Dragon Rider",
    66: "Super Witch",
    67: "M.E.C.H.A / El Primo",
    72: "Party Wizard",
    75: "Siege Barracks",
    76: "Ice Hound",
    80: "Super Bowler",
    81: "Super Dragon",
    82: "Headhunter",
    83: "Super Wizard",
    84: "Super Minion",
    87: "Log Launcher",
    91: "Flame Flinger",
    92: "Battle Drill",
    95: "Electro Titan",
    97: "Apprentice Warden",
    98: "Super Hog",
    109: "Ruin Witch",
    110: "Root Rider",
    119: "Firecracker",
    120: "Azure Dragon",
    121: "Barbarian Kicker",
    122: "Giant Thrower",
    123: "Druid",
    125: "Broom Witch",
    132: "Thrower",
    135: "Troop Launcher",
    142: "Snake Barrel",
    147: "Super Yeti",
    150: "Furnace",
    177: "Meteor Golem",
    188: "Sky Wagon",
}

TROOP_HOUSING_SPACE = {
    "Apprentice Warden": 20,
    "Archer": 1,
    "Azure Dragon": 40,
    "Baby Dragon": 10,
    "Balloon": 5,
    "Barbarian": 1,
    "Barbarian Kicker": 12,
    "Battle Ram": 4,
    "Bowler": 6,
    "Broom Witch": 20,
    "Dragon": 20,
    "Dragon Rider": 25,
    "Druid": 16,
    "Electro Dragon": 30,
    "Electro Titan": 32,
    "Firecracker": 10,
    "Furnace": 18,
    "Giant": 5,
    "Giant Skeleton": 20,
    "Giant Thrower": 15,
    "Goblin": 1,
    "Golem": 30,
    "Headhunter": 6,
    "Healer": 14,
    "Hog Rider": 5,
    "Ice Golem": 15,
    "Ice Hound": 40,
    "Inferno Dragon": 15,
    "Lava Hound": 30,
    "Meteor Golem": 40,
    "Miner": 6,
    "Minion": 2,
    "P.E.K.K.A": 25,
    "Party Wizard": 4,
    "Pumpkin Barbarian": 1,
    "Rocket Balloon": 8,
    "Root Rider": 20,
    "Ruin Witch": 26,
    "Skeleton Barrel": 5,
    "Sky Wagon": 1,
    "Sneaky Goblin": 3,
    "Super Archer": 12,
    "Super Barbarian": 5,
    "Super Bowler": 30,
    "Super Dragon": 40,
    "Super Giant": 10,
    "Super Hog Rider": 12,
    "Super Miner": 24,
    "Super Minion": 12,
    "Super Valkyrie": 20,
    "Super Wall Breaker": 8,
    "Super Witch": 40,
    "Super Wizard": 10,
    "Super Yeti": 35,
    "Thrower": 16,
    "Valkyrie": 8,
    "Wall Breaker": 2,
    "Witch": 12,
    "Wizard": 4,
    "Yeti": 18,
}

HERO_ABBREVIATIONS = {
    "Barbarian King": "BK",
    "Archer Queen": "AQ",
    "Grand Warden": "GW",
    "Royal Champion": "RC",
    "Minion Prince": "MP",
    "Dragon Duke": "DD",
}


def short_display_name(name: str | None) -> str:
    if not name:
        return ""
    return {
        "Balloon": "Rocket Loon",
        "Rocket Balloon": "Rocket Loon",
    }.get(name, name)


def acronym(text: str | None) -> str:
    if not text:
        return ""
    parts = [part for part in re.split(r"[^A-Za-z0-9]+", text) if part]
    if not parts:
        return text
    return "".join(part[0].upper() for part in parts)


def decode_named_entries(payload: str, names: dict[int, str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for part in payload.split("-"):
        if "x" not in part:
            continue
        count, unit_id = part.split("x", 1)
        if not (count.isdigit() and unit_id.isdigit()):
            continue
        unit_num = int(unit_id)
        entries.append(
            {
                "count": int(count),
                "id": unit_num,
                "name": names.get(unit_num, f"Unknown ID {unit_num}"),
            }
        )
    return entries


def decode_castle_entries(payload: str) -> dict[str, list[dict[str, Any]]]:
    troops: list[dict[str, Any]] = []
    spells: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    for part in payload.split("-"):
        if "x" not in part:
            continue
        count, unit_id = part.split("x", 1)
        if not (count.isdigit() and unit_id.isdigit()):
            continue
        entry_count = int(count)
        unit_num = int(unit_id)
        if unit_num in SPELL_NAMES:
            spells.append({"count": entry_count, "id": unit_num, "name": SPELL_NAMES[unit_num]})
        elif unit_num in TROOP_AND_SIEGE_NAMES:
            troops.append({"count": entry_count, "id": unit_num, "name": TROOP_AND_SIEGE_NAMES[unit_num]})
        else:
            unknown.append({"count": entry_count, "id": unit_num, "name": f"Unknown ID {unit_num}"})
    return {"troops": troops, "spells": spells, "unknown": unknown}


def decode_hero_section(payload: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for hero_blob in payload.split("-"):
        if not hero_blob:
            continue
        hero_match = re.match(r"(\d+)", hero_blob)
        if not hero_match:
            continue
        hero_id = int(hero_match.group(1))
        tail = hero_blob[hero_match.end() :]
        mode_match = re.match(r"m\d+", tail)
        if mode_match:
            tail = tail[mode_match.end() :]
        pet_entries: list[dict[str, Any]] = []
        equipment_entries: list[dict[str, Any]] = []

        while tail:
            direct_equipment_match = re.match(r"e(\d+(?:_\d+)*)", tail)
            if direct_equipment_match:
                for equip_piece in direct_equipment_match.group(1).split("_"):
                    if equip_piece.isdigit():
                        equip_id = int(equip_piece)
                        equipment_entries.append({"id": equip_id, "name": EQUIPMENT_NAMES.get(equip_id, f"Unknown ID {equip_id}")})
                tail = tail[direct_equipment_match.end() :]
                continue

            pet_match = re.match(r"p(\d+)e(\d+(?:_\d+)*)", tail)
            if pet_match:
                pet_id = int(pet_match.group(1))
                pet_entries.append({"id": pet_id, "name": PET_NAMES.get(pet_id, f"Unknown ID {pet_id}")})
                for equip_piece in pet_match.group(2).split("_"):
                    if equip_piece.isdigit():
                        equip_id = int(equip_piece)
                        equipment_entries.append({"id": equip_id, "name": EQUIPMENT_NAMES.get(equip_id, f"Unknown ID {equip_id}")})
                tail = tail[pet_match.end() :]
                continue

            break

        entries.append(
            {
                "id": hero_id,
                "name": HERO_NAMES.get(hero_id, f"Unknown ID {hero_id}"),
                "pets": pet_entries,
                "equipment": sorted(equipment_entries, key=lambda item: (item.get("name") or "", item.get("id", 0))),
            }
        )
    return entries


def decode_army_share_code(army_code: str) -> dict[str, Any]:
    if not army_code:
        return {"raw": army_code, "sections": {}, "decoded": False, "fullArmy": False}
    sections: dict[str, Any] = {}
    matches = list(re.finditer(r"([husdi])([^husdi]*)", army_code))
    payloads = {match.group(1): match.group(2) for match in matches}
    if payloads.get("u"):
        sections["troops"] = decode_named_entries(payloads["u"], TROOP_AND_SIEGE_NAMES)
    if payloads.get("s"):
        sections["spells"] = decode_named_entries(payloads["s"], SPELL_NAMES)
    if payloads.get("d"):
        castle_entries = decode_castle_entries(payloads["d"])
        if castle_entries["troops"]:
            sections["clanCastleTroops"] = castle_entries["troops"]
        if castle_entries["spells"]:
            sections["clanCastleSpells"] = castle_entries["spells"]
        if castle_entries["unknown"]:
            sections["clanCastleUnknown"] = castle_entries["unknown"]
    if payloads.get("i"):
        sections["reinforcements"] = decode_named_entries(payloads["i"], TROOP_AND_SIEGE_NAMES)
    if payloads.get("h"):
        sections["heroes"] = decode_hero_section(payloads["h"])
    full_army = bool(sections.get("troops") or sections.get("spells"))
    return {
        "raw": army_code,
        "sections": sections,
        "decoded": bool(sections),
        "fullArmy": full_army,
    }


def format_named_section(entries: list[dict[str, Any]], strip_spell_suffix: bool = False) -> str:
    if not entries:
        return "none"
    parts: list[str] = []
    for entry in entries:
        shown = short_display_name(entry.get("name"))
        if strip_spell_suffix and shown.endswith(" Spell"):
            shown = shown[:-6]
        parts.append(f"{entry.get('count', 0)} {shown}")
    return ", ".join(parts)


def format_army_lines(decoded: dict[str, Any]) -> list[str]:
    sections = decoded.get("sections", {}) if isinstance(decoded, dict) else {}
    lines: list[str] = []
    if sections.get("troops"):
        lines.append(f"Troops: {format_named_section(sections['troops'])}")
    cc_entries = list(sections.get("clanCastleTroops", [])) or list(sections.get("reinforcements", []))
    if cc_entries:
        lines.append(f"Clan Castle: {format_named_section(cc_entries)}")
    spell_entries = list(sections.get("spells", [])) + list(sections.get("clanCastleSpells", []))
    if spell_entries:
        lines.append(f"Spells: {format_named_section(spell_entries, strip_spell_suffix=True)}")
    if sections.get("heroes"):
        hero_bits = []
        for hero in sections["heroes"]:
            hero_name = hero.get("name")
            if not hero_name:
                continue
            short_hero = HERO_ABBREVIATIONS.get(hero_name, acronym(hero_name))
            equips = [short_display_name(piece.get("name")) for piece in hero.get("equipment", []) if piece.get("name")]
            pets = [pet.get("name") for pet in hero.get("pets", []) if pet.get("name")]
            details = []
            if equips:
                details.append("eq: " + ", ".join(acronym(name) or name for name in equips[:2]))
            if pets:
                details.append("pet: " + ", ".join(acronym(name) or name for name in pets[:1]))
            hero_bits.append(f"{short_hero}{' (' + '; '.join(details) + ')' if details else ''}")
        lines.append("Heroes: " + "; ".join(hero_bits))
    return lines


def troop_housing_breakdown(decoded: dict[str, Any]) -> list[tuple[str, int]]:
    sections = decoded.get("sections", {}) if isinstance(decoded, dict) else {}
    weighted: list[tuple[str, int]] = []
    for entry in sections.get("troops", []):
        name = entry.get("name")
        count = int(entry.get("count", 0))
        housing = TROOP_HOUSING_SPACE.get(name, 0)
        total = count * housing
        if total > 0:
            weighted.append((name, total))
    weighted.sort(key=lambda item: (-item[1], item[0]))
    return weighted


def hero_names(decoded: dict[str, Any]) -> set[str]:
    sections = decoded.get("sections", {}) if isinstance(decoded, dict) else {}
    names: set[str] = set()
    for hero in sections.get("heroes", []):
        name = hero.get("name")
        if isinstance(name, str):
            names.add(name)
    return names


def hero_equipment_names(decoded: dict[str, Any]) -> set[str]:
    sections = decoded.get("sections", {}) if isinstance(decoded, dict) else {}
    names: set[str] = set()
    for hero in sections.get("heroes", []):
        for equipment in hero.get("equipment", []):
            name = equipment.get("name")
            if isinstance(name, str):
                names.add(name)
    return names


def hero_equipment_pairs(decoded: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    sections = decoded.get("sections", {}) if isinstance(decoded, dict) else {}
    pairs: dict[str, tuple[str, ...]] = {}
    for hero in sections.get("heroes", []):
        hero_name = hero.get("name")
        if not isinstance(hero_name, str):
            continue
        equipment_names = sorted(
            eq.get("name") for eq in hero.get("equipment", []) if isinstance(eq.get("name"), str)
        )
        if equipment_names:
            pairs[hero_name] = tuple(equipment_names)
    return pairs


def categorize_army(decoded: dict[str, Any]) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    sections = decoded.get("sections", {}) if isinstance(decoded, dict) else {}
    troop_counts = tuple(sorted((entry.get("name"), int(entry.get("count", 0))) for entry in sections.get("troops", [])))
    troop_count_map = {name: count for name, count in troop_counts if name}
    troop_names = set(troop_count_map)
    spell_names = tuple(name for name, _count in tuple(sorted((entry.get("name"), int(entry.get("count", 0))) for entry in sections.get("spells", []))) if name)
    hero_names_set = hero_names(decoded)
    hero_equipment = hero_equipment_names(decoded)
    weighted = troop_housing_breakdown(decoded)
    weighted_map = dict(weighted)
    total_housing = sum(space for _name, space in weighted)

    def share(name: str) -> float:
        if total_housing <= 0:
            return 0.0
        return weighted_map.get(name, 0) / total_housing

    if share("Super Yeti") >= 0.35:
        focus = tuple(name for name in ["Super Yeti", "Apprentice Warden", "Druid", "Ice Golem", "Super Wall Breaker"] if name in troop_names)
        return "Super Yeti Smash", focus, spell_names
    if share("Thrower") >= 0.28 and ("Healer" in troop_names or "Furnace" in troop_names):
        focus = tuple(name for name in ["Thrower", "Healer", "Furnace", "Yeti", "Ice Golem", "Super Wall Breaker", "Druid"] if name in troop_names)
        label = "Thrower Yeti Smash" if "Yeti" in troop_names else "Thrower Smash"
        return label, focus, spell_names
    if share("Super Bowler") >= 0.25 and "Healer" in troop_names:
        focus = tuple(name for name in ["Super Bowler", "Healer", "Ice Golem", "Super Wall Breaker", "Apprentice Warden"] if name in troop_names)
        return "Super Bowler Smash", focus, spell_names
    if share("Valkyrie") >= 0.45:
        focus = tuple(name for name in ["Valkyrie", "Log Launcher", "Root Rider", "Rocket Balloon"] if name in troop_names)
        return "Valkyrie Quake", focus, spell_names

    air_units = {
        "Dragon",
        "Dragon Rider",
        "Inferno Dragon",
        "Rocket Balloon",
        "Lava Hound",
        "Balloon",
        "Baby Dragon",
        "Electro Dragon",
        "Super Dragon",
        "Ice Hound",
        "Sky Wagon",
        "Azure Dragon",
    }
    air_share = sum(weighted_map.get(name, 0) for name in air_units) / total_housing if total_housing else 0.0
    if air_share >= 0.45:
        if share("Dragon Rider") >= 0.18:
            focus = tuple(name for name in ["Dragon", "Dragon Rider", "Inferno Dragon", "Rocket Balloon", "Lava Hound", "Sky Wagon", "Baby Dragon"] if name in troop_names)
            return "Dragon Rider Air", focus, spell_names
        if share("Electro Dragon") >= 0.2 or share("Azure Dragon") >= 0.2:
            focus = tuple(name for name in ["Electro Dragon", "Azure Dragon", "Balloon", "Lava Hound", "Rocket Balloon"] if name in troop_names)
            return "Electro Dragon Air", focus, spell_names
        if share("Balloon") >= 0.25 and share("Ice Hound") >= 0.12 and "Grand Warden" in hero_names_set:
            focus = tuple(name for name in ["Balloon", "Ice Hound", "Inferno Dragon", "Baby Dragon", "Valkyrie"] if name in troop_names)
            if "Fireball" in hero_equipment:
                return "Fireball Air", focus, spell_names
            return "Warden Lalo", focus, spell_names
        if share("Dragon") >= 0.2 or share("Super Dragon") >= 0.2 or share("Balloon") >= 0.25:
            focus = tuple(name for name in ["Dragon", "Super Dragon", "Balloon", "Inferno Dragon", "Rocket Balloon", "Baby Dragon", "Ice Hound"] if name in troop_names)
            return "Dragon Air", focus, spell_names

    core = tuple(name for name, _space in weighted[:4] if name)
    if core:
        return f"{core[0]} Composition", core, spell_names
    return "Mixed Composition", tuple(name for name, _count in troop_counts if name), spell_names


def spell_style_label(decoded: dict[str, Any]) -> str:
    sections = decoded.get("sections", {}) if isinstance(decoded, dict) else {}
    spells = {entry.get("name"): int(entry.get("count", 0)) for entry in sections.get("spells", [])}
    hero_equipment = hero_equipment_names(decoded)
    warden_fireball = "Fireball" in hero_equipment and "Grand Warden" in hero_names(decoded)
    invis = spells.get("Invisibility Spell", 0)
    totem = spells.get("Totem Spell", 0)
    quake = spells.get("Earthquake Spell", 0)
    revive = spells.get("Revive Spell", 0)
    freeze = spells.get("Freeze Spell", 0)
    rage = spells.get("Rage Spell", 0)

    if warden_fireball and invis >= 5:
        return "Warden Fireball"
    if invis >= 5:
        return "Invis Charge"
    if totem >= 4:
        return "Totem Spam"
    if quake >= 4:
        return "Earthquake Heavy"
    if revive >= 2:
        return "Revive Heavy"
    if freeze >= 4:
        return "Freeze Heavy"
    if rage >= 4:
        return "Rage Heavy"
    return "Balanced"


def group_label(decoded: dict[str, Any]) -> str:
    label, _focus, _spell_names = categorize_army(decoded)
    if label == "Dragon Rider Air":
        dd_equipment = hero_equipment_pairs(decoded).get("Dragon Duke", ())
        if "Electro Fangs" in dd_equipment:
            return "Dragon Rider Air (DD Electro Fangs)"
        if "Rocket Backpack" in dd_equipment:
            return "Dragon Rider Air (DD Rocket Backpack)"
        return "Dragon Rider Air (DD Other)"
    return label


def grouping_key(decoded: dict[str, Any]) -> str:
    base = group_label(decoded)
    style = spell_style_label(decoded)
    if style == "Balanced":
        return base
    return f"{base} - {style}"


def attack_signature(attack: dict[str, Any]) -> str:
    decoded = attack.get("armyDecoded", {})
    if not isinstance(decoded, dict):
        return ""
    sections = decoded.get("sections", {}) if isinstance(decoded.get("sections", {}), dict) else {}
    troops = tuple(sorted((int(entry.get("id", 0)), int(entry.get("count", 0))) for entry in sections.get("troops", [])))
    spells = tuple(sorted((int(entry.get("id", 0)), int(entry.get("count", 0))) for entry in sections.get("spells", [])))
    heroes = tuple(
        sorted(
            (
                entry.get("name", ""),
                tuple(sorted((eq.get("name", "") for eq in entry.get("equipment", [])))) if isinstance(entry.get("equipment", []), list) else (),
            )
            for entry in sections.get("heroes", [])
        )
    )
    return json.dumps({"troops": troops, "spells": spells, "heroes": heroes}, sort_keys=True)


def compute_attack_stats(attacks: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(attacks)
    stars_total = sum(int(attack.get("stars") or 0) for attack in attacks)
    destruction_total = sum(int(attack.get("destructionPercentage") or 0) for attack in attacks)
    three_stars = sum(1 for attack in attacks if int(attack.get("stars") or 0) == 3)
    return {
        "attack_count": count,
        "stars_total": stars_total,
        "destruction_total": destruction_total,
        "avg_stars": round(stars_total / count, 3) if count else 0,
        "avg_destruction": round(destruction_total / count, 3) if count else 0,
        "three_star_rate": round((three_stars / count) * 100, 3) if count else 0,
    }


def best_attacks_by_player(attacks: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_player: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for attack in attacks:
        player_tag = attack.get("playerTag")
        if player_tag:
            by_player[player_tag].append(attack)

    retained: list[dict[str, Any]] = []
    player_details: dict[str, Any] = {}
    for player_tag, player_attacks in by_player.items():
        signatures: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for attack in player_attacks:
            signatures[attack_signature(attack)].append(attack)
        if not signatures:
            continue
        best_signature, best_attacks = max(
            signatures.items(),
            key=lambda item: (
                len(item[1]),
                max(int(a.get("stars", 0)) for a in item[1]),
                max(int(a.get("destructionPercentage", 0)) for a in item[1]),
            ),
        )
        retained.extend(best_attacks)
        player_attacks_stats = compute_attack_stats(best_attacks)
        player_details[player_tag] = {
            "best_army_count": len(best_attacks),
            "stats": player_attacks_stats,
        }
    retained.sort(key=lambda x: (x.get("battleTimestamp") or "", x.get("playerTag") or ""))
    return retained, player_details


def summarize_grouped_armies(attacks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for attack in attacks:
        decoded = attack.get("armyDecoded", {})
        if not isinstance(decoded, dict):
            continue
        player_tag = attack.get("playerTag") or ""
        key = grouping_key(decoded)
        group = grouped.setdefault(
            key,
            {
                "label": key,
                "count": 0,
                "players": {},
                "attacks": [],
                "example": decoded,
            },
        )
        group["count"] += 1
        group["attacks"].append(attack)
        group["example"] = group["example"] or decoded
        if player_tag:
            player_bucket = group["players"].setdefault(
                player_tag,
                {
                    "tag": player_tag,
                    "name": attack.get("playerName"),
                    "attack_count": 0,
                    "attacks": [],
                },
            )
            player_bucket["attack_count"] += 1
            player_bucket["attacks"].append(attack)

    result: list[dict[str, Any]] = []
    for group in grouped.values():
        player_rows: list[dict[str, Any]] = []
        for player in group["players"].values():
            stats = compute_attack_stats(player["attacks"])
            best_attack = max(
                player["attacks"],
                key=lambda attack: (
                    int(attack.get("stars", 0)),
                    int(attack.get("destructionPercentage", 0)),
                    attack.get("battleTimestamp") or "",
                ),
            )
            player_rows.append(
                {
                    "tag": player["tag"],
                    "name": player.get("name"),
                    "attack_count": player["attack_count"],
                    "stats": stats,
                    "best_attack": best_attack,
                }
            )
        player_rows.sort(key=lambda row: (-row["stats"]["avg_stars"], -row["stats"]["avg_destruction"], row.get("name") or row["tag"]))
        result.append(
            {
                "label": group["label"],
                "count": group["count"],
                "unique_users": len(group["players"]),
                "stats": compute_attack_stats(group["attacks"]),
                "example": group["example"],
                "players": player_rows,
            }
        )
    result.sort(key=lambda item: (-item["unique_users"], -item["count"], item["label"]))
    return result


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    attacks: list[dict[str, Any]] = []
    if not path.exists():
        return attacks
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        attacks.append(json.loads(line))
    return attacks


def build_site_payload(snapshot: dict[str, Any], daily_attacks: list[dict[str, Any]], tracking_day: str) -> dict[str, Any]:
    decoded_attacks: list[dict[str, Any]] = []
    for attack in daily_attacks:
        decoded = decode_army_share_code(str(attack.get("armyShareCode") or ""))
        if not decoded.get("decoded"):
            continue
        decoded_attacks.append({**attack, "armyDecoded": decoded, "armyLabel": group_label(decoded), "spellStyle": spell_style_label(decoded)})

    retained_attacks, player_details = best_attacks_by_player(decoded_attacks)
    groups = summarize_grouped_armies(retained_attacks)
    overall_stats = compute_attack_stats(retained_attacks)

    payload_groups: list[dict[str, Any]] = []
    for group in groups:
        payload_groups.append(
            {
                "label": group["label"],
                "count": group["count"],
                "uniqueUsers": group["unique_users"],
                "stats": group["stats"],
                "example": group["example"],
                "players": group["players"],
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tracking_day": tracking_day,
        "snapshot": {
            "tracking_day": snapshot.get("tracking_day"),
            "count": snapshot.get("count"),
            "created_at": snapshot.get("created_at"),
        },
        "stats": {
            "top_players": len(snapshot.get("players", [])),
            "attack_records": len(decoded_attacks),
            "favorite_groups": len(payload_groups),
            "avg_attacks_per_player": round(len(retained_attacks) / max(len(player_details), 1), 1),
            "most_popular_army": payload_groups[0]["count"] if payload_groups else 0,
            "overall": overall_stats,
        },
        "players": player_details,
        "groups": payload_groups,
    }

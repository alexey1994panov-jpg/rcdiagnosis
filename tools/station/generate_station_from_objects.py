# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from pathlib import Path
import re


def get_obj_states(obj: ET.Element) -> dict[int, str]:
    states: dict[int, str] = {}
    obj_state = obj.find("ObjState")
    if obj_state is not None:
        for state in obj_state.findall("State"):
            number = int(state.get("Number", 0))
            condition = state.get("Condition", "")
            states[number] = condition
    return states


def make_const_name(prefix: str, raw_name: str) -> str:
    """
    Build a safe Python identifier for generated constants.
    Keeps unicode letters/digits, replaces all separators with underscore.
    """
    name = (raw_name or "").replace("-", "_")
    name = name.replace("&sol;", "_")
    # Keep generated identifiers strictly ASCII-safe.
    name = re.sub(r"[^A-Za-z0-9_]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        name = "OBJ"
    if name[0].isdigit():
        name = f"_{name}"
    return f"{prefix}_{name}"


def get_obj_type(obj: ET.Element) -> int:
    otype = obj.get("Type", "")

    if otype.startswith("1000.1."):
        return 1  # Р Р¦

    if otype.startswith("1000.2."):
        return 2  # РЎС‚СЂРµР»РєРё

    # РЎРІРµС‚РѕС„РѕСЂС‹
    if otype.startswith("1000.3."):
        return 3  # РјР°РЅРµРІСЂРѕРІС‹Рµ

    if otype.startswith("1000.4."):
        return 4  # РїСѓС‚РµРІС‹Рµ

    # Р·Р°РїР°СЃРЅРѕР№ РІР°СЂРёР°РЅС‚: РїРѕР·РґРЅРёРµ СЃ LensG
    if obj.find("ObjData[@NAME='LensG']") is not None:
        return 4

    if otype.startswith("1000.9."):
        return 9  # РРЅРґРёРєР°С‚РѕСЂС‹/РїСЂРѕС‡РёРµ РјРЅРµРјРѕ-РѕР±СЉРµРєС‚С‹ (РіСЂСѓРїРїР° 1000.9.*)

    return 0


def get_obj_subtype(obj: ET.Element) -> int:
    """Р’РѕР·РІСЂР°С‰Р°РµС‚ subtype РґР»СЏ Type РІРёРґР° 1000.X.Y (Y -> int), РёРЅР°С‡Рµ 0."""
    otype = obj.get("Type", "")
    parts = otype.split(".")
    if len(parts) < 3:
        return 0
    try:
        return int(parts[2])
    except Exception:
        return 0


def resolve_ref(obj: ET.Element, data_name: str) -> str | None:
    data = obj.find(f"ObjData[@NAME='{data_name}']")
    if data is None:
        return None
    ref = data.get("Ref", "")
    if not ref:
        return None
    return ref.split("/")[-1] or None


def resolve_ref_obj(
    obj: ET.Element,
    data_name: str,
    root: ET.Element,
) -> tuple[str | None, ET.Element | None]:
    """Р’РѕР·РІСЂР°С‰Р°РµС‚ (NAME, Object) РїРѕ Ref РёР· ObjData."""
    data = obj.find(f"ObjData[@NAME='{data_name}']")
    if data is None:
        return None, None
    ref = data.get("Ref", "")
    if not ref:
        return None, None
    name = ref.split("/")[-1]
    if not name:
        return None, None
    for o in root.findall("Object"):
        if o.get("NAME") == name:
            return name, o
    return name, None


def get_rc_prev_next(obj: ET.Element, root: ET.Element) -> tuple[str | None, str | None]:
    """РўРѕР»СЊРєРѕ РґР»СЏ Р Р¦: PrevSec/NextSec, РµСЃР»Рё СЃСЃС‹Р»РєРё РІРµРґСѓС‚ РЅР° РѕР±СЉРµРєС‚С‹ С‚РёРїР° Р Р¦."""
    prev_name, prev_obj = resolve_ref_obj(obj, "PrevSec", root)
    next_name, next_obj = resolve_ref_obj(obj, "NextSec", root)

    prev_sec: str | None = None
    next_sec: str | None = None

    if prev_obj is not None and get_obj_type(prev_obj) == 1:
        prev_sec = prev_name
    if next_obj is not None and get_obj_type(next_obj) == 1:
        next_sec = next_name

    return prev_sec, next_sec


def get_sig_prev_next(obj: ET.Element, root: ET.Element) -> tuple[str | None, str | None]:
    """
    Р”Р»СЏ СЃРІРµС‚РѕС„РѕСЂР°: PrevSec/NextSec, РЅРѕ СѓС‡РёС‚С‹РІР°РµРј СЃСЃС‹Р»РєСѓ С‚РѕР»СЊРєРѕ РµСЃР»Рё РѕРЅР° РІРµРґС‘С‚ РЅР° Р Р¦ (type == 1).
    Р•СЃР»Рё СЃСЃС‹Р»РєР° РЅР° РЅРµ-Р Р¦, СЃС‡РёС‚Р°РµРј РµС‘ РїСѓСЃС‚РѕР№.
    """
    prev_name, prev_obj = resolve_ref_obj(obj, "PrevSec", root)
    next_name, next_obj = resolve_ref_obj(obj, "NextSec", root)

    prev_sec: str | None = None
    next_sec: str | None = None

    if prev_obj is not None and get_obj_type(prev_obj) == 1:
        prev_sec = prev_name
    if next_obj is not None and get_obj_type(next_obj) == 1:
        next_sec = next_name

    return prev_sec, next_sec


def generate() -> None:
    try:
        base_dir = Path(__file__).resolve().parent.parent.parent
        xml_path = base_dir / "xml" / "Objects.xml"
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"РћС€РёР±РєР° Р·Р°РіСЂСѓР·РєРё С„Р°Р№Р»Р°: {e}")
        return

    objects = root.findall("Object")

    consts: dict[str, str] = {}
    nodes: dict[str, dict] = {}
    states_graph: dict[str, dict[int, str]] = {}

    groups = {
        "rc_ids": [],
        "switches_ids": [],
        "shunt_signals_ids": [],
        "train_signals_ids": [],
        "indicator_ids": [],
    }
    indicator_subtypes: dict[str, list[str]] = {}
    indicators: dict[str, dict[str, object]] = {}

    rc_sections: dict[str, dict[str, object]] = {}

    # -------- РїРµСЂРІС‹Р№ РїСЂРѕС…РѕРґ: Р Р¦ + СЃС‚СЂРµР»РєРё + СЃРІРµС‚РѕС„РѕСЂС‹ --------
    for obj in objects:
        oid = obj.get("ID")
        name = obj.get("NAME")
        if oid is None or name is None:
            continue

        otype = get_obj_type(obj)
        if otype == 0:
            continue

        # РєРѕРЅСЃС‚Р°РЅС‚С‹ RC_*, SW_*, SIG_*
        prefix = "RC" if otype == 1 else "SW" if otype == 2 else "SIG" if otype in (3, 4) else "IND"
        # Include object id to avoid collisions when names are normalized.
        var_name = make_const_name(prefix, f"{name}_{oid}")
        consts[var_name] = oid

        # РіСЂСѓРїРїС‹
        if otype == 1:
            groups["rc_ids"].append(oid)
        elif otype == 2:
            groups["switches_ids"].append(oid)
        elif otype == 3:
            groups["shunt_signals_ids"].append(oid)
        elif otype == 4:
            groups["train_signals_ids"].append(oid)
        elif otype == 9:
            groups["indicator_ids"].append(oid)
            st = str(get_obj_subtype(obj))
            indicator_subtypes.setdefault(st, []).append(oid)

        # prev_links / next_links
        if otype == 1:
            # Р Р¦ вЂ” РїРѕ СЃС‚СЂРѕРіРѕР№ СЃС…РµРјРµ
            prev_links: list[str] = []
            next_links: list[str] = []
            prev_sec, next_sec = get_rc_prev_next(obj, root)
            if prev_sec:
                prev_links.append(prev_sec)
            if next_sec:
                next_links.append(next_sec)
        elif otype in (3, 4):
            # СЃРІРµС‚РѕС„РѕСЂС‹ вЂ” С‚РѕР»СЊРєРѕ РЅР° Р Р¦
            prev_links = []
            next_links = []
            prev_sec, next_sec = get_sig_prev_next(obj, root)
            if prev_sec:
                prev_links.append(prev_sec)
            if next_sec:
                next_links.append(next_sec)
        else:
            prev_links, next_links = [], []

        # Р·Р°РґР°С‡Рё вЂ” С‚РѕР»СЊРєРѕ Сѓ Р Р¦
        tasks: list[dict[str, str]] = []
        if otype == 1:
            for task in obj.findall("ObjTask"):
                t_name = task.get("NAME", "") or ""
                if "LZ" in t_name or "LS" in t_name:
                    tasks.append(
                        {
                            "name": t_name,
                            "class": task.get("CLASS"),
                            "desc": task.get("Description"),
                        }
                    )

        nodes[oid] = {
            "name": name,
            "type": otype,
            "subtype": get_obj_subtype(obj),
            "prev_links": prev_links,
            "next_links": next_links,
            "tasks": tasks,
        }
        if otype == 9:
            indicators[oid] = {
                "name": name,
                "type_code": obj.get("Type", ""),
                "subtype": get_obj_subtype(obj),
            }

        states_graph[oid] = get_obj_states(obj)

        # RC_SECTIONS вЂ” С‚РѕР»СЊРєРѕ РґР»СЏ Р Р¦ (РїРѕ СЃС…РµРјРµ PrevSec/NextSec РјРµР¶РґСѓ Р Р¦)
        if otype == 1:
            prev_sec, next_sec = get_rc_prev_next(obj, root)
            rc_sections[name] = {
                "PrevSec": prev_sec,
                "NextSec": next_sec,
                "Switches": [],
            }

    # -------- РІС‚РѕСЂРѕР№ РїСЂРѕС…РѕРґ: СЃС‚СЂРµР»РєРё --------
    for obj in objects:
        sw_name = obj.get("NAME")
        if sw_name is None:
            continue

        otype = get_obj_type(obj)
        if otype != 2:
            continue

        sw_section_rc = resolve_ref(obj, "SwSection")
        if not sw_section_rc or sw_section_rc not in rc_sections:
            continue

        next_mi = resolve_ref(obj, "NextMi")
        next_pl = resolve_ref(obj, "NextPl")
        next_sw_pl = resolve_ref(obj, "NextSwPl")
        next_sw_mi = resolve_ref(obj, "NextSwMi")
        prev_sw = resolve_ref(obj, "PrevSw")

        sw_info = {
            "name": sw_name,
            "NextMi": next_mi,
            "NextPl": next_pl,
            "NextSwPl": next_sw_pl,
            "NextSwMi": next_sw_mi,
            "PrevSw": prev_sw,
        }

        rc_sections[sw_section_rc]["Switches"].append(sw_info)

    # -------- Р·Р°РїРёСЃСЊ С„Р°Р№Р»РѕРІ --------
    out_station_config = Path(__file__).resolve().parent / "station_config.py"
    out_rc_sections = Path(__file__).resolve().parent / "station_rc_sections.py"

    with out_station_config.open("w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n\n")
        for k in sorted(consts.keys()):
            f.write(f"{k} = '{consts[k]}'\n")
        f.write("\nGROUPS = {\n")
        for k, v in groups.items():
            f.write(f"    '{k}': {v},\n")
        f.write("}\n\n")
        f.write("INDICATOR_SUBTYPES = {\n")
        for k in sorted(indicator_subtypes.keys(), key=lambda x: int(x)):
            f.write(f"    '{k}': {indicator_subtypes[k]},\n")
        f.write("}\n\n")
        f.write("INDICATORS = {\n")
        for oid, info in indicators.items():
            f.write(f"    '{oid}': {info},\n")
        f.write("}\n\n")
        f.write("NODES = {\n")
        for nid, data in nodes.items():
            f.write(f"    '{nid}': {data},\n")
        f.write("}\n\n")
        f.write("STATES_GRAPH = {\n")
        for nid, states in states_graph.items():
            f.write(f"    '{nid}': {states},\n")
        f.write("}\n")

    with out_rc_sections.open("w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n\n")
        f.write("RC_SECTIONS = {\n")
        for rc_name, data in rc_sections.items():
            f.write(f"    '{rc_name}': {data},\n")
        f.write("}\n")


if __name__ == "__main__":
    generate()


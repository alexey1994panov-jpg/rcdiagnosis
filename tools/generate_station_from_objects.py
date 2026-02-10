# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from pathlib import Path


def get_obj_states(obj: ET.Element) -> dict[int, str]:
    states: dict[int, str] = {}
    obj_state = obj.find("ObjState")
    if obj_state is not None:
        for state in obj_state.findall("State"):
            number = int(state.get("Number", 0))
            condition = state.get("Condition", "")
            states[number] = condition
    return states


def get_obj_type(obj: ET.Element) -> int:
    otype = obj.get("Type", "")

    if otype.startswith("1000.1."):
        return 1  # РЦ

    if otype.startswith("1000.2."):
        return 2  # Стрелки

    # Светофоры
    if otype.startswith("1000.3."):
        return 3  # маневровые

    if otype.startswith("1000.4."):
        return 4  # путевые

    # запасной вариант: поздние с LensG
    if obj.find("ObjData[@NAME='LensG']") is not None:
        return 4

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
    """Возвращает (NAME, Object) по Ref из ObjData."""
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
    """Только для РЦ: PrevSec/NextSec, если ссылки ведут на объекты типа РЦ."""
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
    Для светофора: PrevSec/NextSec, но учитываем ссылку только если она ведёт на РЦ (type == 1).
    Если ссылка на не-РЦ, считаем её пустой.
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
        base_dir = Path(__file__).resolve().parent.parent
        xml_path = base_dir / "xml" / "Objects.xml"
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
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
    }

    rc_sections: dict[str, dict[str, object]] = {}

    # -------- первый проход: РЦ + стрелки + светофоры --------
    for obj in objects:
        oid = obj.get("ID")
        name = obj.get("NAME")
        if oid is None or name is None:
            continue

        otype = get_obj_type(obj)
        if otype == 0:
            continue

        # константы RC_*, SW_*, SIG_*
        prefix = "RC" if otype == 1 else "SW" if otype == 2 else "SIG"
        var_name = f"{prefix}_{name.replace('-', '_')}"
        consts[var_name] = oid

        # группы
        if otype == 1:
            groups["rc_ids"].append(oid)
        elif otype == 2:
            groups["switches_ids"].append(oid)
        elif otype == 3:
            groups["shunt_signals_ids"].append(oid)
        elif otype == 4:
            groups["train_signals_ids"].append(oid)

        # prev_links / next_links
        if otype == 1:
            # РЦ — по строгой схеме
            prev_links: list[str] = []
            next_links: list[str] = []
            prev_sec, next_sec = get_rc_prev_next(obj, root)
            if prev_sec:
                prev_links.append(prev_sec)
            if next_sec:
                next_links.append(next_sec)
        elif otype in (3, 4):
            # светофоры — только на РЦ
            prev_links = []
            next_links = []
            prev_sec, next_sec = get_sig_prev_next(obj, root)
            if prev_sec:
                prev_links.append(prev_sec)
            if next_sec:
                next_links.append(next_sec)
        else:
            prev_links, next_links = [], []

        # задачи — только у РЦ
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
            "prev_links": prev_links,
            "next_links": next_links,
            "tasks": tasks,
        }

        states_graph[oid] = get_obj_states(obj)

        # RC_SECTIONS — только для РЦ (по схеме PrevSec/NextSec между РЦ)
        if otype == 1:
            prev_sec, next_sec = get_rc_prev_next(obj, root)
            rc_sections[name] = {
                "PrevSec": prev_sec,
                "NextSec": next_sec,
                "Switches": [],
            }

    # -------- второй проход: стрелки --------
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

    # -------- запись файлов --------
    with open("station_config.py", "w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n\n")
        for k in sorted(consts.keys()):
            f.write(f"{k} = '{consts[k]}'\n")
        f.write("\nGROUPS = {\n")
        for k, v in groups.items():
            f.write(f"    '{k}': {v},\n")
        f.write("}\n\n")
        f.write("NODES = {\n")
        for nid, data in nodes.items():
            f.write(f"    '{nid}': {data},\n")
        f.write("}\n\n")
        f.write("STATES_GRAPH = {\n")
        for nid, states in states_graph.items():
            f.write(f"    '{nid}': {states},\n")
        f.write("}\n")

    with open("station_rc_sections.py", "w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n\n")
        f.write("RC_SECTIONS = {\n")
        for rc_name, data in rc_sections.items():
            f.write(f"    '{rc_name}': {data},\n")
        f.write("}\n")


if __name__ == "__main__":
    generate()

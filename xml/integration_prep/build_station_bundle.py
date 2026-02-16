from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
import xml.etree.ElementTree as ET


TYPE_RC = "1000.1"
TYPE_SWITCH = "1000.2"
TYPE_SIGNAL_SHUNT = "1000.3"
TYPE_SIGNAL_TRAIN = "1000.4"
TYPE_INDICATOR = "1000.9"


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _type_family(type_name: str | None) -> str:
    if not type_name:
        return ""
    parts = type_name.split(".")
    if len(parts) >= 2:
        return ".".join(parts[:2])
    return type_name


def _xml_text_to_number(raw: str | None) -> Any:
    if raw is None:
        return None
    s = str(raw).strip()
    if s == "":
        return None
    s = s.replace(",", ".")
    try:
        if "." in s:
            return float(s)
        return int(s)
    except Exception:
        return raw


def _find_objdata_ref(obj: ET.Element, data_name: str) -> Optional[str]:
    for node in obj.findall("ObjData"):
        if node.attrib.get("NAME") == data_name:
            ref = node.attrib.get("Ref")
            if not ref:
                return None
            return ref
    return None


def _extract_state_numbers(obj: ET.Element) -> List[int]:
    out: List[int] = []
    obj_state = obj.find("ObjState")
    if obj_state is None:
        return out
    for st in obj_state.findall("State"):
        raw = st.attrib.get("Number")
        try:
            if raw is not None:
                out.append(int(raw))
        except Exception:
            continue
    return sorted(set(out))


def _ref_last_name(ref: str | None) -> Optional[str]:
    if not ref:
        return None
    name = ref.split("/")[-1]
    return name or None


@dataclass
class ObjRef:
    obj_id: str
    obj_name: str
    obj_type: str
    obj_class: str


def parse_objects(objects_xml: Path) -> Dict[str, Any]:
    root = ET.parse(objects_xml).getroot()
    objects: List[Dict[str, Any]] = []
    by_name: Dict[str, ObjRef] = {}
    by_id: Dict[str, ObjRef] = {}

    for obj in root.findall("Object"):
        attrs = dict(obj.attrib)
        obj_name = attrs.get("NAME", "")
        obj_id = attrs.get("ID", "")
        obj_type = attrs.get("Type", "")
        obj_class = attrs.get("CLASS", "")
        desc = attrs.get("Description")

        objdata_refs: Dict[str, str] = {}
        for od in obj.findall("ObjData"):
            n = od.attrib.get("NAME")
            r = od.attrib.get("Ref")
            if n and r:
                objdata_refs[n] = r

        tasks: List[Dict[str, Any]] = []
        for t in obj.findall("ObjTask"):
            tasks.append(
                {
                    "name": t.attrib.get("NAME"),
                    "description": t.attrib.get("Description"),
                    "class": t.attrib.get("CLASS"),
                    "number": t.attrib.get("Number"),
                    "adk_number": t.attrib.get("AdkNumber"),
                }
            )

        rec = {
            "id": obj_id,
            "name": obj_name,
            "description": desc,
            "type": obj_type,
            "type_family": _type_family(obj_type),
            "class": obj_class,
            "attrs": attrs,
            "objdata_refs": objdata_refs,
            "tasks": tasks,
            "state_numbers": _extract_state_numbers(obj),
        }
        objects.append(rec)
        if obj_name:
            by_name[obj_name] = ObjRef(obj_id=obj_id, obj_name=obj_name, obj_type=obj_type, obj_class=obj_class)
        if obj_id:
            by_id[obj_id] = ObjRef(obj_id=obj_id, obj_name=obj_name, obj_type=obj_type, obj_class=obj_class)

    rc, sw, sig_sh, sig_tr, ind = [], [], [], [], []
    for o in objects:
        fam = o.get("type_family")
        if fam == TYPE_RC:
            rc.append(o)
        elif fam == TYPE_SWITCH:
            sw.append(o)
        elif fam == TYPE_SIGNAL_SHUNT:
            sig_sh.append(o)
        elif fam == TYPE_SIGNAL_TRAIN:
            sig_tr.append(o)
        elif fam == TYPE_INDICATOR:
            ind.append(o)

    return {
        "objects": objects,
        "by_name": by_name,
        "by_id": by_id,
        "rc": rc,
        "switches": sw,
        "signals_shunt": sig_sh,
        "signals_train": sig_tr,
        "indicators": ind,
    }


def build_topology(parsed: Dict[str, Any]) -> Dict[str, Any]:
    by_name: Dict[str, ObjRef] = parsed["by_name"]

    rc_sections: Dict[str, Dict[str, Any]] = {}
    rc_by_id: Dict[str, str] = {}
    for rc in parsed["rc"]:
        name = rc["name"]
        rid = rc["id"]
        rc_by_id[rid] = name
        prev_name = _ref_last_name(rc["objdata_refs"].get("PrevSec"))
        next_name = _ref_last_name(rc["objdata_refs"].get("NextSec"))

        prev_rc = prev_name if (prev_name in by_name and _type_family(by_name[prev_name].obj_type) == TYPE_RC) else None
        next_rc = next_name if (next_name in by_name and _type_family(by_name[next_name].obj_type) == TYPE_RC) else None
        rc_sections[name] = {"PrevSec": prev_rc, "NextSec": next_rc, "Switches": []}

    # Indicator sections: objects 1000.9.* that define PrevSec/NextSec.
    indicator_sections: Dict[str, Dict[str, Any]] = {}
    indicator_by_id: Dict[str, str] = {}
    indicator_candidates = [i for i in parsed["indicators"] if i["objdata_refs"].get("PrevSec") or i["objdata_refs"].get("NextSec")]
    indicator_names = {i["name"] for i in indicator_candidates}
    all_section_names = set(rc_sections.keys()) | indicator_names

    for ind in indicator_candidates:
        iname = ind["name"]
        iid = ind["id"]
        indicator_by_id[iid] = iname
        prev_name = _ref_last_name(ind["objdata_refs"].get("PrevSec"))
        next_name = _ref_last_name(ind["objdata_refs"].get("NextSec"))
        prev_sec = prev_name if (prev_name in all_section_names) else None
        next_sec = next_name if (next_name in all_section_names) else None
        indicator_sections[iname] = {
            "PrevSec": prev_sec,
            "NextSec": next_sec,
            "Switches": [],
            "kind": "indicator_section",
            "allowed_states": [3, 4],
            "source_type": ind.get("type"),
            "source_subtype": ind.get("attrs", {}).get("Type"),
        }

    route_sections: Dict[str, Dict[str, Any]] = {}
    for k, v in rc_sections.items():
        rec = dict(v)
        rec["kind"] = "rc_section"
        route_sections[k] = rec
    for k, v in indicator_sections.items():
        route_sections[k] = dict(v)

    switches_by_id: Dict[str, str] = {}
    for sw in parsed["switches"]:
        switches_by_id[sw["id"]] = sw["name"]
        section_name = _ref_last_name(sw["objdata_refs"].get("SwSection"))
        if not section_name or section_name not in rc_sections:
            continue
        sw_info = {
            "name": sw["name"],
            "NextMi": _ref_last_name(sw["objdata_refs"].get("NextMi")),
            "NextPl": _ref_last_name(sw["objdata_refs"].get("NextPl")),
            "NextSwPl": _ref_last_name(sw["objdata_refs"].get("NextSwPl")),
            "NextSwMi": _ref_last_name(sw["objdata_refs"].get("NextSwMi")),
            "PrevSw": _ref_last_name(sw["objdata_refs"].get("PrevSw")),
        }
        rc_sections[section_name]["Switches"].append(sw_info)

    # Resolve signal section refs (RC + indicator sections).
    signals: List[Dict[str, Any]] = []
    for sig in list(parsed["signals_shunt"]) + list(parsed["signals_train"]):
        prev_name = _ref_last_name(sig["objdata_refs"].get("PrevSec"))
        next_name = _ref_last_name(sig["objdata_refs"].get("NextSec"))
        prev_rc = prev_name if (prev_name in route_sections) else None
        next_rc = next_name if (next_name in route_sections) else None
        signals.append(
            {
                "id": sig["id"],
                "name": sig["name"],
                "kind": "shunt" if sig["type_family"] == TYPE_SIGNAL_SHUNT else "train",
                "prev_rc": prev_rc,
                "next_rc": next_rc,
            }
        )

    return {
        "rc_sections": rc_sections,
        "indicator_sections": indicator_sections,
        "route_sections": route_sections,
        "rc_by_id": rc_by_id,
        "indicator_by_id": indicator_by_id,
        "switches_by_id": switches_by_id,
        "signals": signals,
    }


def parse_iosystem(iosystem_xml: Path) -> Dict[str, Any]:
    root = ET.parse(iosystem_xml).getroot()
    modules: List[Dict[str, Any]] = []

    def walk(node: ET.Element, path: str) -> None:
        name = node.attrib.get("NAME", "")
        cur = f"{path}/{name}" if path else name
        if _local_name(node.tag) == "MODULE":
            modules.append(
                {
                    "name": name,
                    "number": node.attrib.get("NUMBER"),
                    "address": node.attrib.get("ADDRESS"),
                    "from": node.attrib.get("FROM"),
                    "path": cur,
                }
            )
        for ch in list(node):
            if _local_name(ch.tag) == "MODULE":
                walk(ch, cur)

    walk(root, "")
    return {"root_name": root.attrib.get("NAME"), "root_class": root.attrib.get("CLASS"), "modules": modules}


def parse_diagparams(diag_xml: Path) -> Dict[str, Any]:
    root = ET.parse(diag_xml).getroot()
    by_object: Dict[str, Dict[str, Dict[str, Any]]] = {}

    # Layout: DiagParams(root) -> DiagParams(object) -> DiagParams(task) -> DiagParam(...)
    for obj_node in root.findall("DiagParams"):
        obj_name = obj_node.attrib.get("NAME", "")
        if not obj_name:
            continue
        task_map: Dict[str, Dict[str, Any]] = {}
        for task_node in obj_node.findall("DiagParams"):
            task_name = task_node.attrib.get("NAME", "")
            if not task_name:
                continue
            params: Dict[str, Any] = {}
            raw_params: Dict[str, Dict[str, Any]] = {}
            for p in task_node.findall("DiagParam"):
                pname = p.attrib.get("NAME")
                if not pname:
                    continue
                raw_val = p.attrib.get("Value")
                params[pname] = _xml_text_to_number(raw_val)
                raw_params[pname] = dict(p.attrib)
            task_map[task_name] = {"params": params, "raw_params": raw_params}
        by_object[obj_name] = task_map

    return {"by_object_task": by_object}


def _default_manual_indicators() -> Dict[str, Any]:
    return {
        "version": 1,
        "description": "Manual test indicators. This file is preserved across station re-imports.",
        "indicators": [],
    }


def _build_auto_indicators(parsed_objects: Dict[str, Any], topology: Dict[str, Any]) -> Dict[str, Any]:
    indicator_sections = topology.get("indicator_sections", {}) or {}
    items = []
    for ind in parsed_objects["indicators"]:
        name = ind.get("name")
        state_numbers = ind.get("state_numbers", []) or []
        # Request: indicator sections use states 3/4 in RC-like logic.
        allowed = [3, 4] if name in indicator_sections else state_numbers
        items.append(
            {
                "id": ind.get("id"),
                "name": name,
                "type": ind.get("type"),
                "type_family": ind.get("type_family"),
                "subtype": (ind.get("attrs", {}) or {}).get("Type"),
                "is_indicator_section": name in indicator_sections,
                "prev_section": (indicator_sections.get(name, {}) or {}).get("PrevSec"),
                "next_section": (indicator_sections.get(name, {}) or {}).get("NextSec"),
                "allowed_states": allowed,
                "state_numbers_in_xml": state_numbers,
            }
        )
    return {
        "version": 1,
        "description": "Auto parsed indicators from Objects.xml. Regenerated on each build.",
        "indicators": items,
    }


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_project_seed_from_diag(
    parsed_objects: Dict[str, Any], diag: Dict[str, Any], topology: Dict[str, Any]
) -> Dict[str, Any]:
    # Conservative seed. We intentionally avoid over-guessing variant/time mapping.
    obj_task = diag["by_object_task"]

    # Use one known RC as sample if exists.
    sample_rc_name = None
    for rc in parsed_objects["rc"]:
        sample_rc_name = rc["name"]
        break

    sample_lz = {}
    sample_ls = {}
    if sample_rc_name and sample_rc_name in obj_task:
        # Typical names in source xml
        lz_task = obj_task[sample_rc_name].get("Логическая ложная занятость РЦ", {}).get("params", {})
        ls_task = obj_task[sample_rc_name].get("Логическая ложная свободность РЦ", {}).get("params", {})
        sample_lz = lz_task
        sample_ls = ls_task

    return {
        "station": "from_xml",
        "mapping_status": "needs_manual_mapping",
        "notes": [
            "Values extracted from DiagParams.xml.",
            "Direct mapping from NT* to project option keys is not always 1:1 and must be confirmed.",
            "Objects.xml remains source-of-truth for links and topology.",
        ],
        "detector_options_seed": {
            "global": {
                "t_pk": None,
                "t_mu": None,
                "t_recent_ls": None,
                "t_min_maneuver_v8": None,
                "t_ls_mu": None,
                "t_ls_after_lz": None,
                "t_ls_dsp": None,
                "enable_lz_exc_mu": None,
                "enable_lz_exc_recent_ls": None,
                "enable_lz_exc_dsp": None,
                "enable_ls_exc_mu": None,
                "enable_ls_exc_after_lz": None,
                "enable_ls_exc_dsp": None,
            },
            "lz_sample_from_diagparams": sample_lz,
            "ls_sample_from_diagparams": sample_ls,
            "per_variant_enable_default": {
                "enable_lz1": None,
                "enable_lz2": None,
                "enable_lz3": None,
                "enable_lz4": None,
                "enable_lz5": None,
                "enable_lz6": None,
                "enable_lz7": None,
                "enable_lz8": None,
                "enable_lz9": None,
                "enable_lz10": None,
                "enable_lz11": None,
                "enable_lz12": None,
                "enable_lz13": None,
                "enable_ls1": None,
                "enable_ls2": None,
                "enable_ls4": None,
                "enable_ls5": None,
                "enable_ls6": None,
                "enable_ls9": None,
            },
        },
        "topology_summary": {
            "rc_count": len(topology["rc_sections"]),
            "switch_count": len(topology["switches_by_id"]),
            "signal_count": len(topology["signals"]),
        },
    }


def build_bundle(objects_xml: Path, iosystem_xml: Path, diag_xml: Path, out_dir: Path) -> None:
    parsed_objects = parse_objects(objects_xml)
    topology = build_topology(parsed_objects)
    iosys = parse_iosystem(iosystem_xml)
    diag = parse_diagparams(diag_xml)

    canonical = {
        "meta": {
            "objects_source": str(objects_xml),
            "iosystem_source": str(iosystem_xml),
            "diagparams_source": str(diag_xml),
            "object_count_total": len(parsed_objects["objects"]),
            "object_type_family_counts": dict(
                sorted(Counter(o.get("type_family") or "UNKNOWN" for o in parsed_objects["objects"]).items())
            ),
        },
        "objects": {
            "rc": parsed_objects["rc"],
            "switches": parsed_objects["switches"],
            "signals_shunt": parsed_objects["signals_shunt"],
            "signals_train": parsed_objects["signals_train"],
            "indicators": parsed_objects["indicators"],
        },
        "name_to_id": {o["name"]: o["id"] for o in parsed_objects["objects"] if o.get("name") and o.get("id")},
        "id_to_name": {o["id"]: o["name"] for o in parsed_objects["objects"] if o.get("name") and o.get("id")},
        "iosystem": iosys,
    }

    compat_station_config = {
        "groups": {
            "rc_ids": sorted([o["id"] for o in parsed_objects["rc"] if o.get("id")]),
            "switches_ids": sorted([o["id"] for o in parsed_objects["switches"] if o.get("id")]),
            "shunt_signals_ids": sorted([o["id"] for o in parsed_objects["signals_shunt"] if o.get("id")]),
            "train_signals_ids": sorted([o["id"] for o in parsed_objects["signals_train"] if o.get("id")]),
            "indicator_ids": sorted([o["id"] for o in parsed_objects["indicators"] if o.get("id")]),
            "indicator_section_ids": sorted(
                [
                    o["id"]
                    for o in parsed_objects["indicators"]
                    if o.get("id") and o.get("name") in (topology.get("indicator_sections", {}) or {})
                ]
            ),
        },
        "nodes": {
            o["id"]: {
                "name": o["name"],
                "type_family": o["type_family"],
                "prev_links": [_ref_last_name(o["objdata_refs"].get("PrevSec"))] if o["objdata_refs"].get("PrevSec") else [],
                "next_links": [_ref_last_name(o["objdata_refs"].get("NextSec"))] if o["objdata_refs"].get("NextSec") else [],
                "tasks": o.get("tasks", []),
                "state_numbers": o.get("state_numbers", []),
                "is_indicator_section": bool(
                    o["type_family"] == TYPE_INDICATOR
                    and o.get("name") in (topology.get("indicator_sections", {}) or {})
                ),
                "allowed_states_for_logic": [3, 4]
                if (
                    o["type_family"] == TYPE_INDICATOR
                    and o.get("name") in (topology.get("indicator_sections", {}) or {})
                )
                else o.get("state_numbers", []),
            }
            for o in parsed_objects["objects"]
            if o.get("id")
        },
    }

    compat_station_rc_sections = topology["rc_sections"]
    compat_station_route_sections = topology["route_sections"]

    # Manual indicators file: never overwrite if already present.
    manual_path = out_dir / "manual" / "indicators_manual.json"
    if not manual_path.exists():
        _write_json(manual_path, _default_manual_indicators())

    _write_json(out_dir / "canonical" / "station_bundle.json", canonical)
    _write_json(out_dir / "derived" / "topology_rc_sections.json", topology)
    _write_json(out_dir / "compat" / "station_config_like.json", compat_station_config)
    _write_json(out_dir / "compat" / "station_rc_sections_like.json", compat_station_rc_sections)
    _write_json(out_dir / "compat" / "station_route_sections_like.json", compat_station_route_sections)
    _write_json(out_dir / "config" / "diagparams_by_object_task.json", diag["by_object_task"])
    _write_json(out_dir / "config" / "project_detector_options.seed.json", _build_project_seed_from_diag(parsed_objects, diag, topology))
    _write_json(out_dir / "config" / "indicators_auto.json", _build_auto_indicators(parsed_objects, topology))

    manifest = {
        "status": "ok",
        "output_dir": str(out_dir),
        "files": [
            "canonical/station_bundle.json",
            "derived/topology_rc_sections.json",
            "compat/station_config_like.json",
            "compat/station_rc_sections_like.json",
            "compat/station_route_sections_like.json",
            "config/diagparams_by_object_task.json",
            "config/project_detector_options.seed.json",
            "config/indicators_auto.json",
            "manual/indicators_manual.json",
        ],
        "counts": {
            "objects_total": len(parsed_objects["objects"]),
            "rc": len(parsed_objects["rc"]),
            "switches": len(parsed_objects["switches"]),
            "signals_shunt": len(parsed_objects["signals_shunt"]),
            "signals_train": len(parsed_objects["signals_train"]),
            "indicators": len(parsed_objects["indicators"]),
            "indicator_sections": len(topology.get("indicator_sections", {})),
            "route_sections_total": len(topology.get("route_sections", {})),
        },
    }
    _write_json(out_dir / "manifest.json", manifest)


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Prepare station integration bundle from XML.")
    parser.add_argument("--objects", type=Path, default=here.parent / "Objects.xml")
    parser.add_argument("--iosystem", type=Path, default=here.parent / "IOSystem.xml")
    parser.add_argument("--diagparams", type=Path, default=here.parent / "DiagParams.xml")
    parser.add_argument("--out-dir", type=Path, default=here / "output" / "visochino")
    args = parser.parse_args()

    build_bundle(args.objects, args.iosystem, args.diagparams, args.out_dir)
    print(f"Done: {args.out_dir}")


if __name__ == "__main__":
    main()

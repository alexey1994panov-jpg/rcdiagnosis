from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Any
import re
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Bounds:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y


def _to_float(value: str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _point_tuple(point_el: ET.Element) -> Tuple[float, float]:
    return (_to_float(point_el.attrib.get("X")), _to_float(point_el.attrib.get("Y")))


def _norm_key(value: str) -> str:
    v = (value or "").upper()
    v = v.replace("&SOL;", "/")
    v = v.replace("СП", "SP")
    v = v.replace("АП", "AP")
    v = v.replace("НДП", "NDP")
    v = v.replace("ЧДП", "CHDP")
    v = v.replace("НП", "NP")
    v = v.replace("ЧП", "CHP")
    v = v.replace("П", "P")
    v = v.replace("А", "A")
    v = v.replace("Н", "N")
    v = v.replace("Ч", "CH")
    v = v.replace("Д", "D")
    return re.sub(r"[^A-Z0-9/_-]+", "", v)


def _collect_signal_ids(objects_root: ET.Element) -> set[str]:
    signal_ids: set[str] = set()
    for obj_el in objects_root.findall("Object"):
        name = obj_el.attrib.get("NAME", "")
        type_code = obj_el.attrib.get("Type", "")
        if type_code.startswith("1000.3.") or type_code.startswith("1000.4."):
            signal_ids.add(name)
    return signal_ids


def _collect_indicator_map(objects_root: ET.Element) -> Dict[str, Dict[str, Any]]:
    indicators: Dict[str, Dict[str, Any]] = {}
    for obj_el in objects_root.findall("Object"):
        name = obj_el.attrib.get("NAME", "")
        type_code = obj_el.attrib.get("Type", "")
        if not name or not type_code.startswith("1000.9."):
            continue
        parts = type_code.split(".")
        subtype = 0
        if len(parts) >= 3:
            try:
                subtype = int(parts[2])
            except ValueError:
                subtype = 0
        indicators[name] = {
            "type_code": type_code,
            "subtype": subtype,
            "id": obj_el.attrib.get("ID", ""),
        }
    return indicators


def _compute_bounds(points: List[Tuple[float, float]]) -> Bounds:
    if not points:
        return Bounds(0.0, 0.0, 1.0, 1.0)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return Bounds(min(xs), min(ys), max(xs), max(ys))


def build_station_layout(
    station_xml: Path,
    objects_xml: Path,
    station_name: str = "Visochino",
) -> Dict[str, Any]:
    station_root = ET.parse(station_xml).getroot()
    objects_root = ET.parse(objects_xml).getroot()
    signal_ids = _collect_signal_ids(objects_root)
    indicator_map = _collect_indicator_map(objects_root)

    rails: List[Dict[str, Any]] = []
    switches: List[Dict[str, Any]] = []
    signals: List[Dict[str, Any]] = []
    labels: List[Dict[str, Any]] = []
    indicators: List[Dict[str, Any]] = []
    all_points: List[Tuple[float, float]] = []

    draw_elements = station_root.find(".//GOGROUP[@NAME='DrawElements']")
    if draw_elements is None:
        return {
            "station": station_name,
            "rails": [],
            "switches": [],
            "signals": [],
            "labels": [],
            "indicators": [],
            "bounds": {"min_x": 0, "min_y": 0, "max_x": 1, "max_y": 1, "width": 1, "height": 1, "padding": 40},
        }

    for group in draw_elements.findall("GOGROUP"):
        group_name = group.attrib.get("NAME", "")
        group_obj = group.attrib.get("Obj", "")
        group_norm = _norm_key(group_name)

        for go in group.findall("GO"):
            go_class = go.attrib.get("CLASS", "")
            const = go.find("Const")
            if const is None:
                continue

            if go_class == "DrawRailChain":
                pts = [_point_tuple(p) for p in const.findall("Point")]
                if len(pts) < 2:
                    continue
                all_points.extend(pts)
                rails.append(
                    {
                        "id": f"rail-{len(rails)+1}",
                        "group_name": group_name,
                        "group_key": group_norm,
                        "object_ref": group_obj,
                        "points": [[x, y] for x, y in pts],
                    }
                )
                continue

            if go_class == "DrawSwitch":
                minus = [_point_tuple(p) for p in const.findall("./Minus/Point")]
                plus = [_point_tuple(p) for p in const.findall("./Plus/Point")]
                section = [_point_tuple(p) for p in const.findall("./Section/Point")]
                x = _to_float(const.attrib.get("X"))
                y = _to_float(const.attrib.get("Y"))
                local = [(x, y)] + minus + plus + section
                all_points.extend(local)
                switches.append(
                    {
                        "id": f"switch-{len(switches)+1}",
                        "switch_name": group_name,
                        "switch_key": group_norm,
                        "x": x,
                        "y": y,
                        "minus": [[px, py] for px, py in minus],
                        "plus": [[px, py] for px, py in plus],
                        "section": [[px, py] for px, py in section],
                    }
                )
                continue

            if go_class == "DrawSignal":
                x = _to_float(const.attrib.get("X"))
                y = _to_float(const.attrib.get("Y"))
                radius = _to_float(const.attrib.get("Radius"), 7.0)
                all_points.append((x, y))
                signal_name = group_name if group_name in signal_ids else group_name
                signals.append(
                    {
                        "id": f"signal-{len(signals)+1}",
                        "signal_name": signal_name,
                        "signal_key": _norm_key(signal_name),
                        "x": x,
                        "y": y,
                        "radius": radius,
                        "orientation": int(_to_float(const.attrib.get("Orientation"), 0)),
                    }
                )
                continue

            if go_class in {"DrawText", "DrawTextBox"}:
                text = const.attrib.get("Text", "")
                if not text:
                    continue
                x = _to_float(const.attrib.get("X"))
                y = _to_float(const.attrib.get("Y"))
                all_points.append((x, y))
                labels.append(
                    {
                        "id": f"label-{len(labels)+1}",
                        "group_name": group_name,
                        "text": text,
                        "x": x,
                        "y": y,
                        "class": go_class,
                    }
                )
                continue

            # Generic icon-based draw object linked to Objects.xml indicator (1000.9.*).
            if go_class == "DrawImgList":
                object_name = group_obj.split("/")[-1] if group_obj else group_name
                indicator = indicator_map.get(object_name)
                if indicator is None:
                    continue
                x = _to_float(const.attrib.get("X"))
                y = _to_float(const.attrib.get("Y"))
                all_points.append((x, y))
                indicators.append(
                    {
                        "id": f"indicator-{len(indicators)+1}",
                        "object_name": object_name,
                        "object_id": indicator.get("id", ""),
                        "type_code": indicator.get("type_code", ""),
                        "subtype": indicator.get("subtype", 0),
                        "x": x,
                        "y": y,
                        "image": const.attrib.get("Image", ""),
                        "angle": _to_float(const.attrib.get("Angle"), 0.0),
                        "count": int(_to_float(const.attrib.get("Count"), 0)),
                    }
                )

    bounds = _compute_bounds(all_points)
    return {
        "station": station_name,
        "rails": rails,
        "switches": switches,
        "signals": signals,
        "labels": labels,
        "indicators": indicators,
        "bounds": {
            "min_x": bounds.min_x,
            "min_y": bounds.min_y,
            "max_x": bounds.max_x,
            "max_y": bounds.max_y,
            "width": bounds.width,
            "height": bounds.height,
            "padding": 40,
        },
    }

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from fastapi import HTTPException


def build_station_layout_response(
    station: str,
    *,
    xml_dir: Path,
    layout_cache: Dict[str, Dict[str, Any]],
    api_build: str,
    build_station_layout: Any,
    fix_mojibake: Any,
    nodes: Dict[str, Dict[str, Any]],
    rc_sections: Dict[str, Any],
) -> Dict[str, Any]:
    cache_key = station.strip().lower() or "visochino"
    if cache_key in layout_cache:
        return layout_cache[cache_key]

    station_xml = xml_dir / "Station.xml"
    objects_xml = xml_dir / "Objects.xml"
    if not station_xml.exists() or not objects_xml.exists():
        raise HTTPException(status_code=500, detail="Station XML files not found")
    try:
        layout = build_station_layout(station_xml=station_xml, objects_xml=objects_xml, station_name=station)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cannot build station layout: {exc}")

    for rail in layout.get("rails", []):
        if isinstance(rail, dict):
            rail["group_name"] = fix_mojibake(str(rail.get("group_name", "")))
    for sw in layout.get("switches", []):
        if isinstance(sw, dict):
            sw["switch_name"] = fix_mojibake(str(sw.get("switch_name", "")))
    for sig in layout.get("signals", []):
        if isinstance(sig, dict):
            sig["signal_name"] = fix_mojibake(str(sig.get("signal_name", "")))
    for lbl in layout.get("labels", []):
        if isinstance(lbl, dict):
            lbl["text"] = fix_mojibake(str(lbl.get("text", "")))
            lbl["group_name"] = fix_mojibake(str(lbl.get("group_name", "")))

    rc_catalog: List[str] = []
    switch_catalog: List[str] = []
    signal_catalog: List[str] = []
    switch_to_rc: Dict[str, str] = {}
    rc_id_to_name: Dict[str, str] = {}
    for oid, node in nodes.items():
        ntype = int(node.get("type", 0))
        name = fix_mojibake(str(node.get("name", "")).strip())
        oid = str(oid)
        if not name:
            continue
        if ntype == 1:
            rc_catalog.append(name)
            if oid:
                rc_id_to_name[oid] = name
        elif ntype == 2:
            switch_catalog.append(name)
        elif ntype in (3, 4):
            signal_catalog.append(name)
    for raw_rc_name, rc_meta in rc_sections.items():
        rc_name = fix_mojibake(str(raw_rc_name))
        for sw in (rc_meta or {}).get("Switches", []):
            sw_name = fix_mojibake(str((sw or {}).get("name", "")).strip())
            if sw_name and rc_name:
                switch_to_rc[sw_name] = rc_name
    layout["rc_catalog"] = sorted(set(rc_catalog))
    layout["switch_catalog"] = sorted(set(switch_catalog), key=lambda x: (len(str(x)), str(x)))
    layout["signal_catalog"] = sorted(set(signal_catalog))
    layout["switch_to_rc"] = switch_to_rc
    layout["rc_id_to_name"] = rc_id_to_name
    layout["api_build"] = api_build
    layout_cache[cache_key] = layout
    return layout


def build_node_catalog(*, nodes: Dict[str, Dict[str, Any]], fix_mojibake: Any) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    for oid, node in nodes.items():
        items.append(
            {
                "id": str(oid),
                "name": fix_mojibake(str(node.get("name", ""))),
                "type": int(node.get("type", 0)),
                "subtype": int(node.get("subtype", 0)),
            }
        )
    return {"nodes": items}

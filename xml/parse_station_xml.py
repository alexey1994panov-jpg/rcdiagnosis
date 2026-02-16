from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _find_first_child_by_tag(node: ET.Element, tag: str) -> ET.Element | None:
    for ch in list(node):
        if _local_name(ch.tag) == tag:
            return ch
    return None


def parse_station(xml_path: Path) -> tuple[list[dict], list[dict], dict]:
    root = ET.parse(xml_path).getroot()
    draw_elements = None
    for ch in list(root):
        if _local_name(ch.tag) == "GOGROUP" and ch.attrib.get("NAME") == "DrawElements":
            draw_elements = ch
            break

    groups: list[dict] = []
    go_flat: list[dict] = []

    if draw_elements is not None:
        for grp in list(draw_elements):
            if _local_name(grp.tag) != "GOGROUP":
                continue
            group_name = grp.attrib.get("NAME", "")
            group_obj = grp.attrib.get("Obj", "")
            group_class = grp.attrib.get("CLASS", "")
            go_count = 0
            for go in list(grp):
                if _local_name(go.tag) != "GO":
                    continue
                go_count += 1
                const = _find_first_child_by_tag(go, "Const")
                go_flat.append(
                    {
                        "group_name": group_name,
                        "group_obj": group_obj,
                        "go_name": go.attrib.get("NAME", ""),
                        "go_class": go.attrib.get("CLASS", ""),
                        "x": (const.attrib.get("X") if const is not None else None),
                        "y": (const.attrib.get("Y") if const is not None else None),
                        "text": (const.attrib.get("Text") if const is not None else None),
                    }
                )
            groups.append(
                {
                    "name": group_name,
                    "obj": group_obj,
                    "class": group_class,
                    "go_count": go_count,
                }
            )

    summary = {
        "group_count": len(groups),
        "go_count": len(go_flat),
        "go_class_counts": dict(sorted(Counter(x["go_class"] for x in go_flat).items())),
    }
    return groups, go_flat, summary


def main(argv: list[str] | None = None) -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Parse Station.xml (draw objects and groups).")
    parser.add_argument("--input", type=Path, default=here / "Station.xml")
    parser.add_argument("--out-dir", type=Path, default=here / "parsed" / "station")
    args = parser.parse_args(argv)

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    groups, go_flat, summary = parse_station(args.input)

    (out_dir / "station_groups.json").write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "station_go_flat.json").write_text(json.dumps(go_flat, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "station_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Parsed groups: {len(groups)}")
    print(f"Parsed GO: {len(go_flat)}")
    print(f"Output dir: {out_dir}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _parse_module(node: ET.Element, parent_path: str) -> dict:
    name = node.attrib.get("NAME", "")
    current_path = f"{parent_path}/{name}" if parent_path else name
    module = {
        "name": name,
        "number": node.attrib.get("NUMBER"),
        "address": node.attrib.get("ADDRESS"),
        "from": node.attrib.get("FROM"),
        "path": current_path,
        "attrs": dict(node.attrib),
        "children": [],
    }
    for child in list(node):
        if _local_name(child.tag) == "MODULE":
            module["children"].append(_parse_module(child, current_path))
    return module


def _flatten_modules(module_tree: dict) -> list[dict]:
    items = []

    def walk(node: dict) -> None:
        items.append(
            {
                "name": node["name"],
                "number": node.get("number"),
                "address": node.get("address"),
                "from": node.get("from"),
                "path": node["path"],
            }
        )
        for ch in node.get("children", []):
            walk(ch)

    walk(module_tree)
    return items


def parse_iosystem(xml_path: Path) -> tuple[dict, list[dict]]:
    root = ET.parse(xml_path).getroot()
    tree = {
        "name": root.attrib.get("NAME", ""),
        "class": root.attrib.get("CLASS", ""),
        "attrs": dict(root.attrib),
        "modules": [],
    }
    for child in list(root):
        if _local_name(child.tag) == "MODULE":
            tree["modules"].append(_parse_module(child, tree["name"]))

    flat = []
    for mod in tree["modules"]:
        flat.extend(_flatten_modules(mod))
    return tree, flat


def main(argv: list[str] | None = None) -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Parse IOSystem.xml.")
    parser.add_argument("--input", type=Path, default=here / "IOSystem.xml")
    parser.add_argument("--out-dir", type=Path, default=here / "parsed" / "iosystem")
    args = parser.parse_args(argv)

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    tree, flat = parse_iosystem(args.input)
    summary = {
        "root_name": tree["name"],
        "root_class": tree["class"],
        "module_total": len(flat),
    }

    (out_dir / "iosystem_tree.json").write_text(json.dumps(tree, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "iosystem_modules_flat.json").write_text(
        json.dumps(flat, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "iosystem_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Parsed modules: {len(flat)}")
    print(f"Output dir: {out_dir}")


if __name__ == "__main__":
    main()

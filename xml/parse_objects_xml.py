from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _sanitize_filename(name: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    return clean.strip("._") or "UNKNOWN"


def _type_family(type_name: str | None) -> str:
    if not type_name:
        return "UNKNOWN"
    parts = type_name.split(".")
    if len(parts) >= 2:
        return ".".join(parts[:2])
    return type_name


def _element_to_dict(el: ET.Element) -> dict:
    node: dict = {"tag": _local_name(el.tag)}
    if el.attrib:
        node["attrs"] = dict(el.attrib)
    text = (el.text or "").strip()
    if text:
        node["text"] = text
    children = []
    for child in list(el):
        if isinstance(child.tag, str):
            children.append(_element_to_dict(child))
    if children:
        node["children"] = children
    return node


def parse_objects(xml_path: Path) -> list[dict]:
    root = ET.parse(xml_path).getroot()
    result: list[dict] = []
    for obj in root:
        if _local_name(obj.tag) != "Object":
            continue
        attrs = dict(obj.attrib)
        record = {
            "name": attrs.get("NAME"),
            "description": attrs.get("Description"),
            "type": attrs.get("Type"),
            "id": attrs.get("ID"),
            "adk_type": attrs.get("ADKType"),
            "class": attrs.get("CLASS"),
            "attrs": attrs,
            "children": [_element_to_dict(ch) for ch in list(obj) if isinstance(ch.tag, str)],
        }
        result.append(record)
    return result


def write_outputs(records: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    exact_dir = out_dir / "by_type_exact"
    family_dir = out_dir / "by_type_family"
    exact_dir.mkdir(parents=True, exist_ok=True)
    family_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "objects_all.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    by_exact: dict[str, list[dict]] = defaultdict(list)
    by_family: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        t = rec.get("type") or "UNKNOWN"
        f = _type_family(t)
        by_exact[t].append(rec)
        by_family[f].append(rec)

    for t, items in sorted(by_exact.items()):
        filename = f"{_sanitize_filename(t)}.json"
        (exact_dir / filename).write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    for f, items in sorted(by_family.items()):
        filename = f"{_sanitize_filename(f)}.json"
        (family_dir / filename).write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    exact_index = dict(sorted(Counter(rec.get("type") or "UNKNOWN" for rec in records).items()))
    family_index = dict(sorted(Counter(_type_family(rec.get("type")) for rec in records).items()))
    name_to_type = {rec.get("name") or "": rec.get("type") or "UNKNOWN" for rec in records}

    (out_dir / "type_index.json").write_text(
        json.dumps(exact_index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "type_family_index.json").write_text(
        json.dumps(family_index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "object_name_to_type.json").write_text(
        json.dumps(dict(sorted(name_to_type.items())), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Parse Objects.xml and split JSON by object type.")
    parser.add_argument("--input", type=Path, default=here / "Objects.xml")
    parser.add_argument("--out-dir", type=Path, default=here / "parsed" / "objects")
    args = parser.parse_args(argv)

    records = parse_objects(args.input)
    write_outputs(records, args.out_dir)
    print(f"Parsed objects: {len(records)}")
    print(f"Output dir: {args.out_dir}")


if __name__ == "__main__":
    main()

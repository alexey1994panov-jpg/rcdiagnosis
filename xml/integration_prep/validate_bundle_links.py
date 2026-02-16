from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _type_family(type_name: str | None) -> str:
    if not type_name:
        return ""
    parts = type_name.split(".")
    if len(parts) >= 2:
        return ".".join(parts[:2])
    return type_name


@dataclass
class ValidationReport:
    status: str
    errors_count: int
    warnings_count: int
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]


def _check_unique(values: List[str], label: str, errors: List[str], warnings: List[str]) -> None:
    seen: Set[str] = set()
    dup: Set[str] = set()
    for v in values:
        if not v:
            continue
        if v in seen:
            dup.add(v)
        seen.add(v)
    if dup:
        errors.append(f"{label}: duplicates found ({len(dup)}), samples: {sorted(list(dup))[:10]}")


def _check_object_refs(canonical: Dict[str, Any], errors: List[str], warnings: List[str]) -> Dict[str, Any]:
    name_to_id = canonical.get("name_to_id", {}) or {}
    objects_group = canonical.get("objects", {}) or {}
    all_objects: List[Dict[str, Any]] = []
    for k in ("rc", "switches", "signals_shunt", "signals_train", "indicators"):
        all_objects.extend(objects_group.get(k, []) or [])

    broken_refs = []
    typed_refs = {
        "PrevSec": {"1000.1", "1000.9"},
        "NextSec": {"1000.1", "1000.9"},
        "SwSection": {"1000.1"},
    }

    for obj in all_objects:
        oname = obj.get("name")
        orefs = obj.get("objdata_refs", {}) or {}
        for ref_name, ref_path in orefs.items():
            # Validate only station object refs. IO refs and external refs are not topology errors.
            if "/Station/Objects/" not in str(ref_path):
                continue
            target_name = str(ref_path).split("/")[-1] if ref_path else None
            if not target_name:
                continue
            if target_name not in name_to_id:
                broken_refs.append((oname, ref_name, target_name))
                continue

            # Typed ref checks where obvious.
            expected_families = typed_refs.get(ref_name)
            if expected_families:
                # resolve target object by scanning all.
                t_obj = next((x for x in all_objects if x.get("name") == target_name), None)
                tf = _type_family((t_obj or {}).get("type"))
                if tf and tf not in expected_families:
                    warnings.append(
                        f"Typed ref mismatch: {oname}.{ref_name} -> {target_name} (family={tf}, expected={sorted(expected_families)})"
                    )

    if broken_refs:
        errors.append(
            f"Broken object refs: {len(broken_refs)} entries, samples: "
            + "; ".join([f"{a}.{b}->{c}" for a, b, c in broken_refs[:10]])
        )
    return {"broken_refs_count": len(broken_refs)}


def _check_topology_vs_compat(
    derived: Dict[str, Any], compat_sections: Dict[str, Any], errors: List[str], warnings: List[str]
) -> Dict[str, Any]:
    topo_sections = derived.get("rc_sections", {}) or {}
    t_names = set(topo_sections.keys())
    c_names = set(compat_sections.keys())
    only_topo = sorted(t_names - c_names)
    only_compat = sorted(c_names - t_names)
    if only_topo:
        errors.append(f"Sections only in derived topology: {len(only_topo)}, samples: {only_topo[:10]}")
    if only_compat:
        errors.append(f"Sections only in compat sections: {len(only_compat)}, samples: {only_compat[:10]}")

    mismatches = []
    for s in sorted(t_names & c_names):
        t = topo_sections.get(s, {})
        c = compat_sections.get(s, {})
        if t.get("PrevSec") != c.get("PrevSec") or t.get("NextSec") != c.get("NextSec"):
            mismatches.append(s)
    if mismatches:
        errors.append(f"Prev/Next mismatches between derived and compat: {len(mismatches)}, samples: {mismatches[:10]}")

    return {
        "sections_topology_count": len(t_names),
        "sections_compat_count": len(c_names),
        "section_prevnext_mismatch_count": len(mismatches),
    }


def _check_switch_links(derived: Dict[str, Any], errors: List[str], warnings: List[str]) -> Dict[str, Any]:
    sections = derived.get("rc_sections", {}) or {}
    unknown_refs = []
    switch_nodes = 0
    for sec_name, data in sections.items():
        switches = data.get("Switches", []) or []
        for sw in switches:
            switch_nodes += 1
            for key in ("NextMi", "NextPl"):
                target = sw.get(key)
                if target and target not in sections:
                    unknown_refs.append((sec_name, sw.get("name"), key, target))
            for key in ("NextSwPl", "NextSwMi", "PrevSw"):
                # switch-to-switch refs are checked only for non-empty string shape
                target = sw.get(key)
                if target and not isinstance(target, str):
                    warnings.append(f"Non-string switch link at {sec_name}/{sw.get('name')}.{key}: {target!r}")

    if unknown_refs:
        errors.append(
            f"Switch links to unknown RC sections: {len(unknown_refs)}, samples: "
            + "; ".join([f"{a}/{b}.{k}->{v}" for a, b, k, v in unknown_refs[:10]])
        )
    return {"switch_nodes_count": switch_nodes, "switch_unknown_rc_refs_count": len(unknown_refs)}


def _check_signals(derived: Dict[str, Any], errors: List[str], warnings: List[str]) -> Dict[str, Any]:
    sections = set((derived.get("route_sections", {}) or {}).keys()) or set((derived.get("rc_sections", {}) or {}).keys())
    signals = derived.get("signals", []) or []
    bad = []
    dangling = []
    for s in signals:
        prev_rc = s.get("prev_rc")
        next_rc = s.get("next_rc")
        if prev_rc and prev_rc not in sections:
            bad.append((s.get("name"), "prev_rc", prev_rc))
        if next_rc and next_rc not in sections:
            bad.append((s.get("name"), "next_rc", next_rc))
        if not prev_rc and not next_rc:
            dangling.append(s.get("name"))

    if bad:
        errors.append(
            f"Signals with unknown RC refs: {len(bad)}, samples: "
            + "; ".join([f"{a}.{b}->{c}" for a, b, c in bad[:10]])
        )
    if dangling:
        warnings.append(f"Signals with both prev_rc/next_rc empty: {len(dangling)}, samples: {dangling[:10]}")
    return {"signals_count": len(signals), "signals_dangling_count": len(dangling), "signals_bad_rc_refs_count": len(bad)}


def validate_bundle(out_dir: Path) -> ValidationReport:
    errors: List[str] = []
    warnings: List[str] = []
    metrics: Dict[str, Any] = {}

    canonical = _load_json(out_dir / "canonical" / "station_bundle.json")
    derived = _load_json(out_dir / "derived" / "topology_rc_sections.json")
    compat_cfg = _load_json(out_dir / "compat" / "station_config_like.json")
    compat_sections = _load_json(out_dir / "compat" / "station_rc_sections_like.json")

    groups = (compat_cfg.get("groups", {}) or {})
    _check_unique(groups.get("rc_ids", []) or [], "groups.rc_ids", errors, warnings)
    _check_unique(groups.get("switches_ids", []) or [], "groups.switches_ids", errors, warnings)
    _check_unique(groups.get("train_signals_ids", []) or [], "groups.train_signals_ids", errors, warnings)
    _check_unique(groups.get("shunt_signals_ids", []) or [], "groups.shunt_signals_ids", errors, warnings)

    metrics.update(_check_object_refs(canonical, errors, warnings))
    metrics.update(_check_topology_vs_compat(derived, compat_sections, errors, warnings))
    metrics.update(_check_switch_links(derived, errors, warnings))
    metrics.update(_check_signals(derived, errors, warnings))
    metrics.update(
        {
            "group_rc_count": len(groups.get("rc_ids", []) or []),
            "group_switch_count": len(groups.get("switches_ids", []) or []),
            "group_train_signal_count": len(groups.get("train_signals_ids", []) or []),
            "group_shunt_signal_count": len(groups.get("shunt_signals_ids", []) or []),
        }
    )

    status = "ok" if not errors else "failed"
    return ValidationReport(
        status=status,
        errors_count=len(errors),
        warnings_count=len(warnings),
        errors=errors,
        warnings=warnings,
        metrics=metrics,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate prepared station bundle links/topology.")
    parser.add_argument("--out-dir", type=Path, default=Path("xml/integration_prep/output/visochino"))
    args = parser.parse_args()

    out_dir = args.out_dir
    report = validate_bundle(out_dir)
    report_dict = asdict(report)
    report_path = out_dir / "validation_report.json"
    report_path.write_text(json.dumps(report_dict, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report_dict, ensure_ascii=False, indent=2))
    print(f"Saved: {report_path}")


if __name__ == "__main__":
    main()

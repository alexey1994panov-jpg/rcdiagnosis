from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Set
import sys


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    parser = argparse.ArgumentParser(description="Compare prepared compat JSON with current runtime station data.")
    parser.add_argument(
        "--compat-config",
        type=Path,
        default=Path("xml/integration_prep/output/visochino/compat/station_config_like.json"),
    )
    parser.add_argument(
        "--compat-sections",
        type=Path,
        default=Path("xml/integration_prep/output/visochino/compat/station_rc_sections_like.json"),
    )
    args = parser.parse_args()

    compat_cfg = _load_json(args.compat_config)
    compat_sec = _load_json(args.compat_sections)

    # Runtime imports are read-only; no modifications are performed.
    from tools.station.station_config import GROUPS, NODES  # type: ignore
    from tools.station.station_rc_sections import RC_SECTIONS  # type: ignore

    new_rc_ids = set(compat_cfg.get("groups", {}).get("rc_ids", []))
    cur_rc_ids = set(GROUPS.get("rc_ids", []))
    rc_only_new = sorted(new_rc_ids - cur_rc_ids)
    rc_only_cur = sorted(cur_rc_ids - new_rc_ids)

    new_sw_ids = set(compat_cfg.get("groups", {}).get("switches_ids", []))
    cur_sw_ids = set(GROUPS.get("switches_ids", []))
    sw_only_new = sorted(new_sw_ids - cur_sw_ids)
    sw_only_cur = sorted(cur_sw_ids - new_sw_ids)

    new_sec_names = set(compat_sec.keys())
    cur_sec_names = set(RC_SECTIONS.keys())
    sec_only_new = sorted(new_sec_names - cur_sec_names)
    sec_only_cur = sorted(cur_sec_names - new_sec_names)

    shared_sec = new_sec_names & cur_sec_names
    sec_prevnext_mismatch = []
    for name in sorted(shared_sec):
        a = compat_sec[name]
        b = RC_SECTIONS[name]
        if (a.get("PrevSec") != b.get("PrevSec")) or (a.get("NextSec") != b.get("NextSec")):
            sec_prevnext_mismatch.append(
                {
                    "section": name,
                    "new_prev": a.get("PrevSec"),
                    "new_next": a.get("NextSec"),
                    "cur_prev": b.get("PrevSec"),
                    "cur_next": b.get("NextSec"),
                }
            )

    summary = {
        "counts": {
            "new_rc_ids": len(new_rc_ids),
            "cur_rc_ids": len(cur_rc_ids),
            "new_sw_ids": len(new_sw_ids),
            "cur_sw_ids": len(cur_sw_ids),
            "new_sections": len(new_sec_names),
            "cur_sections": len(cur_sec_names),
            "shared_sections": len(shared_sec),
        },
        "diff": {
            "rc_only_new": rc_only_new,
            "rc_only_current": rc_only_cur,
            "switch_only_new": sw_only_new,
            "switch_only_current": sw_only_cur,
            "section_only_new": sec_only_new,
            "section_only_current": sec_only_cur,
            "section_prev_next_mismatch_count": len(sec_prevnext_mismatch),
            "section_prev_next_mismatch_samples": sec_prevnext_mismatch[:10],
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

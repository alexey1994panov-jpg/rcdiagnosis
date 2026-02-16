from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_station_bundle import build_bundle
from validate_bundle_links import validate_bundle


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Build + validate station integration bundle locally.")
    parser.add_argument("--objects", type=Path, default=here.parent / "Objects.xml")
    parser.add_argument("--iosystem", type=Path, default=here.parent / "IOSystem.xml")
    parser.add_argument("--diagparams", type=Path, default=here.parent / "DiagParams.xml")
    parser.add_argument("--out-dir", type=Path, default=here / "output" / "visochino")
    args = parser.parse_args()

    build_bundle(args.objects, args.iosystem, args.diagparams, args.out_dir)
    report = validate_bundle(args.out_dir)

    report_path = args.out_dir / "validation_report.json"
    report_path.write_text(json.dumps(report.__dict__, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Build done: {args.out_dir}")
    print(f"Validation status: {report.status} (errors={report.errors_count}, warnings={report.warnings_count})")
    print(f"Report: {report_path}")
    if report.errors_count:
        raise SystemExit(2)


if __name__ == "__main__":
    main()


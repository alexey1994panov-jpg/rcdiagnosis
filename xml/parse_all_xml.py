from __future__ import annotations

import argparse
from pathlib import Path

from parse_iosystem_xml import main as parse_iosystem_main
from parse_objects_xml import main as parse_objects_main
from parse_station_xml import main as parse_station_main


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all local XML parsers in xml/.")
    parser.add_argument(
        "--skip-station",
        action="store_true",
        help="Skip Station.xml parsing if you only need Objects/IOSystem.",
    )
    args = parser.parse_args()

    # Use each parser's default paths inside this folder.
    parse_objects_main([])
    parse_iosystem_main([])
    if not args.skip_station:
        parse_station_main([])
    print(f"Done. Base dir: {Path(__file__).resolve().parent}")


if __name__ == "__main__":
    main()

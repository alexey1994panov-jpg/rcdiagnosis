# XML Local Parsers

All scripts and outputs are isolated inside `xml/`.

## Scripts

- `parse_objects_xml.py`:
  - Parses `Objects.xml`
  - Writes:
    - `parsed/objects/objects_all.json`
    - `parsed/objects/by_type_exact/*.json` (full type, e.g. `1000.2.1`)
    - `parsed/objects/by_type_family/*.json` (family, e.g. `1000.2`)
    - `parsed/objects/type_index.json`
    - `parsed/objects/type_family_index.json`
    - `parsed/objects/object_name_to_type.json`

- `parse_iosystem_xml.py`:
  - Parses `IOSystem.xml`
  - Writes:
    - `parsed/iosystem/iosystem_tree.json`
    - `parsed/iosystem/iosystem_modules_flat.json`
    - `parsed/iosystem/iosystem_summary.json`

- `parse_station_xml.py`:
  - Parses `Station.xml`
  - Writes:
    - `parsed/station/station_groups.json`
    - `parsed/station/station_go_flat.json`
    - `parsed/station/station_summary.json`

- `parse_all_xml.py`:
  - Runs all parsers with defaults.
  - Optional: `--skip-station`

## Usage

```powershell
python xml/parse_all_xml.py
python xml/parse_all_xml.py --skip-station
python xml/parse_objects_xml.py
python xml/parse_iosystem_xml.py
python xml/parse_station_xml.py
```

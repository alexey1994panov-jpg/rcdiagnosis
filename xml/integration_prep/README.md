# Station Integration Prep (isolated)

This folder prepares station JSON artifacts from XML without touching runtime code.

## Goals

- Keep parsing local and isolated from the main project.
- Extract station truth from XML (`Objects.xml`, `IOSystem.xml`, `DiagParams.xml`).
- Produce:
  - canonical model (portable between stations),
  - derived topology,
  - compatibility JSON shaped like current runtime expectations,
  - manual indicators file that is never overwritten.

## Run

```powershell
python xml/integration_prep/build_station_bundle.py
python xml/integration_prep/run_local_pipeline.py
```

Optional paths:

```powershell
python xml/integration_prep/build_station_bundle.py ^
  --objects xml/Objects.xml ^
  --iosystem xml/IOSystem.xml ^
  --diagparams xml/DiagParams.xml ^
  --out-dir xml/integration_prep/output/visochino
```

## Output

- `canonical/station_bundle.json`
- `derived/topology_rc_sections.json`
- `compat/station_config_like.json`
- `compat/station_rc_sections_like.json`
- `compat/station_route_sections_like.json`
- `config/diagparams_by_object_task.json`
- `config/project_detector_options.seed.json` (seed/template, manual mapping required)
- `config/indicators_auto.json` (all parsed indicators, including indicator-sections)
- `manual/indicators_manual.json` (created once, preserved on next runs)
- `manifest.json`
- `validation_report.json` (from `run_local_pipeline.py` or `validate_bundle_links.py`)

## Notes

- `Objects.xml` is treated as source-of-truth for object links and relations.
- `Station.xml` graphics are intentionally not used here yet (next stage).
- `project_detector_options.seed.json` is intentionally conservative:
  values come from extracted DiagParams where direct mapping is obvious;
  the rest is marked for manual mapping.

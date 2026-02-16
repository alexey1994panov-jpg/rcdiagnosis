# Integration Plan (no runtime changes yet)

## Current status

- Prepared station artifacts are generated in:
  - `xml/integration_prep/output/visochino/canonical`
  - `xml/integration_prep/output/visochino/derived`
  - `xml/integration_prep/output/visochino/compat`
  - `xml/integration_prep/output/visochino/config`
  - `xml/integration_prep/output/visochino/manual`

- Compatibility layer already exists as JSON:
  - `compat/station_config_like.json`
  - `compat/station_rc_sections_like.json`

This allows migration without changing detector logic first.

## Recommended migration strategy

1. Adapter-only stage (safe):
   - Add loader that reads `compat/*.json`.
   - Convert to current in-memory shape used by `tools.station.station_config` / `station_rc_sections`.
   - Keep current detector and topology code unchanged.
   - Switch via feature flag.

2. Compare stage:
   - Run old tests with both loaders (`legacy_xml_codegen` vs `compat_json_loader`).
   - Diff timeline fields:
     - open/active/close timestamps,
     - effective neighbors,
     - triggered flags/exceptions.

3. Canonical stage:
   - Move topology rebuild to `canonical/station_bundle.json` + `derived/topology_rc_sections.json`.
   - Keep compatibility adapter for old tests until parity is stable.

4. Multi-station stage:
   - Layout per station:
     - `xml/integration_prep/output/<station_id>/...`
   - Active station selected by config/env/UI.

## Important constraints from your requirements

- Source of truth for links and relations: `Objects.xml`.
- `DiagParams.xml` should become truth source for project detector timings/enables.
- Manual test indicators must be preserved on re-import:
  - `manual/indicators_manual.json` is never overwritten.
- First stage must not break existing tests.

## What still needs manual decision

- Exact mapping from `DiagParams` task param names (`NT0_min`, `NT1_min`, ...)
  to project option keys (`ts01_lz*`, `tlz_ls*`, `tkon_*`, ...).
- Variant enable policy by default per RC for each station
  (global defaults vs per-RC overrides).

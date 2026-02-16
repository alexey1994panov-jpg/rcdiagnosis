# Frontend Handoff v1

Last updated: 2026-02-11

This file defines the first stable contract for moving detector visualization to frontend.

## Data Source
Runtime output is produced by `SimulationContext.run()` in `tools/sim_core.py`.

### Single ctrl RC mode
`run()` returns `List[TimelineStep]`-compatible wrappers.

### Multi ctrl RC mode
`run()` returns `List[Dict[str, TimelineStep]]` where key = `ctrl_rc_id`.

## TimelineStep Contract
Fields used by frontend:

```ts
interface TimelineStepDTO {
  t: number;
  step_duration: number;
  ctrl_rc_id: string;
  effective_prev_rc: string | null;
  effective_next_rc: string | null;
  rc_states: Record<string, number>;
  switch_states: Record<string, number>;
  signal_states: Record<string, number>;
  modes: Record<string, unknown>;
  lz_state: boolean;
  lz_variant: number;
  flags: string[];
}
```

## Flag Semantics

### LZ
- active: `llz_v{N}`
- open event: `llz_v{N}_open`
- close event: `llz_v{N}_closed`

### LS
- active: `lls_{N}`
- open event: `lls_{N}_open`
- close event: `lls_{N}_closed`

### Common quality flags
- `false_lz`
- `no_lz_when_occupied`

## Frontend Mapping

### Status Card per ctrl RC
- Current state: `lz_state`
- Current variant: `lz_variant`
- Last events: from `flags` ending with `_open` / `_closed`

### Timeline Chart
- X axis: cumulative `t`
- Y axis: boolean lane per flag (`flags` contains value at step)
- Additional lanes:
  - `rc_states[ctrl_rc_id]`
  - `effective_prev_rc`, `effective_next_rc`

## Normalization Helper (Frontend)
For mixed output modes:

```ts
function normalizeRunOutput(raw: any): TimelineStepDTO[] {
  if (!Array.isArray(raw) || raw.length === 0) return [];

  // single RC wrappers behave like TimelineStep
  if (raw[0] && typeof raw[0].ctrl_rc_id === "string") {
    return raw as TimelineStepDTO[];
  }

  // multi RC: flatten dict per step
  const out: TimelineStepDTO[] = [];
  for (const frame of raw as Record<string, TimelineStepDTO>[]) {
    for (const rcId of Object.keys(frame)) out.push(frame[rcId]);
  }
  return out;
}
```

## Migration Plan
1. Build frontend DTO models and parser for `TimelineStepDTO`.
2. Add status-card and basic timeline page for one `ctrl_rc_id`.
3. Add multi-RC switcher (group by `ctrl_rc_id`).
4. Add mask-name tooltip using backend `mask_to_string` mapping export (next step).

## Next Backend Step for Frontend
Expose a small metadata endpoint/object with:
- variant labels
- flag labels
- mask id -> mask canonical name mapping

## Station Layout Contract (Implemented)
Endpoint:
- `GET /station-layout?station=Visochino`

DTO:
```ts
interface StationLayoutDTO {
  station: string;
  rails: { id: string; group_name: string; group_key: string; points: [number, number][] }[];
  switches: {
    id: string;
    switch_name: string;
    switch_key: string;
    x: number;
    y: number;
    plus: [number, number][];
    minus: [number, number][];
    section: [number, number][];
  }[];
  signals: {
    id: string;
    signal_name: string;
    signal_key: string;
    x: number;
    y: number;
    radius: number;
    orientation: number;
  }[];
  labels: { id: string; group_name: string; text: string; x: number; y: number; class: string }[];
  bounds: {
    min_x: number;
    min_y: number;
    max_x: number;
    max_y: number;
    width: number;
    height: number;
    padding: number;
  };
}
```

Frontend status:
- `frontend/static/timeline-scheme.js` now renders SVG from this endpoint instead of hardcoded RC/switch/signal coordinates.

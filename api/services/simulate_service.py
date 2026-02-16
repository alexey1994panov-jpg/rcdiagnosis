from __future__ import annotations

from typing import Any, Callable, Dict, List

from fastapi import HTTPException

from api.sim.schemas import ScenarioIn, TimelineStepOut
from tools.core.sim_core import ScenarioStep


def simulate_scenario(
    scenario: ScenarioIn,
    *,
    default_options: Dict[str, Any],
    canonicalize_options: Callable[[Dict[str, Any]], Dict[str, Any]],
    resolve_rc_id: Callable[[str], str | None],
    build_detectors_config: Callable[[str, Dict[str, Any]], Any],
    to_float: Callable[[Dict[str, Any], str, float], float],
    convert_rc_states: Callable[[Dict[str, int]], Dict[str, int]],
    convert_switch_states: Callable[[Dict[str, int]], Dict[str, int]],
    convert_signal_states: Callable[[Dict[str, int]], Dict[str, int]],
    run_simulation_contract: Callable[[Dict[str, Any]], Dict[str, Any]],
    parse_flag: Callable[[str, str | None], Dict[str, Any]],
    states_ids_to_names: Callable[[Dict[str, int], set[int]], Dict[str, int]],
    id_to_name: Dict[str, str],
) -> List[TimelineStepOut]:
    options = dict(default_options)
    options.update(scenario.options or {})
    options = canonicalize_options(options)

    seen: set[str] = set()
    for st in scenario.steps:
        for raw_rc in (st.rc_states or {}).keys():
            rc_id = resolve_rc_id(str(raw_rc))
            if rc_id and rc_id not in seen:
                seen.add(rc_id)
    target_ids = sorted(seen)
    if not target_ids:
        raise HTTPException(status_code=400, detail="No target RCs resolved from scenario")

    primary_ctrl_rc_id = target_ids[0]
    det_cfg = build_detectors_config(primary_ctrl_rc_id, options)
    t_pk = to_float(options, "t_pk", 30.0)

    steps_internal: List[ScenarioStep] = []
    for s in scenario.steps:
        auto_actions = {str(k).lower(): int(v) for k, v in (s.auto_actions or {}).items()}
        total_t = float(s.t)
        if total_t <= 0:
            raise HTTPException(status_code=400, detail="Each scenario step must have t > 0")
        rc_states = convert_rc_states(s.rc_states)
        sw_states = convert_switch_states(s.switch_states)
        sig_states = convert_signal_states(s.signal_states)
        indicator_states = {str(k): int(v) for k, v in (s.indicator_states or {}).items()}
        steps_internal.append(
            ScenarioStep(
                t=float(total_t),
                rc_states=dict(rc_states),
                switch_states=dict(sw_states),
                signal_states=dict(sig_states),
                modes=dict(s.modes or {}),
                mu=dict(s.mu or {}),
                dispatcher_control_state=s.dispatcher_control_state,
                auto_actions=dict(auto_actions),
                indicator_states=dict(indicator_states),
            )
        )

    if len(target_ids) == 1:
        contract_payload: Dict[str, Any] = {
            "t_pk": t_pk,
            "ctrl_rc_id": primary_ctrl_rc_id,
            "detectors_config": det_cfg.__dict__,
            "scenario": [
                {
                    "t": float(s.t),
                    "rc_states": dict(s.rc_states),
                    "switch_states": dict(s.switch_states),
                    "signal_states": dict(s.signal_states),
                    "modes": dict(s.modes or {}),
                }
                for s in steps_internal
            ],
        }
    else:
        contract_payload = {
            "t_pk": t_pk,
            "ctrl_rc_ids": target_ids,
            "detectors_configs": {rc_id: build_detectors_config(rc_id, options).__dict__ for rc_id in target_ids},
            "scenario": [
                {
                    "t": float(s.t),
                    "rc_states": dict(s.rc_states),
                    "switch_states": dict(s.switch_states),
                    "signal_states": dict(s.signal_states),
                    "modes": dict(s.modes or {}),
                }
                for s in steps_internal
            ],
        }

    contract_result = run_simulation_contract(contract_payload)
    frames = contract_result.get("frames", []) or []

    result: List[TimelineStepOut] = []
    for frame in frames:
        if not isinstance(frame, dict) or not frame:
            continue
        rows = list(frame.values())
        if not rows:
            continue
        row0 = rows[0]
        merged_rc: Dict[str, int] = {}
        merged_sw: Dict[str, int] = {}
        merged_sig: Dict[str, int] = {}
        merged_modes: Dict[str, Any] = {}
        topology_by_rc: Dict[str, Dict[str, str]] = {}
        lz_state_any = False
        variant_max = 0
        best_row = row0
        best_score = (-1, -1)
        flags_parsed: List[Dict[str, Any]] = []
        seen_flags: set = set()

        for r in rows:
            merged_rc.update(dict(r.get("rc_states", {}) or {}))
            merged_sw.update(dict(r.get("switch_states", {}) or {}))
            merged_sig.update(dict(r.get("signal_states", {}) or {}))
            merged_modes.update(dict(r.get("modes", {}) or {}))

            r_ctrl = str(r.get("ctrl_rc_id") or "")
            if r_ctrl:
                r_prev_raw = r.get("effective_prev_rc")
                r_next_raw = r.get("effective_next_rc")
                r_prev_name = id_to_name.get(str(r_prev_raw), str(r_prev_raw or ""))
                r_next_name = id_to_name.get(str(r_next_raw), str(r_next_raw or ""))
                topology_by_rc[r_ctrl] = {"prev": r_prev_name, "next": r_next_name}

            lz_state_any = lz_state_any or bool(r.get("lz_state", False))
            try:
                rv = int(r.get("lz_variant", 0) or 0)
                variant_max = max(variant_max, rv)
            except Exception:
                rv = 0
            has_neighbors = 1 if (r.get("effective_prev_rc") or r.get("effective_next_rc")) else 0
            score = (rv, has_neighbors)
            if score > best_score:
                best_score = score
                best_row = r
            ctrl_for_flag = r.get("ctrl_rc_id", primary_ctrl_rc_id)
            for f in [str(x) for x in (r.get("flags", []) or []) if x]:
                key = (ctrl_for_flag, f)
                if key in seen_flags:
                    continue
                seen_flags.add(key)
                flags_parsed.append(parse_flag(f, ctrl_for_flag))

        prev_raw = best_row.get("effective_prev_rc")
        next_raw = best_row.get("effective_next_rc")
        ctrl_raw = str(best_row.get("ctrl_rc_id") or row0.get("ctrl_rc_id") or primary_ctrl_rc_id)
        prev_name = id_to_name.get(str(prev_raw), str(prev_raw or ""))
        next_name = id_to_name.get(str(next_raw), str(next_raw or ""))
        result.append(
            TimelineStepOut(
                t=float(row0.get("t", 0.0)),
                step_duration=float(row0.get("step_duration", 0.0)),
                ctrl_rc_id=ctrl_raw,
                topology_by_rc=topology_by_rc,
                lz_state=lz_state_any,
                variant=variant_max,
                effective_prev_rc=prev_name,
                effective_next_rc=next_name,
                flags=flags_parsed,
                modes=merged_modes,
                rc_states=states_ids_to_names(merged_rc, {1}),
                switch_states=states_ids_to_names(merged_sw, {2}),
                signal_states=states_ids_to_names(merged_sig, {3, 4}),
                mu_state=row0.get("mu_state"),
                nas_state=row0.get("nas_state"),
                chas_state=row0.get("chas_state"),
                dsp_state=row0.get("dsp_state"),
            )
        )
    return result

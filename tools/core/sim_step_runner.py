from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from core.detectors_engine import DetectorsState, update_detectors
from core.flags_engine import build_flags_simple
from core.sim_types import ScenarioStep, TimelineStep

if TYPE_CHECKING:
    from core.sim_core import SimulationContext


def step_single_rc(
    ctx: "SimulationContext",
    ctrl_rc_id: str,
    step: ScenarioStep,
    dt: float,
    exception_context: Optional[Dict[str, bool]] = None,
    step_override: Optional[ScenarioStep] = None,
) -> TimelineStep:
    """
    Подшаговая обработка одной контролируемой РЦ.
    Вынесено из SimulationContext для декомпозиции sim_core.py.
    """
    from core.detectors_engine import DetectorsResult, _ensure_rc_states_by_id

    active_step = step_override if step_override is not None else step
    rc_states_by_id = _ensure_rc_states_by_id(ctx.rc_states)

    remaining = float(dt)
    elapsed = 0.0
    event_time: Optional[float] = None

    effective_prev_rc: Optional[str] = None
    effective_next_rc: Optional[str] = None
    modes_for_detectors: Dict[str, Any] = dict(active_step.modes)
    merged_flags: List[str] = []
    last_lz_state = False
    last_lz_variant = 0

    while remaining > 0.0:
        change_dt = ctx.topology.get_next_topology_change_dt(
            rc_id=ctrl_rc_id,
            switch_states=ctx.switch_states,
            max_dt=remaining,
        )
        chunk_dt = remaining if not change_dt else min(remaining, float(change_dt))
        if chunk_dt <= 0.0:
            break

        effective_prev_rc, effective_next_rc, prev_ok, next_ok, prev_nc, next_nc = ctx._compute_effective_neighbors_with_control(
            ctrl_rc_id, chunk_dt
        )

        topology_info = {
            "ctrl_rc_id": ctrl_rc_id,
            "effective_prev_rc": effective_prev_rc,
            "effective_next_rc": effective_next_rc,
        }

        modes_for_detectors = dict(active_step.modes)
        modes_for_detectors["prev_control_ok"] = prev_ok
        modes_for_detectors["next_control_ok"] = next_ok
        modes_for_detectors["prev_nc"] = prev_nc
        modes_for_detectors["next_nc"] = next_nc
        modes_for_detectors.update(
            ctx._compute_dynamic_signal_modes(
                ctrl_rc_id=ctrl_rc_id,
                effective_prev_rc=effective_prev_rc,
                effective_next_rc=effective_next_rc,
            )
        )
        if exception_context:
            modes_for_detectors.update(exception_context)

        det_state = ctx.detectors_states.get(ctrl_rc_id)
        if det_state:
            new_det_state, det_result = update_detectors(
                det_state=det_state,
                station_model=ctx.model,
                t=ctx.time + elapsed,
                dt=chunk_dt,
                rc_states=rc_states_by_id,
                switch_states=ctx.switch_states,
                signal_states=ctx.signal_states,
                topology_info=topology_info,
                cfg=ctx.config.detectors_configs[ctrl_rc_id],
                modes=modes_for_detectors,
            )
            ctx.detectors_states[ctrl_rc_id] = new_det_state
        else:
            det_result = DetectorsResult()
            new_det_state = DetectorsState()

        flags_res = build_flags_simple(
            ctrl_rc_id=ctrl_rc_id,
            det_state=new_det_state,
            det_result=det_result,
            rc_states=rc_states_by_id,
            switch_states=ctx.switch_states,
        )
        last_lz_state = flags_res.lz
        last_lz_variant = flags_res.variant
        for f in flags_res.flags:
            if f not in merged_flags:
                merged_flags.append(f)

        if event_time is None:
            if det_result.opened:
                off = float(det_result.open_offset or 0.0)
                event_time = float(ctx.time) + elapsed + off
            elif det_result.closed:
                off = float(det_result.close_offset or 0.0)
                event_time = float(ctx.time) + elapsed + off

        elapsed += chunk_dt
        remaining -= chunk_dt

    timeline_t = event_time if event_time is not None else float(ctx.time)

    return TimelineStep(
        t=timeline_t,
        step_duration=dt,
        ctrl_rc_id=ctrl_rc_id,
        effective_prev_rc=effective_prev_rc,
        effective_next_rc=effective_next_rc,
        rc_states=dict(ctx.rc_states),
        switch_states=dict(ctx.switch_states),
        signal_states=dict(ctx.signal_states),
        modes=dict(modes_for_detectors),
        lz_state=last_lz_state,
        lz_variant=last_lz_variant,
        flags=list(merged_flags),
        mu_state=int(step.mu.get(ctrl_rc_id, 0)) if step.mu else None,
        nas_state=int(active_step.auto_actions.get("nas")) if "nas" in (active_step.auto_actions or {}) else None,
        chas_state=int(active_step.auto_actions.get("chas")) if "chas" in (active_step.auto_actions or {}) else None,
        dsp_state=int(active_step.dispatcher_control_state)
        if active_step.dispatcher_control_state is not None
        else int(active_step.modes.get("dispatcher_control_state"))
        if "dispatcher_control_state" in active_step.modes
        else None,
    )

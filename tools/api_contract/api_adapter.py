from typing import Any, Dict, List, Tuple

from api_contract.api_schema import TimelineStepDTO


def timeline_step_to_dto(step: Any) -> TimelineStepDTO:
    """Convert TimelineStep-like object to TimelineStepDTO."""
    return TimelineStepDTO(
        t=float(step.t),
        step_duration=float(step.step_duration),
        ctrl_rc_id=str(step.ctrl_rc_id),
        effective_prev_rc=step.effective_prev_rc,
        effective_next_rc=step.effective_next_rc,
        rc_states=dict(step.rc_states),
        switch_states=dict(step.switch_states),
        signal_states=dict(step.signal_states),
        modes=dict(step.modes),
        lz_state=bool(step.lz_state),
        lz_variant=int(step.lz_variant),
        flags=list(step.flags),
    )


def normalize_run_output(raw: Any) -> Tuple[List[Dict[str, TimelineStepDTO]], List[TimelineStepDTO], str, List[str]]:
    """
    Normalize SimulationContext.run() output to a stable API shape.

    Returns:
    - frames: list of dict[ctrl_rc_id, TimelineStepDTO]
    - timeline: flattened list of TimelineStepDTO
    - mode: "single" or "multi"
    - ctrl_rc_ids: ordered unique ids from frames
    """
    frames: List[Dict[str, TimelineStepDTO]] = []
    flat: List[TimelineStepDTO] = []

    if not isinstance(raw, list) or not raw:
        return frames, flat, "single", []

    # Single-RC wrappers: have direct TimelineStep-like attrs and also dict behavior.
    first = raw[0]
    if hasattr(first, "ctrl_rc_id"):
        mode = "single"
        ctrl_rc_ids = []
        for step in raw:
            dto = timeline_step_to_dto(step)
            frames.append({dto.ctrl_rc_id: dto})
            flat.append(dto)
            if dto.ctrl_rc_id not in ctrl_rc_ids:
                ctrl_rc_ids.append(dto.ctrl_rc_id)
        return frames, flat, mode, ctrl_rc_ids

    # Multi-RC path: list[dict[str, TimelineStep-like]]
    mode = "multi"
    ctrl_rc_ids: List[str] = []
    for frame in raw:
        dto_frame: Dict[str, TimelineStepDTO] = {}
        for rc_id, step in frame.items():
            dto = timeline_step_to_dto(step)
            dto_frame[str(rc_id)] = dto
            flat.append(dto)
            if str(rc_id) not in ctrl_rc_ids:
                ctrl_rc_ids.append(str(rc_id))
        frames.append(dto_frame)

    return frames, flat, mode, ctrl_rc_ids



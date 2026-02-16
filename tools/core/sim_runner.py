from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Union

from core.sim_result import SingleResultWrapper
from core.sim_types import ScenarioStep, TimelineStep
from exceptions.exceptions_engine import apply_exceptions, make_exceptions_config

if TYPE_CHECKING:
    from core.sim_core import SimulationContext


def run_context(ctx: "SimulationContext") -> Union[List[TimelineStep], List[Dict[str, TimelineStep]]]:
    """
    Прогон сценария для SimulationContext.
    Вынесено из sim_core.py для упрощения чтения и сопровождения.
    """
    timeline: List[Dict[str, TimelineStep]] = []
    scenario_history: List[ScenarioStep] = []
    timeline_by_rc: Dict[str, List[TimelineStep]] = {rc_id: [] for rc_id in ctx.ctrl_rc_ids}

    if not ctx.scenario_steps:
        return timeline

    for step in ctx.scenario_steps:
        scenario_history.append(step)
        step_results = ctx.step(step)
        if isinstance(step_results, SingleResultWrapper):
            step_dict = dict(step_results._dict)
        else:
            step_dict = dict(step_results)

        processed: Dict[str, TimelineStep] = {}
        for rc_id, current in step_dict.items():
            det_cfg = ctx.config.detectors_configs.get(rc_id)
            exc_cfg = make_exceptions_config(det_cfg)
            current = apply_exceptions(
                ctrl_rc_id=rc_id,
                current=current,
                scenario_history=scenario_history,
                timeline_history=timeline_by_rc.get(rc_id, []),
                cfg=exc_cfg,
            )
            timeline_by_rc.setdefault(rc_id, []).append(current)
            processed[rc_id] = current

        timeline.append(processed)

    if len(ctx.ctrl_rc_ids) == 1:
        single_rc_id = ctx.ctrl_rc_ids[0]
        return [SingleResultWrapper(t[single_rc_id], t) for t in timeline]

    return timeline

from typing import Any, Dict, List

from api_contract.api_adapter import normalize_run_output
from api_contract.api_metadata import get_metadata_dto
from api_contract.api_schema import RunRequestDTO, RunResponseDTO, dto_to_dict
from core.detectors_engine import DetectorsConfig
from core.sim_core import ScenarioStep, SimulationConfig, SimulationContext


def _build_detectors_config(data: Dict[str, Any]) -> DetectorsConfig:
    return DetectorsConfig(**data)


def _build_scenario(steps: List[Dict[str, Any]]) -> List[ScenarioStep]:
    return [
        ScenarioStep(
            t=float(step["t"]),
            rc_states=dict(step.get("rc_states", {})),
            switch_states=dict(step.get("switch_states", {})),
            signal_states=dict(step.get("signal_states", {})),
            modes=dict(step.get("modes", {})),
        )
        for step in steps
    ]


def run_simulation(payload: Dict[str, Any]) -> Dict[str, Any]:
    req = RunRequestDTO(**payload)
    scenario = _build_scenario(req.scenario)

    if req.detectors_configs:
        configs = {rc_id: _build_detectors_config(cfg) for rc_id, cfg in req.detectors_configs.items()}
        sim_cfg = SimulationConfig(t_pk=float(req.t_pk), detectors_configs=configs)
        ctx = SimulationContext(
            config=sim_cfg,
            scenario=scenario,
            ctrl_rc_ids=req.ctrl_rc_ids,
        )
    else:
        if req.detectors_config is None:
            raise ValueError("Either detectors_config or detectors_configs must be provided")
        det_cfg = _build_detectors_config(req.detectors_config)
        sim_cfg = SimulationConfig(t_pk=float(req.t_pk), detectors_config=det_cfg)
        ctx = SimulationContext(
            config=sim_cfg,
            scenario=scenario,
            ctrl_rc_id=req.ctrl_rc_id or det_cfg.ctrl_rc_id,
        )

    raw = ctx.run()
    frames, timeline, mode, ctrl_rc_ids = normalize_run_output(raw)
    resp = RunResponseDTO(mode=mode, ctrl_rc_ids=ctrl_rc_ids, timeline=timeline, frames=frames)
    return dto_to_dict(resp)


def get_metadata() -> Dict[str, Any]:
    return dto_to_dict(get_metadata_dto())



# detectors_engine.py

from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional

from base_detector import BaseDetector
from variant1_lz_factory import make_lz1_detector
from variant2_lz_factory import make_lz2_detector
from variant3_lz_factory import make_lz3_detector


@dataclass
class DetectorsConfig:
    ctrl_rc_id: str
    prev_rc_name: str
    ctrl_rc_name: str
    next_rc_name: Optional[str]
   # v1
    ts01_lz1: float
    tlz_lz1: float
    tkon_lz1: float
    

    # v2
    ts01_lz2: float
    ts02_lz2: float
    tlz_lz2: float
    tkon_lz2: float
    # v3
    ts01_lz3: float  # T_S0103
    tlz_lz3: float   # T_LZ03
    ts02_lz3: float  # T_S0203
    tkon_lz3: float 

    enable_lz1: bool = True
    enable_lz2: bool = False
    enable_lz3: bool = False


@dataclass
class DetectorsState:
    v1_detector: Optional[BaseDetector] = None
    v1_active: bool = False
    v1_prev_lz: bool = False
    v2_detector: Optional[BaseDetector] = None
    v2_active: bool = False
    v3_detector: Optional[BaseDetector] = None
    v3_active: bool = False


@dataclass
class DetectorsResult:
    opened_v1: bool = False
    closed_v1: bool = False
    opened_v2: bool = False
    closed_v2: bool = False
    opened_v3: bool = False
    closed_v3: bool = False


def init_detectors_engine(
    cfg: DetectorsConfig,
    rc_ids: list[str],
) -> DetectorsState:
    _ = rc_ids

    # v1
    v1 = None
    if cfg.enable_lz1:
        v1 = make_lz1_detector(
            prev_rc_name=cfg.prev_rc_name,
            ctrl_rc_name=cfg.ctrl_rc_name,
            next_rc_name=cfg.next_rc_name or "",
            ts01_lz1=cfg.ts01_lz1,
            tlz_lz1=cfg.tlz_lz1,
            tkon_lz1=cfg.tkon_lz1,
        )

    # v2 — пока не реализован поверх нового BaseDetector,
    # поэтому оставляем None или делаем отдельную фабрику позже.
     # v2
    v2 = None
    if cfg.enable_lz2:
        v2 = make_lz2_detector(
            prev_rc_name=cfg.prev_rc_name,
            ctrl_rc_name=cfg.ctrl_rc_name,
            next_rc_name=cfg.next_rc_name or "",
            ts01_lz2=cfg.ts01_lz2,
            ts02_lz2=cfg.ts02_lz2,
            tlz_lz2=cfg.tlz_lz2,
            tkon_lz2=cfg.tkon_lz2,
        )

    # В init_detectors_engine
    v3 = None
    if cfg.enable_lz3:
            v3 = make_lz3_detector(
                prev_rc_name=cfg.prev_rc_name,
                ctrl_rc_name=cfg.ctrl_rc_name,
                next_rc_name=cfg.next_rc_name or "",
                ts01_lz3=cfg.ts01_lz3,
                tlz_lz3=cfg.tlz_lz3,
                ts02_lz3=cfg.ts02_lz3,
                tkon_lz3=cfg.tkon_lz3,
            )

    return DetectorsState(
        v1_detector=v1,
        v1_active=False,
        v1_prev_lz=False,
        v2_detector=v2,
        v2_active=False,
        v3_detector=v3,
        v3_active=False,
    )

class _StepAdapter:
    def __init__(self, rc_states: Dict[str, int], modes: Dict[str, Any]) -> None:
        self.rc_states = rc_states
        self.modes = modes


def update_detectors(
    det_state: DetectorsState,
    t: float,
    dt: float,
    rc_states: Dict[str, int],
    switch_states: Dict[str, int],
    signal_states: Dict[str, int],
    topology_info: Dict[str, Any],
    cfg: DetectorsConfig,
    modes: Dict[str, Any],
) -> Tuple[DetectorsState, DetectorsResult]:
    _ = t, switch_states, signal_states, topology_info, cfg

    step = _StepAdapter(rc_states=rc_states, modes=modes)

    opened_v1, closed_v1 = False, False
    if det_state.v1_detector:
        prev_lz_v1 = det_state.v1_active
        opened_v1, closed_v1 = det_state.v1_detector.update(step, dt)
        det_state.v1_prev_lz = prev_lz_v1
        det_state.v1_active = det_state.v1_detector.active

    opened_v2, closed_v2 = False, False
    if det_state.v2_detector:
        prev_lz_v2 = det_state.v2_active
        opened_v2, closed_v2 = det_state.v2_detector.update(step, dt)
        det_state.v2_active = det_state.v2_detector.active

    
    opened_v3, closed_v3 = False, False
    if det_state.v3_detector:
        prev_lz_v3 = det_state.v3_active
        opened_v3, closed_v3 = det_state.v3_detector.update(step, dt)
        det_state.v3_active = det_state.v3_detector.active



    return det_state, DetectorsResult(
        opened_v1=opened_v1,
        closed_v1=closed_v1,
        opened_v2=opened_v2,
        closed_v2=closed_v2,
        opened_v3=opened_v3,
        closed_v3=closed_v3,
    )

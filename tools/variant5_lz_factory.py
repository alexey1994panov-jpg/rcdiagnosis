from typing import Any, Optional
from base_detector import (
    BaseDetector, 
    PhaseConfig, 
    DetectorConfig, 
    CompletionMode, 
    NeighborRequirement
)
from variants_common import mask_1_not_locked, mask_0_not_locked

# ID масок
MASK_0_NOT_LOCKED = 500
MASK_1_NOT_LOCKED = 501

def make_lz5_detector(ctrl_rc_name: str, ts01_lz5: float,  tlz_lz5: float, tkon_lz5: float) -> BaseDetector:
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz5),
            next_phase_id=1,
            mask_fn=mask_0_not_locked,
            requires_neighbors=NeighborRequirement.ONLY_CTRL
        ),
        PhaseConfig(
            phase_id=1,
            duration=float( tlz_lz5),
            next_phase_id=-1, # ИСПРАВЛЕНО: -1 для активации детектора
            mask_fn=mask_1_not_locked,
            requires_neighbors=NeighborRequirement.ONLY_CTRL
        )
    ]

    # ИСПРАВЛЕНО: передаем phases в DetectorConfig
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        completion_mode=CompletionMode.FREE_TIME,
        t_kon=float(tkon_lz5),
        variant_name="V5"
    )

    # ИСПРАВЛЕНО: сигнатура __init__(config, condition_fn, completion_state_fn, prev, ctrl, next)
    return BaseDetector(
        config=config,
        prev_rc_name=None,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=None
    )
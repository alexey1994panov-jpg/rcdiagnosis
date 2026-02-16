from typing import Any, Optional
from core.base_detector import (
    BaseDetector, 
    PhaseConfig, 
    DetectorConfig, 
    CompletionMode, 
    NeighborRequirement
)
from core.variants_common import mask_rc_1nl, mask_rc_0nl

# ID РјР°СЃРѕРє
MASK_0_NOT_LOCKED = 17
MASK_1_NOT_LOCKED = 18

def make_lz5_detector(ctrl_rc_name: str, ts01_lz5: float,  tlz_lz5: float, tkon_lz5: float) -> BaseDetector:
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz5),
            next_phase_id=1,
            mask_id=MASK_0_NOT_LOCKED,
            mask_fn=mask_rc_0nl,
            requires_neighbors=NeighborRequirement.ONLY_CTRL
        ),
        PhaseConfig(
            phase_id=1,
            duration=float( tlz_lz5),
            next_phase_id=-1, # РРЎРџР РђР’Р›Р•РќРћ: -1 РґР»СЏ Р°РєС‚РёРІР°С†РёРё РґРµС‚РµРєС‚РѕСЂР°
            mask_id=MASK_1_NOT_LOCKED,
            mask_fn=mask_rc_1nl,
            requires_neighbors=NeighborRequirement.ONLY_CTRL
        )
    ]

    # РРЎРџР РђР’Р›Р•РќРћ: РїРµСЂРµРґР°РµРј phases РІ DetectorConfig
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        completion_mode=CompletionMode.FREE_TIME,
        t_kon=float(tkon_lz5),
        variant_name="V5"
    )

    # РРЎРџР РђР’Р›Р•РќРћ: СЃРёРіРЅР°С‚СѓСЂР° __init__(config, condition_fn, completion_state_fn, prev, ctrl, next)
    return BaseDetector(
        config=config,
        prev_rc_name=None,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=None
    )


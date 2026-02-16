from typing import Any, Optional, Tuple

from core.base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from core.base_wrapper import BaseVariantWrapper  # в†ђ РќРћР’Р«Р™ РРњРџРћР Рў
from core.variants_common import (
    mask_x0x, mask_x0x_occ,
    mask_00x, mask_00x_occ,
    mask_x00, mask_x00_occ,
)

# ID РјР°СЃРєРё
MASK_X0X = 9
MASK_X0X_OCC = 10
MASK_00X = 11
MASK_00X_OCC = 12
MASK_X00 = 13
MASK_X00_OCC = 14


def _make_branch_detector(
    mask_0_id: int,
    mask_0_fn: callable,
    mask_1_id: int,
    mask_1_fn: callable,
    ts01_lz7: float,
    tlz_lz7: float,
    tkon_lz7: float,
) -> BaseDetector:
    """РЈРЅРёРІРµСЂСЃР°Р»СЊРЅР°СЏ С„Р°Р±СЂРёРєР° РѕРґРЅРѕР№ РІРµС‚РєРё v7."""
    
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz7),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=mask_0_id,
            mask_fn=mask_0_fn,
            requires_neighbors=NeighborRequirement.NONE,
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_lz7),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=mask_1_id,
            mask_fn=mask_1_fn,
            requires_neighbors=NeighborRequirement.NONE,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz7),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="v7_branch",
    )
    
    return BaseDetector(config=config)


def make_lz7_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_lz7: float,
    tlz_lz7: float,
    tkon_lz7: float,
) -> BaseVariantWrapper:  # в†ђ РњР•РќРЇР•Рњ РўРРџ Р’РћР—Р’Р РђРўРђ
    
    # РЎРѕР·РґР°С‘Рј С‚СЂРё РІРµС‚РєРё РґР»СЏ СЂР°Р·РЅС‹С… С‚РѕРїРѕР»РѕРіРёР№
    det_no_adjacent = _make_branch_detector(
        MASK_X0X, mask_x0x,
        MASK_X0X_OCC, mask_x0x_occ,
        ts01_lz7, tlz_lz7, tkon_lz7,
    )
    
    det_no_prev = _make_branch_detector(
        MASK_00X, mask_00x,
        MASK_00X_OCC, mask_00x_occ,
        ts01_lz7, tlz_lz7, tkon_lz7,
    )
    
    det_no_next = _make_branch_detector(
        MASK_X00, mask_x00,
        MASK_X00_OCC, mask_x00_occ,
        ts01_lz7, tlz_lz7, tkon_lz7,
    )
    
    # в†ђ РќРћР’РћР•: РІРѕР·РІСЂР°С‰Р°РµРј BaseVariantWrapper
    return BaseVariantWrapper([det_no_adjacent, det_no_prev, det_no_next])

# =========================================================================
# Р­РљРЎРџРћР Рў РЎРҐР•РњР«
# =========================================================================

V7_SCHEMA = {
    "variant_id": 7,
    "variant_name": "lz7",
    "description": "Р‘РµСЃСЃС‚СЂРµР»РѕС‡РЅР°СЏ Р Р¦: РЅРµС‚ СЃРјРµР¶РЅС‹С… / РЅРµС‚ prev / РЅРµС‚ next",
    "branches": [
        {
            "branch_name": "no_adjacent",
            "phases": [
                {"mask": "X0X", "mask_id": MASK_X0X},
                {"mask": "X0X_OCC", "mask_id": MASK_X0X_OCC},
            ],
        },
        {
            "branch_name": "no_prev",
            "phases": [
                {"mask": "00X", "mask_id": MASK_00X},
                {"mask": "00X_OCC", "mask_id": MASK_00X_OCC},
            ],
        },
        {
            "branch_name": "no_next",
            "phases": [
                {"mask": "X00", "mask_id": MASK_X00},
                {"mask": "X00_OCC", "mask_id": MASK_X00_OCC},
            ],
        },
    ],
    "completion": {"mode": "FREE_TIME"},
    "parameters": ["ts01_lz7", "tlz_lz7", "tkon_lz7"],
    "topology": "dynamic",
}


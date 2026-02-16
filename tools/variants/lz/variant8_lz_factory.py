# -*- coding: utf-8 -*-
# variant8_lz_factory.py вЂ” Р Р•Р¤РђРљРўРћР РРќР“: РґРµРєР»Р°СЂР°С‚РёРІРЅС‹Р№ СЃС‚РёР»СЊ, РіРѕС‚РѕРІ Рє РїРµСЂРµРЅРѕСЃСѓ РЅР° C

from typing import Any, Optional, Tuple

from core.base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from core.base_wrapper import BaseVariantWrapper  # в†ђ РќРћР’Р«Р™ РРњРџРћР Рў
from core.variants_common import (
    mask_010,                    # 0-1-0: С…РІРѕСЃС‚ РІСЃРµС… РІРµС‚РѕРє, Рё p1 Р’8.3
    mask_011,                    # 0-1-1: p2 Р’8.3
    mask_110_or_111,             # Р’8.1 p1
    mask_011_or_111,             # Р’8.1 p2, Р’8.2 p1
    mask_01x_or_x10,             # Р’8.2 p2
)

# ID РјР°СЃРѕРє РґР»СЏ РѕС‚Р»Р°РґРєРё
MASK_010 = 2
MASK_011 = 8
MASK_110_or_111 = 102
MASK_011_or_111 = 103
MASK_01x_or_x10 = 104


def _make_branch_detector(
    p0_mask_id: int,
    p0_mask_fn: callable,
    p1_mask_id: int,
    p1_mask_fn: callable,
    p2_mask_id: int,
    p2_mask_fn: callable,
    ts01_lz8: float,
    ts02_lz8: float,
    tlz_lz8: float,
    tkon_lz8: float,
) -> BaseDetector:
    """РЈРЅРёРІРµСЂСЃР°Р»СЊРЅР°СЏ С„Р°Р±СЂРёРєР° РѕРґРЅРѕР№ РІРµС‚РєРё v8."""
    
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz8),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=p0_mask_id,
            mask_fn=p0_mask_fn,
            requires_neighbors=NeighborRequirement.BOTH,
            abort_exception_keys=("exc_lz_dsp_timeout",),
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(ts02_lz8),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=p1_mask_id,
            mask_fn=p1_mask_fn,
            requires_neighbors=NeighborRequirement.BOTH,
            abort_exception_keys=("exc_lz_dsp_timeout",),
        ),
        PhaseConfig(
            phase_id=2,
            duration=float(tlz_lz8),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=p2_mask_id,
            mask_fn=p2_mask_fn,
            requires_neighbors=NeighborRequirement.BOTH,
            abort_exception_keys=("exc_lz_dsp_timeout",),
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz8),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="v8_branch",
    )
    
    return BaseDetector(config=config)


def make_lz8_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_lz8: float,
    ts02_lz8: float,
    tlz_lz8: float,
    tkon_lz8: float,
) -> BaseVariantWrapper:  # в†ђ РњР•РќРЇР•Рњ РўРРџ Р’РћР—Р’Р РђРўРђ
    
    # РЎРѕР·РґР°С‘Рј С‚СЂРё РІРµС‚РєРё v8
    det_prev = _make_branch_detector(
        MASK_110_or_111, mask_110_or_111,
        MASK_011_or_111, mask_011_or_111,
        MASK_010, mask_010,
        ts01_lz8, ts02_lz8, tlz_lz8, tkon_lz8,
    )
    
    det_next = _make_branch_detector(
        MASK_011_or_111, mask_011_or_111,
        MASK_01x_or_x10, mask_01x_or_x10,
        MASK_010, mask_010,
        ts01_lz8, ts02_lz8, tlz_lz8, tkon_lz8,
    )
    
    det_mid = _make_branch_detector(
        MASK_010, mask_010,
        MASK_011, mask_011,
        MASK_010, mask_010,
        ts01_lz8, ts02_lz8, tlz_lz8, tkon_lz8,
    )
    
    # в†ђ РќРћР’РћР•: РІРѕР·РІСЂР°С‰Р°РµРј BaseVariantWrapper
    return BaseVariantWrapper([det_prev, det_next, det_mid])


# РЎРҐР•РњР« (Р±РµР· РёР·РјРµРЅРµРЅРёР№)
V8_SCHEMA_PREV_BRANCH = {
    "branch_name": "prev",
    "description": "РџСЂРµРґС‹РґСѓС‰Р°СЏ Р·Р°РЅСЏС‚Р° (Р’8.1)",
    "phases": [
        {"phase_id": 0, "mask": "110|111", "mask_id": MASK_110_or_111, "name": "p1"},
        {"phase_id": 1, "mask": "011|111", "mask_id": MASK_011_or_111, "name": "p2"},
        {"phase_id": 2, "mask": "010", "mask_id": MASK_010, "name": "p3"},
    ],
}

V8_SCHEMA_NEXT_BRANCH = {
    "branch_name": "next",
    "description": "РЎР»РµРґСѓСЋС‰Р°СЏ Р·Р°РЅСЏС‚Р° (Р’8.2)",
    "phases": [
        {"phase_id": 0, "mask": "011|111", "mask_id": MASK_011_or_111, "name": "p1"},
        {"phase_id": 1, "mask": "01x|x10", "mask_id": MASK_01x_or_x10, "name": "p2"},
        {"phase_id": 2, "mask": "010", "mask_id": MASK_010, "name": "p3"},
    ],
}

V8_SCHEMA_MID_BRANCH = {
    "branch_name": "mid",
    "description": "РЎСЂРµРґРЅРёР№ РІР°СЂРёР°РЅС‚ (Р’8.3)",
    "phases": [
        {"phase_id": 0, "mask": "010", "mask_id": MASK_010, "name": "p1"},
        {"phase_id": 1, "mask": "011", "mask_id": MASK_011, "name": "p2"},
        {"phase_id": 2, "mask": "010", "mask_id": MASK_010, "name": "p3"},
    ],
}

V8_SCHEMA = {
    "variant_id": 8,
    "variant_name": "lz8",
    "description": "РўСЂРё РІРµС‚РєРё: РїСЂРµРґС‹РґСѓС‰Р°СЏ Р·Р°РЅСЏС‚Р°, СЃР»РµРґСѓСЋС‰Р°СЏ Р·Р°РЅСЏС‚Р°, СЃСЂРµРґРЅРёР№",
    "branches": [V8_SCHEMA_PREV_BRANCH, V8_SCHEMA_NEXT_BRANCH, V8_SCHEMA_MID_BRANCH],
    "completion": {"mode": "FREE_TIME"},
    "parameters": ["ts01_lz8", "ts02_lz8", "tlz_lz8", "tkon_lz8"],
    "features": ["requires_seen_full_adj"],
    "topology": "dynamic",
}



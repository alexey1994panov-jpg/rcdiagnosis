# -*- coding: utf-8 -*-
"""
Р¤Р°Р±СЂРёРєР° РґР»СЏ РІР°СЂРёР°РЅС‚Р° LS2 (РђСЃРёРјРјРµС‚СЂРёС‡РЅР°СЏ Р»РѕР¶РЅР°СЏ СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ)

РћРїРёСЃР°РЅРёРµ:
    LS2 РґРµС‚РµРєС‚РёСЂСѓРµС‚ Р»РѕР¶РЅСѓСЋ СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ РїРѕ РґРІСѓРј РЅРµР·Р°РІРёСЃРёРјС‹Рј РІРµС‚РєР°Рј:
    - Р’РµС‚РєР° 1 (Prev): 110 в†’ 100 в†’ 110
    - Р’РµС‚РєР° 2 (Next): 011 в†’ 001 в†’ 011
    
Р¤Р°Р·С‹ (РґР»СЏ РєР°Р¶РґРѕР№ РІРµС‚РєРё):
    0: (prev-ctrl Р·Р°РЅСЏС‚С‹) в†’ ts01_ls2
    1: (ctrl РѕСЃРІРѕР±РѕРґРёР»Р°СЃСЊ) в†’ tlz_ls2
    2: (ctrl СЃРЅРѕРІР° Р·Р°РЅСЏС‚Р°) в†’ ts02_ls2 в†’ РѕС‚РєСЂС‹С‚РёРµ Р›РЎ
    
Р—Р°РІРµСЂС€РµРЅРёРµ:
    РІСЃРµ СЃРІРѕР±РѕРґРЅС‹ в‰Ґ tkon_ls2 в†’ Р·Р°РєСЂС‹С‚РёРµ
"""

from typing import Any, Optional
from core.base_detector import (
    BaseDetector,
    PhaseConfig,
    DetectorConfig,
    CompletionMode,
    NeighborRequirement,
)
from core.base_wrapper import BaseVariantWrapper
from core.variants_common import mask_110, mask_100, mask_011, mask_001

# ID РјР°СЃРѕРє РґР»СЏ LS2
MASK_RC_110 = 6
MASK_RC_100 = 5
MASK_RC_011 = 8
MASK_RC_001 = 7


def _make_branch_detector(
    ctrl_rc_name: str,
    neighbor_rc_name: Optional[str],
    m0_id: int, m0_fn: Any,
    m1_id: int, m1_fn: Any,
    m2_id: int, m2_fn: Any,
    ts01: float,
    tlz: float,
    ts02: float,
    tkon: float,
    prev_name: Optional[str],
    next_name: Optional[str],
) -> BaseDetector:
    """РЎРѕР·РґР°РµС‚ РѕРґРЅСѓ РІРµС‚РєСѓ РґРµС‚РµРєС‚РѕСЂР° LS2."""
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=ts01,
            next_phase_id=1,
            mask_id=m0_id,
            mask_fn=m0_fn,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=1,
            duration=tlz,
            next_phase_id=2,
            mask_id=m1_id,
            mask_fn=m1_fn,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=2,
            duration=ts02,
            next_phase_id=-1,
            mask_id=m2_id,
            mask_fn=m2_fn,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=tkon,
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="ls2_branch",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=prev_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_name,
    )


def make_ls2_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_ls2: float,
    tlz_ls2: float,
    ts02_ls2: float,
    tkon_ls2: float,
) -> BaseVariantWrapper:
    """РЎРѕР·РґР°РµС‚ РґРµС‚РµРєС‚РѕСЂ LS2 (РђСЃРёРјРјРµС‚СЂРёС‡РЅР°СЏ Р»РѕР¶РЅР°СЏ СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ) СЃ РґРІСѓРјСЏ РІРµС‚РєР°РјРё."""
    detectors = []
    
    # Р’РµС‚РєР° Prev (110 в†’ 100 в†’ 110)
    if prev_rc_name:
        det_prev = _make_branch_detector(
            ctrl_rc_name=ctrl_rc_name,
            neighbor_rc_name=prev_rc_name,
            m0_id=MASK_RC_110, m0_fn=mask_110,
            m1_id=MASK_RC_100, m1_fn=mask_100,
            m2_id=MASK_RC_110, m2_fn=mask_110,
            ts01=ts01_ls2, tlz=tlz_ls2, ts02=ts02_ls2, tkon=tkon_ls2,
            prev_name=prev_rc_name, next_name=next_rc_name,
        )
        detectors.append(det_prev)
        
    # Р’РµС‚РєР° Next (011 в†’ 001 в†’ 011)
    if next_rc_name:
        det_next = _make_branch_detector(
            ctrl_rc_name=ctrl_rc_name,
            neighbor_rc_name=next_rc_name,
            m0_id=MASK_RC_011, m0_fn=mask_011,
            m1_id=MASK_RC_001, m1_fn=mask_001,
            m2_id=MASK_RC_011, m2_fn=mask_011,
            ts01=ts01_ls2, tlz=tlz_ls2, ts02=ts02_ls2, tkon=tkon_ls2,
            prev_name=prev_rc_name, next_name=next_rc_name,
        )
        detectors.append(det_next)
        
    return BaseVariantWrapper(detectors)
    



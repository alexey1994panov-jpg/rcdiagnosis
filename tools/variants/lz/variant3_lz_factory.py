# variant3_lz_factory.py вЂ” Р Р•Р¤РђРљРўРћР РРќР“: РґРµРєР»Р°СЂР°С‚РёРІРЅС‹Р№ СЃС‚РёР»СЊ, РіРѕС‚РѕРІ Рє РїРµСЂРµРЅРѕСЃСѓ РЅР° C

from typing import Optional

from core.base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from core.variants_common import mask_101, mask_111

# ID РјР°СЃРєРё РґР»СЏ РѕС‚Р»Р°РґРєРё
MASK_101 = 3
MASK_111 = 4


def make_lz3_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_lz3: float,
    tlz_lz3: float,
    ts02_lz3: float,
    tkon_lz3: float,
) -> BaseDetector:
    """
    Р¤Р°Р±СЂРёРєР° РґРµС‚РµРєС‚РѕСЂР° Р›Р— v3 (С€СѓРЅС‚РѕРІРѕРµ РґРІРёР¶РµРЅРёРµ С‡РµСЂРµР· СЃРµРєС†РёСЋ).
    
    Р›РѕРіРёРєР°: 101 в†’ 111 в†’ 101
    - Р¤Р°Р·Р° 0 (p1): РєСЂР°СЏ Р·Р°РЅСЏС‚С‹, С†РµРЅС‚СЂ СЃРІРѕР±РѕРґРµРЅ в‰Ґ ts01_lz3
    - Р¤Р°Р·Р° 1 (p2): РІСЃРµ Р·Р°РЅСЏС‚С‹ в‰Ґ tlz_lz3
    - Р¤Р°Р·Р° 2 (p3): РєСЂР°СЏ Р·Р°РЅСЏС‚С‹, С†РµРЅС‚СЂ СЃРІРѕР±РѕРґРµРЅ в‰Ґ ts02_lz3 в†’ РѕС‚РєСЂС‹С‚РёРµ
    
    РўСЂРµР±РѕРІР°РЅРёСЏ: РѕР±Р° СЃРѕСЃРµРґР° РґРѕР»Р¶РЅС‹ Р±С‹С‚СЊ РґРѕСЃС‚РѕРІРµСЂРЅС‹.
    
    Р”РРќРђРњРР§Р•РЎРљРђРЇ РўРћРџРћР›РћР“РРЇ:
    - prev_rc_name/next_rc_name вЂ” fallback РёР· РєРѕРЅС„РёРіР°
    - Р РµР°Р»СЊРЅС‹Рµ СЃРѕСЃРµРґРё РёР· step.effective_prev_rc / step.effective_next_rc
    - Р•СЃР»Рё С…РѕС‚СЏ Р±С‹ РѕРґРёРЅ СЃРѕСЃРµРґ = None вЂ” РјР°СЃРєР° 101/111 РІРµСЂРЅС‘С‚ False
    
    Р­РєРІРёРІР°Р»РµРЅС‚ РЅР° C:
    ```c
    PhaseConfig phases[] = {
        {0, ts01, 1, TIMER_CONTINUOUS, true, MASK_101, true, true},
        {1, tlz,  2, TIMER_CONTINUOUS, true, MASK_111, true, true},
        {2, ts02, -1, TIMER_CONTINUOUS, true, MASK_101, true, true}
    };
    ```
    """
    
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz3),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_101,
            mask_fn=mask_101,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_lz3),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_111,
            mask_fn=mask_111,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=2,
            duration=float(ts02_lz3),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_101,
            mask_fn=mask_101,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz3),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="v3",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )


# =========================================================================
# Р­РљРЎРџРћР Рў РЎРҐР•РњР«
# =========================================================================

V3_SCHEMA = {
    "variant_id": 3,
    "variant_name": "lz3",
    "description": "РЁСѓРЅС‚РѕРІРѕРµ РґРІРёР¶РµРЅРёРµ: 101 в†’ 111 в†’ 101",
    "phases": [
        {
            "phase_id": 0,
            "name": "p1",
            "mask": "101",
            "mask_id": MASK_101,
            "duration_param": "ts01_lz3",
            "requires_prev_ok": True,
            "requires_next_ok": True,
        },
        {
            "phase_id": 1,
            "name": "p2",
            "mask": "111",
            "mask_id": MASK_111,
            "duration_param": "tlz_lz3",
            "requires_prev_ok": True,
            "requires_next_ok": True,
        },
        {
            "phase_id": 2,
            "name": "p3",
            "mask": "101",
            "mask_id": MASK_101,
            "duration_param": "ts02_lz3",
            "requires_prev_ok": True,
            "requires_next_ok": True,
        },
    ],
    "completion": {
        "mode": "FREE_TIME",
        "duration_param": "tkon_lz3",
    },
    "parameters": ["ts01_lz3", "ts02_lz3", "tlz_lz3", "tkon_lz3"],
    "topology": "dynamic",  # NEW: РїРѕРґРґРµСЂР¶РєР° РґРёРЅР°РјРёС‡РµСЃРєРѕР№ С‚РѕРїРѕР»РѕРіРёРё
}


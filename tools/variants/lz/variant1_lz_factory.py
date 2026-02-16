# variant1_lz_factory.py вЂ” Р Р•Р¤РђРљРўРћР РРќР“: РґРµРєР»Р°СЂР°С‚РёРІРЅС‹Р№ СЃС‚РёР»СЊ, РіРѕС‚РѕРІ Рє РїРµСЂРµРЅРѕСЃСѓ РЅР° C

from typing import Optional

from core.base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from core.variants_common import mask_000, mask_010

# ID РјР°СЃРєРё РґР»СЏ РѕС‚Р»Р°РґРєРё Рё СЃРµСЂРёР°Р»РёР·Р°С†РёРё
MASK_000 = 1
MASK_010 = 2


def make_lz1_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_lz1: float,
    tlz_lz1: float,
    tkon_lz1: float,
) -> BaseDetector:
    """
    Р¤Р°Р±СЂРёРєР° РґРµС‚РµРєС‚РѕСЂР° Р›Р— v1 (РєР»Р°СЃСЃРёС‡РµСЃРєР°СЏ Р»РѕР¶РЅР°СЏ Р·Р°РЅСЏС‚РѕСЃС‚СЊ).
    
    Р›РѕРіРёРєР°: 000 в†’ 010
    - Р¤Р°Р·Р° 0 (idle): РІСЃРµ СЃРІРѕР±РѕРґРЅС‹ в‰Ґ ts01_lz1
    - Р¤Р°Р·Р° 1 (active): С†РµРЅС‚СЂ Р·Р°РЅСЏС‚, РєСЂР°СЏ СЃРІРѕР±РѕРґРЅС‹ в‰Ґ tlz_lz1 в†’ РѕС‚РєСЂС‹С‚РёРµ
    
    РўСЂРµР±РѕРІР°РЅРёСЏ: РѕР±Р° СЃРѕСЃРµРґР° РґРѕР»Р¶РЅС‹ Р±С‹С‚СЊ РґРѕСЃС‚РѕРІРµСЂРЅС‹ (prev_control_ok=True, next_control_ok=True)
    
    Р”РРќРђРњРР§Р•РЎРљРђРЇ РўРћРџРћР›РћР“РРЇ:
    - prev_rc_name/next_rc_name РёСЃРїРѕР»СЊР·СѓСЋС‚СЃСЏ РєР°Рє fallback РёР· РєРѕРЅС„РёРіР°
    - Р РµР°Р»СЊРЅС‹Рµ СЃРѕСЃРµРґРё Р±РµСЂСѓС‚СЃСЏ РёР· step.effective_prev_rc / step.effective_next_rc
    - Р•СЃР»Рё effective_*_rc = None вЂ” СЃРѕСЃРµРґР° РЅРµС‚ (РєСЂР°Р№РЅСЏСЏ Р Р¦ РёР»Рё latch РёСЃС‚С‘Рє)
    
    Р­РєРІРёРІР°Р»РµРЅС‚ РЅР° C:
    ```c
    PhaseConfig phases[] = {
        {0, ts01, 1, TIMER_CONTINUOUS, true, MASK_000, true, true},
        {1, tlz,  -1, TIMER_CONTINUOUS, true, MASK_010, true, true}
    };
    DetectorConfig cfg = {0, phases, 2, tkon, COMPLETION_FREE_TIME, "v1"};
    BaseDetector det = {cfg, prev, ctrl, next};  // fallback РёРјРµРЅР°
    ```
    """
    
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz1),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_000,
            mask_fn=mask_000,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_lz1),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_010,
            mask_fn=mask_010,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz1),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="v1",
    )
    
    # Р”РµРєР»Р°СЂР°С‚РёРІРЅС‹Р№ СЂРµР¶РёРј: РёРјРµРЅР° Р Р¦ вЂ” fallback РёР· РєРѕРЅС„РёРіР°
    # Р РµР°Р»СЊРЅР°СЏ С‚РѕРїРѕР»РѕРіРёСЏ РёР· step.effective_*_rc
    return BaseDetector(
        config=config,
        prev_rc_name=prev_rc_name,  # fallback
        ctrl_rc_name=ctrl_rc_name,  # С„РёРєСЃРёСЂРѕРІР°РЅРѕ
        next_rc_name=next_rc_name,  # fallback
    )


# =========================================================================
# Р­РљРЎРџРћР Рў РЎРҐР•РњР« Р”Р›РЇ Р’РќР•РЁРќРРҐ РРќРЎРўР РЈРњР•РќРўРћР’
# =========================================================================

V1_SCHEMA = {
    "variant_id": 1,
    "variant_name": "lz1",
    "description": "РљР»Р°СЃСЃРёС‡РµСЃРєР°СЏ Р»РѕР¶РЅР°СЏ Р·Р°РЅСЏС‚РѕСЃС‚СЊ: 000 в†’ 010",
    "phases": [
        {
            "phase_id": 0,
            "name": "idle",
            "mask": "000",
            "mask_id": MASK_000,
            "duration_param": "ts01_lz1",
            "requires_prev_ok": True,
            "requires_next_ok": True,
        },
        {
            "phase_id": 1,
            "name": "active",
            "mask": "010",
            "mask_id": MASK_010,
            "duration_param": "tlz_lz1",
            "requires_prev_ok": True,
            "requires_next_ok": True,
        },
    ],
    "completion": {
        "mode": "FREE_TIME",
        "duration_param": "tkon_lz1",
    },
    "parameters": ["ts01_lz1", "tlz_lz1", "tkon_lz1"],
    "topology": "dynamic",  # NEW: РїРѕРґРґРµСЂР¶РєР° РґРёРЅР°РјРёС‡РµСЃРєРѕР№ С‚РѕРїРѕР»РѕРіРёРё
}


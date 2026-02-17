# -*- coding: utf-8 -*-
"""
Р¤Р°Р±СЂРёРєР° РґР»СЏ РІР°СЂРёР°РЅС‚Р° LS1 (РљР»Р°СЃСЃРёС‡РµСЃРєР°СЏ Р»РѕР¶РЅР°СЏ СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ)

РћРїРёСЃР°РЅРёРµ:
    LS1 РґРµС‚РµРєС‚РёСЂСѓРµС‚ РєР»Р°СЃСЃРёС‡РµСЃРєСѓСЋ Р»РѕР¶РЅСѓСЋ СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ - РѕР±СЂР°С‚РЅС‹Р№ РїР°С‚С‚РµСЂРЅ РѕС‚ LZ1.
    РСЃРїРѕР»СЊР·СѓРµС‚ С‚Рµ Р¶Рµ РјР°СЃРєРё С‡С‚Рѕ Рё LZ1, РЅРѕ РІ РѕР±СЂР°С‚РЅРѕРј РїРѕСЂСЏРґРєРµ: 010 в†’ 000
    
Р¤Р°Р·С‹:
    0 (C0101): prev-ctrl-next = 0-1-0 (С†РµРЅС‚СЂ Р·Р°РЅСЏС‚, РєСЂР°СЏ СЃРІРѕР±РѕРґРЅС‹) в†’ РґР»РёС‚РµР»СЊРЅРѕСЃС‚СЊ ts01_ls1
    1 (tail):  prev-ctrl-next = 0-0-0 (РІСЃРµ СЃРІРѕР±РѕРґРЅС‹) в†’ РґР»РёС‚РµР»СЊРЅРѕСЃС‚СЊ tlz_ls1 в†’ РѕС‚РєСЂС‹С‚РёРµ Р›РЎ
    
Р—Р°РІРµСЂС€РµРЅРёРµ:
    РІСЃРµ СЃРІРѕР±РѕРґРЅС‹ в‰Ґ tkon_ls1 в†’ Р·Р°РєСЂС‹С‚РёРµ

РћСЃРѕР±РµРЅРЅРѕСЃС‚Рё:
    - РўСЂРµР±СѓРµС‚ РѕР±РѕРёС… СЃРѕСЃРµРґРµР№ (NeighborRequirement.BOTH)
    - РСЃРїРѕР»СЊР·СѓРµС‚ РјР°СЃРєРё РёР· LZ1: mask_010 Рё mask_000
    - РЎРѕСЃРµРґРё РѕРїСЂРµРґРµР»СЏСЋС‚СЃСЏ РїРѕ СЃС‚СЂРµР»РєР°Рј (РЅСѓР¶РЅС‹ switch_states РІ СЃС†РµРЅР°СЂРёРё)
"""

from core.base_detector import (
    BaseDetector,
    PhaseConfig,
    DetectorConfig,
    CompletionMode,
    NeighborRequirement,
)
from core.variants_common import mask_010, mask_000

# РСЃРїРѕР»СЊР·СѓРµРј РјР°СЃРєРё РёР· LZ1 РІ РѕР±СЂР°С‚РЅРѕРј РїРѕСЂСЏРґРєРµ
MASK_RC_010 = 2  # 0-1-0: center occupied, neighbors free
MASK_RC_000 = 1  # 0-0-0: all free


def make_ls1_detector(
    prev_rc_name: str,
    ctrl_rc_name: str,
    next_rc_name: str,
    ts01_ls1: float,
    tlz_ls1: float,
    tkon_ls1: float,
) -> BaseDetector:
    """
    РЎРѕР·РґР°РµС‚ РґРµС‚РµРєС‚РѕСЂ LS1 (РљР»Р°СЃСЃРёС‡РµСЃРєР°СЏ Р»РѕР¶РЅР°СЏ СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ).
    
    Р›РѕРіРёРєР°: 010 в†’ 000 (РѕР±СЂР°С‚РЅС‹Р№ РїР°С‚С‚РµСЂРЅ РѕС‚ LZ1)
    
    Args:
        prev_rc_name: РРјСЏ РїСЂРµРґС‹РґСѓС‰РµР№ Р Р¦
        ctrl_rc_name: РРјСЏ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕР№ Р Р¦
        next_rc_name: РРјСЏ СЃР»РµРґСѓСЋС‰РµР№ Р Р¦
        ts01_ls1: Р”Р»РёС‚РµР»СЊРЅРѕСЃС‚СЊ С„Р°Р·С‹ C0101 (0-1-0)
        tlz_ls1: Р”Р»РёС‚РµР»СЊРЅРѕСЃС‚СЊ С„Р°Р·С‹ tail (0-0-0)
        tkon_ls1: Р’СЂРµРјСЏ РЅР° Р·Р°РІРµСЂС€РµРЅРёРµ РїРѕСЃР»Рµ РѕС‚РєСЂС‹С‚РёСЏ
        
    Returns:
        BaseDetector РґР»СЏ РІР°СЂРёР°РЅС‚Р° LS1
    """
    phases = [
        # Р¤Р°Р·Р° 0: C0101 - 0-1-0 (С†РµРЅС‚СЂ Р·Р°РЅСЏС‚, РєСЂР°СЏ СЃРІРѕР±РѕРґРЅС‹)
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_ls1),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_RC_010,
            mask_fn=mask_010,  # РёР· LZ1
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        # Р¤Р°Р·Р° 1: tail - 0-0-0 (РІСЃРµ СЃРІРѕР±РѕРґРЅС‹) в†’ РѕС‚РєСЂС‹С‚РёРµ
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_ls1),
            next_phase_id=-1,  # -1 = РѕС‚РєСЂС‹С‚РёРµ Р›РЎ
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_RC_000,
            mask_fn=mask_000,  # РёР· LZ1
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_ls1),
        completion_mode=CompletionMode.OCCUPIED_TIME,  # ЛС закрывается когда РЦ занята
        variant_name="ls1",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )


# JSON-СЃС…РµРјР° РґР»СЏ РґРѕРєСѓРјРµРЅС‚Р°С†РёРё
LS1_SCHEMA = {
    "variant_id": 101,
    "variant_name": "ls1",
    "description": "РљР»Р°СЃСЃРёС‡РµСЃРєР°СЏ Р»РѕР¶РЅР°СЏ СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ (РѕР±СЂР°С‚РЅС‹Р№ РїР°С‚С‚РµСЂРЅ РѕС‚ LZ1)",
    "phases": [
        {"id": 0, "name": "C0101", "condition": "0-1-0 (С†РµРЅС‚СЂ Р·Р°РЅСЏС‚, РєСЂР°СЏ СЃРІРѕР±РѕРґРЅС‹)"},
        {"id": 1, "name": "tail", "condition": "0-0-0 (РІСЃРµ СЃРІРѕР±РѕРґРЅС‹)"},
    ],
    "parameters": ["ts01_ls1", "tlz_ls1", "tkon_ls1"],
    "topology": "both_neighbors",
    "requires_neighbors": True,
    "requires_signals": False,
    "uses_lz1_masks": True,  # РСЃРїРѕР»СЊР·СѓРµС‚ РјР°СЃРєРё РёР· LZ1 РІ РѕР±СЂР°С‚РЅРѕРј РїРѕСЂСЏРґРєРµ
}



# variant2_lz_factory.py вЂ” Р Р•Р¤РђРљРўРћР Р˜РќР“: РґРµРєР»Р°СЂР°С‚РёРІРЅС‹Р№ СЃС‚РёР»СЊ, РіРѕС‚РѕРІ Рє РїРµСЂРµРЅРѕСЃСѓ РЅР° C

from typing import Any, Optional, Tuple

from core.base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from core.base_wrapper import BaseVariantWrapper
from core.variants_common import mask_100, mask_110, mask_100_or_000, mask_001, mask_011, mask_001_or_000

# ID РјР°СЃРєРё РґР»СЏ РѕС‚Р»Р°РґРєРё
MASK_100 = 5
MASK_110 = 6
MASK_100_or_000 = 104
MASK_001 = 7
MASK_011 = 8
MASK_001_or_000 = 101


def _make_branch_detector(
    p1_mask_id: int,
    p1_mask_fn: callable,
    p2_mask_id: int,
    p2_mask_fn: callable,
    p3_mask_id: int,
    p3_mask_fn: callable,
    ts01_lz2: float,
    tlz_lz2: float,
    ts02_lz2: float,
    tkon_lz2: float,
    prev_rc_name: Optional[str] = None,
    ctrl_rc_name: str = "",
    next_rc_name: Optional[str] = None,
) -> BaseDetector:
    """РЈРЅРёРІРµСЂСЃР°Р»СЊРЅР°СЏ С„Р°Р±СЂРёРєР° РѕРґРЅРѕР№ РІРµС‚РєРё v2."""
    
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz2),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=p1_mask_id,
            mask_fn=p1_mask_fn,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_lz2),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=p2_mask_id,
            mask_fn=p2_mask_fn,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=2,
            duration=float(ts02_lz2),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=p3_mask_id,
            mask_fn=p3_mask_fn,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz2),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="v2_branch",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name
    )


def make_lz2_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_lz2: float,
    ts02_lz2: float,
    tlz_lz2: float,
    tkon_lz2: float,
) -> BaseVariantWrapper:
    """
    Р¤Р°Р±СЂРёС‡РЅР°СЏ С„СѓРЅРєС†РёСЏ РґР»СЏ СЃРѕР·РґР°РЅРёСЏ РґРµС‚РµРєС‚РѕСЂР° Р›Р— v2.
    """
    
    # в†ђ РЎРћР—Р”РђРЃРњ Р”Р•РўР•РљРўРћР Р«
    det_prev = _make_branch_detector(
        MASK_100, mask_100,
        MASK_110, mask_110,
        MASK_100_or_000, mask_100_or_000,
        ts01_lz2, tlz_lz2, ts02_lz2, tkon_lz2,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )
    
    det_next = _make_branch_detector(
        MASK_001, mask_001,
        MASK_011, mask_011,
        MASK_001_or_000, mask_001_or_000,
        ts01_lz2, tlz_lz2, ts02_lz2, tkon_lz2,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )
    
    # в†ђ Р’РћР—Р’Р РђР©РђР•Рњ РћР‘РЃР РўРљРЈ РЎ Р”Р•РўР•РљРўРћР РђРњР˜
    return BaseVariantWrapper([det_prev, det_next])

# =========================================================================
# Р­РљРЎРџРћР Рў РЎРҐР•Рњ
# =========================================================================

V2_SCHEMA_PREV_BRANCH = {
    "branch_name": "prev",
    "description": "РџСЂРµРґС‹РґСѓС‰РёР№ СЃРѕСЃРµРґ Р·Р°РЅСЏС‚",
    "phases": [
        {"phase_id": 0, "mask": "100", "mask_id": MASK_100, "name": "p1"},
        {"phase_id": 1, "mask": "110", "mask_id": MASK_110, "name": "p2"},
        {"phase_id": 2, "mask": "100|000", "mask_id": MASK_100_or_000, "name": "p3"},
    ],
    "requires_prev_ok": True,
    "requires_next_ok": None,
}

V2_SCHEMA_NEXT_BRANCH = {
    "branch_name": "next",
    "description": "РЎР»РµРґСѓСЋС‰РёР№ СЃРѕСЃРµРґ Р·Р°РЅСЏС‚",
    "phases": [
        {"phase_id": 0, "mask": "001", "mask_id": MASK_001, "name": "p1"},
        {"phase_id": 1, "mask": "011", "mask_id": MASK_011, "name": "p2"},
        {"phase_id": 2, "mask": "001|000", "mask_id": MASK_001_or_000, "name": "p3"},
    ],
    "requires_prev_ok": None,
    "requires_next_ok": True,
}

V2_SCHEMA = {
    "variant_id": 2,
    "variant_name": "lz2",
    "description": "Р—Р°РЅСЏС‚РѕСЃС‚СЊ РѕРґРЅРѕРіРѕ РёР· СЃРѕСЃРµРґРµР№: 100в†’110в†’(100|000) Р˜Р›Р˜ 001в†’011в†’(001|000)",
    "branches": [V2_SCHEMA_PREV_BRANCH, V2_SCHEMA_NEXT_BRANCH],
    "completion": {"mode": "FREE_TIME"},
    "parameters": ["ts01_lz2", "ts02_lz2", "tlz_lz2", "tkon_lz2"],
    "topology": "dynamic",  # NEW: РїРѕРґРґРµСЂР¶РєР° РґРёРЅР°РјРёС‡РµСЃРєРѕР№ С‚РѕРїРѕР»РѕРіРёРё
}

"""
detectors_engine.py вЂ” РґРІРёР¶РѕРє РґРµС‚РµРєС‚РѕСЂРѕРІ СЃ РїРѕРґРґРµСЂР¶РєРѕР№ РґРёРЅР°РјРёС‡РµСЃРєРѕР№ С‚РѕРїРѕР»РѕРіРёРё.

Р’РµСЂСЃРёСЏ: 2.0 (РґРёРЅР°РјРёС‡РµСЃРєР°СЏ С‚РѕРїРѕР»РѕРіРёСЏ + СЃР±СЂРѕСЃ РїСЂРё СЃРјРµРЅРµ СЃРѕСЃРµРґРµР№)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from station.station_config import NODES
from station.station_capabilities import RC_CAPABILITIES
from station.station_model import load_station_from_config, StationModel

from core.base_detector import BaseDetector, DetectorConfig, PhaseConfig, CompletionMode
from variants.lz.variant1_lz_factory import make_lz1_detector
from variants.lz.variant2_lz_factory import make_lz2_detector
from variants.lz.variant3_lz_factory import make_lz3_detector
from variants.lz.variant4_lz_factory import make_lz4_detector
from variants.lz.variant5_lz_factory import make_lz5_detector
from variants.lz.variant6_lz_factory import make_lz6_detector
from variants.lz.variant7_lz_factory import make_lz7_detector
from variants.lz.variant8_lz_factory import make_lz8_detector
from variants.ls.variant_ls9_lz_factory import make_ls9_detector
from variants.ls.variant_ls1_lz_factory import make_ls1_detector
from variants.ls.variant_ls2_lz_factory import make_ls2_detector
from variants.ls.variant_ls4_lz_factory import make_ls4_detector
from variants.ls.variant_ls5_lz_factory import make_ls5_detector
from variants.lz.variant_lz9_lz_factory import make_lz9_detector
from variants.lz.variant_lz12_lz_factory import make_lz12_detector
from variants.lz.variant_lz11_lz_factory import make_lz11_detector
from variants.lz.variant_lz13_lz_factory import make_lz13_detector
from variants.lz.variant_lz10_lz_factory import make_lz10_detector
from variants.ls.variant_ls6_lz_factory import make_ls6_detector
from core.detectors.phase_exceptions import apply_phase_exception_policy
from core.detectors.types import DetectorsConfig, DetectorsResult, DetectorsState


@dataclass
class _StepAdapter:
    """
    РђРґР°РїС‚РµСЂ РґР»СЏ РїРµСЂРµРґР°С‡Рё РґР°РЅРЅС‹С… РІ BaseDetector.
    
    Р”РРќРђРњРР§Р•РЎРљРђРЇ РўРћРџРћР›РћР“РРЇ:
    - effective_prev_rc / effective_next_rc РїСЂРёС…РѕРґСЏС‚ РёР· topology_manager
    """
    rc_states: Dict[str, int]  # РўР•РџР•Р Р¬: РїРѕ ID, РЅРµ РїРѕ РёРјРµРЅР°Рј!
    modes: Dict[str, Any]
    signal_states: Dict[str, int]
    effective_prev_rc: Optional[str]  # ID
    effective_next_rc: Optional[str]  # ID
    ctrl_rc_name: str
    rc_capabilities: Dict[str, Dict] = field(default_factory=dict)


def init_detectors_engine(cfg: DetectorsConfig, rc_ids: List[str]) -> DetectorsState:
    """РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РґРµС‚РµРєС‚РѕСЂРѕРІ РїРѕ РєРѕРЅС„РёРіСѓСЂР°С†РёРё."""
    state = DetectorsState()
    
    # rc_capabilities needed for LS5, LZ9, LZ12 initialization
    rc_capabilities = {}
    # This part is duplicated from update_detectors, but needed here for init
    # In a real system, this might be passed in or loaded once.
    from station.station_capabilities import RC_CAPABILITIES
    rc_capabilities = {
        rc_id: {
            'can_lock': caps.get('can_lock', True),
            'is_endpoint': caps.get('is_endpoint', False),
            'allowed_detectors': caps.get('allowed_detectors', []),
            'allowed_ls_detectors': caps.get('allowed_ls_detectors', []),
            'task_lz_number': caps.get('task_lz_number'),
            'task_ls_number': caps.get('task_ls_number'),
        }
        for rc_id, caps in RC_CAPABILITIES.items()
    }

    if cfg.enable_lz1:
        state.v1 = make_lz1_detector(
            prev_rc_name=cfg.prev_rc_name,
            ctrl_rc_name=cfg.ctrl_rc_name,
            next_rc_name=cfg.next_rc_name,
            ts01_lz1=cfg.ts01_lz1,
            tlz_lz1=cfg.tlz_lz1,
            tkon_lz1=cfg.tkon_lz1,
        )
    
    if cfg.enable_lz2:
        state.v2 = make_lz2_detector(
            prev_rc_name=cfg.prev_rc_name,
            ctrl_rc_name=cfg.ctrl_rc_name,
            next_rc_name=cfg.next_rc_name,
            ts01_lz2=cfg.ts01_lz2,
            ts02_lz2=cfg.ts02_lz2,
            tlz_lz2=cfg.tlz_lz2,
            tkon_lz2=cfg.tkon_lz2,
        )
    
    if cfg.enable_lz3:
        state.v3 = make_lz3_detector(
            prev_rc_name=cfg.prev_rc_name,
            ctrl_rc_name=cfg.ctrl_rc_name,
            next_rc_name=cfg.next_rc_name,
            ts01_lz3=cfg.ts01_lz3,
            ts02_lz3=cfg.ts02_lz3,
            tlz_lz3=cfg.tlz_lz3,
            tkon_lz3=cfg.tkon_lz3,
        )

    if cfg.enable_lz4:
        state.v4 = make_lz4_detector(
            ctrl_rc_id=cfg.ctrl_rc_id,
            ts01_lz4=cfg.ts01_lz4,
            tlz_lz4=cfg.tlz_lz4,
            tkon_lz4=cfg.tkon_lz4,
            sig_prev_to_ctrl=cfg.sig_lz4_prev_to_ctrl,
            sig_ctrl_to_next=cfg.sig_lz4_ctrl_to_next,
        )

    if cfg.enable_lz5:
        state.v5 = make_lz5_detector(
            ctrl_rc_name=cfg.ctrl_rc_name,
            ts01_lz5=cfg.ts01_lz5,
            tlz_lz5=cfg.tlz_lz5,
            tkon_lz5=cfg.tkon_lz5,
        )

    if cfg.enable_lz6:
        state.v6 = make_lz6_detector(
            ctrl_rc_name=cfg.ctrl_rc_name,
            ts01_lz6=cfg.ts01_lz6,
            tlz_lz6=cfg.tlz_lz6,
            tkon_lz6=cfg.tkon_lz6,
    )
    
    
    if cfg.enable_lz7:
        state.v7 = make_lz7_detector(
            prev_rc_name=cfg.prev_rc_name,
            ctrl_rc_name=cfg.ctrl_rc_name,
            next_rc_name=cfg.next_rc_name,
            ts01_lz7=cfg.ts01_lz7,
            tlz_lz7=cfg.tlz_lz7,
            tkon_lz7=cfg.tkon_lz7,
        )
    
    if cfg.enable_lz8:
        state.v8 = make_lz8_detector(
            prev_rc_name=cfg.prev_rc_name,
            ctrl_rc_name=cfg.ctrl_rc_name,
            next_rc_name=cfg.next_rc_name,
            ts01_lz8=cfg.ts01_lz8,
            ts02_lz8=cfg.ts02_lz8,
            tlz_lz8=cfg.tlz_lz8,
            tkon_lz8=cfg.tkon_lz8,
        )
    
    if cfg.enable_ls9:
        state.ls9 = make_ls9_detector(
            ctrl_rc_name=cfg.ctrl_rc_name,
            ts01_ls9=cfg.ts01_ls9,
            tlz_ls9=cfg.tlz_ls9,
            tkon_ls9=cfg.tkon_ls9,
        )
    
    if cfg.enable_ls1:
        state.ls1 = make_ls1_detector(
            prev_rc_name=cfg.prev_rc_name,
            ctrl_rc_name=cfg.ctrl_rc_name,
            next_rc_name=cfg.next_rc_name,
            ts01_ls1=cfg.ts01_ls1,
            tlz_ls1=cfg.tlz_ls1,
            tkon_ls1=cfg.tkon_ls1,
        )

    if cfg.enable_ls2:
        state.ls2 = make_ls2_detector(
            prev_rc_name=cfg.prev_rc_name,
            ctrl_rc_name=cfg.ctrl_rc_name,
            next_rc_name=cfg.next_rc_name,
            ts01_ls2=cfg.ts01_ls2,
            tlz_ls2=cfg.tlz_ls2,
            ts02_ls2=cfg.ts02_ls2,
            tkon_ls2=cfg.tkon_ls2,
        )

    if cfg.enable_ls4:
        state.ls4 = make_ls4_detector(
            prev_rc_name=cfg.prev_rc_name,
            ctrl_rc_name=cfg.ctrl_rc_name,
            next_rc_name=cfg.next_rc_name,
            ts01_ls4=cfg.ts01_ls4,
            tlz01_ls4=cfg.tlz01_ls4,
            tlz02_ls4=cfg.tlz02_ls4,
            ts02_ls4=cfg.ts02_ls4,
            tkon_ls4=cfg.tkon_ls4,
        )

    if cfg.enable_ls5:
        state.ls5 = make_ls5_detector(
            prev_rc_name=cfg.prev_rc_name,
            ctrl_rc_name=cfg.ctrl_rc_name,
            next_rc_name=cfg.next_rc_name,
            ts01_ls5=cfg.ts01_ls5,
            tlz_ls5=cfg.tlz_ls5,
            tkon_ls5=cfg.tkon_ls5
        )

    if cfg.enable_lz9:
        state.lz9 = make_lz9_detector(
            ctrl_rc_id=cfg.ctrl_rc_id,
            ts01_lz9=cfg.ts01_lz9,
            tlz_lz9=cfg.tlz_lz9,
            t_kon=cfg.tkon_lz9
        )

    if cfg.enable_lz12:
        state.lz12 = make_lz12_detector(
            ctrl_rc_id=cfg.ctrl_rc_id,
            ts01_lz12=cfg.ts01_lz12,
            ts02_lz12=cfg.ts02_lz12,
            tlz_lz12=cfg.tlz_lz12,
            t_kon=cfg.tkon_lz12
        )

    if cfg.enable_lz11:
        state.lz11 = make_lz11_detector(
            ctrl_rc_id=cfg.ctrl_rc_id,
            sig_ids=(cfg.sig_lz11_a, cfg.sig_lz11_b),
            ts01_lz11=cfg.ts01_lz11,
            tlz_lz11=cfg.tlz_lz11,
            tkon_lz11=cfg.tkon_lz11,
        )

    if cfg.enable_lz13:
        state.lz13 = make_lz13_detector(
            ctrl_rc_id=cfg.ctrl_rc_id,
            prev_rc_id=cfg.prev_rc_name,
            next_rc_id=cfg.next_rc_name,
            sig_prev=cfg.sig_lz13_prev,
            sig_next=cfg.sig_lz13_next,
            ts01_lz13=cfg.ts01_lz13,
            ts02_lz13=cfg.ts02_lz13,
            tlz_lz13=cfg.tlz_lz13,
            tkon_lz13=cfg.tkon_lz13,
        )

    if cfg.enable_lz10:
        state.lz10 = make_lz10_detector(
            ctrl_rc_id=cfg.ctrl_rc_id,
            prev_rc_id=cfg.prev_rc_name,
            next_rc_id=cfg.next_rc_name,
            sig_to_next=cfg.sig_lz10_to_next,
            sig_to_prev=cfg.sig_lz10_to_prev,
            ts01_lz10=cfg.ts01_lz10,
            ts02_lz10=cfg.ts02_lz10,
            ts03_lz10=cfg.ts03_lz10,
            tlz_lz10=cfg.tlz_lz10,
            tkon_lz10=cfg.tkon_lz10,
        )

    if cfg.enable_ls6:
        state.ls6 = make_ls6_detector(
            ctrl_rc_id=cfg.ctrl_rc_id,
            prev_rc_id=cfg.prev_rc_name,
            next_rc_id=cfg.next_rc_name,
            sig_prev=cfg.sig_ls6_prev,
            ts01_ls6=cfg.ts01_ls6,
            tlz_ls6=cfg.tlz_ls6,
            tkon_ls6=cfg.tkon_ls6,
        )

    # Единая фазовая политика исключений: вешаем на финальные фазы открытия.
    apply_phase_exception_policy(cfg, state)

    return state


def check_topology_change(
    state: DetectorsState,
    curr_prev: Optional[str],
    curr_next: Optional[str],
) -> bool:
    """
    РџСЂРѕРІРµСЂСЏРµС‚, РёР·РјРµРЅРёР»Р°СЃСЊ Р»Рё С‚РѕРїРѕР»РѕРіРёСЏ (СЃРѕСЃРµРґРё) РїРѕ СЃСЂР°РІРЅРµРЅРёСЋ СЃ РїСЂРѕС€Р»С‹Рј С€Р°РіРѕРј.
    
    :return: True РµСЃР»Рё СЃРѕСЃРµРґРё РёР·РјРµРЅРёР»РёСЃСЊ (РІРєР»СЋС‡Р°СЏ None)
    """
    # РЎСЂР°РІРЅРёРІР°РµРј prev
    prev_changed = state.last_effective_prev != curr_prev
    
    # РЎСЂР°РІРЅРёРІР°РµРј next
    next_changed = state.last_effective_next != curr_next
    
    return prev_changed or next_changed


def reset_formation_phases(state: DetectorsState) -> None:
    """
    РЎР±СЂР°СЃС‹РІР°РµС‚ С„Р°Р·С‹ С„РѕСЂРјРёСЂРѕРІР°РЅРёСЏ РІСЃРµС… РЅРµР°РєС‚РёРІРЅС‹С… РґРµС‚РµРєС‚РѕСЂРѕРІ.
    
    РђРєС‚РёРІРЅС‹Рµ РґРµС‚РµРєС‚РѕСЂС‹ (РѕС‚РєСЂС‹С‚С‹Рµ Р”РЎ) РїСЂРѕРґРѕР»Р¶Р°СЋС‚ СЂР°Р±РѕС‚Сѓ РґРѕ Р·Р°РєСЂС‹С‚РёСЏ РїРѕ t_kon.
    """
    # v1
    if state.v1 and not state.v1.active:
        state.v1.reset()
    
    # v2
    if state.v2 and hasattr(state.v2, 'active') and not state.v2.active:
        state.v2.reset()
    
    # v3
    if state.v3 and not state.v3.active:
        state.v3.reset()

    # v4
    if state.v4 and hasattr(state.v4, 'active') and not state.v4.active:
        state.v4.reset()

    # v5
    if state.v5 and hasattr(state.v5, 'active') and not state.v5.active:
        state.v5.reset()

    # v6
    if state.v6 and hasattr(state.v6, 'active') and not state.v6.active:
        state.v6.reset()
    
    # v7
    if state.v7 and hasattr(state.v7, 'active') and not state.v7.active:
        state.v7.reset()
    
    # v8
    if state.v8 and hasattr(state.v8, 'active') and not state.v8.active:
        state.v8.reset()
    
    # LS9
    if state.ls9 and not state.ls9.active:
        state.ls9.reset()
    
    # LS1
    if state.ls1 and not state.ls1.active:
        state.ls1.reset()

    # LS4
    if state.ls4 and not state.ls4.active:
        state.ls4.reset()

    # LZ11
    if state.lz11 and not state.lz11.active:
        state.lz11.reset()

    # LZ13
    if state.lz13 and hasattr(state.lz13, 'active') and not state.lz13.active:
        state.lz13.reset()

    # LZ10
    if state.lz10 and hasattr(state.lz10, 'active') and not state.lz10.active:
        state.lz10.reset()

    # LS6
    if state.ls6 and hasattr(state.ls6, 'active') and not state.ls6.active:
        state.ls6.reset()
    if state.ls4 and not state.ls4.active:
        state.ls4.reset()

    # LS5
    if state.ls5 and not state.ls5.active:
        state.ls5.reset()
    
    # LZ9
    if state.lz9 and not state.lz9.active:
        state.lz9.reset()

    # LZ12
    if state.lz12 and not state.lz12.active:
        state.lz12.reset()


def _is_already_ids(rc_states: Dict[str, int]) -> bool:
    """РџСЂРѕРІРµСЂСЏРµС‚, СЏРІР»СЏСЋС‚СЃСЏ Р»Рё РєР»СЋС‡Рё rc_states СѓР¶Рµ ID."""
    if not rc_states:
        return True
    first_key = next(iter(rc_states.keys()))
    return first_key in NODES  # РµСЃР»Рё РІ NODES вЂ” СЌС‚Рѕ ID

from typing import Dict
from functools import lru_cache

@lru_cache(maxsize=1)
def _get_name_to_id() -> Dict[str, str]:
    """РљСЌС€РёСЂРѕРІР°РЅРЅС‹Р№ РјР°РїРїРёРЅРі РёРјС‘РЅ РІ ID."""
    from station.station_config import NODES
    return {node["name"]: nid for nid, node in NODES.items() if node.get("name")}


def _ensure_rc_states_by_id(rc_states: Dict[str, int]) -> Dict[str, int]:
    """РљРѕРЅРІРµСЂС‚РёСЂСѓРµС‚ rc_states РІ С„РѕСЂРјР°С‚ РїРѕ ID РµСЃР»Рё РЅСѓР¶РЅРѕ."""
    if not rc_states:
        return {}
    
    sample_key = next(iter(rc_states.keys()))
    
    # РџСЂРѕРІРµСЂСЏРµРј: СЌС‚Рѕ ID СѓР¶Рµ?
    from station.station_config import NODES
    if sample_key in NODES:
        return rc_states  # СѓР¶Рµ ID
    
    # РљРѕРЅРІРµСЂС‚РёСЂСѓРµРј РёРјРµРЅР° РІ ID
    name_to_id = _get_name_to_id()
    return {name_to_id.get(k, k): v for k, v in rc_states.items()}

def update_detectors(
    det_state: DetectorsState,
    t: float,
    dt: float,
    rc_states: Dict[str, int],  # в†ђ РјРѕР¶РµС‚ Р±С‹С‚СЊ РёРјРµРЅР° РёР»Рё ID
    switch_states: Dict[str, int],
    signal_states: Dict[str, int],
    topology_info: Dict[str, Any],
    cfg: DetectorsConfig,
    modes: Dict[str, Any],
    station_model:  Optional['StationModel'] = None,
) -> Tuple[DetectorsState, DetectorsResult]:
    """
    РћР±РЅРѕРІР»СЏРµС‚ РІСЃРµ РґРµС‚РµРєС‚РѕСЂС‹ РЅР° РѕРґРЅРѕРј С€Р°РіРµ.
    rc_states: РєР»СЋС‡Рё вЂ” РёРјРµРЅР° РёР»Рё ID (Р°РІС‚РѕРѕРїСЂРµРґРµР»РµРЅРёРµ)
    """
    result = DetectorsResult()

    # === РљРћРќР’Р•Р РўРђР¦РРЇ rc_states РІ ID ===
    from station.station_config import NODES
    
    # РљСЌС€ РјР°РїРїРёРЅРіР° (РґР»СЏ C: СЃС‚Р°С‚РёС‡РµСЃРєР°СЏ С‚Р°Р±Р»РёС†Р°)
    name_to_id = {node["name"]: nid for nid, node in NODES.items() if node.get("name")}
    
    # РћРїСЂРµРґРµР»СЏРµРј С„РѕСЂРјР°С‚: РїСЂРѕРІРµСЂСЏРµРј РїРµСЂРІС‹Р№ РєР»СЋС‡
    sample_key = next(iter(rc_states.keys())) if rc_states else ""
    is_already_ids = sample_key in NODES
    
    
    rc_states_by_id = _ensure_rc_states_by_id(rc_states)
    
    # РџРѕР»СѓС‡Р°РµРј СЃРѕСЃРµРґРµР№ РёР· С‚РѕРїРѕР»РѕРіРёРё (СѓР¶Рµ ID)
    curr_prev = topology_info.get("effective_prev_rc")   # ID РёР»Рё None
    curr_next = topology_info.get("effective_next_rc")   # ID РёР»Рё None
    
    # РџСЂРѕРІРµСЂСЏРµРј СЃРјРµРЅСѓ С‚РѕРїРѕР»РѕРіРёРё
    if check_topology_change(det_state, curr_prev, curr_next):
        reset_formation_phases(det_state)
    
    det_state.last_effective_prev = curr_prev
    det_state.last_effective_next = curr_next
    
     # Р¤РѕСЂРјРёСЂСѓРµРј rc_capabilities
    rc_capabilities = {}
    if station_model:
        for rc_id, node in station_model.rc_nodes.items():
            rc_capabilities[rc_id] = {
                'can_lock': node.can_lock,
                'is_endpoint': node.is_endpoint,
                'allowed_detectors': node.allowed_detectors,      # LZ
                'allowed_ls_detectors': node.allowed_ls_detectors,  # в†ђ РќРћР’РћР•: LS
                'task_lz_number': node.task_lz_number,              # в†ђ РќРћР’РћР•
                'task_ls_number': node.task_ls_number,              # в†ђ РќРћР’РћР•
            }
    else:
        # Fallback вЂ” Р±РµСЂС‘Рј РЅР°РїСЂСЏРјСѓСЋ РёР· RC_CAPABILITIES
        from station.station_capabilities import RC_CAPABILITIES
        rc_capabilities = {
            rc_id: {
                'can_lock': caps.get('can_lock', True),
                'is_endpoint': caps.get('is_endpoint', False),
                'allowed_detectors': caps.get('allowed_detectors', []),
                'allowed_ls_detectors': caps.get('allowed_ls_detectors', []),  # в†ђ РќРћР’РћР•
                'task_lz_number': caps.get('task_lz_number'),                   # в†ђ РќРћР’РћР•
                'task_ls_number': caps.get('task_ls_number'),                   # в†ђ РќРћР’РћР•
            }
            for rc_id, caps in RC_CAPABILITIES.items()
        }


    # === РРЎРџР РђР’Р›Р•РќРћ: РїРµСЂРµРґР°С‘Рј rc_states_by_id ===
    step_adapter = _StepAdapter(
        rc_states=rc_states_by_id,      # в†ђ Р‘Р«Р›Рћ: rc_states
        rc_capabilities=rc_capabilities,
        modes=modes,
        signal_states=signal_states,
        effective_prev_rc=curr_prev,     # ID
        effective_next_rc=curr_next,     # ID
        ctrl_rc_name=cfg.ctrl_rc_id,     # ID (РїРµСЂРµРёРјРµРЅРѕРІР°С‚СЊ РІ ctrl_rc_id?)
    )
    
    # РћР±РЅРѕРІР»СЏРµРј РєР°Р¶РґС‹Р№ Р°РєС‚РёРІРЅС‹Р№ РґРµС‚РµРєС‚РѕСЂ
    variants_active = []

    def _capture_offsets(det: Any, opened: bool, closed: bool) -> None:
        if opened:
            off = getattr(det, "last_open_offset", None)
            if off is not None:
                foff = float(off)
                if result.open_offset is None or foff < result.open_offset:
                    result.open_offset = foff
        if closed:
            off = getattr(det, "last_close_offset", None)
            if off is not None:
                foff = float(off)
                if result.close_offset is None or foff < result.close_offset:
                    result.close_offset = foff
    
    # v1
    if det_state.v1:
        opened, closed = det_state.v1.update(step_adapter, dt)
        _capture_offsets(det_state.v1, opened, closed)
        if opened:
            result.opened = True
            result.flags.append("llz_v1_open")
        if closed:
            result.closed = True
            result.flags.append("llz_v1_closed")
        if det_state.v1.active:
            variants_active.append(1)
    
    # v2
    if det_state.v2:
        opened, closed = det_state.v2.update(step_adapter, dt)
        _capture_offsets(det_state.v2, opened, closed)
        if opened:
            result.opened = True
            result.flags.append("llz_v2_open")
        if closed:
            result.closed = True
            result.flags.append("llz_v2_closed")
        if det_state.v2.active:
            variants_active.append(2)
    
    # v3
    if det_state.v3:
        opened, closed = det_state.v3.update(step_adapter, dt)
        _capture_offsets(det_state.v3, opened, closed)
        if opened:
            result.opened = True
            result.flags.append("llz_v3_open")
        if closed:
            result.closed = True
            result.flags.append("llz_v3_closed")
        if det_state.v3.active:
            variants_active.append(3)

    # v4
    if det_state.v4:
        opened, closed = det_state.v4.update(step_adapter, dt)
        _capture_offsets(det_state.v4, opened, closed)
        if opened:
            result.opened = True
            result.lz4_open = True
        if closed:
            result.closed = True
            result.lz4_closed = True
        if det_state.v4.active:
            variants_active.append(4)

    # v5
    if det_state.v5:
        opened, closed = det_state.v5.update(step_adapter, dt)
        _capture_offsets(det_state.v5, opened, closed)
        if opened:
            result.opened = True
            result.flags.append("llz_v5_open")
        if closed:
            result.closed = True
            result.flags.append("llz_v5_closed")
        if det_state.v5.active:
            variants_active.append(5)

    if det_state.v6:
        opened, closed = det_state.v6.update(step_adapter, dt)
        _capture_offsets(det_state.v6, opened, closed)
        if opened:
            result.flags.append("llz_v6_open")
        if closed:
            result.flags.append("llz_v6_closed")
        if det_state.v6.active:
            variants_active.append(6)
    
    # v7
    if det_state.v7:
        opened, closed = det_state.v7.update(step_adapter, dt)
        _capture_offsets(det_state.v7, opened, closed)
        if opened:
            result.opened = True
            result.flags.append("llz_v7_open")
        if closed:
            result.closed = True
            result.flags.append("llz_v7_closed")
        if det_state.v7.active:
            variants_active.append(7)
    
    # v8
    if det_state.v8:
        opened, closed = det_state.v8.update(step_adapter, dt)
        _capture_offsets(det_state.v8, opened, closed)
        if opened:
            result.opened = True
            result.flags.append("llz_v8_open")
        if closed:
            result.closed = True
            result.flags.append("llz_v8_closed")
        if det_state.v8.active:
            variants_active.append(8)
    
    # LS9
    if det_state.ls9:
        opened, closed = det_state.ls9.update(step_adapter, dt)
        _capture_offsets(det_state.ls9, opened, closed)
        if opened:
            result.opened = True
            result.flags.append("lls_9_open")
        if closed:
            result.closed = True
            result.flags.append("lls_9_closed")
        if det_state.ls9.active:
            variants_active.append(109)  # LS9 = 100 + 9
    
    # LS1
    if det_state.ls1:
        opened, closed = det_state.ls1.update(step_adapter, dt)
        _capture_offsets(det_state.ls1, opened, closed)
        if opened:
            result.opened = True
            result.flags.append("lls_1_open")
        if closed:
            result.closed = True
            result.flags.append("lls_1_closed")
        if det_state.ls1.active:
            variants_active.append(101)  # LS1 = 100 + 1

    # LS2
    if det_state.ls2:
        opened, closed = det_state.ls2.update(step_adapter, dt)
        _capture_offsets(det_state.ls2, opened, closed)
        if opened:
            result.opened = True
            result.flags.append("lls_2_open")
        if closed:
            result.closed = True
            result.flags.append("lls_2_closed")
        if det_state.ls2.active:
            # LS2 РјРѕР¶РµС‚ РёРјРµС‚СЊ РЅРµСЃРєРѕР»СЊРєРѕ Р°РєС‚РёРІРЅС‹С… РІРµС‚РѕРє РІ РѕР±РµСЂС‚РєРµ, 
            # РЅРѕ РјС‹ РїСЂРѕСЃС‚Рѕ РїРѕРјРµС‡Р°РµРј С‡С‚Рѕ РІР°СЂРёР°РЅС‚ 102 Р°РєС‚РёРІРµРЅ
            variants_active.append(102)

    # LS4
    if det_state.ls4:
        opened, closed = det_state.ls4.update(step_adapter, dt)
        _capture_offsets(det_state.ls4, opened, closed)
        if opened:
            result.opened = True
            result.flags.append("lls_4_open")
        if closed:
            result.closed = True
            result.flags.append("lls_4_closed")
        if det_state.ls4.active:
            variants_active.append(104)

    # LS5
    if det_state.ls5:
        opened, closed = det_state.ls5.update(step_adapter, dt)
        _capture_offsets(det_state.ls5, opened, closed)
        if opened: result.ls5_open = True
        if closed: result.ls5_closed = True
        if det_state.ls5.active:
            variants_active.append(105)
    
    # LZ9
    if det_state.lz9:
        opened, closed = det_state.lz9.update(step_adapter, dt)
        _capture_offsets(det_state.lz9, opened, closed)
        if opened: result.lz9_open = True
        if closed: result.lz9_closed = True
        if det_state.lz9.active:
            variants_active.append(9)

    # LZ12
    if det_state.lz12:
        opened, closed = det_state.lz12.update(step_adapter, dt)
        _capture_offsets(det_state.lz12, opened, closed)
        if opened: result.lz12_open = True
        if closed: result.lz12_closed = True
        if det_state.lz12.active:
            variants_active.append(12)

    # LZ11
    if det_state.lz11:
        opened, closed = det_state.lz11.update(step_adapter, dt)
        _capture_offsets(det_state.lz11, opened, closed)
        if opened: result.lz11_open = True
        if closed: result.lz11_closed = True
        if det_state.lz11.active:
            variants_active.append(11)

    # LZ13
    if det_state.lz13:
        opened, closed = det_state.lz13.update(step_adapter, dt)
        _capture_offsets(det_state.lz13, opened, closed)
        if opened: result.lz13_open = True
        if closed: result.lz13_closed = True
        if det_state.lz13.active:
            variants_active.append(13)

    # LZ10
    if det_state.lz10:
        opened, closed = det_state.lz10.update(step_adapter, dt)
        _capture_offsets(det_state.lz10, opened, closed)
        if opened: result.lz10_open = True
        if closed: result.lz10_closed = True
        if det_state.lz10.active:
            variants_active.append(10)

    # LS6
    if det_state.ls6:
        opened, closed = det_state.ls6.update(step_adapter, dt)
        _capture_offsets(det_state.ls6, opened, closed)
        if opened: result.ls6_open = True
        if closed: result.ls6_closed = True
        if det_state.ls6.active:
            variants_active.append(106)
    
    # РћРїСЂРµРґРµР»СЏРµРј Р°РєС‚РёРІРЅС‹Р№ РІР°СЂРёР°РЅС‚ (РїСЂРёРѕСЂРёС‚РµС‚: LS (100+) > LZ)
    if variants_active:
        result.active_variant = max(variants_active)
    
    return det_state, result


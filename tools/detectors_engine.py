"""
detectors_engine.py — движок детекторов с поддержкой динамической топологии.

Версия: 2.0 (динамическая топология + сброс при смене соседей)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from station_config import NODES
from station_capabilities import RC_CAPABILITIES
from station_model import load_station_from_config, StationModel

from base_detector import BaseDetector, DetectorConfig, PhaseConfig, CompletionMode
from variant1_lz_factory import make_lz1_detector
from variant2_lz_factory import make_lz2_detector
from variant3_lz_factory import make_lz3_detector
from variant5_lz_factory import make_lz5_detector
from variant6_lz_factory import make_lz6_detector
from variant7_lz_factory import make_lz7_detector
from variant8_lz_factory import make_lz8_detector
from variant_ls9_lz_factory import make_ls9_detector
from variant_ls1_lz_factory import make_ls1_detector
from variant_ls2_lz_factory import make_ls2_detector
from variant_ls4_lz_factory import make_ls4_detector
from variant_ls5_lz_factory import make_ls5_detector
from variant_lz9_lz_factory import make_lz9_detector
from variant_lz12_lz_factory import make_lz12_detector
from variant_lz11_lz_factory import make_lz11_detector
from variant_lz13_lz_factory import make_lz13_detector
from variant_lz10_lz_factory import make_lz10_detector
from variant_ls6_lz_factory import make_ls6_detector


@dataclass
class DetectorsConfig:
    """Конфигурация детекторов для одной контролируемой РЦ."""
    ctrl_rc_id: str
    prev_rc_name: Optional[str] = ""
    ctrl_rc_name: str = ""
    next_rc_name: Optional[str] = ""
    
    # v1
    ts01_lz1: float = 0.0
    tlz_lz1: float = 0.0
    tkon_lz1: float = 0.0
    enable_lz1: bool = False
    
    # v2
    ts01_lz2: float = 0.0
    ts02_lz2: float = 0.0
    tlz_lz2: float = 0.0
    tkon_lz2: float = 0.0
    enable_lz2: bool = False
    
    # v3
    ts01_lz3: float = 0.0
    ts02_lz3: float = 0.0
    tlz_lz3: float = 0.0
    tkon_lz3: float = 0.0
    enable_lz3: bool = False

    # v5
    ts01_lz5: float = 0.0
    tlz_lz5: float = 0.0
    tkon_lz5: float = 0.0
    enable_lz5: bool = False

    # v6
    ts01_lz6: float = 0.0
    tlz_lz6: float = 0.0
    tkon_lz6: float = 0.0
    enable_lz6: bool = False
    
    # v7
    ts01_lz7: float = 0.0
    tlz_lz7: float = 0.0
    tkon_lz7: float = 0.0
    enable_lz7: bool = False
    
    # v8
    ts01_lz8: float = 0.0
    ts02_lz8: float = 0.0
    tlz_lz8: float = 0.0
    tkon_lz8: float = 0.0
    enable_lz8: bool = False
    
    # LS9
    ts01_ls9: float = 0.0
    tlz_ls9: float = 0.0
    tkon_ls9: float = 0.0
    enable_ls9: bool = False
    
    # LS1
    ts01_ls1: float = 0.0
    tlz_ls1: float = 0.0
    tkon_ls1: float = 0.0
    enable_ls1: bool = False
    
    # LS2
    ts01_ls2: float = 0.0
    tlz_ls2: float = 0.0
    ts02_ls2: float = 0.0
    tkon_ls2: float = 0.0
    enable_ls2: bool = False
    
    # LS4
    ts01_ls4: float = 0.0
    tlz01_ls4: float = 0.0
    tlz02_ls4: float = 0.0
    tkon_ls4: float = 0.0
    enable_ls4: bool = False
    
    # LS5
    ts01_ls5: float = 0.0
    tlz_ls5: float = 0.0
    tkon_ls5: float = 0.0
    enable_ls5: bool = False

    # LZ9
    enable_lz9: bool = False
    ts01_lz9: float = 0.0
    tlz_lz9: float = 0.0
    tkon_lz9: float = 0.0
    
    # LZ12
    enable_lz12: bool = False
    ts01_lz12: float = 0.0
    tlz_lz12: float = 0.0
    tkon_lz12: float = 0.0

    # LZ11
    enable_lz11: bool = False
    ts01_lz11: float = 0.0
    tlz_lz11: float = 0.0
    tkon_lz11: float = 0.0
    sig_lz11_a: Optional[str] = None
    sig_lz11_b: Optional[str] = None

    # LZ13
    enable_lz13: bool = False
    ts01_lz13: float = 0.0
    ts02_lz13: float = 0.0
    tlz_lz13: float = 0.0
    tkon_lz13: float = 0.0
    sig_lz13_prev: Optional[str] = None
    sig_lz13_next: Optional[str] = None

    # LZ10
    enable_lz10: bool = False
    ts01_lz10: float = 0.0
    ts02_lz10: float = 0.0
    ts03_lz10: float = 0.0
    tlz_lz10: float = 0.0
    tkon_lz10: float = 0.0
    sig_lz10_to_next: Optional[str] = None
    sig_lz10_to_prev: Optional[str] = None

    # LS6
    enable_ls6: bool = False
    ts01_ls6: float = 0.0
    tlz_ls6: float = 0.0
    tkon_ls6: float = 0.0
    sig_ls6_prev: Optional[str] = None


@dataclass
class DetectorsState:
    """Состояние всех детекторов для одной контролируемой РЦ."""
    # Детекторы
    v1: Optional[BaseDetector] = None
    v2: Optional[Any] = None  # Variant2Wrapper
    v3: Optional[BaseDetector] = None
    v5: Optional[BaseDetector] = None
    v6: Optional[BaseDetector] = None
    v7: Optional[Any] = None  # Variant7Wrapper
    v8: Optional[Any] = None  # Variant8Wrapper
    ls9: Optional[BaseDetector] = None
    ls1: Optional[BaseDetector] = None
    ls2: Optional[Any] = None # Wrapper
    ls4: Optional[BaseDetector] = None
    ls5: Optional[Any] = None # Wrapper for LS5
    lz9: Optional[Any] = None
    lz12: Optional[Any] = None
    lz11: Optional[Any] = None
    lz13: Optional[Any] = None
    lz10: Optional[Any] = None
    ls6: Optional[Any] = None
    
    # Служебные поля
    last_effective_prev: Optional[str] = None
    last_effective_next: Optional[str] = None


@dataclass
class DetectorsResult:
    """Результат обновления детекторов."""
    opened: bool = False
    closed: bool = False
    ls5_open: bool = False
    ls5_closed: bool = False
    lz9_open: bool = False
    lz9_closed: bool = False
    lz12_open: bool = False
    lz12_closed: bool = False
    lz11_open: bool = False
    lz11_closed: bool = False
    lz13_open: bool = False
    lz13_closed: bool = False
    lz10_open: bool = False
    lz10_closed: bool = False
    ls6_open: bool = False
    ls6_closed: bool = False
    active_variant: int = 0
    flags: List[str] = field(default_factory=list)


@dataclass
class _StepAdapter:
    """
    Адаптер для передачи данных в BaseDetector.
    
    ДИНАМИЧЕСКАЯ ТОПОЛОГИЯ:
    - effective_prev_rc / effective_next_rc приходят из topology_manager
    """
    rc_states: Dict[str, int]  # ТЕПЕРЬ: по ID, не по именам!
    modes: Dict[str, Any]
    signal_states: Dict[str, int]
    effective_prev_rc: Optional[str]  # ID
    effective_next_rc: Optional[str]  # ID
    ctrl_rc_name: str
    rc_capabilities: Dict[str, Dict] = field(default_factory=dict)


def init_detectors_engine(cfg: DetectorsConfig, rc_ids: List[str]) -> DetectorsState:
    """Инициализация детекторов по конфигурации."""
    state = DetectorsState()
    
    # rc_capabilities needed for LS5, LZ9, LZ12 initialization
    rc_capabilities = {}
    # This part is duplicated from update_detectors, but needed here for init
    # In a real system, this might be passed in or loaded once.
    from station_capabilities import RC_CAPABILITIES
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
    
    return state


def check_topology_change(
    state: DetectorsState,
    curr_prev: Optional[str],
    curr_next: Optional[str],
) -> bool:
    """
    Проверяет, изменилась ли топология (соседи) по сравнению с прошлым шагом.
    
    :return: True если соседи изменились (включая None)
    """
    # Сравниваем prev
    prev_changed = state.last_effective_prev != curr_prev
    
    # Сравниваем next
    next_changed = state.last_effective_next != curr_next
    
    return prev_changed or next_changed


def reset_formation_phases(state: DetectorsState) -> None:
    """
    Сбрасывает фазы формирования всех неактивных детекторов.
    
    Активные детекторы (открытые ДС) продолжают работу до закрытия по t_kon.
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
    """Проверяет, являются ли ключи rc_states уже ID."""
    if not rc_states:
        return True
    first_key = next(iter(rc_states.keys()))
    return first_key in NODES  # если в NODES — это ID

from typing import Dict
from functools import lru_cache

@lru_cache(maxsize=1)
def _get_name_to_id() -> Dict[str, str]:
    """Кэшированный маппинг имён в ID."""
    from station_config import NODES
    return {node["name"]: nid for nid, node in NODES.items() if node.get("name")}


def _ensure_rc_states_by_id(rc_states: Dict[str, int]) -> Dict[str, int]:
    """Конвертирует rc_states в формат по ID если нужно."""
    if not rc_states:
        return {}
    
    sample_key = next(iter(rc_states.keys()))
    
    # Проверяем: это ID уже?
    from station_config import NODES
    if sample_key in NODES:
        return rc_states  # уже ID
    
    # Конвертируем имена в ID
    name_to_id = _get_name_to_id()
    return {name_to_id.get(k, k): v for k, v in rc_states.items()}

def update_detectors(
    det_state: DetectorsState,
    t: float,
    dt: float,
    rc_states: Dict[str, int],  # ← может быть имена или ID
    switch_states: Dict[str, int],
    signal_states: Dict[str, int],
    topology_info: Dict[str, Any],
    cfg: DetectorsConfig,
    modes: Dict[str, Any],
    station_model:  Optional['StationModel'] = None,
) -> Tuple[DetectorsState, DetectorsResult]:
    """
    Обновляет все детекторы на одном шаге.
    rc_states: ключи — имена или ID (автоопределение)
    """
    result = DetectorsResult()

    # === КОНВЕРТАЦИЯ rc_states в ID ===
    from station_config import NODES
    
    # Кэш маппинга (для C: статическая таблица)
    name_to_id = {node["name"]: nid for nid, node in NODES.items() if node.get("name")}
    
    # Определяем формат: проверяем первый ключ
    sample_key = next(iter(rc_states.keys())) if rc_states else ""
    is_already_ids = sample_key in NODES
    
    
    rc_states_by_id = _ensure_rc_states_by_id(rc_states)
    
    # Получаем соседей из топологии (уже ID)
    curr_prev = topology_info.get("effective_prev_rc")   # ID или None
    curr_next = topology_info.get("effective_next_rc")   # ID или None
    
    # Проверяем смену топологии
    if check_topology_change(det_state, curr_prev, curr_next):
        reset_formation_phases(det_state)
    
    det_state.last_effective_prev = curr_prev
    det_state.last_effective_next = curr_next
    
     # Формируем rc_capabilities
    rc_capabilities = {}
    if station_model:
        for rc_id, node in station_model.rc_nodes.items():
            rc_capabilities[rc_id] = {
                'can_lock': node.can_lock,
                'is_endpoint': node.is_endpoint,
                'allowed_detectors': node.allowed_detectors,      # LZ
                'allowed_ls_detectors': node.allowed_ls_detectors,  # ← НОВОЕ: LS
                'task_lz_number': node.task_lz_number,              # ← НОВОЕ
                'task_ls_number': node.task_ls_number,              # ← НОВОЕ
            }
    else:
        # Fallback — берём напрямую из RC_CAPABILITIES
        from station_capabilities import RC_CAPABILITIES
        rc_capabilities = {
            rc_id: {
                'can_lock': caps.get('can_lock', True),
                'is_endpoint': caps.get('is_endpoint', False),
                'allowed_detectors': caps.get('allowed_detectors', []),
                'allowed_ls_detectors': caps.get('allowed_ls_detectors', []),  # ← НОВОЕ
                'task_lz_number': caps.get('task_lz_number'),                   # ← НОВОЕ
                'task_ls_number': caps.get('task_ls_number'),                   # ← НОВОЕ
            }
            for rc_id, caps in RC_CAPABILITIES.items()
        }


    # === ИСПРАВЛЕНО: передаём rc_states_by_id ===
    step_adapter = _StepAdapter(
        rc_states=rc_states_by_id,      # ← БЫЛО: rc_states
        rc_capabilities=rc_capabilities,
        modes=modes,
        signal_states=signal_states,
        effective_prev_rc=curr_prev,     # ID
        effective_next_rc=curr_next,     # ID
        ctrl_rc_name=cfg.ctrl_rc_id,     # ID (переименовать в ctrl_rc_id?)
    )
    
    # Обновляем каждый активный детектор
    variants_active = []
    
    # v1
    if det_state.v1:
        opened, closed = det_state.v1.update(step_adapter, dt)
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
        if opened:
            result.opened = True
            result.flags.append("llz_v3_open")
        if closed:
            result.closed = True
            result.flags.append("llz_v3_closed")
        if det_state.v3.active:
            variants_active.append(3)

    # v5
    if det_state.v5:
        opened, closed = det_state.v5.update(step_adapter, dt)
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
        if opened:
            result.flags.append("llz_v6_open")
        if closed:
            result.flags.append("llz_v6_closed")
        if det_state.v6.active:
            variants_active.append(6)
    
    # v7
    if det_state.v7:
        opened, closed = det_state.v7.update(step_adapter, dt)
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
        if opened:
            result.opened = True
            result.flags.append("lls_2_open")
        if closed:
            result.closed = True
            result.flags.append("lls_2_closed")
        if det_state.ls2.active:
            # LS2 может иметь несколько активных веток в обертке, 
            # но мы просто помечаем что вариант 102 активен
            variants_active.append(102)

    # LS4
    if det_state.ls4:
        opened, closed = det_state.ls4.update(step_adapter, dt)
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
        if opened: result.ls5_open = True
        if closed: result.ls5_closed = True
        if det_state.ls5.active:
            variants_active.append(105)
    
    # LZ9
    if det_state.lz9:
        opened, closed = det_state.lz9.update(step_adapter, dt)
        if opened: result.lz9_open = True
        if closed: result.lz9_closed = True
        if det_state.lz9.active:
            variants_active.append(9)

    # LZ12
    if det_state.lz12:
        opened, closed = det_state.lz12.update(step_adapter, dt)
        if opened: result.lz12_open = True
        if closed: result.lz12_closed = True
        if det_state.lz12.active:
            variants_active.append(12)

    # LZ11
    if det_state.lz11:
        opened, closed = det_state.lz11.update(step_adapter, dt)
        if opened: result.lz11_open = True
        if closed: result.lz11_closed = True
        if det_state.lz11.active:
            variants_active.append(11)

    # LZ13
    if det_state.lz13:
        opened, closed = det_state.lz13.update(step_adapter, dt)
        if opened: result.lz13_open = True
        if closed: result.lz13_closed = True
        if det_state.lz13.active:
            variants_active.append(13)

    # LZ10
    if det_state.lz10:
        opened, closed = det_state.lz10.update(step_adapter, dt)
        if opened: result.lz10_open = True
        if closed: result.lz10_closed = True
        if det_state.lz10.active:
            variants_active.append(10)

    # LS6
    if det_state.ls6:
        opened, closed = det_state.ls6.update(step_adapter, dt)
        if opened: result.ls6_open = True
        if closed: result.ls6_closed = True
        if det_state.ls6.active:
            variants_active.append(106)
    
    # Определяем активный вариант (приоритет: LS (100+) > LZ)
    if variants_active:
        result.active_variant = max(variants_active)
    
    return det_state, result
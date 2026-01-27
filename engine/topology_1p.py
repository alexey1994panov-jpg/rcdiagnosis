from typing import Tuple, Optional, Dict
from dataclasses import dataclass

from .station_visochino_1p import (
    StationModel1P,
    sw_is_plus,
    rc_no_control,
)
from .config_1p import T_PK
from .types_1p import ScenarioStep


# --- RC topology (расширенная) ---


@dataclass(frozen=True)
class RcNode:
    rc_id: str
    # кандидаты слева/справа, в терминах id РЦ (аналог PrevSec/NextSec из XML)
    prev_candidates: Tuple[str, ...]
    next_candidates: Tuple[str, ...]
    # имена стрелок, которые должны быть "плюс", чтобы связь была активна
    prev_switches: Tuple[str, ...]
    next_switches: Tuple[str, ...]


# словарь топологии для участка 1АП – 10-12SP – 1P – 1-7SP – НП и развязок 3П/3СП
RC_TOPOLOGY_1P: Dict[str, RcNode] = {
    # === Основной участок ===
    
    # 1П — бесстрелочная, хранит только отношения к секциям
    "1P": RcNode(
        rc_id="1P",
        prev_candidates=("10-12SP",),
        next_candidates=("1-7SP",),
        prev_switches=("Sw10",),
        next_switches=("Sw1", "Sw5"),
    ),
    
    # 10-12СП — знает следующую секцию и стрелку 10, которая в неё входит
    "10-12SP": RcNode(
        rc_id="10-12SP",
        prev_candidates=("1AP",),
        next_candidates=("1P",),
        prev_switches=(),
        next_switches=("Sw10",),
    ),
    
    # 1-7СП — знает предыдущую секцию (НП) и стрелки 1 и 5, входящие в неё
    "1-7SP": RcNode(
        rc_id="1-7SP",
        prev_candidates=("NP",),
        next_candidates=("1P",),
        prev_switches=(),
        next_switches=("Sw1", "Sw5"),
    ),
    
    # === Расширение: соседние РЦ ===
    
    # 1АП — предыдущая РЦ перед 10-12СП
    # PrevSec: пока не известен (оставляем пустым)
    # NextSec: 10-12СП
    # Смежность определяется стрелкой Sw10 (по XML: PrevSec=1АП, SwSection=10-12СП)
    "1AP": RcNode(
        rc_id="1AP",
        prev_candidates=(),
        next_candidates=("10-12SP",),
        prev_switches=(),
        next_switches=("Sw10",),
    ),
    
    # НП (НеПоименованная) — предыдущая РЦ перед 1-7СП
    # PrevSec: пока не известен (оставляем пустым)
    # NextSec: 1-7СП
    # Смежность определяется стрелкой Sw1 (по XML: PrevSec=НП, SwSection=1-7СП)
    "NP": RcNode(
        rc_id="NP",
        prev_candidates=(),
        next_candidates=("1-7SP",),
        prev_switches=(),
        next_switches=("Sw1",),
    ),
    
    # 3П — развязка (тупик по минусу для стрелок Sw10 и Sw5)
    # По XML: NextMi=3П (промежуточная секция при минусовом направлении стрелок)
    # Пока только заглушка — нет известных связей
    "3P": RcNode(
        rc_id="3P",
        prev_candidates=(),
        next_candidates=(),
        prev_switches=(),
        next_switches=(),
    ),
    
    # 3СП — развязка (по плюсу для стрелки Sw1)
    # По XML: NextMi=3СП (промежуточная секция при плюсовом направлении стрелки 1)
    # Пока только заглушка — нет известных связей
    "3SP": RcNode(
        rc_id="3SP",
        prev_candidates=(),
        next_candidates=(),
        prev_switches=(),
        next_switches=(),
    ),
}


# --- Sw topology (соответствует XML) ---


@dataclass(frozen=True)
class SwNode:
    """
    Узел стрелки по XML:
      - sw_id        — идентификатор стрелки (SwID);
      - sw_section   — секция (РЦ), к которой относится стрелка (SwSection);
      - prev_sec     — секция/РЦ слева (PrevSec или PrevSw-цепочка), если есть;
      - plus_sections  — секции/РЦ по плюсу;
      - minus_sections — секции/РЦ по минусу;
      - transit_sections — транзитные/проходные секции (NextMi, промежуточные и т.п.).
    """
    sw_id: str
    sw_section: str
    prev_sec: Optional[str]
    plus_sections: Tuple[str, ...]
    minus_sections: Tuple[str, ...] = ()
    transit_sections: Tuple[str, ...] = ()


SW_TOPOLOGY_1P: Dict[str, SwNode] = {
    # Стрелка 10:
    #   PrevSec   = 1АП
    #   SwSection = 10-12СП
    #   NextMi    = 3П
    #   NextPl    = 1П
    "Sw10": SwNode(
        sw_id="Sw10",
        sw_section="10-12SP",
        prev_sec="1AP",
        plus_sections=("1P",),      # по плюсу из 10-12СП в 1П
        minus_sections=("3P",),     # по минусу в 3П
    ),

    # Стрелка 1:
    #   PrevSec   = НП
    #   SwSection = 1-7СП
    #   NextMi    = 3СП
    #   NextSwPl  = 5 (цепочка на стрелку 5, пока не моделируем)
    "Sw1": SwNode(
        sw_id="Sw1",
        sw_section="1-7SP",
        prev_sec="NP",
        plus_sections=("3SP",),     # по плюсу в 3СП
        minus_sections=(),          # минус идёт на стрелку 5 (цепочка, пока не моделируем)
    ),

    # Стрелка 5:
    #   SwSection = 1-7СП
    #   PrevSw    = 1 (цепочка стрелок, пока не моделируем)
    #   NextMi    = 3П
    #   NextPl    = 1П
    "Sw5": SwNode(
        sw_id="Sw5",
        sw_section="1-7SP",
        prev_sec=None,              # PrevSw = 1, цепочка стрелок
        plus_sections=("1P",),      # по плюсу в 1П
        minus_sections=("3P",),     # по минусу в 3П
    ),
}


# --- Local adjacency (как было) ---


@dataclass
class LocalAdjacency:
    prev_rc_id: Optional[str]
    next_rc_id: Optional[str]
    prev_state: int
    next_state: int
    prev_nc: bool
    next_nc: bool


class AdjacencyState:
    def __init__(self) -> None:
        self.latched_prev: str = ""
        self.latched_next: str = ""
        self.time_since_prev_lost: Optional[float] = None
        self.time_since_next_lost: Optional[float] = None


def compute_local_adjacency(
    station: StationModel1P,
    step: ScenarioStep,
    ctrl_rc_id: str,
) -> LocalAdjacency:
    """
    Локальная смежность для заданной ctrl_rc_id на участке 10-12SP–1P–1-7SP.

    Используется per-РЦ вариантами (v4/v12/v13 и т.п.).
    
    Функция не изменена — использует RC_TOPOLOGY_1P как раньше.
    """
    rc_states = step.rc_states or {}
    sw = step.switch_states or {}

    node = RC_TOPOLOGY_1P.get(ctrl_rc_id)

    # если нет описания в топологии — ведём себя как раньше в "else"
    if node is None:
        prev_rc_id = None
        next_rc_id = None
        st_prev = 0
        st_next = 0
    else:
        # базовые кандидаты слева/справа из топологии
        prev_rc_id = node.prev_candidates[0] if node.prev_candidates else None
        next_rc_id = node.next_candidates[0] if node.next_candidates else None

        # состояние "слева"
        if prev_rc_id is None:
            st_prev = 0
        else:
            if not node.prev_switches:
                # чистая секция-секция, без стрелок
                st_prev = rc_states.get(prev_rc_id, 0)
            else:
                # все стрелки должны быть "плюс"
                if all(sw_is_plus(sw.get(sw_name, 0)) for sw_name in node.prev_switches):
                    st_prev = rc_states.get(prev_rc_id, 0)
                else:
                    st_prev = 0

        # состояние "справа"
        if next_rc_id is None:
            st_next = 0
        else:
            if not node.next_switches:
                st_next = rc_states.get(next_rc_id, 0)
            else:
                if all(sw_is_plus(sw.get(sw_name, 0)) for sw_name in node.next_switches):
                    st_next = rc_states.get(next_rc_id, 0)
                else:
                    st_next = 0

    prev_nc = rc_no_control(st_prev)
    next_nc = rc_no_control(st_next)

    return LocalAdjacency(
        prev_rc_id=prev_rc_id,
        next_rc_id=next_rc_id,
        prev_state=st_prev,
        next_state=st_next,
        prev_nc=prev_nc,
        next_nc=next_nc,
    )


def update_adjacency(
    state: AdjacencyState,
    station: StationModel1P,
    step: ScenarioStep,
    dt_interval: float,
) -> Tuple[str, str, bool, bool]:
    """
    Старый интерфейс для глобальной ctrl_rc_id (1P/10-12SP/1-7SP).
    Оставляем, как есть, для v1–v3, UI и т.п.
    
    Функция не изменена — использует только RcNode для существующих РЦ.
    """
    modes = getattr(step, "modes", {}) or {}
    ctrl_rc_id = modes.get("ctrl_rc_id", station.ctrl_rc_id)

    if ctrl_rc_id == "1P":
        prev_candidates = station.prev_candidates
        next_candidates = station.next_candidates
        sw_prev_state = step.switch_states.get("Sw10", 0)
        sw_next1_state = step.switch_states.get("Sw1", 0)
        sw_next5_state = step.switch_states.get("Sw5", 0)
        sw_prev_plus = sw_is_plus(sw_prev_state)
        sw_next_ok = sw_is_plus(sw_next1_state) and sw_is_plus(sw_next5_state)
    elif ctrl_rc_id == "10-12SP":
        prev_candidates = []
        next_candidates = ["1P"]
        sw_prev_plus = False
        sw_next1_state = step.switch_states.get("Sw10", 0)
        sw_next_ok = sw_is_plus(sw_next1_state)
    elif ctrl_rc_id == "1-7SP":
        prev_candidates = ["1P"]
        next_candidates = []
        sw_prev1_state = step.switch_states.get("Sw1", 0)
        sw_prev5_state = step.switch_states.get("Sw5", 0)
        sw_prev_plus = sw_is_plus(sw_prev1_state) and sw_is_plus(sw_prev5_state)
        sw_next_ok = False
    else:
        prev_candidates = station.prev_candidates
        next_candidates = station.next_candidates
        sw_prev_state = step.switch_states.get("Sw10", 0)
        sw_next1_state = step.switch_states.get("Sw1", 0)
        sw_next5_state = step.switch_states.get("Sw5", 0)
        sw_prev_plus = sw_is_plus(sw_prev_state)
        sw_next_ok = sw_is_plus(sw_next1_state) and sw_is_plus(sw_next5_state)

    # --- PREV ---
    if not prev_candidates:
        current_prev = ""
        state.latched_prev = ""
        state.time_since_prev_lost = None
    else:
        if sw_prev_plus:
            current_prev = prev_candidates[0]
            state.latched_prev = current_prev
            state.time_since_prev_lost = 0.0
        else:
            if state.latched_prev:
                if state.time_since_prev_lost is None:
                    state.time_since_prev_lost = dt_interval
                else:
                    state.time_since_prev_lost += dt_interval

                if state.time_since_prev_lost <= T_PK:
                    current_prev = state.latched_prev
                else:
                    current_prev = ""
            else:
                current_prev = ""

    # --- NEXT ---
    if not next_candidates:
        current_next = ""
        state.latched_next = ""
        state.time_since_next_lost = None
    else:
        if sw_next_ok:
            current_next = next_candidates[0]
            state.latched_next = current_next
            state.time_since_next_lost = 0.0
        else:
            if state.latched_next:
                if state.time_since_next_lost is None:
                    state.time_since_next_lost = dt_interval
                else:
                    state.time_since_next_lost += dt_interval

                if state.time_since_next_lost <= T_PK:
                    current_next = state.latched_next
                else:
                    current_next = ""
            else:
                current_next = ""

    prev_control_ok = bool(current_prev)
    next_control_ok = bool(current_next)
    return current_prev, current_next, prev_control_ok, next_control_ok

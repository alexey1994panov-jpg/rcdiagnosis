from typing import Tuple, Optional, Dict
from dataclasses import dataclass

from .station_visochino_1p import (
    StationModel1P,
    sw_is_plus,
    rc_no_control,
)
from .config_1p import T_PK
from .types_1p import ScenarioStep


@dataclass(frozen=True)
class RcNode:
    rc_id: str
    # кандидаты слева/справа, в терминах id РЦ (аналог PrevSec/NextSec из XML)
    prev_candidates: Tuple[str, ...]
    next_candidates: Tuple[str, ...]
    # имена стрелок, которые должны быть "плюс", чтобы связь была активна
    prev_switches: Tuple[str, ...]
    next_switches: Tuple[str, ...]


# минимальный словарь топологии для 10-12SP – 1P – 1-7SP
RC_TOPOLOGY_1P: Dict[str, RcNode] = {
    # 1П — бесстрелочная, хранит только отношения к секциям
    "1P": RcNode(
        rc_id="1P",
        prev_candidates=("10-12SP",),
        next_candidates=("1-7SP",),
        prev_switches=(),              # связь секция-секция
        next_switches=(),
    ),
    # 10-12СП — знает следующую секцию и стрелку 10, которая в неё входит
    "10-12SP": RcNode(
        rc_id="10-12SP",
        prev_candidates=(),            # позже здесь будет "1AP"
        next_candidates=("1P",),
        prev_switches=(),
        next_switches=("Sw10",),
    ),
    # 1-7СП — знает предыдущую секцию (НП) и стрелки 1 и 5, входящие в неё
    "1-7SP": RcNode(
        rc_id="1-7SP",
        prev_candidates=("NP",),       # пока формально, фактической НП ещё нет в модели
        next_candidates=(),
        prev_switches=("Sw1", "Sw5"),
        next_switches=(),
    ),
}


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
    """
    rc_states = step.rc_states or {}
    sw = step.switch_states or {}

    if ctrl_rc_id == "1P":
        # базовая логика: слева 10-12SP через Sw10, справа 1-7SP через Sw1+Sw5
        prev_rc_id = "10-12SP"
        next_rc_id = "1-7SP"

        sw10 = sw.get("Sw10", 0)
        sw1 = sw.get("Sw1", 0)
        sw5 = sw.get("Sw5", 0)

        st_prev = rc_states.get(prev_rc_id, 0) if sw_is_plus(sw10) else 0
        st_next = rc_states.get(next_rc_id, 0) if (sw_is_plus(sw1) and sw_is_plus(sw5)) else 0

    elif ctrl_rc_id == "10-12SP":
        # Относительно 10-12SP: слева край (NC), справа 1P по плюсу Sw10.
        prev_rc_id = None
        next_rc_id = "1P"

        sw10 = sw.get("Sw10", 0)
        st_prev = 0
        st_next = rc_states.get(next_rc_id, 0) if sw_is_plus(sw10) else 0

    elif ctrl_rc_id == "1-7SP":
        # Относительно 1-7SP: слева край (NC), справа 1P по плюсу Sw1+Sw5.
        prev_rc_id = None
        next_rc_id = "1P"

        sw1 = sw.get("Sw1", 0)
        sw5 = sw.get("Sw5", 0)
        st_prev = 0
        st_next = rc_states.get(next_rc_id, 0) if (sw_is_plus(sw1) and sw_is_plus(sw5)) else 0

    else:
        # дефолт: нет явной топологии — считаем края
        prev_rc_id = None
        next_rc_id = None
        st_prev = 0
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

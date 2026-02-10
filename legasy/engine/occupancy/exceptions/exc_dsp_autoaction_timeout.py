from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

from .base import LzException

if TYPE_CHECKING:
    from engine.station_visochino_1p import StationModel1P
    from engine.types_1p import ScenarioStep
    from engine.simulate_1p import TimelineStep


@dataclass
class DspAutoActionTimeoutConfig:
    # дефолт, если станция не задаёт своё время
    t_min_maneuver: float = 600.0  # Тмп, секунд


@dataclass
class DspAutoActionTimeoutException(LzException):
    """
    Исключение ЛЗ по варианту 8 при маневровых работах (ДСП + автодействие).

    ЛЗ по варианту 8 на контролируемой РЦ подавляется, если:

    1) Станция под управлением ДСП: dispatcher_control_state == 4.
    2) Для ctrl_rc_id есть автодействие и оно выключено (state in {0, 3}).
    3) ctrl_rc_id — приёмо-отправочный/главный путь (по main_rc_ids).
    4) ctrl_rc_id была непрерывно занята >= t_min_maneuver до текущего момента.
    """

    id: str = "dsp_autoaction_timeout"
    cfg: DspAutoActionTimeoutConfig = field(
        default_factory=DspAutoActionTimeoutConfig
    )

    def should_suppress(
        self,
        station: "StationModel1P",
        history: List["ScenarioStep"],
        idx: int,
        ctrl_rc_id: str,
        timeline: List["TimelineStep"],
    ) -> bool:
        if not (0 <= idx < len(history)):
            return False

        # 1. режим ДСП
        if not self._is_dsp_mode(station):
            return False

        # 2. автодействие по ctrl_rc_id есть и выключено
        if not self._is_auto_action_off(station, ctrl_rc_id):
            return False

        # 3. ctrl_rc_id — приёмо-отправочный / главный путь
        if not self._is_main_or_pa_path(station, ctrl_rc_id):
            return False

        # 4. ctrl_rc_id непрерывно занята >= t_min_maneuver до текущего момента
        t_now = sum(float(s.t) for s in history[: idx + 1])
        t_window = getattr(station, "t_min_maneuver_v8", self.cfg.t_min_maneuver)

        if not self._rc_occupied_continuously(
            history=history,
            rc_id=ctrl_rc_id,
            t_now=t_now,
            t_window=t_window,
        ):
            return False

        return True

    # --- вспомогательные проверки ---

    @staticmethod
    def _is_dsp_mode(station: "StationModel1P") -> bool:
        state_val = getattr(station, "dispatcher_control_state", 3)
        return state_val == 4

    @staticmethod
    def _is_auto_action_off(station: "StationModel1P", rc_id: str) -> bool:
        """
        Для ctrl_rc_id есть автодействие, и оно выключено.

        Выключенные состояния:
        - 0 (АС = 0);
        - 3 (АВ = 0 / режим «выключено»).
        """
        auto_actions = getattr(station, "auto_actions", []) or []
        for aa in auto_actions:
            aa_rc_ids = getattr(aa, "rc_ids", []) or []
            if rc_id not in aa_rc_ids:
                continue
            state = getattr(aa, "state", 4)
            if state in (0, 3):
                return True
        return False

    @staticmethod
    def _is_main_or_pa_path(station: "StationModel1P", rc_id: str) -> bool:
        """
        Проверка, что ctrl_rc_id относится к приёмо-отправочным / главным путям.

        Ожидается, что StationModel1P содержит:
        - список station.main_rc_ids (List[str]) или
        - словарь station.main_rc_by_id: Dict[str, bool].

        Если явной конфигурации нет, условие считаем невыполненным.
        """
        main_rc_ids = getattr(station, "main_rc_ids", None)
        if isinstance(main_rc_ids, list):
            return rc_id in main_rc_ids

        main_rc_by_id = getattr(station, "main_rc_by_id", None)
        if isinstance(main_rc_by_id, dict):
            return bool(main_rc_by_id.get(rc_id, False))

        return False

    @staticmethod
    def _rc_occupied_continuously(
        history: List["ScenarioStep"],
        rc_id: str,
        t_now: float,
        t_window: float,
    ) -> bool:
        """
        Проверяет, что РЦ rc_id была непрерывно занята (6/7/8)
        в интервале [t_now - t_window, t_now).
        """
        if not history or t_window <= 0.0:
            return False

        t_start = max(0.0, t_now - t_window)

        # идём вперёд по истории, накапливаем абсолютное время
        t_acc = 0.0
        for step in history:
            dt = float(step.t)
            t_next = t_acc + dt

            # интервал шага пересекается с интересующим окном?
            if t_next > t_start and t_acc < t_now:
                state_val = step.rc_states.get(rc_id, 0)
                if state_val not in (6, 7, 8):
                    # в окне встретилось состояние «не занято» -> непрерывности нет
                    return False

            t_acc = t_next
            if t_acc >= t_now:
                break

        # если мы дошли до t_now и не встретили свободное состояние в окне —
        # считаем, что весь интервал был занятым
        return t_now - t_start >= t_window

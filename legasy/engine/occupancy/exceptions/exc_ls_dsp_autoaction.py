from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

from .base import LsException

if TYPE_CHECKING:
    from engine.station_visochino_1p import StationModel1P
    from engine.types_1p import ScenarioStep
    from engine.simulate_1p import TimelineStep


@dataclass
class LsDspAutoActionConfig:
    """
    Настройки ДСП-исключения для ЛС.

    t_min_maneuver:
      минимальная длительность непрерывной занятости РЦ, при которой
      при активном режиме ДСП и отключённых автодействиях ЛС подавляется.
    """

    t_min_maneuver: float = 600.0


@dataclass
class LsDspAutoActionException(LsException):
    """
    Исключение ЛС по ДСП и автодействиям.

    Условия:
      1) dispatcher_control_state == 4;
      2) по контролируемой РЦ автодействия NAS/CHAS в состоянии 0 или 3;
      3) РЦ непрерывно занята в течение t_min_maneuver.
    """

    id: str = "ls_exc_dsp_autoaction"
    cfg: LsDspAutoActionConfig = field(default_factory=LsDspAutoActionConfig)

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

        if not self._is_dsp_mode(station):
            return False

        if not self._is_auto_action_off(station, ctrl_rc_id):
            return False

        t_now = sum(float(s.t) for s in history[: idx + 1])

        # сначала специализированный таймер для ЛС (t_ls_dsp),
        # затем общий t_min_maneuver_v8, затем дефолт из конфига
        t_window = getattr(
            station,
            "t_ls_dsp",
            getattr(station, "t_min_maneuver_v8", self.cfg.t_min_maneuver),
        )

        if not self._rc_occupied_continuously(history, ctrl_rc_id, t_now, t_window):
            return False

        return True

    @staticmethod
    def _is_dsp_mode(station: "StationModel1P") -> bool:
        state_val = getattr(station, "dispatcher_control_state", 3)
        return state_val == 4

    @staticmethod
    def _is_auto_action_off(station: "StationModel1P", rc_id: str) -> bool:
        """
        Проверка, что по данной РЦ автодействие выключено:
        state in {0, 3} для NAS/CHAS.
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
    def _rc_occupied_continuously(
        history: List["ScenarioStep"],
        rc_id: str,
        t_now: float,
        t_window: float,
    ) -> bool:
        """
        Проверка непрерывной занятости РЦ в интервале [t_now - t_window, t_now].

        Схема та же, что в DspAutoActionTimeoutException для ЛЗ:
        считаем, что состояние 6, 7, 8 — занято.
        """
        if not history or t_window <= 0.0:
            return False

        t_start = max(0.0, t_now - t_window)
        t_acc = 0.0

        for step in history:
            dt = float(step.t)
            t_next = t_acc + dt

            if t_next > t_start and t_acc <= t_now:
                state_val = int(step.rc_states.get(rc_id, 0))
                if state_val not in (6, 7, 8):
                    return False

            t_acc = t_next
            if t_acc >= t_now:
                break

        return (t_now - t_start) >= t_window

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

from .base import LzException

if TYPE_CHECKING:
    from engine.station_visochino_1p import StationModel1P
    from engine.types_1p import ScenarioStep
    from engine.simulate_1p import TimelineStep


@dataclass
class LocalMuConfig:
    # Тму, секунд: окно, в течение которого МУ считается «недавно активным»
    t_mu: float = 15.0


@dataclass
class LocalMuException(LzException):
    """
    Исключение ЛЗ при местном управлении:

    (prev МУ = 1 ИЛИ curr МУ = 1 ИЛИ next МУ = 1)
    во время формирования ЛЗ или за время Tму до него.
    """

    id: str = "local_mu"
    cfg: LocalMuConfig = field(default_factory=LocalMuConfig)

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

        # какие РЦ нас интересуют
        prev_candidates = getattr(station, "prev_candidates", []) or []
        next_candidates = getattr(station, "next_candidates", []) or []
        prev_rc_id = prev_candidates[0] if prev_candidates else ""
        next_rc_id = next_candidates[0] if next_candidates else ""

        rc_ids = {ctrl_rc_id}
        if prev_rc_id:
            rc_ids.add(prev_rc_id)
        if next_rc_id:
            rc_ids.add(next_rc_id)

        # абсолютное время текущего шага
        t_now = sum(float(s.t) for s in history[: idx + 1])

        # окно Tму берём из настроек станции (проброшено из options),
        # при отсутствии — используем дефолт из конфигурации исключения
        t_window = getattr(station, "t_mu", self.cfg.t_mu)

        return self._mu_active_in_window(
            history=history,
            rc_ids=rc_ids,
            t_now=t_now,
            t_window=t_window,
        )

    @staticmethod
    def _mu_active_in_window(
        history: List["ScenarioStep"],
        rc_ids: set[str],
        t_now: float,
        t_window: float,
    ) -> bool:
        """
        Проверяет, что на любой из rc_ids МУ было активно (mu[rc_id] == 1)
        в момент t_now или в течение t_window до него.

        Берём состояние МУ из поля step.mu (как в simulate_1p).
        """
        if not history or t_window <= 0.0:
            return False

        t_start = max(0.0, t_now - t_window)
        time_cursor = t_now
        i = len(history) - 1

        while i >= 0 and time_cursor > t_start:
            step = history[i]
            dt = float(step.t)
            time_cursor -= dt

            if time_cursor < t_start:
                break

            mu_map = getattr(step, "mu", None) or {}
            for rc_id in rc_ids:
                mu_state = int(mu_map.get(rc_id, 0))
                if mu_state == 1:
                    return True

            i -= 1

        return False

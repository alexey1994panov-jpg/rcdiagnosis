from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING, Set

from .base import LsException

if TYPE_CHECKING:
    from engine.station_visochino_1p import StationModel1P
    from engine.types_1p import ScenarioStep
    from engine.simulate_1p import TimelineStep


@dataclass
class LsLocalMuConfig:
    """
    Настройки исключения ЛС по местному управлению.

    t_mu:
      окно по времени (сек), в пределах которого активное МУ блокирует ЛС.
    """

    t_mu: float = 15.0


@dataclass
class LsLocalMuException(LsException):
    """
    Исключение ЛС: наличие местного управления.

    ЛС не формируется, если в окне t_mu:
      - на контролируемой РЦ или
      - на смежных РЦ
    было активно МУ.
    """

    id: str = "ls_exc_mu"
    cfg: LsLocalMuConfig = field(default_factory=LsLocalMuConfig)

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

        # кандидаты для смежных РЦ (как в LocalMuException для ЛЗ)
        prev_candidates = getattr(station, "prev_candidates", []) or []
        next_candidates = getattr(station, "next_candidates", []) or []

        prev_rc_id = prev_candidates[0] if prev_candidates else None
        next_rc_id = next_candidates[0] if next_candidates else None

        rc_ids: Set[str] = {ctrl_rc_id}
        if prev_rc_id:
            rc_ids.add(prev_rc_id)
        if next_rc_id:
            rc_ids.add(next_rc_id)

        # текущее время по шагам сценария
        t_now = sum(float(s.t) for s in history[: idx + 1])

        # сначала пробуем специализированный таймер для ЛС по МУ (t_ls_mu),
        # затем общий t_mu, затем дефолт из конфига
        t_window = getattr(
            station,
            "t_ls_mu",
            getattr(station, "t_mu", self.cfg.t_mu),
        )

        return self._mu_active_in_window(history, rc_ids, t_now, t_window)

    @staticmethod
    def _mu_active_in_window(
        history: List["ScenarioStep"],
        rc_ids: Set[str],
        t_now: float,
        t_window: float,
    ) -> bool:
        """
        Проверка: было ли МУ активно (mu_state == 4) на любой из rc_ids в окне [t_now - t_window, t_now].
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
                # 4 — местное управление включено (по StationRcMU)
                if mu_state == 4:
                    return True

            i -= 1

        return False

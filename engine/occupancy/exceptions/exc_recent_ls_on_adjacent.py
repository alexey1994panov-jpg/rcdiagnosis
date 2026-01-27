from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

from .base import LzException

if TYPE_CHECKING:
    from engine.station_visochino_1p import StationModel1P
    from engine.types_1p import ScenarioStep
    from engine.simulate_1p import TimelineStep


@dataclass
class RecentLsOnAdjacentConfig:
    """
    Настройки временного окна для исключения «недавняя ЛС».
    """
    t_sv: float = 12.0  # Тсв, секунд (дефолт, если станция не задаёт своё)


@dataclass
class RecentLsOnAdjacentException(LzException):
    """
    Исключение:

    - за время Tсв до текущего шага (t_now) была сформирована ЛС (lls_v*)
      на контролируемой РЦ;
    - в этом случае текущая ЛЗ подавляется.
    """

    id: str = "recent_ls_on_adjacent"
    cfg: RecentLsOnAdjacentConfig = field(default_factory=RecentLsOnAdjacentConfig)

    def should_suppress(
        self,
        station: "StationModel1P",
        history: List["ScenarioStep"],
        idx: int,
        ctrl_rc_id: str,
        timeline: List["TimelineStep"],
    ) -> bool:
        # Нет таймлайна — нечего анализировать
        if not timeline:
            return False

        # Абсолютное время: сумма длительностей уже добавленных шагов
        t_now = sum(ts.step_duration for ts in timeline)

        # Берём окно Tсв из станции, если оно проброшено из options,
        # иначе используем дефолт из конфигурации исключения
        t_window = getattr(station, "t_recent_ls", self.cfg.t_sv)

        return self._has_recent_ls_in_window(
            timeline=timeline,
            t_now=t_now,
            t_window=t_window,
        )

    @staticmethod
    def _has_recent_ls_in_window(
        timeline: List["TimelineStep"],
        t_now: float,
        t_window: float,
    ) -> bool:
        """
        Проверяет, была ли ЛС (флаг lls_v*) за последние t_window секунд
        до момента t_now на контролируемой РЦ.

        В текущей модели флаги ЛС (lls_v1, lls_v2, ...) не привязаны
        к конкретной РЦ, а контролируемая РЦ для 1P — ровно та,
        по которой считаются ЛЗ/ЛС, поэтому достаточно факта наличия
        любого lls_v* в окне.
        """
        if not timeline or t_window <= 0.0:
            return False

        t_start = max(0.0, t_now - t_window)
        time_cursor = t_now
        i = len(timeline) - 1

        while i >= 0 and time_cursor > t_start:
            step = timeline[i]
            dt = float(step.step_duration)
            time_cursor -= dt

            if time_cursor < t_start:
                break

            if RecentLsOnAdjacentException._has_ls_flag(step.flags):
                return True

            i -= 1

        return False

    @staticmethod
    def _has_ls_flag(flags: List[str]) -> bool:
        """Проверяет наличие флагов ЛС в списке flags."""
        return any(f.startswith("lls_v") for f in flags)

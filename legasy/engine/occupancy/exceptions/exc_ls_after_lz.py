from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

from .base import LsException

if TYPE_CHECKING:
    from engine.station_visochino_1p import StationModel1P
    from engine.types_1p import ScenarioStep
    from engine.simulate_1p import TimelineStep


@dataclass
class LsAfterLzConfig:
    """
    Настройки исключения ЛС «не формировать ЛС, если была ЛЗ».
    """

    # окно по умолчанию; может быть переопределено station.t_ls_after_lz
    # или, при его отсутствии, station.t_recent_ls
    t_recent_lz: float = 12.0


@dataclass
class LsAfterLzException(LsException):
    """
    Исключение ЛС: не формировать ЛС, если по этой или смежной РЦ недавно была ЛЗ.
    """

    id: str = "ls_exc_after_lz"
    cfg: LsAfterLzConfig = field(default_factory=LsAfterLzConfig)

    def should_suppress(
        self,
        station: "StationModel1P",
        history: List["ScenarioStep"],
        idx: int,
        ctrl_rc_id: str,
        timeline: List["TimelineStep"],
    ) -> bool:
        if not timeline:
            return False

        # текущее время берем по таймлайну
        t_now = sum(ts.step_duration for ts in timeline)

        # сначала специализированный таймер для ЛС после ЛЗ (t_ls_after_lz),
        # затем общий t_recent_ls, затем дефолт из конфига
        t_window = getattr(
            station,
            "t_ls_after_lz",
            getattr(station, "t_recent_ls", self.cfg.t_recent_lz),
        )

        return self._has_recent_lz_in_window(timeline, t_now, t_window)

    @staticmethod
    def _has_recent_lz_in_window(
        timeline: List["TimelineStep"],
        t_now: float,
        t_window: float,
    ) -> bool:
        """
        Проверка наличия ЛЗ в окне [t_now - t_window, t_now] по флагам llz_v*.
        Смотрим именно фактическую ЛЗ (работу ДС ЛЛЗ), а не просто занятость РЦ.
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

            flags = getattr(step, "flags", []) or []
            # любая активная ЛЗ (любой вариант v1/v2/v3/v8)
            if any(f.startswith("llz_v") for f in flags):
                return True

            i -= 1

        return False

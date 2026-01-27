from __future__ import annotations

from typing import List, Protocol, TYPE_CHECKING


if TYPE_CHECKING:
    from engine.station_visochino_1p import StationModel1P
    from engine.types_1p import ScenarioStep
    from engine.simulate_1p import TimelineStep


class LzException(Protocol):
    """
    Протокол для исключений ЛЗ.
    """

    id: str

    def should_suppress(
        self,
        station: "StationModel1P",
        history: List["ScenarioStep"],
        idx: int,
        ctrl_rc_id: str,
        timeline: List["TimelineStep"],
    ) -> bool:
        ...


class LsException(Protocol):
    """
    Протокол для исключений ЛС.
    """

    id: str

    def should_suppress(
        self,
        station: "StationModel1P",
        history: List["ScenarioStep"],
        idx: int,
        ctrl_rc_id: str,
        timeline: List["TimelineStep"],
    ) -> bool:
        ...

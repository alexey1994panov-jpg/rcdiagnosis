from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ScenarioStep:
    t: float
    rc_states: Dict[str, int]
    switch_states: Dict[str, int]
    modes: Dict[str, Any]
    mu: Dict[str, int] | None = None
    dispatcher_control_state: int | None = None
    auto_actions: Dict[str, int] | None = None

    # НОВОЕ: состояния светофоров (UniStateID по NAME светофора)
    signal_states: Dict[str, int] | None = None
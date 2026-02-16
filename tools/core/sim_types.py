# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from core.detectors_engine import DetectorsConfig


@dataclass
class ScenarioStep:
    """Входные данные на интервале [t, t_next)."""
    t: float
    rc_states: Dict[str, int]
    switch_states: Dict[str, int]
    signal_states: Dict[str, int]
    modes: Dict[str, Any]
    mu: Dict[str, int] = field(default_factory=dict)
    dispatcher_control_state: Optional[int] = None
    auto_actions: Dict[str, int] = field(default_factory=dict)
    indicator_states: Dict[str, int] = field(default_factory=dict)


@dataclass
class TimelineStep:
    """Результат симуляции для одной контролируемой РЦ на одном шаге."""
    t: float
    step_duration: float
    ctrl_rc_id: str
    effective_prev_rc: Optional[str]
    effective_next_rc: Optional[str]
    rc_states: Dict[str, int]
    switch_states: Dict[str, int]
    signal_states: Dict[str, int]
    modes: Dict[str, Any]
    lz_state: bool
    lz_variant: int
    flags: list[str]
    mu_state: Optional[int] = None
    nas_state: Optional[int] = None
    chas_state: Optional[int] = None
    dsp_state: Optional[int] = None


@dataclass
class SimulationConfig:
    """Конфигурация симуляции для одной или нескольких контролируемых РЦ."""
    t_pk: float
    detectors_configs: Dict[str, DetectorsConfig] = field(default_factory=dict)
    exceptions_objects_path: Optional[str] = "tools/exceptions_objects.json"
    detectors_config: Optional[DetectorsConfig] = None

    def __post_init__(self):
        if self.detectors_config is not None and not self.detectors_configs:
            self.detectors_configs[self.detectors_config.ctrl_rc_id] = self.detectors_config

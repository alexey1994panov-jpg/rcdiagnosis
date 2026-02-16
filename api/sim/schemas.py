from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ScenarioStepIn(BaseModel):
    t: float
    rc_states: Dict[str, int] = Field(default_factory=dict)
    switch_states: Dict[str, int] = Field(default_factory=dict)
    signal_states: Dict[str, int] = Field(default_factory=dict)
    modes: Dict[str, Any] = Field(default_factory=dict)
    mu: Dict[str, int] = Field(default_factory=dict)
    dispatcher_control_state: Optional[int] = None
    auto_actions: Dict[str, int] = Field(default_factory=dict)
    indicator_states: Dict[str, int] = Field(default_factory=dict)


class ScenarioIn(BaseModel):
    station: str = "Visochino"
    dt: float = 1.0
    options: Dict[str, Any] = Field(default_factory=dict)
    steps: List[ScenarioStepIn]


class TimelineStepOut(BaseModel):
    t: float
    step_duration: float
    ctrl_rc_id: str = ""
    topology_by_rc: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    lz_state: bool
    variant: int
    effective_prev_rc: str
    effective_next_rc: str
    flags: List[Dict[str, Any]]
    modes: Dict[str, Any] = Field(default_factory=dict)
    rc_states: Dict[str, int]
    switch_states: Dict[str, int]
    signal_states: Dict[str, int] = Field(default_factory=dict)
    mu_state: Optional[int] = None
    nas_state: Optional[int] = None
    chas_state: Optional[int] = None
    dsp_state: Optional[int] = None

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TimelineStepDTO:
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
    flags: List[str]


@dataclass
class RunRequestDTO:
    t_pk: float
    scenario: List[Dict[str, Any]]
    detectors_config: Optional[Dict[str, Any]] = None
    detectors_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    ctrl_rc_id: Optional[str] = None
    ctrl_rc_ids: Optional[List[str]] = None


@dataclass
class RunResponseDTO:
    mode: str
    ctrl_rc_ids: List[str]
    timeline: List[TimelineStepDTO]
    frames: List[Dict[str, TimelineStepDTO]]


@dataclass
class MetadataDTO:
    variants: Dict[str, str]
    flags: Dict[str, str]
    masks: Dict[int, str]


def dto_to_dict(obj: Any) -> Any:
    return asdict(obj)


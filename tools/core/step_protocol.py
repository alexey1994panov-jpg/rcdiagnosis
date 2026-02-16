from typing import Protocol, Dict, Any, Optional

class StepAdapter(Protocol):
    rc_states: Dict[str, int]
    modes: Dict[str, Any]
    effective_prev_rc: Optional[str]
    effective_next_rc: Optional[str]
    ctrl_rc_name: str

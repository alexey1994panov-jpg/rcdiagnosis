from typing import Any, Optional, Tuple
from base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from base_wrapper import BaseVariantWrapper
from variants_common import mask_ctrl_free, mask_ctrl_occupied, _is_signal_closed, _is_signal_open, rc_is_occupied, rc_is_free

MASK_LZ10_P01 = 1010
MASK_LZ10_P02 = 1011
MASK_LZ10_P03 = 1012
MASK_LZ10_KOGDA = 1013

def _make_lz10_branch(
    ctrl_rc_id: str,
    prev_rc_id: str,
    next_rc_id: str,
    sig_id: str,
    ts01_lz10: float,
    ts02_lz10: float,
    ts03_lz10: float,
    tlz_lz10: float,
    tkon_lz10: float,
    direction: str,
) -> BaseDetector:
    
    def mask_p01(step, prev, ctrl, nxt) -> bool:
        # Phase 01: prev_free, curr_occ, next_free, sig_open
        if not prev or not nxt: return False
        s_prev = step.rc_states.get(prev, 0)
        s_ctrl = step.rc_states.get(ctrl, 0)
        s_next = step.rc_states.get(nxt, 0)
        return rc_is_free(s_prev) and rc_is_occupied(s_ctrl) and rc_is_free(s_next) and _is_signal_open(step, sig_id)
        
    def mask_p02(step, prev, ctrl, nxt) -> bool:
        # Phase 02: 
        if not prev or not nxt: return False
        s_prev = step.rc_states.get(prev, 0)
        s_ctrl = step.rc_states.get(ctrl, 0)
        s_next = step.rc_states.get(nxt, 0)
        if direction == "to_next":
            return rc_is_free(s_prev) and rc_is_occupied(s_ctrl) and rc_is_occupied(s_next) and _is_signal_open(step, sig_id)
        else: # to_prev
            return rc_is_occupied(s_prev) and rc_is_occupied(s_ctrl) and rc_is_free(s_next) and _is_signal_open(step, sig_id)

    def mask_p03(step, prev, ctrl, nxt) -> bool:
        # Phase 03:
        if not prev or not nxt: return False
        s_prev = step.rc_states.get(prev, 0)
        s_ctrl = step.rc_states.get(ctrl, 0)
        s_next = step.rc_states.get(nxt, 0)
        if direction == "to_next":
            return rc_is_free(s_prev) and rc_is_occupied(s_ctrl) and rc_is_occupied(s_next) and _is_signal_closed(step, sig_id)
        else:
            return rc_is_occupied(s_prev) and rc_is_occupied(s_ctrl) and rc_is_free(s_next) and _is_signal_closed(step, sig_id)

    def mask_kogda(step, prev, ctrl, nxt) -> bool:
        # КОГДА: prev_free, curr_occ, next_free, sig_closed
        if not prev or not nxt: return False
        s_prev = step.rc_states.get(prev, 0)
        s_ctrl = step.rc_states.get(ctrl, 0)
        s_next = step.rc_states.get(nxt, 0)
        return rc_is_free(s_prev) and rc_is_occupied(s_ctrl) and rc_is_free(s_next) and _is_signal_closed(step, sig_id)

    phases = [
        PhaseConfig(0, float(ts01_lz10), 1, reset_on_exit=True, mask_id=MASK_LZ10_P01, mask_fn=mask_p01, requires_neighbors=NeighborRequirement.ONLY_CTRL),
        PhaseConfig(1, float(ts02_lz10), 2, reset_on_exit=True, mask_id=MASK_LZ10_P02, mask_fn=mask_p02, requires_neighbors=NeighborRequirement.ONLY_CTRL),
        PhaseConfig(2, float(ts03_lz10), 3, reset_on_exit=True, mask_id=MASK_LZ10_P03, mask_fn=mask_p03, requires_neighbors=NeighborRequirement.ONLY_CTRL),
        PhaseConfig(3, float(tlz_lz10), -1, reset_on_exit=True, mask_id=MASK_LZ10_KOGDA, mask_fn=mask_kogda, requires_neighbors=NeighborRequirement.ONLY_CTRL),
    ]
    
    config = DetectorConfig(0, phases, float(tkon_lz10), CompletionMode.FREE_TIME, variant_name=f"lz10_{direction}")
    return BaseDetector(config, prev_rc_name=prev_rc_id, ctrl_rc_name=ctrl_rc_id, next_rc_name=next_rc_id)

def make_lz10_detector(
    ctrl_rc_id: str,
    prev_rc_id: Optional[str],
    next_rc_id: Optional[str],
    sig_to_next: Optional[str],
    sig_to_prev: Optional[str],
    ts01_lz10: float,
    ts02_lz10: float,
    ts03_lz10: float,
    tlz_lz10: float,
    tkon_lz10: float,
) -> Any:
    detectors = []
    if prev_rc_id and next_rc_id:
        if sig_to_next:
            detectors.append(_make_lz10_branch(ctrl_rc_id, prev_rc_id, next_rc_id, sig_to_next, ts01_lz10, ts02_lz10, ts03_lz10, tlz_lz10, tkon_lz10, "to_next"))
        if sig_to_prev:
            detectors.append(_make_lz10_branch(ctrl_rc_id, prev_rc_id, next_rc_id, sig_to_prev, ts01_lz10, ts02_lz10, ts03_lz10, tlz_lz10, tkon_lz10, "to_prev"))
            
    if not detectors:
        return None
    if len(detectors) == 1:
        return detectors[0]
    return BaseVariantWrapper(detectors)

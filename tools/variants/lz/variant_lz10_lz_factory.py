from typing import Any, Optional, Tuple
from core.base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from core.base_wrapper import BaseVariantWrapper
from core.variants_common import (
    make_mask_rc_0_1_0_sig_1,
    make_mask_rc_0_1_1_sig_1,
    make_mask_rc_0_1_1_sig_0,
    make_mask_rc_0_1_0_sig_0,
)

MASK_RC_0_1_0_SIG_1 = 43
MASK_RC_0_1_1_SIG_1 = 44
MASK_RC_0_1_1_SIG_0 = 45
MASK_RC_0_1_0_SIG_0 = 46

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
    if direction == "to_next":
        mode_key = "sig_ctrl_to_next"
        fallback_mode_keys = ("sig_prev_to_ctrl", "sig_next_to_ctrl")
    else:
        mode_key = "sig_ctrl_to_prev"
        fallback_mode_keys = ("sig_prev_to_ctrl", "sig_next_to_ctrl")
    mask_rc_0_1_0_sig_1 = make_mask_rc_0_1_0_sig_1(sig_id, mode_key=mode_key, fallback_mode_keys=fallback_mode_keys)
    mask_rc_0_1_1_sig_1 = make_mask_rc_0_1_1_sig_1(sig_id, direction, mode_key=mode_key, fallback_mode_keys=fallback_mode_keys)
    mask_rc_0_1_1_sig_0 = make_mask_rc_0_1_1_sig_0(sig_id, direction, mode_key=mode_key, fallback_mode_keys=fallback_mode_keys)
    mask_rc_0_1_0_sig_0 = make_mask_rc_0_1_0_sig_0(sig_id, mode_key=mode_key, fallback_mode_keys=fallback_mode_keys)

    phases = [
        PhaseConfig(0, float(ts01_lz10), 1, reset_on_exit=True, mask_id=MASK_RC_0_1_0_SIG_1, mask_fn=mask_rc_0_1_0_sig_1, requires_neighbors=NeighborRequirement.ONLY_CTRL),
        PhaseConfig(1, float(ts02_lz10), 2, reset_on_exit=True, mask_id=MASK_RC_0_1_1_SIG_1, mask_fn=mask_rc_0_1_1_sig_1, requires_neighbors=NeighborRequirement.ONLY_CTRL),
        PhaseConfig(2, float(ts03_lz10), 3, reset_on_exit=True, mask_id=MASK_RC_0_1_1_SIG_0, mask_fn=mask_rc_0_1_1_sig_0, requires_neighbors=NeighborRequirement.ONLY_CTRL),
        PhaseConfig(3, float(tlz_lz10), -1, reset_on_exit=True, mask_id=MASK_RC_0_1_0_SIG_0, mask_fn=mask_rc_0_1_0_sig_0, requires_neighbors=NeighborRequirement.ONLY_CTRL),
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
        # Build both directional branches even without static signal id:
        # signal can be resolved dynamically from step.modes.
        detectors.append(_make_lz10_branch(ctrl_rc_id, prev_rc_id, next_rc_id, sig_to_next, ts01_lz10, ts02_lz10, ts03_lz10, tlz_lz10, tkon_lz10, "to_next"))
        detectors.append(_make_lz10_branch(ctrl_rc_id, prev_rc_id, next_rc_id, sig_to_prev, ts01_lz10, ts02_lz10, ts03_lz10, tlz_lz10, tkon_lz10, "to_prev"))
            
    if not detectors:
        return None
    if len(detectors) == 1:
        return detectors[0]
    return BaseVariantWrapper(detectors)



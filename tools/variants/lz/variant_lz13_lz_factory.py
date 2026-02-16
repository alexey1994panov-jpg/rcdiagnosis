from typing import Any, Optional, Tuple
from core.base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from core.base_wrapper import BaseVariantWrapper
from core.variants_common import mask_rc_0, mask_rc_1, _is_signal_closed, _is_locked, rc_is_occupied, rc_is_free

MASK_RC_0L_0_X_SIG_0 = 40
MASK_RC_1_X_0_X_SIG_0 = 41
MASK_RC_1_X_1_X_SIG_0 = 42

def _make_lz13_branch(
    ctrl_rc_id: str,
    adj_side: str, # "prev" or "next"
    sig_id: str,
    ts01_lz13: float,
    ts02_lz13: float,
    tlz_lz13: float,
    tkon_lz13: float,
) -> BaseDetector:
    
    def mask_rc_0l_0_x_sig_0(step, prev, ctrl, nxt) -> bool:
        # adj   , ctrl ,  
        adj_id = prev if adj_side == "prev" else nxt
        if not adj_id: return False
        # LZ13 must use the signal that governs movement from adjacent RC to ctrl RC.
        # prev-branch: prev -> ctrl, next-branch: next -> ctrl.
        sig_mode = "sig_prev_to_ctrl" if adj_side == "prev" else "sig_next_to_ctrl"
        sig_fallback = ("sig_next_to_ctrl",) if adj_side == "prev" else ("sig_prev_to_ctrl",)
        
        s_adj = step.rc_states.get(adj_id, 0)
        return rc_is_free(s_adj) and _is_locked(step, adj_id) and \
               mask_rc_0(step, prev, ctrl, nxt) and \
               _is_signal_closed(step, sig_id, mode_key=sig_mode, fallback_mode_keys=sig_fallback)
               
    def mask_rc_1l_0_x_sig_0(step, prev, ctrl, nxt) -> bool:
        # adj occupied (lock is not required), ctrl free
        adj_id = prev if adj_side == "prev" else nxt
        if not adj_id: return False
        sig_mode = "sig_prev_to_ctrl" if adj_side == "prev" else "sig_next_to_ctrl"
        sig_fallback = ("sig_next_to_ctrl",) if adj_side == "prev" else ("sig_prev_to_ctrl",)
        
        s_adj = step.rc_states.get(adj_id, 0)
        return rc_is_occupied(s_adj) and \
               mask_rc_0(step, prev, ctrl, nxt) and \
               _is_signal_closed(step, sig_id, mode_key=sig_mode, fallback_mode_keys=sig_fallback)
               
    def mask_rc_1l_1_x_sig_0(step, prev, ctrl, nxt) -> bool:
        # adj occupied (lock is not required), ctrl occupied
        adj_id = prev if adj_side == "prev" else nxt
        if not adj_id: return False
        sig_mode = "sig_prev_to_ctrl" if adj_side == "prev" else "sig_next_to_ctrl"
        sig_fallback = ("sig_next_to_ctrl",) if adj_side == "prev" else ("sig_prev_to_ctrl",)
        
        s_adj = step.rc_states.get(adj_id, 0)
        return rc_is_occupied(s_adj) and \
               mask_rc_1(step, prev, ctrl, nxt) and \
               _is_signal_closed(step, sig_id, mode_key=sig_mode, fallback_mode_keys=sig_fallback)
    
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz13),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_RC_0L_0_X_SIG_0,
            mask_fn=mask_rc_0l_0_x_sig_0,
            requires_neighbors=NeighborRequirement.ONE_ADJ,
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(ts02_lz13),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_RC_1_X_0_X_SIG_0,
            mask_fn=mask_rc_1l_0_x_sig_0,
            requires_neighbors=NeighborRequirement.ONE_ADJ,
        ),
        PhaseConfig(
            phase_id=2,
            duration=float(tlz_lz13),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_RC_1_X_1_X_SIG_0,
            mask_fn=mask_rc_1l_1_x_sig_0,
            requires_neighbors=NeighborRequirement.ONE_ADJ,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz13),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="lz13",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=None,
        ctrl_rc_name=ctrl_rc_id,
        next_rc_name=None,
    )

def make_lz13_detector(
    ctrl_rc_id: str,
    prev_rc_id: Optional[str],
    next_rc_id: Optional[str],
    sig_prev: Optional[str],
    sig_next: Optional[str],
    ts01_lz13: float,
    ts02_lz13: float,
    tlz_lz13: float,
    tkon_lz13: float,
) -> Any:
    detectors = []
    # Always build both branches. For dynamic topology RC can gain/lose
    # prev/next neighbor at runtime even if static config has empty side.
    detectors.append(_make_lz13_branch(ctrl_rc_id, "prev", sig_prev, ts01_lz13, ts02_lz13, tlz_lz13, tkon_lz13))
    detectors.append(_make_lz13_branch(ctrl_rc_id, "next", sig_next, ts01_lz13, ts02_lz13, tlz_lz13, tkon_lz13))
        
    if not detectors:
        return None
    if len(detectors) == 1:
        return detectors[0]
    return BaseVariantWrapper(detectors)



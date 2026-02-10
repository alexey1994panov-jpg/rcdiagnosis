from typing import Any, Optional, Tuple
from base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from base_wrapper import BaseVariantWrapper
from variants_common import mask_ctrl_free, mask_ctrl_occupied, _is_signal_closed, _is_locked, rc_is_occupied, rc_is_free

MASK_LZ13_P01 = 1300
MASK_LZ13_P02 = 1301
MASK_LZ13_KOGDA = 1302

def _make_lz13_branch(
    ctrl_rc_id: str,
    adj_side: str, # "prev" or "next"
    sig_id: str,
    ts01_lz13: float,
    ts02_lz13: float,
    tlz_lz13: float,
    tkon_lz13: float,
) -> BaseDetector:
    
    def mask_p01(step, prev, ctrl, nxt) -> bool:
        # adj свободна и замкнута, ctrl свободна, сигнал закрыт
        adj_id = prev if adj_side == "prev" else nxt
        if not adj_id: return False
        
        s_adj = step.rc_states.get(adj_id, 0)
        return rc_is_free(s_adj) and _is_locked(step, adj_id) and \
               mask_ctrl_free(step, prev, ctrl, nxt) and \
               _is_signal_closed(step, sig_id)
               
    def mask_p02(step, prev, ctrl, nxt) -> bool:
        # adj занята и замкнута, ctrl свободна, сигнал закрыт
        adj_id = prev if adj_side == "prev" else nxt
        if not adj_id: return False
        
        s_adj = step.rc_states.get(adj_id, 0)
        return rc_is_occupied(s_adj) and _is_locked(step, adj_id) and \
               mask_ctrl_free(step, prev, ctrl, nxt) and \
               _is_signal_closed(step, sig_id)
               
    def mask_kogda(step, prev, ctrl, nxt) -> bool:
        # adj занята и замкнута, ctrl занята, сигнал закрыт
        adj_id = prev if adj_side == "prev" else nxt
        if not adj_id: return False
        
        s_adj = step.rc_states.get(adj_id, 0)
        return rc_is_occupied(s_adj) and _is_locked(step, adj_id) and \
               mask_ctrl_occupied(step, prev, ctrl, nxt) and \
               _is_signal_closed(step, sig_id)
    
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz13),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LZ13_P01,
            mask_fn=mask_p01,
            requires_neighbors=NeighborRequirement.ONE_ADJ,
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(ts02_lz13),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LZ13_P02,
            mask_fn=mask_p02,
            requires_neighbors=NeighborRequirement.ONE_ADJ,
        ),
        PhaseConfig(
            phase_id=2,
            duration=float(tlz_lz13),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LZ13_KOGDA,
            mask_fn=mask_kogda,
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
    # Теперь мы создаем детекторы, если задан СИГНАЛ, даже если сосед None на старте.
    # Динамическая топология найдет соседа позже.
    if sig_prev:
        detectors.append(_make_lz13_branch(ctrl_rc_id, "prev", sig_prev, ts01_lz13, ts02_lz13, tlz_lz13, tkon_lz13))
    if sig_next:
        detectors.append(_make_lz13_branch(ctrl_rc_id, "next", sig_next, ts01_lz13, ts02_lz13, tlz_lz13, tkon_lz13))
        
    if not detectors:
        return None
    if len(detectors) == 1:
        return detectors[0]
    return BaseVariantWrapper(detectors)

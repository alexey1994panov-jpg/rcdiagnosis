from typing import Any, Optional, Tuple
from base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from variants_common import mask_ctrl_free, mask_ctrl_occupied, _is_signal_closed, rc_is_free, rc_is_occupied

MASK_LZ11_DANO = 1100
MASK_LZ11_KOGDA = 1101

def make_lz11_detector(
    ctrl_rc_id: str,
    sig_ids: Tuple[str, str],
    ts01_lz11: float,
    tlz_lz11: float,
    tkon_lz11: float,
) -> BaseDetector:
    """
    LZ11: Два светофора закрыты.
    ДАНО: ctrl свободна, оба светофора закрыты.
    КОГДА: ctrl занята, оба светофора закрыты.
    """
    if not sig_ids or len(sig_ids) < 2:
        # Fallback or error
        sig_a, sig_b = None, None
    else:
        sig_a, sig_b = sig_ids
    
    def mask_dano(step, prev, ctrl, nxt) -> bool:
        # Получаем состояние ctrl из аргумента
        s_ctrl = step.rc_states.get(ctrl, 0)
        res = rc_is_free(s_ctrl) and \
               _is_signal_closed(step, sig_a) and \
               _is_signal_closed(step, sig_b)
        if not res:
             print(f"DEBUG LZ11 DANO: ctrl={ctrl} s={s_ctrl} free={rc_is_free(s_ctrl)} sigA={sig_a} cl={_is_signal_closed(step, sig_a)} sigB={sig_b} cl={_is_signal_closed(step, sig_b)} -> False")
        return res
               
    def mask_kogda(step, prev, ctrl, nxt) -> bool:
        s_ctrl = step.rc_states.get(ctrl, 0)
        res = rc_is_occupied(s_ctrl) and \
               _is_signal_closed(step, sig_a) and \
               _is_signal_closed(step, sig_b)
        if not res:
             print(f"DEBUG LZ11 KOGDA: ctrl={ctrl} s={s_ctrl} occ={rc_is_occupied(s_ctrl)} sigA={sig_a} cl={_is_signal_closed(step, sig_a)} sigB={sig_b} cl={_is_signal_closed(step, sig_b)} -> False")
        return res
               
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz11),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LZ11_DANO,
            mask_fn=mask_dano,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_lz11),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LZ11_KOGDA,
            mask_fn=mask_kogda,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz11),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="lz11",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=None,
        ctrl_rc_name=ctrl_rc_id,
        next_rc_name=None,
    )

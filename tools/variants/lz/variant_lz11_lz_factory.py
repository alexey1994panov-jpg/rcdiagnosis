from typing import Tuple

from core.base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from core.variants_common import _is_signal_closed, rc_is_free, rc_is_occupied

MASK_SIG_0_RC_0_SIG_0 = 38
MASK_SIG_0_RC_1_SIG_0 = 39


def make_lz11_detector(
    ctrl_rc_id: str,
    sig_ids: Tuple[str, str],
    ts01_lz11: float,
    tlz_lz11: float,
    tkon_lz11: float,
) -> BaseDetector:
    """
    LZ11: two closed signals + ctrl free->occupied transition.
    """
    if not sig_ids or len(sig_ids) < 2:
        sig_a, sig_b = None, None
    else:
        sig_a, sig_b = sig_ids

    def mask_rc_0_sig_0_sig_0(step, prev, ctrl, nxt) -> bool:
        if not sig_a or not sig_b:
            return False
        s_ctrl = step.rc_states.get(ctrl, 0)
        return rc_is_free(s_ctrl) and _is_signal_closed(step, sig_a) and _is_signal_closed(step, sig_b)

    def mask_rc_1_sig_0_sig_0(step, prev, ctrl, nxt) -> bool:
        if not sig_a or not sig_b:
            return False
        s_ctrl = step.rc_states.get(ctrl, 0)
        return rc_is_occupied(s_ctrl) and _is_signal_closed(step, sig_a) and _is_signal_closed(step, sig_b)

    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz11),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_SIG_0_RC_0_SIG_0,
            mask_fn=mask_rc_0_sig_0_sig_0,
            requires_neighbors=NeighborRequirement.ONLY_CTRL,
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_lz11),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_SIG_0_RC_1_SIG_0,
            mask_fn=mask_rc_1_sig_0_sig_0,
            requires_neighbors=NeighborRequirement.ONLY_CTRL,
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

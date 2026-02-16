# -*- coding: utf-8 -*-
from typing import Optional

from core.base_detector import (
    BaseDetector,
    PhaseConfig,
    DetectorConfig,
    CompletionMode,
    NeighborRequirement,
)
from core.base_wrapper import BaseVariantWrapper
from core.variants_common import rc_is_free, rc_is_occupied, _is_signal_closed


MASK_SIG_0_RC_N_0_0 = 26
MASK_SIG_0_RC_N_1_0 = 27
MASK_RC_0_0_N_SIG_0 = 28
MASK_RC_0_1_N_SIG_0 = 29


def make_lz4_detector(
    ctrl_rc_id: str,
    ts01_lz4: float,
    tlz_lz4: float,
    tkon_lz4: float,
    sig_prev_to_ctrl: Optional[str] = None,
    sig_ctrl_to_next: Optional[str] = None,
):
    """
    LZ4:    LZ12 (  NC),   . 
        NC.

     PrevNC:
      P0: prev_nc + ctrl_free + sig_prev_to_ctrl closed
      P1: prev_nc + ctrl_occ  + sig_prev_to_ctrl closed

     NextNC:
      P0: next_nc + ctrl_free + sig_ctrl_to_next closed
      P1: next_nc + ctrl_occ  + sig_ctrl_to_next closed
    """

    def mask_rc_n_0_0_sig_0(step, prev, ctrl, nxt):
        return (
            bool(step.modes.get("prev_nc", False))
            and rc_is_free(step.rc_states.get(ctrl, 0))
            and _is_signal_closed(
                step,
                sig_prev_to_ctrl,
                mode_key="sig_prev_to_ctrl",
                fallback_mode_keys=("sig_next_to_ctrl",),
            )
        )

    def mask_rc_n_1_0_sig_0(step, prev, ctrl, nxt):
        return (
            bool(step.modes.get("prev_nc", False))
            and rc_is_occupied(step.rc_states.get(ctrl, 0))
            and _is_signal_closed(
                step,
                sig_prev_to_ctrl,
                mode_key="sig_prev_to_ctrl",
                fallback_mode_keys=("sig_next_to_ctrl",),
            )
        )

    def mask_rc_0_0_n_sig_0(step, prev, ctrl, nxt):
        return (
            bool(step.modes.get("next_nc", False))
            and rc_is_free(step.rc_states.get(ctrl, 0))
            and _is_signal_closed(
                step,
                sig_ctrl_to_next,
                mode_key="sig_ctrl_to_next",
                fallback_mode_keys=("sig_ctrl_to_prev",),
            )
        )

    def mask_rc_0_1_n_sig_0(step, prev, ctrl, nxt):
        return (
            bool(step.modes.get("next_nc", False))
            and rc_is_occupied(step.rc_states.get(ctrl, 0))
            and _is_signal_closed(
                step,
                sig_ctrl_to_next,
                mode_key="sig_ctrl_to_next",
                fallback_mode_keys=("sig_ctrl_to_prev",),
            )
        )

    branch_prev = BaseDetector(
        config=DetectorConfig(
            initial_phase_id=0,
            phases=[
                PhaseConfig(
                    phase_id=0,
                    duration=float(ts01_lz4),
                    next_phase_id=1,
                    reset_on_exit=True,
                    mask_id=MASK_SIG_0_RC_N_0_0,
                    mask_fn=mask_rc_n_0_0_sig_0,
                    requires_neighbors=NeighborRequirement.ONE_NC,
                ),
                PhaseConfig(
                    phase_id=1,
                    duration=float(tlz_lz4),
                    next_phase_id=-1,
                    reset_on_exit=True,
                    mask_id=MASK_SIG_0_RC_N_1_0,
                    mask_fn=mask_rc_n_1_0_sig_0,
                    requires_neighbors=NeighborRequirement.ONE_NC,
                ),
            ],
            t_kon=float(tkon_lz4),
            completion_mode=CompletionMode.FREE_TIME,
            variant_name="LZ4_PrevNC",
        ),
        ctrl_rc_name=ctrl_rc_id,
    )

    branch_next = BaseDetector(
        config=DetectorConfig(
            initial_phase_id=0,
            phases=[
                PhaseConfig(
                    phase_id=0,
                    duration=float(ts01_lz4),
                    next_phase_id=1,
                    reset_on_exit=True,
                    mask_id=MASK_RC_0_0_N_SIG_0,
                    mask_fn=mask_rc_0_0_n_sig_0,
                    requires_neighbors=NeighborRequirement.ONE_NC,
                ),
                PhaseConfig(
                    phase_id=1,
                    duration=float(tlz_lz4),
                    next_phase_id=-1,
                    reset_on_exit=True,
                    mask_id=MASK_RC_0_1_N_SIG_0,
                    mask_fn=mask_rc_0_1_n_sig_0,
                    requires_neighbors=NeighborRequirement.ONE_NC,
                ),
            ],
            t_kon=float(tkon_lz4),
            completion_mode=CompletionMode.FREE_TIME,
            variant_name="LZ4_NextNC",
        ),
        ctrl_rc_name=ctrl_rc_id,
    )

    return BaseVariantWrapper(detectors=[branch_prev, branch_next])



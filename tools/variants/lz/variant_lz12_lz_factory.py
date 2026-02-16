# -*- coding: utf-8 -*-
from typing import List, Optional
from core.base_detector import BaseDetector, DetectorConfig, PhaseConfig, CompletionMode, NeighborRequirement
from core.base_wrapper import BaseVariantWrapper
from core.variants_common import get_mask_by_id

MASK_RC_N_1_0L = 22
MASK_RC_N_1_1L = 23
MASK_RC_L0_1_N = 24
MASK_RC_L1_1_N = 25

def make_lz12_detector(
    ctrl_rc_id: str,
    ts01_lz12: float,
    ts02_lz12: float,
    tlz_lz12: float,
    t_kon: float,
) -> BaseVariantWrapper:
    """
       LZ12 (  / NC).
    
     : 
    1. Prev NC: (Prev=NC, Ctrl=Free) -> (Prev=NC, Ctrl=Occ)
    2. Next NC: (Next=NC, Ctrl=Free) -> (Next=NC, Ctrl=Occ)
    """
    
    #  1: Prev NC
    branch_prev = BaseDetector(
        config=DetectorConfig(
            initial_phase_id=0,
            phases=[
                PhaseConfig(
                    phase_id=0,
                    duration=ts01_lz12,
                    next_phase_id=1,
                    mask_id=MASK_RC_N_1_0L,
                    mask_fn=get_mask_by_id(MASK_RC_N_1_0L),
                    requires_neighbors=NeighborRequirement.ONE_NC
                ),
                PhaseConfig(
                    phase_id=1,
                    duration=ts02_lz12,
                    next_phase_id=2,
                    mask_id=MASK_RC_N_1_1L,
                    mask_fn=get_mask_by_id(MASK_RC_N_1_1L),
                    requires_neighbors=NeighborRequirement.ONE_NC
                ),
                PhaseConfig(
                    phase_id=2,
                    duration=tlz_lz12,
                    next_phase_id=-1,
                    mask_id=MASK_RC_N_1_0L,
                    mask_fn=get_mask_by_id(MASK_RC_N_1_0L),
                    requires_neighbors=NeighborRequirement.ONE_NC
                ),
            ],
            t_kon=t_kon,
            completion_mode=CompletionMode.FREE_TIME,
            variant_name="LZ12_PrevNC"
        ),
        ctrl_rc_name=ctrl_rc_id
    )

    #  2: Next NC
    branch_next = BaseDetector(
        config=DetectorConfig(
            initial_phase_id=0,
            phases=[
                PhaseConfig(
                    phase_id=0,
                    duration=ts01_lz12,
                    next_phase_id=1,
                    mask_id=MASK_RC_L0_1_N,
                    mask_fn=get_mask_by_id(MASK_RC_L0_1_N),
                    requires_neighbors=NeighborRequirement.ONE_NC
                ),
                PhaseConfig(
                    phase_id=1,
                    duration=ts02_lz12,
                    next_phase_id=2,
                    mask_id=MASK_RC_L1_1_N,
                    mask_fn=get_mask_by_id(MASK_RC_L1_1_N),
                    requires_neighbors=NeighborRequirement.ONE_NC
                ),
                PhaseConfig(
                    phase_id=2,
                    duration=tlz_lz12,
                    next_phase_id=-1,
                    mask_id=MASK_RC_L0_1_N,
                    mask_fn=get_mask_by_id(MASK_RC_L0_1_N),
                    requires_neighbors=NeighborRequirement.ONE_NC
                ),
            ],
            t_kon=t_kon,
            completion_mode=CompletionMode.FREE_TIME,
            variant_name="LZ12_NextNC"
        ),
        ctrl_rc_name=ctrl_rc_id
    )

    return BaseVariantWrapper(detectors=[branch_prev, branch_next])



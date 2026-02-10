# -*- coding: utf-8 -*-
from typing import List, Optional
from base_detector import BaseDetector, DetectorConfig, PhaseConfig, CompletionMode, NeighborRequirement
from base_wrapper import BaseVariantWrapper
from variants_common import get_mask_by_id

def make_lz12_detector(
    ctrl_rc_id: str,
    ts01_lz12: float,
    tlz_lz12: float,
    t_kon: float,
) -> BaseVariantWrapper:
    """
    Фабрика для варианта LZ12 (Крайние секции / NC).
    
    Две ветки: 
    1. Prev NC: (Prev=NC, Ctrl=Free) -> (Prev=NC, Ctrl=Occ)
    2. Next NC: (Next=NC, Ctrl=Free) -> (Next=NC, Ctrl=Occ)
    """
    
    # Ветка 1: Prev NC
    branch_prev = BaseDetector(
        config=DetectorConfig(
            initial_phase_id=0,
            phases=[
                PhaseConfig(
                    phase_id=0,
                    duration=ts01_lz12,
                    next_phase_id=1,
                    mask_id=512, # LZ12_PREV_NC_P0
                    mask_fn=get_mask_by_id(512),
                    requires_neighbors=NeighborRequirement.ONE_NC
                ),
                PhaseConfig(
                    phase_id=1,
                    duration=tlz_lz12,
                    next_phase_id=-1,
                    mask_id=513, # LZ12_PREV_NC_P1
                    mask_fn=get_mask_by_id(513),
                    requires_neighbors=NeighborRequirement.ONE_NC
                )
            ],
            t_kon=t_kon,
            completion_mode=CompletionMode.FREE_TIME,
            variant_name="LZ12_PrevNC"
        ),
        ctrl_rc_name=ctrl_rc_id
    )

    # Ветка 2: Next NC
    branch_next = BaseDetector(
        config=DetectorConfig(
            initial_phase_id=0,
            phases=[
                PhaseConfig(
                    phase_id=0,
                    duration=ts01_lz12,
                    next_phase_id=1,
                    mask_id=514, # LZ12_NEXT_NC_P0
                    mask_fn=get_mask_by_id(514),
                    requires_neighbors=NeighborRequirement.ONE_NC
                ),
                PhaseConfig(
                    phase_id=1,
                    duration=tlz_lz12,
                    next_phase_id=-1,
                    mask_id=515, # LZ12_NEXT_NC_P1
                    mask_fn=get_mask_by_id(515),
                    requires_neighbors=NeighborRequirement.ONE_NC
                )
            ],
            t_kon=t_kon,
            completion_mode=CompletionMode.FREE_TIME,
            variant_name="LZ12_NextNC"
        ),
        ctrl_rc_name=ctrl_rc_id
    )

    return BaseVariantWrapper(detectors=[branch_prev, branch_next])

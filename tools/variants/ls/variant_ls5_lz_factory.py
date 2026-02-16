# -*- coding: utf-8 -*-
"""
   LS5 (  )

:
    LS5         .
    
 (  ):
    0: (  +,  +)  ts01_ls5
    1: (   +,  +)  tlz_ls5   
    
:
       tkon_ls5  
"""

from typing import Any, Optional, List
from core.base_detector import (
    BaseDetector,
    PhaseConfig,
    DetectorConfig,
    CompletionMode,
    NeighborRequirement,
)
from core.base_wrapper import BaseVariantWrapper
from core.variants_common import (
    mask_rc_1l_0l_0l,
    mask_rc_0l_0l_1l,
    mask_rc_1l_0l_1l,
)

# ID   LS5
MASK_RC_1L_0L_0L = 19
MASK_RC_0L_0L_1L = 20
MASK_RC_1L_0L_1L = 21


def _make_branch_detector(
    ctrl_rc_name: str,
    p0_id: int, p0_fn: Any,
    ts01: float,
    tlz: float,
    tkon: float,
    prev_name: Optional[str],
    next_name: Optional[str],
) -> BaseDetector:
    """    LS5."""
    phases = [
        #  0:   
        PhaseConfig(
            phase_id=0,
            duration=ts01,
            next_phase_id=1,
            mask_id=p0_id,
            mask_fn=p0_fn,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        #  1:   
        PhaseConfig(
            phase_id=1,
            duration=tlz,
            next_phase_id=-1,
            mask_id=MASK_RC_1L_0L_1L,
            mask_fn=mask_rc_1l_0l_1l,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=tkon,
        completion_mode=CompletionMode.OCCUPIED_TIME, #    ( )
        variant_name="ls5_branch",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=prev_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_name,
    )


def make_ls5_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_ls5: float,
    tlz_ls5: float,
    tkon_ls5: float,
) -> BaseVariantWrapper:
    """  LS5 ( )   ."""
    detectors = []
    
    #  Prev (Prev    )
    if prev_rc_name and next_rc_name:
        det_prev = _make_branch_detector(
            ctrl_rc_name=ctrl_rc_name,
            p0_id=MASK_RC_1L_0L_0L, p0_fn=mask_rc_1l_0l_0l,
            ts01=ts01_ls5, tlz=tlz_ls5, tkon=tkon_ls5,
            prev_name=prev_rc_name, next_name=next_rc_name,
        )
        detectors.append(det_prev)
        
    #  Next (Next    )
    if prev_rc_name and next_rc_name:
        det_next = _make_branch_detector(
            ctrl_rc_name=ctrl_rc_name,
            p0_id=MASK_RC_0L_0L_1L, p0_fn=mask_rc_0l_0l_1l,
            ts01=ts01_ls5, tlz=tlz_ls5, tkon=tkon_ls5,
            prev_name=prev_rc_name, next_name=next_rc_name,
        )
        detectors.append(det_next)
        
    return BaseVariantWrapper(detectors)
    



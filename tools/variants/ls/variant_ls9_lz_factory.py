# -*- coding: utf-8 -*-
"""
   LS9 (  )

:
    LS9  "  " - ,  
             .
    
:
    0 (S0109): ctrl    ts01_ls9
    1 (tail):  ctrl    tlz_ls9  
    2 (S0209): ctrl    tlz_ls9   
    
:
    ctrl   tkon_ls9  

:
    -    (NeighborRequirement.ONLY_CTRL)
    -     
    -   
"""

from core.base_detector import (
    BaseDetector,
    PhaseConfig,
    DetectorConfig,
    CompletionMode,
    NeighborRequirement,
)
from core.variants_common import mask_rc_1, mask_rc_0

#    LZ6 (v6)
MASK_RC_1_PHASE_01 = 16  # ctrl occupied
MASK_RC_0_PHASE_02 = 15  # ctrl free
MASK_RC_1_PHASE_03 = 16  # ctrl occupied


def make_ls9_detector(
    ctrl_rc_name: str,
    ts01_ls9: float,
    tlz_ls9: float,
    tkon_ls9: float,
) -> BaseDetector:
    """
      LS9 (  ).
    
    :
    0 (S0109): ctrl   ts01_ls9
    1 (tail):  ctrl   tlz_ls9
    2 (S0209): ctrl   tlz_ls9  
    
    : ctrl   tkon_ls9  
    
       LZ6:
    - mask_ctrl_occupied (601)
    - mask_ctrl_free (600)
    
    Args:
        ctrl_rc_name:   
        ts01_ls9:   S0109 ( )
        tlz_ls9:   tail  S0209
        tkon_ls9:     
        
    Returns:
        BaseDetector   LS9
    """
    phases = [
        #  0: S0109 - ctrl 
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_ls9),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_RC_1_PHASE_01,
            mask_fn=mask_rc_1,  # ctrl 
            requires_neighbors=NeighborRequirement.ONLY_CTRL,
        ),
        #  1: tail - ctrl 
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_ls9),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_RC_0_PHASE_02,
            mask_fn=mask_rc_0,  # ctrl 
            requires_neighbors=NeighborRequirement.ONLY_CTRL,
        ),
        #  2: S0209 - ctrl   
        PhaseConfig(
            phase_id=2,
            duration=float(tlz_ls9),
            next_phase_id=-1,  # -1 =  
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_RC_1_PHASE_03,
            mask_fn=mask_rc_1,  # ctrl 
            requires_neighbors=NeighborRequirement.ONLY_CTRL,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_ls9),
        completion_mode=CompletionMode.OCCUPIED_TIME,
        variant_name="ls9",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=None,  #   
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=None,  #   
    )


# JSON-  
LS9_SCHEMA = {
    "variant_id": 109,
    "variant_name": "ls9",
    "description": "  ",
    "phases": [
        {"id": 0, "name": "S0109", "condition": "ctrl "},
        {"id": 1, "name": "tail", "condition": "ctrl "},
        {"id": 2, "name": "S0209", "condition": "ctrl "},
    ],
    "parameters": ["ts01_ls9", "tlz_ls9", "tkon_ls9"],
    "topology": "none",
    "requires_neighbors": False,
    "requires_signals": False,
    "requires_nc_flags": False,
}



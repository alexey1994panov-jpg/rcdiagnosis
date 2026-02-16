"""
  6 (v6) -      .
:  (  Ts06)   (  Tlz06)  .
"""

from core.base_detector import (
    BaseDetector,
    PhaseConfig,
    DetectorConfig,
    CompletionMode,
    NeighborRequirement,
)
from core.variants_common import mask_rc_0, mask_rc_1


def make_lz6_detector(
    ctrl_rc_name: str,
    ts01_lz6: float,
    tlz_lz6: float,
    tkon_lz6: float,
) -> BaseDetector:
    """
       v6.
    
    :
    0:  -     Ts06
    1:  -     Tlz06  
    
    :    Tkon (FREE_TIME )
    """
    
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz6),
            next_phase_id=1,
            timer_mode="continuous",  #    
            reset_on_exit=True,
            mask_id=15,  # v6  0
            mask_fn=mask_rc_0,  #  
            requires_neighbors=NeighborRequirement.ONLY_CTRL,  #   
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_lz6),
            next_phase_id=-1,  #   
            timer_mode="continuous",  #    
            reset_on_exit=True,
            mask_id=16,  # v6  1
            mask_fn=mask_rc_1,  #  
            requires_neighbors=NeighborRequirement.ONLY_CTRL,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz6),
        completion_mode=CompletionMode.FREE_TIME,  #   
        variant_name="v6",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=None,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=None
    )


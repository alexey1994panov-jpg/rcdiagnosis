# -*- coding: utf-8 -*-
"""
Фабрика для варианта LS4 (Шунтовое движение)

Описание:
    LS4 детектирует ложную свободность при шунтовом движении (заняты оба соседа).
    
Фазы:
    0: (все три заняты 111) → ts01_ls4
    1: (центр освободился 101) → tlz01_ls4
    2: (центр снова занят 111) → tlz02_ls4 → открытие ЛС
    
Завершение:
    все свободны ≥ tkon_ls4 → закрытие
"""

from base_detector import (
    BaseDetector,
    PhaseConfig,
    DetectorConfig,
    CompletionMode,
    NeighborRequirement,
)
from variants_common import mask_111, mask_101

# ID масок для LS4
MASK_LS4_111 = 0b111
MASK_LS4_101 = 0b101


def make_ls4_detector(
    prev_rc_name: str,
    ctrl_rc_name: str,
    next_rc_name: str,
    ts01_ls4: float,
    tlz01_ls4: float,
    tlz02_ls4: float,
    tkon_ls4: float,
) -> BaseDetector:
    """Создает детектор LS4 (Шунтовое движение)."""
    phases = [
        # Фаза 0: 111 (все заняты)
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_ls4),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LS4_111,
            mask_fn=mask_111,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        # Фаза 1: 101 (края заняты, центр свободен)
        PhaseConfig(
            phase_id=1,
            duration=float(tlz01_ls4),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LS4_101,
            mask_fn=mask_101,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        # Фаза 2: 111 (снова все заняты)
        PhaseConfig(
            phase_id=2,
            duration=float(tlz02_ls4),
            next_phase_id=-1, # Открытие
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LS4_111,
            mask_fn=mask_111,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_ls4),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="ls4",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )
    

# -*- coding: utf-8 -*-
"""
Фабрика для варианта LS2 (Асимметричная ложная свободность)

Описание:
    LS2 детектирует ложную свободность по двум независимым веткам:
    - Ветка 1 (Prev): 110 → 100 → 110
    - Ветка 2 (Next): 011 → 001 → 011
    
Фазы (для каждой ветки):
    0: (prev-ctrl заняты) → ts01_ls2
    1: (ctrl освободилась) → tlz_ls2
    2: (ctrl снова занята) → ts02_ls2 → открытие ЛС
    
Завершение:
    все свободны ≥ tkon_ls2 → закрытие
"""

from typing import Any, Optional, List
from base_detector import (
    BaseDetector,
    PhaseConfig,
    DetectorConfig,
    CompletionMode,
    NeighborRequirement,
)
from base_wrapper import BaseVariantWrapper
from variants_common import mask_110, mask_100, mask_011, mask_001

# ID масок для LS2
MASK_LS2_110 = 0b110
MASK_LS2_100 = 0b100
MASK_LS2_011 = 0b011
MASK_LS2_001 = 0b001


def _make_branch_detector(
    ctrl_rc_name: str,
    neighbor_rc_name: Optional[str],
    m0_id: int, m0_fn: Any,
    m1_id: int, m1_fn: Any,
    m2_id: int, m2_fn: Any,
    ts01: float,
    tlz: float,
    ts02: float,
    tkon: float,
    prev_name: Optional[str],
    next_name: Optional[str],
) -> BaseDetector:
    """Создает одну ветку детектора LS2."""
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=ts01,
            next_phase_id=1,
            mask_id=m0_id,
            mask_fn=m0_fn,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=1,
            duration=tlz,
            next_phase_id=2,
            mask_id=m1_id,
            mask_fn=m1_fn,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=2,
            duration=ts02,
            next_phase_id=-1,
            mask_id=m2_id,
            mask_fn=m2_fn,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=tkon,
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="ls2_branch",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=prev_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_name,
    )


def make_ls2_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_ls2: float,
    tlz_ls2: float,
    ts02_ls2: float,
    tkon_ls2: float,
) -> BaseVariantWrapper:
    """Создает детектор LS2 (Асимметричная ложная свободность) с двумя ветками."""
    detectors = []
    
    # Ветка Prev (110 → 100 → 110)
    if prev_rc_name:
        det_prev = _make_branch_detector(
            ctrl_rc_name=ctrl_rc_name,
            neighbor_rc_name=prev_rc_name,
            m0_id=MASK_LS2_110, m0_fn=mask_110,
            m1_id=MASK_LS2_100, m1_fn=mask_100,
            m2_id=MASK_LS2_110, m2_fn=mask_110,
            ts01=ts01_ls2, tlz=tlz_ls2, ts02=ts02_ls2, tkon=tkon_ls2,
            prev_name=prev_rc_name, next_name=next_rc_name,
        )
        detectors.append(det_prev)
        
    # Ветка Next (011 → 001 → 011)
    if next_rc_name:
        det_next = _make_branch_detector(
            ctrl_rc_name=ctrl_rc_name,
            neighbor_rc_name=next_rc_name,
            m0_id=MASK_LS2_011, m0_fn=mask_011,
            m1_id=MASK_LS2_001, m1_fn=mask_001,
            m2_id=MASK_LS2_011, m2_fn=mask_011,
            ts01=ts01_ls2, tlz=tlz_ls2, ts02=ts02_ls2, tkon=tkon_ls2,
            prev_name=prev_rc_name, next_name=next_rc_name,
        )
        detectors.append(det_next)
        
    return BaseVariantWrapper(detectors)
    

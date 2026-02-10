# -*- coding: utf-8 -*-
"""
Фабрика для варианта LS5 (Замыкание смежной РЦ)

Описание:
    LS5 детектирует ложную свободность при замыкании смежной и контролируемой РЦ.
    
Фазы (для каждой ветки):
    0: (одна смежная занята+замкнута, центр свободен+замкнут) → ts01_ls5
    1: (вторая смежная тоже занята+замкнута, центр свободен+замкнут) → tlz_ls5 → открытие ЛС
    
Завершение:
    центр занят ≥ tkon_ls5 → закрытие
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
from variants_common import (
    mask_ls5_prev_locked_p0,
    mask_ls5_next_locked_p0,
    mask_ls5_both_locked_p1
)

# ID масок для LS5
MASK_LS5_PREV_LOCKED = 505
MASK_LS5_NEXT_LOCKED = 506
MASK_LS5_BOTH_LOCKED = 507


def _make_branch_detector(
    ctrl_rc_name: str,
    p0_id: int, p0_fn: Any,
    ts01: float,
    tlz: float,
    tkon: float,
    prev_name: Optional[str],
    next_name: Optional[str],
) -> BaseDetector:
    """Создает одну ветку детектора LS5."""
    phases = [
        # Фаза 0: Одна смежная занята
        PhaseConfig(
            phase_id=0,
            duration=ts01,
            next_phase_id=1,
            mask_id=p0_id,
            mask_fn=p0_fn,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        # Фаза 1: Обе смежные заняты
        PhaseConfig(
            phase_id=1,
            duration=tlz,
            next_phase_id=-1,
            mask_id=MASK_LS5_BOTH_LOCKED,
            mask_fn=mask_ls5_both_locked_p1,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=tkon,
        completion_mode=CompletionMode.OCCUPIED_TIME, # Закрытие по занятию (из ТЗ)
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
    """Создает детектор LS5 (Замыкание смежной) с двумя ветками."""
    detectors = []
    
    # Ветка Prev (Prev занят → Оба заняты)
    if prev_rc_name and next_rc_name:
        det_prev = _make_branch_detector(
            ctrl_rc_name=ctrl_rc_name,
            p0_id=MASK_LS5_PREV_LOCKED, p0_fn=mask_ls5_prev_locked_p0,
            ts01=ts01_ls5, tlz=tlz_ls5, tkon=tkon_ls5,
            prev_name=prev_rc_name, next_name=next_rc_name,
        )
        detectors.append(det_prev)
        
    # Ветка Next (Next занят → Оба заняты)
    if prev_rc_name and next_rc_name:
        det_next = _make_branch_detector(
            ctrl_rc_name=ctrl_rc_name,
            p0_id=MASK_LS5_NEXT_LOCKED, p0_fn=mask_ls5_next_locked_p0,
            ts01=ts01_ls5, tlz=tlz_ls5, tkon=tkon_ls5,
            prev_name=prev_rc_name, next_name=next_rc_name,
        )
        detectors.append(det_next)
        
    return BaseVariantWrapper(detectors)
    

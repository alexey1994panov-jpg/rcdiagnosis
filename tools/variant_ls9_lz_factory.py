# -*- coding: utf-8 -*-
"""
Фабрика для варианта LS9 (Пробой изолирующего стыка)

Описание:
    LS9 детектирует "пробой изолирующего стыка" - ситуацию, когда РЦ
    переходит из занятого состояния в свободное и обратно в занятое.
    
Фазы:
    0 (S0109): ctrl занята → длительность ts01_ls9
    1 (tail):  ctrl свободна → длительность tlz_ls9  
    2 (S0209): ctrl занята → длительность tlz_ls9 → открытие ЛС
    
Завершение:
    ctrl свободна ≥ tkon_ls9 → закрытие

Особенности:
    - Не требует соседей (NeighborRequirement.ONLY_CTRL)
    - Работает только на контролируемой РЦ
    - Три фазы формирования
"""

from base_detector import (
    BaseDetector,
    PhaseConfig,
    DetectorConfig,
    CompletionMode,
    NeighborRequirement,
)
from variants_common import mask_ctrl_occupied, mask_ctrl_free

# Используем маски из LZ6 (v6)
MASK_LS9_S0109 = 601  # ctrl занята (как в LZ6 фаза 1)
MASK_LS9_TAIL = 600   # ctrl свободна (как в LZ6 фаза 0)
MASK_LS9_S0209 = 601  # ctrl занята (как в LZ6 фаза 1)


def make_ls9_detector(
    ctrl_rc_name: str,
    ts01_ls9: float,
    tlz_ls9: float,
    tkon_ls9: float,
) -> BaseDetector:
    """
    Создает детектор LS9 (Пробой изолирующего стыка).
    
    Фазы:
    0 (S0109): ctrl занята ≥ ts01_ls9
    1 (tail):  ctrl свободна ≥ tlz_ls9
    2 (S0209): ctrl занята ≥ tlz_ls9 → открытие
    
    Завершение: ctrl свободна ≥ tkon_ls9 → закрытие
    
    Использует маски из LZ6:
    - mask_ctrl_occupied (601)
    - mask_ctrl_free (600)
    
    Args:
        ctrl_rc_name: Имя контролируемой РЦ
        ts01_ls9: Длительность фазы S0109 (первая занятость)
        tlz_ls9: Длительность фаз tail и S0209
        tkon_ls9: Время на завершение после открытия
        
    Returns:
        BaseDetector для варианта LS9
    """
    phases = [
        # Фаза 0: S0109 - ctrl занята
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_ls9),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LS9_S0109,
            mask_fn=mask_ctrl_occupied,  # ctrl занята
            requires_neighbors=NeighborRequirement.ONLY_CTRL,
        ),
        # Фаза 1: tail - ctrl свободна
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_ls9),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LS9_TAIL,
            mask_fn=mask_ctrl_free,  # ctrl свободна (из LZ6)
            requires_neighbors=NeighborRequirement.ONLY_CTRL,
        ),
        # Фаза 2: S0209 - ctrl занята → открытие
        PhaseConfig(
            phase_id=2,
            duration=float(tlz_ls9),
            next_phase_id=-1,  # -1 = открытие ЛС
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LS9_S0209,
            mask_fn=mask_ctrl_occupied,  # ctrl занята (из LZ6)
            requires_neighbors=NeighborRequirement.ONLY_CTRL,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_ls9),
        completion_mode=CompletionMode.FREE_TIME,  # Закрытие при свободности
        variant_name="ls9",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=None,  # не требует соседей
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=None,  # не требует соседей
    )


# JSON-схема для документации
LS9_SCHEMA = {
    "variant_id": 109,
    "variant_name": "ls9",
    "description": "Пробой изолирующего стыка",
    "phases": [
        {"id": 0, "name": "S0109", "condition": "ctrl занята"},
        {"id": 1, "name": "tail", "condition": "ctrl свободна"},
        {"id": 2, "name": "S0209", "condition": "ctrl занята"},
    ],
    "parameters": ["ts01_ls9", "tlz_ls9", "tkon_ls9"],
    "topology": "none",
    "requires_neighbors": False,
    "requires_signals": False,
    "requires_nc_flags": False,
}

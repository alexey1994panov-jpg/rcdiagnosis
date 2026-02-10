# -*- coding: utf-8 -*-
"""
Фабрика для варианта LS1 (Классическая ложная свободность)

Описание:
    LS1 детектирует классическую ложную свободность - обратный паттерн от LZ1.
    Использует те же маски что и LZ1, но в обратном порядке: 010 → 000
    
Фазы:
    0 (C0101): prev-ctrl-next = 0-1-0 (центр занят, края свободны) → длительность ts01_ls1
    1 (tail):  prev-ctrl-next = 0-0-0 (все свободны) → длительность tlz_ls1 → открытие ЛС
    
Завершение:
    все свободны ≥ tkon_ls1 → закрытие

Особенности:
    - Требует обоих соседей (NeighborRequirement.BOTH)
    - Использует маски из LZ1: mask_010 и mask_000
    - Соседи определяются по стрелкам (нужны switch_states в сценарии)
"""

from base_detector import (
    BaseDetector,
    PhaseConfig,
    DetectorConfig,
    CompletionMode,
    NeighborRequirement,
)
from variants_common import mask_010, mask_000

# Используем маски из LZ1 в обратном порядке
MASK_LS1_C0101 = 0b010  # 0-1-0: центр занят, края свободны (как LZ1 фаза 1)
MASK_LS1_TAIL = 0b000   # 0-0-0: все свободны (как LZ1 фаза 0)


def make_ls1_detector(
    prev_rc_name: str,
    ctrl_rc_name: str,
    next_rc_name: str,
    ts01_ls1: float,
    tlz_ls1: float,
    tkon_ls1: float,
) -> BaseDetector:
    """
    Создает детектор LS1 (Классическая ложная свободность).
    
    Логика: 010 → 000 (обратный паттерн от LZ1)
    
    Args:
        prev_rc_name: Имя предыдущей РЦ
        ctrl_rc_name: Имя контролируемой РЦ
        next_rc_name: Имя следующей РЦ
        ts01_ls1: Длительность фазы C0101 (0-1-0)
        tlz_ls1: Длительность фазы tail (0-0-0)
        tkon_ls1: Время на завершение после открытия
        
    Returns:
        BaseDetector для варианта LS1
    """
    phases = [
        # Фаза 0: C0101 - 0-1-0 (центр занят, края свободны)
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_ls1),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LS1_C0101,
            mask_fn=mask_010,  # из LZ1
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        # Фаза 1: tail - 0-0-0 (все свободны) → открытие
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_ls1),
            next_phase_id=-1,  # -1 = открытие ЛС
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_LS1_TAIL,
            mask_fn=mask_000,  # из LZ1
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_ls1),
        completion_mode=CompletionMode.FREE_TIME,  # Закрытие при свободности
        variant_name="ls1",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )


# JSON-схема для документации
LS1_SCHEMA = {
    "variant_id": 101,
    "variant_name": "ls1",
    "description": "Классическая ложная свободность (обратный паттерн от LZ1)",
    "phases": [
        {"id": 0, "name": "C0101", "condition": "0-1-0 (центр занят, края свободны)"},
        {"id": 1, "name": "tail", "condition": "0-0-0 (все свободны)"},
    ],
    "parameters": ["ts01_ls1", "tlz_ls1", "tkon_ls1"],
    "topology": "both_neighbors",
    "requires_neighbors": True,
    "requires_signals": False,
    "uses_lz1_masks": True,  # Использует маски из LZ1 в обратном порядке
}

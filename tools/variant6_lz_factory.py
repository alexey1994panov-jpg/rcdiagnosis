"""
Фабрика варианта 6 (v6) - Длительная занятость одной РЦ без замыкания.
Логика: ДАНО (свободна ≥ Ts06) → КОГДА (занята ≥ Tlz06) → Открытие.
"""

from base_detector import (
    BaseDetector,
    PhaseConfig,
    DetectorConfig,
    CompletionMode,
    NeighborRequirement,
)
from variants_common import mask_ctrl_free, mask_ctrl_occupied


def make_lz6_detector(
    ctrl_rc_name: str,
    ts01_lz6: float,
    tlz_lz6: float,
    tkon_lz6: float,
) -> BaseDetector:
    """
    Создает детектор ЛЗ v6.
    
    Фазы:
    0: ДАНО - РЦ свободна непрерывно ≥ Ts06
    1: КОГДА - РЦ занята непрерывно ≥ Tlz06 → открытие
    
    Завершение: РЦ свободна ≥ Tkon (FREE_TIME режим)
    """
    
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz6),
            next_phase_id=1,
            timer_mode="continuous",  # Сброс при прерывании свободности
            reset_on_exit=True,
            mask_id=600,  # v6 фаза 0
            mask_fn=mask_ctrl_free,  # Центр свободен
            requires_neighbors=NeighborRequirement.ONLY_CTRL,  # Только контролируемая секция
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_lz6),
            next_phase_id=-1,  # Финал → открытие
            timer_mode="continuous",  # Сброс при прерывании занятости
            reset_on_exit=True,
            mask_id=601,  # v6 фаза 1
            mask_fn=mask_ctrl_occupied,  # Центр занят
            requires_neighbors=NeighborRequirement.ONLY_CTRL,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz6),
        completion_mode=CompletionMode.FREE_TIME,  # Завершение по свободе
        variant_name="v6",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=None,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=None
    )
# variant1_lz_factory.py — РЕФАКТОРИНГ: декларативный стиль, готов к переносу на C

from typing import Optional

from base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from variants_common import mask_000, mask_010

# ID маски для отладки и сериализации
MASK_000 = 0
MASK_010 = 1


def make_lz1_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_lz1: float,
    tlz_lz1: float,
    tkon_lz1: float,
) -> BaseDetector:
    """
    Фабрика детектора ЛЗ v1 (классическая ложная занятость).
    
    Логика: 000 → 010
    - Фаза 0 (idle): все свободны ≥ ts01_lz1
    - Фаза 1 (active): центр занят, края свободны ≥ tlz_lz1 → открытие
    
    Требования: оба соседа должны быть достоверны (prev_control_ok=True, next_control_ok=True)
    
    ДИНАМИЧЕСКАЯ ТОПОЛОГИЯ:
    - prev_rc_name/next_rc_name используются как fallback из конфига
    - Реальные соседи берутся из step.effective_prev_rc / step.effective_next_rc
    - Если effective_*_rc = None — соседа нет (крайняя РЦ или latch истёк)
    
    Эквивалент на C:
    ```c
    PhaseConfig phases[] = {
        {0, ts01, 1, TIMER_CONTINUOUS, true, MASK_000, true, true},
        {1, tlz,  -1, TIMER_CONTINUOUS, true, MASK_010, true, true}
    };
    DetectorConfig cfg = {0, phases, 2, tkon, COMPLETION_FREE_TIME, "v1"};
    BaseDetector det = {cfg, prev, ctrl, next};  // fallback имена
    ```
    """
    
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz1),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_000,
            mask_fn=mask_000,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_lz1),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_010,
            mask_fn=mask_010,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz1),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="v1",
    )
    
    # Декларативный режим: имена РЦ — fallback из конфига
    # Реальная топология из step.effective_*_rc
    return BaseDetector(
        config=config,
        prev_rc_name=prev_rc_name,  # fallback
        ctrl_rc_name=ctrl_rc_name,  # фиксировано
        next_rc_name=next_rc_name,  # fallback
    )


# =========================================================================
# ЭКСПОРТ СХЕМЫ ДЛЯ ВНЕШНИХ ИНСТРУМЕНТОВ
# =========================================================================

V1_SCHEMA = {
    "variant_id": 1,
    "variant_name": "lz1",
    "description": "Классическая ложная занятость: 000 → 010",
    "phases": [
        {
            "phase_id": 0,
            "name": "idle",
            "mask": "000",
            "mask_id": MASK_000,
            "duration_param": "ts01_lz1",
            "requires_prev_ok": True,
            "requires_next_ok": True,
        },
        {
            "phase_id": 1,
            "name": "active",
            "mask": "010",
            "mask_id": MASK_010,
            "duration_param": "tlz_lz1",
            "requires_prev_ok": True,
            "requires_next_ok": True,
        },
    ],
    "completion": {
        "mode": "FREE_TIME",
        "duration_param": "tkon_lz1",
    },
    "parameters": ["ts01_lz1", "tlz_lz1", "tkon_lz1"],
    "topology": "dynamic",  # NEW: поддержка динамической топологии
}

# variant3_lz_factory.py — РЕФАКТОРИНГ: декларативный стиль, готов к переносу на C

from typing import Optional

from base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from variants_common import mask_101, mask_111

# ID маски для отладки
MASK_101 = 2
MASK_111 = 3


def make_lz3_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_lz3: float,
    tlz_lz3: float,
    ts02_lz3: float,
    tkon_lz3: float,
) -> BaseDetector:
    """
    Фабрика детектора ЛЗ v3 (шунтовое движение через секцию).
    
    Логика: 101 → 111 → 101
    - Фаза 0 (p1): края заняты, центр свободен ≥ ts01_lz3
    - Фаза 1 (p2): все заняты ≥ tlz_lz3
    - Фаза 2 (p3): края заняты, центр свободен ≥ ts02_lz3 → открытие
    
    Требования: оба соседа должны быть достоверны.
    
    ДИНАМИЧЕСКАЯ ТОПОЛОГИЯ:
    - prev_rc_name/next_rc_name — fallback из конфига
    - Реальные соседи из step.effective_prev_rc / step.effective_next_rc
    - Если хотя бы один сосед = None — маска 101/111 вернёт False
    
    Эквивалент на C:
    ```c
    PhaseConfig phases[] = {
        {0, ts01, 1, TIMER_CONTINUOUS, true, MASK_101, true, true},
        {1, tlz,  2, TIMER_CONTINUOUS, true, MASK_111, true, true},
        {2, ts02, -1, TIMER_CONTINUOUS, true, MASK_101, true, true}
    };
    ```
    """
    
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz3),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_101,
            mask_fn=mask_101,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_lz3),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_111,
            mask_fn=mask_111,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
        PhaseConfig(
            phase_id=2,
            duration=float(ts02_lz3),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_101,
            mask_fn=mask_101,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz3),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="v3",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )


# =========================================================================
# ЭКСПОРТ СХЕМЫ
# =========================================================================

V3_SCHEMA = {
    "variant_id": 3,
    "variant_name": "lz3",
    "description": "Шунтовое движение: 101 → 111 → 101",
    "phases": [
        {
            "phase_id": 0,
            "name": "p1",
            "mask": "101",
            "mask_id": MASK_101,
            "duration_param": "ts01_lz3",
            "requires_prev_ok": True,
            "requires_next_ok": True,
        },
        {
            "phase_id": 1,
            "name": "p2",
            "mask": "111",
            "mask_id": MASK_111,
            "duration_param": "tlz_lz3",
            "requires_prev_ok": True,
            "requires_next_ok": True,
        },
        {
            "phase_id": 2,
            "name": "p3",
            "mask": "101",
            "mask_id": MASK_101,
            "duration_param": "ts02_lz3",
            "requires_prev_ok": True,
            "requires_next_ok": True,
        },
    ],
    "completion": {
        "mode": "FREE_TIME",
        "duration_param": "tkon_lz3",
    },
    "parameters": ["ts01_lz3", "ts02_lz3", "tlz_lz3", "tkon_lz3"],
    "topology": "dynamic",  # NEW: поддержка динамической топологии
}
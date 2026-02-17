from typing import Callable, Optional

from core.base_detector import (
    BaseDetector,
    CompletionMode,
    DetectorConfig,
    NeighborRequirement,
    PhaseConfig,
)
from core.base_wrapper import BaseVariantWrapper
from core.variants_common import mask_00x, mask_01x, mask_x00, mask_x0x, mask_x10, mask_x1x

# ID масок
MASK_X0X = 9
MASK_X1X = 10
MASK_00X = 11
MASK_01X = 12
MASK_X00 = 13
MASK_X10 = 14


def _make_branch_detector(
    mask_0_id: int,
    mask_0_fn: Callable[..., bool],
    mask_1_id: int,
    mask_1_fn: Callable[..., bool],
    ts01_lz7: float,
    tlz_lz7: float,
    tkon_lz7: float,
    prev_rc_name: Optional[str] = None,
    ctrl_rc_name: str = "",
    next_rc_name: Optional[str] = None,
) -> BaseDetector:
    """Универсальная фабрика одной ветки варианта v7."""

    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz7),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=mask_0_id,
            mask_fn=mask_0_fn,
            requires_neighbors=NeighborRequirement.NONE,
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_lz7),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=mask_1_id,
            mask_fn=mask_1_fn,
            requires_neighbors=NeighborRequirement.NONE,
        ),
    ]

    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz7),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="v7_branch",
    )

    return BaseDetector(
        config=config,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name
    )


def make_lz7_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_lz7: float,
    tlz_lz7: float,
    tkon_lz7: float,
) -> BaseVariantWrapper:
    # Создаем три ветки для разных топологий
    det_no_adjacent = _make_branch_detector(
        MASK_X0X,
        mask_x0x,
        MASK_X1X,
        mask_x1x,
        ts01_lz7,
        tlz_lz7,
        tkon_lz7,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )

    det_no_prev = _make_branch_detector(
        MASK_00X,
        mask_00x,
        MASK_01X,
        mask_01x,
        ts01_lz7,
        tlz_lz7,
        tkon_lz7,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )

    det_no_next = _make_branch_detector(
        MASK_X00,
        mask_x00,
        MASK_X10,
        mask_x10,
        ts01_lz7,
        tlz_lz7,
        tkon_lz7,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )

    return BaseVariantWrapper([det_no_adjacent, det_no_prev, det_no_next])


# =========================================================================
# ЭКСПОРТ СХЕМЫ
# =========================================================================

V7_SCHEMA = {
    "variant_id": 7,
    "variant_name": "lz7",
    "description": "Бесстрелочная РЦ: нет смежных / нет prev / нет next",
    "branches": [
        {
            "branch_name": "no_adjacent",
            "phases": [
                {"mask": "X0X", "mask_id": MASK_X0X},
                {"mask": "X1X", "mask_id": MASK_X1X},
            ],
        },
        {
            "branch_name": "no_prev",
            "phases": [
                {"mask": "00X", "mask_id": MASK_00X},
                {"mask": "01X", "mask_id": MASK_01X},
            ],
        },
        {
            "branch_name": "no_next",
            "phases": [
                {"mask": "X00", "mask_id": MASK_X00},
                {"mask": "X10", "mask_id": MASK_X10},
            ],
        },
    ],
    "completion": {"mode": "FREE_TIME"},
    "parameters": ["ts01_lz7", "tlz_lz7", "tkon_lz7"],
    "topology": "dynamic",
}

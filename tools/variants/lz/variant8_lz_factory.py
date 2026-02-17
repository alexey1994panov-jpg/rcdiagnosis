# -*- coding: utf-8 -*-
# variant8_lz_factory.py — декларативное описание варианта LZ8

from typing import Callable, Optional

from core.base_detector import (
    BaseDetector,
    CompletionMode,
    DetectorConfig,
    NeighborRequirement,
    PhaseConfig,
)
from core.base_wrapper import BaseVariantWrapper
from core.variants_common import (
    mask_010,         # p3 для веток prev/next и p1/p3 для ветки mid
    mask_011,         # p2 для ветки mid
    mask_011_or_111,  # p2 для ветки prev, p1 для ветки next
    mask_01X_or_X10,  # p2 для ветки next
    mask_110_or_111,  # p1 для ветки prev
)

# ID масок
MASK_010 = 2
MASK_011 = 8
MASK_110_OR_111 = 102
MASK_011_OR_111 = 103
MASK_01X_OR_X10 = 104


def _make_branch_detector(
    p0_mask_id: int,
    p0_mask_fn: Callable[..., bool],
    p1_mask_id: int,
    p1_mask_fn: Callable[..., bool],
    p2_mask_id: int,
    p2_mask_fn: Callable[..., bool],
    ts01_lz8: float,
    ts02_lz8: float,
    tlz_lz8: float,
    tkon_lz8: float,
    prev_rc_name: Optional[str] = None,
    ctrl_rc_name: str = "",
    next_rc_name: Optional[str] = None,
) -> BaseDetector:
    """Универсальная фабрика одной ветки варианта v8."""

    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lz8),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=p0_mask_id,
            mask_fn=p0_mask_fn,
            requires_neighbors=NeighborRequirement.BOTH,
            abort_exception_keys=("exc_lz_dsp_timeout",),
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(ts02_lz8),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=p1_mask_id,
            mask_fn=p1_mask_fn,
            requires_neighbors=NeighborRequirement.BOTH,
            abort_exception_keys=("exc_lz_dsp_timeout",),
        ),
        PhaseConfig(
            phase_id=2,
            duration=float(tlz_lz8),
            next_phase_id=-1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=p2_mask_id,
            mask_fn=p2_mask_fn,
            requires_neighbors=NeighborRequirement.BOTH,
            abort_exception_keys=("exc_lz_dsp_timeout",),
        ),
    ]

    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lz8),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name="v8_branch",
    )

    return BaseDetector(
        config=config,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name
    )


def make_lz8_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_lz8: float,
    ts02_lz8: float,
    tlz_lz8: float,
    tkon_lz8: float,
) -> BaseVariantWrapper:
    # Ветка prev
    det_prev = _make_branch_detector(
        MASK_110_OR_111,
        mask_110_or_111,
        MASK_011_OR_111,
        mask_011_or_111,
        MASK_010,
        mask_010,
        ts01_lz8,
        ts02_lz8,
        tlz_lz8,
        tkon_lz8,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )

    # Ветка next
    det_next = _make_branch_detector(
        MASK_011_OR_111,
        mask_011_or_111,
        MASK_01X_OR_X10,
        mask_01X_or_X10,
        MASK_010,
        mask_010,
        ts01_lz8,
        ts02_lz8,
        tlz_lz8,
        tkon_lz8,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )

    # Ветка mid
    det_mid = _make_branch_detector(
        MASK_010,
        mask_010,
        MASK_011,
        mask_011,
        MASK_010,
        mask_010,
        ts01_lz8,
        ts02_lz8,
        tlz_lz8,
        tkon_lz8,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )

    return BaseVariantWrapper([det_prev, det_next, det_mid])


V8_SCHEMA_PREV_BRANCH = {
    "branch_name": "prev",
    "description": "Предыдущая занята (V8.1)",
    "phases": [
        {"phase_id": 0, "mask": "110|111", "mask_id": MASK_110_OR_111, "name": "p1"},
        {"phase_id": 1, "mask": "011|111", "mask_id": MASK_011_OR_111, "name": "p2"},
        {"phase_id": 2, "mask": "010", "mask_id": MASK_010, "name": "p3"},
    ],
}

V8_SCHEMA_NEXT_BRANCH = {
    "branch_name": "next",
    "description": "Следующая занята (V8.2)",
    "phases": [
        {"phase_id": 0, "mask": "011|111", "mask_id": MASK_011_OR_111, "name": "p1"},
        {"phase_id": 1, "mask": "01X|X10", "mask_id": MASK_01X_OR_X10, "name": "p2"},
        {"phase_id": 2, "mask": "010", "mask_id": MASK_010, "name": "p3"},
    ],
}

V8_SCHEMA_MID_BRANCH = {
    "branch_name": "mid",
    "description": "Средний вариант (V8.3)",
    "phases": [
        {"phase_id": 0, "mask": "010", "mask_id": MASK_010, "name": "p1"},
        {"phase_id": 1, "mask": "011", "mask_id": MASK_011, "name": "p2"},
        {"phase_id": 2, "mask": "010", "mask_id": MASK_010, "name": "p3"},
    ],
}

V8_SCHEMA = {
    "variant_id": 8,
    "variant_name": "lz8",
    "description": "Три ветки: предыдущая занята, следующая занята, средний",
    "branches": [V8_SCHEMA_PREV_BRANCH, V8_SCHEMA_NEXT_BRANCH, V8_SCHEMA_MID_BRANCH],
    "completion": {"mode": "FREE_TIME"},
    "parameters": ["ts01_lz8", "ts02_lz8", "tlz_lz8", "tkon_lz8"],
    "features": ["requires_seen_full_adj"],
    "topology": "dynamic",
}

# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.base_detector import BaseDetector


@dataclass
class DetectorsConfig:
    """Конфигурация детекторов для одной контролируемой РЦ."""
    ctrl_rc_id: str
    prev_rc_name: Optional[str] = ""
    ctrl_rc_name: str = ""
    next_rc_name: Optional[str] = ""

    # v1
    ts01_lz1: float = 0.0
    tlz_lz1: float = 0.0
    tkon_lz1: float = 0.0
    enable_lz1: bool = False

    # v2
    ts01_lz2: float = 0.0
    ts02_lz2: float = 0.0
    tlz_lz2: float = 0.0
    tkon_lz2: float = 0.0
    enable_lz2: bool = False

    # v3
    ts01_lz3: float = 0.0
    ts02_lz3: float = 0.0
    tlz_lz3: float = 0.0
    tkon_lz3: float = 0.0
    enable_lz3: bool = False

    # v4
    ts01_lz4: float = 0.0
    tlz_lz4: float = 0.0
    tkon_lz4: float = 0.0
    enable_lz4: bool = False
    sig_lz4_prev_to_ctrl: Optional[str] = None
    sig_lz4_ctrl_to_next: Optional[str] = None

    # v5
    ts01_lz5: float = 0.0
    tlz_lz5: float = 0.0
    tkon_lz5: float = 0.0
    enable_lz5: bool = False

    # v6
    ts01_lz6: float = 0.0
    tlz_lz6: float = 0.0
    tkon_lz6: float = 0.0
    enable_lz6: bool = False

    # v7
    ts01_lz7: float = 0.0
    tlz_lz7: float = 0.0
    tkon_lz7: float = 0.0
    enable_lz7: bool = False

    # v8
    ts01_lz8: float = 0.0
    ts02_lz8: float = 0.0
    tlz_lz8: float = 0.0
    tkon_lz8: float = 0.0
    enable_lz8: bool = False

    # LS9
    ts01_ls9: float = 0.0
    tlz_ls9: float = 0.0
    tkon_ls9: float = 0.0
    enable_ls9: bool = False

    # LS1
    ts01_ls1: float = 0.0
    tlz_ls1: float = 0.0
    tkon_ls1: float = 0.0
    enable_ls1: bool = False

    # LS2
    ts01_ls2: float = 0.0
    tlz_ls2: float = 0.0
    ts02_ls2: float = 0.0
    tkon_ls2: float = 0.0
    enable_ls2: bool = False

    # LS4
    ts01_ls4: float = 0.0
    ts02_ls4: float = 0.0
    tlz01_ls4: float = 0.0
    tlz02_ls4: float = 0.0
    tkon_ls4: float = 0.0
    enable_ls4: bool = False

    # LS5
    ts01_ls5: float = 0.0
    tlz_ls5: float = 0.0
    tkon_ls5: float = 0.0
    enable_ls5: bool = False

    # LZ9
    enable_lz9: bool = False
    ts01_lz9: float = 0.0
    tlz_lz9: float = 0.0
    tkon_lz9: float = 0.0

    # LZ12
    enable_lz12: bool = False
    ts01_lz12: float = 0.0
    ts02_lz12: float = 0.0
    tlz_lz12: float = 0.0
    tkon_lz12: float = 0.0

    # LZ11
    enable_lz11: bool = False
    ts01_lz11: float = 0.0
    tlz_lz11: float = 0.0
    tkon_lz11: float = 0.0
    sig_lz11_a: Optional[str] = None
    sig_lz11_b: Optional[str] = None

    # LZ13
    enable_lz13: bool = False
    ts01_lz13: float = 0.0
    ts02_lz13: float = 0.0
    tlz_lz13: float = 0.0
    tkon_lz13: float = 0.0
    sig_lz13_prev: Optional[str] = None
    sig_lz13_next: Optional[str] = None

    # LZ10
    enable_lz10: bool = False
    ts01_lz10: float = 0.0
    ts02_lz10: float = 0.0
    ts03_lz10: float = 0.0
    tlz_lz10: float = 0.0
    tkon_lz10: float = 0.0
    sig_lz10_to_next: Optional[str] = None
    sig_lz10_to_prev: Optional[str] = None

    # LS6
    enable_ls6: bool = False
    ts01_ls6: float = 0.0
    tlz_ls6: float = 0.0
    tkon_ls6: float = 0.0
    sig_ls6_prev: Optional[str] = None

    # Exceptions
    enable_lz_exc_mu: bool = False
    enable_lz_exc_recent_ls: bool = False
    enable_lz_exc_dsp: bool = False
    enable_ls_exc_mu: bool = False
    enable_ls_exc_after_lz: bool = False
    enable_ls_exc_dsp: bool = False
    # Если задано, DSP-исключение ЛЗ применяется только к указанным вариантам (например [3, 8]).
    # Пусто/None: применяется ко всем ЛЗ-вариантам.
    lz_exc_dsp_variants: Optional[List[int]] = None
    t_mu: float = 15.0
    t_recent_ls: float = 30.0
    t_min_maneuver_v8: float = 600.0
    t_ls_mu: float = 15.0
    t_ls_after_lz: float = 30.0
    t_ls_dsp: float = 600.0


@dataclass
class DetectorsState:
    """Состояние всех детекторов для одной контролируемой РЦ."""
    v1: Optional[BaseDetector] = None
    v2: Optional[Any] = None
    v3: Optional[BaseDetector] = None
    v4: Optional[Any] = None
    v5: Optional[BaseDetector] = None
    v6: Optional[BaseDetector] = None
    v7: Optional[Any] = None
    v8: Optional[Any] = None
    ls9: Optional[BaseDetector] = None
    ls1: Optional[BaseDetector] = None
    ls2: Optional[Any] = None
    ls4: Optional[BaseDetector] = None
    ls5: Optional[Any] = None
    lz9: Optional[Any] = None
    lz12: Optional[Any] = None
    lz11: Optional[Any] = None
    lz13: Optional[Any] = None
    lz10: Optional[Any] = None
    ls6: Optional[Any] = None

    last_effective_prev: Optional[str] = None
    last_effective_next: Optional[str] = None


@dataclass
class DetectorsResult:
    """Результат обновления детекторов."""
    opened: bool = False
    closed: bool = False
    ls5_open: bool = False
    ls5_closed: bool = False
    lz9_open: bool = False
    lz9_closed: bool = False
    lz12_open: bool = False
    lz12_closed: bool = False
    lz11_open: bool = False
    lz11_closed: bool = False
    lz13_open: bool = False
    lz13_closed: bool = False
    lz4_open: bool = False
    lz4_closed: bool = False
    lz10_open: bool = False
    lz10_closed: bool = False
    ls6_open: bool = False
    ls6_closed: bool = False
    active_variant: int = 0
    open_offset: Optional[float] = None
    close_offset: Optional[float] = None
    flags: List[str] = field(default_factory=list)

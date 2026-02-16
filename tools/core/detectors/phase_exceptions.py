# -*- coding: utf-8 -*-
from typing import List, Tuple

from core.base_detector import BaseDetector
from core.detectors.types import DetectorsConfig, DetectorsState


def iter_base_detectors_with_key(det_state: DetectorsState):
    """Итерирует все BaseDetector в состоянии, включая ветки wrapper-вариантов."""
    for key in (
        "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8",
        "ls9", "ls1", "ls2", "ls4", "ls5", "ls6",
        "lz9", "lz10", "lz11", "lz12", "lz13",
    ):
        obj = getattr(det_state, key, None)
        if obj is None:
            continue
        if isinstance(obj, BaseDetector):
            yield key, obj
            continue
        detectors = getattr(obj, "detectors", None)
        if isinstance(detectors, list):
            for det in detectors:
                if isinstance(det, BaseDetector):
                    yield key, det


def detector_family(det_key: str) -> str:
    if det_key.startswith("ls"):
        return "ls"
    return "lz"


def exception_keys_for_detector(cfg: DetectorsConfig, det_key: str) -> Tuple[str, ...]:
    family = detector_family(det_key)
    keys: List[str] = []
    if family == "lz":
        if cfg.enable_lz_exc_mu:
            keys.append("exc_lz_mu_active")
        if cfg.enable_lz_exc_recent_ls:
            keys.append("exc_lz_recent_ls")
    else:
        if cfg.enable_ls_exc_mu:
            keys.append("exc_ls_mu_active")
        if cfg.enable_ls_exc_after_lz:
            keys.append("exc_ls_after_lz")
        if cfg.enable_ls_exc_dsp:
            keys.append("exc_ls_dsp_timeout")
    return tuple(keys)


def merge_abort_keys(existing: Tuple[str, ...], extra: Tuple[str, ...]) -> Tuple[str, ...]:
    out: List[str] = []
    for k in list(existing or ()) + list(extra or ()):
        if k and k not in out:
            out.append(k)
    return tuple(out)


def apply_phase_exception_policy(cfg: DetectorsConfig, state: DetectorsState) -> None:
    """
    Навешивает фазовые исключения на фазы открытия.
    - Для LS/LZ MU/recent/after_lz: только финальная фаза (next_phase_id < 0)
    - Для LZ DSP: все фазы формирования (с возможностью фильтра по вариантам).
    """
    selected_dsp_variants = {
        int(v)
        for v in (cfg.lz_exc_dsp_variants or [])
        if isinstance(v, int) or (isinstance(v, str) and str(v).strip().isdigit())
    }
    for det_key, det in iter_base_detectors_with_key(state):
        family = detector_family(det_key)
        extra_final = exception_keys_for_detector(cfg, det_key)
        extra_all: Tuple[str, ...] = ()
        if family == "lz" and cfg.enable_lz_exc_dsp:
            apply_dsp_for_detector = True
            if selected_dsp_variants:
                variant_num = 0
                if det_key.startswith("v"):
                    suffix = det_key[1:]
                    if suffix.isdigit():
                        variant_num = int(suffix)
                elif det_key.startswith("lz") and det_key[2:].isdigit():
                    variant_num = int(det_key[2:])
                apply_dsp_for_detector = variant_num in selected_dsp_variants
            if apply_dsp_for_detector:
                extra_all = ("exc_lz_dsp_timeout",)

        for phase in det.config.phases:
            if extra_all:
                phase.abort_exception_keys = merge_abort_keys(
                    phase.abort_exception_keys,
                    extra_all,
                )
            if int(phase.next_phase_id) < 0 and extra_final:
                phase.abort_exception_keys = merge_abort_keys(
                    phase.abort_exception_keys,
                    extra_final,
                )

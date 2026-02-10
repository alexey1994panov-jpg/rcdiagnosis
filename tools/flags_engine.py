from dataclasses import dataclass
from typing import Dict, List

from uni_states import rc_is_free, rc_is_occupied
from detectors_engine import DetectorsState, DetectorsResult


@dataclass
class FlagsResult:
    flags: List[str]
    lz: bool
    variant: int


def build_flags_simple(
    ctrl_rc_id: str,
    det_state: DetectorsState,
    det_result: DetectorsResult,
    rc_states: Dict[str, int],
    switch_states: Dict[str, int],
) -> FlagsResult:
    """
    Сборка флагов с учетом variant1, variant2, variant3, variant7, variant8.
    
    Адаптирована под новую структуру:
    - det_state.v1, v2, v3, v7, v8 — объекты детекторов (или None)
    - det_result — результат update_detectors с opened/closed флагами
    """

    flags: List[str] = list(det_result.flags)  # Копируем флаги из результата

    rc_state = rc_states.get(ctrl_rc_id, 0)
    curr_free = rc_is_free(rc_state)
    curr_occ = rc_is_occupied(rc_state)

    # Активность детекторов — из объектов (новая структура)
    v1_active = det_state.v1.active if det_state.v1 else False
    v2_active = det_state.v2.active if det_state.v2 else False
    v3_active = det_state.v3.active if det_state.v3 else False
    v5_active = det_state.v5.active if det_state.v5 else False
    v6_active = det_state.v6.active if det_state.v6 else False
    v7_active = det_state.v7.active if det_state.v7 else False
    v8_active = det_state.v8.active if det_state.v8 else False
    ls9_active = det_state.ls9.active if det_state.ls9 else False
    ls1_active = det_state.ls1.active if det_state.ls1 else False
    ls2_active = det_state.ls2.active if det_state.ls2 else False
    ls4_active = det_state.ls4.active if det_state.ls4 else False
    ls5_active = det_state.ls5.active if det_state.ls5 else False
    lz9_active = det_state.lz9.active if det_state.lz9 else False
    lz12_active = det_state.lz12.active if det_state.lz12 else False
    lz11_active = det_state.lz11.active if det_state.lz11 else False
    lz13_active = det_state.lz13.active if det_state.lz13 else False
    lz10_active = det_state.lz10.active if det_state.lz10 else False
    ls6_active = det_state.ls6.active if det_state.ls6 else False

    # Номер варианта: приоритет ls9 > ls1 > v8 > v7 > v3 > v2 > v1
    variant = 0
    if ls9_active:
        variant = 109  # LS9
    elif ls6_active:
        variant = 106  # LS6
    elif ls5_active:
        variant = 105  # LS5
    elif ls4_active:
        variant = 104  # LS4
    elif ls2_active:
        variant = 102  # LS2
    elif ls1_active:
        variant = 101  # LS1
    elif lz13_active:
        variant = 13
    elif lz12_active:
        variant = 12
    elif lz11_active:
        variant = 11
    elif lz10_active:
        variant = 10
    elif lz9_active:
        variant = 9
    elif v8_active:
        variant = 8
    elif v7_active:
        variant = 7
    elif v6_active:
        variant = 6
    elif v5_active:
        variant = 5
    elif v3_active:
        variant = 3
    elif v2_active:
        variant = 2
    elif v1_active:
        variant = 1

    # Добавляем флаги активности (если ещё не добавлены из det_result)
    if v1_active and "llz_v1" not in flags:
        flags.append("llz_v1")
    if v2_active and "llz_v2" not in flags:
        flags.append("llz_v2")
    if v3_active and "llz_v3" not in flags:
        flags.append("llz_v3")
    if v5_active and "llz_v5" not in flags:
        flags.append("llz_v5")
    if v6_active and "llz_v6" not in flags:
        flags.append("llz_v6")
    if v7_active and "llz_v7" not in flags:
        flags.append("llz_v7")
    if v8_active and "llz_v8" not in flags:
        flags.append("llz_v8")
    if ls9_active and "lls_9" not in flags:
        flags.append("lls_9")
    if ls1_active and "lls_1" not in flags:
        flags.append("lls_1")
    if ls2_active and "lls_2" not in flags:
        flags.append("lls_2")
    if ls4_active and "lls_4" not in flags:
        flags.append("lls_4")
    if ls5_active and "lls_5" not in flags:
        flags.append("lls_5")
    if lz9_active and "llz_v9" not in flags:
        flags.append("llz_v9")
    if lz12_active and "llz_v12" not in flags:
        flags.append("llz_v12")
    if lz11_active and "llz_v11" not in flags:
        flags.append("llz_v11")
    if lz13_active and "llz_v13" not in flags:
        flags.append("llz_v13")
    if lz10_active and "llz_v10" not in flags:
        flags.append("llz_v10")
    if ls6_active and "lls_6" not in flags:
        flags.append("lls_6")
    
    # Флаги открытия/закрытия
    if det_result.ls5_open: flags.append("lls_5_open")
    if det_result.ls5_closed: flags.append("lls_5_closed")
    if det_result.lz9_open: flags.append("llz_v9_open")
    if det_result.lz9_closed: flags.append("llz_v9_closed")
    if det_result.lz12_open: flags.append("llz_v12_open")
    if det_result.lz12_closed: flags.append("llz_v12_closed")
    if det_result.lz11_open: flags.append("llz_v11_open")
    if det_result.lz11_closed: flags.append("llz_v11_closed")
    if det_result.lz13_open: flags.append("llz_v13_open")
    if det_result.lz13_closed: flags.append("llz_v13_closed")
    if det_result.lz10_open: flags.append("llz_v10_open")
    if det_result.lz10_closed: flags.append("llz_v10_closed")
    if det_result.ls6_open: flags.append("lls_6_open")
    if det_result.ls6_closed: flags.append("lls_6_closed")

    # Базовая ЛЗ/ЛС: по активности любого детектора
    lz = bool(
        v1_active or v2_active or v3_active or v5_active or v6_active or v7_active or v8_active or
        ls9_active or ls6_active or ls5_active or ls4_active or ls2_active or ls1_active or
        lz9_active or lz10_active or lz11_active or lz12_active or lz13_active
    )

    # Качество ЛЗ
    if lz and curr_free:
        flags.append("false_lz")
    if (not lz) and curr_occ:
        flags.append("no_lz_when_occupied")

    # Пока без проверки потери контроля стрелки
    _ = switch_states

    return FlagsResult(flags=flags, lz=lz, variant=variant)
from typing import List
from .station_visochino_1p import rc_is_free, rc_is_occupied, sw_lost_control


class FlagsResult:
    def __init__(self) -> None:
        self.flags: List[str] = []
        self.lz: bool = False
        self.variant: int = 0


def build_flags(
    ds_active_v1: bool,
    ds_active_v2: bool,
    ds_active_v3: bool,
    ds_active_v8: bool,
    ls_active_v1: bool,
    ls_active_v2: bool,
    ls_active_v4: bool,
    ls_active_v9: bool,
    opened_res,
    closed_res,
    rc_1p_state: int,
    sw10_state: int,
    lz_suppressed: bool = False,
) -> FlagsResult:
    """
    Унифицированная сборка флагов по состояниям детекторов и событиям opened/closed.

    Параметр lz_suppressed зарезервирован для слоя исключений:
    если True, логическая занятость будет принудительно подавлена,
    а в флагах появится 'lz_suppressed_by_exception'.
    """
    r = FlagsResult()

    curr_free = rc_is_free(rc_1p_state)
    curr_occ = rc_is_occupied(rc_1p_state)

    # Вариант ЛЗ по приоритету (как в simulate_1p)
    if ds_active_v1:
        r.variant = 1
    if ds_active_v2:
        r.variant = 2
    if ds_active_v3:
        r.variant = 3
    if ds_active_v8:
        r.variant = 8

    # Активность ЛЗ
    if ds_active_v1:
        r.flags.append("llz_v1")
    if ds_active_v2:
        r.flags.append("llz_v2")
    if ds_active_v3:
        r.flags.append("llz_v3")
    if ds_active_v8:
        r.flags.append("llz_v8")

    # Активность ЛС
    if ls_active_v1:
        r.flags.append("lls_v1")
    if ls_active_v2:
        r.flags.append("lls_v2")
    if ls_active_v4:
        r.flags.append("lls_v4")
    if ls_active_v9:
        r.flags.append("lls_v9")

    # Открытие ЛЗ
    if opened_res.opened_v1:
        r.flags.append("llz_v1_open")
    if opened_res.opened_v2:
        r.flags.append("llz_v2_open")
    if opened_res.opened_v3:
        r.flags.append("llz_v3_open")
    if opened_res.opened_v8:
        r.flags.append("llz_v8_open")

    # Открытие ЛС
    if opened_res.opened_ls1:
        r.flags.append("lls_v1_open")
    if opened_res.opened_ls2:
        r.flags.append("lls_v2_open")
    if opened_res.opened_ls4:
        r.flags.append("lls_v4_open")
    if opened_res.opened_ls9:
        r.flags.append("lls_v9_open")

    # Закрытие ЛЗ: только если ЛЗ НЕ подавлена исключением
    if not lz_suppressed:
        if closed_res.closed_v1:
            r.flags.append("llz_v1_closed")
        if closed_res.closed_v2:
            r.flags.append("llz_v2_closed")
        if closed_res.closed_v3:
            r.flags.append("llz_v3_closed")
        if closed_res.closed_v8:
            r.flags.append("llz_v8_closed")

    # Закрытие ЛС
    if closed_res.closed_ls1:
        r.flags.append("lls_v1_closed")
    if closed_res.closed_ls2:
        r.flags.append("lls_v2_closed")
    if closed_res.closed_ls4:
        r.flags.append("lls_v4_closed")
    if closed_res.closed_ls9:
        r.flags.append("lls_v9_closed")

    # Базовая логическая занятость
    r.lz = (
        curr_occ
        or ds_active_v1
        or ds_active_v2
        or ds_active_v3
        or ds_active_v8
    )

    # Исключения: подавление ЛЗ
    if lz_suppressed and r.lz:
        r.lz = False
        # Сносим все флаги ЛЗ, включая активность и open/closed
        r.flags = [f for f in r.flags if not f.startswith("llz_v")]
        r.flags.append("lz_suppressed_by_exception")

    # Качество ЛЗ (false_lz / no_lz_when_occupied / потеря контроля стрелки)
    v1_free_ok = ds_active_v1 and curr_free
    if r.lz and curr_free and not v1_free_ok:
        r.flags.append("false_lz")
    if (not r.lz) and curr_occ:
        r.flags.append("no_lz_when_occupied")
    if r.lz and sw_lost_control(sw10_state):
        r.flags.append("switch_lost_control_with_lz")

    return r

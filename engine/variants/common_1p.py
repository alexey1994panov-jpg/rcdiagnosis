# engine/variants/common_1p.py

from typing import List, Any

from ..station_visochino_1p import rc_is_free, rc_is_occupied


def get_mode(step: Any, name: str, default: bool = False) -> bool:
    """Безопасное чтение флага из modes."""
    return bool(step.modes.get(name, default))


def is_exception(prev_history: List[Any], curr_idx: int) -> bool:
    """
    Заглушка исключений формирования ДС.

    Для всех вариантов (1, 2, 3, 8 и т.д.) сейчас считаем, что исключений нет.
    При необходимости сюда можно добавить:
      - анализ последних шагов по prev_history;
      - учёт спец. флагов в step.modes (например, 'exception_v3_*', 'exception_v8_*').
    """
    return False


def pattern_holds(
    history: List[Any],
    idx: int,
    duration_s: int,
    p_prev: int,
    p_curr: int,
    p_next: int,
) -> bool:
    """
    Проверка, что в интервале [t_now - duration_s, t_now] выдерживается
    заданный паттерн по предыдущей, текущей и следующей РЦ.

    p_*:
      -1 = не проверять,
       0 = свободна,
       1 = занята.

    Может использоваться для любых вариантов ЛЗ (1, 2, 3, 8, ...),
    в том числе для паттернов 1‑0‑1, 1‑1‑1, 1‑1‑0 и т.п.
    """
    if duration_s <= 0:
        return True

    t_now = history[idx].t
    t_min = t_now - duration_s

    k = idx
    while k >= 0 and history[k].t >= t_min:
        step = history[k]

        st_prev = step.rc_states.get("10-12SP", 0)
        st_curr = step.rc_states.get("1P", 0)
        st_next = step.rc_states.get("1-7SP", 0)

        if p_prev != -1:
            if p_prev == 0 and not rc_is_free(st_prev):
                return False
            if p_prev == 1 and not rc_is_occupied(st_prev):
                return False

        if p_curr != -1:
            if p_curr == 0 and not rc_is_free(st_curr):
                return False
            if p_curr == 1 and not rc_is_occupied(st_curr):
                return False

        if p_next != -1:
            if p_next == 0 and not rc_is_free(st_next):
                return False
            if p_next == 1 and not rc_is_occupied(st_next):
                return False

        k -= 1

    return True

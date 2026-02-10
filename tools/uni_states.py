# -*- coding: utf-8 -*-
"""
Утилиты для интерпретации Uni_State_ID по РЦ, стрелкам и светофорам.
"""

# ---------- Общая часть ----------

def no_control_state(uni_state_id: int) -> bool:
    """Универсальное отсутствие контроля / некорректное состояние."""
    return uni_state_id in (0, 1, 2, 100)


# ---------- РЦ (Рельсовые цепи) ----------

def rc_is_free(uni_state_id: int) -> bool:
    """РЦ свободна: Uni_State_ID из списка {3, 4, 5}."""
    return uni_state_id in (3, 4, 5)


def rc_is_occupied(uni_state_id: int) -> bool:
    """РЦ занята: Uni_State_ID из списка {6, 7, 8}."""
    return uni_state_id in (6, 7, 8)


def rc_is_locked(uni_state_id: int) -> bool:
    """
    РЦ замкнута (З=1).
    Определяется по конкретным кодам Uni_State_ID:
    4 — свободна, замкнута
    5 — свободна, замкнута (искусственное размыкание)
    7 — занята, замкнута
    8 — занята, замкнута (искусственное размыкание)
    """
    return uni_state_id in (4, 5, 7, 8)


def rc_no_control(uni_state_id: int) -> bool:
    """Отсутствие контроля РЦ."""
    return no_control_state(uni_state_id)


# ---------- Стрелки ----------

def sw_is_plus(uni_state_id: int) -> bool:
    """Стрелка в ПК: Uni_State_ID 3–8."""
    return uni_state_id in (3, 4, 5, 6, 7, 8)


def sw_is_minus(uni_state_id: int) -> bool:
    """Стрелка в МК: Uni_State_ID 9–14."""
    return uni_state_id in (9, 10, 11, 12, 13, 14)


def sw_no_control(uni_state_id: int) -> bool:
    """Потеря контроля или некорректное состояние стрелки."""
    # 15-20 — это специфические стейты потери контроля для стрелок
    return no_control_state(uni_state_id) or (15 <= uni_state_id <= 20)


# ---------- Светофоры (Поездные) ----------

def signal_is_open(uni_state_id: int) -> bool:
    """Светофор открыт на разрешающее показание (поездное)."""
    # Список кодов из вашего протокола
    return uni_state_id in {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 20, 22, 23, 24}


def signal_is_closed(uni_state_id: int) -> bool:
    """Светофор закрыт (красный)."""
    return uni_state_id == 15


# ---------- Светофоры (Маневровые) ----------

def shunting_signal_is_open(uni_state_id: int) -> bool:
    """Маневровый светофор открыт (белый). Обычно стейт 4 или 5."""
    return uni_state_id in (4, 5)


def shunting_signal_is_closed(uni_state_id: int) -> bool:
    """Маневровый светофор закрыт (синий или красный)."""
    return uni_state_id in (3, 7)
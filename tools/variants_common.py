from typing import Any, Optional
from uni_states import rc_is_free, rc_is_occupied, rc_is_locked, signal_is_closed, shunting_signal_is_closed, signal_is_open, shunting_signal_is_open
from station_config import NODES


# ============================================================================
# БАЗОВЫЕ МАСКИ (все комбинации для трёх РЦ)
# ============================================================================

def mask_000(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-0-0: Все три РЦ свободны.
    ДИНАМИЧЕСКАЯ ТОПОЛОГИЯ: если сосед = None, считаем его условно "свободным"
    (для крайних РЦ — важно только состояние ctrl и существующих соседей)
    """
    if not ctrl:
        return False
    
    s_prev = step.rc_states.get(prev, 0) if prev else 0
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0) if next else 0
    
    # None считаем свободным (0), но только если ctrl свободен
    prev_ok = rc_is_free(s_prev) if prev else True
    next_ok = rc_is_free(s_next) if next else True
    
    return prev_ok and rc_is_free(s_ctrl) and next_ok


def mask_010(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-1-0: Центр занят, края свободны.
    ДИНАМИЧЕСКАЯ ТОПОЛОГИЯ: None = "свободен" (нет соседа = не мешает)
    """
    if not ctrl:
        return False
    
    s_prev = step.rc_states.get(prev, 0) if prev else 0
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0) if next else 0
    
    prev_ok = rc_is_free(s_prev) if prev else True
    next_ok = rc_is_free(s_next) if next else True
    
    return prev_ok and rc_is_occupied(s_ctrl) and next_ok


def mask_101(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    1-0-1: Края заняты, центр свободен.
    ТРЕБУЕТ ОБОИХ СОСЕДЕЙ: если prev или next = None — False
    """
    if not ctrl or prev is None or next is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    
    return rc_is_occupied(s_prev) and rc_is_free(s_ctrl) and rc_is_occupied(s_next)


def mask_111(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    1-1-1: Все три РЦ заняты.
    ТРЕБУЕТ ОБОИХ СОСЕДЕЙ: если prev или next = None — False
    """
    if not ctrl or prev is None or next is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    
    return rc_is_occupied(s_prev) and rc_is_occupied(s_ctrl) and rc_is_occupied(s_next)


# ============================================================================
# МАСКИ ДЛЯ v2 (асимметричные — один сосед занят)
# ============================================================================

def mask_100(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    1-0-0: Prev занят, ctrl и next свободны.
    ТРЕБУЕТ prev: если prev = None — False
    """
    if not ctrl or prev is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0) if next else 0
    
    return rc_is_occupied(s_prev) and rc_is_free(s_ctrl) and rc_is_free(s_next)


def mask_110(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    1-1-0: Prev и ctrl заняты, next свободен.
    ТРЕБУЕТ prev: если prev = None — False
    """
    if not ctrl or prev is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0) if next else 0
    
    return rc_is_occupied(s_prev) and rc_is_occupied(s_ctrl) and rc_is_free(s_next)


def mask_100_or_000(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """1-0-0 ИЛИ 0-0-0: Возврат к начальному состоянию или полный сброс."""
    return mask_100(step, prev, ctrl, next) or mask_000(step, prev, ctrl, next)


def mask_001(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-0-1: Next занят, prev и ctrl свободны.
    ТРЕБУЕТ next: если next = None — False
    """
    if not ctrl or next is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0) if prev else 0
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    
    return rc_is_free(s_prev) and rc_is_free(s_ctrl) and rc_is_occupied(s_next)


def mask_011(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-1-1: Ctrl и next заняты, prev свободен.
    ТРЕБУЕТ next: если next = None — False
    """
    if not ctrl or next is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0) if prev else 0
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    
    return rc_is_free(s_prev) and rc_is_occupied(s_ctrl) and rc_is_occupied(s_next)


def mask_001_or_000(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """0-0-1 ИЛИ 0-0-0: Возврат или сброс."""
    return mask_001(step, prev, ctrl, next) or mask_000(step, prev, ctrl, next)


# ============================================================================
# МАСКИ ДЛЯ v7 (бесстрелочные — учёт отсутствия соседей)
# ============================================================================

def mask_x0x(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    X-0-X: Центр свободен, края не важны (могут отсутствовать).
    Для v7 no_adjacent: нет смежных РЦ вообще (prev=None И next=None)
    """
    if not ctrl:
        return False
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_free(s_ctrl)


def mask_x0x_occ(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """X-0-X (занятость): Центр занят, края не важны."""
    if not ctrl:
        return False
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_occupied(s_ctrl)


def mask_00x(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-0-X: prev и ctrl свободны, next не важен (м.б. None).
    Для v7 no_prev: нет предыдущей (prev=None), есть следующая (next!=None)
    """
    if not ctrl:
        return False
    
    # prev должен отсутствовать (None) или быть свободным
    s_prev = step.rc_states.get(prev, 0) if prev else 0
    prev_ok = (prev is None) or rc_is_free(s_prev)
    
    s_ctrl = step.rc_states.get(ctrl, 0)
    
    # next должен существовать и быть свободным
    if next is None:
        return False
    s_next = step.rc_states.get(next, 0)
    next_ok = rc_is_free(s_next)
    
    return prev_ok and rc_is_free(s_ctrl) and next_ok


def mask_00x_occ(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """0-0-X с центром занятым — фаза 1 для no_prev."""
    if not ctrl or next is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0) if prev else 0
    prev_ok = (prev is None) or rc_is_free(s_prev)
    
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    next_ok = rc_is_free(s_next)  # next должен остаться свободным!
    
    return prev_ok and rc_is_occupied(s_ctrl) and next_ok


def mask_x00(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    X-0-0: ctrl и next свободны, prev не важен.
    Для v7 no_next: есть предыдущая (prev!=None), нет следующей (next=None)
    """
    if not ctrl:
        return False
    
    # prev должен существовать и быть свободным
    if prev is None:
        return False
    s_prev = step.rc_states.get(prev, 0)
    prev_ok = rc_is_free(s_prev)
    
    s_ctrl = step.rc_states.get(ctrl, 0)
    
    # next должен отсутствовать (None) или быть свободным
    s_next = step.rc_states.get(next, 0) if next else 0
    next_ok = (next is None) or rc_is_free(s_next)
    
    return prev_ok and rc_is_free(s_ctrl) and next_ok


def mask_x00_occ(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """X-0-0 с центром занятым — фаза 1 для no_next."""
    if not ctrl or prev is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0)
    prev_ok = rc_is_free(s_prev)  # prev должен остаться свободным!
    
    s_ctrl = step.rc_states.get(ctrl, 0)
    
    s_next = step.rc_states.get(next, 0) if next else 0
    next_ok = (next is None) or rc_is_free(s_next)
    
    return prev_ok and rc_is_occupied(s_ctrl) and next_ok


# ============================================================================
# МАСКИ ДЛЯ v8 (составные условия)
# ============================================================================

def mask_110_or_111(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    1-1-0 или 1-1-1: prev и ctrl заняты, next любой.
    ТРЕБУЕТ prev: если prev = None — False
    """
    if not ctrl or prev is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    
    return rc_is_occupied(s_prev) and rc_is_occupied(s_ctrl)


def mask_011_or_111(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-1-1 или 1-1-1: ctrl и next заняты, prev любой.
    ТРЕБУЕТ next: если next = None — False
    """
    if not ctrl or next is None:
        return False
    
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    
    return rc_is_occupied(s_ctrl) and rc_is_occupied(s_next)


def mask_01x_or_x10(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-1-X или X-1-0: ctrl занят, и (prev свободен ИЛИ next свободен).
    ДИНАМИЧЕСКАЯ ТОПОЛОГИЯ: None считаем "свободным" (нет соседа = не мешает)
    """
    if not ctrl:
        return False
    
    s_prev = step.rc_states.get(prev, 0) if prev else 0
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0) if next else 0
    
    curr_occ = rc_is_occupied(s_ctrl)
    prev_free = rc_is_free(s_prev) if prev else True  # None = свободен
    next_free = rc_is_free(s_next) if next else True  # None = свободен
    
    return curr_occ and (prev_free or next_free)

# ============================================================================
# МАСКИ ДЛЯ v5 (учет замыкания, смежные не важны)
# ============================================================================

def mask_0_not_locked(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """Фаза ДАНО: РЦ свободна, не замкнута И can_lock=True."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    
    # Базовое условие: свободна и не замкнута
    if not (rc_is_free(s_ctrl) and not rc_is_locked(s_ctrl)):
        return False
    
    # Проверка can_lock через rc_capabilities
    caps = getattr(step, 'rc_capabilities', {})
    ctrl_caps = caps.get(ctrl, {})
    return ctrl_caps.get('can_lock', False)


def mask_1_not_locked(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """Фаза КОГДА: РЦ занята, не замкнута И can_lock=True."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    
    # Базовое условие: занята и не замкнута
    if not (rc_is_occupied(s_ctrl) and not rc_is_locked(s_ctrl)):
        return False
    
    # Проверка can_lock через rc_capabilities
    caps = getattr(step, 'rc_capabilities', {})
    ctrl_caps = caps.get(ctrl, {})
    return ctrl_caps.get('can_lock', False)

def mask_ctrl_free(step, prev, ctrl, next) -> bool:
    """
    Маска v6 фаза 0: контролируемая РЦ свободна.
    ctrl - это ID РЦ (строка), нужно взять состояние из step.rc_states
    """
    if not ctrl:
        return False
    # Получаем состояние РЦ (0=свободна, 1=занята, и т.д.)
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_free(s_ctrl)


def mask_ctrl_occupied(step, prev, ctrl, next) -> bool:
    """
    Маска v6 фаза 1: контролируемая РЦ занята.
    """
    if not ctrl:
        return False
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_occupied(s_ctrl)


# ============================================================================
# МАСКИ ДЛЯ LS5 (учет замыкания на смежных)
# ============================================================================

def mask_ls5_prev_locked_p0(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LS5 Branch Prev Phase 0: Prev(Occ+Lock), Ctrl(Free+Lock)"""
    if not ctrl or prev is None:
        return False
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_occupied(s_prev) and rc_is_locked(s_prev) and \
           rc_is_free(s_ctrl) and rc_is_locked(s_ctrl)


def mask_ls5_next_locked_p0(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LS5 Branch Next Phase 0: Next(Occ+Lock), Ctrl(Free+Lock)"""
    if not ctrl or next is None:
        return False
    s_next = step.rc_states.get(next, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_occupied(s_next) and rc_is_locked(s_next) and \
           rc_is_free(s_ctrl) and rc_is_locked(s_ctrl)


def mask_ls5_both_locked_p1(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LS5 Phase 1: Both(Occ+Lock), Ctrl(Free+Lock)"""
    if not ctrl or prev is None or next is None:
        return False
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    return rc_is_occupied(s_prev) and rc_is_locked(s_prev) and \
           rc_is_occupied(s_next) and rc_is_locked(s_next) and \
           rc_is_free(s_ctrl) and rc_is_locked(s_ctrl)


# ============================================================================
# МАСКИ ДЛЯ LZ12 (крайние секции NC)
# ============================================================================

def mask_lz12_prev_nc_p0(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ12 Ветка Prev NC Фаза 0: Сосед NC, Центр свободен."""
    if not step.modes.get("prev_nc", False):
        return False
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_free(s_ctrl)

def mask_lz12_prev_nc_p1(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ12 Ветка Prev NC Фаза 1: Сосед NC, Центр занят."""
    if not step.modes.get("prev_nc", False):
        return False
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_occupied(s_ctrl)

def mask_lz12_next_nc_p0(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ12 Ветка Next NC Фаза 0: Сосед NC, Центр свободен."""
    if not step.modes.get("next_nc", False):
        return False
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_free(s_ctrl)

def mask_lz12_next_nc_p1(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ12 Ветка Next NC Фаза 1: Сосед NC, Центр занят."""
    if not step.modes.get("next_nc", False):
        return False
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_occupied(s_ctrl)

# ============================================================================
# МАСКИ ДЛЯ LZ9 (пробой стыка)
# ============================================================================

def _is_free_or_nc(step: Any, rc_id: Optional[str], side: str) -> bool:
    """Хелпер: РЦ свободна ИЛИ находится в состоянии NC (край)."""
    if not rc_id or step.modes.get(f"{side}_nc", False):
        return True
    return rc_is_free(step.rc_states.get(rc_id, 0))

def _is_occ_and_not_nc(step: Any, rc_id: Optional[str], side: str) -> bool:
    """Хелпер: РЦ занята (и она точно существует, не NC)."""
    if not rc_id or step.modes.get(f"{side}_nc", False):
        return False
    return rc_is_occupied(step.rc_states.get(rc_id, 0))

def _is_locked(step: Any, rc_id: Optional[str]) -> bool:
    """Хелпер: РЦ замкнута (З=1)."""
    if not rc_id:
        return False
    return rc_is_locked(step.rc_states.get(rc_id, 0))

def _is_signal_closed(step: Any, sig_id: Optional[str]) -> bool:
    """Хелпер: светофор закрыт."""
    if not sig_id:
        return True
    st = step.signal_states.get(sig_id, 0)
    
    node = NODES.get(sig_id)
    if node:
        t = node.get("type")
        if t == 3: # Shunting
            return shunting_signal_is_closed(st)
        if t == 4: # Train
            return signal_is_closed(st)
            
    # Fallback: check both if type unknown
    return signal_is_closed(st) or shunting_signal_is_closed(st)

def _is_signal_open(step: Any, sig_id: Optional[str]) -> bool:
    """Хелпер: светофор открыт."""
    if not sig_id:
        return False
    st = step.signal_states.get(sig_id, 0)
    
    node = NODES.get(sig_id)
    if node:
        t = node.get("type")
        if t == 3: # Shunting
            return shunting_signal_is_open(st)
        if t == 4: # Train
            return signal_is_open(st)
            
    # Fallback: check both if type unknown
    return signal_is_open(st) or shunting_signal_is_open(st)

def mask_lz9_given(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ9: Дано - центр свободен, соседи свободны или NC."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    if not rc_is_free(s_ctrl): return False
    return _is_free_or_nc(step, prev, "prev") and _is_free_or_nc(step, next, "next")

def mask_lz9_ctrl_occ_adj_free(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ9: Центр занят, соседи все еще свободны или NC."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    if not rc_is_occupied(s_ctrl): return False
    return _is_free_or_nc(step, prev, "prev") and _is_free_or_nc(step, next, "next")

def mask_lz9_ctrl_free_adj_occ(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ9: Центр свободен, но кто-то из соседей (не NC) занялся."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    if not rc_is_free(s_ctrl): return False
    any_adj_occ = _is_occ_and_not_nc(step, prev, "prev") or _is_occ_and_not_nc(step, next, "next")
    return any_adj_occ

def mask_lz9_both_occ(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ9: Открытие - центр занят И кто-то из соседей (не NC) занят."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    if not rc_is_occupied(s_ctrl): return False
    any_adj_occ = _is_occ_and_not_nc(step, prev, "prev") or _is_occ_and_not_nc(step, next, "next")
    return any_adj_occ

def get_mask_by_id(mask_id: int) -> callable:
    """Получение маски по числовому ID."""
    mask_map = {
        0b000: mask_000,
        0b010: mask_010,
        0b101: mask_101,
        0b111: mask_111,
        0b100: mask_100,
        0b110: mask_110,
        0b001: mask_001,
        0b011: mask_011,
        100: mask_100_or_000,
        101: mask_001_or_000,
        200: mask_x0x,
        201: mask_x0x_occ,
        202: mask_00x,
        203: mask_00x_occ,
        204: mask_x00,
        205: mask_x00_occ,
        208: mask_110_or_111,
        209: mask_011_or_111,
        210: mask_01x_or_x10,
        500: mask_0_not_locked,
        501: mask_1_not_locked,
        505: mask_ls5_prev_locked_p0,
        506: mask_ls5_next_locked_p0,
        507: mask_ls5_both_locked_p1,
        512: mask_lz12_prev_nc_p0,
        513: mask_lz12_prev_nc_p1,
        514: mask_lz12_next_nc_p0,
        515: mask_lz12_next_nc_p1,
        900: mask_lz9_given,
        901: mask_lz9_ctrl_occ_adj_free,
        902: mask_lz9_ctrl_free_adj_occ,
        903: mask_lz9_both_occ,
        600: mask_ctrl_free,
        601: mask_ctrl_occupied,
        1100: mask_000, # LZ11 DANO
        1101: mask_010, # LZ11 KOGDA
        1300: mask_000, # LZ13 Phase 01
        1301: mask_000, # LZ13 Phase 02
        1302: mask_010, # LZ13 KOGDA
    }
    return mask_map.get(mask_id, mask_000)


def mask_to_string(mask_id: int) -> str:
    """Человекочитаемое представление маски."""
    names = {
        0b000: "000",
        0b010: "010",
        0b101: "101",
        0b111: "111",
        0b100: "100",
        0b110: "110",
        0b001: "001",
        0b011: "011",
        100: "100|000",
        101: "001|000",
        200: "X0X",
        201: "X0X_OCC",
        202: "00X",
        203: "00X_OCC",
        204: "X00",
        205: "X00_OCC",
        208: "110|111",
        209: "011|111",
        210: "01x|x10",
        500: "FREE_!LOCKED",
        501: "OCC_!LOCKED",
        505: "LS5_PREV_LOCKED",
        506: "LS5_NEXT_LOCKED",
        507: "LS5_BOTH_LOCKED",
        512: "LZ12_PREV_NC_P0",
        513: "LZ12_PREV_NC_P1",
        514: "LZ12_NEXT_NC_P0",
        515: "LZ12_NEXT_NC_P1",
        900: "LZ9_GIVEN",
        901: "LZ9_CTRL_OCC_WAIT_ADJ",
        902: "LZ9_ADJ_OCC_WAIT_CTRL",
        903: "LZ9_BOTH_OCC",
        600: "v6:ctrl_free",
        601: "v6:ctrl_occupied",
        1100: "LZ11_DANO",
        1101: "LZ11_KOGDA",
        1300: "LZ13_P01",
        1301: "LZ13_P02",
        1302: "LZ13_KOGDA",
    }
    return names.get(mask_id, f"UNKNOWN({mask_id})")
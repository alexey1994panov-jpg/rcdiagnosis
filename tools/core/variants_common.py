from typing import Any, Optional, Sequence
from core.uni_states import rc_is_free, rc_is_occupied, rc_is_locked, signal_is_closed, shunting_signal_is_closed, signal_is_open, shunting_signal_is_open
from station.station_config import NODES


# ============================================================================
#   (    )
# ============================================================================

def mask_000(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-0-0:    .
     :   = None,    ""
    (       ctrl   )
    """
    if not ctrl:
        return False
    
    s_prev = step.rc_states.get(prev, 0) if prev else 0
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0) if next else 0
    
    # None   (0),    ctrl 
    prev_ok = rc_is_free(s_prev) if prev else True
    next_ok = rc_is_free(s_next) if next else True
    
    return prev_ok and rc_is_free(s_ctrl) and next_ok


def mask_010(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-1-0:  ,  .
     : None = "" (  =  )
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
    1-0-1:  ,  .
      :  prev  next = None  False
    """
    if not ctrl or prev is None or next is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    
    return rc_is_occupied(s_prev) and rc_is_free(s_ctrl) and rc_is_occupied(s_next)


def mask_111(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    1-1-1:    .
      :  prev  next = None  False
    """
    if not ctrl or prev is None or next is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    
    return rc_is_occupied(s_prev) and rc_is_occupied(s_ctrl) and rc_is_occupied(s_next)


# ============================================================================
#   v2 (    )
# ============================================================================

def mask_100(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    1-0-0: Prev , ctrl  next .
     prev:  prev = None  False
    """
    if not ctrl or prev is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0) if next else 0
    
    return rc_is_occupied(s_prev) and rc_is_free(s_ctrl) and rc_is_free(s_next)


def mask_110(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    1-1-0: Prev  ctrl , next .
     prev:  prev = None  False
    """
    if not ctrl or prev is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0) if next else 0
    
    return rc_is_occupied(s_prev) and rc_is_occupied(s_ctrl) and rc_is_free(s_next)


def mask_100_or_000(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """1-0-0  0-0-0:       ."""
    return mask_100(step, prev, ctrl, next) or mask_000(step, prev, ctrl, next)


def mask_001(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-0-1: Next , prev  ctrl .
     next:  next = None  False
    """
    if not ctrl or next is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0) if prev else 0
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    
    return rc_is_free(s_prev) and rc_is_free(s_ctrl) and rc_is_occupied(s_next)


def mask_011(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-1-1: Ctrl  next , prev .
     next:  next = None  False
    """
    if not ctrl or next is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0) if prev else 0
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    
    return rc_is_free(s_prev) and rc_is_occupied(s_ctrl) and rc_is_occupied(s_next)


def mask_001_or_000(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """0-0-1  0-0-0:   ."""
    return mask_001(step, prev, ctrl, next) or mask_000(step, prev, ctrl, next)


# ============================================================================
#   v7 (    )
# ============================================================================

def mask_x0x(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    X-0-X:  ,    ( ).
     v7 no_adjacent:     (prev=None  next=None)
    """
    if not ctrl:
        return False
    if prev is not None or next is not None:
        return False
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_free(s_ctrl)


def mask_x1x(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """X-1-X: no_adjacent, контролируемая занята."""
    if not ctrl:
        return False
    if prev is not None or next is not None:
        return False
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_occupied(s_ctrl)


def mask_00x(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-0-X: prev  ctrl , next   (.. None).
     v7 no_prev:   (prev=None),   (next!=None)
    """
    if not ctrl:
        return False
    
    # no_prev branch must have no previous adjacent RC in effective topology
    if prev is not None:
        return False
    
    s_ctrl = step.rc_states.get(ctrl, 0)
    
    # next     
    if next is None:
        return False
    s_next = step.rc_states.get(next, 0)
    next_ok = rc_is_free(s_next)
    
    return rc_is_free(s_ctrl) and next_ok


def mask_01x(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """0-1-X: no_prev, next свободна, контролируемая занята."""
    if not ctrl or next is None:
        return False
    
    # no_prev branch must have no previous adjacent RC in effective topology
    if prev is not None:
        return False
    
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    next_ok = rc_is_free(s_next)  # next   !
    
    return rc_is_occupied(s_ctrl) and next_ok


def mask_x00(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    X-0-0: ctrl  next , prev  .
     v7 no_next:   (prev!=None),   (next=None)
    """
    if not ctrl:
        return False
    
    # prev     
    if prev is None:
        return False
    s_prev = step.rc_states.get(prev, 0)
    prev_ok = rc_is_free(s_prev)
    
    s_ctrl = step.rc_states.get(ctrl, 0)

    # no_next branch must have no next adjacent RC in effective topology
    if next is not None:
        return False
    
    return prev_ok and rc_is_free(s_ctrl)


def mask_x10(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """X-1-0: no_next, prev свободна, контролируемая занята."""
    if not ctrl or prev is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0)
    prev_ok = rc_is_free(s_prev)  # prev   !
    
    s_ctrl = step.rc_states.get(ctrl, 0)
    
    # no_next branch must have no next adjacent RC in effective topology
    if next is not None:
        return False

    return prev_ok and rc_is_occupied(s_ctrl)


# Backward-compatible aliases for old v7 names
mask_x0x_occ = mask_x1x
mask_00x_occ = mask_01x
mask_x00_occ = mask_x10


# ============================================================================
#   v8 ( )
# ============================================================================

def mask_110_or_111(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    1-1-0  1-1-1: prev  ctrl , next .
     prev:  prev = None  False
    """
    if not ctrl or prev is None:
        return False
    
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    
    return rc_is_occupied(s_prev) and rc_is_occupied(s_ctrl)


def mask_011_or_111(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    0-1-1  1-1-1: ctrl  next , prev .
     next:  next = None  False
    """
    if not ctrl or next is None:
        return False
    
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    
    return rc_is_occupied(s_ctrl) and rc_is_occupied(s_next)


def mask_01X_or_X10(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """
    01X | X10: контролируемая занята, хотя бы одна смежная свободна.
    Для отсутствующей смежной (None) условие свободы считается истинным.
    """
    if not ctrl:
        return False
    
    s_prev = step.rc_states.get(prev, 0) if prev else 0
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0) if next else 0
    
    curr_occ = rc_is_occupied(s_ctrl)
    prev_free = rc_is_free(s_prev) if prev else True  # None = 
    next_free = rc_is_free(s_next) if next else True  # None = 
    
    return curr_occ and (prev_free or next_free)


# Backward-compatible alias (old non-canonical name)
mask_01x_or_x10 = mask_01X_or_X10

# ============================================================================
#   v5 ( ,   )
# ============================================================================

def mask_0_not_locked(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """ :  ,    can_lock=True."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    
    #  :    
    if not (rc_is_free(s_ctrl) and not rc_is_locked(s_ctrl)):
        return False
    
    #  can_lock  rc_capabilities
    caps = getattr(step, 'rc_capabilities', {})
    ctrl_caps = caps.get(ctrl, {})
    return ctrl_caps.get('can_lock', False)


def mask_1_not_locked(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """ :  ,    can_lock=True."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    
    #  :    
    if not (rc_is_occupied(s_ctrl) and not rc_is_locked(s_ctrl)):
        return False
    
    #  can_lock  rc_capabilities
    caps = getattr(step, 'rc_capabilities', {})
    ctrl_caps = caps.get(ctrl, {})
    return ctrl_caps.get('can_lock', False)

def mask_ctrl_free(step, prev, ctrl, next) -> bool:
    """
     v6  0:   .
    ctrl -  ID  (),     step.rc_states
    """
    if not ctrl:
        return False
    #    (0=, 1=,  ..)
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_free(s_ctrl)


def mask_ctrl_occupied(step, prev, ctrl, next) -> bool:
    """
     v6  1:   .
    """
    if not ctrl:
        return False
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_occupied(s_ctrl)


# ============================================================================
#   LS5 (   )
# ============================================================================

def mask_rc_1l_0l_0l(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LS5 Branch Prev Phase 0: Prev(Occ+Lock), Ctrl(Free+Lock)"""
    if not ctrl or prev is None:
        return False
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_occupied(s_prev) and rc_is_locked(s_prev) and \
           rc_is_free(s_ctrl) and rc_is_locked(s_ctrl)


def mask_rc_0l_0l_1l(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LS5 Branch Next Phase 0: Next(Occ+Lock), Ctrl(Free+Lock)"""
    if not ctrl or next is None:
        return False
    s_next = step.rc_states.get(next, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_occupied(s_next) and rc_is_locked(s_next) and \
           rc_is_free(s_ctrl) and rc_is_locked(s_ctrl)


def mask_rc_1l_0l_1l(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LS5 Phase 1: Both(Occ+Lock), Ctrl(Free+Lock)"""
    if not ctrl or prev is None or next is None:
        return False
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    return rc_is_occupied(s_prev) and rc_is_locked(s_prev) and \
           rc_is_occupied(s_next) and rc_is_locked(s_next) and \
           rc_is_free(s_ctrl) and rc_is_locked(s_ctrl)

# Backward-compatible LS5 aliases
mask_ls5_prev_locked_p0 = mask_rc_1l_0l_0l
mask_ls5_next_locked_p0 = mask_rc_0l_0l_1l
mask_ls5_both_locked_p1 = mask_rc_1l_0l_1l


# ============================================================================
#   LZ12 (  NC)
# ============================================================================

def mask_rc_n_1_0l(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ12 Prev-NC P0/KOGDA: prev=NC, ctrl=occ+locked, next=free+locked."""
    if not step.modes.get("prev_nc", False) or not next:
        return False
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    return (
        rc_is_occupied(s_ctrl) and rc_is_locked(s_ctrl) and
        rc_is_free(s_next) and rc_is_locked(s_next)
    )

def mask_rc_n_1_1l(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ12 Prev-NC P1: prev=NC, ctrl=occ+locked, next=occ+locked."""
    if not step.modes.get("prev_nc", False) or not next:
        return False
    s_ctrl = step.rc_states.get(ctrl, 0)
    s_next = step.rc_states.get(next, 0)
    return (
        rc_is_occupied(s_ctrl) and rc_is_locked(s_ctrl) and
        rc_is_occupied(s_next) and rc_is_locked(s_next)
    )

def mask_rc_l0_1_n(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ12 Next-NC P0/KOGDA: next=NC, ctrl=occ+locked, prev=free+locked."""
    if not step.modes.get("next_nc", False) or not prev:
        return False
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    return (
        rc_is_occupied(s_ctrl) and rc_is_locked(s_ctrl) and
        rc_is_free(s_prev) and rc_is_locked(s_prev)
    )

def mask_rc_l1_1_n(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ12 Next-NC P1: next=NC, ctrl=occ+locked, prev=occ+locked."""
    if not step.modes.get("next_nc", False) or not prev:
        return False
    s_prev = step.rc_states.get(prev, 0)
    s_ctrl = step.rc_states.get(ctrl, 0)
    return (
        rc_is_occupied(s_ctrl) and rc_is_locked(s_ctrl) and
        rc_is_occupied(s_prev) and rc_is_locked(s_prev)
    )

# Backward-compatible LZ12 aliases
mask_lz12_prev_nc_p0 = mask_rc_n_1_0l
mask_lz12_prev_nc_p1 = mask_rc_n_1_1l
mask_lz12_next_nc_p0 = mask_rc_l0_1_n
mask_lz12_next_nc_p1 = mask_rc_l1_1_n

# ============================================================================
#   LZ9 ( )
# ============================================================================

def _is_free_or_nc(step: Any, rc_id: Optional[str], side: str) -> bool:
    """:       NC ()."""
    if not rc_id or step.modes.get(f"{side}_nc", False):
        return True
    return rc_is_free(step.rc_states.get(rc_id, 0))

def _is_occ_and_not_nc(step: Any, rc_id: Optional[str], side: str) -> bool:
    """:   (   ,  NC)."""
    if not rc_id or step.modes.get(f"{side}_nc", False):
        return False
    return rc_is_occupied(step.rc_states.get(rc_id, 0))

def _is_locked(step: Any, rc_id: Optional[str]) -> bool:
    """:   (=1)."""
    if not rc_id:
        return False
    return rc_is_locked(step.rc_states.get(rc_id, 0))

def _is_signal_closed(
    step: Any,
    sig_id: Optional[str],
    mode_key: Optional[str] = None,
    fallback_mode_keys: Optional[Sequence[str]] = None,
) -> bool:
    """:  ."""
    resolved_sig = _resolve_runtime_signal_id(
        step=step,
        sig_id=sig_id,
        mode_key=mode_key,
        fallback_mode_keys=fallback_mode_keys,
    )
    if not resolved_sig:
        return False
    st = step.signal_states.get(resolved_sig, 0)
    
    node = NODES.get(resolved_sig)
    if node:
        t = node.get("type")
        if t == 3: # Shunting
            return shunting_signal_is_closed(st)
        if t == 4: # Train
            return signal_is_closed(st)
            
    # Fallback for unknown type: treat as train signal (strict red=15 only).
    return signal_is_closed(st)

def _is_signal_open(
    step: Any,
    sig_id: Optional[str],
    mode_key: Optional[str] = None,
    fallback_mode_keys: Optional[Sequence[str]] = None,
) -> bool:
    """:  ."""
    resolved_sig = _resolve_runtime_signal_id(
        step=step,
        sig_id=sig_id,
        mode_key=mode_key,
        fallback_mode_keys=fallback_mode_keys,
    )
    if not resolved_sig:
        return False
    st = step.signal_states.get(resolved_sig, 0)
    
    node = NODES.get(resolved_sig)
    if node:
        t = node.get("type")
        if t == 3: # Shunting
            return shunting_signal_is_open(st)
        if t == 4: # Train
            return signal_is_open(st)
            
    # Fallback: check both if type unknown
    return signal_is_open(st) or shunting_signal_is_open(st)



def _resolve_runtime_signal_id(
    step: Any,
    sig_id: Optional[str],
    mode_key: Optional[str] = None,
    fallback_mode_keys: Optional[Sequence[str]] = None,
) -> Optional[str]:
    """Resolve signal id with priority: explicit id -> mode key -> fallback mode keys."""
    if sig_id:
        return sig_id
    modes = getattr(step, "modes", {}) or {}
    if mode_key:
        dyn = modes.get(mode_key)
        if dyn:
            return str(dyn)
    if fallback_mode_keys:
        for key in fallback_mode_keys:
            dyn = modes.get(key)
            if dyn:
                return str(dyn)
    return None
# ============================================================================
#   LZ10 (,   )
# ============================================================================

def make_mask_rc_0_1_0_sig_1(
    sig_id: Optional[str],
    mode_key: Optional[str] = None,
    fallback_mode_keys: Optional[Sequence[str]] = None,
):
    """RC_0_1_0 + SIG_1."""
    def mask_rc_0_1_0_sig_1(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
        if not prev or not next:
            return False
        s_prev = step.rc_states.get(prev, 0)
        s_ctrl = step.rc_states.get(ctrl, 0)
        s_next = step.rc_states.get(next, 0)
        return rc_is_free(s_prev) and rc_is_occupied(s_ctrl) and rc_is_free(s_next) and _is_signal_open(
            step, sig_id, mode_key=mode_key, fallback_mode_keys=fallback_mode_keys
        )
    return mask_rc_0_1_0_sig_1


def make_mask_rc_0_1_1_sig_1(
    sig_id: Optional[str],
    direction: str,
    mode_key: Optional[str] = None,
    fallback_mode_keys: Optional[Sequence[str]] = None,
):
    """RC_(011|110) + SIG_1 (depends on direction)."""
    def mask_rc_0_1_1_sig_1(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
        if not prev or not next:
            return False
        s_prev = step.rc_states.get(prev, 0)
        s_ctrl = step.rc_states.get(ctrl, 0)
        s_next = step.rc_states.get(next, 0)
        if direction == "to_next":
            state_ok = rc_is_free(s_prev) and rc_is_occupied(s_ctrl) and rc_is_occupied(s_next)
        else:
            state_ok = rc_is_occupied(s_prev) and rc_is_occupied(s_ctrl) and rc_is_free(s_next)
        return state_ok and _is_signal_open(
            step, sig_id, mode_key=mode_key, fallback_mode_keys=fallback_mode_keys
        )
    return mask_rc_0_1_1_sig_1


def make_mask_rc_0_1_1_sig_0(
    sig_id: Optional[str],
    direction: str,
    mode_key: Optional[str] = None,
    fallback_mode_keys: Optional[Sequence[str]] = None,
):
    """RC_(011|110) + SIG_0 (depends on direction)."""
    def mask_rc_0_1_1_sig_0(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
        if not prev or not next:
            return False
        s_prev = step.rc_states.get(prev, 0)
        s_ctrl = step.rc_states.get(ctrl, 0)
        s_next = step.rc_states.get(next, 0)
        if direction == "to_next":
            state_ok = rc_is_free(s_prev) and rc_is_occupied(s_ctrl) and rc_is_occupied(s_next)
        else:
            state_ok = rc_is_occupied(s_prev) and rc_is_occupied(s_ctrl) and rc_is_free(s_next)
        return state_ok and _is_signal_closed(
            step, sig_id, mode_key=mode_key, fallback_mode_keys=fallback_mode_keys
        )
    return mask_rc_0_1_1_sig_0


def make_mask_rc_0_1_0_sig_0(
    sig_id: Optional[str],
    mode_key: Optional[str] = None,
    fallback_mode_keys: Optional[Sequence[str]] = None,
):
    """RC_0_1_0 + SIG_0."""
    def mask_rc_0_1_0_sig_0(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
        if not prev or not next:
            return False
        s_prev = step.rc_states.get(prev, 0)
        s_ctrl = step.rc_states.get(ctrl, 0)
        s_next = step.rc_states.get(next, 0)
        return rc_is_free(s_prev) and rc_is_occupied(s_ctrl) and rc_is_free(s_next) and _is_signal_closed(
            step, sig_id, mode_key=mode_key, fallback_mode_keys=fallback_mode_keys
        )
    return mask_rc_0_1_0_sig_0


# ============================================================================
# CANONICAL MASK NAMES (variant-agnostic aliases)
# ============================================================================
mask_rc_0_0_0 = mask_000
mask_rc_0_1_0 = mask_010
mask_rc_1_0_1 = mask_101
mask_rc_1_1_1 = mask_111
mask_rc_1_0_0 = mask_100
mask_rc_1_1_0 = mask_110
mask_rc_0_0_1 = mask_001
mask_rc_0_1_1 = mask_011

mask_rc_x_0_x = mask_x0x
mask_rc_x_1_x = mask_x1x
mask_rc_0_0_x = mask_00x
mask_rc_0_1_x = mask_01x
mask_rc_x_0_0 = mask_x00
mask_rc_x_1_0 = mask_x10

mask_rc_0 = mask_ctrl_free
mask_rc_1 = mask_ctrl_occupied

mask_rc_0nl = mask_0_not_locked
mask_rc_1nl = mask_1_not_locked

# Canonical signal-dependent aliases (parameterized/variant-local logic)
mask_sig_0_rc_0_sig_0 = mask_000
mask_sig_0_rc_1_sig_0 = mask_010
mask_rc_0l_0_x_sig_0 = mask_000
mask_rc_1l_0_x_sig_0 = mask_000
mask_rc_1l_1_x_sig_0 = mask_010
mask_rc_0_1_0_sig_1 = mask_000
mask_rc_0_1_1_sig_1 = mask_000
mask_rc_0_1_1_sig_0 = mask_000
mask_rc_0_1_0_sig_0 = mask_010


# Backward-compatible aliases for previous make_mask names
make_mask_lz10_p01_sig_open = make_mask_rc_0_1_0_sig_1
make_mask_lz10_p02_sig_open = make_mask_rc_0_1_1_sig_1
make_mask_lz10_p03_sig_closed = make_mask_rc_0_1_1_sig_0
make_mask_lz10_kogda_sig_closed = make_mask_rc_0_1_0_sig_0

def mask_rc_0_0l_0(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ9:  -  ,    NC."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    if not rc_is_free(s_ctrl): return False
    return _is_free_or_nc(step, prev, "prev") and _is_free_or_nc(step, next, "next")

def mask_rc_ctrl_1_adj_free_or_nc(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ9:  ,      NC."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    if not rc_is_occupied(s_ctrl): return False
    return _is_free_or_nc(step, prev, "prev") and _is_free_or_nc(step, next, "next")

def mask_rc_ctrl_0_adj_occ(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ9:  ,  -   ( NC) ."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    if not rc_is_free(s_ctrl): return False
    any_adj_occ = _is_occ_and_not_nc(step, prev, "prev") or _is_occ_and_not_nc(step, next, "next")
    return any_adj_occ

def mask_rc_ctrl_1_adj_occ(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ9:  -    -   ( NC) ."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    if not rc_is_occupied(s_ctrl): return False
    any_adj_occ = _is_occ_and_not_nc(step, prev, "prev") or _is_occ_and_not_nc(step, next, "next")
    return any_adj_occ

def mask_rc_ctrl_1_prev_occ(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ9:      prev (prev  NC)."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    if not rc_is_occupied(s_ctrl):
        return False
    return _is_occ_and_not_nc(step, prev, "prev")

def mask_rc_ctrl_1_next_occ(step: Any, prev: Optional[str], ctrl: str, next: Optional[str]) -> bool:
    """LZ9:      next (next  NC)."""
    s_ctrl = step.rc_states.get(ctrl, 0)
    if not rc_is_occupied(s_ctrl):
        return False
    return _is_occ_and_not_nc(step, next, "next")

# Backward-compatible LZ9 aliases
mask_lz9_given = mask_rc_0_0l_0
mask_lz9_ctrl_occ_adj_free = mask_rc_ctrl_1_adj_free_or_nc
mask_lz9_ctrl_free_adj_occ = mask_rc_ctrl_0_adj_occ
mask_lz9_both_occ = mask_rc_ctrl_1_adj_occ
mask_lz9_ctrl_occ_prev_occ = mask_rc_ctrl_1_prev_occ
mask_lz9_ctrl_occ_next_occ = mask_rc_ctrl_1_next_occ

def get_mask_by_id(mask_id: int) -> callable:
    """Return mask function by canonical numeric ID."""
    mask_map = {
        # Simple RC masks (1..)
        1: mask_rc_0_0_0,
        2: mask_rc_0_1_0,
        3: mask_rc_1_0_1,
        4: mask_rc_1_1_1,
        5: mask_rc_1_0_0,
        6: mask_rc_1_1_0,
        7: mask_rc_0_0_1,
        8: mask_rc_0_1_1,

        # X-masks
        9: mask_rc_x_0_x,
        10: mask_rc_x_1_x,
        11: mask_rc_0_0_x,
        12: mask_rc_0_1_x,
        13: mask_rc_x_0_0,
        14: mask_rc_x_1_0,

        # Ctrl-only
        15: mask_rc_0,
        16: mask_rc_1,

        # Lock-related
        17: mask_rc_0nl,
        18: mask_rc_1nl,
        19: mask_rc_1l_0l_0l,
        20: mask_rc_0l_0l_1l,
        21: mask_rc_1l_0l_1l,

        # NC-related
        22: mask_rc_n_1_0l,
        23: mask_rc_n_1_1l,
        24: mask_rc_l0_1_n,
        25: mask_rc_l1_1_n,

        # Timing-event support
        32: mask_rc_0_0l_0,
        33: mask_rc_ctrl_1_adj_free_or_nc,
        34: mask_rc_ctrl_0_adj_occ,
        35: mask_rc_ctrl_1_adj_occ,
        36: mask_rc_ctrl_1_prev_occ,
        37: mask_rc_ctrl_1_next_occ,

        # Signal-dependent IDs (factory-parameterized logic)
        38: mask_sig_0_rc_0_sig_0,
        39: mask_sig_0_rc_1_sig_0,
        40: mask_rc_0l_0_x_sig_0,
        41: mask_rc_1l_0_x_sig_0,
        42: mask_rc_1l_1_x_sig_0,
        43: mask_rc_0_1_0_sig_1,
        44: mask_rc_0_1_1_sig_1,
        45: mask_rc_0_1_1_sig_0,
        46: mask_rc_0_1_0_sig_0,

        # Composite masks (100+)
        100: mask_100_or_000,
        101: mask_001_or_000,
        102: mask_110_or_111,
        103: mask_011_or_111,
        104: mask_01X_or_X10,

        # Compatibility alias
        106: mask_001_or_000,
    }
    return mask_map.get(mask_id, mask_000)


def mask_to_string(mask_id: int) -> str:
    """Return canonical, variant-agnostic mask name by ID."""
    names = {
        1: "RC_0_0_0",
        2: "RC_0_1_0",
        3: "RC_1_0_1",
        4: "RC_1_1_1",
        5: "RC_1_0_0",
        6: "RC_1_1_0",
        7: "RC_0_0_1",
        8: "RC_0_1_1",

        9: "RC_X_0_X",
        10: "RC_X_1_X",
        11: "RC_0_0_X",
        12: "RC_0_1_X",
        13: "RC_X_0_0",
        14: "RC_X_1_0",

        15: "RC_0",
        16: "RC_1",

        17: "RC_0NL",
        18: "RC_1NL",
        19: "RC_1L_0L_0L",
        20: "RC_0L_0L_1L",
        21: "RC_1L_0L_1L",

        22: "RC_N_1_0L",
        23: "RC_N_1_1L",
        24: "RC_L0_1_N",
        25: "RC_L1_1_N",

        32: "RC_0_0L_0",
        33: "RC_CTRL_1__ADJ_FREE_OR_NC",
        34: "RC_CTRL_0__ADJ_OCC",
        35: "RC_CTRL_1__ADJ_OCC",
        36: "RC_CTRL_1__PREV_OCC",
        37: "RC_CTRL_1__NEXT_OCC",

        38: "SIG_0_RC_0_SIG_0",
        39: "SIG_0_RC_1_SIG_0",
        40: "RC_0L_0_X_SIG_0",
        41: "RC_1L_0_X_SIG_0",
        42: "RC_1L_1_X_SIG_0",
        43: "RC_0_1_0_SIG_1",
        44: "RC_0_1_1_SIG_1",
        45: "RC_0_1_1_SIG_0",
        46: "RC_0_1_0_SIG_0",

        100: "RC_1_0_0_OR_0_0_0",
        101: "RC_0_0_1_OR_0_0_0",
        102: "RC_1_1_0_OR_1_1_1",
        103: "RC_0_1_1_OR_1_1_1",
        104: "RC_0_1_X_OR_X_1_0",
        106: "RC_0_0_1_OR_0_0_0",
    }
    return names.get(mask_id, f"UNKNOWN({mask_id})")




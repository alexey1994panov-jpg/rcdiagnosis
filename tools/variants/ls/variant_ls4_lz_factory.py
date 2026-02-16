# -*- coding: utf-8 -*-
from typing import Any, Optional, Tuple

from core.uni_states import rc_is_occupied
from core.variants_common import mask_101, mask_111

MASK_RC_111 = 4
MASK_RC_101 = 3


class LS4WindowDetector:
    """
    LS4 with explicit phase-2 window:
    1) 111 for ts01_ls4
    2) 101 for [tlz01_ls4 .. tlz02_ls4]
    3) 111 for ts02_ls4 -> open
    Close: ctrl occupied for tkon_ls4
    """

    def __init__(
        self,
        prev_rc_name: str,
        ctrl_rc_name: str,
        next_rc_name: str,
        ts01_ls4: float,
        tlz01_ls4: float,
        tlz02_ls4: float,
        ts02_ls4: float,
        tkon_ls4: float,
    ) -> None:
        self.prev_rc_name = prev_rc_name
        self.ctrl_rc_name = ctrl_rc_name
        self.next_rc_name = next_rc_name

        self.ts01 = float(ts01_ls4)
        self.tlz01 = float(tlz01_ls4)
        self.tlz02 = float(tlz02_ls4)
        self.ts02 = float(ts02_ls4)
        self.tkon = float(tkon_ls4)

        self.phase_id = 0
        self.timer = 0.0
        self.completion_timer = 0.0
        self.active = False
        self.last_open_offset: Optional[float] = None
        self.last_close_offset: Optional[float] = None

    def reset(self) -> None:
        self.phase_id = 0
        self.timer = 0.0
        self.completion_timer = 0.0
        self.active = False
        self.last_open_offset = None
        self.last_close_offset = None

    def get_current_mask_id(self) -> Optional[int]:
        if self.active:
            return MASK_RC_111
        if self.phase_id == 0:
            return MASK_RC_111
        if self.phase_id == 1:
            return MASK_RC_101
        if self.phase_id == 2:
            return MASK_RC_111
        return None

    def _neighbors(self, step: Any) -> Tuple[Optional[str], str, Optional[str]]:
        prev = getattr(step, "effective_prev_rc", None)
        if prev is None and not hasattr(step, "effective_prev_rc"):
            prev = self.prev_rc_name
        nxt = getattr(step, "effective_next_rc", None)
        if nxt is None and not hasattr(step, "effective_next_rc"):
            nxt = self.next_rc_name
        return prev, self.ctrl_rc_name, nxt

    def _neighbors_ok(self, step: Any) -> bool:
        modes = getattr(step, "modes", {}) or {}
        return bool(modes.get("prev_control_ok", True)) and bool(modes.get("next_control_ok", True))

    def _mask_111(self, step: Any) -> bool:
        if not self._neighbors_ok(step):
            return False
        prev, ctrl, nxt = self._neighbors(step)
        return mask_111(step, prev, ctrl, nxt)

    def _mask_101(self, step: Any) -> bool:
        if not self._neighbors_ok(step):
            return False
        prev, ctrl, nxt = self._neighbors(step)
        return mask_101(step, prev, ctrl, nxt)

    def _ctrl_occupied(self, step: Any) -> bool:
        return rc_is_occupied(int(step.rc_states.get(self.ctrl_rc_name, 0)))

    def _reset_formation(self) -> None:
        self.phase_id = 0
        self.timer = 0.0

    def _update_completion(self, step: Any, dt: float) -> bool:
        if self._ctrl_occupied(step):
            prev = self.completion_timer
            self.completion_timer += dt
            if self.completion_timer >= self.tkon:
                self.last_close_offset = max(0.0, min(float(dt), self.tkon - prev))
                self.reset()
                return True
        else:
            self.completion_timer = 0.0
        return False

    def _bootstrap_completion_on_open(self, step: Any, dt: float) -> bool:
        """
        Count the whole opening interval toward completion when ctrl is occupied.
        This matches table semantics where open row contributes to tkon.
        """
        if not self._ctrl_occupied(step):
            self.completion_timer = 0.0
            return False
        prev = self.completion_timer
        self.completion_timer += float(dt)
        if self.completion_timer >= self.tkon:
            self.last_close_offset = max(0.0, min(float(dt), self.tkon - prev))
            self.reset()
            return True
        return False

    def update(self, step: Any, dt: float) -> Tuple[bool, bool]:
        self.last_open_offset = None
        self.last_close_offset = None

        if self.active:
            return False, self._update_completion(step, dt)

        # Phase 0: accumulate 111 for >= ts01, then wait for 101 transition
        if self.phase_id == 0:
            if self._mask_111(step):
                self.timer += dt
                return False, False
            if self._mask_101(step) and self.timer >= self.ts01:
                # Start phase 1 on first 101 interval after enough 111 time.
                self.phase_id = 1
                self.timer = dt
                if self.timer > self.tlz02:
                    self._reset_formation()
                return False, False
            self._reset_formation()
            return False, False

        # Phase 1: 101 for [tlz01..tlz02], then next 111 starts phase 2
        if self.phase_id == 1:
            if self._mask_101(step):
                self.timer += dt
                if self.timer > self.tlz02:
                    self._reset_formation()
                return False, False
            if self._mask_111(step) and (self.tlz01 <= self.timer <= self.tlz02):
                self.phase_id = 2
                self.timer = dt
                if self.timer < self.ts02:
                    return False, False
                self.active = True
                self.last_open_offset = max(0.0, min(float(dt), self.ts02))
                self.completion_timer = 0.0
                self.phase_id = 2
                self.timer = 0.0
                if self._bootstrap_completion_on_open(step, dt):
                    return True, True
                return True, False
            self._reset_formation()
            return False, False

        # Phase 2: 111 for ts02 -> open
        if self.phase_id == 2:
            if not self._mask_111(step):
                self._reset_formation()
                return False, False
            prev = self.timer
            self.timer += dt
            if self.timer < self.ts02:
                return False, False
            self.active = True
            self.last_open_offset = max(0.0, min(float(dt), self.ts02 - prev))
            self.completion_timer = 0.0
            self.phase_id = 2
            self.timer = 0.0
            if self._bootstrap_completion_on_open(step, dt):
                return True, True
            return True, False

        return False, False


def make_ls4_detector(
    prev_rc_name: str,
    ctrl_rc_name: str,
    next_rc_name: str,
    ts01_ls4: float,
    tlz01_ls4: float,
    tlz02_ls4: float,
    ts02_ls4: Optional[float],
    tkon_ls4: float,
) -> LS4WindowDetector:
    phase3_duration = float(ts02_ls4 if ts02_ls4 is not None else tlz02_ls4)
    return LS4WindowDetector(
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
        ts01_ls4=float(ts01_ls4),
        tlz01_ls4=float(tlz01_ls4),
        tlz02_ls4=float(tlz02_ls4),
        ts02_ls4=phase3_duration,
        tkon_ls4=float(tkon_ls4),
    )

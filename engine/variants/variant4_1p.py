from typing import Any, Tuple

from ..station_visochino_1p import (
    rc_is_free,
    rc_is_occupied,
    signal_is_closed,
    shunting_signal_is_closed,
)


class Variant4Detector:
    """
    ЛЗ v4: ложная занятость на контролируемой РЦ при закрытом входном/выходном
    светофоре и отсутствии контроля одной из смежных РЦ.

    prev/curr/next для варианта считаются на уровне станции и кладутся в modes:
      <ctrl_rc>_prev_state, <ctrl_rc>_next_state, <ctrl_rc>_prev_nc, <ctrl_rc>_next_nc.
    """

    def __init__(
        self,
        prev_rc_id: str,   # оставляем для совместимости, фактически не используется в смежности
        ctrl_rc_id: str,
        next_rc_id: str,
        t_s0401: float,
        t_lz04: float,
        t_kon: float,
        *,
        signal_prev_to_ctrl_id: str,
        signal_ctrl_to_next_id: str,
        ctrl_to_next_is_shunting: bool = True,
    ) -> None:
        self.prev_rc_id = prev_rc_id
        self.ctrl_rc_id = ctrl_rc_id
        self.next_rc_id = next_rc_id

        self.T_S0401 = float(t_s0401)
        self.T_LZ04 = float(t_lz04)
        self.T_KON = float(t_kon)

        self.signal_prev_to_ctrl_id = signal_prev_to_ctrl_id
        self.signal_ctrl_to_next_id = signal_ctrl_to_next_id
        self.ctrl_to_next_is_shunting = bool(ctrl_to_next_is_shunting)

        # idle -> p1_4_1 / p1_4_2 -> active
        self.phase: str = "idle"
        self.dur_p1: float = 0.0
        self.dur_lz: float = 0.0
        self.dur_free_after_lz: float = 0.0
        self.active: bool = False

    def reset(self) -> None:
        self.phase = "idle"
        self.dur_p1 = 0.0
        self.dur_lz = 0.0
        self.dur_free_after_lz = 0.0
        self.active = False

    def _states(self, step: Any) -> Tuple[bool, bool, bool, bool, bool, bool]:
        modes = getattr(step, "modes", {}) or {}
        key = self.ctrl_rc_id

        st_curr = step.rc_states.get(self.ctrl_rc_id, 0)
        st_prev = int(modes.get(f"{key}_prev_state", 0))
        st_next = int(modes.get(f"{key}_next_state", 0))

        prev_free = rc_is_free(st_prev)
        prev_occ = rc_is_occupied(st_prev)
        curr_free = rc_is_free(st_curr)
        curr_occ = rc_is_occupied(st_curr)
        next_free = rc_is_free(st_next)
        next_occ = rc_is_occupied(st_next)

        return prev_free, prev_occ, curr_free, curr_occ, next_free, next_occ

    def _nc_flags(self, step: Any) -> Tuple[bool, bool]:
        modes = getattr(step, "modes", {}) or {}
        key = self.ctrl_rc_id
        prev_nc = bool(modes.get(f"{key}_prev_nc", False))
        next_nc = bool(modes.get(f"{key}_next_nc", False))
        return prev_nc, next_nc

    def _signal_states(self, step: Any) -> Tuple[bool, bool]:
        sig_map = getattr(step, "signal_states", {}) or {}
        st_prev_ctrl = sig_map.get(self.signal_prev_to_ctrl_id, 0)
        st_ctrl_next = sig_map.get(self.signal_ctrl_to_next_id, 0)

        sig_prev_ctrl_closed = signal_is_closed(st_prev_ctrl)

        if self.ctrl_to_next_is_shunting:
            sig_ctrl_next_closed = shunting_signal_is_closed(st_ctrl_next)
        else:
            sig_ctrl_next_closed = signal_is_closed(st_ctrl_next)

        return sig_prev_ctrl_closed, sig_ctrl_next_closed

    def update(self, step: Any, dt_interval: float) -> Tuple[bool, bool]:
        if dt_interval <= 0.0:
            dt_interval = 0.0

        opened = False
        closed = False

        (
            prev_free,
            prev_occ,
            curr_free,
            curr_occ,
            next_free,
            next_occ,
        ) = self._states(step)
        prev_nc, next_nc = self._nc_flags(step)
        sig_prev_ctrl_closed, sig_ctrl_next_closed = self._signal_states(step)

        # Завершение, если уже активно
        # если уже активно, только отслеживаем освобождение и T_KON
        if self.active:
            if curr_free:
                self.dur_free_after_lz += dt_interval
                if self.dur_free_after_lz >= self.T_KON:
                    closed = True
                    self.reset()
            elif curr_occ:
                self.dur_free_after_lz = 0.0
            else:
                self.dur_free_after_lz = 0.0
            return opened, closed

        # ДС ещё не активно
        if self.phase == "idle":
            # Универсальная для стрелочных логика:
            #   prev_nc (край), curr свободна, next свободна, "свой" сигнал закрыт.
            # Для 10-12SP "свой" поездной = prev->ctrl (ЧМ1),
            # Для 1-7SP "свой" маневровый = ctrl->next (М1).

            if self.ctrl_rc_id == "10-12SP":
                cond_p1 = prev_nc and curr_free and next_free and sig_prev_ctrl_closed
            elif self.ctrl_rc_id == "1-7SP":
                cond_p1 = prev_nc and curr_free and next_free and sig_ctrl_next_closed
            else:
                # на всякий случай, для других РЦ можно не активироваться
                cond_p1 = False

            if cond_p1:
                self.dur_p1 += dt_interval
                self.dur_lz = 0.0
                if self.dur_p1 >= self.T_S0401:
                    self.phase = "p1"
            else:
                self.dur_p1 = 0.0
                self.dur_lz = 0.0

        elif self.phase == "p1":
            # КОГДА: curr занята, тот же "свой" сигнал закрыт
            if self.ctrl_rc_id == "10-12SP":
                cond_lz = curr_occ and sig_prev_ctrl_closed
            elif self.ctrl_rc_id == "1-7SP":
                cond_lz = curr_occ and sig_ctrl_next_closed
            else:
                cond_lz = False

            if cond_lz:
                self.dur_lz += dt_interval
                if self.dur_lz >= self.T_LZ04:
                    opened = True
                    self.active = True
                    self.dur_free_after_lz = 0.0
            else:
                self.dur_lz = 0.0

        return opened, closed
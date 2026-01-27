from typing import Any

from ..station_visochino_1p import rc_is_free, rc_is_occupied


class Variant8Detector:
    """
    Вариант 8 ЛЗ 1П.

    В8.1 — предыдущая занята (prev-ветка).
    В8.2 — следующая занята (next-ветка).
    В8.3 — «средний» вариант (mid-ветка).

    Завершение ДС: Curr=0 суммарно не менее T_KON (накопление, не подряд).
    Работает только при корректной смежности (prev_control_ok/next_control_ok)
    и после хотя бы одного шага с обеими достоверными смежными (Tпк).
    """

    def __init__(
        self,
        t_s0108: float,
        t_s0208: float,
        t_lz08: float,
        t_kon: float,
    ) -> None:
        self.T_S0108 = float(t_s0108)
        self.T_S0208 = float(t_s0208)
        self.T_LZ08 = float(t_lz08)
        self.T_KON = float(t_kon)

        # В8.1 (prev): idle -> p1_done -> p2_done -> active
        self.phase_prev: str = "idle"
        self.dur_prev_p1: float = 0.0
        self.dur_prev_p2: float = 0.0
        self.dur_prev_tail: float = 0.0

        # В8.2 (next): idle -> p1_done -> p2_done -> active
        self.phase_next: str = "idle"
        self.dur_next_p1: float = 0.0
        # Фаза 2 для 8.2: две альтернативы
        self.dur_next_p2_prev_free: float = 0.0  # 8.2.1: 0-1-*
        self.dur_next_p2_next_free: float = 0.0  # 8.2.2: *-1-0
        self.dur_next_tail: float = 0.0

        # В8.3 (mid): idle -> p1_done -> p2_done -> active
        self.phase_mid: str = "idle"
        self.dur_mid_p1: float = 0.0
        self.dur_mid_p2: float = 0.0
        self.dur_mid_tail: float = 0.0

        # Завершение ДС
        self.dur_free_after_lz: float = 0.0

        # Общий флаг активного ДС по варианту 8
        self.active: bool = False

        # Был ли хоть один шаг с двумя достоверными смежными (Tпк)
        self.seen_full_adj: bool = False

        # Отладка (если нужно печатать шаг открытия)
        self._debug_step_idx: int = 0

    def reset(self) -> None:
        # В8.1
        self.phase_prev = "idle"
        self.dur_prev_p1 = 0.0
        self.dur_prev_p2 = 0.0
        self.dur_prev_tail = 0.0

        # В8.2
        self.phase_next = "idle"
        self.dur_next_p1 = 0.0
        self.dur_next_p2_prev_free = 0.0
        self.dur_next_p2_next_free = 0.0
        self.dur_next_tail = 0.0

        # В8.3
        self.phase_mid = "idle"
        self.dur_mid_p1 = 0.0
        self.dur_mid_p2 = 0.0
        self.dur_mid_tail = 0.0

        self.dur_free_after_lz = 0.0
        self.active = False
        # seen_full_adj не сбрасываем: информация о том, что нормальная смежность уже была,
        # действует на всём протяжении работы варианта 8.

    @staticmethod
    def _states(step: Any) -> tuple[bool, bool, bool, bool, bool, bool]:
        st_prev = step.rc_states.get("10-12SP", 0)
        st_curr = step.rc_states.get("1P", 0)
        st_next = step.rc_states.get("1-7SP", 0)

        prev_free = rc_is_free(st_prev)
        prev_occ = rc_is_occupied(st_prev)

        curr_free = rc_is_free(st_curr)
        curr_occ = rc_is_occupied(st_curr)

        next_free = rc_is_free(st_next)
        next_occ = rc_is_occupied(st_next)

        return prev_free, prev_occ, curr_free, curr_occ, next_free, next_occ

    def update(self, step: Any, dt_interval: float) -> tuple[bool, bool]:
        if dt_interval < 0:
            dt_interval = 0.0

        (
            prev_free,
            prev_occ,
            curr_free,
            curr_occ,
            next_free,
            next_occ,
        ) = self._states(step)

        modes = getattr(step, "modes", {}) or {}
        prev_control_ok = bool(
            modes.get("prevcontrolok", modes.get("prev_control_ok", False))
        )
        next_control_ok = bool(
            modes.get("nextcontrolok", modes.get("next_control_ok", False))
        )

        # Запоминаем факт наличия корректной смежности с обеих сторон
        if prev_control_ok and next_control_ok:
            self.seen_full_adj = True

        opened = False
        closed = False

        # Если ни разу не было шага с двумя достоверными смежными, ДС v8 не может стартовать
        if not self.seen_full_adj and not self.active:
            return False, False

        # --- В8.1 «предыдущая занята» ---
        if not self.active and prev_control_ok:
            if self.phase_prev == "idle":
                # Фаза 1: (Prev1,Curr1,Next0) или (Prev1,Curr1,Next1) — подряд T_S0108
                if prev_occ and curr_occ and (next_free or next_occ):
                    self.dur_prev_p1 += dt_interval
                    if self.dur_prev_p1 >= self.T_S0108:
                        self.phase_prev = "p1_done"
                        self.dur_prev_p2 = 0.0
                else:
                    self.dur_prev_p1 = 0.0

            elif self.phase_prev == "p1_done":
                # Фаза 2: Curr1,Next1 (Prev не учитывается) — подряд T_S0208
                if curr_occ and next_occ:
                    self.dur_prev_p2 += dt_interval
                    if self.dur_prev_p2 >= self.T_S0208:
                        self.phase_prev = "p2_done"
                        self.dur_prev_tail = 0.0
                else:
                    # разрыв p2 — сбрасываем только счётчик p2, оставляем p1_done
                    self.dur_prev_p2 = 0.0

            if self.phase_prev == "p2_done":
                # Хвост: Prev0,Curr1,Next0 — подряд T_LZ08
                if prev_free and curr_occ and next_free:
                    self.dur_prev_tail += dt_interval
                    if self.dur_prev_tail >= self.T_LZ08:
                        opened = True
                        self.active = True
                        self.phase_prev = "active"
                        self.dur_free_after_lz = 0.0
                else:
                    # разрыв хвоста — сбрасываем только хвост, остаёмся в p2_done
                    self.dur_prev_tail = 0.0

        # --- В8.2 «следующая занята» ---
        if not self.active and next_control_ok:
            if self.phase_next == "idle":
                # Фаза 1: (Prev*,Curr1,Next1) — подряд T_S0108 (*-1-1)
                if curr_occ and next_occ:
                    self.dur_next_p1 += dt_interval
                    if self.dur_next_p1 >= self.T_S0108:
                        self.phase_next = "p1_done"
                        self.dur_next_p2_prev_free = 0.0
                        self.dur_next_p2_next_free = 0.0
                else:
                    self.dur_next_p1 = 0.0

            elif self.phase_next == "p1_done":
                # Фаза 2: две альтернативы
                # 8.2.1: Prev0,Curr1,Next* => 0-1-*
                if prev_free and curr_occ:
                    self.dur_next_p2_prev_free += dt_interval
                else:
                    self.dur_next_p2_prev_free = 0.0

                # 8.2.2: Prev*,Curr1,Next0 => *-1-0
                if curr_occ and next_free:
                    self.dur_next_p2_next_free += dt_interval
                else:
                    self.dur_next_p2_next_free = 0.0

                if (
                    self.dur_next_p2_prev_free >= self.T_S0208
                    or self.dur_next_p2_next_free >= self.T_S0208
                ):
                    self.phase_next = "p2_done"
                    self.dur_next_tail = 0.0

            if self.phase_next == "p2_done":
                # Хвост: Prev0,Curr1,Next0 — подряд T_LZ08 (0-1-0)
                if prev_free and curr_occ and next_free:
                    self.dur_next_tail += dt_interval
                    if self.dur_next_tail >= self.T_LZ08:
                        opened = True
                        self.active = True
                        self.phase_next = "active"
                        self.dur_free_after_lz = 0.0
                else:
                    self.dur_next_tail = 0.0

        # --- В8.3 «средний» ---
        if not self.active and prev_control_ok and next_control_ok:
            if self.phase_mid == "idle":
                # Фаза 1: Prev0,Curr1,Next0 — подряд T_S0108
                if prev_free and curr_occ and next_free:
                    self.dur_mid_p1 += dt_interval
                    if self.dur_mid_p1 >= self.T_S0108:
                        self.phase_mid = "p1_done"
                        self.dur_mid_p2 = 0.0
                else:
                    self.dur_mid_p1 = 0.0

            elif self.phase_mid == "p1_done":
                # Фаза 2: Prev0,Curr1,Next1 — подряд T_S0208
                if prev_free and curr_occ and next_occ:
                    self.dur_mid_p2 += dt_interval
                    if self.dur_mid_p2 >= self.T_S0208:
                        self.phase_mid = "p2_done"
                        self.dur_mid_tail = 0.0
                else:
                    # разрыв p2 — сбрасываем только счётчик p2
                    self.dur_mid_p2 = 0.0

            if self.phase_mid == "p2_done":
                # Хвост: Prev0,Curr1,Next0 — подряд T_LZ08
                if prev_free and curr_occ and next_free:
                    self.dur_mid_tail += dt_interval
                    if self.dur_mid_tail >= self.T_LZ08:
                        opened = True
                        self.active = True
                        self.phase_mid = "active"
                        self.dur_free_after_lz = 0.0
                else:
                    # разрыв хвоста — сбрасываем только хвост
                    self.dur_mid_tail = 0.0

        # --- Завершение ДС ---
        if self.active:
            if curr_free:
                self.dur_free_after_lz += dt_interval
                if self.dur_free_after_lz >= self.T_KON:
                    closed = True
                    self.reset()
            else:
                self.dur_free_after_lz = 0.0

        self._debug_step_idx += 1
        return opened, closed

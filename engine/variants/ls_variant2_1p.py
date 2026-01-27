from typing import Any

from ..station_visochino_1p import rc_is_free, rc_is_occupied


def _states(step: Any) -> tuple[bool, bool, bool, bool, bool, bool]:
    """
    Булевы признаки занятости/свободности:
    prev_free, prev_occ, curr_free, curr_occ, next_free, next_occ.

    Prev/Next берём из глобальной смежности (modes.prev_state/next_state),
    при её отсутствии — из rc_states для бэкомпата с простыми сценариями.
    """
    modes = getattr(step, "modes", {}) or {}

    st_curr = step.rc_states.get("1P", 0)

    # Fallback: если prev_state/next_state не заданы, используем прямые РЦ
    st_prev = int(modes.get("prev_state", step.rc_states.get("10-12SP", 0)))
    st_next = int(modes.get("next_state", step.rc_states.get("1-7SP", 0)))

    prev_free = rc_is_free(st_prev)
    prev_occ = rc_is_occupied(st_prev)
    curr_free = rc_is_free(st_curr)
    curr_occ = rc_is_occupied(st_curr)
    next_free = rc_is_free(st_next)
    next_occ = rc_is_occupied(st_next)

    return prev_free, prev_occ, curr_free, curr_occ, next_free, next_occ


class VariantLS2Detector:
    """
    Вариант 2 Логической ложной свободности (ЛС2) для 1П.

    Ветка "предыдущая занята":
      S0102: Prev=1, Curr=1, Next=0 не менее T_S0102_LS.
      Хвост: Prev=1, Curr=0, Next=0 суммарно T ∈ [T_LS0102, T_LS0202].
      S0202: Prev=1, Curr=1, Next=0 не менее T_S0202_LS.

    Ветка "следующая занята":
      S0102: Prev=0, Curr=1, Next=1 не менее T_S0102_LS.
      Хвост: Prev=0, Curr=0, Next=1 суммарно T ∈ [T_LS0102, T_LS0202].
      S0202: Prev=0, Curr=1, Next=1 не менее T_S0202_LS.

    Завершение:
      После формирования ЛС2 Curr=1 суммарно не менее T_KON_LS2.

    Контроль смежных:
      - до открытия: нужна достоверность смежного по выбранной ветке,
        если ветка не выбрана — хотя бы один смежный достоверен;
      - после открытия: контролируем только Curr/T_KON_LS2.
    """

    
    def __init__(
        self,
        t_s0102: float,
        t_s0202: float,
        t_ls0102: float,
        t_ls0202: float,
        t_kon_ls2: float,
    ) -> None:
        self.T_S0102  = float(t_s0102)
        self.T_S0202  = float(t_s0202)
        self.T_LS0102 = float(t_ls0102)
        self.T_LS0202 = float(t_ls0202)
        self.T_KON_LS2 = float(t_kon_ls2)

        # prev-ветка: idle -> s0102_done -> tail_done -> active
        self.phase_prev = "idle"
        self.dur_prev_s0102 = 0.0
        self.dur_prev_tail  = 0.0
        self.dur_prev_s0202 = 0.0

        # next-ветка
        self.phase_next = "idle"
        self.dur_next_s0102 = 0.0
        self.dur_next_tail  = 0.0
        self.dur_next_s0202 = 0.0

        self.dur_occ_after_ls = 0.0
        self.active = False
        self.seen_full_adj = False

    def reset(self) -> None:
        self.phase_prev = "idle"
        self.dur_prev_s0102 = self.dur_prev_tail = self.dur_prev_s0202 = 0.0

        self.phase_next = "idle"
        self.dur_next_s0102 = self.dur_next_tail = self.dur_next_s0202 = 0.0

        self.dur_occ_after_ls = 0.0
        self.active = False

    def update(self, step: Any, dt_interval: float) -> tuple[bool, bool]:
        if dt_interval < 0:
            dt_interval = 0.0

        prev_free, prev_occ, curr_free, curr_occ, next_free, next_occ = _states(step)
        modes = getattr(step, "modes", {}) or {}
        prev_control_ok = bool(modes.get("prevcontrolok", modes.get("prev_control_ok", False)))
        next_control_ok = bool(modes.get("nextcontrolok", modes.get("next_control_ok", False)))

        if prev_control_ok and next_control_ok:
            self.seen_full_adj = True

        opened = False
        closed = False

        if not self.seen_full_adj and not self.active:
            return False, False

        # --- формирование ДС (если ещё не активно) ---
        if not self.active:
            # Ветка prev
            if prev_control_ok:
                if self.phase_prev == "idle":
                    # S0102 prev: 1-1-0 >= T_S0102_LS
                    s0102_prev = prev_occ and curr_occ and next_free
                    if s0102_prev:
                        self.dur_prev_s0102 += dt_interval
                        if self.dur_prev_s0102 >= self.T_S0102:
                            self.phase_prev = "s0102_done"
                            self.dur_prev_tail = 0.0
                    else:
                        self.dur_prev_s0102 = 0.0

                elif self.phase_prev == "s0102_done":
                    # хвост: 1-0-0, накапливаем dur_tail
                    tail_ok = prev_occ and curr_free and next_free
                    s0202_cfg = prev_occ and curr_occ and next_free
                    if tail_ok:
                        self.dur_prev_tail += dt_interval
                    elif self.dur_prev_tail > 0 and s0202_cfg:
                        # переход хвост -> S0202
                        if self.T_LS0102 <= self.dur_prev_tail <= self.T_LS0202:
                            self.phase_prev = "tail_done"
                            self.dur_prev_s0202 = 0.0
                        else:
                            # хвост некорректной длины — сброс всей ветки
                            self.phase_prev = "idle"
                            self.dur_prev_s0102 = self.dur_prev_tail = 0.0
                    elif not tail_ok and not s0202_cfg:
                        # ушли из сценария — полный сброс ветки
                        self.phase_prev = "idle"
                        self.dur_prev_s0102 = self.dur_prev_tail = 0.0

                elif self.phase_prev == "tail_done":
                    # S0202 prev: 1-1-0 >= T_S0202_LS
                    s0202_prev = prev_occ and curr_occ and next_free
                    if s0202_prev:
                        self.dur_prev_s0202 += dt_interval
                        if self.dur_prev_s0202 >= self.T_S0202:
                            opened = True
                            self.active = True
                            self.phase_prev = "active"
                            self.dur_occ_after_ls = 0.0
                    else:
                        # Сбрасываем только S0202, хвост и S0102 считаем выполненными
                        self.dur_prev_s0202 = 0.0

            # Ветка next (разрешаем, если prev не идёт)
            if not self.active and next_control_ok and self.phase_prev == "idle":
                if self.phase_next == "idle":
                    # S0102 next: 0-1-1
                    s0102_next = prev_free and curr_occ and next_occ
                    if s0102_next:
                        self.dur_next_s0102 += dt_interval
                        if self.dur_next_s0102 >= self.T_S0102:
                            self.phase_next = "s0102_done"
                            self.dur_next_tail = 0.0
                    else:
                        self.dur_next_s0102 = 0.0

                elif self.phase_next == "s0102_done":
                    tail_ok = prev_free and curr_free and next_occ
                    s0202_cfg = prev_free and curr_occ and next_occ
                    if tail_ok:
                        self.dur_next_tail += dt_interval
                    elif self.dur_next_tail > 0 and s0202_cfg:
                        if self.T_LS0102 <= self.dur_next_tail <= self.T_LS0202:
                            self.phase_next = "tail_done"
                            self.dur_next_s0202 = 0.0
                        else:
                            self.phase_next = "idle"
                            self.dur_next_s0102 = self.dur_next_tail = 0.0
                    elif not tail_ok and not s0202_cfg:
                        self.phase_next = "idle"
                        self.dur_next_s0102 = self.dur_next_tail = 0.0

                elif self.phase_next == "tail_done":
                    s0202_next = prev_free and curr_occ and next_occ
                    if s0202_next:
                        self.dur_next_s0202 += dt_interval
                        if self.dur_next_s0202 >= self.T_S0202:
                            opened = True
                            self.active = True
                            self.phase_next = "active"
                            self.dur_occ_after_ls = 0.0
                    else:
                        self.dur_next_s0202 = 0.0

        # --- завершение ДС (KON) ---
        if self.active:
            if curr_occ:
                self.dur_occ_after_ls += dt_interval
                if self.dur_occ_after_ls >= self.T_KON_LS2:
                    closed = True
                    self.reset()
            else:
                self.dur_occ_after_ls = 0.0

        return opened, closed

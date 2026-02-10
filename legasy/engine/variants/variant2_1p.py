from typing import Any

from ..station_visochino_1p import rc_is_free, rc_is_occupied


class Variant2Detector:
    """
    Интервальный детектор варианта 2 ЛЗ 1П.

    Ветка «предыдущая занята»:
        Фаза 1 (01): Prev=1, Curr=0, Next=0 не менее T_S0102 (подряд).
        Фаза 2 (02): Prev=1, Curr=1, Next=0 не менее T_LZ02 (подряд).
        Фаза 3 (КОГДА):
            Вариант 2.1: Prev=1, Curr=0, Next=0 не менее T_S0202 (подряд),
            Вариант 2.2: Prev=0, Curr=0, Next=0 не менее T_S0202 (подряд).

    Ветка «следующая занята»:
        Фаза 1 (01): Prev=0, Curr=0, Next=1 не менее T_S0102 (подряд).
        Фаза 2 (02): Prev=0, Curr=1, Next=1 не менее T_LZ02 (подряд).
        Фаза 3 (КОГДА):
            Вариант 2.1: Prev=0, Curr=0, Next=1 не менее T_S0202 (подряд),
            Вариант 2.2: Prev=0, Curr=0, Next=0 не менее T_S0202 (подряд).

    Завершение ДС:
        После формирования ДС контролируемая РЦ (1P) становится свободной (П=0)
        и остаётся свободной суммарно не менее T_KON секунд (накопление, не подряд).
    """

    def __init__(
        self,
        t_s0102: float,
        t_s0202: float,
        t_lz02: float,
        t_kon: float,
    ) -> None:
        self.T_S0102 = float(t_s0102)
        self.T_S0202 = float(t_s0202)
        self.T_LZ02 = float(t_lz02)
        self.T_KON = float(t_kon)

        # состояние ветки «предыдущая занята»: idle -> p1_done -> p2_done -> active
        self.phase_prev = "idle"
        self.dur_prev_p1 = 0.0
        self.dur_prev_p2 = 0.0
        self.dur_prev_p3 = 0.0

        # состояние ветки «следующая занята»: idle -> p1_done -> p2_done -> active
        self.phase_next = "idle"
        self.dur_next_p1 = 0.0
        self.dur_next_p2 = 0.0
        self.dur_next_p3 = 0.0

        # для завершения ДС (общий для обеих веток)
        self.dur_free_after_lz = 0.0

        # флаг, что ДС сейчас активно (по любой ветке)
        self.active = False
        self.seen_full_adj = False

    def reset(self) -> None:
        # ветка prev
        self.phase_prev = "idle"
        self.dur_prev_p1 = 0.0
        self.dur_prev_p2 = 0.0
        self.dur_prev_p3 = 0.0

        # ветка next
        self.phase_next = "idle"
        self.dur_next_p1 = 0.0
        self.dur_next_p2 = 0.0
        self.dur_next_p3 = 0.0

        self.dur_free_after_lz = 0.0
        self.active = False
        self.seen_full_adj = False

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
        prev_control_ok = bool(modes.get("prev_control_ok", False))
        next_control_ok = bool(modes.get("next_control_ok", False))
        # если на этом шаге обе смежные достоверны — запоминаем как «полноценную смежность»
        if prev_control_ok and next_control_ok:
            self.seen_full_adj = True


        opened = False
        closed = False

        # если ни разу не было состояния с двумя достоверными смежными, ДС варианта 2 не может стартовать
        if not self.seen_full_adj and not self.active:
            # не трогаем завершение уже активного ДС
            return False, False

        # Маски для ветки «предыдущая занята»
        mask_prev_p1 = prev_occ and curr_free and next_free   # 1-0-0
        mask_prev_p2 = prev_occ and curr_occ and next_free   # 1-1-0
        # Фаза 3: либо 1-0-0 (вариант 2.1), либо 0-0-0 (вариант 2.2)
        mask_prev_p3_busy = prev_occ and curr_free and next_free   # 1-0-0
        mask_prev_p3_free = prev_free and curr_free and next_free  # 0-0-0
        mask_prev_p3 = mask_prev_p3_busy or mask_prev_p3_free

        # Маски для ветки «следующая занята»
        mask_next_p1 = prev_free and curr_free and next_occ   # 0-0-1
        mask_next_p2 = prev_free and curr_occ and next_occ   # 0-1-1
        # Фаза 3: либо 0-0-1 (вариант 2.1), либо 0-0-0 (вариант 2.2)
        mask_next_p3_busy = prev_free and curr_free and next_occ   # 0-0-1
        mask_next_p3_free = prev_free and curr_free and next_free  # 0-0-0
        mask_next_p3 = mask_next_p3_busy or mask_next_p3_free

        # --- ВЕТКА «ПРЕДЫДУЩАЯ ЗАНЯТА» ---
        if not self.active and prev_control_ok:
            if self.phase_prev == "idle":
                # Фаза 1: строго 1-0-0 подряд
                if mask_prev_p1:
                    self.dur_prev_p1 += dt_interval
                    if self.dur_prev_p1 >= self.T_S0102:
                        self.phase_prev = "p1_done"
                        self.dur_prev_p2 = 0.0
                else:
                    self.dur_prev_p1 = 0.0

            elif self.phase_prev == "p1_done":
                # Фаза 2: строго 1-1-0 подряд
                if mask_prev_p2:
                    self.dur_prev_p2 += dt_interval
                    if self.dur_prev_p2 >= self.T_LZ02:
                        self.phase_prev = "p2_done"
                        self.dur_prev_p3 = 0.0
                else:
                    # любое состояние, не равное маске фазы 2, после p1_done — сброс сценария
                    self.phase_prev = "idle"
                    self.dur_prev_p1 = 0.0
                    self.dur_prev_p2 = 0.0
                    self.dur_prev_p3 = 0.0

            elif self.phase_prev == "p2_done":
                # Пока всё ещё маска фазы 2 — остаёмся в p2_done
                if mask_prev_p2:
                    pass
                elif mask_prev_p3:
                    # Фаза 3: (1-0-0) ИЛИ (0-0-0) подряд
                    self.dur_prev_p3 += dt_interval
                    if self.dur_prev_p3 >= self.T_S0202:
                        opened = True
                        self.active = True
                        self.phase_prev = "active"
                        self.dur_free_after_lz = 0.0
                else:
                    # любое другое состояние после p2_done — полный сброс
                    self.phase_prev = "idle"
                    self.dur_prev_p1 = 0.0
                    self.dur_prev_p2 = 0.0
                    self.dur_prev_p3 = 0.0

        # --- ВЕТКА «СЛЕДУЮЩАЯ ЗАНЯТА» ---
        if not self.active and next_control_ok and self.phase_prev == "idle":
            if self.phase_next == "idle":
                # Фаза 1: строго 0-0-1 подряд
                if mask_next_p1:
                    self.dur_next_p1 += dt_interval
                    if self.dur_next_p1 >= self.T_S0102:
                        self.phase_next = "p1_done"
                        self.dur_next_p2 = 0.0
                else:
                    self.dur_next_p1 = 0.0

            elif self.phase_next == "p1_done":
                # Фаза 2: строго 0-1-1 подряд
                if mask_next_p2:
                    self.dur_next_p2 += dt_interval
                    if self.dur_next_p2 >= self.T_LZ02:
                        self.phase_next = "p2_done"
                        self.dur_next_p3 = 0.0
                else:
                    # любое состояние, не равное маске фазы 2, после p1_done — сброс
                    self.phase_next = "idle"
                    self.dur_next_p1 = 0.0
                    self.dur_next_p2 = 0.0
                    self.dur_next_p3 = 0.0

            elif self.phase_next == "p2_done":
                # Пока всё ещё маска фазы 2 — остаёмся в p2_done
                if mask_next_p2:
                    pass
                elif mask_next_p3:
                    # Фаза 3: (0-0-1) ИЛИ (0-0-0) подряд
                    self.dur_next_p3 += dt_interval
                    if self.dur_next_p3 >= self.T_S0202:
                        opened = True
                        self.active = True
                        self.phase_next = "active"
                        self.dur_free_after_lz = 0.0
                else:
                    # любое другое состояние после p2_done — сброс
                    self.phase_next = "idle"
                    self.dur_next_p1 = 0.0
                    self.dur_next_p2 = 0.0
                    self.dur_next_p3 = 0.0

        # --- ЗАВЕРШЕНИЕ ДС ---
        if self.active:
            if curr_free:
                self.dur_free_after_lz += dt_interval
                if self.dur_free_after_lz >= self.T_KON:
                    closed = True
                    self.reset()
            else:
                self.dur_free_after_lz = 0.0

        return opened, closed

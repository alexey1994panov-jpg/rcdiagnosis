from typing import Any

from ..station_visochino_1p import rc_is_free, rc_is_occupied


class Variant3Detector:
    """
    Интервальный детектор варианта 3 ЛЗ 1П.

    Фаза 1: Prev=1, Curr=0, Next=1 не менее T_S0103 подряд.
    Фаза 2: Prev=1, Curr=1, Next=1 не менее T_LZ03 суммарно.
    Фаза 3: Prev=1, Curr=0, Next=1 не менее T_S0203 суммарно.

    Завершение ДС:
    После формирования ДС контролируемая РЦ (1P) свободна суммарно
    не менее T_KON секунд (накопление, не подряд).

    До открытия ДС требуются достоверные обе смежные (prev_control_ok, next_control_ok).
    После открытия ДС потеря достоверности смежных на завершение не влияет.
    """

    def __init__(
        self,
        t_s0103: float,
        t_s0203: float,
        t_lz03: float,
        t_kon: float,
    ) -> None:
        self.T_S0103 = float(t_s0103)
        self.T_S0203 = float(t_s0203)
        self.T_LZ03 = float(t_lz03)
        self.T_KON = float(t_kon)

        self.phase = "idle"
        self.dur_p1 = 0.0
        self.dur_p2 = 0.0
        self.dur_p3 = 0.0
        self.dur_free_after_lz = 0.0
        self.active = False

    def reset(self) -> None:
        self.phase = "idle"
        self.dur_p1 = 0.0
        self.dur_p2 = 0.0
        self.dur_p3 = 0.0
        self.dur_free_after_lz = 0.0
        self.active = False

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
        # по умолчанию смежные считаем недостоверными, если simulate_1p их не проставил
        prev_control_ok = bool(modes.get("prev_control_ok", False))
        next_control_ok = bool(modes.get("next_control_ok", False))

        opened = False
        closed = False

        # --- ФОРМИРОВАНИЕ ДС (ФАЗЫ 1–3) ---
        if not self.active:
            # до открытия требуем достоверные обе смежные
            if not (prev_control_ok and next_control_ok):
                # нет достоверных смежных — сбрасываем фазы и не накапливаем выдержки
                self.phase = "idle"
                self.dur_p1 = 0.0
                self.dur_p2 = 0.0
                self.dur_p3 = 0.0
            else:
                if self.phase == "idle":
                    # Фаза 1: Prev=1, Curr=0, Next=1 подряд
                    if prev_occ and curr_free and next_occ:
                        self.dur_p1 += dt_interval
                        if self.dur_p1 >= self.T_S0103:
                            self.phase = "p1_done"
                    else:
                        self.dur_p1 = 0.0

                elif self.phase == "p1_done":
                    # Фаза 2: Prev=1, Curr=1, Next=1 — накопление суммарно
                    if prev_occ and curr_occ and next_occ:
                        self.dur_p2 += dt_interval
                        if self.dur_p2 >= self.T_LZ03:
                            self.phase = "p2_done"
                    # при иных состояниях dur_p2 не сбрасываем

                elif self.phase == "p2_done":
                    # Фаза 3: Prev=1, Curr=0, Next=1 — накопление суммарно
                    if prev_occ and curr_free and next_occ:
                        self.dur_p3 += dt_interval
                        if self.dur_p3 >= self.T_S0203:
                            opened = True
                            self.active = True
                            self.phase = "active"
                            self.dur_free_after_lz = 0.0
                    # при иных состояниях dur_p3 не сбрасываем

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

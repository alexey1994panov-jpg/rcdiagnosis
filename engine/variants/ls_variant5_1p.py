from typing import Any, Tuple

from ..station_visochino_1p import rc_is_free, rc_is_occupied


class VariantLS5Detector:
    """
    ЛС v5: логическая ложная свободность по трём РЦ (prev, curr, next).

    Ветка 5.1 (предыдущая занята):
      Фаза 1: prev=1, curr=0, next=0 (1-0-0) подряд не менее T_S0105.
      Фаза 2: prev=1, curr=0, next=1 (1-0-1) подряд не менее T_LS05.

    Ветка 5.2 (следующая занята):
      Фаза 1: prev=0, curr=0, next=1 (0-0-1) подряд не менее T_S0105.
      Фаза 2: prev=1, curr=0, next=1 (1-0-1) подряд не менее T_LS05.

    Завершение:
      после формирования ДС контролируемая РЦ (curr) занята подряд не менее T_KON.

    До открытия ДС требуются достоверные обе смежные (prev_control_ok, next_control_ok).
    После открытия ДС потеря достоверности смежных на завершение не влияет.

    После первого завершения (closed) ЛС5 больше не формируется до конца сценария,
    если ever_closed=True.
    """

    def __init__(
        self,
        prev_rc_id: str,
        ctrl_rc_id: str,
        next_rc_id: str,
        t_s0105: float,
        t_ls05: float,
        t_kon: float,
        ever_closed: bool = True,
    ) -> None:
        # Имя РЦ оставляем, чтобы детектор был универсальным для других станций,
        # но логика для Височино использует их как prev/curr/next.
        self.prev_rc_id = prev_rc_id
        self.ctrl_rc_id = ctrl_rc_id
        self.next_rc_id = next_rc_id

        self.T_S0105 = float(t_s0105)
        self.T_LS05 = float(t_ls05)
        self.T_KON = float(t_kon)
        self.ever_closed_enabled = bool(ever_closed)

        # Фазы:
        # idle
        #   -> p1_prev / p1_next (накопление фазы 1)
        #   -> p1_prev_done / p1_next_done (фаза 1 выполнена)
        #   -> p2_prev / p2_next (накопление фазы 2)
        #   -> active
        self.phase: str = "idle"

        self.dur_p1: float = 0.0          # длительность фазы 1
        self.dur_p2: float = 0.0          # длительность фазы 2
        self.dur_occ_after_ls: float = 0.0  # занятость curr после ЛС для завершения

        self.active: bool = False
        self.ever_closed: bool = False

    # -------- вспомогательные --------

    def _states(self, step: Any) -> tuple[bool, bool, bool, bool, bool, bool]:
        """
        prev_free, prev_occ, curr_free, curr_occ, next_free, next_occ.
        """
        st_prev = step.rc_states.get(self.prev_rc_id, 0)
        st_curr = step.rc_states.get(self.ctrl_rc_id, 0)
        st_next = step.rc_states.get(self.next_rc_id, 0)

        prev_free = rc_is_free(st_prev)
        prev_occ = rc_is_occupied(st_prev)

        curr_free = rc_is_free(st_curr)
        curr_occ = rc_is_occupied(st_curr)

        next_free = rc_is_free(st_next)
        next_occ = rc_is_occupied(st_next)

        return prev_free, prev_occ, curr_free, curr_occ, next_free, next_occ

    @staticmethod
    def _control_ok(step: Any, ctrl_rc_id: str) -> Tuple[bool, bool]:
        """
        prev_control_ok, next_control_ok по ctrl_rc_id.

        Берём либо персональные флаги <ctrl>_prev_control_ok / <ctrl>_next_control_ok,
        либо общие prev_control_ok / next_control_ok.
        """
        modes = getattr(step, "modes", {}) or {}
        key = ctrl_rc_id
        prev_ok = bool(modes.get(f"{key}_prev_control_ok", modes.get("prev_control_ok", False)))
        next_ok = bool(modes.get(f"{key}_next_control_ok", modes.get("next_control_ok", False)))
        return prev_ok, next_ok

    def _soft_reset(self) -> None:
        """Сброс фаз без обнуления ever_closed."""
        self.phase = "idle"
        self.dur_p1 = 0.0
        self.dur_p2 = 0.0
        self.dur_occ_after_ls = 0.0
        self.active = False

    def reset(self) -> None:
        """Полный сброс между сценариями."""
        self._soft_reset()
        self.ever_closed = False

    # -------- основной метод --------

    def update(self, step: Any, dt_interval: float) -> tuple[bool, bool, bool]:
        """
        :return: (opened, active, closed)
        """
        if dt_interval < 0.0:
            dt_interval = 0.0

        (
            prev_free,
            prev_occ,
            curr_free,
            curr_occ,
            next_free,
            next_occ,
        ) = self._states(step)

        prev_ok, next_ok = self._control_ok(step, self.ctrl_rc_id)

        opened = False
        closed = False

        # Повторное формирование запрещено
        if self.ever_closed_enabled and self.ever_closed:
            return False, False, False

        # До открытия ДС требуем достоверные обе смежные
        if not self.active:
            if not (prev_ok and next_ok):
                self._soft_reset()
                return opened, self.active, closed

        # Конфигурации масок
        cfg_p1_prev = prev_occ and curr_free and next_free   # 1-0-0 (ветка 5.1)
        cfg_p1_next = prev_free and curr_free and next_occ   # 0-0-1 (ветка 5.2)
        cfg_p2 = prev_occ and curr_free and next_occ         # 1-0-1 (фаза 2 для обеих веток)

        # --- Формирование ДС ---
        if not self.active:
            if self.phase == "idle":
                # фаза 1 по любой ветке
                self.dur_p1 = 0.0
                self.dur_p2 = 0.0
                self.dur_occ_after_ls = 0.0

                if cfg_p1_prev:
                    self.dur_p1 = dt_interval
                    if self.dur_p1 >= self.T_S0105:
                        self.phase = "p1_prev_done"
                    else:
                        self.phase = "p1_prev"
                elif cfg_p1_next:
                    self.dur_p1 = dt_interval
                    if self.dur_p1 >= self.T_S0105:
                        self.phase = "p1_next_done"
                    else:
                        self.phase = "p1_next"
                else:
                    # нет подходящей маски для старта
                    pass

            elif self.phase == "p1_prev":
                if cfg_p1_prev:
                    self.dur_p1 += dt_interval
                    if self.dur_p1 >= self.T_S0105:
                        self.phase = "p1_prev_done"
                else:
                    # фаза 1 оборвалась до выдержки
                    self._soft_reset()

            elif self.phase == "p1_next":
                if cfg_p1_next:
                    self.dur_p1 += dt_interval
                    if self.dur_p1 >= self.T_S0105:
                        self.phase = "p1_next_done"
                else:
                    self._soft_reset()

            elif self.phase in ("p1_prev_done", "p1_next_done"):
                # фаза 1 уже выполнена по времени, ждём маску фазы 2
                if cfg_p2:
                    self.dur_p2 = dt_interval
                    if self.dur_p2 >= self.T_LS05:
                        opened = True
                        self.active = True
                        self.phase = "active"
                        self.dur_occ_after_ls = 0.0
                    else:
                        # нужна более длинная фаза 2
                        self.phase = "p2_prev" if self.phase == "p1_prev_done" else "p2_next"
                else:
                    # ушли в другое состояние до начала фазы 2
                    self._soft_reset()

            elif self.phase == "p2_prev":
                if cfg_p2:
                    self.dur_p2 += dt_interval
                    if self.dur_p2 >= self.T_LS05:
                        opened = True
                        self.active = True
                        self.phase = "active"
                        self.dur_occ_after_ls = 0.0
                else:
                    self._soft_reset()

            elif self.phase == "p2_next":
                if cfg_p2:
                    self.dur_p2 += dt_interval
                    if self.dur_p2 >= self.T_LS05:
                        opened = True
                        self.active = True
                        self.phase = "active"
                        self.dur_occ_after_ls = 0.0
                else:
                    self._soft_reset()

        # --- Завершение ДС по занятости curr ---
        if self.phase == "active" and self.active:
            if curr_occ:
                self.dur_occ_after_ls += dt_interval
                if self.dur_occ_after_ls >= self.T_KON:
                    closed = True
                    self.ever_closed = True
                    self._soft_reset()
            else:
                # при свободности сбрасываем только таймер завершения
                self.dur_occ_after_ls = 0.0

        return opened, self.active, closed

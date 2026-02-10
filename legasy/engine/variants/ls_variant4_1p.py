from typing import Any

from ..station_visochino_1p import rc_is_free, rc_is_occupied


def _states(step: Any) -> tuple[bool, bool, bool, bool, bool, bool]:
    """
    prev_free, prev_occ, curr_free, curr_occ, next_free, next_occ.
    """
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


class VariantLS4Detector:
    """
    Вариант 4 ЛС (ложная свободность 1П).

    Фазы (по контролируемой 1П и смежным):
      idle
        -> s0104 (накоплена фаза S0104: 1-1-1 подряд не менее T_S0104)
        -> tail  (хвост: 1-0-1 суммарно в интервале [T_LS0104, T_LS0204])
        -> s0204 (фаза S0204: 1-1-1 подряд не менее T_S0204)
        -> active
        -> closed

    После первого завершения (closed) ЛС4 больше НЕ формируется до конца сценария.
    """

    def __init__(
        self,
        t_s0104: float,
        t_s0204: float,
        t_ls0104: float,
        t_ls0204: float,
        t_kon_ls4: float,
    ) -> None:
        self.T_S0104 = float(t_s0104)
        self.T_S0204 = float(t_s0204)
        self.T_LS0104 = float(t_ls0104)
        self.T_LS0204 = float(t_ls0204)
        self.T_KON_LS4 = float(t_kon_ls4)

        self.phase: str = "idle"
        self.dur_s0104: float = 0.0       # подряд 1-1-1 до S0104
        self.dur_tail: float = 0.0        # суммарный хвост 1-0-1
        self.dur_s0204: float = 0.0       # подряд 1-1-1 до S0204
        self.dur_occ_after_ls: float = 0.0  # занятость после ЛС

        self.active: bool = False
        self.ever_closed: bool = False

    def _soft_reset(self) -> None:
        """Сброс фаз без обнуления ever_closed."""
        self.phase = "idle"
        self.dur_s0104 = 0.0
        self.dur_tail = 0.0
        self.dur_s0204 = 0.0
        self.dur_occ_after_ls = 0.0
        self.active = False

    def reset(self) -> None:
        """Полный сброс детектора между сценариями."""
        self._soft_reset()
        self.ever_closed = False

    def update(self, step: Any, dt_interval: float) -> tuple[bool, bool]:
        """
        Обновление детектора на интервале dt_interval.
        Возвращает (opened, closed).
        """
        if dt_interval < 0.0:
            dt_interval = 0.0

        (
            _prev_free,
            prev_occ,
            curr_free,
            curr_occ,
            _next_free,
            next_occ,
        ) = _states(step)

        modes = getattr(step, "modes", {}) or {}
        prev_control_ok = bool(
            modes.get("prevcontrolok", modes.get("prev_control_ok", True))
        )
        next_control_ok = bool(
            modes.get("nextcontrolok", modes.get("next_control_ok", True))
        )

        opened = False
        closed = False

        # Если ЛС4 уже была закрыта раньше — больше не формируем её
        if self.ever_closed:
            return False, False

        # --- если ДС ещё не активно, контролируем достоверность смежных ---
        if not self.active:
            if not (prev_control_ok and next_control_ok):
                # недостоверные смежные — сброс фаз, но оставляем ever_closed
                self._soft_reset()
                return False, False

        # Конфигурации
        s0104_cfg = prev_occ and curr_occ and next_occ   # 1-1-1
        tail_cfg = prev_occ and curr_free and next_occ   # 1-0-1
        s0204_cfg = s0104_cfg                            # 1-1-1

        # --- формирование ДС ---
        if not self.active:
            if self.phase == "idle":
                # Фаза S0104: подряд 1-1-1
                if s0104_cfg:
                    self.dur_s0104 += dt_interval
                    if self.dur_s0104 >= self.T_S0104:
                        self.phase = "s0104"
                        # хвост ещё не начался
                        self.dur_tail = 0.0
                else:
                    self.dur_s0104 = 0.0

            elif self.phase == "s0104":
                # После S0104 ждём хвост 1-0-1
                if tail_cfg:
                    self.phase = "tail"
                    self.dur_tail = dt_interval
                elif s0104_cfg:
                    # продолжается 1-1-1 — просто держим фазу s0104,
                    # повторно S0104 не накапливаем
                    pass
                else:
                    # ушли из сценария
                    self._soft_reset()

            elif self.phase == "tail":
                # Хвост: суммарно 1-0-1 в диапазоне [T_LS0104, T_LS0204]
                if tail_cfg:
                    self.dur_tail += dt_interval
                    if self.dur_tail > self.T_LS0204:
                        # хвост слишком длинный
                        self._soft_reset()
                elif s0204_cfg and self.dur_tail > 0.0:
                    # переход в S0204 возможен только если хвост в допуске
                    if self.T_LS0104 <= self.dur_tail <= self.T_LS0204:
                        self.phase = "s0204"
                        self.dur_s0204 = 0.0
                    else:
                        self._soft_reset()
                else:
                    # состояние не хвост и не начало S0204 — сброс
                    self._soft_reset()

            elif self.phase == "s0204":
                # Фаза S0204: подряд 1-1-1
                if s0204_cfg:
                    self.dur_s0204 += dt_interval
                    if self.dur_s0204 >= self.T_S0204:
                        opened = True
                        self.active = True
                        self.phase = "active"
                        self.dur_occ_after_ls = 0.0
                else:
                    # потеряли маску S0204 до выполнения выдержки
                    self._soft_reset()

        # --- завершение ДС ---
        if self.phase == "active" and self.active:
            if curr_occ:
                self.dur_occ_after_ls += dt_interval
                if self.dur_occ_after_ls >= self.T_KON_LS4:
                    closed = True
                    self.ever_closed = True
                    self._soft_reset()
            else:
                # при свободности сбрасываем только таймер завершения
                self.dur_occ_after_ls = 0.0

        return opened, closed

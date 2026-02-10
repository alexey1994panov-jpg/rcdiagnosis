# engine/variants/ls_variant9_1p.py

from typing import Any, List

from ..station_visochino_1p import rc_is_free, rc_is_occupied
from .common_1p import is_exception, get_mode


def _curr_states(step: Any, rc_id: str) -> tuple[bool, bool]:
    """
    curr_free, curr_occ для произвольной РЦ rc_id.
    """
    st_curr = step.rc_states.get(rc_id, 0)
    curr_free = rc_is_free(st_curr)
    curr_occ = rc_is_occupied(st_curr)
    return curr_free, curr_occ


class VariantLS9Detector:
    """
    Вариант 9 ЛС (логическая ложная свободность) для одной контролируемой РЦ.

    Фазы:
      idle -> s0109 -> tail -> s0209 -> active -> closed

    Формирование ДС:
      ДАНО:
        - контролируемая РЦ занята (П=1) на время >= T_S0109;
        - затем свободна (П=0) на время T_LS0109 <= T <= T_LS0209;
      КОГДА:
        - затем снова занята (П=1) на время >= T_S0209;
        - и НЕ зафиксировано исключение is_exception(...) ИЛИ включена тестовая проверка;
      ТОГДА:
        - формируется ДС "Логическая ложная свободность" (opened=True).

    Завершение ДС:
      ДАНО:
        - ДС сформирован;
      КОГДА:
        - контролируемая РЦ занята (П=1) на время >= T_KON;
      ТОГДА:
        - закрыть ДС (closed=True) и больше его не формировать до конца сценария.
    """

    def __init__(
        self,
        rc_id: str,
        t_s0109: float,
        t_s0209: float,
        t_ls0109: float,
        t_ls0209: float,
        t_kon: float,
    ) -> None:
        self.rc_id = rc_id

        self.T_S0109 = float(t_s0109)
        self.T_S0209 = float(t_s0209)
        self.T_LS0109 = float(t_ls0109)
        self.T_LS0209 = float(t_ls0209)
        self.T_KON = float(t_kon)

        self.phase: str = "idle"
        self.dur_s0109: float = 0.0
        self.dur_tail: float = 0.0
        self.dur_s0209: float = 0.0
        self.dur_occ_after_ls: float = 0.0

        self.active: bool = False
        self.tail_running: bool = False
        self.ever_closed: bool = False

    def _soft_reset(self) -> None:
        self.phase = "idle"
        self.dur_s0109 = 0.0
        self.dur_tail = 0.0
        self.dur_s0209 = 0.0
        self.dur_occ_after_ls = 0.0
        self.active = False
        self.tail_running = False

    def reset(self) -> None:
        self._soft_reset()
        self.ever_closed = False

    def update(
        self,
        history: List[Any],
        idx: int,
        dt_interval: float,
    ) -> tuple[bool, bool]:
        """
        Обновление детектора на шаге history[idx].
        history — список ScenarioStep, idx — индекс текущего шага.
        """
        if dt_interval < 0.0:
            dt_interval = 0.0

        step = history[idx]
        curr_free, curr_occ = _curr_states(step, self.rc_id)

        opened = False
        closed = False

        if self.ever_closed:
            return False, False

        # --- формирование ДС ---
        if not self.active:
            if self.phase == "idle":
                # Фаза S0109 — занятость
                if curr_occ:
                    self.dur_s0109 += dt_interval
                    if self.dur_s0109 >= self.T_S0109:
                        self.phase = "s0109"
                        self.dur_tail = 0.0
                        self.tail_running = False
                else:
                    self._soft_reset()

            elif self.phase == "s0109":
                # Либо продолжаем S0109, либо переходим в хвост
                if curr_occ:
                    self.dur_s0109 += dt_interval
                elif curr_free:
                    self.phase = "tail"
                    self.tail_running = True
                    self.dur_tail += dt_interval
                else:
                    self._soft_reset()

            elif self.phase == "tail":
                if curr_free:
                    self.tail_running = True
                    self.dur_tail += dt_interval
                    if self.dur_tail > self.T_LS0209:
                        self._soft_reset()
                elif curr_occ and self.tail_running:
                    # хвост закончился, проверяем диапазон
                    if self.T_LS0109 <= self.dur_tail <= self.T_LS0209:
                        self.phase = "s0209"
                        self.dur_s0209 = dt_interval
                    else:
                        self._soft_reset()
                else:
                    self._soft_reset()

            elif self.phase == "s0209":
                if curr_occ:
                    self.dur_s0209 += dt_interval
                    if self.dur_s0209 >= self.T_S0209:
                        has_exception = is_exception(history, idx)
                        test_mode = get_mode(step, "test_check_ls9_active")
                        if (not has_exception) or test_mode:
                            opened = True
                            self.active = True
                            self.phase = "active"
                            self.dur_occ_after_ls = 0.0
                        else:
                            self._soft_reset()
                else:
                    self._soft_reset()

        # --- завершение ДС ---
        if self.phase == "active" and self.active:
            if curr_occ:
                self.dur_occ_after_ls += dt_interval
                if self.dur_occ_after_ls >= self.T_KON:
                    closed = True
                    self.ever_closed = True
                    self._soft_reset()
            else:
                # обрывы занятости сбрасывают только таймер завершения
                self.dur_occ_after_ls = 0.0

        return opened, closed

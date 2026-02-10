# engine/occupancy/variant11_1p.py

from typing import Any, Tuple

from ..station_visochino_1p import (
    rc_is_free,
    rc_is_occupied,
    signal_is_closed,
    signal_is_shunting,
)


class Variant11Detector:
    """
    Вариант 11 ЛЗ.

    Работает только по:
      - контролируемой РЦ (ctrl_rc_id, для 1П это "1P"),
      - двум смежным светофорам, для которых контролируемая РЦ является следующей по ссылке.

    Параметры:
      T_S11  — длительность фазы ДАНО (контролируемая свободна, оба светофора закрыты);
      T_LZ11 — длительность фазы КОГДА (контролируемая занята, оба светофора закрыты);
      T_KON  — время свободности контролируемой РЦ для завершения ДС.

    Формирование ДС "Логическая ложная занятость":
      ДАНО:
        - ctrl_rc свободна (П=0);
        - оба смежных светофора закрыты (С=0 или МС=0);
        - условия выдержаны >= T_S11.
      КОГДА:
        - ctrl_rc занята (П=1);
        - оба тех же светофора закрыты (С=0 или МС=0);
        - условия выдержаны >= T_LZ11;
        - и нет активных исключений / тестовой проверки (обрабатывается вне детектора).

    Завершение ДС:
      - ДС сформирован;
      - ctrl_rc свободна (П=0) подряд не менее T_KON.
    """

    def __init__(
        self,
        ctrl_rc_id: str,
        sig_ids: tuple[str, str],
        t_s11: float,
        t_lz11: float,
        t_kon: float,
    ) -> None:
        # Идентификатор контролируемой РЦ и парa смежных светофоров
        self.ctrl_rc_id = ctrl_rc_id
        self.sig_ids = sig_ids  # (sig_a, sig_b)

        self.T_S11 = float(t_s11)
        self.T_LZ11 = float(t_lz11)
        self.T_KON = float(t_kon)

        # Фазы:
        # "idle" -> "s11_done" -> "active"
        self.phase: str = "idle"

        # длительность ДАНО (ctrl free + оба светофора закрыты)
        self.dur_dano: float = 0.0
        # длительность КОГДА (ctrl occ + оба светофора закрыты)
        self.dur_lz: float = 0.0
        # длительность свободности после ДС для завершения
        self.dur_free_after_lz: float = 0.0

        # активность ДС
        self.active: bool = False

    def reset(self) -> None:
        """Полный сброс детектора."""
        self.phase = "idle"
        self.dur_dano = 0.0
        self.dur_lz = 0.0
        self.dur_free_after_lz = 0.0
        self.active = False

    def _ctrl_states(self, step: Any) -> Tuple[bool, bool]:
        """Возвращает (ctrl_free, ctrl_occ) для контролируемой РЦ."""
        st_curr = step.rc_states.get(self.ctrl_rc_id, 0)
        ctrl_free = rc_is_free(st_curr)
        ctrl_occ = rc_is_occupied(st_curr)
        return ctrl_free, ctrl_occ

    def _both_signals_closed(self, step: Any) -> bool:
        """
        Проверка: оба смежных светофора
        (для которых ctrl_rc является следующей) закрыты (С=0 или МС=0).
        """
        sig_state_map = getattr(step, "signal_states", None) or {}
        sig_a_id, sig_b_id = self.sig_ids

        st_a = sig_state_map.get(sig_a_id, 0)
        st_b = sig_state_map.get(sig_b_id, 0)

        # трактуем shunting как закрытый/разрешающий маневровый по ТЗ "С=0 или МС=0"
        closed_a = signal_is_closed(st_a) or signal_is_shunting(st_a)
        closed_b = signal_is_closed(st_b) or signal_is_shunting(st_b)

        return closed_a and closed_b

    def update(self, step: Any, dt_interval: float) -> Tuple[bool, bool]:
        """
        Обновление детектора по шагу сценария.

        :param step: ScenarioStep (используются rc_states, signal_states)
        :param dt_interval: длительность шага, с
        :return: (opened, closed)
                 opened=True  -> сформирован ДС "Логическая ложная занятость"
                 closed=True  -> завершён ДС "Логическая ложная занятость"
        """
        if dt_interval <= 0.0:
            dt_interval = 0.0

        opened = False
        closed = False

        ctrl_free, ctrl_occ = self._ctrl_states(step)
        both_closed = self._both_signals_closed(step)

        # --- Завершение ДС, если он уже активен ---
        if self.active and self.phase == "active":
            if ctrl_free:
                self.dur_free_after_lz += dt_interval
                if self.dur_free_after_lz >= self.T_KON:
                    closed = True
                    self.reset()
            elif ctrl_occ:
                # РЦ снова занята — сбрасываем накопление свободности
                self.dur_free_after_lz = 0.0
            else:
                # Неопределённое состояние — не накапливаем
                self.dur_free_after_lz = 0.0

            return opened, closed

        # --- Формирование ДС (ДАНО + КОГДА) ---

        # Ещё не активен ДС
        if not self.active:
            if self.phase == "idle":
                # ДАНО: ctrl_free и оба светофора закрыты
                if ctrl_free and both_closed:
                    self.dur_dano += dt_interval
                    if self.dur_dano >= self.T_S11:
                        self.phase = "s11_done"
                else:
                    self.dur_dano = 0.0
                    self.dur_lz = 0.0

            elif self.phase == "s11_done":
                # КОГДА: ctrl_occ и оба светофора закрыты
                if ctrl_occ and both_closed:
                    self.dur_lz += dt_interval
                    if self.dur_lz >= self.T_LZ11:
                        opened = True
                        self.active = True
                        self.phase = "active"
                        self.dur_free_after_lz = 0.0
                elif ctrl_free and both_closed:
                    # остаёмся в ДАНО: допускаем, что free-состояние продолжается
                    self.dur_dano += dt_interval
                    self.dur_lz = 0.0
                else:
                    # потеряли условия – полный сброс последовательности
                    self.reset()

        return opened, closed

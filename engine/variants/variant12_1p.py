# engine/occupancy/variant12_1p.py

from typing import Any, Tuple

from ..station_visochino_1p import (
    rc_is_free,
    rc_is_occupied,
)


class Variant12Detector:
    """
    Вариант 12 ЛЗ.

    Работает по трём РЦ:
      - prev: предыдущая РЦ,
      - curr: контролируемая РЦ,
      - next: следующая РЦ.

    Параметры:
      T_S0112, T_S0212 — длительности фаз 01/02;
      T_LZ12           — длительность фазы КОГДА;
      T_KON            — время на завершение ситуации (освобождение curr).

    Ветка 12.1 (предыдущая не контролируется):
      Фаза 01: prev NC, curr занята, next свободна    (>= T_S0112)
      Фаза 02: prev NC, curr занята, next занята      (>= T_S0212)
      КОГДА:  prev NC, curr занята, next свободна     (>= T_LZ12)

    Ветка 12.2 (следующая не контролируется):
      Фаза 01: prev свободна, curr занята, next NC    (>= T_S0112)
      Фаза 02: prev занята,  curr занята, next NC     (>= T_S0212)
      КОГДА:  prev свободна, curr занята, next NC     (>= T_LZ12)

    Завершение ДС:
      ДС активна пока curr занята.
      Как только curr свободна подряд >= T_KON — ДС завершается.
    """

    def __init__(
        self,
        prev_rc_id: str,
        ctrl_rc_id: str,
        next_rc_id: str,
        t_s0112: float,
        t_s0212: float,
        t_lz12: float,
        t_kon: float,
    ) -> None:
        self.prev_rc_id = prev_rc_id
        self.ctrl_rc_id = ctrl_rc_id
        self.next_rc_id = next_rc_id

        self.T_S0112 = float(t_s0112)
        self.T_S0212 = float(t_s0212)
        self.T_LZ12 = float(t_lz12)
        self.T_KON = float(t_kon)

        # idle -> p1_12_1 / p1_12_2 -> p2_12_1 / p2_12_2 -> active
        self.phase: str = "idle"

        self.dur_p1: float = 0.0
        self.dur_p2: float = 0.0
        self.dur_lz: float = 0.0
        self.dur_free_after_lz: float = 0.0

        self.active: bool = False

    def reset(self) -> None:
        """Полный сброс детектора."""
        self.phase = "idle"
        self.dur_p1 = 0.0
        self.dur_p2 = 0.0
        self.dur_lz = 0.0
        self.dur_free_after_lz = 0.0
        self.active = False

    def _states(self, step: Any) -> Tuple[bool, bool, bool, bool, bool, bool]:
        """
        prev_free, prev_occ,
        curr_free, curr_occ,
        next_free, next_occ
        по состояниям для ctrl_rc_id из modes.

        prev/curr/next для варианта считаются на уровне станции и кладутся в modes:
          <ctrl>_prev_state, <ctrl>_next_state.
        """
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

        return (
            prev_free,
            prev_occ,
            curr_free,
            curr_occ,
            next_free,
            next_occ,
        )

    @staticmethod
    def _nc_flags(step: Any, ctrl_rc_id: str) -> Tuple[bool, bool]:
        """
        prev_nc, next_nc по флагам смежности для конкретной ctrl_rc_id.

        Используется информация из simulate_1p / compute_local_adjacency:
          modes["<ctrl>_prev_nc"], modes["<ctrl>_next_nc"].
        """
        modes = getattr(step, "modes", {}) or {}
        key = ctrl_rc_id
        prev_nc = bool(modes.get(f"{key}_prev_nc", False))
        next_nc = bool(modes.get(f"{key}_next_nc", False))
        return prev_nc, next_nc

    def update(self, step: Any, dt_interval: float) -> Tuple[bool, bool]:
        """
        Обновление детектора по шагу сценария.

        :param step: ScenarioStep (используются rc_states, modes)
        :param dt_interval: длительность шага, с
        :return: (opened, closed)
        """
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

        prev_nc, next_nc = self._nc_flags(step, self.ctrl_rc_id)

        # Завершение ДС, если уже активен
        if self.active:
            if curr_free:
                self.dur_free_after_lz += dt_interval
                if self.dur_free_after_lz >= self.T_KON:
                    closed = True
                    self.reset()
            elif curr_occ:
                self.dur_free_after_lz = 0.0
            else:
                # неопределённое состояние – не продвигаем завершение
                self.dur_free_after_lz = 0.0
            return opened, closed

        # ДС ещё не активен: фазы 01/02 и КОГДА
        if self.phase == "idle":
            # Ветка 12.1: предыдущая не контролируется
            # Фаза 01: prev NC, curr занята, next свободна
            cond_p1_12_1 = prev_nc and curr_occ and next_free

            # Ветка 12.2: следующая не контролируется
            # Фаза 01: prev свободна, curr занята, next NC
            cond_p1_12_2 = prev_free and curr_occ and next_nc

            if cond_p1_12_1:
                self.dur_p1 += dt_interval
                self.dur_p2 = 0.0
                self.dur_lz = 0.0
                if self.dur_p1 >= self.T_S0112:
                    self.phase = "p1_12_1"
            elif cond_p1_12_2:
                self.dur_p1 += dt_interval
                self.dur_p2 = 0.0
                self.dur_lz = 0.0
                if self.dur_p1 >= self.T_S0112:
                    self.phase = "p1_12_2"
            else:
                self.dur_p1 = 0.0
                self.dur_p2 = 0.0
                self.dur_lz = 0.0

        elif self.phase == "p1_12_1":
            # Фаза 02 для 12.1: prev NC, curr занята, next занята
            cond_p2_12_1 = prev_nc and curr_occ and next_occ
            if cond_p2_12_1:
                self.dur_p2 += dt_interval
                if self.dur_p2 >= self.T_S0212:
                    self.phase = "p2_12_1"
            else:
                self.dur_p2 = 0.0

        elif self.phase == "p1_12_2":
            # Фаза 02 для 12.2: prev занята, curr занята, next NC
            cond_p2_12_2 = prev_occ and curr_occ and next_nc
            if cond_p2_12_2:
                self.dur_p2 += dt_interval
                if self.dur_p2 >= self.T_S0212:
                    self.phase = "p2_12_2"
            else:
                self.dur_p2 = 0.0

        elif self.phase == "p2_12_1":
            # КОГДА 12.1: prev NC, curr занята, next свободна
            cond_lz_12_1 = prev_nc and curr_occ and next_free
            if cond_lz_12_1:
                self.dur_lz += dt_interval
                if self.dur_lz >= self.T_LZ12:
                    opened = True
                    self.active = True
                    self.dur_free_after_lz = 0.0
            else:
                self.dur_lz = 0.0

        elif self.phase == "p2_12_2":
            # КОГДА 12.2: prev свободна, curr занята, next NC
            cond_lz_12_2 = prev_free and curr_occ and next_nc
            if cond_lz_12_2:
                self.dur_lz += dt_interval
                if self.dur_lz >= self.T_LZ12:
                    opened = True
                    self.active = True
                    self.dur_free_after_lz = 0.0
            else:
                self.dur_lz = 0.0

        return opened, closed

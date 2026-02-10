# engine/occupancy/variant13_1p.py

from typing import Any, Tuple

from ..station_visochino_1p import (
    rc_is_free,
    rc_is_occupied,
    rc_is_locked, 
    signal_is_closed,
    signal_is_shunting,
)


class Variant13Detector:
    """
    Вариант 13 ЛЗ.

    Работает по:
      - ctrl_rc: контролируемая РЦ (10-12SP или 1-7SP),
      - adj_rc: смежная РЦ (для нашей конфигурации всегда 1P),
      - одному светофору между ними (НМ1 или Ч1).

    ВАЖНО: смежная РЦ должна быть ЗАМКНУТА (З=1).

    Параметры:
      T_S0113 — длительность фазы 01;
      T_S0213 — длительность фазы 02;
      T_LZ13  — длительность фазы КОГДА;
      T_KON   — время на завершение ситуации (освобождение ctrl_rc).

    Ветка 13.1 (предыдущая замкнута):
      Фаза 01:
        adj свободна и замкнута (П=0, З=1),
        ctrl свободна (П=0),
        светофор закрыт (С=0 или МС=0) >= T_S0113.

      Фаза 02:
        adj занята и замкнута (П=1, З=1),
        ctrl свободна (П=0),
        светофор закрыт >= T_S0213.

      КОГДА:
        adj занята и замкнута (П=1, З=1),
        ctrl занята (П=1),
        светофор закрыт >= T_LZ13.

    Завершение ДС:
      сформирован ДС и ctrl занята;
      когда ctrl свободна (П=0) подряд >= T_KON — завершить ДС.
    """

    def __init__(
        self,
        ctrl_rc_id: str,
        adj_rc_id: str,
        signal_id: str,
        t_s0113: float,
        t_s0213: float,
        t_lz13: float,
        t_kon: float,
    ) -> None:
        self.ctrl_rc_id = ctrl_rc_id
        self.adj_rc_id = adj_rc_id
        self.signal_id = signal_id

        self.T_S0113 = float(t_s0113)
        self.T_S0213 = float(t_s0213)
        self.T_LZ13 = float(t_lz13)
        self.T_KON = float(t_kon)

        # Фазы: idle -> p1_done -> p2_done -> active
        self.phase: str = "idle"

        self.dur_p1: float = 0.0
        self.dur_p2: float = 0.0
        self.dur_lz: float = 0.0
        self.dur_free_after_lz: float = 0.0

        self.active: bool = False

    def reset(self) -> None:
        self.phase = "idle"
        self.dur_p1 = 0.0
        self.dur_p2 = 0.0
        self.dur_lz = 0.0
        self.dur_free_after_lz = 0.0
        self.active = False

    def _states(self, step: Any) -> Tuple[bool, bool, bool, bool, bool]:
        # ctrl_free, ctrl_occ, adj_free, adj_occ, adj_locked
        st_ctrl = step.rc_states.get(self.ctrl_rc_id, 0)
        st_adj = step.rc_states.get(self.adj_rc_id, 0)

        ctrl_free = rc_is_free(st_ctrl)
        ctrl_occ = rc_is_occupied(st_ctrl)
        adj_free = rc_is_free(st_adj)
        adj_occ = rc_is_occupied(st_adj)
        
        # Замыкание кодируется битом 1 в состоянии РЦ
        adj_locked = rc_is_locked(st_adj)

        return ctrl_free, ctrl_occ, adj_free, adj_occ, adj_locked

    def _signal_closed(self, step: Any) -> bool:
        sig_map = getattr(step, "signal_states", {}) or {}
        st = sig_map.get(self.signal_id, 0)
        return signal_is_closed(st) or signal_is_shunting(st)

    def update(self, step: Any, dt_interval: float) -> Tuple[bool, bool]:
        if dt_interval <= 0.0:
            return False, False

        opened = False
        closed = False

        ctrl_free, ctrl_occ, adj_free, adj_occ, adj_locked = self._states(step)
        sig_closed = self._signal_closed(step)
       

        # --- Завершение ДС ---
        if self.active:
            if ctrl_free:
                self.dur_free_after_lz += dt_interval
                if self.dur_free_after_lz >= self.T_KON:
                    closed = True
                    self.reset()
            elif ctrl_occ:
                self.dur_free_after_lz = 0.0
            else:
                self.dur_free_after_lz = 0.0
            return opened, closed

        # --- Формирование ДС ---

        if self.phase == "idle":
            # Фаза 01: ctrl_free, adj замкнута, сигнал закрыт
            if ctrl_free and adj_locked and sig_closed:
                self.dur_p1 += dt_interval
                self.dur_p2 = 0.0
                self.dur_lz = 0.0
                if self.dur_p1 >= self.T_S0113:
                    self.phase = "p1_done"
            else:
                self.dur_p1 = 0.0
                self.dur_p2 = 0.0
                self.dur_lz = 0.0

        elif self.phase == "p1_done":
            # Фаза 02: ctrl_free, adj_occ И adj_locked, сигнал закрыт
            if ctrl_free and adj_occ and adj_locked and sig_closed:
                self.dur_p2 += dt_interval
                if self.dur_p2 >= self.T_S0213:
                    self.phase = "p2_done"
            else:
                self.dur_p2 = 0.0

        elif self.phase == "p2_done":
            # КОГДА: ctrl_occ, adj_occ И adj_locked, сигнал закрыт
            if ctrl_occ and adj_occ and adj_locked and sig_closed:
                self.dur_lz += dt_interval
                if self.dur_lz >= self.T_LZ13:
                    opened = True
                    self.active = True
                    self.dur_free_after_lz = 0.0
            else:
                self.dur_lz = 0.0

        return opened, closed

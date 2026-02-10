# engine/occupancy/variant10_1p.py

from typing import Any, Tuple

from ..station_visochino_1p import (
    rc_is_free,
    rc_is_occupied,
    signal_is_open,
    signal_is_shunting,
    signal_is_closed,
)


class Variant10Detector:
    """
    Вариант 10 ЛЗ.

    Работает по трём РЦ:
      - prev: предыдущая РЦ (10-12SP или 1-7SP, зависит от смежности),
      - curr: контролируемая РЦ (1P),
      - next: следующая РЦ (1-7SP или 10-12SP),
    и по светофору между curr и next:
      - Ч1 при движении 1P -> 1-7SP,
      - НМ1 при движении 1P -> 10-12SP.

    Параметры:
      TS0110, TS0210, TS0310 — длительности фаз 01/02/03;
      TLZ10                  — длительность фазы LZ (КОГДА);
      TKON                   — время на завершение ситуации (освобождение curr).
    """

    def __init__(
        self,
        ts0110: float,
        ts0210: float,
        ts0310: float,
        tlz10: float,
        tkon: float,
    ) -> None:
        self.TS0110 = float(ts0110)
        self.TS0210 = float(ts0210)
        self.TS0310 = float(ts0310)
        self.TLZ10 = float(tlz10)
        self.TKON = float(tkon)

        # Фаза ДАНО (общая для веток 10.1 и 10.2)
        # state: "idle" -> "p1done" -> "p2_free_prev"/"p2_occ_prev" -> "ready"
        self.phase: str = "idle"
        self.dur_p1: float = 0.0
        self.dur_p2: float = 0.0
        self.dur_p3: float = 0.0

        # Фаза КОГДА (prev_free, curr_occ, next_free, светофор закрыт)
        self.dur_lz: float = 0.0

        # Завершение ДС (curr становится свободной на TKON)
        self.dur_free_after_lz: float = 0.0

        # Признак активного ДС "Логическая ложная занятость"
        self.active: bool = False

        # Зафиксированное направление ("to_next" или "to_prev")
        self.direction: str | None = None

    def reset(self) -> None:
        """Полный сброс детектора."""
        self.phase = "idle"
        self.dur_p1 = 0.0
        self.dur_p2 = 0.0
        self.dur_p3 = 0.0
        self.dur_lz = 0.0
        self.dur_free_after_lz = 0.0
        self.active = False
        self.direction = None

    @staticmethod
    def _states(step: Any) -> Tuple[bool, bool, bool, bool, bool, bool]:
        """
        prev_free, prev_occ, curr_free, curr_occ, next_free, next_occ
        по rc_states шага.
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

    def update(self, step: Any, dt_interval: float) -> Tuple[bool, bool]:
        """
        Обновление детектора по шагу сценария.
        """
        if dt_interval <= 0.0:
            dt_interval = 0.0

        opened = False
        closed = False

        prev_free, prev_occ, curr_free, curr_occ, next_free, next_occ = self._states(step)
        sig_state_map = getattr(step, "signal_states", None) or {}

        # --- выбор/фиксация направления ---
        # Направление фиксируем, когда видна ветка 10.1 или 10.2
        if self.direction is None:
            if prev_free and curr_occ and next_occ:
                # ветка 10.1 (1P -> 1-7SP)
                self.direction = "to_next"
            elif prev_occ and curr_occ and next_free:
                # ветка 10.2 (1P -> 10-12SP)
                self.direction = "to_prev"

        # --- выбор сигнала по направлению ---
        if self.direction == "to_next":
            sig_id = "Ч1"
        elif self.direction == "to_prev":
            sig_id = "НМ1"
        else:
            # самая первая фаза: prev_free, curr_occ, next_free,
            # направления ещё не видно — пробуем любой открытый Ч1/НМ1
            if "Ч1" in sig_state_map and (signal_is_open(sig_state_map["Ч1"]) or signal_is_shunting(sig_state_map["Ч1"])):
                sig_id = "Ч1"
                # можно сразу считать, что направление вперёд
                self.direction = "to_next"
            elif "НМ1" in sig_state_map and (signal_is_open(sig_state_map["НМ1"]) or signal_is_shunting(sig_state_map["НМ1"])):
                sig_id = "НМ1"
                # и здесь — назад
                self.direction = "to_prev"
            else:
                sig_id = None

        sig_state = sig_state_map.get(sig_id, 0) if sig_id else 0
        sig_open = signal_is_open(sig_state) or signal_is_shunting(sig_state)
        sig_closed = signal_is_closed(sig_state)

        # --- если уже активен ДС: ждём освобождения curr ---
        if self.active:
            if curr_free:
                self.dur_free_after_lz += dt_interval
                if self.dur_free_after_lz >= self.TKON:
                    closed = True
                    self.reset()
            elif curr_occ:
                self.dur_free_after_lz = 0.0
            return opened, closed

        # --- Если ДС не активен: фазы ДАНО и КОГДА ---

        # Фаза 01
        if self.phase == "idle":
            if prev_free and curr_occ and next_free and sig_open:
                self.dur_p1 += dt_interval
                if self.dur_p1 >= self.TS0110:
                    self.phase = "p1done"
            else:
                self.dur_p1 = 0.0
                self.dur_p2 = 0.0
                self.dur_p3 = 0.0

        elif self.phase == "p1done":
            # Фаза 02: ветка 10.1 или 10.2
            if prev_free and curr_occ and next_occ and sig_open:
                # 10.1
                self.dur_p2 += dt_interval
                if self.dur_p2 >= self.TS0210:
                    self.phase = "p2_free_prev"
            elif prev_occ and curr_occ and next_free and sig_open:
                # 10.2
                self.dur_p2 += dt_interval
                if self.dur_p2 >= self.TS0210:
                    self.phase = "p2_occ_prev"
            else:
                self.dur_p2 = 0.0

        elif self.phase == "p2_free_prev":
            # Фаза 03 для 10.1
            if prev_free and curr_occ and next_occ and sig_closed:
                self.dur_p3 += dt_interval
                if self.dur_p3 >= self.TS0310:
                    self.phase = "ready"
                    self.dur_lz = 0.0
            else:
                self.dur_p3 = 0.0

        elif self.phase == "p2_occ_prev":
            # Фаза 03 для 10.2
            if prev_occ and curr_occ and next_free and sig_closed:
                self.dur_p3 += dt_interval
                if self.dur_p3 >= self.TS0310:
                    self.phase = "ready"
                    self.dur_lz = 0.0
            else:
                self.dur_p3 = 0.0

        # Фаза КОГДА
        if self.phase == "ready":
            if prev_free and curr_occ and next_free and sig_closed:
                self.dur_lz += dt_interval
                if self.dur_lz >= self.TLZ10:
                    opened = True
                    self.active = True
                    self.dur_free_after_lz = 0.0
            else:
                self.dur_lz = 0.0

        return opened, closed

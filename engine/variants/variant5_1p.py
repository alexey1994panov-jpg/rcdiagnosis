# engine/occupancy/variant5_1p.py

from typing import Any

from ..station_visochino_1p import rc_is_free, rc_is_occupied


class Variant5Detector:
    """
    ЛЗ v5: ложная занятость на РЦ с замыканием.

    ДАНО:
      Контролируемая РЦ свободна (П=0), не замкнута в маршруте (З=0)
      непрерывно ≥ Ts05.

    КОГДА:
      Контролируемая РЦ занята (П=1), не замкнута в маршруте (З=0)
      непрерывно ≥ Tlz05.

    Завершение:
      Пока РЦ занята (П=1) — ДС активна.
      Когда РЦ свободна (П=0) непрерывно ≥ Tkon — ДС завершается.
    """

    def __init__(
        self,
        rc_id: str,
        ts05: float,
        tlz05: float,
        tkon: float,
        allow_route_lock_states: bool,
    ) -> None:
        self.rc_id = rc_id
        self.TS05 = float(ts05)
        self.TLZ05 = float(tlz05)
        self.TKON = float(tkon)
        # если True — допускаем состояния с замыканием (4,5,7,8)
        self.allow_route_lock_states = bool(allow_route_lock_states)

        # Фазы: "idle" -> "given_done" -> "active"
        self.phase: str = "idle"

        # Таймеры
        self.dur_free: float = 0.0          # длительность свободности (ДАНО)
        self.dur_occ: float = 0.0           # длительность занятости (КОГДА)
        self.dur_free_after_lz: float = 0.0 # свободность после ЛЗ (для завершения)

        # Флаг активной ЛЗ
        self.active: bool = False

    def reset(self) -> None:
        self.phase = "idle"
        self.dur_free = 0.0
        self.dur_occ = 0.0
        self.dur_free_after_lz = 0.0
        self.active = False

    def _is_free_no_lock(self, step: Any) -> bool:
        """
        Свободна без замыкания (3), опционально с замыканием (4,5),
        если allow_route_lock_states=True.
        """
        st = step.rc_states.get(self.rc_id, 0)
        if self.allow_route_lock_states:
            # свободна: 3,4,5 (3 — без замыкания, 4–5 — с замыканием)
            return st in (3, 4, 5)
        # строго без замыкания
        return st == 3

    def _is_occupied_no_lock(self, step: Any) -> bool:
        """
        Занята без замыкания (6), опционально с замыканием (7,8),
        если allow_route_lock_states=True.
        """
        st = step.rc_states.get(self.rc_id, 0)
        if self.allow_route_lock_states:
            # занята: 6,7,8 (6 — без замыкания, 7–8 — с замыканием)
            return st in (6, 7, 8)
        # строго без замыкания
        return st == 6

    def update(self, step: Any, dtinterval: float) -> tuple[bool, bool]:
        """
        Обновление детектора на очередном шаге сценария.

        :param step: ScenarioStep (или совместимый объект) с полем rc_states.
        :param dtinterval: длительность шага в секундах.
        :return: (opened, closed)
                 opened == True -> на этом шаге сформирована ЛЗ v5.
                 closed == True -> на этом шаге завершена ЛЗ v5.
        """
        if dtinterval <= 0.0:
            dtinterval = 0.0

        opened = False
        closed = False

        curr_free = self._is_free_no_lock(step)
        curr_occ = self._is_occupied_no_lock(step)

        # Если ЛЗ ещё не активна – отрабатываем ДАНО/КОГДА
        if not self.active:
            if self.phase == "idle":
                # ДАНО: РЦ свободна (П=0, З=0) ≥ TS05
                if curr_free:
                    self.dur_free += dtinterval
                    self.dur_occ = 0.0
                    if self.dur_free >= self.TS05:
                        self.phase = "given_done"
                else:
                    # Любое несвободное состояние до выполнения ДАНО – сброс
                    self.dur_free = 0.0
                    self.dur_occ = 0.0

            elif self.phase == "given_done":
                # КОГДА: РЦ занята (П=1, З=0) ≥ TLZ05
                if curr_occ:
                    self.dur_occ += dtinterval
                    if self.dur_occ >= self.TLZ05:
                        opened = True
                        self.active = True
                        self.phase = "active"
                        self.dur_free_after_lz = 0.0
                elif curr_free:
                    # Вернулись к свободности до TLZ05 – считаем, что ДАНО не выполнено
                    self.reset()
                else:
                    # Состояние ни свободно, ни занято (нет контроля и т.п.) – сброс
                    self.reset()

        # Если ЛЗ уже активна – ждём свободности для завершения
        if self.active and self.phase == "active":
            if curr_free:
                self.dur_free_after_lz += dtinterval
                if self.dur_free_after_lz >= self.TKON:
                    closed = True
                    self.reset()
            elif curr_occ:
                # Пока занята – сбрасываем таймер завершения
                self.dur_free_after_lz = 0.0
            else:
                # Нет контроля/неопределённое состояние – не продвигаем завершение,
                # но ЛЗ остаётся активной
                self.dur_free_after_lz = 0.0

        return opened, closed

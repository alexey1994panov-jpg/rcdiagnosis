# engine/occupancy/variant6_1p.py

from typing import Any

from ..station_visochino_1p import rc_is_free, rc_is_occupied


class Variant6Detector:
    """
    ЛЗ v6: длительная занятость одной РЦ без замыкания.

    Применяется для любой РЦ без замыкания (решение об этом принимается снаружи,
    в init_detectors), без учёта смежных и сигналов.

    Логика:

    ДАНО:
        Контролируемая РЦ свободна (П=0; UniStateID ∈ {3,4,5}) непрерывно ≥ Ts06.

    КОГДА:
        Контролируемая РЦ занята (П=1; UniStateID ∈ {6,7,8}) непрерывно ≥ Tlz06
        и не сработало ни одно исключение формирования ЛЗ, и не активен тестовый режим.

    ТОГДА:
        Формируется ДС "Логическая ложная занятость" (opened=True, active=True).

    Завершение ДС:
        Пока контролируемая РЦ занята (П=1) – ДС активна.
        Когда РЦ свободна (П=0) непрерывно ≥ Tkon – ДС завершается (closed=True),
        детектор сбрасывается в исходное состояние.
    """

    def __init__(self, rc_id: str, ts06: float, tlz06: float, tkon: float) -> None:
        self.rc_id = rc_id
        self.TS06 = float(ts06)
        self.TLZ06 = float(tlz06)
        self.TKON = float(tkon)

        # Фазы: "idle" -> "given_done" -> "active"
        self.phase: str = "idle"

        # Таймеры
        self.dur_free: float = 0.0            # длительность свободности (ДАНО)
        self.dur_occ: float = 0.0             # длительность занятости (КОГДА)
        self.dur_free_after_lz: float = 0.0   # свободность после ЛЗ (для завершения)

        # Флаг активной ЛЗ
        self.active: bool = False

    def reset(self) -> None:
        self.phase = "idle"
        self.dur_free = 0.0
        self.dur_occ = 0.0
        self.dur_free_after_lz = 0.0
        self.active = False

    def _is_free(self, step: Any) -> bool:
        st = step.rc_states.get(self.rc_id, 0)
        return rc_is_free(st)

    def _is_occupied(self, step: Any) -> bool:
        st = step.rc_states.get(self.rc_id, 0)
        return rc_is_occupied(st)

    def update(self, step: Any, dtinterval: float) -> tuple[bool, bool]:
        """
        Обновление детектора на очередном шаге сценария.

        :param step: ScenarioStep (или совместимый объект) с полем rcstates.
        :param dtinterval: длительность шага в секундах.
        :return: (opened, closed)
            opened == True  -> на этом шаге сформирована ЛЗ v6.
            closed == True  -> на этом шаге завершена ЛЗ v6.
        """
        if dtinterval <= 0.0:
            dtinterval = 0.0

        opened = False
        closed = False

        curr_free = self._is_free(step)
        curr_occ = self._is_occupied(step)

        # Если ЛЗ ещё не активна – отрабатываем ДАНО/КОГДА
        if not self.active:
            if self.phase == "idle":
                # ДАНО: РЦ свободна ≥ TS06
                if curr_free:
                    self.dur_free += dtinterval
                    self.dur_occ = 0.0
                    if self.dur_free >= self.TS06:
                        self.phase = "given_done"
                else:
                    # Любое несвободное состояние до выполнения ДАНО – сброс
                    self.dur_free = 0.0
                    self.dur_occ = 0.0

            elif self.phase == "given_done":
                # КОГДА: РЦ занята ≥ TLZ06
                if curr_occ:
                    self.dur_occ += dtinterval
                    if self.dur_occ >= self.TLZ06:
                        opened = True
                        self.active = True
                        self.phase = "active"
                        self.dur_free_after_lz = 0.0
                elif curr_free:
                    # Вернулись к свободности до TLZ06 – считаем, что ДАНО не выполнено
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

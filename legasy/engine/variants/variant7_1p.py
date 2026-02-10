# engine/occupancy/variant7_1p.py

from typing import Any

from ..station_visochino_1p import rc_is_free, rc_is_occupied


class Variant7Detector:
    """
    ЛЗ v7: ложная занятость на бесстрелочной контролируемой РЦ
    с учётом наличия/отсутствия смежных РЦ по положению стрелок.

    Объединяет требования:
      - «нет смежных РЦ» (старый v6, нет предыдущей и нет следующей);
      - v7.1: нет предыдущей по положению стрелки;
      - v7.2: нет следующей по положению стрелки.

    Временная логика одинакова для всех ситуаций:

    ДАНО:
      Условия свободности по контролируемой и смежным РЦ
      выполняются непрерывно ≥ TS07.

    КОГДА:
      Условия занятости по контролируемой и смежным РЦ
      выполняются непрерывно ≥ TLZ07.

    ТОГДА:
      Формируется ДС "Логическая ложная занятость" (opened=True, active=True).

    Завершение ДС:
      Пока контролируемая РЦ занята – ДС активна.
      Когда контролируемая РЦ свободна непрерывно ≥ TKON –
      ДС завершается (closed=True), детектор сбрасывается.
    """

    def __init__(
        self,
        ctrl_rc_id: str,
        prev_rc_id: str | None,
        next_rc_id: str | None,
        ts07: float,
        tlz07: float,
        tkon_v7: float,
        mode: str = "no_adjacent",
    ) -> None:
        self.ctrl_rc_id = ctrl_rc_id
        self.prev_rc_id = prev_rc_id
        self.next_rc_id = next_rc_id

        self.TS07 = float(ts07)
        self.TLZ07 = float(tlz07)
        self.TKON = float(tkon_v7)

        # Фазы: "idle" -> "given_done" -> "active"
        self.phase: str = "idle"

        # Таймеры
        self.dur_free: float = 0.0           # длительность ДАНО
        self.dur_occ: float = 0.0            # длительность КОГДА
        self.dur_free_after_lz: float = 0.0  # свободность после ЛЗ (для завершения)

        # Флаг активной ЛЗ
        self.active: bool = False
        self.mode = mode

    # --- Вспомогательные методы получения состояний ---

    def _is_rc_free(self, step: Any, rc_id: str | None) -> bool:
        if not rc_id:
            return False
        st = step.rc_states.get(rc_id, 0)
        return rc_is_free(st)

    def _is_rc_occ(self, step: Any, rc_id: str | None) -> bool:
        if not rc_id:
            return False
        st = step.rc_states.get(rc_id, 0)
        return rc_is_occupied(st)

    def _get_adjacent_flags(self, step: Any) -> tuple[bool, bool]:
        """
        Возвращает (prev_control_ok, next_control_ok) из step.modes.

        Эти флаги выставляются в simulate_1p.update_adjacency()
        на основе положений стрелок Sw10 (предыдущая) и Sw1/Sw5 (следующая).
        """
        modes = getattr(step, "modes", None) or {}
        prev_ok = bool(modes.get("prev_control_ok", True))
        next_ok = bool(modes.get("next_control_ok", True))
        return prev_ok, next_ok

    # --- Условия ДАНО/КОГДА согласно объединённым требованиям v6/v7 ---

    def _given_condition(self, step: Any) -> bool:
        """
        ДАНО:

        1) Нет смежных РЦ:
           ctrl_free, !prev_control_ok, !next_control_ok.

        2) Нет предыдущей по положению стрелки (v7.1):
           !prev_control_ok, next_control_ok,
           ctrl_free, next_free.

        3) Нет следующей по положению стрелки (v7.2):
           prev_control_ok, !next_control_ok,
           prev_free, ctrl_free.
        """
        ctrl_free = self._is_rc_free(step, self.ctrl_rc_id)
        if not ctrl_free:
            return False

        prev_ok, next_ok = self._get_adjacent_flags(step)
        prev_free = self._is_rc_free(step, self.prev_rc_id) if self.prev_rc_id else False
        next_free = self._is_rc_free(step, self.next_rc_id) if self.next_rc_id else False

        # 1) Нет смежных РЦ
        if not prev_ok and not next_ok:
            return True

        # 2) Нет предыдущей по положению стрелки (v7.1)
        if (not prev_ok) and next_ok and next_free:
            return True

        # 3) Нет следующей по положению стрелки (v7.2)
        if prev_ok and (not next_ok) and prev_free:
            return True

        return False

    def _when_condition(self, step: Any) -> bool:
        """
        КОГДА:

        1) Нет смежных РЦ:
           ctrl_occ, !prev_control_ok, !next_control_ok.

        2) Нет предыдущей по положению стрелки (v7.1):
           !prev_control_ok, next_control_ok,
           ctrl_occ, next_free.

        3) Нет следующей по положению стрелки (v7.2):
           prev_control_ok, !next_control_ok,
           prev_free, ctrl_occ.
        """
        ctrl_occ = self._is_rc_occ(step, self.ctrl_rc_id)
        if not ctrl_occ:
            return False

        prev_ok, next_ok = self._get_adjacent_flags(step)
        prev_free = self._is_rc_free(step, self.prev_rc_id) if self.prev_rc_id else False
        next_free = self._is_rc_free(step, self.next_rc_id) if self.next_rc_id else False

        # 1) Нет смежных РЦ
        if not prev_ok and not next_ok:
            return True

        # 2) Нет предыдущей по положению стрелки (v7.1)
        if (not prev_ok) and next_ok and next_free:
            return True

        # 3) Нет следующей по положению стрелки (v7.2)
        if prev_ok and (not next_ok) and prev_free:
            return True

        return False

    # --- Управление состоянием детектора ---

    def reset(self) -> None:
        self.phase = "idle"
        self.dur_free = 0.0
        self.dur_occ = 0.0
        self.dur_free_after_lz = 0.0
        self.active = False

    def update(self, step: Any, dtinterval: float) -> tuple[bool, bool]:
        """
        Обновление детектора на очередном шаге сценария.

        :param step: ScenarioStep (или совместимый объект).
        :param dtinterval: длительность шага в секундах.
        :return: (opened, closed)
                 opened == True -> на этом шаге сформирована ЛЗ v7.
                 closed == True -> на этом шаге завершена ЛЗ v7.
        """
        if dtinterval <= 0.0:
            dtinterval = 0.0

        opened = False
        closed = False

        # Если ЛЗ ещё не активна – отрабатываем ДАНО/КОГДА
        if not self.active:
            if self.phase == "idle":
                # ДАНО: условия _given_condition() выполняются ≥ TS07
                if self._given_condition(step):
                    self.dur_free += dtinterval
                    self.dur_occ = 0.0
                    if self.dur_free >= self.TS07:
                        self.phase = "given_done"
                else:
                    # Любое нарушение ДАНО – сброс таймеров
                    self.dur_free = 0.0
                    self.dur_occ = 0.0

            elif self.phase == "given_done":
                # КОГДА: условия _when_condition() выполняются ≥ TLZ07
                if self._when_condition(step):
                    self.dur_occ += dtinterval
                    if self.dur_occ >= self.TLZ07:
                        opened = True
                        self.active = True
                        self.phase = "active"
                        self.dur_free_after_lz = 0.0
                else:
                    # Условия КОГДА нарушены — возвращаемся в исходное состояние
                    self.reset()

        # Если ЛЗ уже активна – ждём свободности контролируемой РЦ для завершения
        if self.active and self.phase == "active":
            ctrl_free = self._is_rc_free(step, self.ctrl_rc_id)
            ctrl_occ = self._is_rc_occ(step, self.ctrl_rc_id)

            if ctrl_free:
                self.dur_free_after_lz += dtinterval
                if self.dur_free_after_lz >= self.TKON:
                    closed = True
                    self.reset()
            elif ctrl_occ:
                # Пока занята – сбрасываем таймер завершения
                self.dur_free_after_lz = 0.0
            else:
                # Нет контроля / неопределённое состояние – не продвигаем завершение,
                # но ЛЗ остаётся активной
                self.dur_free_after_lz = 0.0

        return opened, closed

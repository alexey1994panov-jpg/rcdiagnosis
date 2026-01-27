# engine/occupancy/variant9_1p.py

from __future__ import annotations

from typing import Any, Tuple

from ..station_visochino_1p import rc_is_free, rc_is_occupied, rc_is_locked
from ..station_visochino_1p import StationModel1P
from ..adjacency_1p import compute_local_adjacency


class Variant9Detector:
    """
    Вариант 9 ЛЗ: «Пробой изолирующего стыка».

    Работает по контролируемой РЦ ctrl и её смежным РЦ (prev/next).
    Семантика:
    - «занята» = rc_is_occupied(...)
    - «замкнута» для ctrl определяется по коду состояния РЦ (П/З),
      rc_has_route_lock[ctrl_rc_id] — только признак того, что
      на этой РЦ вообще возможно замыкание (вариант 9 допустим).

    Параметры:
      t_s0109  — выдержка исходного состояния (ДАНО);
      t_lz09   — окно между занятием ctrl и любой смежной РЦ (|Δt| ≤ t_lz09);
      t_kon_v9 — время свободности для завершения ДС;
      enable_v9 — флаг включения варианта (учитывается снаружи).

    Особенность для 1П:
    - если ctrl в состоянии З=1 (свободна замкнута) — смежные берём по текущему положению стрелок (ветка 3.1);
    - если ctrl в состоянии З=0 (свободна не замкнута) — смежные берём по топологии, независимо от положения стрелок (ветка 3.2).
    """

    def __init__(
        self,
        station: StationModel1P,
        ctrl_rc_id: str,
        adjacent_rc_ids: list[str],
        t_s0109: float,
        t_lz09: float,
        t_kon_v9: float,
    ) -> None:
        self.station = station
        self.ctrl_rc_id = ctrl_rc_id

        # adjacent_rc_ids трактуем как топологические смежные
        # (для ветки 3.2 и для завершения ДС).
        self.adjacent_rc_ids_topology = list(adjacent_rc_ids)

        self.T_S0109 = float(t_s0109)
        self.T_LZ09 = float(t_lz09)
        self.T_KON = float(t_kon_v9)

        self.phase: str = "idle"
        self.dur_s0: float = 0.0
        self.dur_free_after_lz: float = 0.0
        self.active: bool = False

        self._time: float = 0.0
        self.ctrl_last_occ_time: float | None = None
        self.adj_last_occ_time: float | None = None

    # -------- служебные методы --------

    def reset(self) -> None:
        self.phase = "idle"
        self.dur_s0 = 0.0
        self.dur_free_after_lz = 0.0
        self.active = False
        self.ctrl_last_occ_time = None
        self.adj_last_occ_time = None

    def _ctrl_states(self, step: Any) -> tuple[bool, bool, bool]:
        """
        Возвращает (ctrl_free, ctrl_occ, ctrl_locked_now).

        ctrl_locked_now — текущий признак З=1 по состоянию РЦ.
        """
        st = step.rc_states.get(self.ctrl_rc_id, 0)

        ctrl_free = rc_is_free(st)
        ctrl_occ = rc_is_occupied(st)
        ctrl_locked_now = rc_is_locked(st)

        return ctrl_free, ctrl_occ, ctrl_locked_now
    def _adj_ids_locked(self, step: Any) -> list[str]:
        """
        Смежные для случая замкнутой ctrl (ветка 3.1):
        зависят от положения стрелок. Если по стрелкам смежность
        не определяется (стрелки не ведут на ctrl / нет контроля),
        возвращаем пустой список.
        """
        adj = compute_local_adjacency(self.station, step, self.ctrl_rc_id)

        ids: list[str] = []
        if adj.prev_rc_id is not None and not adj.prev_nc:
            ids.append(adj.prev_rc_id)
        if adj.next_rc_id is not None and not adj.next_nc:
            ids.append(adj.next_rc_id)
        return ids

    def _adj_states(self, step: Any, ctrl_locked_now: bool) -> tuple[bool, bool, bool]:
        """
        Сводные состояния по смежным РЦ:
        returns (all_adj_free, any_adj_free, any_adj_occ).

        ctrl_locked_now = True  -> смежные по текущему положению стрелок (ветка 3.1);
        ctrl_locked_now = False -> смежные по топологии (ветка 3.2 и завершение).
        Замыкание на смежных не учитывается.
        """
        if ctrl_locked_now:
            adj_ids = self._adj_ids_locked(step)
        else:
            adj_ids = self.adjacent_rc_ids_topology

        if not adj_ids:
            # нет определяемых смежных — вариант 9 по смыслу не работает
            return True, False, False

        any_free = False
        all_free = True
        any_occ = False

        for rc_id in adj_ids:
            st = step.rc_states.get(rc_id, 0)
            is_free = rc_is_free(st)
            is_occ = rc_is_occupied(st)

            if is_free:
                any_free = True
            else:
                all_free = False

            if is_occ:
                any_occ = True

        return all_free, any_free, any_occ

    def _update_internal_time(self, dt_interval: float) -> None:
        if dt_interval < 0.0:
            dt = 0.0
        else:
            dt = dt_interval
        self._time += dt

    # -------- основной метод --------

    def update(self, step: Any, dt_interval: float) -> Tuple[bool, bool]:
        if dt_interval <= 0.0:
            dt_interval = 0.0

        self._update_internal_time(dt_interval)

        opened = False
        closed = False

        ctrl_free, ctrl_occ, ctrl_locked_now = self._ctrl_states(step)
        adj_all_free, adj_any_free, adj_any_occ = self._adj_states(step, ctrl_locked_now)

        # --- Завершение ДС, если уже активен ---
        if self.active and self.phase == "active":
            # Завершение: ctrl свободна и все смежные свободны подряд ≥ T_KON.
            # Смежные берём по той же модели, что и для ДАНО 3.2 (топология),
            # но ctrl_locked_now уже учтён при вызове _adj_states.
            if ctrl_free and adj_all_free:
                self.dur_free_after_lz += dt_interval
                if self.dur_free_after_lz >= self.T_KON:
                    closed = True
                    self.reset()
            else:
                self.dur_free_after_lz = 0.0

            return opened, closed

        # --- Формирование ДС (ДАНО + КОГДА) ---
        if not self.active:
            # 1. Фаза ДАНО
            if self.phase == "idle":
                # Ветка 3.1: ctrl свободна и З=1 (свободна замкнута), хотя бы одна смежная свободна.
                # Смежные определены по положению стрелок; если их список пуст,
                # считаем, что смежность не определена и ДАНО не выполняется.
                cond_31 = ctrl_free and ctrl_locked_now and adj_any_free

                # Ветка 3.2: ctrl свободна и З=0 (свободна не замкнута), все смежные свободны
                # (смежные по топологии, независимо от положения стрелок).
                cond_32 = ctrl_free and (not ctrl_locked_now) and adj_all_free

                if cond_31 or cond_32:
                    self.dur_s0 += dt_interval
                    if self.dur_s0 >= self.T_S0109:
                        self.phase = "ready"
                        self.ctrl_last_occ_time = None
                        self.adj_last_occ_time = None
                else:
                    self.dur_s0 = 0.0

            # 2. Фаза КОГДА (только если ДАНО выполнено)
            if self.phase == "ready":
                if ctrl_occ and self.ctrl_last_occ_time is None:
                    self.ctrl_last_occ_time = self._time

                if adj_any_occ and self.adj_last_occ_time is None:
                    self.adj_last_occ_time = self._time

                if (
                    self.ctrl_last_occ_time is not None
                    and self.adj_last_occ_time is not None
                ):
                    dt_between = abs(
                        self.ctrl_last_occ_time - self.adj_last_occ_time
                    )
                    if dt_between <= self.T_LZ09:
                        opened = True
                        self.active = True
                        self.phase = "active"
                        self.dur_free_after_lz = 0.0

        return opened, closed

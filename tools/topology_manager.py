# -*- coding: utf-8 -*-
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass

from station_model import StationModel
from uni_states import sw_no_control  # общий критерий "стрелка без контроля"


@dataclass
class TopologyState:
    """
    Память топологии для конкретной РЦ.
    Удерживает соседа при временной потере контроля стрелок (T_PK).
    """
    rc_id: str
    latched_prev: str = ""
    latched_next: str = ""
    time_since_prev_lost: Optional[float] = None
    time_since_next_lost: Optional[float] = None


class UniversalTopologyManager:
    """
    Универсальный менеджер топологии.

    Работает поверх StationModel.rc_nodes, где связи заданы как
      (neighbor_rc_id, switch_id, required_state):

    - связи без стрелки (switch_id is None или required_state < 0) считаются
      безусловными: сосед всегда доступен (линейная топология);

    - стрелочно-зависимые связи (switch_id задан) активируются только при
      наличии контроля стрелки и требуемого положения (plus/minus);

    - при потере контроля стрелки используем механизм удержания (latch) до T_PK:
      если физический сосед временно не определяется, остаётся latched_*,
      пока не истечёт T_PK; после T_PK сосед считается недоступным.

    Логика того, какие связи должны быть стрелочно-зависимыми (в том числе для
    бесстрелочных контролируемых секций через NextMi/NextPl соседей),
    задаётся на уровне apply_switch_topology_rules.
    """

    def __init__(self, model: StationModel, t_pk: float = 30.0):
        self.model = model
        self.T_PK = t_pk
        self.states: Dict[str, TopologyState] = {
            rc_id: TopologyState(rc_id) for rc_id in model.rc_nodes.keys()
        }

    # --- Новый уровень: соседи + контроль ---

    def get_neighbors_with_control(
        self,
        rc_id: str,
        switch_states: Dict[str, int],
        dt: float,
    ) -> Tuple[str, str, bool, bool, bool, bool]:
        """
        Возвращает (prev_rc_id, next_rc_id, prev_control_ok, next_control_ok, prev_nc, next_nc)
        для указанной РЦ.

        prev_nc/next_nc: True, если в данном направлении нет связей (тупик/граница модели).
        """
        prev_rc, next_rc = self.get_active_neighbors(rc_id, switch_states, dt)
        
        node = self.model.rc_nodes.get(rc_id)
        prev_nc = len(node.prev_links) == 0 if node else False
        next_nc = len(node.next_links) == 0 if node else False

        prev_ok = bool(prev_rc)
        next_ok = bool(next_rc)

        return prev_rc, next_rc, prev_ok, next_ok, prev_nc, next_nc

    # --- Старый интерфейс: оставляем как есть для совместимости ---

    def get_active_neighbors(
        self,
        rc_id: str,
        switch_states: Dict[str, int],
        dt: float,
    ) -> Tuple[str, str]:
        """
        Возвращает (prev_rc_id, next_rc_id) для указанной РЦ.

        switch_states: { 'SwID': Uni_State_ID }.

        Логика:
        1. По RcNode.prev_links/next_links ищем физического соседа:
           - без стрелки → связь безусловна (neighbor_rc_id, None, req<0),
             сосед считается всегда доступным;
           - с стрелкой → смотрим Uni_State_ID:
             * если sw_no_control(...) → контроля нет, физический сосед
               неизвестен на этом шаге;
             * если есть валидный стейт и он соответствует required_state →
               сосед активен.
        2. Если физический сосед неизвестен, используем latched-значение
           не дольше T_PK.
        3. При восстановлении контроля (любой валидный стейт → появляется
           current_phys) latch обновляется, время сбрасывается.

        Какие именно связи зависят от стрелок (включая случай, когда
        бесстрелочная контролируемая секция зависит от стрелок на соседях
        через NextMi/NextPl), уже решено на этапе apply_switch_topology_rules.
        """
        node = self.model.rc_nodes.get(rc_id)
        state = self.states.get(rc_id)

        if not node or not state:
            return "", ""

        current_prev_phys = self._find_phys_neighbor(node.prev_links, switch_states)
        current_next_phys = self._find_phys_neighbor(node.next_links, switch_states)

        # Определяем, есть ли потеря контроля для prev/next
        is_prev_control_lost = self._is_control_lost_for_links(node.prev_links, switch_states)
        is_next_control_lost = self._is_control_lost_for_links(node.next_links, switch_states)

        resolved_prev = self._resolve_with_latch(
            current_phys=current_prev_phys,
            is_control_lost=is_prev_control_lost,
            state_attr="latched_prev",
            time_attr="time_since_prev_lost",
            state=state,
            dt=dt,
        )

        resolved_next = self._resolve_with_latch(
            current_phys=current_next_phys,
            is_control_lost=is_next_control_lost,
            state_attr="latched_next",
            time_attr="time_since_next_lost",
            state=state,
            dt=dt,
        )

        return resolved_prev, resolved_next

    # ---------- Вспомогательные методы ----------

    def _find_phys_neighbor(
        self,
        links: List[Tuple[str, Optional[str], int]],
        switch_states: Dict[str, int],
    ) -> str:
        """
        Поиск физического соседа по списку связей.

        links: [(target_rc_id, switch_id | None, required_state), ...]
        switch_states: { 'SwID': Uni_State_ID }.

        required_state:
        - 1 → стрелка должна быть в плюсе (sw_is_plus);
        - 0 → в минусе (sw_is_minus);
        - required_state < 0 или switch_id is None → безусловная связь,
          не зависящая от контроля стрелки.

        Важный момент:
        - если для одного и того же target_rc_id есть несколько
          стрелочных условий, считаем соседа доступным только если
          ВСЕ эти условия выполнены (логическое AND по стрелкам).
        """
        from uni_states import sw_is_plus, sw_is_minus  # локальный импорт

        # Сначала быстрый путь: безусловные связи (вообще без SwID)
        for target_rc, sw_id, required_state in links:
            if sw_id is not None:
                print(f"DEBUG: Checking link to {target_rc}, sw={sw_id}, req={required_state}, state={switch_states.get(sw_id, 'MISSING')}")
            if sw_id is None:
                return target_rc

        # Группируем стрелочные связи по target_rc
        by_target: Dict[str, List[Tuple[Optional[str], int]]] = {}
        for target_rc, sw_id, required_state in links:
            if sw_id is None or required_state < 0:
                # безусловные уже обработали выше
                continue
            by_target.setdefault(target_rc, []).append((sw_id, required_state))

        # Для каждого кандидата-соседа проверяем все его стрелки
        for target_rc, conds in by_target.items():
            all_ok = True
            for sw_id, required_state in conds:
                uni_state_id = switch_states.get(sw_id)
                # Нет записи или стрелка без контроля → сосед недоступен
                if uni_state_id is None or sw_no_control(uni_state_id):
                    all_ok = False
                    break
                # Проверяем требуемое положение (только если оно задано >= 0)
                if required_state == 1 and not sw_is_plus(uni_state_id):
                    all_ok = False
                    break
                if required_state == 0 and not sw_is_minus(uni_state_id):
                    all_ok = False
                    break
            if all_ok:
                return target_rc

        return ""

    def _is_control_lost_for_links(
        self,
        links: List[Tuple[str, Optional[str], int]],
        switch_states: Dict[str, int],
    ) -> bool:
        """
        Проверяет, есть ли потеря контроля для данного набора связей.
        """
        # Если есть безусловные связи (вообще без SwID) — контроль не теряется
        for target_rc, sw_id, required_state in links:
            if sw_id is None:
                return False
        
        # Проверяем стрелочные связи
        for target_rc, sw_id, required_state in links:
            if sw_id is not None:
                uni_state_id = switch_states.get(sw_id)
                if uni_state_id is not None and sw_no_control(uni_state_id):
                    return True  # Потеря контроля!
        
        # Стрелки под контролем, но связи неактивны (смена положения)
        return False

    def _resolve_with_latch(
        self,
        current_phys: str,
        is_control_lost: bool,  # ← НОВЫЙ ПАРАМЕТР!
        state_attr: str,
        time_attr: str,
        state: TopologyState,
        dt: float,
    ) -> str:
        latched_val = getattr(state, state_attr)
        time_val = getattr(state, time_attr)

        if current_phys:
            # Восстановление — обновляем latch
            setattr(state, state_attr, current_phys)
            setattr(state, time_attr, 0.0)
            return current_phys

        # current_phys == ""
        if is_control_lost and latched_val:
            # Потеря контроля — используем latch
            new_time = (time_val or 0.0) + dt
            setattr(state, time_attr, new_time)
            if new_time <= self.T_PK:
                return latched_val
            # T_PK истёк — сбрасываем
            setattr(state, state_attr, "")
            setattr(state, time_attr, None)
            return ""
        else:
            # Стрелка под контролем, но связь неактивна (смена положения)
            # Сбрасываем latch!
            setattr(state, state_attr, "")
            setattr(state, time_attr, None)
            return ""
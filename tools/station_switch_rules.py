# -*- coding: utf-8 -*-
"""
Правила формирования топологии по стрелкам.

Цель:
- автоматически проставить в RcNode.prev_links/next_links зависимости вида
  (neighbor_rc_id, switch_id, required_state),
используя данные из station_rc_sections.RC_SECTIONS и station_config.NODES.

Новый важный момент (для бесстрелочных контролируемых секций):

1) Для РЦ ctrl, у которой Switches = [] (т.е. сама секция бесстрелочная),
   её линейные соседи по PrevSec/NextSec считаются:

   - безусловными (сосед всегда есть), если НЕТ ни одной стрелки
     на соседних секциях, у которой NextPl/NextMi указывают на ctrl;

   - "стрелочно-зависимыми", если есть соседняя секция S, у которой
     в RC_SECTIONS[S]["Switches"] есть стрелка, для которой
       NextPl == ctrl_name или NextMi == ctrl_name.
     В этом случае линейная связь ctrl <-> S должна зависеть от
     этой стрелки (switch_id, required_state).

2) Конкретное поведение при потере контроля и ТПК реализуется
   в UniversalTopologyManager: там по switch_id и required_state
   решается, считать ли сосед сейчас доступным, в том числе с учётом
   удержания (latch) на время T_PK.

На этом уровне мы не лезем в детекторы и исключения, только топология секций.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Tuple

from station_config import NODES, GROUPS
from station_rc_sections import RC_SECTIONS
from station_switch_logic import SWITCH_LOGIC  


# Требуемое состояние стрелки
SW_PLUS = 1
SW_MINUS = 0


@dataclass
class SwitchDirection:
    """
    Описание направления через стрелку:

    - stem_rc_id: РЦ "ствола" (секция, к которой привязана стрелка – SwSection);
    - branch_rc_id: РЦ "ответвления" (NextMi / NextPl);
    - switch_id: ID стрелки;
    - required_state: 1 (плюс) или 0 (минус).
    """
    stem_rc_id: str
    branch_rc_id: str
    switch_id: str
    required_state: int


def _build_name_to_id() -> Dict[str, str]:
    """
    Строит маппинг NAME -> ID для всех объектов из NODES.
    Нужен, чтобы перевести имена секций ('3СП') и стрелок ('3') в ID.
    """
    name_to_id: Dict[str, str] = {}
    for obj_id, node_data in NODES.items():
        name = node_data.get("name", "")
        if name:
            name_to_id[name] = obj_id
    return name_to_id


def _build_switch_directions_from_rc_sections(
    name_to_id: Dict[str, str],
) -> List[SwitchDirection]:
    """
    Строит направления через стрелки по данным RC_SECTIONS.

    RC_SECTIONS[sec_name]['Switches'] содержит записи:
      { 'name': '3', 'NextMi': '1-7СП', 'NextPl': 'НДП', 'NextSwPl': ...,
        'NextSwMi': ..., 'PrevSw': ... }

    Для каждого SwSection (секции) и её стрелок строим:
      - stem = ID секции (SwSection),
      - branch_minus = ID NextMi (если есть) → required_state = SW_MINUS,
      - branch_plus  = ID NextPl (если есть) → required_state = SW_PLUS.

    Если имя секции или стрелки не удаётся перевести в ID, направление пропускается.
    """
    directions: List[SwitchDirection] = []

    for sec_name, sec_data in RC_SECTIONS.items():
        stem_id = name_to_id.get(sec_name)
        if not stem_id:
            # секция из RC_SECTIONS не найдена в NODES
            continue

        switches = sec_data.get("Switches") or []
        for sw in switches:
            sw_name = sw.get("name")
            if not sw_name:
                continue

            sw_id = name_to_id.get(sw_name)
            if not sw_id:
                # стрелка без ID — пропускаем
                continue

            next_mi = sw.get("NextMi")
            next_pl = sw.get("NextPl")

            # Минусовое направление (МК): stem -> NextMi
            if next_mi:
                branch_id = name_to_id.get(next_mi)
                if branch_id:
                    directions.append(
                        SwitchDirection(
                            stem_rc_id=stem_id,
                            branch_rc_id=branch_id,
                            switch_id=sw_id,
                            required_state=SW_MINUS,
                        )
                    )

            # Плюсовое направление (ПК): stem -> NextPl
            if next_pl:
                branch_id = name_to_id.get(next_pl)
                if branch_id:
                    directions.append(
                        SwitchDirection(
                            stem_rc_id=stem_id,
                            branch_rc_id=branch_id,
                            switch_id=sw_id,
                            required_state=SW_PLUS,
                        )
                    )

    return directions



def _build_ctrl_depend_on_neighbor_switch(
    name_to_id: Dict[str, str],
) -> Dict[str, List[Tuple[str, str, int]]]:
    """
    Строит карту "какие бесстрелочные секции ctrl зависят от стрелок на соседях".

    Форматы:
        result: { ctrl_id: [(neighbor_id, switch_id, required_state), ...], ... }

    Источники данных:
        - RC_SECTIONS: простые случаи (одна стрелка NextMi/NextPl ведёт на ctrl);
        - SWITCH_LOGIC: сложные случаи, где у секции несколько стволов (stem)
          и ctrl входит в её plus_rc (например, 1-7СП со stem=['1','5'] и plus_rc=['1П']).
    """
    result: Dict[str, List[Tuple[str, str, int]]] = {}

    rc_ids_set = set(GROUPS.get("rc_ids", []))

    # --- 1. Базовые зависимости по RC_SECTIONS (одна стрелка -> ctrl) ---
    for ctrl_name, ctrl_data in RC_SECTIONS.items():
        switches = ctrl_data.get("Switches") or []
        # интересуют только бесстрелочные РЦ
        if switches:
            continue

        ctrl_id = name_to_id.get(ctrl_name)
        if not ctrl_id or ctrl_id not in rc_ids_set:
            continue

        prev_name = ctrl_data.get("PrevSec")
        next_name = ctrl_data.get("NextSec")

        neighbors: List[str] = []
        if prev_name:
            neighbors.append(prev_name)
        if next_name:
            neighbors.append(next_name)

        deps: List[Tuple[str, str, int]] = []

        for neigh_name in neighbors:
            neigh_data = RC_SECTIONS.get(neigh_name) or {}
            neigh_id = name_to_id.get(neigh_name)
            if not neigh_id or neigh_id not in rc_ids_set:
                continue

            neigh_switches = neigh_data.get("Switches") or []

            for sw in neigh_switches:
                sw_name = sw.get("name")
                if not sw_name:
                    continue

                sw_id = name_to_id.get(sw_name)
                if not sw_id:
                    continue

                next_mi = sw.get("NextMi")
                next_pl = sw.get("NextPl")

                # Если стрелка на соседней секции ведёт на ctrl по минусу
                if next_mi == ctrl_name:
                    deps.append((neigh_id, sw_id, SW_MINUS))

                # Если стрелка на соседней секции ведёт на ctrl по плюсу
                if next_pl == ctrl_name:
                    deps.append((neigh_id, sw_id, SW_PLUS))

            # --- 3. Стволовые (Stem) зависимости по RC_SECTIONS ---
            # Если между ctrl и neigh есть связь, но она не является ответвлением 
            # ни одной стрелки на neigh — значит это ствол.
            if neigh_switches and not any(d[0] == neigh_id for d in deps):
                # Пробуем найти явную связь по NextMi/NextPl если она есть
                # (для однониточных планов иногда NextSec указывает на стрелку, которая смотрит на нас)
                for sw in neigh_switches:
                    sw_id = name_to_id.get(sw.get("name"))
                    if not sw_id: continue
                    
                    # Если NextMi этой стрелки указывает на нас -> зависим от минуса
                    if sw.get("NextMi") == ctrl_name:
                         deps.append((neigh_id, sw_id, SW_MINUS))
                         break
                    # Если NextPl этой стрелки указывает на нас -> зависим от плюса
                    if sw.get("NextPl") == ctrl_name:
                         deps.append((neigh_id, sw_id, SW_PLUS))
                         break
                
                # Если специфической зависимости не нашли - ищем корневую (общий ствол)
                # Это когда мы со стороны остряка
                if not deps:
                    root_sw_id = None
                    for sw in neigh_switches:
                        if not sw.get("PrevSw"):
                            root_sw_id = name_to_id.get(sw.get("name"))
                            break
                    if not root_sw_id:
                        root_sw_id = name_to_id.get(neigh_switches[0].get("name"))
                    
                    if root_sw_id:
                        # req=-1 означает "любое положение, но должен быть контроль"
                        deps.append((neigh_id, root_sw_id, -1))

        if deps:
            result[ctrl_id] = deps

    # --- 4. Дополнительные зависимости по SWITCH_LOGIC (сложные стволы) ---
    # Здесь мы учитываем случаи, когда у секции несколько стрелок в stem
    # и ctrl входит в её plus_rc. Это как раз 1-7СП -> 1П через стрелки 1 и 5.
    for sec_name, logic in SWITCH_LOGIC.items():
        stem_switch_names = logic.get("stem") or []
        plus_rc_list = logic.get("plus_rc") or []
        if not stem_switch_names or not plus_rc_list:
            continue

        sec_id = name_to_id.get(sec_name)
        if not sec_id or sec_id not in rc_ids_set:
            continue

        for ctrl_name in plus_rc_list:
            ctrl_id = name_to_id.get(ctrl_name)
            if not ctrl_id or ctrl_id not in rc_ids_set:
                continue

            # интересуют только бесстрелочные контролируемые секции
            ctrl_rc_data = RC_SECTIONS.get(ctrl_name) or {}
            if ctrl_rc_data.get("Switches"):
                continue

            # линейная связь ctrl <-> sec_name должна зависеть от всех стрелок stem в плюсе.
            # Представляем это как несколько зависимостей (sec_id, sw_id, SW_PLUS),
            # одну на каждую стрелку из stem.
            for sw_name in stem_switch_names:
                sw_id = name_to_id.get(sw_name)
                if not sw_id:
                    continue
                result.setdefault(ctrl_id, []).append((sec_id, sw_id, SW_PLUS))

    return result



def apply_switch_topology_rules(
    rc_nodes: Dict[str, Any],
) -> None:
    """
    На основании RC_SECTIONS и простых правил по стрелкам заполняет
    RcNode.prev_links/next_links в виде (neighbor_rc_id, switch_id, required_state).

    Важно:
    - не удаляем уже существующие (безусловные) связи (PrevSec/NextSec),
      а только добавляем стрелочные;
    - работаем только с РЦ из GROUPS["rc_ids"].

    Дополнительное правило для бесстрелочных контролируемых секций:

    1) Для РЦ ctrl с Switches = [] её линейные соседи по PrevSec/NextSec
       считаются всегда доступными, если на соседних секциях НЕТ стрелок,
       у которых NextPl/NextMi указывают на ctrl.

    2) Если есть соседняя секция S, у которой в RC_SECTIONS[S]["Switches"]
       есть стрелка с NextPl == ctrl_name или NextMi == ctrl_name,
       то линейная связь ctrl <-> S должна зависеть от этой стрелки:
       - при наличии контроля и нужном положении стрелки сосед допустим,
       - при отсутствии контроля или "не том" положении стрелки сосед
         считается недоступным. Конкретное удержание по T_PK реализовано
         в UniversalTopologyManager (по switch_id и required_state).

    Во всех остальных случаях:
       если на контролируемую секцию нет таких ссылок NextPl/NextMi
       со смежных секций — PrevSec/NextSec остаются безусловными,
       как сейчас: сосед всегда будет, независимо от стрелок.
    """
    name_to_id = _build_name_to_id()
    directions = _build_switch_directions_from_rc_sections(name_to_id)
    ctrl_deps = _build_ctrl_depend_on_neighbor_switch(name_to_id)

    rc_ids_set = set(GROUPS.get("rc_ids", []))

    # 1. Обычные стрелочные направления (ствол -> ветвь)
    for d in directions:
        stem = d.stem_rc_id
        branch = d.branch_rc_id
        sw_id = d.switch_id
        req = d.required_state

        if stem not in rc_ids_set or branch not in rc_ids_set:
            # стрелка может ссылаться на объекты, которые не входят в rc_ids
            continue

        # stem -> branch через sw_id, required_state
        # ВАЖНО: заменяем безусловную связь на стрелочную, если она была
        stem_node = rc_nodes.get(stem)
        if stem_node is not None:
            new_next = []
            replaced = False
            for tid, sid, rstate in stem_node.next_links:
                if tid == branch and (sid is None or rstate < 0):
                    new_next.append((branch, sw_id, req))
                    replaced = True
                else:
                    new_next.append((tid, sid, rstate))
            if not replaced:
                new_next.append((branch, sw_id, req))
            stem_node.next_links = new_next

        branch_node = rc_nodes.get(branch)
        if branch_node is not None:
            new_prev = []
            replaced = False
            for tid, sid, rstate in branch_node.prev_links:
                if tid == stem and (sid is None or rstate < 0):
                    new_prev.append((stem, sw_id, req))
                    replaced = True
                else:
                    new_prev.append((tid, sid, rstate))
            if not replaced:
                new_prev.append((stem, sw_id, req))
            branch_node.prev_links = new_prev

    # 2. Для бесстрелочных контролируемых секций пересобираем линейные связи,
    #    если они должны зависеть от стрелок соседей.
    for ctrl_id, deps in ctrl_deps.items():
        ctrl_node = rc_nodes.get(ctrl_id)
        if ctrl_node is None:
            continue

        # deps: список (neighbor_id, sw_id, required_state)
        # Для каждой зависимости ищем соответствующих линейных соседей
        # и дополняем их стрелочной информацией.
        for neigh_id, sw_id, req in deps:
            # Обновляем prev_links: ctrl <- neigh
            new_prev: List[Tuple[str, Any, int]] = []
            for target_rc, sid, rstate in ctrl_node.prev_links:
                if target_rc == neigh_id and (sid is None or rstate < 0):
                    # Линейная связь ctrl <- neigh становится стрелочно-зависимой
                    new_prev.append((target_rc, sw_id, req))
                else:
                    new_prev.append((target_rc, sid, rstate))
            ctrl_node.prev_links = new_prev

            # Обновляем next_links: ctrl -> neigh
            new_next: List[Tuple[str, Any, int]] = []
            for target_rc, sid, rstate in ctrl_node.next_links:
                if target_rc == neigh_id and (sid is None or rstate < 0):
                    # Линейная связь ctrl -> neigh становится стрелочно-зависимой
                    new_next.append((target_rc, sw_id, req))
                else:
                    new_next.append((target_rc, sid, rstate))
            ctrl_node.next_links = new_next

            # --- ВАЖНО: Симметричное обновление соседа (neigh) ---
            # Если ctrl зависит от стрелки sw_id, чтобы попасть в neigh,
            # то и neigh должен зависеть от этой же стрелки, чтобы попасть в ctrl.
            neigh_node = rc_nodes.get(neigh_id)
            if neigh_node:
                # Обновляем prev_links у соседа: neigh <- ctrl
                new_prev_neigh = []
                for tid, sid, rstate in neigh_node.prev_links:
                    if tid == ctrl_id and (sid is None or rstate < 0):
                        new_prev_neigh.append((tid, sw_id, req))
                    else:
                        new_prev_neigh.append((tid, sid, rstate))
                neigh_node.prev_links = new_prev_neigh

                # Обновляем next_links у соседа: neigh -> ctrl
                new_next_neigh = []
                for tid, sid, rstate in neigh_node.next_links:
                    if tid == ctrl_id and (sid is None or rstate < 0):
                        new_next_neigh.append((tid, sw_id, req))
                    else:
                        new_next_neigh.append((tid, sid, rstate))
                neigh_node.next_links = new_next_neigh

    # 3. Для всех РЦ со стрелками гарантируем, что ЛИНЕЙНЫЕ связи (PrevSec/NextSec)
    #    тоже зависят от контроля стрелок этой секции (хотя бы одной "корневой").
    #    Это покрывает Stem-стороны.
    for rc_id, node in rc_nodes.items():
        # Берем данные из RC_SECTIONS по ID
        rc_name_raw = next((v.get('name') for k, v in NODES.items() if k == rc_id), None)
        if not rc_name_raw:
            continue
        
        sec_data = RC_SECTIONS.get(rc_name_raw)
        if not sec_data:
            continue
            
        switches = sec_data.get("Switches") or []
        if not switches:
            continue
            
        # Находим "корневую" стрелку (у которой нет PrevSw на этой же секции)
        root_sw_id = None
        for sw in switches:
            if not sw.get("PrevSw"):
                sw_name = sw.get("name")
                root_sw_id = name_to_id.get(sw_name)
                break
        
        if not root_sw_id and switches:
            # fallback: любая из секции
            root_sw_id = name_to_id.get(switches[0].get("name"))
            
        if not root_sw_id:
            continue

        # Превращаем оставшиеся безусловные связи в зависимые от root_sw_id (req=-1)
        # Prev:
        new_prev = []
        for tid, sid, rstate in node.prev_links:
            if sid is None:
                new_prev.append((tid, root_sw_id, -1))
            else:
                new_prev.append((tid, sid, rstate))
        node.prev_links = new_prev

        # Next:
        new_next = []
        for tid, sid, rstate in node.next_links:
            if sid is None:
                new_next.append((tid, root_sw_id, -1))
            else:
                new_next.append((tid, sid, rstate))
        node.next_links = new_next

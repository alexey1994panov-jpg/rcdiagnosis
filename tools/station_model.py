# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

from station_switch_rules import apply_switch_topology_rules

# Базовый конфиг станции (ID, типы объектов)
from station_config import GROUPS, NODES
# Детализированное описание секций РЦ
from station_rc_sections import RC_SECTIONS
from station_capabilities import RC_CAPABILITIES

try:
    from station_signals_logic import SIGNALS_LOGIC
except ImportError:
    # If SIGNALS_LOGIC is not found, create an empty one
    SIGNALS_LOGIC: Dict[str, Dict] = {}


# =========================
#  Базовые структуры
# =========================

@dataclass
class RcNode:
    """
    Топологический узел РЦ.

    prev_links / next_links:
      (neighbor_rc_id, switch_id, required_state)

    required_state:
      1  — стрелка должна быть в плюсе (sw_is_plus),
      0  — стрелка должна быть в минусе (sw_is_minus),
     -1  — без условия по стрелке (заглушка для связей без стрелок).
    """
    rc_id: str
    prev_links: List[Tuple[str, Optional[str], int]] = field(default_factory=list)
    next_links: List[Tuple[str, Optional[str], int]] = field(default_factory=list)
    can_lock: bool = True
    is_endpoint: bool = False
    allowed_detectors: List[int] = field(default_factory=list)
    allowed_ls_detectors: List[int] = field(default_factory=list)
    task_lz_number: Optional[int] = None
    task_ls_number: Optional[int] = None


@dataclass
class RcTaskBinding:
    """Привязка технологической задачи (LZ/LS) к объекту."""
    task_name: str
    class_name: str
    description: str


# === НОВОЕ: Структура для сигнала ===
@dataclass
class SignalNode:
    """
    Топологический узел сигнала.
    
    signal_type: "SIG" (маневровый) или "LATE_SIG" (поездной/входной/выходной)
    prev_sec: предыдущая секция (откуда приходят поезда)
    next_sec: следующая секция (куда ведет сигнал) — обязательное поле
    """
    signal_id: str           # ID сигнала (из NODES)
    name: str                # Имя сигнала ("Ч1", "М1", "НМ1")
    signal_type: str         # "SIG" или "LATE_SIG"
    node_id: str             # ID узла в NODES (дублирует signal_id)
    prev_sec: Optional[str]  # ID предыдущей РЦ (может быть None)
    next_sec: str            # ID следующей РЦ (куда ведет сигнал)
    is_shunting: bool = False  # True для маневровых (М*)

# =========================
#  StationModel
# =========================

@dataclass
class StationModel:
    """
    Модель станции, построенная на основе station_config.py и station_rc_sections.py.
    Центральный объект для инициализации топологии и детекторов.
    """

    # РЦ по ID
    rc_nodes: Dict[str, RcNode]

    # Списки ID стрелок и сигналов
    switches: List[str]
    signals: List[str]

    # Задачи LZ/LS, привязанные к РЦ
    tasks: Dict[str, List[RcTaskBinding]] = field(default_factory=dict)

    # Маппинги для быстрого доступа
    rc_ids: List[str] = field(default_factory=list)
    switch_ids: List[str] = field(default_factory=list)
    signal_ids: List[str] = field(default_factory=list)

    rc_index_by_id: Dict[str, int] = field(default_factory=dict)
    switch_index_by_id: Dict[str, int] = field(default_factory=dict)
    signal_index_by_id: Dict[str, int] = field(default_factory=dict)

    # === НОВОЕ: Данные о сигналах ===
    signal_nodes: Dict[str, SignalNode] = field(default_factory=dict)   # ID -> SignalNode
    signal_by_name: Dict[str, str] = field(default_factory=dict)        # name -> ID ("Ч1" -> "114")
    signals_to_rc: Dict[str, List[str]] = field(default_factory=dict)   # rc_id -> [sig_ids] (ведут НА РЦ)
    signals_from_rc: Dict[str, List[str]] = field(default_factory=dict) # rc_id -> [sig_ids] (ведут С РЦ)

    def get_active_neighbors_ids(
        self,
        rc_id: str,
        switch_states: Dict[str, int],
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Простейший помощник на уровне ID (аналог старой get_active_neighbors).
        switch_states: { 'ID_стрелки': 1/0 }.

        Здесь нет памяти (T_PK) и нет учёта Uni_State_ID — это делает TopologyManager.
        """
        node = self.rc_nodes.get(rc_id)
        if not node:
            return None, None

        def find_active(links: List[Tuple[str, Optional[str], int]]) -> Optional[str]:
            for target_rc, sw_id, req_state in links:
                if sw_id is None or req_state < 0:
                    # Безусловная связь или заглушка без условия по стрелке
                    return target_rc
                if switch_states.get(sw_id) == req_state:
                    return target_rc
            return None

        return find_active(node.prev_links), find_active(node.next_links)

    # === НОВОЕ: Методы для работы с сигналами ===
    
    def get_signals_to_rc(self, rc_id: str) -> List[SignalNode]:
        """Возвращает сигналы, ведущие НА данную РЦ (next_sec == rc_id)."""
        sig_ids = self.signals_to_rc.get(rc_id, [])
        return [self.signal_nodes[sid] for sid in sig_ids if sid in self.signal_nodes]
    
    def get_signals_from_rc(self, rc_id: str) -> List[SignalNode]:
        """Возвращает сигналы, ведущие С данной РЦ (prev_sec == rc_id)."""
        sig_ids = self.signals_from_rc.get(rc_id, [])
        return [self.signal_nodes[sid] for sid in sig_ids if sid in self.signal_nodes]
    
    def get_signal_by_name(self, name: str) -> Optional[SignalNode]:
        """Получить сигнал по имени (Ч1, М1, НМ1)."""
        sig_id = self.signal_by_name.get(name)
        return self.signal_nodes.get(sig_id) if sig_id else None
    
    def get_signal_by_id(self, signal_id: str) -> Optional[SignalNode]:
        """Получить сигнал по ID."""
        return self.signal_nodes.get(signal_id)

# =========================
#  Конструктор модели
# =========================

# === НОВОЕ: Конфигурация сигналов (импортируется отдельно) ===
# SIGNALS_LOGIC импортируется из station_signals_logic.py в начале файла


def load_signals_from_config(
    name_to_id: Dict[str, str],
    signals_logic: Optional[Dict[str, Dict]] = None
) -> Tuple[Dict[str, SignalNode], Dict[str, str], Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Загружает сигналы из SIGNALS_LOGIC и строит индексы.
    
    Returns:
        signal_nodes: Dict[signal_id, SignalNode]
        signal_by_name: Dict[name, signal_id]
        signals_to_rc: Dict[rc_id, List[signal_id]] (сигналы, ведущие НА РЦ)
        signals_from_rc: Dict[rc_id, List[signal_id]] (сигналы, ведущие С РЦ)
    """
    if signals_logic is None:
        signals_logic = SIGNALS_LOGIC
    
    signal_nodes: Dict[str, SignalNode] = {}
    signal_by_name: Dict[str, str] = {}
    signals_to_rc: Dict[str, List[str]] = {}
    signals_from_rc: Dict[str, List[str]] = {}
    
    for sig_name, sig_data in signals_logic.items():
        node_id = sig_data.get("node_id")
        if not node_id:
            continue
            
        # Конвертируем имена секций в ID
        prev_sec_name = sig_data.get("PrevSec")
        next_sec_name = sig_data.get("NextSec")
        
        prev_sec_id = name_to_id.get(prev_sec_name) if prev_sec_name else None
        next_sec_id = name_to_id.get(next_sec_name) if next_sec_name else None
        
        # Пропускаем если нет next_sec (некуда ведет сигнал)
        if not next_sec_id:
            continue
        
        sig_type = sig_data.get("type", "LATE_SIG")
        is_shunting = sig_name.startswith("М") and sig_type == "SIG"
        
        signal_node = SignalNode(
            signal_id=node_id,
            name=sig_name,
            signal_type=sig_type,
            node_id=node_id,
            prev_sec=prev_sec_id,
            next_sec=next_sec_id,
            is_shunting=is_shunting,
        )
        
        signal_nodes[node_id] = signal_node
        signal_by_name[sig_name] = node_id
        
        # Индексируем по РЦ
        if next_sec_id:
            signals_to_rc.setdefault(next_sec_id, []).append(node_id)
        if prev_sec_id:
            signals_from_rc.setdefault(prev_sec_id, []).append(node_id)
    
    return signal_nodes, signal_by_name, signals_to_rc, signals_from_rc


def load_station_from_config(
    signals_logic: Optional[Dict[str, Dict]] = None
) -> StationModel:
    """
    Строит StationModel на основе:
      - station_config.GROUPS / NODES (ID, типы, задачи),
      - station_rc_sections.RC_SECTIONS (PrevSec/NextSec + Switches),
      - SIGNALS_LOGIC (сигналы и их связи с РЦ).

    ВАЖНО: prev_links/next_links узлов RcNode формируем по RC_SECTIONS,
    а не по NODES[*]['prev_links'].
    Связи по стрелкам (switch_id, required_state) пока не размечены:
    заполняются как (neighbor_rc_id, None, -1), детальная логика по стрелкам
    задаётся в apply_switch_topology_rules.
    """
    rc_nodes: Dict[str, RcNode] = {}
    tasks: Dict[str, List[RcTaskBinding]] = {}

    # 1. Базовые списки из GROUPS
    rc_ids: List[str] = list(GROUPS.get("rc_ids", []))
    switch_ids: List[str] = list(GROUPS.get("switches_ids", []))
    shunt_signal_ids: List[str] = list(GROUPS.get("shunt_signals_ids", []))
    train_signal_ids: List[str] = list(GROUPS.get("train_signals_ids", []))
    signal_ids: List[str] = shunt_signal_ids + train_signal_ids

    # 2. Маппинг NAME -> ID (для РЦ, стрелок, сигналов)
    name_to_id: Dict[str, str] = {}
    for obj_id, node_data in NODES.items():
        name = node_data.get("name", "")
        if name:
            name_to_id[name] = obj_id

    # 3. Инициализация RcNode по RC_SECTIONS (основная топология по секциям)
    # RC_SECTIONS: { '3СП': { 'PrevSec': '2П', 'NextSec': None, 'Switches': [...] }, ... }
    for rc_name, sec_data in RC_SECTIONS.items():
        rc_id = name_to_id.get(rc_name)
        if rc_id is None:
            # Секция есть в RC_SECTIONS, но нет в NODES — пропускаем (можно залогировать)
            continue

        prev_sec_name: Optional[str] = sec_data.get("PrevSec")
        next_sec_name: Optional[str] = sec_data.get("NextSec")

        prev_links: List[Tuple[str, Optional[str], int]] = []
        next_links: List[Tuple[str, Optional[str], int]] = []

        # PrevSec: простая связь без стрелки
        if prev_sec_name:
            prev_id = name_to_id.get(prev_sec_name)
            if prev_id is not None:
                prev_links.append((prev_id, None, -1))

        # NextSec: базовая связь без стрелки
        if next_sec_name:
            next_id = name_to_id.get(next_sec_name)
            if next_id is not None:
                next_links.append((next_id, None, -1))

        # Пока игнорируем Switches — детальная топология по стрелкам будет
        # добавлена rules-движком (apply_switch_topology_rules).
        rc_nodes[rc_id] = RcNode(
            rc_id=rc_id,
            prev_links=prev_links,
            next_links=next_links,
        )

    # 4. Задачи LZ/LS по NODES (как и раньше)
    for obj_id, node_data in NODES.items():
        obj_type = node_data.get("type")
        if obj_type != 1:
            continue

        node_tasks: List[RcTaskBinding] = []
        for t in node_data.get("tasks", []):
            t_name = t.get("name", "")
            if "LZ" in t_name or "LS" in t_name:
                node_tasks.append(
                    RcTaskBinding(
                        task_name=t_name,
                        class_name=t.get("class", ""),
                        description=t.get("desc", ""),
                    )
                )
        tasks[obj_id] = node_tasks

    # 5. Здесь можно применить правила по стрелкам (автоматически, не руками).
    #    Они будут дополнять prev_links/next_links с учётом Switches и состояний стрелок.
    apply_switch_topology_rules(rc_nodes)

    # 6. Индексация ID
    rc_index_by_id: Dict[str, int] = {rc_id: i for i, rc_id in enumerate(rc_ids)}
    switch_index_by_id: Dict[str, int] = {sw_id: i for i, sw_id in enumerate(switch_ids)}
    signal_index_by_id: Dict[str, int] = {sig_id: i for i, sig_id in enumerate(signal_ids)}

    # 7. Применяем capabilities к РЦ
    for rc_id, node in rc_nodes.items():
        caps = RC_CAPABILITIES.get(rc_id, {})
        node.can_lock = caps.get('can_lock', True)
        node.is_endpoint = caps.get('is_endpoint', False)
        node.allowed_detectors = caps.get('allowed_detectors', list(range(1, 14)))
        node.allowed_ls_detectors = caps.get('allowed_ls_detectors', list(range(1, 10)))
        node.task_lz_number = caps.get('task_lz_number')
        node.task_ls_number = caps.get('task_ls_number')

    # === НОВОЕ: Загрузка сигналов ===
    signal_nodes: Dict[str, SignalNode] = {}
    signal_by_name: Dict[str, str] = {}
    signals_to_rc: Dict[str, List[str]] = {}
    signals_from_rc: Dict[str, List[str]] = {}
    
    # Загружаем сигналы по умолчанию из station_signals_logic
    if signals_logic is None:
        try:
            from station_signals_logic import SIGNALS_LOGIC as default_signals
            signals_logic = default_signals
        except ImportError:
            signals_logic = {}
    
    # Загружаем сигналы
    if signals_logic:
        signal_nodes, signal_by_name, signals_to_rc, signals_from_rc = load_signals_from_config(
            name_to_id=name_to_id,
            signals_logic=signals_logic
        )

    return StationModel(
        rc_nodes=rc_nodes,
        switches=switch_ids,
        signals=signal_ids,
        tasks=tasks,
        rc_ids=rc_ids,
        switch_ids=switch_ids,
        signal_ids=signal_ids,
        rc_index_by_id=rc_index_by_id,
        switch_index_by_id=switch_index_by_id,
        signal_index_by_id=signal_index_by_id,
        # === НОВОЕ: Данные о сигналах ===
        signal_nodes=signal_nodes,
        signal_by_name=signal_by_name,
        signals_to_rc=signals_to_rc,
        signals_from_rc=signals_from_rc,
    )


if __name__ == "__main__":
    model = load_station_from_config()
    from station_config import NODES as RAW_NODES

    print(f"RC count: {len(model.rc_ids)}")
    print(f"Switch count: {len(model.switch_ids)}")
    print(f"Signal count: {len(model.signal_ids)}")
    print(f"Signal nodes loaded: {len(model.signal_nodes)}")
    print()
    
    # Вывод информации о сигналах
    if model.signal_nodes:
        print("=== SIGNALS ===")
        for sig_id, sig_node in list(model.signal_nodes.items())[:5]:  # Первые 5
            print(f"Signal {sig_node.name} (ID={sig_id}): {sig_node.prev_sec} -> {sig_node.next_sec}")
        print()

    # Вывод информации о РЦ с топологией
    for rc_id in model.rc_ids:
        node = model.rc_nodes.get(rc_id)
        if not node:
            continue
        
        rc_name = RAW_NODES.get(rc_id, {}).get("name", "?")

        print(f"RC {rc_name} (ID={rc_id}):")

        # prev_links
        if node.prev_links:
            prev_strs = []
            for target_id, sw_id, req in node.prev_links:
                target_name = RAW_NODES.get(target_id, {}).get("name", "?")
                if sw_id is None:
                    prev_strs.append(f"{target_name}(ID={target_id}, no_sw, req={req})")
                else:
                    sw_name = RAW_NODES.get(sw_id, {}).get("name", "?")
                    prev_strs.append(f"{target_name}(ID={target_id}) via {sw_name}(SW_ID={sw_id}, req={req})")
            print(f"  prev_links: {', '.join(prev_strs)}")
        else:
            print(f"  prev_links: -")

        # next_links
        if node.next_links:
            next_strs = []
            for target_id, sw_id, req in node.next_links:
                target_name = RAW_NODES.get(target_id, {}).get("name", "?")
                if sw_id is None:
                    next_strs.append(f"{target_name}(ID={target_id}, no_sw, req={req})")
                else:
                    sw_name = RAW_NODES.get(sw_id, {}).get("name", "?")
                    next_strs.append(f"{target_name}(ID={target_id}) via {sw_name}(SW_ID={sw_id}, req={req})")
            print(f"  next_links: {', '.join(next_strs)}")
        else:
            print(f"  next_links: -")

        print()
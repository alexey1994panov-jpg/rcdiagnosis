# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

from station.station_switch_rules import apply_switch_topology_rules

# Р‘Р°Р·РѕРІС‹Р№ РєРѕРЅС„РёРі СЃС‚Р°РЅС†РёРё (ID, С‚РёРїС‹ РѕР±СЉРµРєС‚РѕРІ)
from station.station_config import GROUPS, NODES
# Р”РµС‚Р°Р»РёР·РёСЂРѕРІР°РЅРЅРѕРµ РѕРїРёСЃР°РЅРёРµ СЃРµРєС†РёР№ Р Р¦
from station.station_rc_sections import RC_SECTIONS
from station.station_capabilities import RC_CAPABILITIES
from exceptions.indicator_states import INDICATOR_OFF, INDICATOR_ON

try:
    from station.station_signals_logic import SIGNALS_LOGIC
except ImportError:
    # If SIGNALS_LOGIC is not found, create an empty one
    SIGNALS_LOGIC: Dict[str, Dict] = {}


# =========================
#  Р‘Р°Р·РѕРІС‹Рµ СЃС‚СЂСѓРєС‚СѓСЂС‹
# =========================

@dataclass
class RcNode:
    """
    РўРѕРїРѕР»РѕРіРёС‡РµСЃРєРёР№ СѓР·РµР» Р Р¦.

    prev_links / next_links:
      (neighbor_rc_id, switch_id, required_state)

    required_state:
      1  вЂ” СЃС‚СЂРµР»РєР° РґРѕР»Р¶РЅР° Р±С‹С‚СЊ РІ РїР»СЋСЃРµ (sw_is_plus),
      0  вЂ” СЃС‚СЂРµР»РєР° РґРѕР»Р¶РЅР° Р±С‹С‚СЊ РІ РјРёРЅСѓСЃРµ (sw_is_minus),
     -1  вЂ” Р±РµР· СѓСЃР»РѕРІРёСЏ РїРѕ СЃС‚СЂРµР»РєРµ (Р·Р°РіР»СѓС€РєР° РґР»СЏ СЃРІСЏР·РµР№ Р±РµР· СЃС‚СЂРµР»РѕРє).
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
    """РџСЂРёРІСЏР·РєР° С‚РµС…РЅРѕР»РѕРіРёС‡РµСЃРєРѕР№ Р·Р°РґР°С‡Рё (LZ/LS) Рє РѕР±СЉРµРєС‚Сѓ."""
    task_name: str
    class_name: str
    description: str


# === РќРћР’РћР•: РЎС‚СЂСѓРєС‚СѓСЂР° РґР»СЏ СЃРёРіРЅР°Р»Р° ===
@dataclass
class SignalNode:
    """
    РўРѕРїРѕР»РѕРіРёС‡РµСЃРєРёР№ СѓР·РµР» СЃРёРіРЅР°Р»Р°.
    
    signal_type: "SIG" (РјР°РЅРµРІСЂРѕРІС‹Р№) РёР»Рё "LATE_SIG" (РїРѕРµР·РґРЅРѕР№/РІС…РѕРґРЅРѕР№/РІС‹С…РѕРґРЅРѕР№)
    prev_sec: РїСЂРµРґС‹РґСѓС‰Р°СЏ СЃРµРєС†РёСЏ (РѕС‚РєСѓРґР° РїСЂРёС…РѕРґСЏС‚ РїРѕРµР·РґР°)
    next_sec: СЃР»РµРґСѓСЋС‰Р°СЏ СЃРµРєС†РёСЏ (РєСѓРґР° РІРµРґРµС‚ СЃРёРіРЅР°Р») вЂ” РѕР±СЏР·Р°С‚РµР»СЊРЅРѕРµ РїРѕР»Рµ
    """
    signal_id: str           # ID СЃРёРіРЅР°Р»Р° (РёР· NODES)
    name: str                # РРјСЏ СЃРёРіРЅР°Р»Р° ("Р§1", "Рњ1", "РќРњ1")
    signal_type: str         # "SIG" РёР»Рё "LATE_SIG"
    node_id: str             # ID СѓР·Р»Р° РІ NODES (РґСѓР±Р»РёСЂСѓРµС‚ signal_id)
    prev_sec: Optional[str]  # ID РїСЂРµРґС‹РґСѓС‰РµР№ Р Р¦ (РјРѕР¶РµС‚ Р±С‹С‚СЊ None)
    next_sec: str            # ID СЃР»РµРґСѓСЋС‰РµР№ Р Р¦ (РєСѓРґР° РІРµРґРµС‚ СЃРёРіРЅР°Р»)
    is_shunting: bool = False  # True РґР»СЏ РјР°РЅРµРІСЂРѕРІС‹С… (Рњ*)

# =========================
#  StationModel
# =========================

@dataclass
class StationModel:
    """
    РњРѕРґРµР»СЊ СЃС‚Р°РЅС†РёРё, РїРѕСЃС‚СЂРѕРµРЅРЅР°СЏ РЅР° РѕСЃРЅРѕРІРµ station_config.py Рё station_rc_sections.py.
    Р¦РµРЅС‚СЂР°Р»СЊРЅС‹Р№ РѕР±СЉРµРєС‚ РґР»СЏ РёРЅРёС†РёР°Р»РёР·Р°С†РёРё С‚РѕРїРѕР»РѕРіРёРё Рё РґРµС‚РµРєС‚РѕСЂРѕРІ.
    """

    # Р Р¦ РїРѕ ID
    rc_nodes: Dict[str, RcNode]

    # РЎРїРёСЃРєРё ID СЃС‚СЂРµР»РѕРє Рё СЃРёРіРЅР°Р»РѕРІ
    switches: List[str]
    signals: List[str]

    # Р—Р°РґР°С‡Рё LZ/LS, РїСЂРёРІСЏР·Р°РЅРЅС‹Рµ Рє Р Р¦
    tasks: Dict[str, List[RcTaskBinding]] = field(default_factory=dict)

    # РњР°РїРїРёРЅРіРё РґР»СЏ Р±С‹СЃС‚СЂРѕРіРѕ РґРѕСЃС‚СѓРїР°
    rc_ids: List[str] = field(default_factory=list)
    switch_ids: List[str] = field(default_factory=list)
    signal_ids: List[str] = field(default_factory=list)
    indicator_ids: List[str] = field(default_factory=list)

    rc_index_by_id: Dict[str, int] = field(default_factory=dict)
    switch_index_by_id: Dict[str, int] = field(default_factory=dict)
    signal_index_by_id: Dict[str, int] = field(default_factory=dict)
    indicator_index_by_id: Dict[str, int] = field(default_factory=dict)

    # === РќРћР’РћР•: Р”Р°РЅРЅС‹Рµ Рѕ СЃРёРіРЅР°Р»Р°С… ===
    signal_nodes: Dict[str, SignalNode] = field(default_factory=dict)   # ID -> SignalNode
    signal_by_name: Dict[str, str] = field(default_factory=dict)        # name -> ID ("Р§1" -> "114")
    signals_to_rc: Dict[str, List[str]] = field(default_factory=dict)   # rc_id -> [sig_ids] (РІРµРґСѓС‚ РќРђ Р Р¦)
    signals_from_rc: Dict[str, List[str]] = field(default_factory=dict) # rc_id -> [sig_ids] (РІРµРґСѓС‚ РЎ Р Р¦)

    def get_active_neighbors_ids(
        self,
        rc_id: str,
        switch_states: Dict[str, int],
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        РџСЂРѕСЃС‚РµР№С€РёР№ РїРѕРјРѕС‰РЅРёРє РЅР° СѓСЂРѕРІРЅРµ ID (Р°РЅР°Р»РѕРі СЃС‚Р°СЂРѕР№ get_active_neighbors).
        switch_states: { 'ID_СЃС‚СЂРµР»РєРё': 1/0 }.

        Р—РґРµСЃСЊ РЅРµС‚ РїР°РјСЏС‚Рё (T_PK) Рё РЅРµС‚ СѓС‡С‘С‚Р° Uni_State_ID вЂ” СЌС‚Рѕ РґРµР»Р°РµС‚ TopologyManager.
        """
        node = self.rc_nodes.get(rc_id)
        if not node:
            return None, None

        def find_active(links: List[Tuple[str, Optional[str], int]]) -> Optional[str]:
            for target_rc, sw_id, req_state in links:
                if sw_id is None or req_state < 0:
                    # Р‘РµР·СѓСЃР»РѕРІРЅР°СЏ СЃРІСЏР·СЊ РёР»Рё Р·Р°РіР»СѓС€РєР° Р±РµР· СѓСЃР»РѕРІРёСЏ РїРѕ СЃС‚СЂРµР»РєРµ
                    return target_rc
                if switch_states.get(sw_id) == req_state:
                    return target_rc
            return None

        return find_active(node.prev_links), find_active(node.next_links)

    # === РќРћР’РћР•: РњРµС‚РѕРґС‹ РґР»СЏ СЂР°Р±РѕС‚С‹ СЃ СЃРёРіРЅР°Р»Р°РјРё ===
    
    def get_signals_to_rc(self, rc_id: str) -> List[SignalNode]:
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ СЃРёРіРЅР°Р»С‹, РІРµРґСѓС‰РёРµ РќРђ РґР°РЅРЅСѓСЋ Р Р¦ (next_sec == rc_id)."""
        sig_ids = self.signals_to_rc.get(rc_id, [])
        return [self.signal_nodes[sid] for sid in sig_ids if sid in self.signal_nodes]
    
    def get_signals_from_rc(self, rc_id: str) -> List[SignalNode]:
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ СЃРёРіРЅР°Р»С‹, РІРµРґСѓС‰РёРµ РЎ РґР°РЅРЅРѕР№ Р Р¦ (prev_sec == rc_id)."""
        sig_ids = self.signals_from_rc.get(rc_id, [])
        return [self.signal_nodes[sid] for sid in sig_ids if sid in self.signal_nodes]
    
    def get_signal_by_name(self, name: str) -> Optional[SignalNode]:
        """РџРѕР»СѓС‡РёС‚СЊ СЃРёРіРЅР°Р» РїРѕ РёРјРµРЅРё (Р§1, Рњ1, РќРњ1)."""
        sig_id = self.signal_by_name.get(name)
        return self.signal_nodes.get(sig_id) if sig_id else None
    
    def get_signal_by_id(self, signal_id: str) -> Optional[SignalNode]:
        """РџРѕР»СѓС‡РёС‚СЊ СЃРёРіРЅР°Р» РїРѕ ID."""
        return self.signal_nodes.get(signal_id)

    @staticmethod
    def is_indicator_on(state: int) -> bool:
        return int(state) == INDICATOR_ON

    @staticmethod
    def is_indicator_off(state: int) -> bool:
        return int(state) == INDICATOR_OFF

# =========================
#  РљРѕРЅСЃС‚СЂСѓРєС‚РѕСЂ РјРѕРґРµР»Рё
# =========================

# === РќРћР’РћР•: РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ СЃРёРіРЅР°Р»РѕРІ (РёРјРїРѕСЂС‚РёСЂСѓРµС‚СЃСЏ РѕС‚РґРµР»СЊРЅРѕ) ===
# SIGNALS_LOGIC РёРјРїРѕСЂС‚РёСЂСѓРµС‚СЃСЏ РёР· station_signals_logic.py РІ РЅР°С‡Р°Р»Рµ С„Р°Р№Р»Р°


def load_signals_from_config(
    name_to_id: Dict[str, str],
    signals_logic: Optional[Dict[str, Dict]] = None
) -> Tuple[Dict[str, SignalNode], Dict[str, str], Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Р—Р°РіСЂСѓР¶Р°РµС‚ СЃРёРіРЅР°Р»С‹ РёР· SIGNALS_LOGIC Рё СЃС‚СЂРѕРёС‚ РёРЅРґРµРєСЃС‹.
    
    Returns:
        signal_nodes: Dict[signal_id, SignalNode]
        signal_by_name: Dict[name, signal_id]
        signals_to_rc: Dict[rc_id, List[signal_id]] (СЃРёРіРЅР°Р»С‹, РІРµРґСѓС‰РёРµ РќРђ Р Р¦)
        signals_from_rc: Dict[rc_id, List[signal_id]] (СЃРёРіРЅР°Р»С‹, РІРµРґСѓС‰РёРµ РЎ Р Р¦)
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
            
        # РљРѕРЅРІРµСЂС‚РёСЂСѓРµРј РёРјРµРЅР° СЃРµРєС†РёР№ РІ ID
        prev_sec_name = sig_data.get("PrevSec")
        next_sec_name = sig_data.get("NextSec")
        
        prev_sec_id = name_to_id.get(prev_sec_name) if prev_sec_name else None
        next_sec_id = name_to_id.get(next_sec_name) if next_sec_name else None
        
        # РџСЂРѕРїСѓСЃРєР°РµРј РµСЃР»Рё РЅРµС‚ next_sec (РЅРµРєСѓРґР° РІРµРґРµС‚ СЃРёРіРЅР°Р»)
        if not next_sec_id:
            continue
        
        sig_type = sig_data.get("type", "LATE_SIG")
        is_shunting = sig_name.startswith("Рњ") and sig_type == "SIG"
        
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
        
        # РРЅРґРµРєСЃРёСЂСѓРµРј РїРѕ Р Р¦
        if next_sec_id:
            signals_to_rc.setdefault(next_sec_id, []).append(node_id)
        if prev_sec_id:
            signals_from_rc.setdefault(prev_sec_id, []).append(node_id)
    
    return signal_nodes, signal_by_name, signals_to_rc, signals_from_rc


def load_station_from_config(
    signals_logic: Optional[Dict[str, Dict]] = None
) -> StationModel:
    """
    РЎС‚СЂРѕРёС‚ StationModel РЅР° РѕСЃРЅРѕРІРµ:
      - station_config.GROUPS / NODES (ID, С‚РёРїС‹, Р·Р°РґР°С‡Рё),
      - station_rc_sections.RC_SECTIONS (PrevSec/NextSec + Switches),
      - SIGNALS_LOGIC (СЃРёРіРЅР°Р»С‹ Рё РёС… СЃРІСЏР·Рё СЃ Р Р¦).

    Р’РђР–РќРћ: prev_links/next_links СѓР·Р»РѕРІ RcNode С„РѕСЂРјРёСЂСѓРµРј РїРѕ RC_SECTIONS,
    Р° РЅРµ РїРѕ NODES[*]['prev_links'].
    РЎРІСЏР·Рё РїРѕ СЃС‚СЂРµР»РєР°Рј (switch_id, required_state) РїРѕРєР° РЅРµ СЂР°Р·РјРµС‡РµРЅС‹:
    Р·Р°РїРѕР»РЅСЏСЋС‚СЃСЏ РєР°Рє (neighbor_rc_id, None, -1), РґРµС‚Р°Р»СЊРЅР°СЏ Р»РѕРіРёРєР° РїРѕ СЃС‚СЂРµР»РєР°Рј
    Р·Р°РґР°С‘С‚СЃСЏ РІ apply_switch_topology_rules.
    """
    rc_nodes: Dict[str, RcNode] = {}
    tasks: Dict[str, List[RcTaskBinding]] = {}

    # 1. Р‘Р°Р·РѕРІС‹Рµ СЃРїРёСЃРєРё РёР· GROUPS
    rc_ids: List[str] = list(GROUPS.get("rc_ids", []))
    switch_ids: List[str] = list(GROUPS.get("switches_ids", []))
    shunt_signal_ids: List[str] = list(GROUPS.get("shunt_signals_ids", []))
    train_signal_ids: List[str] = list(GROUPS.get("train_signals_ids", []))
    signal_ids: List[str] = shunt_signal_ids + train_signal_ids
    indicator_ids: List[str] = list(GROUPS.get("indicator_ids", []))

    # 2. РњР°РїРїРёРЅРі NAME -> ID (РґР»СЏ Р Р¦, СЃС‚СЂРµР»РѕРє, СЃРёРіРЅР°Р»РѕРІ)
    name_to_id: Dict[str, str] = {}
    for obj_id, node_data in NODES.items():
        name = node_data.get("name", "")
        if name:
            name_to_id[name] = obj_id

    # 3. РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ RcNode РїРѕ RC_SECTIONS (РѕСЃРЅРѕРІРЅР°СЏ С‚РѕРїРѕР»РѕРіРёСЏ РїРѕ СЃРµРєС†РёСЏРј)
    # RC_SECTIONS: { '3РЎРџ': { 'PrevSec': '2Рџ', 'NextSec': None, 'Switches': [...] }, ... }
    for rc_name, sec_data in RC_SECTIONS.items():
        rc_id = name_to_id.get(rc_name)
        if rc_id is None:
            # РЎРµРєС†РёСЏ РµСЃС‚СЊ РІ RC_SECTIONS, РЅРѕ РЅРµС‚ РІ NODES вЂ” РїСЂРѕРїСѓСЃРєР°РµРј (РјРѕР¶РЅРѕ Р·Р°Р»РѕРіРёСЂРѕРІР°С‚СЊ)
            continue

        prev_sec_name: Optional[str] = sec_data.get("PrevSec")
        next_sec_name: Optional[str] = sec_data.get("NextSec")

        prev_links: List[Tuple[str, Optional[str], int]] = []
        next_links: List[Tuple[str, Optional[str], int]] = []

        # PrevSec: РїСЂРѕСЃС‚Р°СЏ СЃРІСЏР·СЊ Р±РµР· СЃС‚СЂРµР»РєРё
        if prev_sec_name:
            prev_id = name_to_id.get(prev_sec_name)
            if prev_id is not None:
                prev_links.append((prev_id, None, -1))

        # NextSec: Р±Р°Р·РѕРІР°СЏ СЃРІСЏР·СЊ Р±РµР· СЃС‚СЂРµР»РєРё
        if next_sec_name:
            next_id = name_to_id.get(next_sec_name)
            if next_id is not None:
                next_links.append((next_id, None, -1))

        # РџРѕРєР° РёРіРЅРѕСЂРёСЂСѓРµРј Switches вЂ” РґРµС‚Р°Р»СЊРЅР°СЏ С‚РѕРїРѕР»РѕРіРёСЏ РїРѕ СЃС‚СЂРµР»РєР°Рј Р±СѓРґРµС‚
        # РґРѕР±Р°РІР»РµРЅР° rules-РґРІРёР¶РєРѕРј (apply_switch_topology_rules).
        rc_nodes[rc_id] = RcNode(
            rc_id=rc_id,
            prev_links=prev_links,
            next_links=next_links,
        )

    # 4. Р—Р°РґР°С‡Рё LZ/LS РїРѕ NODES (РєР°Рє Рё СЂР°РЅСЊС€Рµ)
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

    # 5. Р—РґРµСЃСЊ РјРѕР¶РЅРѕ РїСЂРёРјРµРЅРёС‚СЊ РїСЂР°РІРёР»Р° РїРѕ СЃС‚СЂРµР»РєР°Рј (Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё, РЅРµ СЂСѓРєР°РјРё).
    #    РћРЅРё Р±СѓРґСѓС‚ РґРѕРїРѕР»РЅСЏС‚СЊ prev_links/next_links СЃ СѓС‡С‘С‚РѕРј Switches Рё СЃРѕСЃС‚РѕСЏРЅРёР№ СЃС‚СЂРµР»РѕРє.
    apply_switch_topology_rules(rc_nodes)

    # 6. РРЅРґРµРєСЃР°С†РёСЏ ID
    rc_index_by_id: Dict[str, int] = {rc_id: i for i, rc_id in enumerate(rc_ids)}
    switch_index_by_id: Dict[str, int] = {sw_id: i for i, sw_id in enumerate(switch_ids)}
    signal_index_by_id: Dict[str, int] = {sig_id: i for i, sig_id in enumerate(signal_ids)}
    indicator_index_by_id: Dict[str, int] = {ind_id: i for i, ind_id in enumerate(indicator_ids)}

    # 7. РџСЂРёРјРµРЅСЏРµРј capabilities Рє Р Р¦
    for rc_id, node in rc_nodes.items():
        caps = RC_CAPABILITIES.get(rc_id, {})
        node.can_lock = caps.get('can_lock', True)
        node.is_endpoint = caps.get('is_endpoint', False)
        node.allowed_detectors = caps.get('allowed_detectors', list(range(1, 14)))
        node.allowed_ls_detectors = caps.get('allowed_ls_detectors', list(range(1, 10)))
        node.task_lz_number = caps.get('task_lz_number')
        node.task_ls_number = caps.get('task_ls_number')

    # === РќРћР’РћР•: Р—Р°РіСЂСѓР·РєР° СЃРёРіРЅР°Р»РѕРІ ===
    signal_nodes: Dict[str, SignalNode] = {}
    signal_by_name: Dict[str, str] = {}
    signals_to_rc: Dict[str, List[str]] = {}
    signals_from_rc: Dict[str, List[str]] = {}
    
    # Р—Р°РіСЂСѓР¶Р°РµРј СЃРёРіРЅР°Р»С‹ РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ РёР· station_signals_logic
    if signals_logic is None:
        try:
            from station.station_signals_logic import SIGNALS_LOGIC as default_signals
            signals_logic = default_signals
        except ImportError:
            signals_logic = {}
    
    # Р—Р°РіСЂСѓР¶Р°РµРј СЃРёРіРЅР°Р»С‹
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
        indicator_ids=indicator_ids,
        rc_index_by_id=rc_index_by_id,
        switch_index_by_id=switch_index_by_id,
        signal_index_by_id=signal_index_by_id,
        indicator_index_by_id=indicator_index_by_id,
        # === РќРћР’РћР•: Р”Р°РЅРЅС‹Рµ Рѕ СЃРёРіРЅР°Р»Р°С… ===
        signal_nodes=signal_nodes,
        signal_by_name=signal_by_name,
        signals_to_rc=signals_to_rc,
        signals_from_rc=signals_from_rc,
    )


if __name__ == "__main__":
    model = load_station_from_config()
    from station.station_config import NODES as RAW_NODES

    print(f"RC count: {len(model.rc_ids)}")
    print(f"Switch count: {len(model.switch_ids)}")
    print(f"Signal count: {len(model.signal_ids)}")
    print(f"Signal nodes loaded: {len(model.signal_nodes)}")
    print()
    
    # Р’С‹РІРѕРґ РёРЅС„РѕСЂРјР°С†РёРё Рѕ СЃРёРіРЅР°Р»Р°С…
    if model.signal_nodes:
        print("=== SIGNALS ===")
        for sig_id, sig_node in list(model.signal_nodes.items())[:5]:  # РџРµСЂРІС‹Рµ 5
            print(f"Signal {sig_node.name} (ID={sig_id}): {sig_node.prev_sec} -> {sig_node.next_sec}")
        print()

    # Р’С‹РІРѕРґ РёРЅС„РѕСЂРјР°С†РёРё Рѕ Р Р¦ СЃ С‚РѕРїРѕР»РѕРіРёРµР№
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


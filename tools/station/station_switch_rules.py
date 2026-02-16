# -*- coding: utf-8 -*-
"""
РџСЂР°РІРёР»Р° С„РѕСЂРјРёСЂРѕРІР°РЅРёСЏ С‚РѕРїРѕР»РѕРіРёРё РїРѕ СЃС‚СЂРµР»РєР°Рј.

Р¦РµР»СЊ:
- Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё РїСЂРѕСЃС‚Р°РІРёС‚СЊ РІ RcNode.prev_links/next_links Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РІРёРґР°
  (neighbor_rc_id, switch_id, required_state),
РёСЃРїРѕР»СЊР·СѓСЏ РґР°РЅРЅС‹Рµ РёР· station_rc_sections.RC_SECTIONS Рё station_config.NODES.

РќРѕРІС‹Р№ РІР°Р¶РЅС‹Р№ РјРѕРјРµРЅС‚ (РґР»СЏ Р±РµСЃСЃС‚СЂРµР»РѕС‡РЅС‹С… РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹С… СЃРµРєС†РёР№):

1) Р”Р»СЏ Р Р¦ ctrl, Сѓ РєРѕС‚РѕСЂРѕР№ Switches = [] (С‚.Рµ. СЃР°РјР° СЃРµРєС†РёСЏ Р±РµСЃСЃС‚СЂРµР»РѕС‡РЅР°СЏ),
   РµС‘ Р»РёРЅРµР№РЅС‹Рµ СЃРѕСЃРµРґРё РїРѕ PrevSec/NextSec СЃС‡РёС‚Р°СЋС‚СЃСЏ:

   - Р±РµР·СѓСЃР»РѕРІРЅС‹РјРё (СЃРѕСЃРµРґ РІСЃРµРіРґР° РµСЃС‚СЊ), РµСЃР»Рё РќР•Рў РЅРё РѕРґРЅРѕР№ СЃС‚СЂРµР»РєРё
     РЅР° СЃРѕСЃРµРґРЅРёС… СЃРµРєС†РёСЏС…, Сѓ РєРѕС‚РѕСЂРѕР№ NextPl/NextMi СѓРєР°Р·С‹РІР°СЋС‚ РЅР° ctrl;

   - "СЃС‚СЂРµР»РѕС‡РЅРѕ-Р·Р°РІРёСЃРёРјС‹РјРё", РµСЃР»Рё РµСЃС‚СЊ СЃРѕСЃРµРґРЅСЏСЏ СЃРµРєС†РёСЏ S, Сѓ РєРѕС‚РѕСЂРѕР№
     РІ RC_SECTIONS[S]["Switches"] РµСЃС‚СЊ СЃС‚СЂРµР»РєР°, РґР»СЏ РєРѕС‚РѕСЂРѕР№
       NextPl == ctrl_name РёР»Рё NextMi == ctrl_name.
     Р’ СЌС‚РѕРј СЃР»СѓС‡Р°Рµ Р»РёРЅРµР№РЅР°СЏ СЃРІСЏР·СЊ ctrl <-> S РґРѕР»Р¶РЅР° Р·Р°РІРёСЃРµС‚СЊ РѕС‚
     СЌС‚РѕР№ СЃС‚СЂРµР»РєРё (switch_id, required_state).

2) РљРѕРЅРєСЂРµС‚РЅРѕРµ РїРѕРІРµРґРµРЅРёРµ РїСЂРё РїРѕС‚РµСЂРµ РєРѕРЅС‚СЂРѕР»СЏ Рё РўРџРљ СЂРµР°Р»РёР·СѓРµС‚СЃСЏ
   РІ UniversalTopologyManager: С‚Р°Рј РїРѕ switch_id Рё required_state
   СЂРµС€Р°РµС‚СЃСЏ, СЃС‡РёС‚Р°С‚СЊ Р»Рё СЃРѕСЃРµРґ СЃРµР№С‡Р°СЃ РґРѕСЃС‚СѓРїРЅС‹Рј, РІ С‚РѕРј С‡РёСЃР»Рµ СЃ СѓС‡С‘С‚РѕРј
   СѓРґРµСЂР¶Р°РЅРёСЏ (latch) РЅР° РІСЂРµРјСЏ T_PK.

РќР° СЌС‚РѕРј СѓСЂРѕРІРЅРµ РјС‹ РЅРµ Р»РµР·РµРј РІ РґРµС‚РµРєС‚РѕСЂС‹ Рё РёСЃРєР»СЋС‡РµРЅРёСЏ, С‚РѕР»СЊРєРѕ С‚РѕРїРѕР»РѕРіРёСЏ СЃРµРєС†РёР№.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Tuple

from station.station_config import NODES, GROUPS
from station.station_rc_sections import RC_SECTIONS
from station.station_switch_logic import SWITCH_LOGIC  


# РўСЂРµР±СѓРµРјРѕРµ СЃРѕСЃС‚РѕСЏРЅРёРµ СЃС‚СЂРµР»РєРё
SW_PLUS = 1
SW_MINUS = 0


@dataclass
class SwitchDirection:
    """
    РћРїРёСЃР°РЅРёРµ РЅР°РїСЂР°РІР»РµРЅРёСЏ С‡РµСЂРµР· СЃС‚СЂРµР»РєСѓ:

    - stem_rc_id: Р Р¦ "СЃС‚РІРѕР»Р°" (СЃРµРєС†РёСЏ, Рє РєРѕС‚РѕСЂРѕР№ РїСЂРёРІСЏР·Р°РЅР° СЃС‚СЂРµР»РєР° вЂ“ SwSection);
    - branch_rc_id: Р Р¦ "РѕС‚РІРµС‚РІР»РµРЅРёСЏ" (NextMi / NextPl);
    - switch_id: ID СЃС‚СЂРµР»РєРё;
    - required_state: 1 (РїР»СЋСЃ) РёР»Рё 0 (РјРёРЅСѓСЃ).
    """
    stem_rc_id: str
    branch_rc_id: str
    switch_id: str
    required_state: int
    stem_side: str = "next"


def _build_name_to_id() -> Dict[str, str]:
    """
    РЎС‚СЂРѕРёС‚ РјР°РїРїРёРЅРі NAME -> ID РґР»СЏ РІСЃРµС… РѕР±СЉРµРєС‚РѕРІ РёР· NODES.
    РќСѓР¶РµРЅ, С‡С‚РѕР±С‹ РїРµСЂРµРІРµСЃС‚Рё РёРјРµРЅР° СЃРµРєС†РёР№ ('3РЎРџ') Рё СЃС‚СЂРµР»РѕРє ('3') РІ ID.
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
    РЎС‚СЂРѕРёС‚ РЅР°РїСЂР°РІР»РµРЅРёСЏ С‡РµСЂРµР· СЃС‚СЂРµР»РєРё РїРѕ РґР°РЅРЅС‹Рј RC_SECTIONS.

    RC_SECTIONS[sec_name]['Switches'] СЃРѕРґРµСЂР¶РёС‚ Р·Р°РїРёСЃРё:
      { 'name': '3', 'NextMi': '1-7РЎРџ', 'NextPl': 'РќР”Рџ', 'NextSwPl': ...,
        'NextSwMi': ..., 'PrevSw': ... }

    Р”Р»СЏ РєР°Р¶РґРѕРіРѕ SwSection (СЃРµРєС†РёРё) Рё РµС‘ СЃС‚СЂРµР»РѕРє СЃС‚СЂРѕРёРј:
      - stem = ID СЃРµРєС†РёРё (SwSection),
      - branch_minus = ID NextMi (РµСЃР»Рё РµСЃС‚СЊ) в†’ required_state = SW_MINUS,
      - branch_plus  = ID NextPl (РµСЃР»Рё РµСЃС‚СЊ) в†’ required_state = SW_PLUS.

    Р•СЃР»Рё РёРјСЏ СЃРµРєС†РёРё РёР»Рё СЃС‚СЂРµР»РєРё РЅРµ СѓРґР°С‘С‚СЃСЏ РїРµСЂРµРІРµСЃС‚Рё РІ ID, РЅР°РїСЂР°РІР»РµРЅРёРµ РїСЂРѕРїСѓСЃРєР°РµС‚СЃСЏ.
    """
    directions: List[SwitchDirection] = []

    for sec_name, sec_data in RC_SECTIONS.items():
        stem_id = name_to_id.get(sec_name)
        if not stem_id:
            # СЃРµРєС†РёСЏ РёР· RC_SECTIONS РЅРµ РЅР°Р№РґРµРЅР° РІ NODES
            continue
        prev_sec = sec_data.get("PrevSec")
        next_sec = sec_data.get("NextSec")
        stem_side = "next"
        if (not prev_sec) and next_sec:
            stem_side = "prev"

        switches = sec_data.get("Switches") or []
        for sw in switches:
            sw_name = sw.get("name")
            if not sw_name:
                continue

            sw_id = name_to_id.get(sw_name)
            if not sw_id:
                # СЃС‚СЂРµР»РєР° Р±РµР· ID вЂ” РїСЂРѕРїСѓСЃРєР°РµРј
                continue

            next_mi = sw.get("NextMi")
            next_pl = sw.get("NextPl")

            # РњРёРЅСѓСЃРѕРІРѕРµ РЅР°РїСЂР°РІР»РµРЅРёРµ (РњРљ): stem -> NextMi
            if next_mi:
                branch_id = name_to_id.get(next_mi)
                if branch_id:
                    directions.append(
                        SwitchDirection(
                            stem_rc_id=stem_id,
                            branch_rc_id=branch_id,
                            switch_id=sw_id,
                            required_state=SW_MINUS,
                            stem_side=stem_side,
                        )
                    )

            # РџР»СЋСЃРѕРІРѕРµ РЅР°РїСЂР°РІР»РµРЅРёРµ (РџРљ): stem -> NextPl
            if next_pl:
                branch_id = name_to_id.get(next_pl)
                if branch_id:
                    directions.append(
                        SwitchDirection(
                            stem_rc_id=stem_id,
                            branch_rc_id=branch_id,
                            switch_id=sw_id,
                            required_state=SW_PLUS,
                            stem_side=stem_side,
                        )
                    )

    return directions



def _build_ctrl_depend_on_neighbor_switch(
    name_to_id: Dict[str, str],
) -> Dict[str, List[Tuple[str, str, int]]]:
    """
    РЎС‚СЂРѕРёС‚ РєР°СЂС‚Сѓ "РєР°РєРёРµ Р±РµСЃСЃС‚СЂРµР»РѕС‡РЅС‹Рµ СЃРµРєС†РёРё ctrl Р·Р°РІРёСЃСЏС‚ РѕС‚ СЃС‚СЂРµР»РѕРє РЅР° СЃРѕСЃРµРґСЏС…".

    Р¤РѕСЂРјР°С‚С‹:
        result: { ctrl_id: [(neighbor_id, switch_id, required_state), ...], ... }

    РСЃС‚РѕС‡РЅРёРєРё РґР°РЅРЅС‹С…:
        - RC_SECTIONS: РїСЂРѕСЃС‚С‹Рµ СЃР»СѓС‡Р°Рё (РѕРґРЅР° СЃС‚СЂРµР»РєР° NextMi/NextPl РІРµРґС‘С‚ РЅР° ctrl);
        - SWITCH_LOGIC: СЃР»РѕР¶РЅС‹Рµ СЃР»СѓС‡Р°Рё, РіРґРµ Сѓ СЃРµРєС†РёРё РЅРµСЃРєРѕР»СЊРєРѕ СЃС‚РІРѕР»РѕРІ (stem)
          Рё ctrl РІС…РѕРґРёС‚ РІ РµС‘ plus_rc (РЅР°РїСЂРёРјРµСЂ, 1-7РЎРџ СЃРѕ stem=['1','5'] Рё plus_rc=['1Рџ']).
    """
    result: Dict[str, List[Tuple[str, str, int]]] = {}

    rc_ids_set = set(GROUPS.get("rc_ids", []))

    # --- 1. Р‘Р°Р·РѕРІС‹Рµ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РїРѕ RC_SECTIONS (РѕРґРЅР° СЃС‚СЂРµР»РєР° -> ctrl) ---
    for ctrl_name, ctrl_data in RC_SECTIONS.items():
        switches = ctrl_data.get("Switches") or []
        # РёРЅС‚РµСЂРµСЃСѓСЋС‚ С‚РѕР»СЊРєРѕ Р±РµСЃСЃС‚СЂРµР»РѕС‡РЅС‹Рµ Р Р¦
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

                # Р•СЃР»Рё СЃС‚СЂРµР»РєР° РЅР° СЃРѕСЃРµРґРЅРµР№ СЃРµРєС†РёРё РІРµРґС‘С‚ РЅР° ctrl РїРѕ РјРёРЅСѓСЃСѓ
                if next_mi == ctrl_name:
                    deps.append((neigh_id, sw_id, SW_MINUS))

                # Р•СЃР»Рё СЃС‚СЂРµР»РєР° РЅР° СЃРѕСЃРµРґРЅРµР№ СЃРµРєС†РёРё РІРµРґС‘С‚ РЅР° ctrl РїРѕ РїР»СЋСЃСѓ
                if next_pl == ctrl_name:
                    deps.append((neigh_id, sw_id, SW_PLUS))

            # --- 3. РЎС‚РІРѕР»РѕРІС‹Рµ (Stem) Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РїРѕ RC_SECTIONS ---
            # Р•СЃР»Рё РјРµР¶РґСѓ ctrl Рё neigh РµСЃС‚СЊ СЃРІСЏР·СЊ, РЅРѕ РѕРЅР° РЅРµ СЏРІР»СЏРµС‚СЃСЏ РѕС‚РІРµС‚РІР»РµРЅРёРµРј 
            # РЅРё РѕРґРЅРѕР№ СЃС‚СЂРµР»РєРё РЅР° neigh вЂ” Р·РЅР°С‡РёС‚ СЌС‚Рѕ СЃС‚РІРѕР».
            if neigh_switches and not any(d[0] == neigh_id for d in deps):
                # РџСЂРѕР±СѓРµРј РЅР°Р№С‚Рё СЏРІРЅСѓСЋ СЃРІСЏР·СЊ РїРѕ NextMi/NextPl РµСЃР»Рё РѕРЅР° РµСЃС‚СЊ
                # (РґР»СЏ РѕРґРЅРѕРЅРёС‚РѕС‡РЅС‹С… РїР»Р°РЅРѕРІ РёРЅРѕРіРґР° NextSec СѓРєР°Р·С‹РІР°РµС‚ РЅР° СЃС‚СЂРµР»РєСѓ, РєРѕС‚РѕСЂР°СЏ СЃРјРѕС‚СЂРёС‚ РЅР° РЅР°СЃ)
                for sw in neigh_switches:
                    sw_id = name_to_id.get(sw.get("name"))
                    if not sw_id: continue
                    
                    # Р•СЃР»Рё NextMi СЌС‚РѕР№ СЃС‚СЂРµР»РєРё СѓРєР°Р·С‹РІР°РµС‚ РЅР° РЅР°СЃ -> Р·Р°РІРёСЃРёРј РѕС‚ РјРёРЅСѓСЃР°
                    if sw.get("NextMi") == ctrl_name:
                         deps.append((neigh_id, sw_id, SW_MINUS))
                         break
                    # Р•СЃР»Рё NextPl СЌС‚РѕР№ СЃС‚СЂРµР»РєРё СѓРєР°Р·С‹РІР°РµС‚ РЅР° РЅР°СЃ -> Р·Р°РІРёСЃРёРј РѕС‚ РїР»СЋСЃР°
                    if sw.get("NextPl") == ctrl_name:
                         deps.append((neigh_id, sw_id, SW_PLUS))
                         break
                
                # Р•СЃР»Рё СЃРїРµС†РёС„РёС‡РµСЃРєРѕР№ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РЅРµ РЅР°С€Р»Рё - РёС‰РµРј РєРѕСЂРЅРµРІСѓСЋ (РѕР±С‰РёР№ СЃС‚РІРѕР»)
                # Р­С‚Рѕ РєРѕРіРґР° РјС‹ СЃРѕ СЃС‚РѕСЂРѕРЅС‹ РѕСЃС‚СЂСЏРєР°
                if not deps:
                    root_sw_id = None
                    for sw in neigh_switches:
                        if not sw.get("PrevSw"):
                            root_sw_id = name_to_id.get(sw.get("name"))
                            break
                    if not root_sw_id:
                        root_sw_id = name_to_id.get(neigh_switches[0].get("name"))
                    
                    if root_sw_id:
                        # req=-1 РѕР·РЅР°С‡Р°РµС‚ "Р»СЋР±РѕРµ РїРѕР»РѕР¶РµРЅРёРµ, РЅРѕ РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ РєРѕРЅС‚СЂРѕР»СЊ"
                        deps.append((neigh_id, root_sw_id, -1))

        if deps:
            result[ctrl_id] = deps

    # --- 4. Р”РѕРїРѕР»РЅРёС‚РµР»СЊРЅС‹Рµ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РїРѕ SWITCH_LOGIC (СЃР»РѕР¶РЅС‹Рµ СЃС‚РІРѕР»С‹) ---
    # Р—РґРµСЃСЊ РјС‹ СѓС‡РёС‚С‹РІР°РµРј СЃР»СѓС‡Р°Рё, РєРѕРіРґР° Сѓ СЃРµРєС†РёРё РЅРµСЃРєРѕР»СЊРєРѕ СЃС‚СЂРµР»РѕРє РІ stem
    # Рё ctrl РІС…РѕРґРёС‚ РІ РµС‘ plus_rc. Р­С‚Рѕ РєР°Рє СЂР°Р· 1-7РЎРџ -> 1Рџ С‡РµСЂРµР· СЃС‚СЂРµР»РєРё 1 Рё 5.
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

            # РёРЅС‚РµСЂРµСЃСѓСЋС‚ С‚РѕР»СЊРєРѕ Р±РµСЃСЃС‚СЂРµР»РѕС‡РЅС‹Рµ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹Рµ СЃРµРєС†РёРё
            ctrl_rc_data = RC_SECTIONS.get(ctrl_name) or {}
            if ctrl_rc_data.get("Switches"):
                continue

            # Р»РёРЅРµР№РЅР°СЏ СЃРІСЏР·СЊ ctrl <-> sec_name РґРѕР»Р¶РЅР° Р·Р°РІРёСЃРµС‚СЊ РѕС‚ РІСЃРµС… СЃС‚СЂРµР»РѕРє stem РІ РїР»СЋСЃРµ.
            # РџСЂРµРґСЃС‚Р°РІР»СЏРµРј СЌС‚Рѕ РєР°Рє РЅРµСЃРєРѕР»СЊРєРѕ Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№ (sec_id, sw_id, SW_PLUS),
            # РѕРґРЅСѓ РЅР° РєР°Р¶РґСѓСЋ СЃС‚СЂРµР»РєСѓ РёР· stem.
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
    РќР° РѕСЃРЅРѕРІР°РЅРёРё RC_SECTIONS Рё РїСЂРѕСЃС‚С‹С… РїСЂР°РІРёР» РїРѕ СЃС‚СЂРµР»РєР°Рј Р·Р°РїРѕР»РЅСЏРµС‚
    RcNode.prev_links/next_links РІ РІРёРґРµ (neighbor_rc_id, switch_id, required_state).

    Р’Р°Р¶РЅРѕ:
    - РЅРµ СѓРґР°Р»СЏРµРј СѓР¶Рµ СЃСѓС‰РµСЃС‚РІСѓСЋС‰РёРµ (Р±РµР·СѓСЃР»РѕРІРЅС‹Рµ) СЃРІСЏР·Рё (PrevSec/NextSec),
      Р° С‚РѕР»СЊРєРѕ РґРѕР±Р°РІР»СЏРµРј СЃС‚СЂРµР»РѕС‡РЅС‹Рµ;
    - СЂР°Р±РѕС‚Р°РµРј С‚РѕР»СЊРєРѕ СЃ Р Р¦ РёР· GROUPS["rc_ids"].

    Р”РѕРїРѕР»РЅРёС‚РµР»СЊРЅРѕРµ РїСЂР°РІРёР»Рѕ РґР»СЏ Р±РµСЃСЃС‚СЂРµР»РѕС‡РЅС‹С… РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹С… СЃРµРєС†РёР№:

    1) Р”Р»СЏ Р Р¦ ctrl СЃ Switches = [] РµС‘ Р»РёРЅРµР№РЅС‹Рµ СЃРѕСЃРµРґРё РїРѕ PrevSec/NextSec
       СЃС‡РёС‚Р°СЋС‚СЃСЏ РІСЃРµРіРґР° РґРѕСЃС‚СѓРїРЅС‹РјРё, РµСЃР»Рё РЅР° СЃРѕСЃРµРґРЅРёС… СЃРµРєС†РёСЏС… РќР•Рў СЃС‚СЂРµР»РѕРє,
       Сѓ РєРѕС‚РѕСЂС‹С… NextPl/NextMi СѓРєР°Р·С‹РІР°СЋС‚ РЅР° ctrl.

    2) Р•СЃР»Рё РµСЃС‚СЊ СЃРѕСЃРµРґРЅСЏСЏ СЃРµРєС†РёСЏ S, Сѓ РєРѕС‚РѕСЂРѕР№ РІ RC_SECTIONS[S]["Switches"]
       РµСЃС‚СЊ СЃС‚СЂРµР»РєР° СЃ NextPl == ctrl_name РёР»Рё NextMi == ctrl_name,
       С‚Рѕ Р»РёРЅРµР№РЅР°СЏ СЃРІСЏР·СЊ ctrl <-> S РґРѕР»Р¶РЅР° Р·Р°РІРёСЃРµС‚СЊ РѕС‚ СЌС‚РѕР№ СЃС‚СЂРµР»РєРё:
       - РїСЂРё РЅР°Р»РёС‡РёРё РєРѕРЅС‚СЂРѕР»СЏ Рё РЅСѓР¶РЅРѕРј РїРѕР»РѕР¶РµРЅРёРё СЃС‚СЂРµР»РєРё СЃРѕСЃРµРґ РґРѕРїСѓСЃС‚РёРј,
       - РїСЂРё РѕС‚СЃСѓС‚СЃС‚РІРёРё РєРѕРЅС‚СЂРѕР»СЏ РёР»Рё "РЅРµ С‚РѕРј" РїРѕР»РѕР¶РµРЅРёРё СЃС‚СЂРµР»РєРё СЃРѕСЃРµРґ
         СЃС‡РёС‚Р°РµС‚СЃСЏ РЅРµРґРѕСЃС‚СѓРїРЅС‹Рј. РљРѕРЅРєСЂРµС‚РЅРѕРµ СѓРґРµСЂР¶Р°РЅРёРµ РїРѕ T_PK СЂРµР°Р»РёР·РѕРІР°РЅРѕ
         РІ UniversalTopologyManager (РїРѕ switch_id Рё required_state).

    Р’Рѕ РІСЃРµС… РѕСЃС‚Р°Р»СЊРЅС‹С… СЃР»СѓС‡Р°СЏС…:
       РµСЃР»Рё РЅР° РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјСѓСЋ СЃРµРєС†РёСЋ РЅРµС‚ С‚Р°РєРёС… СЃСЃС‹Р»РѕРє NextPl/NextMi
       СЃРѕ СЃРјРµР¶РЅС‹С… СЃРµРєС†РёР№ вЂ” PrevSec/NextSec РѕСЃС‚Р°СЋС‚СЃСЏ Р±РµР·СѓСЃР»РѕРІРЅС‹РјРё,
       РєР°Рє СЃРµР№С‡Р°СЃ: СЃРѕСЃРµРґ РІСЃРµРіРґР° Р±СѓРґРµС‚, РЅРµР·Р°РІРёСЃРёРјРѕ РѕС‚ СЃС‚СЂРµР»РѕРє.
    """
    name_to_id = _build_name_to_id()
    directions = _build_switch_directions_from_rc_sections(name_to_id)
    ctrl_deps = _build_ctrl_depend_on_neighbor_switch(name_to_id)

    rc_ids_set = set(GROUPS.get("rc_ids", []))

    # 1. РћР±С‹С‡РЅС‹Рµ СЃС‚СЂРµР»РѕС‡РЅС‹Рµ РЅР°РїСЂР°РІР»РµРЅРёСЏ (СЃС‚РІРѕР» -> РІРµС‚РІСЊ)
    for d in directions:
        stem = d.stem_rc_id
        branch = d.branch_rc_id
        sw_id = d.switch_id
        req = d.required_state
        stem_side = d.stem_side

        if stem not in rc_ids_set or branch not in rc_ids_set:
            # СЃС‚СЂРµР»РєР° РјРѕР¶РµС‚ СЃСЃС‹Р»Р°С‚СЊСЃСЏ РЅР° РѕР±СЉРµРєС‚С‹, РєРѕС‚РѕСЂС‹Рµ РЅРµ РІС…РѕРґСЏС‚ РІ rc_ids
            continue

        # stem -> branch С‡РµСЂРµР· sw_id, required_state
        # Р’РђР–РќРћ: Р·Р°РјРµРЅСЏРµРј Р±РµР·СѓСЃР»РѕРІРЅСѓСЋ СЃРІСЏР·СЊ РЅР° СЃС‚СЂРµР»РѕС‡РЅСѓСЋ, РµСЃР»Рё РѕРЅР° Р±С‹Р»Р°
        stem_links_attr = "next_links" if stem_side != "prev" else "prev_links"
        branch_links_attr = "prev_links" if stem_side != "prev" else "next_links"

        stem_node = rc_nodes.get(stem)
        if stem_node is not None:
            current_links = list(getattr(stem_node, stem_links_attr, []))
            new_links = []
            replaced = False
            for tid, sid, rstate in current_links:
                if tid == branch and (sid is None or rstate < 0):
                    new_links.append((branch, sw_id, req))
                    replaced = True
                else:
                    new_links.append((tid, sid, rstate))
            if not replaced:
                new_links.append((branch, sw_id, req))
            setattr(stem_node, stem_links_attr, new_links)

        branch_node = rc_nodes.get(branch)
        if branch_node is not None:
            current_links = list(getattr(branch_node, branch_links_attr, []))
            new_links = []
            replaced = False
            for tid, sid, rstate in current_links:
                if tid == stem and (sid is None or rstate < 0):
                    new_links.append((stem, sw_id, req))
                    replaced = True
                else:
                    new_links.append((tid, sid, rstate))
            if not replaced:
                new_links.append((stem, sw_id, req))
            setattr(branch_node, branch_links_attr, new_links)

    # 2. Р”Р»СЏ Р±РµСЃСЃС‚СЂРµР»РѕС‡РЅС‹С… РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹С… СЃРµРєС†РёР№ РїРµСЂРµСЃРѕР±РёСЂР°РµРј Р»РёРЅРµР№РЅС‹Рµ СЃРІСЏР·Рё,
    #    РµСЃР»Рё РѕРЅРё РґРѕР»Р¶РЅС‹ Р·Р°РІРёСЃРµС‚СЊ РѕС‚ СЃС‚СЂРµР»РѕРє СЃРѕСЃРµРґРµР№.
    for ctrl_id, deps in ctrl_deps.items():
        ctrl_node = rc_nodes.get(ctrl_id)
        if ctrl_node is None:
            continue

        # deps: СЃРїРёСЃРѕРє (neighbor_id, sw_id, required_state)
        # Р”Р»СЏ РєР°Р¶РґРѕР№ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РёС‰РµРј СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓСЋС‰РёС… Р»РёРЅРµР№РЅС‹С… СЃРѕСЃРµРґРµР№
        # Рё РґРѕРїРѕР»РЅСЏРµРј РёС… СЃС‚СЂРµР»РѕС‡РЅРѕР№ РёРЅС„РѕСЂРјР°С†РёРµР№.
        for neigh_id, sw_id, req in deps:
            # РћР±РЅРѕРІР»СЏРµРј prev_links: ctrl <- neigh
            new_prev: List[Tuple[str, Any, int]] = []
            for target_rc, sid, rstate in ctrl_node.prev_links:
                if target_rc == neigh_id and (sid is None or rstate < 0):
                    # Р›РёРЅРµР№РЅР°СЏ СЃРІСЏР·СЊ ctrl <- neigh СЃС‚Р°РЅРѕРІРёС‚СЃСЏ СЃС‚СЂРµР»РѕС‡РЅРѕ-Р·Р°РІРёСЃРёРјРѕР№
                    new_prev.append((target_rc, sw_id, req))
                else:
                    new_prev.append((target_rc, sid, rstate))
            ctrl_node.prev_links = new_prev

            # РћР±РЅРѕРІР»СЏРµРј next_links: ctrl -> neigh
            new_next: List[Tuple[str, Any, int]] = []
            for target_rc, sid, rstate in ctrl_node.next_links:
                if target_rc == neigh_id and (sid is None or rstate < 0):
                    # Р›РёРЅРµР№РЅР°СЏ СЃРІСЏР·СЊ ctrl -> neigh СЃС‚Р°РЅРѕРІРёС‚СЃСЏ СЃС‚СЂРµР»РѕС‡РЅРѕ-Р·Р°РІРёСЃРёРјРѕР№
                    new_next.append((target_rc, sw_id, req))
                else:
                    new_next.append((target_rc, sid, rstate))
            ctrl_node.next_links = new_next

            # --- Р’РђР–РќРћ: РЎРёРјРјРµС‚СЂРёС‡РЅРѕРµ РѕР±РЅРѕРІР»РµРЅРёРµ СЃРѕСЃРµРґР° (neigh) ---
            # Р•СЃР»Рё ctrl Р·Р°РІРёСЃРёС‚ РѕС‚ СЃС‚СЂРµР»РєРё sw_id, С‡С‚РѕР±С‹ РїРѕРїР°СЃС‚СЊ РІ neigh,
            # С‚Рѕ Рё neigh РґРѕР»Р¶РµРЅ Р·Р°РІРёСЃРµС‚СЊ РѕС‚ СЌС‚РѕР№ Р¶Рµ СЃС‚СЂРµР»РєРё, С‡С‚РѕР±С‹ РїРѕРїР°СЃС‚СЊ РІ ctrl.
            neigh_node = rc_nodes.get(neigh_id)
            if neigh_node:
                # РћР±РЅРѕРІР»СЏРµРј prev_links Сѓ СЃРѕСЃРµРґР°: neigh <- ctrl
                new_prev_neigh = []
                for tid, sid, rstate in neigh_node.prev_links:
                    if tid == ctrl_id and (sid is None or rstate < 0):
                        new_prev_neigh.append((tid, sw_id, req))
                    else:
                        new_prev_neigh.append((tid, sid, rstate))
                neigh_node.prev_links = new_prev_neigh

                # РћР±РЅРѕРІР»СЏРµРј next_links Сѓ СЃРѕСЃРµРґР°: neigh -> ctrl
                new_next_neigh = []
                for tid, sid, rstate in neigh_node.next_links:
                    if tid == ctrl_id and (sid is None or rstate < 0):
                        new_next_neigh.append((tid, sw_id, req))
                    else:
                        new_next_neigh.append((tid, sid, rstate))
                neigh_node.next_links = new_next_neigh

    # 3. Р”Р»СЏ РІСЃРµС… Р Р¦ СЃРѕ СЃС‚СЂРµР»РєР°РјРё РіР°СЂР°РЅС‚РёСЂСѓРµРј, С‡С‚Рѕ Р›РРќР•Р™РќР«Р• СЃРІСЏР·Рё (PrevSec/NextSec)
    #    С‚РѕР¶Рµ Р·Р°РІРёСЃСЏС‚ РѕС‚ РєРѕРЅС‚СЂРѕР»СЏ СЃС‚СЂРµР»РѕРє СЌС‚РѕР№ СЃРµРєС†РёРё (С…РѕС‚СЏ Р±С‹ РѕРґРЅРѕР№ "РєРѕСЂРЅРµРІРѕР№").
    #    Р­С‚Рѕ РїРѕРєСЂС‹РІР°РµС‚ Stem-СЃС‚РѕСЂРѕРЅС‹.
    for rc_id, node in rc_nodes.items():
        # Р‘РµСЂРµРј РґР°РЅРЅС‹Рµ РёР· RC_SECTIONS РїРѕ ID
        rc_name_raw = next((v.get('name') for k, v in NODES.items() if k == rc_id), None)
        if not rc_name_raw:
            continue
        
        sec_data = RC_SECTIONS.get(rc_name_raw)
        if not sec_data:
            continue
            
        switches = sec_data.get("Switches") or []
        if not switches:
            continue
            
        # РќР°С…РѕРґРёРј "РєРѕСЂРЅРµРІСѓСЋ" СЃС‚СЂРµР»РєСѓ (Сѓ РєРѕС‚РѕСЂРѕР№ РЅРµС‚ PrevSw РЅР° СЌС‚РѕР№ Р¶Рµ СЃРµРєС†РёРё)
        root_sw_id = None
        for sw in switches:
            if not sw.get("PrevSw"):
                sw_name = sw.get("name")
                root_sw_id = name_to_id.get(sw_name)
                break
        
        if not root_sw_id and switches:
            # fallback: Р»СЋР±Р°СЏ РёР· СЃРµРєС†РёРё
            root_sw_id = name_to_id.get(switches[0].get("name"))
            
        if not root_sw_id:
            continue

        # РџСЂРµРІСЂР°С‰Р°РµРј РѕСЃС‚Р°РІС€РёРµСЃСЏ Р±РµР·СѓСЃР»РѕРІРЅС‹Рµ СЃРІСЏР·Рё РІ Р·Р°РІРёСЃРёРјС‹Рµ РѕС‚ root_sw_id (req=-1)
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


# -*- coding: utf-8 -*-
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass

from station.station_model import StationModel
from core.uni_states import sw_no_control  # РѕР±С‰РёР№ РєСЂРёС‚РµСЂРёР№ "СЃС‚СЂРµР»РєР° Р±РµР· РєРѕРЅС‚СЂРѕР»СЏ"


@dataclass
class TopologyState:
    """
    РџР°РјСЏС‚СЊ С‚РѕРїРѕР»РѕРіРёРё РґР»СЏ РєРѕРЅРєСЂРµС‚РЅРѕР№ Р Р¦.
    РЈРґРµСЂР¶РёРІР°РµС‚ СЃРѕСЃРµРґР° РїСЂРё РІСЂРµРјРµРЅРЅРѕР№ РїРѕС‚РµСЂРµ РєРѕРЅС‚СЂРѕР»СЏ СЃС‚СЂРµР»РѕРє (T_PK).
    """
    rc_id: str
    latched_prev: str = ""
    latched_next: str = ""
    time_since_prev_lost: Optional[float] = None
    time_since_next_lost: Optional[float] = None


class UniversalTopologyManager:
    """
    РЈРЅРёРІРµСЂСЃР°Р»СЊРЅС‹Р№ РјРµРЅРµРґР¶РµСЂ С‚РѕРїРѕР»РѕРіРёРё.

    Р Р°Р±РѕС‚Р°РµС‚ РїРѕРІРµСЂС… StationModel.rc_nodes, РіРґРµ СЃРІСЏР·Рё Р·Р°РґР°РЅС‹ РєР°Рє
      (neighbor_rc_id, switch_id, required_state):

    - СЃРІСЏР·Рё Р±РµР· СЃС‚СЂРµР»РєРё (switch_id is None РёР»Рё required_state < 0) СЃС‡РёС‚Р°СЋС‚СЃСЏ
      Р±РµР·СѓСЃР»РѕРІРЅС‹РјРё: СЃРѕСЃРµРґ РІСЃРµРіРґР° РґРѕСЃС‚СѓРїРµРЅ (Р»РёРЅРµР№РЅР°СЏ С‚РѕРїРѕР»РѕРіРёСЏ);

    - СЃС‚СЂРµР»РѕС‡РЅРѕ-Р·Р°РІРёСЃРёРјС‹Рµ СЃРІСЏР·Рё (switch_id Р·Р°РґР°РЅ) Р°РєС‚РёРІРёСЂСѓСЋС‚СЃСЏ С‚РѕР»СЊРєРѕ РїСЂРё
      РЅР°Р»РёС‡РёРё РєРѕРЅС‚СЂРѕР»СЏ СЃС‚СЂРµР»РєРё Рё С‚СЂРµР±СѓРµРјРѕРіРѕ РїРѕР»РѕР¶РµРЅРёСЏ (plus/minus);

    - РїСЂРё РїРѕС‚РµСЂРµ РєРѕРЅС‚СЂРѕР»СЏ СЃС‚СЂРµР»РєРё РёСЃРїРѕР»СЊР·СѓРµРј РјРµС…Р°РЅРёР·Рј СѓРґРµСЂР¶Р°РЅРёСЏ (latch) РґРѕ T_PK:
      РµСЃР»Рё С„РёР·РёС‡РµСЃРєРёР№ СЃРѕСЃРµРґ РІСЂРµРјРµРЅРЅРѕ РЅРµ РѕРїСЂРµРґРµР»СЏРµС‚СЃСЏ, РѕСЃС‚Р°С‘С‚СЃСЏ latched_*,
      РїРѕРєР° РЅРµ РёСЃС‚РµС‡С‘С‚ T_PK; РїРѕСЃР»Рµ T_PK СЃРѕСЃРµРґ СЃС‡РёС‚Р°РµС‚СЃСЏ РЅРµРґРѕСЃС‚СѓРїРЅС‹Рј.

    Р›РѕРіРёРєР° С‚РѕРіРѕ, РєР°РєРёРµ СЃРІСЏР·Рё РґРѕР»Р¶РЅС‹ Р±С‹С‚СЊ СЃС‚СЂРµР»РѕС‡РЅРѕ-Р·Р°РІРёСЃРёРјС‹РјРё (РІ С‚РѕРј С‡РёСЃР»Рµ РґР»СЏ
    Р±РµСЃСЃС‚СЂРµР»РѕС‡РЅС‹С… РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹С… СЃРµРєС†РёР№ С‡РµСЂРµР· NextMi/NextPl СЃРѕСЃРµРґРµР№),
    Р·Р°РґР°С‘С‚СЃСЏ РЅР° СѓСЂРѕРІРЅРµ apply_switch_topology_rules.
    """

    def __init__(self, model: StationModel, t_pk: float = 30.0):
        self.model = model
        self.T_PK = t_pk
        self.states: Dict[str, TopologyState] = {
            rc_id: TopologyState(rc_id) for rc_id in model.rc_nodes.keys()
        }

    # --- РќРѕРІС‹Р№ СѓСЂРѕРІРµРЅСЊ: СЃРѕСЃРµРґРё + РєРѕРЅС‚СЂРѕР»СЊ ---

    def get_neighbors_with_control(
        self,
        rc_id: str,
        switch_states: Dict[str, int],
        dt: float,
    ) -> Tuple[str, str, bool, bool, bool, bool]:
        """
        Р’РѕР·РІСЂР°С‰Р°РµС‚ (prev_rc_id, next_rc_id, prev_control_ok, next_control_ok, prev_nc, next_nc)
        РґР»СЏ СѓРєР°Р·Р°РЅРЅРѕР№ Р Р¦.

        prev_nc/next_nc: True, РµСЃР»Рё РІ РґР°РЅРЅРѕРј РЅР°РїСЂР°РІР»РµРЅРёРё РЅРµС‚ СЃРІСЏР·РµР№ (С‚СѓРїРёРє/РіСЂР°РЅРёС†Р° РјРѕРґРµР»Рё).
        """
        prev_rc, next_rc = self.get_active_neighbors(rc_id, switch_states, dt)
        
        node = self.model.rc_nodes.get(rc_id)
        prev_nc = len(node.prev_links) == 0 if node else False
        next_nc = len(node.next_links) == 0 if node else False

        prev_ok = bool(prev_rc)
        next_ok = bool(next_rc)

        return prev_rc, next_rc, prev_ok, next_ok, prev_nc, next_nc

    # --- РЎС‚Р°СЂС‹Р№ РёРЅС‚РµСЂС„РµР№СЃ: РѕСЃС‚Р°РІР»СЏРµРј РєР°Рє РµСЃС‚СЊ РґР»СЏ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё ---

    def get_active_neighbors(
        self,
        rc_id: str,
        switch_states: Dict[str, int],
        dt: float,
    ) -> Tuple[str, str]:
        """
        Р’РѕР·РІСЂР°С‰Р°РµС‚ (prev_rc_id, next_rc_id) РґР»СЏ СѓРєР°Р·Р°РЅРЅРѕР№ Р Р¦.

        switch_states: { 'SwID': Uni_State_ID }.

        Р›РѕРіРёРєР°:
        1. РџРѕ RcNode.prev_links/next_links РёС‰РµРј С„РёР·РёС‡РµСЃРєРѕРіРѕ СЃРѕСЃРµРґР°:
           - Р±РµР· СЃС‚СЂРµР»РєРё в†’ СЃРІСЏР·СЊ Р±РµР·СѓСЃР»РѕРІРЅР° (neighbor_rc_id, None, req<0),
             СЃРѕСЃРµРґ СЃС‡РёС‚Р°РµС‚СЃСЏ РІСЃРµРіРґР° РґРѕСЃС‚СѓРїРЅС‹Рј;
           - СЃ СЃС‚СЂРµР»РєРѕР№ в†’ СЃРјРѕС‚СЂРёРј Uni_State_ID:
             * РµСЃР»Рё sw_no_control(...) в†’ РєРѕРЅС‚СЂРѕР»СЏ РЅРµС‚, С„РёР·РёС‡РµСЃРєРёР№ СЃРѕСЃРµРґ
               РЅРµРёР·РІРµСЃС‚РµРЅ РЅР° СЌС‚РѕРј С€Р°РіРµ;
             * РµСЃР»Рё РµСЃС‚СЊ РІР°Р»РёРґРЅС‹Р№ СЃС‚РµР№С‚ Рё РѕРЅ СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓРµС‚ required_state в†’
               СЃРѕСЃРµРґ Р°РєС‚РёРІРµРЅ.
        2. Р•СЃР»Рё С„РёР·РёС‡РµСЃРєРёР№ СЃРѕСЃРµРґ РЅРµРёР·РІРµСЃС‚РµРЅ, РёСЃРїРѕР»СЊР·СѓРµРј latched-Р·РЅР°С‡РµРЅРёРµ
           РЅРµ РґРѕР»СЊС€Рµ T_PK.
        3. РџСЂРё РІРѕСЃСЃС‚Р°РЅРѕРІР»РµРЅРёРё РєРѕРЅС‚СЂРѕР»СЏ (Р»СЋР±РѕР№ РІР°Р»РёРґРЅС‹Р№ СЃС‚РµР№С‚ в†’ РїРѕСЏРІР»СЏРµС‚СЃСЏ
           current_phys) latch РѕР±РЅРѕРІР»СЏРµС‚СЃСЏ, РІСЂРµРјСЏ СЃР±СЂР°СЃС‹РІР°РµС‚СЃСЏ.

        РљР°РєРёРµ РёРјРµРЅРЅРѕ СЃРІСЏР·Рё Р·Р°РІРёСЃСЏС‚ РѕС‚ СЃС‚СЂРµР»РѕРє (РІРєР»СЋС‡Р°СЏ СЃР»СѓС‡Р°Р№, РєРѕРіРґР°
        Р±РµСЃСЃС‚СЂРµР»РѕС‡РЅР°СЏ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјР°СЏ СЃРµРєС†РёСЏ Р·Р°РІРёСЃРёС‚ РѕС‚ СЃС‚СЂРµР»РѕРє РЅР° СЃРѕСЃРµРґСЏС…
        С‡РµСЂРµР· NextMi/NextPl), СѓР¶Рµ СЂРµС€РµРЅРѕ РЅР° СЌС‚Р°РїРµ apply_switch_topology_rules.
        """
        node = self.model.rc_nodes.get(rc_id)
        state = self.states.get(rc_id)

        if not node or not state:
            return "", ""

        current_prev_phys = self._find_phys_neighbor(node.prev_links, switch_states)
        current_next_phys = self._find_phys_neighbor(node.next_links, switch_states)

        # РћРїСЂРµРґРµР»СЏРµРј, РµСЃС‚СЊ Р»Рё РїРѕС‚РµСЂСЏ РєРѕРЅС‚СЂРѕР»СЏ РґР»СЏ prev/next
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

    def get_next_topology_change_dt(
        self,
        rc_id: str,
        switch_states: Dict[str, int],
        max_dt: float,
    ) -> Optional[float]:
        """
        Возвращает ближайший момент внутри [0, max_dt), когда latch-сосед
        перестанет действовать из-за истечения T_PK.
        """
        if max_dt <= 0.0:
            return None

        node = self.model.rc_nodes.get(rc_id)
        state = self.states.get(rc_id)
        if not node or not state:
            return None

        candidates: List[float] = []
        candidates.extend(
            self._get_side_expire_candidates(
                links=node.prev_links,
                switch_states=switch_states,
                latched_val=state.latched_prev,
                time_val=state.time_since_prev_lost,
                max_dt=max_dt,
            )
        )
        candidates.extend(
            self._get_side_expire_candidates(
                links=node.next_links,
                switch_states=switch_states,
                latched_val=state.latched_next,
                time_val=state.time_since_next_lost,
                max_dt=max_dt,
            )
        )
        if not candidates:
            return None
        return min(candidates)

    # ---------- Р’СЃРїРѕРјРѕРіР°С‚РµР»СЊРЅС‹Рµ РјРµС‚РѕРґС‹ ----------

    def _find_phys_neighbor(
        self,
        links: List[Tuple[str, Optional[str], int]],
        switch_states: Dict[str, int],
    ) -> str:
        """
        РџРѕРёСЃРє С„РёР·РёС‡РµСЃРєРѕРіРѕ СЃРѕСЃРµРґР° РїРѕ СЃРїРёСЃРєСѓ СЃРІСЏР·РµР№.

        links: [(target_rc_id, switch_id | None, required_state), ...]
        switch_states: { 'SwID': Uni_State_ID }.

        required_state:
        - 1 в†’ СЃС‚СЂРµР»РєР° РґРѕР»Р¶РЅР° Р±С‹С‚СЊ РІ РїР»СЋСЃРµ (sw_is_plus);
        - 0 в†’ РІ РјРёРЅСѓСЃРµ (sw_is_minus);
        - required_state < 0 РёР»Рё switch_id is None в†’ Р±РµР·СѓСЃР»РѕРІРЅР°СЏ СЃРІСЏР·СЊ,
          РЅРµ Р·Р°РІРёСЃСЏС‰Р°СЏ РѕС‚ РєРѕРЅС‚СЂРѕР»СЏ СЃС‚СЂРµР»РєРё.

        Р’Р°Р¶РЅС‹Р№ РјРѕРјРµРЅС‚:
        - РµСЃР»Рё РґР»СЏ РѕРґРЅРѕРіРѕ Рё С‚РѕРіРѕ Р¶Рµ target_rc_id РµСЃС‚СЊ РЅРµСЃРєРѕР»СЊРєРѕ
          СЃС‚СЂРµР»РѕС‡РЅС‹С… СѓСЃР»РѕРІРёР№, СЃС‡РёС‚Р°РµРј СЃРѕСЃРµРґР° РґРѕСЃС‚СѓРїРЅС‹Рј С‚РѕР»СЊРєРѕ РµСЃР»Рё
          Р’РЎР• СЌС‚Рё СѓСЃР»РѕРІРёСЏ РІС‹РїРѕР»РЅРµРЅС‹ (Р»РѕРіРёС‡РµСЃРєРѕРµ AND РїРѕ СЃС‚СЂРµР»РєР°Рј).
        """
        from core.uni_states import sw_is_plus, sw_is_minus  # Р»РѕРєР°Р»СЊРЅС‹Р№ РёРјРїРѕСЂС‚

        # РЎРЅР°С‡Р°Р»Р° Р±С‹СЃС‚СЂС‹Р№ РїСѓС‚СЊ: Р±РµР·СѓСЃР»РѕРІРЅС‹Рµ СЃРІСЏР·Рё (РІРѕРѕР±С‰Рµ Р±РµР· SwID)
        for target_rc, sw_id, required_state in links:
            if sw_id is None or required_state < 0:
                return target_rc

        # Р“СЂСѓРїРїРёСЂСѓРµРј СЃС‚СЂРµР»РѕС‡РЅС‹Рµ СЃРІСЏР·Рё РїРѕ target_rc
        by_target: Dict[str, List[Tuple[Optional[str], int]]] = {}
        for target_rc, sw_id, required_state in links:
            if sw_id is None or required_state < 0:
                # Р±РµР·СѓСЃР»РѕРІРЅС‹Рµ СѓР¶Рµ РѕР±СЂР°Р±РѕС‚Р°Р»Рё РІС‹С€Рµ
                continue
            by_target.setdefault(target_rc, []).append((sw_id, required_state))

        # Р”Р»СЏ РєР°Р¶РґРѕРіРѕ РєР°РЅРґРёРґР°С‚Р°-СЃРѕСЃРµРґР° РїСЂРѕРІРµСЂСЏРµРј РІСЃРµ РµРіРѕ СЃС‚СЂРµР»РєРё
        for target_rc, conds in by_target.items():
            all_ok = True
            for sw_id, required_state in conds:
                uni_state_id = switch_states.get(sw_id)
                # РќРµС‚ Р·Р°РїРёСЃРё РёР»Рё СЃС‚СЂРµР»РєР° Р±РµР· РєРѕРЅС‚СЂРѕР»СЏ в†’ СЃРѕСЃРµРґ РЅРµРґРѕСЃС‚СѓРїРµРЅ
                if uni_state_id is None or sw_no_control(uni_state_id):
                    all_ok = False
                    break
                # РџСЂРѕРІРµСЂСЏРµРј С‚СЂРµР±СѓРµРјРѕРµ РїРѕР»РѕР¶РµРЅРёРµ (С‚РѕР»СЊРєРѕ РµСЃР»Рё РѕРЅРѕ Р·Р°РґР°РЅРѕ >= 0)
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
        РџСЂРѕРІРµСЂСЏРµС‚, РµСЃС‚СЊ Р»Рё РїРѕС‚РµСЂСЏ РєРѕРЅС‚СЂРѕР»СЏ РґР»СЏ РґР°РЅРЅРѕРіРѕ РЅР°Р±РѕСЂР° СЃРІСЏР·РµР№.
        """
        # Р•СЃР»Рё РµСЃС‚СЊ Р±РµР·СѓСЃР»РѕРІРЅС‹Рµ СЃРІСЏР·Рё (РІРѕРѕР±С‰Рµ Р±РµР· SwID) вЂ” РєРѕРЅС‚СЂРѕР»СЊ РЅРµ С‚РµСЂСЏРµС‚СЃСЏ
        for target_rc, sw_id, required_state in links:
            if sw_id is None or required_state < 0:
                return False
        
        # РџСЂРѕРІРµСЂСЏРµРј СЃС‚СЂРµР»РѕС‡РЅС‹Рµ СЃРІСЏР·Рё
        for target_rc, sw_id, required_state in links:
            if sw_id is not None:
                uni_state_id = switch_states.get(sw_id)
                if uni_state_id is not None and sw_no_control(uni_state_id):
                    return True  # РџРѕС‚РµСЂСЏ РєРѕРЅС‚СЂРѕР»СЏ!
        
        # РЎС‚СЂРµР»РєРё РїРѕРґ РєРѕРЅС‚СЂРѕР»РµРј, РЅРѕ СЃРІСЏР·Рё РЅРµР°РєС‚РёРІРЅС‹ (СЃРјРµРЅР° РїРѕР»РѕР¶РµРЅРёСЏ)
        return False

    def _get_side_expire_candidates(
        self,
        links: List[Tuple[str, Optional[str], int]],
        switch_states: Dict[str, int],
        latched_val: str,
        time_val: Optional[float],
        max_dt: float,
    ) -> List[float]:
        """
        Возвращает момент(ы) истечения latch для одной стороны.
        """
        if not latched_val:
            return []

        current_phys = self._find_phys_neighbor(links, switch_states)
        is_control_lost = self._is_control_lost_for_links(links, switch_states)
        if current_phys or not is_control_lost:
            return []

        elapsed = float(time_val or 0.0)
        remaining = self.T_PK - elapsed
        if 0.0 < remaining < max_dt:
            return [remaining]
        return []

    def _resolve_with_latch(
        self,
        current_phys: str,
        is_control_lost: bool,  # в†ђ РќРћР’Р«Р™ РџРђР РђРњР•РўР !
        state_attr: str,
        time_attr: str,
        state: TopologyState,
        dt: float,
    ) -> str:
        latched_val = getattr(state, state_attr)
        time_val = getattr(state, time_attr)

        if current_phys:
            # Р’РѕСЃСЃС‚Р°РЅРѕРІР»РµРЅРёРµ вЂ” РѕР±РЅРѕРІР»СЏРµРј latch
            setattr(state, state_attr, current_phys)
            setattr(state, time_attr, 0.0)
            return current_phys

        # current_phys == ""
        if is_control_lost and latched_val:
            # РџРѕС‚РµСЂСЏ РєРѕРЅС‚СЂРѕР»СЏ вЂ” РёСЃРїРѕР»СЊР·СѓРµРј latch
            new_time = (time_val or 0.0) + dt
            setattr(state, time_attr, new_time)
            if new_time <= self.T_PK:
                return latched_val
            # T_PK РёСЃС‚С‘Рє вЂ” СЃР±СЂР°СЃС‹РІР°РµРј
            setattr(state, state_attr, "")
            setattr(state, time_attr, None)
            return ""
        else:
            # РЎС‚СЂРµР»РєР° РїРѕРґ РєРѕРЅС‚СЂРѕР»РµРј, РЅРѕ СЃРІСЏР·СЊ РЅРµР°РєС‚РёРІРЅР° (СЃРјРµРЅР° РїРѕР»РѕР¶РµРЅРёСЏ)
            # РЎР±СЂР°СЃС‹РІР°РµРј latch!
            setattr(state, state_attr, "")
            setattr(state, time_attr, None)
            return ""


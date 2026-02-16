# -*- coding: utf-8 -*-
from typing import Any, Tuple, Optional
from core.base_detector import CompletionMode
from core.variants_common import get_mask_by_id, rc_is_free, rc_is_occupied

class TimingDetectorLZ9:
    """
    РЎРїРµС†РёР°Р»РёР·РёСЂРѕРІР°РЅРЅС‹Р№ РґРµС‚РµРєС‚РѕСЂ РґР»СЏ LZ9 (РџСЂРѕР±РѕР№ СЃС‚С‹РєР°).
    Р’РјРµСЃС‚Рѕ Р¶РµСЃС‚РєРёС… С„Р°Р· РёСЃРїРѕР»СЊР·СѓРµС‚ Р·Р°РјРµСЂ РІСЂРµРјРµРЅРё РјРµР¶РґСѓ СЃРѕР±С‹С‚РёСЏРјРё Р·Р°РЅСЏС‚РёСЏ.
    
    Р›РѕРіРёРєР°:
    1. Phase 0 (Given): РћР¶РёРґР°РЅРёРµ 0-0-0 (РёР»Рё NC) РІ С‚РµС‡РµРЅРёРµ ts01_lz9.
    2. Phase 1 (Wait): РћР¶РёРґР°РЅРёРµ РЅР°С‡Р°Р»Р° Р·Р°РЅСЏС‚РёСЏ С†РµРЅС‚СЂР° РёР»Рё СЃРѕСЃРµРґР°.
    3. РћС‚РєСЂС‹С‚РёРµ: Р•СЃР»Рё РѕР±Р° Р·Р°РЅСЏР»РёСЃСЊ СЃ СЂР°Р·РЅРёС†РµР№ <= tlz_lz9.
    """
    def __init__(
        self,
        ctrl_rc_id: str,
        ts01_lz9: float,
        tlz_lz9: float,
        t_kon: float,
    ) -> None:
        self.ctrl_rc_id = ctrl_rc_id
        self.ts01_lz9 = ts01_lz9
        self.tlz_lz9 = tlz_lz9
        self.t_kon = t_kon
        
        # РњР°СЃРєРё
        self.mask_given = get_mask_by_id(32)
        self.mask_ctrl_occ = get_mask_by_id(33)
        self.mask_adj_occ = get_mask_by_id(34)
        self.mask_both_occ = get_mask_by_id(35)
        self.mask_prev_occ = get_mask_by_id(36)
        self.mask_next_occ = get_mask_by_id(37)
        
        self.reset()

    def reset(self):
        self.phase = "given"
        self.timer = 0.0
        self.active = False
        self.t_ctrl_occ: Optional[float] = None
        self.t_adj_occ: Optional[float] = None
        self.global_time = 0.0

    def update(self, step: Any, dt: float) -> Tuple[bool, bool]:
        self.global_time += dt
        opened = False
        closed = False
        
        # РџРѕР»СѓС‡Р°РµРј СЌС„С„РµРєС‚РёРІРЅС‹С… СЃРѕСЃРµРґРµР№
        prev = getattr(step, "effective_prev_rc", None)
        ctrl = self.ctrl_rc_id
        nxt = getattr(step, "effective_next_rc", None)

        if not self.active:
            if self.phase == "given":
                res = self.mask_given(step, prev, ctrl, nxt)
                if res:
                    self.timer += dt
                    if self.timer >= self.ts01_lz9:
                        self.phase = "wait"
                        self.timer = 0.0
                else:
                    self.timer = 0.0
            
            elif self.phase == "wait":
                # Р¤РёРєСЃРёСЂСѓРµРј РІСЂРµРјСЏ РїРµСЂРІРѕРіРѕ Р·Р°РЅСЏС‚РёСЏ
                if self.t_ctrl_occ is None and rc_is_occupied(step.rc_states.get(ctrl, 0)):
                    self.t_ctrl_occ = self.global_time
                
                # РЇРІРЅРѕ РїРѕРєСЂС‹РІР°РµРј РѕР±Р° РЅР°РїСЂР°РІР»РµРЅРёСЏ + Р°РіСЂРµРіРёСЂРѕРІР°РЅРЅСѓСЋ РјР°СЃРєСѓ.
                is_adj_occ = (
                    self.mask_adj_occ(step, prev, ctrl, nxt)
                    or self.mask_both_occ(step, prev, ctrl, nxt)
                    or self.mask_prev_occ(step, prev, ctrl, nxt)
                    or self.mask_next_occ(step, prev, ctrl, nxt)
                )
                if self.t_adj_occ is None and is_adj_occ:
                    self.t_adj_occ = self.global_time
                
                # Р•СЃР»Рё РѕР±Р° Р·Р°РЅСЏР»РёСЃСЊ, РїСЂРѕРІРµСЂСЏРµРј РґРµР»СЊС‚Сѓ
                if self.t_ctrl_occ is not None and self.t_adj_occ is not None:
                    delta = abs(self.t_ctrl_occ - self.t_adj_occ)
                    if delta <= self.tlz_lz9:
                        opened = True
                        self.active = True
                        self.phase = "active"
                        self.timer = 0.0
                    else:
                        pass
                
                # Р•СЃР»Рё РїСЂРѕС€Р»Рѕ СЃР»РёС€РєРѕРј РјРЅРѕРіРѕ РІСЂРµРјРµРЅРё СЃ РїРµСЂРІРѕРіРѕ СЃРѕР±С‹С‚РёСЏ, СЃР±СЂР°СЃС‹РІР°РµРј РѕР¶РёРґР°РЅРёРµ
                first_t = self.t_ctrl_occ or self.t_adj_occ
                if first_t is not None and (self.global_time - first_t) > self.tlz_lz9:
                    # РћРєРЅРѕ Р·Р°С…Р»РѕРїРЅСѓР»РѕСЃСЊ, СЃР±СЂРѕСЃ Рє idle (РЅРѕ РµСЃР»Рё РІСЃРµ РµС‰Рµ Given, РјРѕР¶РЅРѕ РІ Given)
                    self.t_ctrl_occ = None
                    self.t_adj_occ = None
                    self.phase = "given" # Р’РѕР·РІСЂР°С‚ Рє РїСЂРѕРІРµСЂРєРµ Р”Р°РЅРѕ

        else:
            # РђРєС‚РёРІРµРЅ. Р—Р°РІРµСЂС€РµРЅРёРµ РїРѕ Рў_РљРћРќ (СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ С†РµРЅС‚СЂР°)
            st_ctrl = step.rc_states.get(ctrl, 0)
            if rc_is_free(st_ctrl):
                self.timer += dt
                if self.timer >= self.t_kon:
                    closed = True
                    self.reset()
            else:
                self.timer = 0.0
                
        return opened, closed

def make_lz9_detector(
    ctrl_rc_id: str,
    ts01_lz9: float,
    tlz_lz9: float,
    t_kon: float,
) -> TimingDetectorLZ9:
    return TimingDetectorLZ9(ctrl_rc_id, ts01_lz9, tlz_lz9, t_kon)



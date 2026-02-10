# -*- coding: utf-8 -*-
from typing import Any, Tuple, Optional
from base_detector import CompletionMode
from variants_common import get_mask_by_id, rc_is_free, rc_is_occupied

class TimingDetectorLZ9:
    """
    Специализированный детектор для LZ9 (Пробой стыка).
    Вместо жестких фаз использует замер времени между событиями занятия.
    
    Логика:
    1. Phase 0 (Given): Ожидание 0-0-0 (или NC) в течение ts01_lz9.
    2. Phase 1 (Wait): Ожидание начала занятия центра или соседа.
    3. Открытие: Если оба занялись с разницей <= tlz_lz9.
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
        
        # Маски
        self.mask_given = get_mask_by_id(900)
        self.mask_ctrl_occ = get_mask_by_id(901)
        self.mask_adj_occ = get_mask_by_id(902)
        self.mask_both_occ = get_mask_by_id(903)
        
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
        
        # Получаем эффективных соседей
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
                # Фиксируем время первого занятия
                if self.t_ctrl_occ is None and rc_is_occupied(step.rc_states.get(ctrl, 0)):
                    self.t_ctrl_occ = self.global_time
                
                # any_adj_occ проверяем через маски 902 или 903
                is_adj_occ = self.mask_adj_occ(step, prev, ctrl, nxt) or self.mask_both_occ(step, prev, ctrl, nxt)
                if self.t_adj_occ is None and is_adj_occ:
                    self.t_adj_occ = self.global_time
                
                # Если оба занялись, проверяем дельту
                if self.t_ctrl_occ is not None and self.t_adj_occ is not None:
                    delta = abs(self.t_ctrl_occ - self.t_adj_occ)
                    if delta <= self.tlz_lz9:
                        opened = True
                        self.active = True
                        self.phase = "active"
                        self.timer = 0.0
                    else:
                        pass
                
                # Если прошло слишком много времени с первого события, сбрасываем ожидание
                first_t = self.t_ctrl_occ or self.t_adj_occ
                if first_t is not None and (self.global_time - first_t) > self.tlz_lz9:
                    # Окно захлопнулось, сброс к idle (но если все еще Given, можно в Given)
                    self.t_ctrl_occ = None
                    self.t_adj_occ = None
                    self.phase = "given" # Возврат к проверке Дано

        else:
            # Активен. Завершение по Т_КОН (свободность центра)
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

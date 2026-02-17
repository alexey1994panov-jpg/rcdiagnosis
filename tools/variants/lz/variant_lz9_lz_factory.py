# -*- coding: utf-8 -*-
from typing import Any, Optional, Tuple

from core.base_detector import CompletionMode
from core.variants_common import (
    mask_rc_0_0l_0,
    mask_rc_ctrl_0_adj_occ,
    mask_rc_ctrl_1_adj_free_or_nc,
    mask_rc_ctrl_1_adj_occ,
    mask_rc_ctrl_1_next_occ,
    mask_rc_ctrl_1_prev_occ,
    rc_is_free,
    rc_is_occupied,
)


class TimingDetectorLZ9:
    """
    Специализированный детектор для LZ9 (пробой стыка).

    Логика:
    1. Фаза given: ожидание базового условия (контролируемая свободна, смежные свободны/NC)
       в течение ts01_lz9.
    2. Фаза wait: фиксация времени занятия контролируемой и смежной РЦ.
    3. Открытие: если оба события произошли в окне |dt| <= tlz_lz9.
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

        # Маски (явные канонические ссылки)
        self.mask_given = mask_rc_0_0l_0
        self.mask_ctrl_occ = mask_rc_ctrl_1_adj_free_or_nc
        self.mask_adj_occ = mask_rc_ctrl_0_adj_occ
        self.mask_both_occ = mask_rc_ctrl_1_adj_occ
        self.mask_prev_occ = mask_rc_ctrl_1_prev_occ
        self.mask_next_occ = mask_rc_ctrl_1_next_occ

        self.reset()

    def reset(self) -> None:
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
                # Фиксируем время занятия контролируемой РЦ
                if self.t_ctrl_occ is None and rc_is_occupied(step.rc_states.get(ctrl, 0)):
                    self.t_ctrl_occ = self.global_time

                # Проверяем занятие смежной РЦ по всем допустимым условиям
                is_adj_occ = (
                    self.mask_adj_occ(step, prev, ctrl, nxt)
                    or self.mask_both_occ(step, prev, ctrl, nxt)
                    or self.mask_prev_occ(step, prev, ctrl, nxt)
                    or self.mask_next_occ(step, prev, ctrl, nxt)
                )
                if self.t_adj_occ is None and is_adj_occ:
                    self.t_adj_occ = self.global_time

                # Проверка окна синхронности
                if self.t_ctrl_occ is not None and self.t_adj_occ is not None:
                    delta = abs(self.t_ctrl_occ - self.t_adj_occ)
                    if delta <= self.tlz_lz9:
                        opened = True
                        self.active = True
                        self.phase = "active"
                        self.timer = 0.0

                # Если второе событие не пришло в окно, возвращаемся к given
                first_t = self.t_ctrl_occ or self.t_adj_occ
                if first_t is not None and (self.global_time - first_t) > self.tlz_lz9:
                    self.t_ctrl_occ = None
                    self.t_adj_occ = None
                    self.phase = "given"

        else:
            # Завершение по t_kon: контролируемая должна быть свободна непрерывно
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

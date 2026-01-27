from typing import Any, Tuple

from ..station_visochino_1p import (
    rc_is_free,
    rc_is_occupied,
    rc_is_locked,
    rc_no_control,          # ДОБАВИТЬ импорт
    signal_is_open,
    signal_is_shunting,
    signal_is_closed,
    shunting_signal_is_closed,
)


class VariantLS6Detector:
    """
    Вариант 6 ЛС.

    Топология prev/curr/next и признаки NC берутся из общей логики станции:
      modes["<ctrl>_prev_state"], modes["<ctrl>_next_state"],
      modes["<ctrl>_prev_nc"],    modes["<ctrl>_next_nc"],
    которые заполняются compute_local_adjacency в simulate_1p,
    как для варианта 12 ЛЗ.

    Светофоры задаются, как в варианте 4 ЛЗ:
      - signal_prev_to_ctrl_id — светофор между prev и ctrl,
      - signal_ctrl_to_next_id — светофор между ctrl и next,
        поездной или маневровый в зависимости от ctrl_to_next_is_shunting.

    Ветка 6.1 (предыдущая не контролируется):
      ДАНО:  prev NC, curr свободна и замкнута, next свободна и замкнута,
             светофор prev->ctrl открыт (разрешающее показание) не менее T_S0106.
      КОГДА: prev NC, curr свободна и замкнута, next занята и замкнута
             не менее T_LS06 (сигнал не учитывается).

    Ветка 6.2 (следующая не контролируется):
      ДАНО:  prev свободна и замкнута, curr свободна и замкнута, next NC,
             светофор ctrl->next открыт (поездное или маневровое разрешение)
             не менее T_S0106.
      КОГДА: prev занята и замкнута, curr свободна и замкнута, next NC
             не менее T_LS06 (сигнал не учитывается).

    Завершение ДС:
      после формирования ЛС curr занята подряд не менее T_KON.
    """

    def __init__(
        self,
        prev_rc_id: str,
        ctrl_rc_id: str,
        next_rc_id: str,
        t_s0106: float,
        t_ls06: float,
        t_kon: float,
        *,
        signal_prev_to_ctrl_id: str,
        signal_ctrl_to_next_id: str,
        ctrl_to_next_is_shunting: bool = True,
    ) -> None:
        # поля для совместимости и возможной отладки, на топологию не опираемся
        self.prev_rc_id = prev_rc_id
        self.ctrl_rc_id = ctrl_rc_id
        self.next_rc_id = next_rc_id

        self.T_S0106 = float(t_s0106)
        self.T_LS06 = float(t_ls06)
        self.T_KON = float(t_kon)

        self.signal_prev_to_ctrl_id = signal_prev_to_ctrl_id
        self.signal_ctrl_to_next_id = signal_ctrl_to_next_id
        self.ctrl_to_next_is_shunting = bool(ctrl_to_next_is_shunting)

        self.phase = "idle"
        self.dur_p1 = 0.0
        self.dur_ls = 0.0
        self.dur_occ_after_ls = 0.0

        self.active = False
        self.ever_closed = False

    # -------- вспомогательные --------

    def _states(
        self, step: Any
    ) -> Tuple[bool, bool, bool, bool, bool, bool, bool, bool, bool]:
        """
        prev_free, prev_occ, prev_locked,
        curr_free, curr_occ, curr_locked,
        next_free, next_occ, next_locked.

        Для ЛС6 смежность берём не из modes (v12),
        а по фактическим РЦ, на которые смотрят сигналы:
          prev_rc_id -> ctrl_rc_id по signal_prev_to_ctrl_id,
          ctrl_rc_id -> next_rc_id по signal_ctrl_to_next_id.
        """
        # состояния РЦ по модели станции
        st_curr = step.rc_states.get(self.ctrl_rc_id, 0)
        st_prev = step.rc_states.get(self.prev_rc_id, 0) if self.prev_rc_id else 0
        st_next = step.rc_states.get(self.next_rc_id, 0) if self.next_rc_id else 0

        prev_free = rc_is_free(st_prev)
        prev_occ = rc_is_occupied(st_prev)
        prev_locked = rc_is_locked(st_prev)

        curr_free = rc_is_free(st_curr)
        curr_occ = rc_is_occupied(st_curr)
        curr_locked = rc_is_locked(st_curr)

        next_free = rc_is_free(st_next)
        next_occ = rc_is_occupied(st_next)
        next_locked = rc_is_locked(st_next)

        return (
            prev_free,
            prev_occ,
            prev_locked,
            curr_free,
            curr_occ,
            curr_locked,
            next_free,
            next_occ,
            next_locked,
        )

    @staticmethod
    def _nc_flags(step: Any, ctrl_rc_id: str) -> Tuple[bool, bool]:
        """
        prev_nc, next_nc для ЛС6 считаем по реальным prev_rc_id/next_rc_id
        (как "нет контроля по РЦ"), а не по локальной смежности v12.
        """
        # находим сам детектор ЛС6 из modes (его ctrl_rc_id уже известен)
        modes = getattr(step, "modes", {}) or {}
        # prev/next состояния те же, что использует _states
        # но нам нужен именно признак "нет контроля"
        # curr_rc_id для доступа к полям детектора здесь не нужен
        # (nc зависит только от Uni_State_ID)
        st_curr = step.rc_states.get(ctrl_rc_id, 0)

        # prev/next состояния восстановим по тем же ключам, что пишет simulate_1p,
        # но для ЛС6 привязка к prev_rc_id/next_rc_id уже в _states
        # здесь считаем NC через rc_no_control по тем же Uni_State_ID
        # что и в _states (через rc_states)
        # Для унификации читаем те же поля, что и _states
        # (они уже положены в modes simulate_1p для per-RC вариантов).
        st_prev = int(modes.get(f"{ctrl_rc_id}_prev_state", 0))
        st_next = int(modes.get(f"{ctrl_rc_id}_next_state", 0))

        prev_nc = rc_no_control(st_prev)
        next_nc = rc_no_control(st_next)
        return prev_nc, next_nc

    def _signal_states(self, step: Any) -> Tuple[bool, bool]:
        """
        prev->ctrl: поездной разрешающий.
        ctrl->next: поездной или маневровый разрешающий.
        Связка светофор<->РЦ такая же, как в v4 (через ID сигналов).
        """
        sig_map = getattr(step, "signal_states", {}) or {}
        st_prev_ctrl = sig_map.get(self.signal_prev_to_ctrl_id, 0)
        st_ctrl_next = sig_map.get(self.signal_ctrl_to_next_id, 0)

        sig_prev_ctrl_open = signal_is_open(st_prev_ctrl) and not signal_is_closed(
            st_prev_ctrl
        )

        if self.ctrl_to_next_is_shunting:
            sig_ctrl_next_open = signal_is_shunting(
                st_ctrl_next
            ) and not shunting_signal_is_closed(st_ctrl_next)
        else:
            sig_ctrl_next_open = signal_is_open(
                st_ctrl_next
            ) and not signal_is_closed(st_ctrl_next)

        return sig_prev_ctrl_open, sig_ctrl_next_open

    def _soft_reset(self) -> None:
        self.phase = "idle"
        self.dur_p1 = 0.0
        self.dur_ls = 0.0
        self.dur_occ_after_ls = 0.0
        self.active = False

    def reset(self) -> None:
        self._soft_reset()
        self.ever_closed = False

    # -------- основной метод --------

    def update(self, step: Any, dt_interval: float) -> Tuple[bool, bool]:
        """
        Обновление детектора по шагу сценария.

        :return: (opened, closed)
        """
        if dt_interval <= 0.0:
            dt_interval = 0.0

        opened = False
        closed = False

        (
            prev_free,
            prev_occ,
            prev_locked,
            curr_free,
            curr_occ,
            curr_locked,
            next_free,
            next_occ,
            next_locked,
        ) = self._states(step)

        prev_nc, next_nc = self._nc_flags(step, self.ctrl_rc_id)
        sig_prev_ctrl_open, sig_ctrl_next_open = self._signal_states(step)

        # уже был завершён — новое формирование не допускаем
        if self.ever_closed:
            return False, False

        # --- завершение ДС ---
        if self.active:
            if curr_occ:
                self.dur_occ_after_ls += dt_interval
                if self.dur_occ_after_ls >= self.T_KON:
                    closed = True
                    self.ever_closed = True
                    self._soft_reset()
            else:
                self.dur_occ_after_ls = 0.0
            return opened, closed

        # --- формирование ДС ---

        if self.phase == "idle":
            # Ветка 6.1: предыдущая не контролируется
            # ДАНО: prev NC, curr свободна+замкнута, next свободна+замкнута,
            #       светофор prev->ctrl открыт.
            print(
                f"[LS6 dbg] ctrl={self.ctrl_rc_id} "
                f"prev_rc={self.prev_rc_id} next_rc={self.next_rc_id} "
                f"prev_nc={prev_nc} next_nc={next_nc} "
                f"curr_free={curr_free} curr_locked={curr_locked} "
                f"next_free={next_free} next_locked={next_locked} "
                f"sig_prev_open={sig_prev_ctrl_open} sig_next_open={sig_ctrl_next_open} "
                f"dur_p1={self.dur_p1}"
            )
            
            cond_p1_6_1 = (
                prev_nc
                and curr_free
                and curr_locked
                and next_free
                and next_locked
                and sig_prev_ctrl_open
            )

            # Ветка 6.2: следующая не контролируется
            # ДАНО: prev свободна+замкнута, curr свободна+замкнута, next NC,
            #       светофор ctrl->next открыт.
            cond_p1_6_2 = (
                prev_free
                and prev_locked
                and curr_free
                and curr_locked
                and next_nc
                and sig_ctrl_next_open
            )

            if cond_p1_6_1:
                self.dur_p1 += dt_interval
                self.dur_ls = 0.0
                if self.dur_p1 >= self.T_S0106:
                    self.phase = "p1_6_1"
            elif cond_p1_6_2:
                self.dur_p1 += dt_interval
                self.dur_ls = 0.0
                if self.dur_p1 >= self.T_S0106:
                    self.phase = "p1_6_2"
            else:
                self.dur_p1 = 0.0
                self.dur_ls = 0.0

        elif self.phase == "p1_6_1":
            # КОГДА 6.1: prev NC, curr свободна+замкнута, next занята+замкнута.
            print(
                f"[LS6 dbg] phase=p1_6_1 ctrl={self.ctrl_rc_id} "
                f"prev_nc={prev_nc} curr_free={curr_free} curr_locked={curr_locked} "
                f"next_occ={next_occ} next_locked={next_locked} dur_ls={self.dur_ls}"
            )

            cond_ls_6_1 = (
                prev_nc
                and curr_free
                and curr_locked
                and next_occ
                and next_locked
            )
            if cond_ls_6_1:
                self.dur_ls += dt_interval
                if self.dur_ls >= self.T_LS06:
                    opened = True
                    self.active = True
                    self.dur_occ_after_ls = 0.0
            else:
                self.dur_ls = 0.0

        elif self.phase == "p1_6_2":
            # КОГДА 6.2: prev занята+замкнута, curr свободна+замкнута, next NC.

            print(
                f"[LS6 dbg] phase=p1_6_2 ctrl={self.ctrl_rc_id} "
                f"prev_nc={prev_nc} curr_free={curr_free} curr_locked={curr_locked} "
                f"next_occ={next_occ} next_locked={next_locked} dur_ls={self.dur_ls}"
            )
            cond_ls_6_2 = (
                prev_occ
                and prev_locked
                and curr_free
                and curr_locked
                and next_nc
            )
            if cond_ls_6_2:
                self.dur_ls += dt_interval
                if self.dur_ls >= self.T_LS06:
                    opened = True
                    self.active = True
                    self.dur_occ_after_ls = 0.0
            else:
                self.dur_ls = 0.0

        return opened, closed

from typing import Any
from ..station_visochino_1p import rc_is_free, rc_is_occupied

T_S0101 = 15  # сек 0-0-0
T_LZ01 = 5    # сек 0-1-0
T_KON = 10    # сек свободности для завершения ДС

def _is_000(step: Any) -> bool:
    st_prev = step.rc_states.get("10-12SP", 0)
    st_curr = step.rc_states.get("1P", 0)
    st_next = step.rc_states.get("1-7SP", 0)
    return rc_is_free(st_prev) and rc_is_free(st_curr) and rc_is_free(st_next)

def _is_010(step: Any) -> bool:
    st_prev = step.rc_states.get("10-12SP", 0)
    st_curr = step.rc_states.get("1P", 0)
    st_next = step.rc_states.get("1-7SP", 0)
    return rc_is_free(st_prev) and rc_is_occupied(st_curr) and rc_is_free(st_next)

def _is_curr_free(step: Any) -> bool:
    st_curr = step.rc_states.get("1P", 0)
    return rc_is_free(st_curr)

def _is_curr_occupied(step: Any) -> bool:
    st_curr = step.rc_states.get("1P", 0)
    return rc_is_occupied(st_curr)

class Variant1Detector:
    """
    Вариант 1 ЛЗ 1П.

    Формирование:
    1) не менее T_S0101 секунд подряд 0-0-0,
    2) затем не менее T_LZ01 секунд подряд 0-1-0.

    Завершение ДС:
    — после формирования ДС контролируемая РЦ (1P) свободна
      подряд не менее T_KON секунд.

    До открытия ДС требуются достоверные обе смежные (prev_control_ok, next_control_ok).
    После открытия ДС потеря достоверности смежных не влияет на завершение.
    """

    def __init__(
        self,
        t_s0101: float = T_S0101,
        t_lz01: float = T_LZ01,
        t_kon: float = T_KON,
    ) -> None:
        self.T_S0101 = float(t_s0101)
        self.T_LZ01 = float(t_lz01)
        self.T_KON = float(t_kon)

        # phase: "idle" -> "s0101_done" -> "active"
        self.phase = "idle"

        self.dur_000 = 0.0
        self.dur_010 = 0.0

        # для завершения ДС
        self.dur_free_after_lz = 0.0

        self.active = False

    def reset(self) -> None:
        self.phase = "idle"
        self.dur_000 = 0.0
        self.dur_010 = 0.0
        self.dur_free_after_lz = 0.0
        self.active = False

    def update(self, step: Any, dt_interval: float) -> tuple[bool, bool]:
        if dt_interval < 0:
            dt_interval = 0.0

        s000 = _is_000(step)
        s010 = _is_010(step)
        curr_free = _is_curr_free(step)
        curr_occ = _is_curr_occupied(step)

        modes = getattr(step, "modes", {}) or {}
        # по умолчанию считаем, что смежные НЕДОСТОВЕРНЫ, если simulate_1p их не проставил
        prev_control_ok = bool(modes.get("prev_control_ok", False))
        next_control_ok = bool(modes.get("next_control_ok", False))

        opened = False
        closed = False

        # --- формирование ДС ---
        if not self.active:
            # до открытия требуем достоверные обе смежные
            if not (prev_control_ok and next_control_ok):
                # нет достоверных смежных – вариант 1 недопустим, сбрасываем фазы
                self.phase = "idle"
                self.dur_000 = 0.0
                self.dur_010 = 0.0
            else:
                if self.phase == "idle":
                    if s000:
                        self.dur_000 += dt_interval
                        self.dur_010 = 0.0
                        if self.dur_000 >= self.T_S0101:
                            self.phase = "s0101_done"
                    else:
                        self.dur_000 = 0.0
                        self.dur_010 = 0.0

                elif self.phase == "s0101_done":
                    if s010:
                        self.dur_010 += dt_interval
                        if self.dur_010 >= self.T_LZ01:
                            opened = True
                            self.active = True
                            self.phase = "active"
                            self.dur_free_after_lz = 0.0
                    elif s000:
                        self.dur_000 += dt_interval
                        self.dur_010 = 0.0
                    else:
                        self.reset()

        # --- завершение ДС по T_KON ---
        if self.phase == "active" and self.active:
            if curr_free:
                self.dur_free_after_lz += dt_interval
                if self.dur_free_after_lz >= self.T_KON:
                    closed = True
                    self.reset()
            elif curr_occ:
                self.dur_free_after_lz = 0.0
            else:
                self.dur_free_after_lz = 0.0

        return opened, closed

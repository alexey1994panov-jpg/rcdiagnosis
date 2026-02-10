# engine/variants/ls_variant1_1p.py

from typing import Any

from ..station_visochino_1p import rc_is_free, rc_is_occupied


# Значения по умолчанию (могут переопределяться через simulate_1p options)
T_C0101_LS_DEFAULT = 20.0  # Тс0101: длительность события 01 ЛС
T_LS01_DEFAULT = 10.0      # Тлс01: хвост свободности для записи протокола ЛС
T_KON_LS_DEFAULT = 10.0    # Ткон: ожидание завершения ситуации (занятость после ЛС)


def _is_nc(value: int) -> bool:
    """
    Признак "РЦ не контролируется" для ЛС.

    Конкретные коды зависят от модели станции.
    Здесь предполагается, что 0 = нет контроля, 3 = свободна, 6 = занята.
    При необходимости адаптируйте под реальные коды.
    """
    return value not in (3, 6)


def _is_c0101_state(step: Any) -> bool:
    """
    Событие 01 для ЛС (вариант 1):

    1) Prev=0, Curr=1, Next=0
    2) Prev=NC, Curr=1, Next=0
    3) Prev=0, Curr=1, Next=NC
    4) Prev=NC, Curr=1, Next=NC

    ВАЖНО:
    - Достоверность смежных (Prev/Next) по стрелкам и Тпк (T_PK) НЕ вычисляется здесь.
      Она уже учтена в prev_control_ok/next_control_ok, которые формирует simulate_1p.
    - Здесь рассматриваются только значения rc_states при условии, что
      prev_control_ok/next_control_ok == True.
    """
    st_prev = step.rc_states.get("10-12SP", 0)
    st_curr = step.rc_states.get("1P", 0)
    st_next = step.rc_states.get("1-7SP", 0)

    prev_free = rc_is_free(st_prev)
    prev_occ = rc_is_occupied(st_prev)
    next_free = rc_is_free(st_next)
    next_occ = rc_is_occupied(st_next)

    prev_nc = _is_nc(st_prev)
    next_nc = _is_nc(st_next)
    curr_occ = rc_is_occupied(st_curr)

    # 1) Prev=0, Curr=1, Next=0
    if prev_free and curr_occ and next_free:
        return True

    # 2) Prev=NC, Curr=1, Next=0
    if prev_nc and not prev_occ and curr_occ and next_free:
        return True

    # 3) Prev=0, Curr=1, Next=NC
    if prev_free and curr_occ and next_nc and not next_occ:
        return True

    # 4) Prev=NC, Curr=1, Next=NC
    if prev_nc and not prev_occ and curr_occ and next_nc and not next_occ:
        return True

    return False


def _is_curr_free(step: Any) -> bool:
    st_curr = step.rc_states.get("1P", 0)
    return rc_is_free(st_curr)


def _is_curr_occupied(step: Any) -> bool:
    st_curr = step.rc_states.get("1P", 0)
    return rc_is_occupied(st_curr)


class VariantLS1Detector:
    """
    Вариант 1 Логической ложной свободности (ЛС) для 1П.

    Глобальное правило по Тпк:
    - Достоверность смежных по стрелкам (Prev/Next) и выдержка T_PK
      полностью реализованы в simulate_1p.
    - Детектор получает только флаги modes.prev_control_ok / modes.next_control_ok
      и не знает о стрелках и T_PK напрямую.
    - Это правило едино для всех вариантов ЛЗ/ЛС.

    Формирование ДС (ЛС1):

    ДАНО (фаза C0101):
    - (Prev=0, Curr=1, Next=0) не менее T_C0101_LS (подряд), ИЛИ
    - (Prev=NC, Curr=1, Next=0) не менее T_C0101_LS (подряд), ИЛИ
    - (Prev=0, Curr=1, Next=NC) не менее T_C0101_LS (подряд), ИЛИ
    - (Prev=NC, Curr=1, Next=NC) не менее T_C0101_LS (подряд).

    КОГДА (хвост):
    - Curr=0 (свободна) подряд не менее T_LS01.

    И нет:
    - исключения формирования ЛС (обрабатывается снаружи simulate_1p),
    - активной тестовой проверки (флаг test_check_ls_active обрабатывается снаружи).

    ТОГДА:
    - формируется ДС "Логическая ложная свободность" (ЛС1).

    Завершение ДС:

    ДАНО:
    - ДС ЛС сформирован (phase == "active").

    КОГДА:
    - Curr=1 (занята) суммарно не менее T_KON_LS.

    ТОГДА:
    - ДС ЛС завершается.
    """

    def __init__(
        self,
        t_c0101: float = T_C0101_LS_DEFAULT,
        t_ls01: float = T_LS01_DEFAULT,
        t_kon_ls: float = T_KON_LS_DEFAULT,
    ) -> None:
        self.T_C0101 = float(t_c0101)
        self.T_LS01 = float(t_ls01)
        self.T_KON_LS = float(t_kon_ls)

        # Фазы: "idle" -> "c0101_done" -> "active"
        self.phase: str = "idle"

        # Накопление времени по фазам
        self.dur_c0101: float = 0.0      # событие 01 (Curr=1, смежные 0/NC)
        self.dur_tail_free: float = 0.0  # хвост свободности Curr=0

        # Для завершения ДС
        self.dur_occ_after_ls: float = 0.0  # занятость после ЛС

        # Флаг активного ДС
        self.active: bool = False

    def reset(self) -> None:
        self.phase = "idle"
        self.dur_c0101 = 0.0
        self.dur_tail_free = 0.0
        self.dur_occ_after_ls = 0.0
        self.active = False

    def update(self, step: Any, dt_interval: float) -> tuple[bool, bool]:
        """
        Обновить состояние детектора на интервале dt_interval.

        Возвращает (opened, closed):
        - opened == True — на этом интервале сформировалась ЛС (ДС открыто);
        - closed == True — на этом интервале выполнены условия завершения ДС.

        ВАЖНО:
        - prev_control_ok / next_control_ok должны быть заранее установлены в simulate_1p
          с учётом стрелок и T_PK и являются единственным источником информации
          о достоверности смежных для ЛС1.
        """
        if dt_interval < 0:
            dt_interval = 0.0

        s_c0101 = _is_c0101_state(step)
        curr_free = _is_curr_free(step)
        curr_occ = _is_curr_occupied(step)

        # признаки достоверности смежных (общие с ЛЗ)
        modes = getattr(step, "modes", {}) or {}
        prev_control_ok = bool(modes.get("prev_control_ok", True))
        next_control_ok = bool(modes.get("next_control_ok", True))

        opened = False
        closed = False

        # --- формирование ДС ---
        if not self.active:
            # если смежные недостоверны — ЛС недопустима (логика та же, что и для ЛЗ)
            if not prev_control_ok or not next_control_ok:
                self.phase = "idle"
                self.dur_c0101 = 0.0
                self.dur_tail_free = 0.0
            else:
                if self.phase == "idle":
                    # Фаза C0101: Curr=1, смежные 0/NC — время подряд
                    if s_c0101:
                        self.dur_c0101 += dt_interval
                        self.dur_tail_free = 0.0
                        if self.dur_c0101 >= self.T_C0101:
                            self.phase = "c0101_done"
                    else:
                        self.dur_c0101 = 0.0
                        self.dur_tail_free = 0.0

                elif self.phase == "c0101_done":
                    # Хвост: Curr=0 подряд T_LS01
                    if curr_free:
                        self.dur_tail_free += dt_interval
                        if self.dur_tail_free >= self.T_LS01:
                            opened = True
                            self.active = True
                            self.phase = "active"
                            self.dur_occ_after_ls = 0.0
                    elif s_c0101:
                        # если вернулись к событию 01 — можно продолжать накапливать C0101
                        self.dur_c0101 += dt_interval
                        self.dur_tail_free = 0.0
                    else:
                        # разрыв — полный сброс
                        self.reset()

        # --- завершение ДС по T_KON_LS ---
        if self.phase == "active" and self.active:
            if curr_occ:
                # суммарная занятость после ЛС
                self.dur_occ_after_ls += dt_interval
                if self.dur_occ_after_ls >= self.T_KON_LS:
                    closed = True
                    self.reset()
            else:
                # при свободности/неконтролируемости сбрасываем выдержку
                self.dur_occ_after_ls = 0.0

        return opened, closed

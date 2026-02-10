# variant_configs.py
from base_detector import PhaseConfig, DetectorConfig, CompletionMode

# уже есть
MASK_000 = 0
MASK_010 = 1

# добавим маски для v2
MASK_V2_PREV_P1 = 10
MASK_V2_PREV_P2 = 11
MASK_V2_PREV_P3 = 12
MASK_V2_NEXT_P1 = 20
MASK_V2_NEXT_P2 = 21
MASK_V2_NEXT_P3 = 22

# маски для v7
MASK_V7_GIVEN_NO_ADJACENT = 70
MASK_V7_GIVEN_NO_PREV = 71
MASK_V7_GIVEN_NO_NEXT = 72
MASK_V7_WHEN_NO_ADJACENT = 73
MASK_V7_WHEN_NO_PREV = 74
MASK_V7_WHEN_NO_NEXT = 75


def make_lz1_config(ts01_lz1: float, tlz_lz1: float, tkon_lz1: float) -> DetectorConfig:
    return DetectorConfig(
        variant_id=1,
        initial_phase_id=0,
        phases=[
            PhaseConfig(
                phase_id=0,
                name="idle",
                mask_id=MASK_000,
                duration=float(ts01_lz1),
                next_phase_id=1,
                timer_mode="continuous",
                reset_on_exit=True,
            ),
            PhaseConfig(
                phase_id=1,
                name="s0101_done",
                mask_id=MASK_010,
                duration=float(tlz_lz1),
                next_phase_id=-1,
                timer_mode="continuous",
                reset_on_exit=True,
            ),
        ],
        t_kon=float(tkon_lz1),
        completion_mode=CompletionMode.FREE_TIME,
        requires_adjacent=True,
        parallel_branches={},
    )


def make_lz2_config(ts01_lz2: float, ts02_lz2: float, tlz_lz2: float, tkon_lz2: float) -> DetectorConfig:
    """
    Вариант 2 — две параллельные ветки:
      ветка prev: p1(10) -> p2(11) -> p3(12)
      ветка next: p1(20) -> p2(21) -> p3(22)
    Финальная фаза p3 -> открытие ДС, завершение по FREE_TIME и tkon_lz2.
    """
    # основная ветка для v2 не используется, всё в параллельных
    phases_main: list[PhaseConfig] = [
        PhaseConfig(
            phase_id=0,
            name="idle",
            mask_id=MASK_000,
            duration=0.0,
            next_phase_id=0,
            timer_mode="continuous",
            reset_on_exit=False,
        )
    ]

    # ветка "предыдущая занята"
    prev_branch = [
        PhaseConfig(
            phase_id=0,
            name="prev_p1",
            mask_id=MASK_V2_PREV_P1,
            duration=float(ts01_lz2),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=1,
            name="prev_p2",
            mask_id=MASK_V2_PREV_P2,
            duration=float(tlz_lz2),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=2,
            name="prev_p3",
            mask_id=MASK_V2_PREV_P3,
            duration=float(ts02_lz2),
            next_phase_id=-1,  # финал -> open
            timer_mode="continuous",
            reset_on_exit=True,
        ),
    ]

    # ветка "следующая занята"
    next_branch = [
        PhaseConfig(
            phase_id=0,
            name="next_p1",
            mask_id=MASK_V2_NEXT_P1,
            duration=float(ts01_lz2),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=1,
            name="next_p2",
            mask_id=MASK_V2_NEXT_P2,
            duration=float(tlz_lz2),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=2,
            name="next_p3",
            mask_id=MASK_V2_NEXT_P3,
            duration=float(ts02_lz2),
            next_phase_id=-1,  # финал -> open
            timer_mode="continuous",
            reset_on_exit=True,
        ),
    ]

    return DetectorConfig(
        variant_id=2,
        initial_phase_id=0,
        phases=phases_main,
        t_kon=float(tkon_lz2),
        completion_mode=CompletionMode.FREE_TIME,
        requires_adjacent=False,  # для v2 логика достоверности своя
        parallel_branches={
            1: prev_branch,
            2: next_branch,
        },
    )


def make_lz7_config(ts01_lz7: float, tlz_lz7: float, tkon_lz7: float) -> DetectorConfig:
    """
    Вариант 7 — три параллельные ветки:
      - ветка no_adjacent: нет смежных РЦ (v6)
      - ветка no_prev: нет предыдущей по положению стрелки (v7.1)
      - ветка no_next: нет следующей по положению стрелки (v7.2)
    
    Каждая ветка имеет 2 фазы:
      - phase 0 (given): ДАНО — условия свободности ≥ ts01_lz7
      - phase 1 (when): КОГДА — условия занятости ≥ tlz_lz7
    
    Завершение по FREE_TIME с t_kon = tkon_lz7.
    """
    # Основная ветка не используется, всё в параллельных
    phases_main: list[PhaseConfig] = [
        PhaseConfig(
            phase_id=0,
            name="idle",
            mask_id=MASK_000,
            duration=0.0,
            next_phase_id=0,
            timer_mode="continuous",
            reset_on_exit=False,
        )
    ]

    # Ветка "нет смежных РЦ" (v6)
    no_adjacent_branch = [
        PhaseConfig(
            phase_id=0,
            name="no_adjacent_given",
            mask_id=MASK_V7_GIVEN_NO_ADJACENT,
            duration=float(ts01_lz7),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=1,
            name="no_adjacent_when",
            mask_id=MASK_V7_WHEN_NO_ADJACENT,
            duration=float(tlz_lz7),
            next_phase_id=-1,  # финал -> open
            timer_mode="continuous",
            reset_on_exit=True,
        ),
    ]

    # Ветка v7.1: нет предыдущей по положению стрелки
    no_prev_branch = [
        PhaseConfig(
            phase_id=0,
            name="no_prev_given",
            mask_id=MASK_V7_GIVEN_NO_PREV,
            duration=float(ts01_lz7),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=1,
            name="no_prev_when",
            mask_id=MASK_V7_WHEN_NO_PREV,
            duration=float(tlz_lz7),
            next_phase_id=-1,  # финал -> open
            timer_mode="continuous",
            reset_on_exit=True,
        ),
    ]

    # Ветка v7.2: нет следующей по положению стрелки
    no_next_branch = [
        PhaseConfig(
            phase_id=0,
            name="no_next_given",
            mask_id=MASK_V7_GIVEN_NO_NEXT,
            duration=float(ts01_lz7),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=1,
            name="no_next_when",
            mask_id=MASK_V7_WHEN_NO_NEXT,
            duration=float(tlz_lz7),
            next_phase_id=-1,  # финал -> open
            timer_mode="continuous",
            reset_on_exit=True,
        ),
    ]

    return DetectorConfig(
        variant_id=7,
        initial_phase_id=0,
        phases=phases_main,
        t_kon=float(tkon_lz7),
        completion_mode=CompletionMode.FREE_TIME,
        requires_adjacent=False,  # для v7 логика достоверности своя (через флаги)
        parallel_branches={
            1: no_adjacent_branch,
            2: no_prev_branch,
            3: no_next_branch,
        },
    )

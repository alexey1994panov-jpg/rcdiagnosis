# -*- coding: utf-8 -*-
"""
Тесты для варианта LS9 (Пробой изолирующего стыка)

LS9 детектирует ситуацию, когда РЦ переходит из занятого состояния
в свободное и обратно в занятое (пробой изолирующего стыка).

Фазы:
    0 (S0109): ctrl занята → ts01_ls9
    1 (tail):  ctrl свободна → tlz_ls9
    2 (S0209): ctrl занята → tlz_ls9 → открытие
    Завершение: ctrl свободна ≥ tkon_ls9 → закрытие
"""

from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig


def test_ls9_108_full_cycle():
    """
    Полный цикл LS9 на 108 (1П) - из legacy теста.
    
    Сценарий из legacy/tests/test_ls_variant9_1p.py:
    - 3 шага: 1П занята (6) - фаза S0109
    - 3 шага: 1П свободна (3) - фаза tail
    - 6 шагов: 1П занята (6) - фаза S0209 → открытие → завершение
    
    Тайминги: ts01_ls9=2.0, tlz_ls9=2.0, tkon_ls9=3.0
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 1П (ID)
        prev_rc_name=None,         # LS9 не требует соседей
        ctrl_rc_name="108",
        next_rc_name=None,
        # Отключаем все остальные варианты
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        # LS9 параметры
        ts01_ls9=2.0,  # Фаза S0109: занята ≥ 2с
        tlz_ls9=2.0,   # Фаза tail: свободна ≥ 2с, фаза S0209: занята ≥ 2с
        tkon_ls9=3.0,  # Завершение: свободна ≥ 3с
        enable_ls9=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-3с: S0109 - 1П занята (6) ≥ ts01_ls9=2.0 → переход к фазе 1
        ScenarioStep(
            t=3.0,
            rc_states={"108": 6},  # занята
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 3-6с: tail - 1П свободна (3) ≥ tlz_ls9=2.0 → переход к фазе 2
        ScenarioStep(
            t=3.0,
            rc_states={"108": 3},  # свободна
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 6-12с: S0209 - 1П занята (6) ≥ tlz_ls9=2.0 → открытие ЛС9
        # Затем свободна ≥ tkon_ls9=3.0 → закрытие
        ScenarioStep(
            t=6.0,
            rc_states={"108": 6},  # занята
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 12-16с: Завершение - 1П свободна (3) ≥ tkon_ls9=3.0 → закрытие
        ScenarioStep(
            t=4.0,
            rc_states={"108": 3},  # свободна
            switch_states={},
            signal_states={},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="108",
    )

    timeline = ctx.run()

    # Вывод для отладки
    print("\n=== LS9 Test: 108 (1П) ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_108={st.rc_states.get('108', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # Проверки
    assert any("lls_9_open" in s.flags for s in timeline), "Нет lls_9_open"
    assert any("lls_9" in s.flags and s.lz_variant == 109 for s in timeline), "lls_9 без variant=109"
    assert any("lls_9_closed" in s.flags for s in timeline), "Нет lls_9_closed"


def test_ls9_59_full_cycle():
    """
    Полный цикл LS9 на 59 (10-12СП).
    
    Проверяем работу на другой РЦ с теми же фазами.
    Тайминги: ts01_ls9=1.5, tlz_ls9=1.5, tkon_ls9=2.0
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",           # 10-12СП (ID)
        prev_rc_name=None,
        ctrl_rc_name="59",
        next_rc_name=None,
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        ts01_ls9=1.5,
        tlz_ls9=1.5,
        tkon_ls9=2.0,
        enable_ls9=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-2с: S0109 - занята
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2-4с: tail - свободна
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 4-6с: S0209 - занята → открытие
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 6-9с: Завершение - свободна → закрытие
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="59",
    )

    timeline = ctx.run()

    print("\n=== LS9 Test: 59 (10-12СП) ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("lls_9_open" in s.flags for s in timeline), "Нет lls_9_open"
    assert any("lls_9" in s.flags and s.lz_variant == 109 for s in timeline), "lls_9 без variant=109"
    assert any("lls_9_closed" in s.flags for s in timeline), "Нет lls_9_closed"


def test_ls9_83_interrupted_phase():
    """
    Тест прерывания фазы LS9 на 83 (1-7СП).
    
    Проверяем, что если условие фазы нарушается,
    детектор сбрасывается и не открывается.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="83",           # 1-7СП (ID)
        prev_rc_name=None,
        ctrl_rc_name="83",
        next_rc_name=None,
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        ts01_ls9=2.0,
        tlz_ls9=2.0,
        tkon_ls9=3.0,
        enable_ls9=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-1с: S0109 - занята (недостаточно для ts01_ls9=2.0)
        ScenarioStep(
            t=1.0,
            rc_states={"83": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 1-2с: Прерывание - свободна (сброс фазы 0)
        ScenarioStep(
            t=1.0,
            rc_states={"83": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2-5с: Снова занята (новая попытка S0109)
        ScenarioStep(
            t=3.0,
            rc_states={"83": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 5-8с: Свободна (фаза tail)
        ScenarioStep(
            t=3.0,
            rc_states={"83": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 8-11с: Занята (фаза S0209) → открытие
        ScenarioStep(
            t=3.0,
            rc_states={"83": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 11-15с: Свободна → закрытие
        ScenarioStep(
            t=4.0,
            rc_states={"83": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="83",
    )

    timeline = ctx.run()

    print("\n=== LS9 Test: 83 (1-7СП) - Interrupted Phase ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_83={st.rc_states.get('83', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # Проверяем, что ЛС9 всё равно открылась после восстановления
    assert any("lls_9_open" in s.flags for s in timeline), "Нет lls_9_open после прерывания"
    assert any("lls_9" in s.flags and s.lz_variant == 109 for s in timeline), "lls_9 без variant=109"
    assert any("lls_9_closed" in s.flags for s in timeline), "Нет lls_9_closed"


def test_ls9_65_no_open_insufficient_time():
    """
    Тест на 65 (4П) - недостаточное время для открытия.
    
    Проверяем, что если фазы не выполняются достаточно долго,
    ЛС9 не открывается.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="65",           # 4П (ID)
        prev_rc_name=None,
        ctrl_rc_name="65",
        next_rc_name=None,
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        ts01_ls9=3.0,  # Требуем 3 секунды
        tlz_ls9=3.0,
        tkon_ls9=2.0,
        enable_ls9=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-2с: S0109 - занята (недостаточно для ts01_ls9=3.0)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2-4с: tail - свободна (недостаточно для tlz_ls9=3.0)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 4-6с: S0209 - занята (недостаточно для tlz_ls9=3.0)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 6-8с: Свободна
        ScenarioStep(
            t=2.0,
            rc_states={"65": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="65",
    )

    timeline = ctx.run()

    print("\n=== LS9 Test: 65 (4П) - Insufficient Time ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_65={st.rc_states.get('65', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # Проверяем, что ЛС9 НЕ открылась
    assert not any("lls_9_open" in s.flags for s in timeline), "lls_9_open не должно быть"
    assert not any("lls_9" in s.flags for s in timeline), "lls_9 не должно быть активно"

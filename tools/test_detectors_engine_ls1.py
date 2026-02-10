# -*- coding: utf-8 -*-
"""
Тесты для варианта LS1 (Классическая ложная свободность)

LS1 детектирует классическую ложную свободность когда один или оба
соседа не контролируются (NC), а контролируемая РЦ занята, затем освобождается.

Фазы:
    0 (C0101): (prev NC или next NC) И curr занята → ts01_ls1
    1 (tail):  curr свободна → tlz_ls1 → открытие
    Завершение: curr занята ≥ tkon_ls1 → закрытие

NC (not controlled) - состояние не равно 3 (свободна) или 6 (занята).
Например: 0, 1, 2, 4, 5, 7, 8 и т.д.
"""

from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig


def test_ls1_108_prev_nc_full_cycle():
    """
    Полный цикл LS1 на 108 (1П) с prev NC.
    
    Сценарий:
    - prev (59) NC (состояние 0), curr (108) занята (6) - фаза C0101
    - curr (108) свободна (3) - фаза tail → открытие
    - curr (108) занята (6) → закрытие
    
    Тайминги: ts01_ls1=2.0, tlz_ls1=2.0, tkon_ls1=3.0
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 1П (ID)
        prev_rc_name="59",         # 10-12СП (ID)
        ctrl_rc_name="108",
        next_rc_name="83",         # 1-7СП (ID)
        # Отключаем все остальные варианты
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        enable_ls9=False,
        # LS1 параметры
        ts01_ls1=2.0,  # Фаза C0101: (prev NC или next NC) И curr занята ≥ 2с
        tlz_ls1=2.0,   # Фаза tail: curr свободна ≥ 2с
        tkon_ls1=3.0,  # Завершение: curr занята ≥ 3с
        enable_ls1=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-3с: C0101 - 0-1-0 (центр занят 108, края свободны 59/83)
        # Для 108: 59 = prev, 83 = next. Нужны Sw10=+ (ID 110), Sw5=+ (ID 88)
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            switch_states={"110": 3, "88": 3, "87": 3},
            signal_states={},
            modes={},
        ),
        # 3-6с: tail - 0-0-0 (все свободны) → открытие ЛС1
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"110": 15, "88": 15, "87": 15},
            signal_states={},
            modes={},
        ),
        # 6-10с: Завершение - 0-0-0 (все свободны) ≥ tkon_ls1=3.0 → закрытие
        ScenarioStep(
            t=4.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"110": 3, "88": 3, "87": 3},
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
    print("\n=== LS1 Test: 108 (1П) - prev NC ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59', 0)}, "
            f"rc_108={st.rc_states.get('108', 0)}, rc_83={st.rc_states.get('83', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # Проверки
    assert any("lls_1_open" in s.flags for s in timeline), "Нет lls_1_open"
    assert any("lls_1" in s.flags and s.lz_variant == 101 for s in timeline), "lls_1 без variant=101"
    assert any("lls_1_closed" in s.flags for s in timeline), "Нет lls_1_closed"


def test_ls1_59_next_nc_full_cycle():
    """
    Полный цикл LS1 на 59 (10-12СП) с next NC.
    
    Сценарий:
    - prev свободна, curr занята, next NC - фаза C0101
    - curr свободна - фаза tail → открытие
    - curr занята → закрытие
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",           # 10-12СП (ID)
        prev_rc_name="47",         # 1АП (ID)
        ctrl_rc_name="59",
        next_rc_name="104",        # 3СП (ID)
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        enable_ls9=False,
        ts01_ls1=1.5,
        tlz_ls1=1.5,
        tkon_ls1=2.0,
        enable_ls1=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-2с: C0101 - 0-1-0 (центр занята 59, края 47/108 свободны)
        # Для 59: 47 = prev (безусловный), 108 = next. Нужна Sw10=+ (ID 110)
        ScenarioStep(
            t=2.0,
            rc_states={"47": 3, "59": 6, "108": 3},
            switch_states={"110": 3},
            signal_states={},
            modes={},
        ),
        # 2-4с: tail - 0-0-0 (все свободны) → открытие
        ScenarioStep(
            t=2.0,
            rc_states={"47": 3, "59": 3, "108": 3},
            switch_states={"110": 3},
            signal_states={},
            modes={},
        ),
        # 4-7с: Завершение - 0-0-0 (все свободны) → закрытие
        ScenarioStep(
            t=3.0,
            rc_states={"47": 3, "59": 3, "108": 3},
            switch_states={"110": 3},
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

    print("\n=== LS1 Test: 59 (10-12СП) - next NC ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_47={st.rc_states.get('47', 0)}, "
            f"rc_59={st.rc_states.get('59', 0)}, rc_108={st.rc_states.get('108', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("lls_1_open" in s.flags for s in timeline), "Нет lls_1_open"
    assert any("lls_1" in s.flags and s.lz_variant == 101 for s in timeline), "lls_1 без variant=101"
    assert any("lls_1_closed" in s.flags for s in timeline), "Нет lls_1_closed"


def test_ls1_83_both_nc_full_cycle():
    """
    Полный цикл LS1 на 83 (1-7СП) с обоими соседями NC.
    
    Проверяем, что LS1 срабатывает когда оба соседа NC.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="83",           # 1-7СП (ID)
        prev_rc_name="86",         # 3СП (ID)
        ctrl_rc_name="83",
        next_rc_name="81",         # НП (ID)
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        enable_ls9=False,
        ts01_ls1=2.0,
        tlz_ls1=2.0,
        tkon_ls1=3.0,
        enable_ls1=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-3с: C0101 - 0-1-0 (83 занята, соседа 86/81 свободны)
        # Для 83: 86 = prev (Sw150=0/Minus), 81 = next (безусловный)
        ScenarioStep(
            t=3.0,
            rc_states={"86": 3, "83": 6, "81": 3},
            switch_states={"150": 9},  # 150 в Минусе (9) для соединения 86
            signal_states={},
            modes={},
        ),
        # 3-6с: tail - 0-0-0 (все свободны) → открытие
        ScenarioStep(
            t=3.0,
            rc_states={"86": 3, "83": 3, "81": 3},
            switch_states={"150": 9},
            signal_states={},
            modes={},
        ),
        # 6-10с: Завершение - 0-0-0 (все свободны) → закрытие
        ScenarioStep(
            t=4.0,
            rc_states={"86": 3, "83": 3, "81": 3},
            switch_states={"150": 9},
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

    print("\n=== LS1 Test: 83 (1-7СП) - both NC ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_86={st.rc_states.get('86', 0)}, "
            f"rc_83={st.rc_states.get('83', 0)}, rc_81={st.rc_states.get('81', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("lls_1_open" in s.flags for s in timeline), "Нет lls_1_open"
    assert any("lls_1" in s.flags and s.lz_variant == 101 for s in timeline), "lls_1 без variant=101"
    assert any("lls_1_closed" in s.flags for s in timeline), "Нет lls_1_closed"


def test_ls1_65_no_open_no_nc():
    """
    Тест на 65 (4П) - нет NC, ЛС1 не должна открыться.
    
    Проверяем, что если оба соседа контролируются (не NC),
    то ЛС1 не формируется.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="65",           # 4П (ID)
        prev_rc_name="36",         # 2-8СП (ID)
        ctrl_rc_name="65",
        next_rc_name="94",         # 14-16СП (ID)
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        enable_ls9=False,
        ts01_ls1=2.0,
        tlz_ls1=2.0,
        tkon_ls1=3.0,
        enable_ls1=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-3с: prev свободна (3), curr занята (6), next свободна (3) - НЕТ NC!
        ScenarioStep(
            t=3.0,
            rc_states={"36": 3, "65": 6, "94": 3},  # нет NC
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 3-6с: curr свободна (3)
        ScenarioStep(
            t=3.0,
            rc_states={"36": 3, "65": 3, "94": 3},  # curr свободна
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 6-8с: curr занята (6)
        ScenarioStep(
            t=2.0,
            rc_states={"36": 3, "65": 6, "94": 3},  # curr занята
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

    print("\n=== LS1 Test: 65 (4П) - No NC ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_36={st.rc_states.get('36', 0)}, "
            f"rc_65={st.rc_states.get('65', 0)}, rc_94={st.rc_states.get('94', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # Проверяем, что ЛС1 НЕ открылась (нет NC)
    assert not any("lls_1_open" in s.flags for s in timeline), "lls_1_open не должно быть (нет NC)"
    assert not any("lls_1" in s.flags for s in timeline), "lls_1 не должно быть активно (нет NC)"

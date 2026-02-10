# -*- coding: utf-8 -*-
"""
Тесты для варианта LS5 (Замыкание смежной РЦ)

Логика: Две ветки, учет замыкания (state 4, 7).
- Ветка 1 (Prev): 100 (prev занята+замкнута, центр свободен+замкнут) → 101 (обе заняты+замкнуты, центр свободен+замкнут)
- Ветка 2 (Next): 001 (next занята+замкнута, центр свободен+замкнут) → 101 (обе заняты+замкнуты, центр свободен+замкнут)

Завершение: центр занят (state 7) ≥ tkon_ls5 → закрытие
"""

from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig


def test_ls5_83_prev_branch_full_cycle():
    """
    Полный цикл LS5 на 83 (1-7СП) по ветке Prev (100 → 101).
    Используем состояния с замыканием: 7 (занята+замкнута), 4 (свободна+замкнута).
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="83",
        prev_rc_name="86",  # 1-3СП
        ctrl_rc_name="83",
        next_rc_name="81",  # 2П
        enable_lz1=False, enable_ls5=True,
        ts01_ls5=2.0, tlz_ls5=2.0, tkon_ls5=2.0,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-3с: Фаза 0 - Prev занята+замкнута (7), Ctrl свободна+замкнута (4), Next свободна (3)
        ScenarioStep(
            t=3.0,
            rc_states={"86": 7, "83": 4, "81": 3},
            switch_states={"150": 9}, # соединение 86
            signal_states={}, modes={},
        ),
        # 3-6с: Фаза 1 - Обе смежные заняты+замкнуты (7), Ctrl свободна+замкнута (4) → открытие
        ScenarioStep(
            t=3.0,
            rc_states={"86": 7, "83": 4, "81": 7},
            switch_states={"150": 9},
            signal_states={}, modes={},
        ),
        # 6-10с: Завершение - центр занят (7) → закрытие
        ScenarioStep(
            t=4.0,
            rc_states={"86": 7, "83": 7, "81": 7},
            switch_states={"150": 9},
            signal_states={}, modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="83")
    timeline = ctx.run()

    print("\n=== LS5 Test: 83 (1-7СП) - Prev Branch ===")
    for i, st in enumerate(timeline, start=1):
        print(f"{i}: t={st.t:.1f}, rc_86={st.rc_states.get('86',0)}, rc_83={st.rc_states.get('83',0)}, rc_81={st.rc_states.get('81',0)}, "
              f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}")

    assert any("lls_5_open" in s.flags for s in timeline), "Нет lls_5_open"
    assert any("lls_5" in s.flags and s.lz_variant == 105 for s in timeline), "LLS_5 не активна"
    assert any("lls_5_closed" in s.flags for s in timeline), "Нет lls_5_closed"


def test_ls5_108_next_branch_full_cycle():
    """
    Полный цикл LS5 на 108 (1П) по ветке Next (001 → 101).
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59", 
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False, enable_ls5=True,
        ts01_ls5=2.0, tlz_ls5=2.0, tkon_ls5=2.0,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-3с: Фаза 0 - Next занята+замкнута (7), Ctrl свободна+замкнута (4), Prev свободна (3)
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 4, "83": 7},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 3-6с: Фаза 1 - Обе смежные заняты+замкнуты (7), Ctrl свободна+замкнута (4) → открытие
        ScenarioStep(
            t=3.0,
            rc_states={"59": 7, "108": 4, "83": 7},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 6-10с: Завершение - центр занят (7) → закрытие
        ScenarioStep(
            t=4.0,
            rc_states={"59": 7, "108": 7, "83": 7},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()

    print("\n=== LS5 Test: 108 (1П) - Next Branch ===")
    for i, st in enumerate(timeline, start=1):
        print(f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59',0)}, rc_108={st.rc_states.get('108',0)}, rc_83={st.rc_states.get('83',0)}, "
              f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}")

    assert any("lls_5_open" in s.flags for s in timeline), "Нет lls_5_open"
    assert any("lls_5" in s.flags and s.lz_variant == 105 for s in timeline), "LLS_5 не активна"
    assert any("lls_5_closed" in s.flags for s in timeline), "Нет lls_5_closed"

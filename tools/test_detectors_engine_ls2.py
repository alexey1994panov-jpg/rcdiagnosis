# -*- coding: utf-8 -*-
"""
Тесты для варианта LS2 (Асимметричная ложная свободность)

LS2 детектирует ложную свободность по двум веткам:
- Ветка 1 (Prev): 110 → 100 → 110
- Ветка 2 (Next): 011 → 001 → 011

Фазы:
    0: (110 или 011) → ts01_ls2
    1: (100 или 001 - центр освободился) → tlz_ls2
    2: (110 или 011 - центр снова занят) → ts02_ls2 → открытие
    Завершение: все свободны ≥ tkon_ls2 → закрытие
"""

from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig


def test_ls2_108_prev_branch_full_cycle():
    """
    Полный цикл LS2 на 108 (1П) по ветке Prev (110 → 100 → 110).
    
    Сценарий:
    - 3 шага: 110 (10-12СП и 1П заняты)
    - 3 шага: 100 (10-12СП занята, 1П освободилась)
    - 4 шага: 110 (снова обе заняты) → открытие
    - 4 шага: 000 (все свободны) → закрытие
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",  # 10-12СП
        ctrl_rc_name="108",
        next_rc_name="83",  # 1-7СП
        enable_lz1=False, enable_lz2=False, enable_lz3=False,
        enable_ls2=True,
        ts01_ls2=2.0, tlz_ls2=2.0, ts02_ls2=2.0, tkon_ls2=3.0,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-3с: Фаза 0 - 110 (Prev=59, Ctrl=108)
        ScenarioStep(
            t=3.0,
            rc_states={"59": 6, "108": 6, "83": 3},
            switch_states={"110": 3, "88": 3}, # Соседи активны
            signal_states={}, modes={},
        ),
        # 3-6с: Фаза 1 - 100 (59 занята, 108 освободилась)
        ScenarioStep(
            t=3.0,
            rc_states={"59": 6, "108": 3, "83": 3},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 6-10с: Фаза 2 - 110 (снова заняты) → открытие
        ScenarioStep(
            t=4.0,
            rc_states={"59": 6, "108": 6, "83": 3},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 10-15с: Завершение - 000 (все свободны) → закрытие
        ScenarioStep(
            t=5.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()

    print("\n=== LS2 Test: 108 (1П) - Prev Branch ===")
    for i, st in enumerate(timeline, start=1):
        print(f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59',0)}, rc_108={st.rc_states.get('108',0)}, "
              f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}")

    assert any("lls_2_open" in s.flags for s in timeline), "Нет lls_2_open"
    assert any("lls_2" in s.flags and s.lz_variant == 102 for s in timeline), "LLS_2 не активна"
    assert any("lls_2_closed" in s.flags for s in timeline), "Нет lls_1_closed"


def test_ls2_59_next_branch_full_cycle():
    """
    Полный цикл LS2 на 59 (10-12СП) по ветке Next (011 → 001 → 011).
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",
        prev_rc_name="47", 
        ctrl_rc_name="59",
        next_rc_name="108",
        enable_lz1=False, enable_ls2=True,
        ts01_ls2=1.5, tlz_ls2=1.5, ts02_ls2=1.5, tkon_ls2=2.0,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-2с: Фаза 0 - 011 (Ctrl=59, Next=108)
        ScenarioStep(
            t=2.0,
            rc_states={"47": 3, "59": 6, "108": 6},
            switch_states={"110": 3},
            signal_states={}, modes={},
        ),
        # 2-4с: Фаза 1 - 001 (59 освободилась, 108 занята)
        ScenarioStep(
            t=2.0,
            rc_states={"47": 3, "59": 3, "108": 6},
            switch_states={"110": 3},
            signal_states={}, modes={},
        ),
        # 4-6с: Фаза 2 - 011 (снова заняты) → открытие
        ScenarioStep(
            t=2.0,
            rc_states={"47": 3, "59": 6, "108": 6},
            switch_states={"110": 3},
            signal_states={}, modes={},
        ),
        # 6-9с: Завершение - 000 → закрытие
        ScenarioStep(
            t=3.0,
            rc_states={"47": 3, "59": 3, "108": 3},
            switch_states={"110": 3},
            signal_states={}, modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="59")
    timeline = ctx.run()

    print("\n=== LS2 Test: 59 (10-12СП) - Next Branch ===")
    for i, st in enumerate(timeline, start=1):
        print(f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59',0)}, rc_108={st.rc_states.get('108',0)}, "
              f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}")

    assert any("lls_2_open" in s.flags for s in timeline), "Нет lls_2_open"
    assert any("lls_2" in s.flags and s.lz_variant == 102 for s in timeline), "LLS_2 не активна"
    assert any("lls_2_closed" in s.flags for s in timeline), "Нет lls_2_closed"

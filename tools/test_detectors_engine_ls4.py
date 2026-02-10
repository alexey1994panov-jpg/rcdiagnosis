# -*- coding: utf-8 -*-
"""
Тесты для варианта LS4 (Шунтовое движение)

Логика: Одна ветка, 3 фазы.
- Фаза 0: 111 (все три РЦ заняты) → ts01_ls4
- Фаза 1: 101 (края заняты, центр свободен) → tlz01_ls4
- Фаза 2: 111 (снова все три заняты) → tlz02_ls4 → открытие
- Завершение: все свободны ≥ tkon_ls4 → закрытие
"""

from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig


def test_ls4_108_full_cycle():
    """
    Полный цикл LS4 на 108 (1П).
    
    Сценарий:
    - 4 шага: 111 (59, 108, 83 заняты)
    - 4 шага: 101 (59 и 83 заняты, 108 свободна)
    - 6 шагов: 111 (все снова заняты) → открытие
    - 6 шагов: 000 (все свободны) → закрытие
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False, enable_ls4=True,
        ts01_ls4=3.0, tlz01_ls4=3.0, tlz02_ls4=3.0, tkon_ls4=3.0,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-4с: Фаза 0 - 111 (все заняты)
        ScenarioStep(
            t=4.0,
            rc_states={"59": 6, "108": 6, "83": 6},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 4-8с: Фаза 1 - 101 (края заняты, центр свободен)
        ScenarioStep(
            t=4.0,
            rc_states={"59": 6, "108": 3, "83": 6},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 8-14с: Фаза 2 - 111 (снова все заняты) → открытие
        ScenarioStep(
            t=6.0,
            rc_states={"59": 6, "108": 6, "83": 6},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 14-20с: Завершение - 000 (все свободны) → закрытие
        ScenarioStep(
            t=6.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()

    print("\n=== LS4 Test: 108 (1П) ===")
    for i, st in enumerate(timeline, start=1):
        print(f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59',0)}, rc_108={st.rc_states.get('108',0)}, rc_83={st.rc_states.get('83',0)}, "
              f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}")

    assert any("lls_4_open" in s.flags for s in timeline), "Нет lls_4_open"
    assert any("lls_4" in s.flags and s.lz_variant == 104 for s in timeline), "LLS_4 не активна"
    assert any("lls_4_closed" in s.flags for s in timeline), "Нет lls_4_closed"

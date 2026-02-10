# -*- coding: utf-8 -*-
from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig

def test_lz13_full_cycle_prev():
    """
    Тест LZ13 (ветка Prev).
    01: adj free+locked (4), ctrl free (3), sig closed (15)
    02: adj occ+locked (7), ctrl free (3), sig closed (15)
    КОГДА: adj occ+locked (7), ctrl occ (6), sig closed (15) -> открытие ЛЗ13
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",
        prev_rc_name="47", # Adj
        next_rc_name="57",
        enable_lz13=True,
        ts01_lz13=2.0,
        ts02_lz13=2.0,
        tlz_lz13=2.0,
        tkon_lz13=3.0,
        sig_lz13_prev="114", # Ч1
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-3с: Фаза 01 (adj free+locked=4)
        ScenarioStep(
            t=3.0,
            rc_states={"47": 4, "59": 3, "57": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
        # 3-6с: Фаза 02 (adj occ+locked=7, ctrl free=3)
        ScenarioStep(
            t=3.0,
            rc_states={"47": 7, "59": 3, "57": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
        # 6-9с: Фаза КОГДА (adj occ+locked=7, ctrl occ=6) -> открытие
        ScenarioStep(
            t=3.0,
            rc_states={"47": 7, "59": 6, "57": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
        # 9-13с: Свободна -> закрытие по tkon=3.0
        ScenarioStep(
            t=4.0,
            rc_states={"47": 3, "59": 3, "57": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="59",
    )

    timeline = ctx.run()

    print("\n=== LZ13 Test: 59 (branch Prev) ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_47={st.rc_states.get('47', 0)}, rc_59={st.rc_states.get('59', 0)}, "
            f"sig_114={st.signal_states.get('114', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("llz_v13_open" in s.flags for s in timeline), "Нет llz_v13_open"
    assert any("llz_v13" in s.flags and s.lz_variant == 13 for s in timeline), "llz_v13 без variant=13"
    assert any("llz_v13_closed" in s.flags for s in timeline), "Нет llz_v13_closed"

def test_lz13_no_open_not_locked():
    """
    LZ13 не должна открываться если adj не замкнута.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",
        prev_rc_name="47",
        enable_lz13=True,
        ts01_lz13=1.0, ts02_lz13=1.0, tlz_lz13=1.0, tkon_lz13=1.0,
        sig_lz13_prev="114",
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # adj free но НЕ замкнута (3 вместо 4)
        ScenarioStep(
            t=2.0,
            rc_states={"47": 3, "59": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
        # adj occ но НЕ замкнута (6 вместо 7)
        ScenarioStep(
            t=2.0,
            rc_states={"47": 6, "59": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
        # занятие ctrl
        ScenarioStep(
            t=2.0,
            rc_states={"47": 6, "59": 6},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="59")
    timeline = ctx.run()

    assert not any("llz_v13_open" in s.flags for s in timeline), "llz_v13_open без замыкания!"

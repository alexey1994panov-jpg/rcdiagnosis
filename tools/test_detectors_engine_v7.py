from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig


def test_v7_108_from_json_like_legacy():
    """
    Цикл v7 на 1П по шагам из JSON:
    1) 3 c свободности 1П
    2) 3 c занятости 1П
    3) 3 c свободности 1П
    Ожидаем: хотя бы один open/active/closed v3.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 1П (ID)
        prev_rc_name="10-12СП",    # имя
        ctrl_rc_name="1П",
        next_rc_name="1-7СП",
        ts01_lz1=0.0,              # v1 отключена
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        ts01_lz2=0.0,              # v2 отключена
        ts02_lz2=0.0,
        tlz_lz2=0.0,
        tkon_lz2=0.0,

        ts01_lz3=2.0,
        ts02_lz3=2.0,
        tlz_lz3=2.0,
        tkon_lz3=3.0,

        ts01_lz7=3.0,
        tlz_lz7=3.0,
        tkon_lz7=3.0,
        ts01_lz8 = 3.0,
    ts02_lz8 = 3.0,
    tlz_lz8 = 3.0,
    tkon_lz8 = 3.0,
	enable_lz8 = False,

        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz7=True,

    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # ДАНО: 1П свободна, стрелки не ведут (в минусе)
        ScenarioStep(
            t=35.0,
            rc_states={"10-12СП": 3, "1П": 3, "1-7СП": 3},
            switch_states={"87": 9, "88": 9, "110": 3},
            signal_states={},
            modes={},

        ),
        ScenarioStep(
            t=3.0,
            rc_states={"10-12СП": 3, "1П": 3, "1-7СП": 3},
            switch_states={"87": 9, "88": 9, "110": 3},
            signal_states={},
            modes={},

        ),
        # КОГДА: 1П занята, стрелки всё так же в минусе
        ScenarioStep(
            t=3.0,
            rc_states={"10-12СП": 3, "1П": 6, "1-7СП": 3},
            switch_states={"87": 9, "88": 9, "110": 3},
            signal_states={},
            modes={},
  
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"10-12СП": 3, "1П": 6, "1-7СП": 3},
            switch_states={"87": 9, "88": 9, "110": 3},
            signal_states={},
            modes={},

        ),
        # Завершение: 1П снова свободна, стрелки по‑прежнему в минусе
        ScenarioStep(
            t=15.0,
            rc_states={"10-12СП": 3, "1П": 3, "1-7СП": 3},
            switch_states={"87": 9, "88": 9, "110": 3},
            signal_states={},
            modes={},

        ),
        ScenarioStep(
            t=3.0,
            rc_states={"10-12СП": 3, "1П": 3, "1-7СП": 3},
            switch_states={"87": 9, "88": 9, "110": 3},
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

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("llz_v7_open" in s.flags for s in timeline)
    assert any("llz_v7" in s.flags and s.lz_variant == 7 for s in timeline)
    assert any("llz_v7_closed" in s.flags for s in timeline)


def test_v7_108_minus_branch_from_json():
    """
    Цикл v7 на 1П при движении по минусовому направлению:
    шаги полностью соответствуют второму JSON-сценарию.
    Ожидаем один полный цикл v3.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="10-12СП",
        ctrl_rc_name="1П",
        next_rc_name="1-7СП",
        ts01_lz1=0.0,
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        ts01_lz2=0.0,
        ts02_lz2=0.0,
        tlz_lz2=0.0,
        tkon_lz2=0.0,

        ts01_lz3=2.0,
        ts02_lz3=2.0,
        tlz_lz3=2.0,
        tkon_lz3=3.0,

        ts01_lz7=3.0,
        tlz_lz7=3.0,
        tkon_lz7=3.0,
        ts01_lz8 = 3.0,
    ts02_lz8 = 3.0,
    tlz_lz8 = 3.0,
    tkon_lz8 = 3.0,
	enable_lz8 = False,

        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz7=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # ДАНО: 1П свободна, стрелки не ведут (в минусе)
        ScenarioStep(
            t=35.0,
            rc_states={"10-12СП": 3, "1П": 3, "1-7СП": 3},
            switch_states={"87": 9, "88": 9, "110": 9},
            signal_states={},
            modes={},

        ),
        ScenarioStep(
            t=3.0,
            rc_states={"10-12СП": 3, "1П": 3, "1-7СП": 3},
            switch_states={"87": 9, "88": 9, "110": 9},
            signal_states={},
            modes={},

        ),
        # КОГДА: 1П занята, стрелки всё так же в минусе
        ScenarioStep(
            t=3.0,
            rc_states={"10-12СП": 3, "1П": 6, "1-7СП": 3},
            switch_states={"87": 9, "88": 9, "110": 9},
            signal_states={},
            modes={},
  
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"10-12СП": 3, "1П": 6, "1-7СП": 3},
            switch_states={"87": 9, "88": 9, "110": 9},
            signal_states={},
            modes={},

        ),
        # Завершение: 1П снова свободна, стрелки по‑прежнему в минусе
        ScenarioStep(
            t=15.0,
            rc_states={"10-12СП": 3, "1П": 3, "1-7СП": 3},
            switch_states={"87": 9, "88": 9, "110": 9},
            signal_states={},
            modes={},

        ),
        ScenarioStep(
            t=3.0,
            rc_states={"10-12СП": 3, "1П": 3, "1-7СП": 3},
            switch_states={"87": 9, "88": 9, "110": 9},
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

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("llz_v7_open" in s.flags for s in timeline)
    assert any("llz_v7" in s.flags and s.lz_variant == 7 for s in timeline)
    assert any("llz_v7_closed" in s.flags for s in timeline)

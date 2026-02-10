# -*- coding: utf-8 -*-
from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig

def test_v2_108_full_cycle_like_legacy():
    """
    Аналог старого simulate_1p для v2 на 108:
    ts01_lz2 = 2.0, ts02_lz2 = 2.0, tlz_lz2 = 2.0, tkon_lz2 = 3.0, шаг dt = 1.0.
    Ожидаем: есть open, есть активная ЛЗ v2, есть закрытие.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 108 (ID)
        prev_rc_name="59",   # имя
        ctrl_rc_name="108",
        next_rc_name="83",
        ts01_lz1=0.0,             # Отключаем v1
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=2.0,             # Тайминги для v2
        ts02_lz2=2.0,
        tlz_lz2=2.0,
        tkon_lz2=2.0,
        enable_lz2=True,
        ts01_lz3=3.0,
        tlz_lz3=3.0,
        ts02_lz3=3.0,
        tkon_lz3=3.0,
        enable_lz3=False,
        ts01_lz7 = 3.0,
        tlz_lz7 = 3.0,
        tkon_lz7 = 3.0,
        enable_lz7 = False,
        ts01_lz8 = 3.0,
    ts02_lz8 = 3.0,
    tlz_lz8 = 3.0,
    tkon_lz8 = 3.0,
	enable_lz8 = False,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    # ВАЖНО: rc_states задаём по ИМЕНАМ, как ожидает Variant2Detector.
    scenario = [
        # 0–2 c: 1-0-0 (фаза 1)
        ScenarioStep(
            t=1.0,
            rc_states={"59": 6, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"59": 6, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 2–4 c: 1-1-0 (фаза 2)
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"59": 6, "108": 6, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 4–6 c: 1-0-0 (фаза 3, открытие)
        ScenarioStep(
            t=4.0,
            rc_states={"59": 6, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=5.0,
            rc_states={"59": 6, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 6–9 c: 0-0-0 (завершение по tkon_lz2)
        ScenarioStep(
            t=6.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=7.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=8.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
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

    assert any("llz_v2_open" in s.flags for s in timeline), "Нет llz_v2_open"
    assert any("llz_v2" in s.flags and s.lz_variant == 2 for s in timeline), "llz_v2 без variant=2"
    assert any("llz_v2_closed" in s.flags for s in timeline), "Нет llz_v2_closed"

def test_v2_37_full_cycle_topology_controls_modes():
    """
    Полный цикл v2 на 37 (ctrl_rc_id='37'), где prev/next берутся из топологии.
    Цепочка:
      prev = 36
      ctrl = 37
      next = 62
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="37",          # 37 (ID)
        prev_rc_name="36",    # по инженерной логике
        ctrl_rc_name="37",
        next_rc_name="62",
        ts01_lz1=0.0,            # Отключаем v1
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=2.0,            # Тайминги для v2
        ts02_lz2=2.0,
        tlz_lz2=2.0,
        tkon_lz2=2.0,
        enable_lz2=True,
        ts01_lz3=3.0,
        tlz_lz3=3.0,
        ts02_lz3=3.0,
        tkon_lz3=3.0,
        enable_lz3=False,
        ts01_lz7 = 3.0,
        tlz_lz7 = 3.0,
        tkon_lz7 = 3.0,
        enable_lz7 = False,
        ts01_lz8 = 3.0,
    ts02_lz8 = 3.0,
    tlz_lz8 = 3.0,
    tkon_lz8 = 3.0,
	enable_lz8 = False,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0–2 c: 1-0-0 (фаза 1)
        ScenarioStep(
            t=3.0,
            rc_states={"36": 6, "37": 3, "62": 3},
            switch_states={"149": 3, "32": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"36": 6, "37": 3, "62": 3},
            switch_states={"149": 3, "32": 3},
            signal_states={},
            modes={},
        ),
        # 2–4 c: 1-1-0 (фаза 2)
        ScenarioStep(
            t=2.0,
            rc_states={"36": 6, "37": 6, "62": 3},
            switch_states={"149": 3, "32": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"36": 6, "37": 6, "62": 3},
            switch_states={"149": 15, "32": 15},
            signal_states={},
            modes={},
        ),
        # 4–6 c: 1-0-0 (фаза 3, открытие)
        ScenarioStep(
            t=4.0,
            rc_states={"36": 6, "37": 3, "62": 3},
            switch_states={"149": 3, "32": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=5.0,
            rc_states={"36": 6, "37": 3, "62": 3},
            switch_states={"149": 3, "32": 3},
            signal_states={},
            modes={},
        ),
        # 6–9 c: 0-0-0 (завершение по tkon_lz2)
        ScenarioStep(
            t=6.0,
            rc_states={"36": 3, "37": 3, "62": 3},
            switch_states={"149": 3, "32": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=7.0,
            rc_states={"36": 3, "37": 3, "62": 3},
            switch_states={"149": 3, "32": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=8.0,
            rc_states={"36": 3, "37": 3, "62": 3},
            switch_states={"149": 3, "32": 3},
            signal_states={},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="37",
    )

    timeline = ctx.run()

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}, "
            f"prev={st.effective_prev_rc}, next={st.effective_next_rc}"
        )

    assert any(st.effective_prev_rc for st in timeline), "Топология не видит prev для 37"
    assert any(st.effective_next_rc for st in timeline), "Топология не видит next для 37"

    assert any("llz_v2_open" in s.flags for s in timeline), "Для 37 нет llz_v2_open"
    assert any("llz_v2" in s.flags and s.lz_variant == 2 for s in timeline), "Для 37 llz_v2 без variant=2"
    assert any("llz_v2_closed" in s.flags for s in timeline), "Для 37 нет llz_v2_closed"

def test_v2_65_both_switches_no_control():
    """
    4П (ctrl_rc_id='65'), стрелки 2 и 16 без контроля.
    Ожидаем: топология не может гарантировать prev/next, v2 не формируется.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="65",        # 4П (ID)
        prev_rc_name="36",
        ctrl_rc_name="4П",
        next_rc_name="14-137",
        ts01_lz1=0.0,            # Отключаем v1
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=2.0,            # Тайминги для v2
        ts02_lz2=2.0,
        tlz_lz2=2.0,
        tkon_lz2=2.0,
        enable_lz2=True,
        ts01_lz3=3.0,
        tlz_lz3=3.0,
        ts02_lz3=3.0,
        tkon_lz3=3.0,
        enable_lz3=False,
        ts01_lz7 = 3.0,
        tlz_lz7 = 3.0,
        tkon_lz7 = 3.0,
        enable_lz7 = False,
        ts01_lz8 = 3.0,
    ts02_lz8 = 3.0,
    tlz_lz8 = 3.0,
    tkon_lz8 = 3.0,
	enable_lz8 = False,
    )
    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        ScenarioStep(
            t=5.0,
            rc_states={"36": 3, "4П": 3, "14-137": 3},
            switch_states={"32": 15, "73": 15},  # оба без контроля
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"36": 3, "4П": 6, "14-137": 3},
            switch_states={"32": 15, "73": 15},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=6.0,
            rc_states={"36": 3, "4П": 3, "14-137": 3},
            switch_states={"32": 15, "73": 15},
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

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}, "
            f"prev={st.effective_prev_rc}, next={st.effective_next_rc}"
        )

    assert not any("llz_v2" in st.flags for st in timeline)
    assert not any("llz_v2_open" in st.flags for st in timeline)
    assert not any("llz_v2_closed" in st.flags for st in timeline)

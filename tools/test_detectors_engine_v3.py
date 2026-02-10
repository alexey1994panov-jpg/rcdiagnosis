from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig


def test_v3_108_full_cycle_like_legacy():
    """
    Аналог старого теста для v3 на 108:
    ts01_lz3 = 2.0, ts02_lz3 = 2.0, tlz_lz3 = 2.0, tkon_lz3 = 3.0, шаг dt = 1.0.
    Ожидаем: есть open, есть активная ЛЗ v3, есть закрытие.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 108 (ID)
        prev_rc_name="59",    # имя
        ctrl_rc_name="108",
        next_rc_name="83",
        ts01_lz1=0.0,              # v1 отключена
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=0.0,              # v2 отключена
        ts02_lz2=0.0,
        tlz_lz2=0.0,
        tkon_lz2=0.0,
        enable_lz2=False,
        ts01_lz3=2.0,
        ts02_lz3=2.0,
        tlz_lz3=2.0,
        tkon_lz3=3.0,
        enable_lz3=True,
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

    # Сценарий из старого теста, адаптированный под v3
    scenario = [
        # 0–2 c: 1-0-1 (фаза 1)
        ScenarioStep(
            t=1.0,
            rc_states={"59": 6, "108": 3, "83": 6},
            switch_states={"87": 3, "88": 3, "110": 3},  # 1,5,10 в плюсе
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"59": 6, "108": 3, "83": 6},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 2–4 c: 1-1-1 (фаза 2)
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 6},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 6},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 4–6 c: 1-0-1 (фаза 3, открытие)
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 3, "83": 6},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 3, "83": 6},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 6–9 c: 0-0-0 (завершение по tkon_lz3)
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
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

    assert any("llz_v3_open" in s.flags for s in timeline), "Нет llz_v3_open"
    assert any("llz_v3" in s.flags and s.lz_variant == 3 for s in timeline), "llz_v3 без variant=3"
    assert any("llz_v3_closed" in s.flags for s in timeline), "Нет llz_v3_closed"


def test_v3_108_full_cycle_all_switches_no_control():
    """
    Тот же сценарий для 108, но все стрелки 1/5/10 на всех шагах в состоянии 15 (без контроля).
    Ожидаем: v3 не активируется, флагов llz_v3_* быть не должно.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        ts01_lz1=0.0,
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=0.0,
        ts02_lz2=0.0,
        tlz_lz2=0.0,
        tkon_lz2=0.0,
        enable_lz2=False,
        ts01_lz3=2.0,
        tlz_lz3=2.0,
        ts02_lz3=2.0,
        
        tkon_lz3=3.0,
        enable_lz3=True,
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

    # Тот же временной сценарий, но все стрелки без контроля (15)
    scenario = [
        ScenarioStep(
            t=1.0,
            rc_states={"59": 6, "108": 3, "83": 6},
            switch_states={"87": 15, "88": 15, "110": 15},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"59": 6, "108": 3, "83": 6},
            switch_states={"87": 15, "88": 15, "110": 15},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 6},
            switch_states={"87": 15, "88": 15, "110": 15},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 6},
            switch_states={"87": 15, "88": 15, "110": 15},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 3, "83": 6},
            switch_states={"87": 15, "88": 15, "110": 15},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 3, "83": 6},
            switch_states={"87": 15, "88": 15, "110": 15},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 15, "88": 15, "110": 15},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 15, "88": 15, "110": 15},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 15, "88": 15, "110": 15},
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

    assert not any("llz_v3_open" in s.flags for s in timeline)
    assert not any("llz_v3" in s.flags for s in timeline)
    assert not any("llz_v3_closed" in s.flags for s in timeline)


def test_v3_4sp_full_cycle_minus_branch():
    """
    Полный цикл v3 на 58 по минусовому направлению:
    58 <-> 37 через стрелку 4 в минусе, стрелка 6 тоже в минусе.
    Сценарий аналогичен 108: формируем фазу занятости и освобождения
    для проверки работы v3.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="58",          # 58 (ID по NODES)
        prev_rc_name="57",
        ctrl_rc_name="58",
        next_rc_name="37",
        ts01_lz1=0.0,
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=0.0,
        ts02_lz2=0.0,
        tlz_lz2=0.0,
        tkon_lz2=0.0,
        enable_lz2=False,
        ts01_lz3=2.0,
        ts02_lz3=2.0,
        tlz_lz3=2.0,
        tkon_lz3=3.0,
        enable_lz3=True,
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

    # 0–2 c: 57=свободна, 58=свободна, 37=занята (1-0-1 условно)
    # 2–4 c: 58 занята
    # 4–6 c: 58 снова свободна
    # 6–9 c: всё свободно (завершение по tkon_lz3)
    scenario = [
        # 0–2 с: начальная фаза
        ScenarioStep(
            t=3.0,
            rc_states={"57": 6, "58": 3, "37": 6},
            switch_states={"33": 9, "149": 9},  # 4 в минусе, 6 в минусе
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"57": 6, "58": 3, "37": 6},
            switch_states={"33": 9, "149": 9},
            signal_states={},
            modes={},
        ),
        # 2–4 с: 58 занята
        ScenarioStep(
            t=2.0,
            rc_states={"57": 6, "58": 6, "37": 6},
            switch_states={"33": 9, "149": 9},
            signal_states={},
            modes={},
        ),
        # 4–6 с: 58 снова свободна
        ScenarioStep(
            t=2.0,
            rc_states={"57": 6, "58": 3, "37": 6},
            switch_states={"33": 9, "149": 9},
            signal_states={},
            modes={},
        ),
        # 6–9 с: всё свободно
        ScenarioStep(
            t=3.0,
            rc_states={"57": 6, "58": 3, "37": 3},
            switch_states={"33": 9, "149": 9},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=6.0,
            rc_states={"57": 6, "58": 3, "37": 3},
            switch_states={"33": 9, "149": 9},
            signal_states={},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="58",
    )

    timeline = ctx.run()

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("llz_v3_open" in s.flags for s in timeline), "Нет llz_v3_open на 58"
    assert any("llz_v3" in s.flags and s.lz_variant == 3 for s in timeline), "llz_v3 без variant=3 на 58"
    assert any("llz_v3_closed" in s.flags for s in timeline), "Нет llz_v3_closed на 58"

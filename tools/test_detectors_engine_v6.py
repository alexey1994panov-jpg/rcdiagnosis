# -*- coding: utf-8 -*-
from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig


def test_v6_59_full_cycle():
    """
    Полный цикл v6 на 59 (1-7СП).
    ts01_lz6=2.0, tlz_lz6=2.0, tkon_lz6=2.0.
    Ожидаем: есть open, активная ЛЗ v6, есть closed.
    Соседи не требуются — NeighborRequirement.ONLY_CTRL.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",           # 1-7СП (ID)
        prev_rc_name=None,         # соседи не нужны
        ctrl_rc_name="59",
        next_rc_name=None,
        # Отключаем все остальные варианты
        ts01_lz1=0.0,
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=0.0,
        ts02_lz2=0.0,
        tlz_lz2=0.0,
        tkon_lz2=0.0,
        enable_lz2=False,
        ts01_lz3=0.0,
        ts02_lz3=0.0,
        tlz_lz3=0.0,
        tkon_lz3=0.0,
        enable_lz3=False,
        ts01_lz7=0.0,
        tlz_lz7=0.0,
        tkon_lz7=0.0,
        enable_lz7=False,
        ts01_lz8=0.0,
        ts02_lz8=0.0,
        tlz_lz8=0.0,
        tkon_lz8=0.0,
        enable_lz8=False,
        ts01_lz5=1.0,
        tlz_lz5=1.0,
        tkon_lz5=1.0,
        enable_lz5=False,
        ts01_lz6=2.0,
        tlz_lz6=2.0,
        tkon_lz6=2.0,
        enable_lz6=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0–2 с: ДАНО — ctrl free (3) ≥ ts01_lz6=2.0
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2–4 с: КОГДА — ctrl occupied (6) ≥ tlz_lz6=2.0 → open
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 4–6 с: Завершение — ctrl free (3) ≥ tkon_lz6=2.0 → closed
        ScenarioStep(
            t=2.0,
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

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("llz_v6_open" in s.flags for s in timeline), "Нет llz_v6_open"
    # ИСПРАВЛЕНО: variant == 6 (было 5)
    assert any("llz_v6" in s.flags and s.lz_variant == 6 for s in timeline), "llz_v6 без variant=6"
    assert any("llz_v6_closed" in s.flags for s in timeline), "Нет llz_v6_closed"


def test_v6_65_full_cycle():
    """
    Полный цикл v6 на 65 (4П) — v6 работает на ЛЮБОЙ РЦ, включая без can_lock.
    ts01_lz6=2.0, tlz_lz6=2.0, tkon_lz6=2.0.
    Ожидаем: есть open, активная ЛЗ v6, есть closed.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="65",           # 4П (ID), can_lock=False — но v6 всё равно работает!
        prev_rc_name=None,
        ctrl_rc_name="65",
        next_rc_name=None,
        # Отключаем все остальные варианты
        ts01_lz1=0.0,
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=0.0,
        ts02_lz2=0.0,
        tlz_lz2=0.0,
        tkon_lz2=0.0,
        enable_lz2=False,
        ts01_lz3=0.0,
        ts02_lz3=0.0,
        tlz_lz3=0.0,
        tkon_lz3=0.0,
        enable_lz3=False,
        ts01_lz7=0.0,
        tlz_lz7=0.0,
        tkon_lz7=0.0,
        enable_lz7=False,
        ts01_lz8=0.0,
        ts02_lz8=0.0,
        tlz_lz8=0.0,
        tkon_lz8=0.0,
        enable_lz8=False,
        ts01_lz5=1.0,
        tlz_lz5=1.0,
        tkon_lz5=1.0,
        enable_lz5=False,
        ts01_lz6=2.0,
        tlz_lz6=2.0,
        tkon_lz6=2.0,
        enable_lz6=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0–2 с: ДАНО — ctrl free (3)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2–4 с: КОГДА — ctrl occupied (6)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 4–6 с: Завершение — ctrl free (3)
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

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # ИСПРАВЛЕНО: v6 работает на любой РЦ, поэтому проверяем наличие событий
    assert any("llz_v6_open" in s.flags for s in timeline), "Нет llz_v6_open"
    assert any("llz_v6" in s.flags and s.lz_variant == 6 for s in timeline), "llz_v6 без variant=6"
    assert any("llz_v6_closed" in s.flags for s in timeline), "Нет llz_v6_closed"
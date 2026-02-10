# test_detectors_engine_v8.py

from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig


def test_v8_108_full_cycle_prev_branch():
    """
    Полный цикл v8 на 108, ветка В8.1 (prev занят):
    - Начальная фаза: 1-1-0 или 1-1-1 (prev и curr заняты) ≥ ts01
    - Вторая фаза: X-1-1 (curr и next заняты) ≥ ts02
    - Хвост: 0-1-0 ≥ tlz → открытие
    - Завершение: свободность ctrl ≥ tkon
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        # v1-v7 отключены
        ts01_lz1=0.0, tlz_lz1=0.0, tkon_lz1=0.0, enable_lz1=False,
        ts01_lz2=0.0, ts02_lz2=0.0, tlz_lz2=0.0, tkon_lz2=0.0, enable_lz2=False,
        ts01_lz3=0.0, ts02_lz3=0.0, tlz_lz3=0.0, tkon_lz3=0.0, enable_lz3=False,
        ts01_lz7=0.0, tlz_lz7=0.0, tkon_lz7=0.0, enable_lz7=False,
        # v8 включен
        ts01_lz8=2.0,
        ts02_lz8=2.0,
        tlz_lz8=2.0,
        tkon_lz8=3.0,
        enable_lz8=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-2 с: Начальная фаза 1-1-0 (prev и curr заняты, next свободен)
        # ВАЖНО: первый шаг должен иметь оба control_ok для seen_full_adj!
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 2-4 с: Вторая фаза 1-1-1 (все заняты)
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 6},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 4-6 с: Хвост 0-1-0 (prev и next свободны, curr занят)
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 6-9 с: Завершение — свободность ctrl
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 6-9 с: Завершение — свободность ctrl
        ScenarioStep(
            t=3.0,
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
    print(f"TIMELINE LENGTH: {len(timeline)}")  # ← ДОЛЖНО БЫТЬ > 0
    print(f"TIMELINE: {timeline}")  # ← Что внутри?

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("llz_v8_open" in s.flags for s in timeline), "Нет llz_v8_open"
    assert any("llz_v8" in s.flags and s.lz_variant == 8 for s in timeline), "llz_v8 без variant=8"
    assert any("llz_v8_closed" in s.flags for s in timeline), "Нет llz_v8_closed"


def test_v8_no_seen_full_adj_no_start():
    """
    Если не было шага с обоими достоверными (prev_control_ok и next_control_ok),
    v8 не должен стартовать даже при правильных масках.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        ts01_lz1=0.0, tlz_lz1=0.0, tkon_lz1=0.0, enable_lz1=False,
        ts01_lz2=0.0, ts02_lz2=0.0, tlz_lz2=0.0, tkon_lz2=0.0, enable_lz2=False,
        ts01_lz3=0.0, ts02_lz3=0.0, tlz_lz3=0.0, tkon_lz3=0.0, enable_lz3=False,
        ts01_lz7=0.0, tlz_lz7=0.0, tkon_lz7=0.0, enable_lz7=False,
        ts01_lz8=2.0, ts02_lz8=2.0, tlz_lz8=2.0, tkon_lz8=3.0, enable_lz8=True,
    )
    

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # Шаги с полными масками, но без seen_full_adj
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 3},  # 1-1-0
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},  # только prev!
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 6},  # 1-1-1
            switch_states={"87": 3, "88": 3, "110": 9},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 6, "83": 3},  # 0-1-0
            switch_states={"87": 3, "88": 3, "110": 9},
            signal_states={},
            modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()
    

    # v8 не должен активироваться
    assert not any("llz_v8" in s.flags for s in timeline)
    assert not any("llz_v8_open" in s.flags for s in timeline)


def test_v8_108_full_cycle_next_branch():
    """
    Цикл v8, ветка В8.2 (next занят):
    - p1: X-1-1 (curr и next заняты)
    - p2: 0-1-X или X-1-0 (альтернативы)
    - tail: 0-1-0
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        ts01_lz1=0.0, tlz_lz1=0.0, tkon_lz1=0.0, enable_lz1=False,
        ts01_lz2=0.0, ts02_lz2=0.0, tlz_lz2=0.0, tkon_lz2=0.0, enable_lz2=False,
        ts01_lz3=0.0, ts02_lz3=0.0, tlz_lz3=0.0, tkon_lz3=0.0, enable_lz3=False,
        ts01_lz7=0.0, tlz_lz7=0.0, tkon_lz7=0.0, enable_lz7=False,
        ts01_lz8=2.0, ts02_lz8=2.0, tlz_lz8=2.0, tkon_lz8=3.0, enable_lz8=True,
    )
    print(f"V8 ENABLED: {det_cfg.enable_lz8}") 

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-2 с: p1 — X-1-1 (curr и next заняты, prev любой)
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 6, "83": 6},  # 0-1-1
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 2-4 с: p2 — 0-1-X (prev свободен, curr занят, next любой)
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 6, "83": 6},  # 0-1-1 (prev свободен!)
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 4-6 с: tail — 0-1-0
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 6-9 с: завершение
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 6-9 с: завершение
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
   
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()
    print(f"TIMELINE LENGTH: {len(timeline)}")  # ← ДОЛЖНО БЫТЬ > 0
    print(f"TIMELINE: {timeline}")  # ← Что внутри?

    print(f"Checking llz_v8_open: {any('llz_v8_open' in s.flags for s in timeline)}")
    assert any("llz_v8_open" in s.flags for s in timeline)
    print(f"Checking lz_variant==8: {any('llz_v8' in s.flags and s.lz_variant == 8 for s in timeline)}")
    assert any("llz_v8" in s.flags and s.lz_variant == 8 for s in timeline)
    print(f"Checking llz_v8_closed: {any('llz_v8_closed' in s.flags for s in timeline)}")
    assert any("llz_v8_closed" in s.flags for s in timeline)
# -*- coding: utf-8 -*-
from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig

def test_lz11_full_cycle():
    """
    Тест LZ11.
    ДАНО: ctrl свободна, sigA=15(closed), sigB=15(closed)
    КОГДА: ctrl занята, sigA=15(closed), sigB=15(closed) -> открытие ЛЗ11
    Завершение: ctrl свободна
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",
        ctrl_rc_name="59",
        enable_lz11=True,
        ts01_lz11=2.0,
        tlz_lz11=2.0,
        tkon_lz11=3.0,
        sig_lz11_a="114", # Ч1
        sig_lz11_b="107", # НМ1
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-3с: ДАНО (свободна + сигналы закрыты)
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3},
            switch_states={},
            signal_states={"114": 15, "107": 15},
            modes={},
        ),
        # 3-6с: КОГДА (занята + сигналы закрыты) -> открытие
        ScenarioStep(
            t=6.0,
            rc_states={"59": 6},
            switch_states={},
            signal_states={"114": 15, "107": 15},
            modes={},
        ),
        # 6-10с: Свободна -> закрытие по tkon=3.0
        ScenarioStep(
            t=10.0,
            rc_states={"59": 3},
            switch_states={},
            signal_states={"114": 15, "107": 15},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="59",
    )

    timeline = ctx.run()

    print("\n=== LZ11 Test: 59 ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59', 0)}, "
            f"sig_114={st.signal_states.get('114', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("llz_v11_open" in s.flags for s in timeline), "Нет llz_v11_open"
    assert any("llz_v11" in s.flags and s.lz_variant == 11 for s in timeline), "llz_v11 без variant=11"
    assert any("llz_v11_closed" in s.flags for s in timeline), "Нет llz_v11_closed"

def test_lz11_no_open_signal_open():
    """
    LZ11 не должна открываться если один из сигналов открыт.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",
        ctrl_rc_name="59",
        enable_lz11=True,
        ts01_lz11=2.0,
        tlz_lz11=2.0,
        tkon_lz11=3.0,
        sig_lz11_a="114", # Ч1 (Train)
        sig_lz11_b="107", # НМ1 (Train)
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # sigA открыт (3 для поездного - это Желтый/Разрешающий)
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3},
            switch_states={},
            signal_states={"114": 3, "107": 15},
            modes={},
        ),
        # занятие
        ScenarioStep(
            t=3.0,
            rc_states={"59": 6},
            switch_states={},
            signal_states={"114": 3, "107": 15},
            modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="59")
    timeline = ctx.run()

    # С учетом исправления в _is_signal_closed, стейт 3 для поездного сигнала 114 НЕ считается закрытым.
    assert not any("llz_v11_open" in s.flags for s in timeline), "llz_v11_open при открытом сигнале!"

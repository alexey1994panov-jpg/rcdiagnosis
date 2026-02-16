# -*- coding: utf-8 -*-
from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig

def test_lz10_full_cycle_to_next():
    """
    РўРµСЃС‚ LZ10 (РЅР°РїСЂР°РІР»РµРЅРёРµ to_next).
    P01: prev free (3), ctrl occ (6), next free (3), sig open (3)
    P02: prev free (3), ctrl occ (6), next occ (6), sig open (3)
    P03: prev free (3), ctrl occ (6), next occ (6), sig closed (15)
    РљРћР“Р”Рђ: prev free (3), ctrl occ (6), next free (3), sig closed (15) -> РѕС‚РєСЂС‹С‚РёРµ Р›Р—10
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        next_rc_name="83",
        enable_lz10=True,
        ts01_lz10=1.0,
        ts02_lz10=1.0,
        ts03_lz10=1.0,
        tlz_lz10=1.0,
        tkon_lz10=2.0,
        sig_lz10_to_next="114", # Р§1
        sig_lz11_a="999", # Dummy to avoid conflicts if any
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # Phase 01: 0-2СЃ
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            switch_states={"110": 3, "88": 3},
            signal_states={"114": 3},
            modes={},
        ),
        # Phase 02: 2-4СЃ
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 6, "83": 6},
            switch_states={"110": 3, "88": 3},
            signal_states={"114": 3},
            modes={},
        ),
        # Phase 03: 4-6СЃ
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 6, "83": 6},
            switch_states={"110": 3, "88": 3},
            signal_states={"114": 15},
            modes={},
        ),
        # Phase РљРћР“Р”Рђ: 6-8СЃ -> РѕС‚РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            switch_states={"110": 3, "88": 3},
            signal_states={"114": 15},
            modes={},
        ),
        # Р—Р°РІРµСЂС€РµРЅРёРµ: 8-11СЃ -> Р·Р°РєСЂС‹С‚РёРµ РїРѕ tkon=2.0
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"110": 3, "88": 3},
            signal_states={"114": 15},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="108",
    )

    timeline = ctx.run()

    print("\n=== LZ10 Test: 108 (to_next) ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_108={st.rc_states.get('108', 0)}, "
            f"sig_114={st.signal_states.get('114', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("llz_v10_open" in s.flags for s in timeline), "РќРµС‚ llz_v10_open"
    assert any("llz_v10" in s.flags and s.lz_variant == 10 for s in timeline), "llz_v10 Р±РµР· variant=10"
    assert any("llz_v10_closed" in s.flags for s in timeline), "РќРµС‚ llz_v10_closed"



# -*- coding: utf-8 -*-
"""
РўРµСЃС‚С‹ РґР»СЏ РІР°СЂРёР°РЅС‚Р° LS4 (РЁСѓРЅС‚РѕРІРѕРµ РґРІРёР¶РµРЅРёРµ)

Р›РѕРіРёРєР°: РћРґРЅР° РІРµС‚РєР°, 3 С„Р°Р·С‹.
- Р¤Р°Р·Р° 0: 111 (РІСЃРµ С‚СЂРё Р Р¦ Р·Р°РЅСЏС‚С‹) в†’ ts01_ls4
- Р¤Р°Р·Р° 1: 101 (РєСЂР°СЏ Р·Р°РЅСЏС‚С‹, С†РµРЅС‚СЂ СЃРІРѕР±РѕРґРµРЅ) в†’ tlz01_ls4
- Р¤Р°Р·Р° 2: 111 (СЃРЅРѕРІР° РІСЃРµ С‚СЂРё Р·Р°РЅСЏС‚С‹) в†’ ts02_ls4 в†’ РѕС‚РєСЂС‹С‚РёРµ
- Р—Р°РІРµСЂС€РµРЅРёРµ: РІСЃРµ СЃРІРѕР±РѕРґРЅС‹ в‰Ґ tkon_ls4 в†’ Р·Р°РєСЂС‹С‚РёРµ
"""

from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_ls4_108_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» LS4 РЅР° 108 (1Рџ).
    
    РЎС†РµРЅР°СЂРёР№:
    - 4 С€Р°РіР°: 111 (59, 108, 83 Р·Р°РЅСЏС‚С‹)
    - 4 С€Р°РіР°: 101 (59 Рё 83 Р·Р°РЅСЏС‚С‹, 108 СЃРІРѕР±РѕРґРЅР°)
    - 6 С€Р°РіРѕРІ: 111 (РІСЃРµ СЃРЅРѕРІР° Р·Р°РЅСЏС‚С‹) в†’ РѕС‚РєСЂС‹С‚РёРµ
    - 6 С€Р°РіРѕРІ: 000 (РІСЃРµ СЃРІРѕР±РѕРґРЅС‹) в†’ Р·Р°РєСЂС‹С‚РёРµ
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False, enable_ls4=True,
        ts01_ls4=3.0, tlz01_ls4=3.0, ts02_ls4=3.0, tlz02_ls4=10.0, tkon_ls4=3.0,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-4СЃ: Р¤Р°Р·Р° 0 - 111 (РІСЃРµ Р·Р°РЅСЏС‚С‹)
        ScenarioStep(
            t=4.0,
            rc_states={"59": 6, "108": 6, "83": 6},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 4-8СЃ: Р¤Р°Р·Р° 1 - 101 (РєСЂР°СЏ Р·Р°РЅСЏС‚С‹, С†РµРЅС‚СЂ СЃРІРѕР±РѕРґРµРЅ)
        ScenarioStep(
            t=4.0,
            rc_states={"59": 6, "108": 3, "83": 6},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 8-14СЃ: Р¤Р°Р·Р° 2 - 111 (СЃРЅРѕРІР° РІСЃРµ Р·Р°РЅСЏС‚С‹) в†’ РѕС‚РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=6.0,
            rc_states={"59": 6, "108": 6, "83": 6},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 14-17СЃ: РґР°РµРј Р·Р°РЅСЏС‚РѕСЃС‚СЊ ctrl РґР»СЏ Р·Р°РІРµСЂС€РµРЅРёСЏ РїРѕ tkon
        ScenarioStep(
            t=3.0,
            rc_states={"59": 6, "108": 6, "83": 6},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 17-20СЃ: РїРѕС‚РѕРј СѓР¶Рµ СЃРІРѕР±РѕРґРЅРѕРµ СЃРѕСЃС‚РѕСЏРЅРёРµ
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()

    print("\n=== LS4 Test: 108 (1Рџ) ===")
    for i, st in enumerate(timeline, start=1):
        print(f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59',0)}, rc_108={st.rc_states.get('108',0)}, rc_83={st.rc_states.get('83',0)}, "
              f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}")

    assert any("lls_4_open" in s.flags for s in timeline), "РќРµС‚ lls_4_open"
    assert timeline[-1].lz_state is False, "LS4 must end inactive by the end of scenario"


def test_ls4_opens_when_phase2_in_window():
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False,
        enable_ls4=True,
        ts01_ls4=2.0,
        tlz01_ls4=2.0,
        tlz02_ls4=4.0,
        ts02_ls4=2.0,
        tkon_ls4=2.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)
    scenario = [
        ScenarioStep(t=2.0, rc_states={"59": 6, "108": 6, "83": 6}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        ScenarioStep(t=3.0, rc_states={"59": 6, "108": 3, "83": 6}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        ScenarioStep(t=2.0, rc_states={"59": 6, "108": 6, "83": 6}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
    ]
    timeline = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108").run()
    assert any("lls_4_open" in s.flags for s in timeline), "LS4 must open when phase2 is within [tlz01, tlz02]"


def test_ls4_does_not_open_when_phase2_exceeds_upper_window():
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False,
        enable_ls4=True,
        ts01_ls4=2.0,
        tlz01_ls4=2.0,
        tlz02_ls4=4.0,
        ts02_ls4=2.0,
        tkon_ls4=2.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)
    scenario = [
        ScenarioStep(t=2.0, rc_states={"59": 6, "108": 6, "83": 6}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        ScenarioStep(t=5.0, rc_states={"59": 6, "108": 3, "83": 6}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        ScenarioStep(t=2.0, rc_states={"59": 6, "108": 6, "83": 6}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
    ]
    timeline = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108").run()
    assert not any("lls_4_open" in s.flags for s in timeline), "LS4 must not open when phase2 exceeds tlz02_ls4"


def test_ls4_user_like_1p_opens_and_closes_by_tkon():
    """
    User-like scenario on 1P (108):
    - 111 for 4s (phase A satisfied)
    - 101 for 4s (inside [tlz01, tlz02])
    - 111 for 6s (open + enough occupied time to close by tkon=5)
    - then free tail
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False,
        enable_ls4=True,
        ts01_ls4=2.0,
        ts02_ls4=2.0,
        tlz01_ls4=2.0,
        tlz02_ls4=10.0,
        tkon_ls4=5.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = []
    for _ in range(4):
        scenario.append(
            ScenarioStep(
                t=1.0,
                rc_states={"59": 6, "108": 6, "83": 6},
                switch_states={"110": 3, "88": 3},
                signal_states={},
                modes={},
            )
        )
    for _ in range(4):
        scenario.append(
            ScenarioStep(
                t=1.0,
                rc_states={"59": 6, "108": 3, "83": 6},
                switch_states={"110": 3, "88": 3},
                signal_states={},
                modes={},
            )
        )
    for _ in range(6):
        scenario.append(
            ScenarioStep(
                t=1.0,
                rc_states={"59": 6, "108": 6, "83": 6},
                switch_states={"110": 3, "88": 3},
                signal_states={},
                modes={},
            )
        )
    for _ in range(2):
        scenario.append(
            ScenarioStep(
                t=1.0,
                rc_states={"59": 6, "108": 3, "83": 6},
                switch_states={"110": 3, "88": 3},
                signal_states={},
                modes={},
            )
        )

    timeline = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108").run()
    open_idx = next((i for i, s in enumerate(timeline) if "lls_4_open" in s.flags), None)
    close_idx = next((i for i, s in enumerate(timeline) if "lls_4_closed" in s.flags), None)

    assert open_idx is not None, "LS4 must open in user-like scenario"
    assert close_idx is not None, "LS4 must close by tkon in user-like scenario"
    assert close_idx > open_idx, "Close must happen after open"


# -*- coding: utf-8 -*-
from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_lz4_next_nc_branch_endpoint_81():
    """
    LZ4 (РІРµС‚РєР° NextNC): ctrl=81 (РќРџ, РєСЂР°Р№РЅСЏСЏ Р Р¦), next_nc=True.
    РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ РїСЂРё Р·Р°РєСЂС‹С‚РѕРј СЃРёРіРЅР°Р»Рµ РЅР° СЃС‚РѕСЂРѕРЅРµ NC С„РѕСЂРјРёСЂСѓРµС‚СЃСЏ LLZ v4.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="81",
        enable_lz4=True,
        ts01_lz4=2.0,
        tlz_lz4=1.0,
        tkon_lz4=2.0,
        sig_lz4_ctrl_to_next="78",  # Рќ
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        ScenarioStep(
            t=3.0,
            rc_states={"81": 3, "83": 3},
            switch_states={},
            signal_states={"78": 15},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"81": 6, "83": 3},
            switch_states={},
            signal_states={"78": 15},
            modes={},
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"81": 3, "83": 3},
            switch_states={},
            signal_states={"78": 15},
            modes={},
        ),
    ]

    timeline = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="81").run()

    assert any("llz_v4_open" in s.flags for s in timeline), "РќРµС‚ llz_v4_open"
    assert any("llz_v4" in s.flags and s.lz_variant == 4 for s in timeline), "РќРµС‚ Р°РєС‚РёРІРЅРѕРіРѕ llz_v4 (variant=4)"
    assert any("llz_v4_closed" in s.flags for s in timeline), "РќРµС‚ llz_v4_closed"


def test_lz4_prev_nc_branch_endpoint_40():
    """
    LZ4 (РІРµС‚РєР° PrevNC): ctrl=40 (Р§Рџ, РєСЂР°Р№РЅСЏСЏ Р Р¦), prev_nc=True.
    РџСЂРѕРІРµСЂСЏРµРј С„РѕСЂРјРёСЂРѕРІР°РЅРёРµ РїСЂРё Р·Р°РєСЂС‹С‚РѕРј СЃРёРіРЅР°Р»Рµ РЅР° СЃС‚РѕСЂРѕРЅРµ NC.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="40",
        enable_lz4=True,
        ts01_lz4=2.0,
        tlz_lz4=1.0,
        tkon_lz4=2.0,
        sig_lz4_prev_to_ctrl="42",  # Р§
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        ScenarioStep(
            t=3.0,
            rc_states={"40": 3, "36": 3},
            switch_states={},
            signal_states={"42": 15},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"40": 6, "36": 3},
            switch_states={},
            signal_states={"42": 15},
            modes={},
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"40": 3, "36": 3},
            switch_states={},
            signal_states={"42": 15},
            modes={},
        ),
    ]

    timeline = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="40").run()

    assert any("llz_v4_open" in s.flags for s in timeline), "РќРµС‚ llz_v4_open"
    assert any("llz_v4" in s.flags and s.lz_variant == 4 for s in timeline), "РќРµС‚ Р°РєС‚РёРІРЅРѕРіРѕ llz_v4 (variant=4)"
    assert any("llz_v4_closed" in s.flags for s in timeline), "РќРµС‚ llz_v4_closed"



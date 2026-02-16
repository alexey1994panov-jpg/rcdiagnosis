# -*- coding: utf-8 -*-
from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig

def test_v2_108_full_cycle_like_legacy():
    """
    РђРЅР°Р»РѕРі СЃС‚Р°СЂРѕРіРѕ simulate_1p РґР»СЏ v2 РЅР° 108:
    ts01_lz2 = 2.0, ts02_lz2 = 2.0, tlz_lz2 = 2.0, tkon_lz2 = 3.0, С€Р°Рі dt = 1.0.
    РћР¶РёРґР°РµРј: РµСЃС‚СЊ open, РµСЃС‚СЊ Р°РєС‚РёРІРЅР°СЏ Р›Р— v2, РµСЃС‚СЊ Р·Р°РєСЂС‹С‚РёРµ.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 108 (ID)
        prev_rc_name="59",   # РёРјСЏ
        ctrl_rc_name="108",
        next_rc_name="83",
        ts01_lz1=0.0,             # РћС‚РєР»СЋС‡Р°РµРј v1
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=2.0,             # РўР°Р№РјРёРЅРіРё РґР»СЏ v2
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

    # Р’РђР–РќРћ: rc_states Р·Р°РґР°С‘Рј РїРѕ РРњР•РќРђРњ, РєР°Рє РѕР¶РёРґР°РµС‚ Variant2Detector.
    scenario = [
        # 0вЂ“2 c: 1-0-0 (С„Р°Р·Р° 1)
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
        # 2вЂ“4 c: 1-1-0 (С„Р°Р·Р° 2)
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
        # 4вЂ“6 c: 1-0-0 (С„Р°Р·Р° 3, РѕС‚РєСЂС‹С‚РёРµ)
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
        # 6вЂ“9 c: 0-0-0 (Р·Р°РІРµСЂС€РµРЅРёРµ РїРѕ tkon_lz2)
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

    assert any("llz_v2_open" in s.flags for s in timeline), "РќРµС‚ llz_v2_open"
    assert any("llz_v2" in s.flags and s.lz_variant == 2 for s in timeline), "llz_v2 Р±РµР· variant=2"
    assert any("llz_v2_closed" in s.flags for s in timeline), "РќРµС‚ llz_v2_closed"

def test_v2_37_full_cycle_topology_controls_modes():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» v2 РЅР° 37 (ctrl_rc_id='37'), РіРґРµ prev/next Р±РµСЂСѓС‚СЃСЏ РёР· С‚РѕРїРѕР»РѕРіРёРё.
    Р¦РµРїРѕС‡РєР°:
      prev = 36
      ctrl = 37
      next = 62
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="37",          # 37 (ID)
        prev_rc_name="36",    # РїРѕ РёРЅР¶РµРЅРµСЂРЅРѕР№ Р»РѕРіРёРєРµ
        ctrl_rc_name="37",
        next_rc_name="62",
        ts01_lz1=0.0,            # РћС‚РєР»СЋС‡Р°РµРј v1
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=2.0,            # РўР°Р№РјРёРЅРіРё РґР»СЏ v2
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
        # 0вЂ“2 c: 1-0-0 (С„Р°Р·Р° 1)
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
        # 2вЂ“4 c: 1-1-0 (С„Р°Р·Р° 2)
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
        # 4вЂ“6 c: 1-0-0 (С„Р°Р·Р° 3, РѕС‚РєСЂС‹С‚РёРµ)
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
        # 6вЂ“9 c: 0-0-0 (Р·Р°РІРµСЂС€РµРЅРёРµ РїРѕ tkon_lz2)
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

    assert any(st.effective_prev_rc for st in timeline), "РўРѕРїРѕР»РѕРіРёСЏ РЅРµ РІРёРґРёС‚ prev РґР»СЏ 37"
    assert any(st.effective_next_rc for st in timeline), "РўРѕРїРѕР»РѕРіРёСЏ РЅРµ РІРёРґРёС‚ next РґР»СЏ 37"

    assert any("llz_v2_open" in s.flags for s in timeline), "Р”Р»СЏ 37 РЅРµС‚ llz_v2_open"
    assert any("llz_v2" in s.flags and s.lz_variant == 2 for s in timeline), "Р”Р»СЏ 37 llz_v2 Р±РµР· variant=2"
    assert any("llz_v2_closed" in s.flags for s in timeline), "Р”Р»СЏ 37 РЅРµС‚ llz_v2_closed"

def test_v2_65_both_switches_no_control():
    """
    4Рџ (ctrl_rc_id='65'), СЃС‚СЂРµР»РєРё 2 Рё 16 Р±РµР· РєРѕРЅС‚СЂРѕР»СЏ.
    РћР¶РёРґР°РµРј: С‚РѕРїРѕР»РѕРіРёСЏ РЅРµ РјРѕР¶РµС‚ РіР°СЂР°РЅС‚РёСЂРѕРІР°С‚СЊ prev/next, v2 РЅРµ С„РѕСЂРјРёСЂСѓРµС‚СЃСЏ.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="65",        # 4Рџ (ID)
        prev_rc_name="36",
        ctrl_rc_name="4Рџ",
        next_rc_name="14-137",
        ts01_lz1=0.0,            # РћС‚РєР»СЋС‡Р°РµРј v1
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=2.0,            # РўР°Р№РјРёРЅРіРё РґР»СЏ v2
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
            rc_states={"36": 3, "4Рџ": 3, "14-137": 3},
            switch_states={"32": 15, "73": 15},  # РѕР±Р° Р±РµР· РєРѕРЅС‚СЂРѕР»СЏ
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"36": 3, "4Рџ": 6, "14-137": 3},
            switch_states={"32": 15, "73": 15},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=6.0,
            rc_states={"36": 3, "4Рџ": 3, "14-137": 3},
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


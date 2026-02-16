from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_v3_108_full_cycle_like_legacy():
    """
    РђРЅР°Р»РѕРі СЃС‚Р°СЂРѕРіРѕ С‚РµСЃС‚Р° РґР»СЏ v3 РЅР° 108:
    ts01_lz3 = 2.0, ts02_lz3 = 2.0, tlz_lz3 = 2.0, tkon_lz3 = 3.0, С€Р°Рі dt = 1.0.
    РћР¶РёРґР°РµРј: РµСЃС‚СЊ open, РµСЃС‚СЊ Р°РєС‚РёРІРЅР°СЏ Р›Р— v3, РµСЃС‚СЊ Р·Р°РєСЂС‹С‚РёРµ.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 108 (ID)
        prev_rc_name="59",    # РёРјСЏ
        ctrl_rc_name="108",
        next_rc_name="83",
        ts01_lz1=0.0,              # v1 РѕС‚РєР»СЋС‡РµРЅР°
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=0.0,              # v2 РѕС‚РєР»СЋС‡РµРЅР°
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

    # РЎС†РµРЅР°СЂРёР№ РёР· СЃС‚Р°СЂРѕРіРѕ С‚РµСЃС‚Р°, Р°РґР°РїС‚РёСЂРѕРІР°РЅРЅС‹Р№ РїРѕРґ v3
    scenario = [
        # 0вЂ“2 c: 1-0-1 (С„Р°Р·Р° 1)
        ScenarioStep(
            t=1.0,
            rc_states={"59": 6, "108": 3, "83": 6},
            switch_states={"87": 3, "88": 3, "110": 3},  # 1,5,10 РІ РїР»СЋСЃРµ
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
        # 2вЂ“4 c: 1-1-1 (С„Р°Р·Р° 2)
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
        # 4вЂ“6 c: 1-0-1 (С„Р°Р·Р° 3, РѕС‚РєСЂС‹С‚РёРµ)
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
        # 6вЂ“9 c: 0-0-0 (Р·Р°РІРµСЂС€РµРЅРёРµ РїРѕ tkon_lz3)
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

    assert any("llz_v3_open" in s.flags for s in timeline), "РќРµС‚ llz_v3_open"
    assert any("llz_v3" in s.flags and s.lz_variant == 3 for s in timeline), "llz_v3 Р±РµР· variant=3"
    assert any("llz_v3_closed" in s.flags for s in timeline), "РќРµС‚ llz_v3_closed"


def test_v3_108_full_cycle_all_switches_no_control():
    """
    РўРѕС‚ Р¶Рµ СЃС†РµРЅР°СЂРёР№ РґР»СЏ 108, РЅРѕ РІСЃРµ СЃС‚СЂРµР»РєРё 1/5/10 РЅР° РІСЃРµС… С€Р°РіР°С… РІ СЃРѕСЃС‚РѕСЏРЅРёРё 15 (Р±РµР· РєРѕРЅС‚СЂРѕР»СЏ).
    РћР¶РёРґР°РµРј: v3 РЅРµ Р°РєС‚РёРІРёСЂСѓРµС‚СЃСЏ, С„Р»Р°РіРѕРІ llz_v3_* Р±С‹С‚СЊ РЅРµ РґРѕР»Р¶РЅРѕ.
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

    # РўРѕС‚ Р¶Рµ РІСЂРµРјРµРЅРЅРѕР№ СЃС†РµРЅР°СЂРёР№, РЅРѕ РІСЃРµ СЃС‚СЂРµР»РєРё Р±РµР· РєРѕРЅС‚СЂРѕР»СЏ (15)
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
    РџРѕР»РЅС‹Р№ С†РёРєР» v3 РЅР° 58 РїРѕ РјРёРЅСѓСЃРѕРІРѕРјСѓ РЅР°РїСЂР°РІР»РµРЅРёСЋ:
    58 <-> 37 С‡РµСЂРµР· СЃС‚СЂРµР»РєСѓ 4 РІ РјРёРЅСѓСЃРµ, СЃС‚СЂРµР»РєР° 6 С‚РѕР¶Рµ РІ РјРёРЅСѓСЃРµ.
    РЎС†РµРЅР°СЂРёР№ Р°РЅР°Р»РѕРіРёС‡РµРЅ 108: С„РѕСЂРјРёСЂСѓРµРј С„Р°Р·Сѓ Р·Р°РЅСЏС‚РѕСЃС‚Рё Рё РѕСЃРІРѕР±РѕР¶РґРµРЅРёСЏ
    РґР»СЏ РїСЂРѕРІРµСЂРєРё СЂР°Р±РѕС‚С‹ v3.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="58",          # 58 (ID РїРѕ NODES)
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

    # 0вЂ“2 c: 57=СЃРІРѕР±РѕРґРЅР°, 58=СЃРІРѕР±РѕРґРЅР°, 37=Р·Р°РЅСЏС‚Р° (1-0-1 СѓСЃР»РѕРІРЅРѕ)
    # 2вЂ“4 c: 58 Р·Р°РЅСЏС‚Р°
    # 4вЂ“6 c: 58 СЃРЅРѕРІР° СЃРІРѕР±РѕРґРЅР°
    # 6вЂ“9 c: РІСЃС‘ СЃРІРѕР±РѕРґРЅРѕ (Р·Р°РІРµСЂС€РµРЅРёРµ РїРѕ tkon_lz3)
    scenario = [
        # 0вЂ“2 СЃ: РЅР°С‡Р°Р»СЊРЅР°СЏ С„Р°Р·Р°
        ScenarioStep(
            t=3.0,
            rc_states={"57": 6, "58": 3, "37": 6},
            switch_states={"33": 9, "149": 9},  # 4 РІ РјРёРЅСѓСЃРµ, 6 РІ РјРёРЅСѓСЃРµ
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
        # 2вЂ“4 СЃ: 58 Р·Р°РЅСЏС‚Р°
        ScenarioStep(
            t=2.0,
            rc_states={"57": 6, "58": 6, "37": 6},
            switch_states={"33": 9, "149": 9},
            signal_states={},
            modes={},
        ),
        # 4вЂ“6 СЃ: 58 СЃРЅРѕРІР° СЃРІРѕР±РѕРґРЅР°
        ScenarioStep(
            t=2.0,
            rc_states={"57": 6, "58": 3, "37": 6},
            switch_states={"33": 9, "149": 9},
            signal_states={},
            modes={},
        ),
        # 6вЂ“9 СЃ: РІСЃС‘ СЃРІРѕР±РѕРґРЅРѕ
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

    assert any("llz_v3_open" in s.flags for s in timeline), "РќРµС‚ llz_v3_open РЅР° 58"
    assert any("llz_v3" in s.flags and s.lz_variant == 3 for s in timeline), "llz_v3 Р±РµР· variant=3 РЅР° 58"
    assert any("llz_v3_closed" in s.flags for s in timeline), "РќРµС‚ llz_v3_closed РЅР° 58"


# test_detectors_engine_v8.py

from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_v8_dsp_exception_aborts_phase_before_open():
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz8=True,
        ts01_lz8=1.0,
        ts02_lz8=1.0,
        tlz_lz8=1.0,
        tkon_lz8=1.0,
        enable_lz_exc_dsp=True,
        t_min_maneuver_v8=1.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
            dispatcher_control_state=4,
            auto_actions={"nas": 0},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 6},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
            dispatcher_control_state=4,
            auto_actions={"nas": 0},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
            dispatcher_control_state=4,
            auto_actions={"nas": 0},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()

    assert not any("llz_v8_open" in s.flags for s in timeline)
    assert not any("llz_v8" in s.flags for s in timeline)


def test_v8_108_full_cycle_prev_branch():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» v8 РЅР° 108, РІРµС‚РєР° Р’8.1 (prev Р·Р°РЅСЏС‚):
    - РќР°С‡Р°Р»СЊРЅР°СЏ С„Р°Р·Р°: 1-1-0 РёР»Рё 1-1-1 (prev Рё curr Р·Р°РЅСЏС‚С‹) в‰Ґ ts01
    - Р’С‚РѕСЂР°СЏ С„Р°Р·Р°: X-1-1 (curr Рё next Р·Р°РЅСЏС‚С‹) в‰Ґ ts02
    - РҐРІРѕСЃС‚: 0-1-0 в‰Ґ tlz в†’ РѕС‚РєСЂС‹С‚РёРµ
    - Р—Р°РІРµСЂС€РµРЅРёРµ: СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ ctrl в‰Ґ tkon
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        # v1-v7 РѕС‚РєР»СЋС‡РµРЅС‹
        ts01_lz1=0.0, tlz_lz1=0.0, tkon_lz1=0.0, enable_lz1=False,
        ts01_lz2=0.0, ts02_lz2=0.0, tlz_lz2=0.0, tkon_lz2=0.0, enable_lz2=False,
        ts01_lz3=0.0, ts02_lz3=0.0, tlz_lz3=0.0, tkon_lz3=0.0, enable_lz3=False,
        ts01_lz7=0.0, tlz_lz7=0.0, tkon_lz7=0.0, enable_lz7=False,
        # v8 РІРєР»СЋС‡РµРЅ
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
        # 0-2 СЃ: РќР°С‡Р°Р»СЊРЅР°СЏ С„Р°Р·Р° 1-1-0 (prev Рё curr Р·Р°РЅСЏС‚С‹, next СЃРІРѕР±РѕРґРµРЅ)
        # Р’РђР–РќРћ: РїРµСЂРІС‹Р№ С€Р°Рі РґРѕР»Р¶РµРЅ РёРјРµС‚СЊ РѕР±Р° control_ok РґР»СЏ seen_full_adj!
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 2-4 СЃ: Р’С‚РѕСЂР°СЏ С„Р°Р·Р° 1-1-1 (РІСЃРµ Р·Р°РЅСЏС‚С‹)
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 6},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 4-6 СЃ: РҐРІРѕСЃС‚ 0-1-0 (prev Рё next СЃРІРѕР±РѕРґРЅС‹, curr Р·Р°РЅСЏС‚)
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 6-9 СЃ: Р—Р°РІРµСЂС€РµРЅРёРµ вЂ” СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ ctrl
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 6-9 СЃ: Р—Р°РІРµСЂС€РµРЅРёРµ вЂ” СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ ctrl
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
    print(f"TIMELINE LENGTH: {len(timeline)}")  # в†ђ Р”РћР›Р–РќРћ Р‘Р«РўР¬ > 0
    print(f"TIMELINE: {timeline}")  # в†ђ Р§С‚Рѕ РІРЅСѓС‚СЂРё?

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("llz_v8_open" in s.flags for s in timeline), "РќРµС‚ llz_v8_open"
    assert any("llz_v8" in s.flags and s.lz_variant == 8 for s in timeline), "llz_v8 Р±РµР· variant=8"
    assert any("llz_v8_closed" in s.flags for s in timeline), "РќРµС‚ llz_v8_closed"


def test_v8_no_seen_full_adj_no_start():
    """
    Р•СЃР»Рё РЅРµ Р±С‹Р»Рѕ С€Р°РіР° СЃ РѕР±РѕРёРјРё РґРѕСЃС‚РѕРІРµСЂРЅС‹РјРё (prev_control_ok Рё next_control_ok),
    v8 РЅРµ РґРѕР»Р¶РµРЅ СЃС‚Р°СЂС‚РѕРІР°С‚СЊ РґР°Р¶Рµ РїСЂРё РїСЂР°РІРёР»СЊРЅС‹С… РјР°СЃРєР°С….
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
        # РЁР°РіРё СЃ РїРѕР»РЅС‹РјРё РјР°СЃРєР°РјРё, РЅРѕ Р±РµР· seen_full_adj
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6, "108": 6, "83": 3},  # 1-1-0
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},  # С‚РѕР»СЊРєРѕ prev!
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
    

    # v8 РЅРµ РґРѕР»Р¶РµРЅ Р°РєС‚РёРІРёСЂРѕРІР°С‚СЊСЃСЏ
    assert not any("llz_v8" in s.flags for s in timeline)
    assert not any("llz_v8_open" in s.flags for s in timeline)


def test_v8_108_full_cycle_next_branch():
    """
    Р¦РёРєР» v8, РІРµС‚РєР° Р’8.2 (next Р·Р°РЅСЏС‚):
    - p1: X-1-1 (curr Рё next Р·Р°РЅСЏС‚С‹)
    - p2: 0-1-X РёР»Рё X-1-0 (Р°Р»СЊС‚РµСЂРЅР°С‚РёРІС‹)
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
        # 0-2 СЃ: p1 вЂ” X-1-1 (curr Рё next Р·Р°РЅСЏС‚С‹, prev Р»СЋР±РѕР№)
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 6, "83": 6},  # 0-1-1
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 2-4 СЃ: p2 вЂ” 0-1-X (prev СЃРІРѕР±РѕРґРµРЅ, curr Р·Р°РЅСЏС‚, next Р»СЋР±РѕР№)
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3, "108": 6, "83": 6},  # 0-1-1 (prev СЃРІРѕР±РѕРґРµРЅ!)
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 4-6 СЃ: tail вЂ” 0-1-0
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 6-9 СЃ: Р·Р°РІРµСЂС€РµРЅРёРµ
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # 6-9 СЃ: Р·Р°РІРµСЂС€РµРЅРёРµ
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
    print(f"TIMELINE LENGTH: {len(timeline)}")  # в†ђ Р”РћР›Р–РќРћ Р‘Р«РўР¬ > 0
    print(f"TIMELINE: {timeline}")  # в†ђ Р§С‚Рѕ РІРЅСѓС‚СЂРё?

    print(f"Checking llz_v8_open: {any('llz_v8_open' in s.flags for s in timeline)}")
    assert any("llz_v8_open" in s.flags for s in timeline)
    print(f"Checking lz_variant==8: {any('llz_v8' in s.flags and s.lz_variant == 8 for s in timeline)}")
    assert any("llz_v8" in s.flags and s.lz_variant == 8 for s in timeline)
    print(f"Checking llz_v8_closed: {any('llz_v8_closed' in s.flags for s in timeline)}")
    assert any("llz_v8_closed" in s.flags for s in timeline)


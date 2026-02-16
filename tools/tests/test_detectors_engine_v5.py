# -*- coding: utf-8 -*-
from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_v5_59_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» v5 РЅР° 59 (1-7РЎРџ, can_lock=True).
    ts05_lz5=1.0, tlz_lz5=1.0, tkon_lz5=1.0.
    РћР¶РёРґР°РµРј: РµСЃС‚СЊ open, Р°РєС‚РёРІРЅР°СЏ Р›Р— v5, РµСЃС‚СЊ closed.
    РЎРѕСЃРµРґРё РЅРµ С‚СЂРµР±СѓСЋС‚СЃСЏ вЂ” NeighborRequirement.NONE.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",           # 1-7РЎРџ (ID), can_lock=True
        prev_rc_name=None,         # СЃРѕСЃРµРґРё РЅРµ РЅСѓР¶РЅС‹
        ctrl_rc_name="59",
        next_rc_name=None,
        # РћС‚РєР»СЋС‡Р°РµРј РІСЃРµ РѕСЃС‚Р°Р»СЊРЅС‹Рµ РІР°СЂРёР°РЅС‚С‹
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
        # Р’РєР»СЋС‡Р°РµРј v5
        ts01_lz5=1.0,
        tlz_lz5=1.0,
        tkon_lz5=1.0,
        enable_lz5=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0вЂ“2 СЃ: Р”РђРќРћ вЂ” ctrl free Р±РµР· lock (3) в‰Ґ ts05=1.0
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3},  # С‚РѕР»СЊРєРѕ ctrl, СЃРѕСЃРµРґРё РЅРµ РІР°Р¶РЅС‹
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2вЂ“4 СЃ: РљРћР“Р”Рђ вЂ” ctrl occupied Р±РµР· lock (6) в‰Ґ tlz=1.0 в†’ open
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 4вЂ“6 СЃ: Р—Р°РІРµСЂС€РµРЅРёРµ вЂ” ctrl free (3) в‰Ґ tkon=1.0 в†’ closed
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

    assert any("llz_v5_open" in s.flags for s in timeline), "РќРµС‚ llz_v5_open"
    assert any("llz_v5" in s.flags and s.lz_variant == 5 for s in timeline), "llz_v5 Р±РµР· variant=5"
    assert any("llz_v5_closed" in s.flags for s in timeline), "РќРµС‚ llz_v5_closed"

def test_v5_65_should_not_trigger():
    """
    РџСЂРѕРІРµСЂРєР° С‡С‚Рѕ v5 РќР• СЃСЂР°Р±Р°С‚С‹РІР°РµС‚ РЅР° Р Р¦ 65 (4Рџ), РіРґРµ can_lock=False.
    v5 С‚СЂРµР±СѓРµС‚ can_lock=True (Р·Р°РјС‹РєР°РЅРёРµ РІРѕР·РјРѕР¶РЅРѕ).
    РћР¶РёРґР°РµРј: РЅРµС‚ open, variant=0, С„Р»Р°РіРё РЅРµ СЃРѕРґРµСЂР¶Р°С‚ llz_v5.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="65",           # 4Рџ (ID), can_lock=False
        prev_rc_name=None,
        ctrl_rc_name="65",
        next_rc_name=None,
        # РћС‚РєР»СЋС‡Р°РµРј РІСЃРµ РѕСЃС‚Р°Р»СЊРЅС‹Рµ РІР°СЂРёР°РЅС‚С‹
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
        # Р’РєР»СЋС‡Р°РµРј v5
        ts01_lz5=1.0,
        tlz_lz5=1.0,
        tkon_lz5=1.0,
        enable_lz5=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0вЂ“2 СЃ: Р”РђРќРћ вЂ” ctrl free (3)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2вЂ“4 СЃ: РљРћР“Р”Рђ вЂ” ctrl occupied (6)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 4вЂ“6 СЃ: Р—Р°РІРµСЂС€РµРЅРёРµ вЂ” ctrl free (3)
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

    # РџСЂРѕРІРµСЂСЏРµРј С‡С‚Рѕ v5 РќР• СЃСЂР°Р±РѕС‚Р°Р»
    assert not any("llz_v5_open" in s.flags for s in timeline), "v5 СЃСЂР°Р±РѕС‚Р°Р», РЅРѕ РЅРµ РґРѕР»Р¶РµРЅ (can_lock=False)"
    assert not any(s.lz_variant == 5 for s in timeline), "variant=5, РЅРѕ РЅРµ РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ"
    assert not any("llz_v5" in s.flags for s in timeline), "Р•СЃС‚СЊ С„Р»Р°Рі llz_v5, РЅРѕ РЅРµ РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ"
    print("вњ… v5 РєРѕСЂСЂРµРєС‚РЅРѕ РќР• СЃСЂР°Р±РѕС‚Р°Р» РЅР° Р Р¦ Р±РµР· Р·Р°РјС‹РєР°РЅРёСЏ")

# -*- coding: utf-8 -*-
from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_v6_59_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» v6 РЅР° 59 (1-7РЎРџ).
    ts01_lz6=2.0, tlz_lz6=2.0, tkon_lz6=2.0.
    РћР¶РёРґР°РµРј: РµСЃС‚СЊ open, Р°РєС‚РёРІРЅР°СЏ Р›Р— v6, РµСЃС‚СЊ closed.
    РЎРѕСЃРµРґРё РЅРµ С‚СЂРµР±СѓСЋС‚СЃСЏ вЂ” NeighborRequirement.ONLY_CTRL.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",           # 1-7РЎРџ (ID)
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
        # 0вЂ“2 СЃ: Р”РђРќРћ вЂ” ctrl free (3) в‰Ґ ts01_lz6=2.0
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2вЂ“4 СЃ: РљРћР“Р”Рђ вЂ” ctrl occupied (6) в‰Ґ tlz_lz6=2.0 в†’ open
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 4вЂ“6 СЃ: Р—Р°РІРµСЂС€РµРЅРёРµ вЂ” ctrl free (3) в‰Ґ tkon_lz6=2.0 в†’ closed
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

    assert any("llz_v6_open" in s.flags for s in timeline), "РќРµС‚ llz_v6_open"
    # РРЎРџР РђР’Р›Р•РќРћ: variant == 6 (Р±С‹Р»Рѕ 5)
    assert any("llz_v6" in s.flags and s.lz_variant == 6 for s in timeline), "llz_v6 Р±РµР· variant=6"
    assert any("llz_v6_closed" in s.flags for s in timeline), "РќРµС‚ llz_v6_closed"


def test_v6_65_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» v6 РЅР° 65 (4Рџ) вЂ” v6 СЂР°Р±РѕС‚Р°РµС‚ РЅР° Р›Р®Р‘РћР™ Р Р¦, РІРєР»СЋС‡Р°СЏ Р±РµР· can_lock.
    ts01_lz6=2.0, tlz_lz6=2.0, tkon_lz6=2.0.
    РћР¶РёРґР°РµРј: РµСЃС‚СЊ open, Р°РєС‚РёРІРЅР°СЏ Р›Р— v6, РµСЃС‚СЊ closed.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="65",           # 4Рџ (ID), can_lock=False вЂ” РЅРѕ v6 РІСЃС‘ СЂР°РІРЅРѕ СЂР°Р±РѕС‚Р°РµС‚!
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

    # РРЎРџР РђР’Р›Р•РќРћ: v6 СЂР°Р±РѕС‚Р°РµС‚ РЅР° Р»СЋР±РѕР№ Р Р¦, РїРѕСЌС‚РѕРјСѓ РїСЂРѕРІРµСЂСЏРµРј РЅР°Р»РёС‡РёРµ СЃРѕР±С‹С‚РёР№
    assert any("llz_v6_open" in s.flags for s in timeline), "РќРµС‚ llz_v6_open"
    assert any("llz_v6" in s.flags and s.lz_variant == 6 for s in timeline), "llz_v6 Р±РµР· variant=6"
    assert any("llz_v6_closed" in s.flags for s in timeline), "РќРµС‚ llz_v6_closed"

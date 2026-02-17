# -*- coding: utf-8 -*-
"""
РўРµСЃС‚С‹ РґР»СЏ РІР°СЂРёР°РЅС‚Р° LS1 (РљР»Р°СЃСЃРёС‡РµСЃРєР°СЏ Р»РѕР¶РЅР°СЏ СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ)

LS1 РґРµС‚РµРєС‚РёСЂСѓРµС‚ РєР»Р°СЃСЃРёС‡РµСЃРєСѓСЋ Р»РѕР¶РЅСѓСЋ СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ РєРѕРіРґР° РѕРґРёРЅ РёР»Рё РѕР±Р°
СЃРѕСЃРµРґР° РЅРµ РєРѕРЅС‚СЂРѕР»РёСЂСѓСЋС‚СЃСЏ (NC), Р° РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјР°СЏ Р Р¦ Р·Р°РЅСЏС‚Р°, Р·Р°С‚РµРј РѕСЃРІРѕР±РѕР¶РґР°РµС‚СЃСЏ.

Р¤Р°Р·С‹:
    0 (C0101): (prev NC РёР»Рё next NC) Р curr Р·Р°РЅСЏС‚Р° в†’ ts01_ls1
    1 (tail):  curr СЃРІРѕР±РѕРґРЅР° в†’ tlz_ls1 в†’ РѕС‚РєСЂС‹С‚РёРµ
    Р—Р°РІРµСЂС€РµРЅРёРµ: curr Р·Р°РЅСЏС‚Р° в‰Ґ tkon_ls1 в†’ Р·Р°РєСЂС‹С‚РёРµ

NC (not controlled) - СЃРѕСЃС‚РѕСЏРЅРёРµ РЅРµ СЂР°РІРЅРѕ 3 (СЃРІРѕР±РѕРґРЅР°) РёР»Рё 6 (Р·Р°РЅСЏС‚Р°).
РќР°РїСЂРёРјРµСЂ: 0, 1, 2, 4, 5, 7, 8 Рё С‚.Рґ.
"""

from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_ls1_108_prev_nc_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» LS1 РЅР° 108 (1Рџ) СЃ prev NC.
    
    РЎС†РµРЅР°СЂРёР№:
    - prev (59) NC (СЃРѕСЃС‚РѕСЏРЅРёРµ 0), curr (108) Р·Р°РЅСЏС‚Р° (6) - С„Р°Р·Р° C0101
    - curr (108) СЃРІРѕР±РѕРґРЅР° (3) - С„Р°Р·Р° tail в†’ РѕС‚РєСЂС‹С‚РёРµ
    - curr (108) Р·Р°РЅСЏС‚Р° (6) в†’ Р·Р°РєСЂС‹С‚РёРµ
    
    РўР°Р№РјРёРЅРіРё: ts01_ls1=2.0, tlz_ls1=2.0, tkon_ls1=3.0
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 1Рџ (ID)
        prev_rc_name="59",         # 10-12РЎРџ (ID)
        ctrl_rc_name="108",
        next_rc_name="83",         # 1-7РЎРџ (ID)
        # РћС‚РєР»СЋС‡Р°РµРј РІСЃРµ РѕСЃС‚Р°Р»СЊРЅС‹Рµ РІР°СЂРёР°РЅС‚С‹
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        enable_ls9=False,
        # LS1 РїР°СЂР°РјРµС‚СЂС‹
        ts01_ls1=2.0,  # Р¤Р°Р·Р° C0101: (prev NC РёР»Рё next NC) Р curr Р·Р°РЅСЏС‚Р° в‰Ґ 2СЃ
        tlz_ls1=2.0,   # Р¤Р°Р·Р° tail: curr СЃРІРѕР±РѕРґРЅР° в‰Ґ 2СЃ
        tkon_ls1=3.0,  # Р—Р°РІРµСЂС€РµРЅРёРµ: curr Р·Р°РЅСЏС‚Р° в‰Ґ 3СЃ
        enable_ls1=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-3СЃ: C0101 - 0-1-0 (С†РµРЅС‚СЂ Р·Р°РЅСЏС‚ 108, РєСЂР°СЏ СЃРІРѕР±РѕРґРЅС‹ 59/83)
        # Р”Р»СЏ 108: 59 = prev,
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            # Sw10(110)=3 (PLUS) connects 59 to 108
            # Sw1(87)=3 (PLUS) and Sw5(88)=3 (PLUS) connect 83 to 108
            switch_states={"110": 3, "88": 3, "87": 3},
            signal_states={},
            modes={},
        ),
        # 3-6СЃ: tail - 0-0-0 (РІСЃРµ СЃРІРѕР±РѕРґРЅС‹) в†’ РѕС‚РєСЂС‹С‚РёРµ Р›РЎ1
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            # Sw10(110)=15 (No Control) -> Neighbor 59 is NOT controlled
            switch_states={"110": 15, "88": 3, "87": 3},
            signal_states={},
            modes={},
        ),
        # 6-10с: Завершение - 108 занята ≥ tkon_ls1=3.0 → закрытие
        ScenarioStep(
            t=4.0,
            rc_states={"59": 3, "108": 6, "83": 3},  # 108 занята для закрытия
            switch_states={"110": 3, "88": 3, "87": 3},
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

    # Р’С‹РІРѕРґ РґР»СЏ РѕС‚Р»Р°РґРєРё
    print("\n=== LS1 Test: 108 (1Рџ) - prev NC ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59', 0)}, "
            f"rc_108={st.rc_states.get('108', 0)}, rc_83={st.rc_states.get('83', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # РџСЂРѕРІРµСЂРєРё
    assert any("lls_1_open" in s.flags for s in timeline), "РќРµС‚ lls_1_open"
    assert any("lls_1" in s.flags and s.lz_variant == 101 for s in timeline), "lls_1 Р±РµР· variant=101"
    assert any("lls_1_closed" in s.flags for s in timeline), "РќРµС‚ lls_1_closed"


def test_ls1_59_next_nc_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» LS1 РЅР° 59 (10-12РЎРџ) СЃ next NC.
    
    РЎС†РµРЅР°СЂРёР№:
    - prev СЃРІРѕР±РѕРґРЅР°, curr Р·Р°РЅСЏС‚Р°, next NC - С„Р°Р·Р° C0101
    - curr СЃРІРѕР±РѕРґРЅР° - С„Р°Р·Р° tail в†’ РѕС‚РєСЂС‹С‚РёРµ
    - curr Р·Р°РЅСЏС‚Р° в†’ Р·Р°РєСЂС‹С‚РёРµ
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",           # 10-12РЎРџ (ID)
        prev_rc_name="47",         # 1РђРџ (ID)
        ctrl_rc_name="59",
        next_rc_name="104",        # 3РЎРџ (ID)
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        enable_ls9=False,
        ts01_ls1=1.5,
        tlz_ls1=1.5,
        tkon_ls1=2.0,
        enable_ls1=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-2СЃ: C0101 - 0-1-0 (С†РµРЅС‚СЂ Р·Р°РЅСЏС‚Р° 59, РєСЂР°СЏ 47/108 СЃРІРѕР±РѕРґРЅС‹)
        # Р”Р»СЏ 59: 47 = prev (Р±РµР·СѓСЃР»РѕРІРЅС‹Р№),
        ScenarioStep(
            t=2.0,
            rc_states={"47": 3, "59": 6, "108": 3},
            switch_states={"110": 3},
            signal_states={},
            modes={},
        ),
        # 2-4СЃ: tail - 0-0-0 (РІСЃРµ СЃРІРѕР±РѕРґРЅС‹) в†’ РѕС‚РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=2.0,
            rc_states={"47": 3, "59": 3, "108": 3},
            switch_states={"110": 3},
            signal_states={},
            modes={},
        ),
        # 4-7с: Завершение - 59 занята ≥ tkon_ls1=2.0 → закрытие
        ScenarioStep(
            t=3.0,
            rc_states={"47": 3, "59": 6, "108": 3},  # 59 занята для закрытия
            switch_states={"110": 3},
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

    print("\n=== LS1 Test: 59 (10-12РЎРџ) - next NC ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_47={st.rc_states.get('47', 0)}, "
            f"rc_59={st.rc_states.get('59', 0)}, rc_108={st.rc_states.get('108', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("lls_1_open" in s.flags for s in timeline), "РќРµС‚ lls_1_open"
    assert any("lls_1" in s.flags and s.lz_variant == 101 for s in timeline), "lls_1 Р±РµР· variant=101"
    assert any("lls_1_closed" in s.flags for s in timeline), "РќРµС‚ lls_1_closed"


def test_ls1_83_both_nc_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» LS1 РЅР° 83 (1-7РЎРџ) СЃ РѕР±РѕРёРјРё СЃРѕСЃРµРґСЏРјРё NC.
    
    РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ LS1 СЃСЂР°Р±Р°С‚С‹РІР°РµС‚ РєРѕРіРґР° РѕР±Р° СЃРѕСЃРµРґР° NC.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="83",           # 1-7РЎРџ (ID)
        prev_rc_name="86",         # 3РЎРџ (ID)
        ctrl_rc_name="83",
        next_rc_name="81",         # РќРџ (ID)
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        enable_ls9=False,
        ts01_ls1=2.0,
        tlz_ls1=2.0,
        tkon_ls1=3.0,
        enable_ls1=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-3СЃ: C0101 - 0-1-0 (83 Р·Р°РЅСЏС‚Р°, СЃРѕСЃРµРґР° 86/81 СЃРІРѕР±РѕРґРЅС‹)
        # Р”Р»СЏ 83: 86 = prev (Sw150=0/Minus), 81 = next (Р±РµР·СѓСЃР»РѕРІРЅС‹Р№)
        ScenarioStep(
            t=3.0,
            rc_states={"86": 3, "83": 6, "81": 3},
            # Sw1(87)=9 (MINUS) connects 83 to 86
            # Sw3(150)=9 (MINUS) connects 86 to 83
            switch_states={"87": 9, "150": 9},
            signal_states={},
            modes={},
        ),
        # 3-6СЃ: tail - 0-0-0 (РІСЃРµ СЃРІРѕР±РѕРґРЅС‹) в†’ РѕС‚РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=3.0,
            rc_states={"86": 3, "83": 3, "81": 3},
            # Switch stays in MINUS -> neighbor 86 is adjacent
            # BUT we set it to some other state to test LOSS OF CONTROL
            switch_states={"87": 0, "150": 9}, 
            signal_states={},
            modes={},
        ),
        # 6-10с: Завершение - 83 занята ≥ tkon_ls1=3.0 → закрытие
        ScenarioStep(
            t=4.0,
            rc_states={"86": 3, "83": 6, "81": 3},  # 83 занята для закрытия
            switch_states={"150": 9},
            signal_states={},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="83",
    )

    timeline = ctx.run()

    print("\n=== LS1 Test: 83 (1-7РЎРџ) - both NC ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_86={st.rc_states.get('86', 0)}, "
            f"rc_83={st.rc_states.get('83', 0)}, rc_81={st.rc_states.get('81', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("lls_1_open" in s.flags for s in timeline), "РќРµС‚ lls_1_open"
    assert any("lls_1" in s.flags and s.lz_variant == 101 for s in timeline), "lls_1 Р±РµР· variant=101"
    assert any("lls_1_closed" in s.flags for s in timeline), "РќРµС‚ lls_1_closed"


def test_ls1_65_no_open_no_nc():
    """
    РўРµСЃС‚ РЅР° 65 (4Рџ) - РЅРµС‚ NC, Р›РЎ1 РЅРµ РґРѕР»Р¶РЅР° РѕС‚РєСЂС‹С‚СЊСЃСЏ.
    
    РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ РµСЃР»Рё РѕР±Р° СЃРѕСЃРµРґР° РєРѕРЅС‚СЂРѕР»РёСЂСѓСЋС‚СЃСЏ (РЅРµ NC),
    С‚Рѕ Р›РЎ1 РЅРµ С„РѕСЂРјРёСЂСѓРµС‚СЃСЏ.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="65",           # 4Рџ (ID)
        prev_rc_name="36",         # 2-8РЎРџ (ID)
        ctrl_rc_name="65",
        next_rc_name="94",         # 14-16РЎРџ (ID)
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        enable_ls9=False,
        ts01_ls1=2.0,
        tlz_ls1=2.0,
        tkon_ls1=3.0,
        enable_ls1=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-3СЃ: prev СЃРІРѕР±РѕРґРЅР° (3), curr Р·Р°РЅСЏС‚Р° (6), next СЃРІРѕР±РѕРґРЅР° (3) - РќР•Рў NC!
        ScenarioStep(
            t=3.0,
            rc_states={"36": 3, "65": 6, "94": 3},  # РЅРµС‚ NC
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 3-6СЃ: curr СЃРІРѕР±РѕРґРЅР° (3)
        ScenarioStep(
            t=3.0,
            rc_states={"36": 3, "65": 3, "94": 3},  # curr СЃРІРѕР±РѕРґРЅР°
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 6-8СЃ: curr Р·Р°РЅСЏС‚Р° (6)
        ScenarioStep(
            t=2.0,
            rc_states={"36": 3, "65": 6, "94": 3},  # curr Р·Р°РЅСЏС‚Р°
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

    print("\n=== LS1 Test: 65 (4Рџ) - No NC ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_36={st.rc_states.get('36', 0)}, "
            f"rc_65={st.rc_states.get('65', 0)}, rc_94={st.rc_states.get('94', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ Р›РЎ1 РќР• РѕС‚РєСЂС‹Р»Р°СЃСЊ (РЅРµС‚ NC)
    assert not any("lls_1_open" in s.flags for s in timeline), "lls_1_open РЅРµ РґРѕР»Р¶РЅРѕ Р±С‹С‚СЊ (РЅРµС‚ NC)"
    assert not any("lls_1" in s.flags for s in timeline), "lls_1 РЅРµ РґРѕР»Р¶РЅРѕ Р±С‹С‚СЊ Р°РєС‚РёРІРЅРѕ (РЅРµС‚ NC)"


def test_ls1_81_boundary_must_not_open():
    """
    РўРµСЃС‚ РЅР° 81 (РќРџ) - РіСЂР°РЅРёС‡РЅР°СЏ Р Р¦.
    Р”РѕР»Р¶РЅР° СЃС‚СЂРѕРіРѕ С‚СЂРµР±РѕРІР°С‚СЊ BOTH СЃРѕСЃРµРґРµР№.
    РЈ РќРџ С‚РѕР»СЊРєРѕ РѕРґРёРЅ СЃРѕСЃРµРґ (83), РІС‚РѕСЂРѕРіРѕ РЅРµС‚.
    РћР¶РёРґР°РµРј: Р›РЎ1 РЅРµ РѕС‚РєСЂС‹РІР°РµС‚СЃСЏ.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="81",
        prev_rc_name="83",
        ctrl_rc_name="81",
        next_rc_name="",  # РќРµС‚ СЃРѕСЃРµРґР°
        enable_ls1=True,
        ts01_ls1=1.0,
        tlz_ls1=1.0,
        tkon_ls1=1.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)
    
    scenario = [
        # Center occupied, neighbor free
        ScenarioStep(t=2.0, rc_states={"83": 3, "81": 6}, switch_states={}, signal_states={}, modes={}),
        # Center free, neighbor free
        ScenarioStep(t=2.0, rc_states={"83": 3, "81": 3}, switch_states={}, signal_states={}, modes={}),
    ]
    
    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="81")
    timeline = ctx.run()
    
    assert not any("lls_1_open" in s.flags for s in timeline), "LS1 РЅРµ РґРѕР»Р¶РµРЅ РѕС‚РєСЂС‹РІР°С‚СЊСЃСЏ РЅР° РіСЂР°РЅРёС†Рµ (BOTH requirement)"



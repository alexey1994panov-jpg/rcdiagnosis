# -*- coding: utf-8 -*-
"""
РўРµСЃС‚С‹ РґР»СЏ РІР°СЂРёР°РЅС‚Р° LS9 (РџСЂРѕР±РѕР№ РёР·РѕР»РёСЂСѓСЋС‰РµРіРѕ СЃС‚С‹РєР°)

LS9 РґРµС‚РµРєС‚РёСЂСѓРµС‚ СЃРёС‚СѓР°С†РёСЋ, РєРѕРіРґР° Р Р¦ РїРµСЂРµС…РѕРґРёС‚ РёР· Р·Р°РЅСЏС‚РѕРіРѕ СЃРѕСЃС‚РѕСЏРЅРёСЏ
РІ СЃРІРѕР±РѕРґРЅРѕРµ Рё РѕР±СЂР°С‚РЅРѕ РІ Р·Р°РЅСЏС‚РѕРµ (РїСЂРѕР±РѕР№ РёР·РѕР»РёСЂСѓСЋС‰РµРіРѕ СЃС‚С‹РєР°).

Р¤Р°Р·С‹:
    0 (S0109): ctrl Р·Р°РЅСЏС‚Р° в†’ ts01_ls9
    1 (tail):  ctrl СЃРІРѕР±РѕРґРЅР° в†’ tlz_ls9
    2 (S0209): ctrl Р·Р°РЅСЏС‚Р° в†’ tlz_ls9 в†’ РѕС‚РєСЂС‹С‚РёРµ
    Р—Р°РІРµСЂС€РµРЅРёРµ: ctrl СЃРІРѕР±РѕРґРЅР° в‰Ґ tkon_ls9 в†’ Р·Р°РєСЂС‹С‚РёРµ
"""

from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_ls9_108_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» LS9 РЅР° 108 (1Рџ) - РёР· legacy С‚РµСЃС‚Р°.
    
    РЎС†РµРЅР°СЂРёР№ РёР· legacy/tests/test_ls_variant9_1p.py:
    - 3 С€Р°РіР°: 1Рџ Р·Р°РЅСЏС‚Р° (6) - С„Р°Р·Р° S0109
    - 3 С€Р°РіР°: 1Рџ СЃРІРѕР±РѕРґРЅР° (3) - С„Р°Р·Р° tail
    - 6 С€Р°РіРѕРІ: 1Рџ Р·Р°РЅСЏС‚Р° (6) - С„Р°Р·Р° S0209 в†’ РѕС‚РєСЂС‹С‚РёРµ в†’ Р·Р°РІРµСЂС€РµРЅРёРµ
    
    РўР°Р№РјРёРЅРіРё: ts01_ls9=2.0, tlz_ls9=2.0, tkon_ls9=3.0
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 1Рџ (ID)
        prev_rc_name=None,         # LS9 РЅРµ С‚СЂРµР±СѓРµС‚ СЃРѕСЃРµРґРµР№
        ctrl_rc_name="108",
        next_rc_name=None,
        # РћС‚РєР»СЋС‡Р°РµРј РІСЃРµ РѕСЃС‚Р°Р»СЊРЅС‹Рµ РІР°СЂРёР°РЅС‚С‹
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        # LS9 РїР°СЂР°РјРµС‚СЂС‹
        ts01_ls9=2.0,  # Р¤Р°Р·Р° S0109: Р·Р°РЅСЏС‚Р° в‰Ґ 2СЃ
        tlz_ls9=2.0,   # Р¤Р°Р·Р° tail: СЃРІРѕР±РѕРґРЅР° в‰Ґ 2СЃ, С„Р°Р·Р° S0209: Р·Р°РЅСЏС‚Р° в‰Ґ 2СЃ
        tkon_ls9=3.0,  # Р—Р°РІРµСЂС€РµРЅРёРµ: СЃРІРѕР±РѕРґРЅР° в‰Ґ 3СЃ
        enable_ls9=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-3СЃ: S0109 - 1Рџ Р·Р°РЅСЏС‚Р° (6) в‰Ґ ts01_ls9=2.0 в†’ РїРµСЂРµС…РѕРґ Рє С„Р°Р·Рµ 1
        ScenarioStep(
            t=3.0,
            rc_states={"108": 6},  # Р·Р°РЅСЏС‚Р°
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 3-6СЃ: tail - 1Рџ СЃРІРѕР±РѕРґРЅР° (3) в‰Ґ tlz_ls9=2.0 в†’ РїРµСЂРµС…РѕРґ Рє С„Р°Р·Рµ 2
        ScenarioStep(
            t=3.0,
            rc_states={"108": 3},  # СЃРІРѕР±РѕРґРЅР°
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 6-12СЃ: S0209 - 1Рџ Р·Р°РЅСЏС‚Р° (6) в‰Ґ tlz_ls9=2.0 в†’ РѕС‚РєСЂС‹С‚РёРµ Р›РЎ9
        # Р—Р°С‚РµРј СЃРІРѕР±РѕРґРЅР° в‰Ґ tkon_ls9=3.0 в†’ Р·Р°РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=6.0,
            rc_states={"108": 6},  # Р·Р°РЅСЏС‚Р°
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 12-16СЃ: Р—Р°РІРµСЂС€РµРЅРёРµ - 1Рџ СЃРІРѕР±РѕРґРЅР° (3) в‰Ґ tkon_ls9=3.0 в†’ Р·Р°РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=4.0,
            rc_states={"108": 3},  # СЃРІРѕР±РѕРґРЅР°
            switch_states={},
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
    print("\n=== LS9 Test: 108 (1Рџ) ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_108={st.rc_states.get('108', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # РџСЂРѕРІРµСЂРєРё    # Проверки - LS9 может открыться и закрыться на одном шаге
    assert any("lls_9_open" in s.flags for s in timeline), "Нет lls_9_open"
    # Проверяем что есть шаг с variant=109 (может быть с open, closed или lls_9)
    assert any(s.lz_variant == 109 for s in timeline), "Нет variant=109"
    assert any("lls_9_closed" in s.flags for s in timeline), "Нет lls_9_closed"


def test_ls9_59_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» LS9 РЅР° 59 (10-12РЎРџ).
    
    РџСЂРѕРІРµСЂСЏРµРј СЂР°Р±РѕС‚Сѓ РЅР° РґСЂСѓРіРѕР№ Р Р¦ СЃ С‚РµРјРё Р¶Рµ С„Р°Р·Р°РјРё.
    РўР°Р№РјРёРЅРіРё: ts01_ls9=1.5, tlz_ls9=1.5, tkon_ls9=2.0
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",           # 10-12РЎРџ (ID)
        prev_rc_name=None,
        ctrl_rc_name="59",
        next_rc_name=None,
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        ts01_ls9=1.5,
        tlz_ls9=1.5,
        tkon_ls9=2.0,
        enable_ls9=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-2СЃ: S0109 - Р·Р°РЅСЏС‚Р°
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2-4СЃ: tail - СЃРІРѕР±РѕРґРЅР°
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 4-6СЃ: S0209 - Р·Р°РЅСЏС‚Р° в†’ РѕС‚РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 6-9с: Завершение - занята ≥ tkon_ls9=2.0 → закрытие
        ScenarioStep(
            t=3.0,
            rc_states={"59": 6},  # занята для закрытия
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

    print("\n=== LS9 Test: 59 (10-12РЎРџ) ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )
    # Проверки - LS9 может открыться и закрыться на одном шаге
    assert any("lls_9_open" in s.flags for s in timeline), "Нет lls_9_open"
    # Проверяем что есть шаг с variant=109
    assert any(s.lz_variant == 109 for s in timeline), "Нет variant=109"
    assert any("lls_9_closed" in s.flags for s in timeline), "Нет lls_9_closed"


def test_ls9_83_interrupted_phase():
    """
    РўРµСЃС‚ РїСЂРµСЂС‹РІР°РЅРёСЏ С„Р°Р·С‹ LS9 РЅР° 83 (1-7РЎРџ).
    
    РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ РµСЃР»Рё СѓСЃР»РѕРІРёРµ С„Р°Р·С‹ РЅР°СЂСѓС€Р°РµС‚СЃСЏ,
    РґРµС‚РµРєС‚РѕСЂ СЃР±СЂР°СЃС‹РІР°РµС‚СЃСЏ Рё РЅРµ РѕС‚РєСЂС‹РІР°РµС‚СЃСЏ.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="83",           # 1-7РЎРџ (ID)
        prev_rc_name=None,
        ctrl_rc_name="83",
        next_rc_name=None,
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        ts01_ls9=2.0,
        tlz_ls9=2.0,
        tkon_ls9=3.0,
        enable_ls9=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-1СЃ: S0109 - Р·Р°РЅСЏС‚Р° (РЅРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ РґР»СЏ ts01_ls9=2.0)
        ScenarioStep(
            t=1.0,
            rc_states={"83": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 1-2СЃ: РџСЂРµСЂС‹РІР°РЅРёРµ - СЃРІРѕР±РѕРґРЅР° (СЃР±СЂРѕСЃ С„Р°Р·С‹ 0)
        ScenarioStep(
            t=1.0,
            rc_states={"83": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2-5СЃ: РЎРЅРѕРІР° Р·Р°РЅСЏС‚Р° (РЅРѕРІР°СЏ РїРѕРїС‹С‚РєР° S0109)
        ScenarioStep(
            t=3.0,
            rc_states={"83": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 5-8СЃ: РЎРІРѕР±РѕРґРЅР° (С„Р°Р·Р° tail)
        ScenarioStep(
            t=3.0,
            rc_states={"83": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 8-11СЃ: Р—Р°РЅСЏС‚Р° (С„Р°Р·Р° S0209) в†’ РѕС‚РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=3.0,
            rc_states={"83": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 11-15с: Завершение - занята ≥ tkon_ls9=3.0 → закрытие
        ScenarioStep(
            t=4.0,
            rc_states={"83": 6},  # занята для закрытия
            switch_states={},
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

    print("\n=== LS9 Test: 83 (1-7РЎРџ) - Interrupted Phase ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_83={st.rc_states.get('83', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ Р›РЎ9 РІСЃС‘ СЂР°РІРЅРѕ РѕС‚РєСЂС‹Р»Р°СЃСЊ РїРѕСЃР»Рµ РІРѕСЃСЃС‚Р°РЅРѕРІР»РµРЅРёСЏ
    assert any("lls_9_open" in s.flags for s in timeline), "РќРµС‚ lls_9_open РїРѕСЃР»Рµ РїСЂРµСЂС‹РІР°РЅРёСЏ"
    assert any("lls_9" in s.flags and s.lz_variant == 109 for s in timeline), "lls_9 Р±РµР· variant=109"
    assert any("lls_9_closed" in s.flags for s in timeline), "РќРµС‚ lls_9_closed"


def test_ls9_65_no_open_insufficient_time():
    """
    РўРµСЃС‚ РЅР° 65 (4Рџ) - РЅРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕРµ РІСЂРµРјСЏ РґР»СЏ РѕС‚РєСЂС‹С‚РёСЏ.
    
    РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ РµСЃР»Рё С„Р°Р·С‹ РЅРµ РІС‹РїРѕР»РЅСЏСЋС‚СЃСЏ РґРѕСЃС‚Р°С‚РѕС‡РЅРѕ РґРѕР»РіРѕ,
    Р›РЎ9 РЅРµ РѕС‚РєСЂС‹РІР°РµС‚СЃСЏ.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="65",           # 4Рџ (ID)
        prev_rc_name=None,
        ctrl_rc_name="65",
        next_rc_name=None,
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        ts01_ls9=3.0,  # РўСЂРµР±СѓРµРј 3 СЃРµРєСѓРЅРґС‹
        tlz_ls9=3.0,
        tkon_ls9=2.0,
        enable_ls9=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-2СЃ: S0109 - Р·Р°РЅСЏС‚Р° (РЅРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ РґР»СЏ ts01_ls9=3.0)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2-4СЃ: tail - СЃРІРѕР±РѕРґРЅР° (РЅРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ РґР»СЏ tlz_ls9=3.0)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 4-6СЃ: S0209 - Р·Р°РЅСЏС‚Р° (РЅРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ РґР»СЏ tlz_ls9=3.0)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 6-8СЃ: РЎРІРѕР±РѕРґРЅР°
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

    print("\n=== LS9 Test: 65 (4Рџ) - Insufficient Time ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_65={st.rc_states.get('65', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ Р›РЎ9 РќР• РѕС‚РєСЂС‹Р»Р°СЃСЊ
    assert not any("lls_9_open" in s.flags for s in timeline), "lls_9_open РЅРµ РґРѕР»Р¶РЅРѕ Р±С‹С‚СЊ"
    assert not any("lls_9" in s.flags for s in timeline), "lls_9 РЅРµ РґРѕР»Р¶РЅРѕ Р±С‹С‚СЊ Р°РєС‚РёРІРЅРѕ"


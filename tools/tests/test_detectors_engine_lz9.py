# -*- coding: utf-8 -*-
"""
РўРµСЃС‚С‹ РґР»СЏ РІР°СЂРёР°РЅС‚Р° LZ9 (РџСЂРѕР±РѕР№ РёР·РѕР»РёСЂСѓСЋС‰РµРіРѕ СЃС‚С‹РєР°) СЃ РїРѕРґРґРµСЂР¶РєРѕР№ NC.

Р›РѕРіРёРєР°: РџРѕС‡С‚Рё РѕРґРЅРѕРІСЂРµРјРµРЅРЅРѕРµ Р·Р°РЅСЏС‚РёРµ С†РµРЅС‚СЂР° Рё СЃРѕСЃРµРґР° (|dt| <= tlz_lz9).
РЎРѕСЃРµРґРё РїСЂРѕРІРµСЂСЏСЋС‚СЃСЏ РїРѕ РјР°СЃРєРµ (Free | NC).
"""

from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_lz9_1p_ctrl_then_adj():
    """Р¦РµРЅС‚СЂ Р·Р°РЅСЏР»СЃСЏ, С‡РµСЂРµР· 1СЃ Р·Р°РЅСЏР»СЃСЏ СЃРѕСЃРµРґ -> LZ9."""
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False, enable_lz9=True,
        ts01_lz9=2.0, tlz_lz9=2.0, tkon_lz9=2.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-3СЃ: Р”Р°РЅРѕ (0-0-0)
        ScenarioStep(t=3.0, rc_states={"59": 3, "108": 3, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        # 3-4СЃ: Р¦РµРЅС‚СЂ Р·Р°РЅСЏР»СЃСЏ (t=0)
        ScenarioStep(t=1.0, rc_states={"59": 3, "108": 6, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        # 4-5СЃ: РЎРѕСЃРµРґ Р·Р°РЅСЏР»СЃСЏ (t=1, delta=1 <= 2) -> РћС‚РєСЂС‹С‚РёРµ
        ScenarioStep(t=1.0, rc_states={"59": 6, "108": 6, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        # 5-8СЃ: РўРєРѕРЅ
        ScenarioStep(t=3.0, rc_states={"59": 3, "108": 3, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()

    print("\n=== LZ9 Test: Ctrl First ===")
    for s in timeline:
        print(f"t={s.t:.1f}, lz={s.lz_state}, variant={s.lz_variant}, flags={s.flags}")

    assert any("llz_v9_open" in s.flags for s in timeline)
    assert any(s.lz_variant == 9 for s in timeline)
    assert any("llz_v9_closed" in s.flags for s in timeline)


def test_lz9_1p_adj_then_ctrl():
    """РЎРѕСЃРµРґ Р·Р°РЅСЏР»СЃСЏ, С‡РµСЂРµР· 1.5СЃ Р·Р°РЅСЏР»СЃСЏ С†РµРЅС‚СЂ -> LZ9."""
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108", prev_rc_name="59", ctrl_rc_name="108", next_rc_name="83",
        enable_lz9=True, ts01_lz9=1.0, tlz_lz9=2.0, tkon_lz9=2.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        ScenarioStep(t=2.0, rc_states={"59": 3, "108": 3, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        ScenarioStep(t=1.5, rc_states={"59": 6, "108": 3, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        ScenarioStep(t=0.5, rc_states={"59": 6, "108": 6, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        ScenarioStep(t=3.0, rc_states={"59": 3, "108": 3, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()
    assert any("llz_v9_open" in s.flags for s in timeline)


def test_lz9_nc_neighbor():
    """РћРґРёРЅ СЃРѕСЃРµРґ NC (С‚СѓРїРёРє). Р¦РµРЅС‚СЂ Р·Р°РЅСЏР»СЃСЏ -> РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ NC РЅРµ Р±Р»РѕРєРёСЂСѓРµС‚."""
    # Р Р¦ 59 (РѕР±С‹С‡РЅР°СЏ)
    det_cfg_59 = DetectorsConfig(
        ctrl_rc_id="59", prev_rc_name="47", ctrl_rc_name="59", next_rc_name="108",
        enable_lz9=True, ts01_lz9=1.0, tlz_lz9=2.0, tkon_lz9=2.0,
    )
    # Р Р¦ 57 (Р§Р”Рџ, РєСЂР°Р№РЅСЏСЏ)
    det_cfg_57 = DetectorsConfig(
        ctrl_rc_id="57", prev_rc_name="NONE", ctrl_rc_name="57", next_rc_name="58",
        enable_lz9=True, ts01_lz9=1.0, tlz_lz9=2.0, tkon_lz9=2.0,
    )
    
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_configs={"59": det_cfg_59, "57": det_cfg_57})

    scenario = [
        # 0-2СЃ: Р’СЃРµ СЃРІРѕР±РѕРґРЅС‹
        ScenarioStep(t=2.0, rc_states={"47": 3, "59": 3, "57": 3, "58": 3}, switch_states={"110": 3}, signal_states={}, modes={}),
        # 2-3СЃ: Р—Р°РЅСЏС‚РёРµ 47 Рё 58 (СЃРѕСЃРµРґРё)
        ScenarioStep(t=1.0, rc_states={"47": 6, "59": 3, "57": 3, "58": 6}, switch_states={"110": 3}, signal_states={}, modes={}),
        # 3-3.5СЃ: Р—Р°РЅСЏС‚РёРµ С†РµРЅС‚СЂРѕРІ 59 Рё 57 (BREAKDOWN)
        ScenarioStep(t=0.5, rc_states={"47": 6, "59": 6, "57": 6, "58": 6}, switch_states={"110": 3}, signal_states={}, modes={}),
        # 3.5-6.5СЃ: РЎРІРѕР±РѕРґРЅС‹
        ScenarioStep(t=3.0, rc_states={"47": 3, "59": 3, "57": 3, "58": 3}, switch_states={"110": 3}, signal_states={}, modes={}),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_ids=["59", "57"])
    timeline = ctx.run()
    
    # РџСЂРѕРІРµСЂСЏРµРј 57 (РєСЂР°Р№РЅСЋСЋ)
    results_57 = [step["57"] for step in timeline]
    assert any("llz_v9_open" in s.flags for s in results_57)
    assert any(s.lz_variant == 9 for s in results_57)


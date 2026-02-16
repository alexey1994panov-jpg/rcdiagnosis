# -*- coding: utf-8 -*-
"""
РўРµСЃС‚С‹ РґР»СЏ РІР°СЂРёР°РЅС‚Р° LS5 (Р—Р°РјС‹РєР°РЅРёРµ СЃРјРµР¶РЅРѕР№ Р Р¦)

Р›РѕРіРёРєР°: Р”РІРµ РІРµС‚РєРё, СѓС‡РµС‚ Р·Р°РјС‹РєР°РЅРёСЏ (state 4, 7).
- Р’РµС‚РєР° 1 (Prev): 100 (prev Р·Р°РЅСЏС‚Р°+Р·Р°РјРєРЅСѓС‚Р°, С†РµРЅС‚СЂ СЃРІРѕР±РѕРґРµРЅ+Р·Р°РјРєРЅСѓС‚) в†’ 101 (РѕР±Рµ Р·Р°РЅСЏС‚С‹+Р·Р°РјРєРЅСѓС‚С‹, С†РµРЅС‚СЂ СЃРІРѕР±РѕРґРµРЅ+Р·Р°РјРєРЅСѓС‚)
- Р’РµС‚РєР° 2 (Next): 001 (next Р·Р°РЅСЏС‚Р°+Р·Р°РјРєРЅСѓС‚Р°, С†РµРЅС‚СЂ СЃРІРѕР±РѕРґРµРЅ+Р·Р°РјРєРЅСѓС‚) в†’ 101 (РѕР±Рµ Р·Р°РЅСЏС‚С‹+Р·Р°РјРєРЅСѓС‚С‹, С†РµРЅС‚СЂ СЃРІРѕР±РѕРґРµРЅ+Р·Р°РјРєРЅСѓС‚)

Р—Р°РІРµСЂС€РµРЅРёРµ: С†РµРЅС‚СЂ Р·Р°РЅСЏС‚ (state 7) в‰Ґ tkon_ls5 в†’ Р·Р°РєСЂС‹С‚РёРµ
"""

from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_ls5_83_prev_branch_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» LS5 РЅР° 83 (1-7РЎРџ) РїРѕ РІРµС‚РєРµ Prev (100 в†’ 101).
    РСЃРїРѕР»СЊР·СѓРµРј СЃРѕСЃС‚РѕСЏРЅРёСЏ СЃ Р·Р°РјС‹РєР°РЅРёРµРј: 7 (Р·Р°РЅСЏС‚Р°+Р·Р°РјРєРЅСѓС‚Р°), 4 (СЃРІРѕР±РѕРґРЅР°+Р·Р°РјРєРЅСѓС‚Р°).
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="83",
        prev_rc_name="86",  # 1-3РЎРџ
        ctrl_rc_name="83",
        next_rc_name="81",  # 2Рџ
        enable_lz1=False, enable_ls5=True,
        ts01_ls5=2.0, tlz_ls5=2.0, tkon_ls5=2.0,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-3СЃ: Р¤Р°Р·Р° 0 - Prev Р·Р°РЅСЏС‚Р°+Р·Р°РјРєРЅСѓС‚Р° (7), Ctrl СЃРІРѕР±РѕРґРЅР°+Р·Р°РјРєРЅСѓС‚Р° (4), Next СЃРІРѕР±РѕРґРЅР° (3)
        ScenarioStep(
            t=3.0,
            rc_states={"86": 7, "83": 4, "81": 3},
            switch_states={"150": 9}, # СЃРѕРµРґРёРЅРµРЅРёРµ 86
            signal_states={}, modes={},
        ),
        # 3-6СЃ: Р¤Р°Р·Р° 1 - РћР±Рµ СЃРјРµР¶РЅС‹Рµ Р·Р°РЅСЏС‚С‹+Р·Р°РјРєРЅСѓС‚С‹ (7), Ctrl СЃРІРѕР±РѕРґРЅР°+Р·Р°РјРєРЅСѓС‚Р° (4) в†’ РѕС‚РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=3.0,
            rc_states={"86": 7, "83": 4, "81": 7},
            switch_states={"150": 9},
            signal_states={}, modes={},
        ),
        # 6-10СЃ: Р—Р°РІРµСЂС€РµРЅРёРµ - С†РµРЅС‚СЂ Р·Р°РЅСЏС‚ (7) в†’ Р·Р°РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=4.0,
            rc_states={"86": 7, "83": 7, "81": 7},
            switch_states={"150": 9},
            signal_states={}, modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="83")
    timeline = ctx.run()

    print("\n=== LS5 Test: 83 (1-7РЎРџ) - Prev Branch ===")
    for i, st in enumerate(timeline, start=1):
        print(f"{i}: t={st.t:.1f}, rc_86={st.rc_states.get('86',0)}, rc_83={st.rc_states.get('83',0)}, rc_81={st.rc_states.get('81',0)}, "
              f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}")

    assert any("lls_5_open" in s.flags for s in timeline), "РќРµС‚ lls_5_open"
    assert any("lls_5" in s.flags and s.lz_variant == 105 for s in timeline), "LLS_5 РЅРµ Р°РєС‚РёРІРЅР°"
    assert any("lls_5_closed" in s.flags for s in timeline), "РќРµС‚ lls_5_closed"


def test_ls5_108_next_branch_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» LS5 РЅР° 108 (1Рџ) РїРѕ РІРµС‚РєРµ Next (001 в†’ 101).
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59", 
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False, enable_ls5=True,
        ts01_ls5=2.0, tlz_ls5=2.0, tkon_ls5=2.0,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-3СЃ: Р¤Р°Р·Р° 0 - Next Р·Р°РЅСЏС‚Р°+Р·Р°РјРєРЅСѓС‚Р° (7), Ctrl СЃРІРѕР±РѕРґРЅР°+Р·Р°РјРєРЅСѓС‚Р° (4), Prev СЃРІРѕР±РѕРґРЅР° (3)
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 4, "83": 7},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 3-6СЃ: Р¤Р°Р·Р° 1 - РћР±Рµ СЃРјРµР¶РЅС‹Рµ Р·Р°РЅСЏС‚С‹+Р·Р°РјРєРЅСѓС‚С‹ (7), Ctrl СЃРІРѕР±РѕРґРЅР°+Р·Р°РјРєРЅСѓС‚Р° (4) в†’ РѕС‚РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=3.0,
            rc_states={"59": 7, "108": 4, "83": 7},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 6-10СЃ: Р—Р°РІРµСЂС€РµРЅРёРµ - С†РµРЅС‚СЂ Р·Р°РЅСЏС‚ (7) в†’ Р·Р°РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=4.0,
            rc_states={"59": 7, "108": 7, "83": 7},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()

    print("\n=== LS5 Test: 108 (1Рџ) - Next Branch ===")
    for i, st in enumerate(timeline, start=1):
        print(f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59',0)}, rc_108={st.rc_states.get('108',0)}, rc_83={st.rc_states.get('83',0)}, "
              f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}")

    assert any("lls_5_open" in s.flags for s in timeline), "РќРµС‚ lls_5_open"
    assert any("lls_5" in s.flags and s.lz_variant == 105 for s in timeline), "LLS_5 РЅРµ Р°РєС‚РёРІРЅР°"
    assert any("lls_5_closed" in s.flags for s in timeline), "РќРµС‚ lls_5_closed"


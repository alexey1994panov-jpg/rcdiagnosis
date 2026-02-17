# -*- coding: utf-8 -*-
from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_v7_108_from_json_like_legacy():
    """
    Р¦РёРєР» v7 РЅР° 1П РїРѕ С€Р°РіР°Рј РёР· JSON:
    1) 3 c СЃРІРѕР±РѕРґРЅРѕСЃС‚Рё 1П
    2) 3 c Р·Р°РЅСЏС‚РѕСЃС‚Рё 1П
    3) 3 c СЃРІРѕР±РѕРґРЅРѕСЃС‚Рё 1П
    РћР¶РёРґР°РµРј: С…РѕС‚СЏ Р±С‹ РѕРґРёРЅ open/active/closed v3.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 1П (ID)
        prev_rc_name="59",    # РёРјСЏ
        ctrl_rc_name="108",
        next_rc_name="83",
        ts01_lz1=0.0,              # v1 РѕС‚РєР»СЋС‡РµРЅР°
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        ts01_lz2=0.0,              # v2 РѕС‚РєР»СЋС‡РµРЅР°
        ts02_lz2=0.0,
        tlz_lz2=0.0,
        tkon_lz2=0.0,

        ts01_lz3=2.0,
        ts02_lz3=2.0,
        tlz_lz3=2.0,
        tkon_lz3=3.0,

        ts01_lz7=3.0,
        tlz_lz7=3.0,
        tkon_lz7=3.0,
        ts01_lz8 = 3.0,
    ts02_lz8 = 3.0,
    tlz_lz8 = 3.0,
    tkon_lz8 = 3.0,
	enable_lz8 = False,

        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz7=True,

    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # Р”РђРќРћ: 1П СЃРІРѕР±РѕРґРЅР°, СЃС‚СЂРµР»РєРё РЅРµ РІРµРґСѓС‚ (РІ РјРёРЅСѓСЃРµ)
        ScenarioStep(
            t=35.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 9, "88": 9, "110": 3},
            signal_states={},
            modes={},

        ),
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 9, "88": 9, "110": 3},
            signal_states={},
            modes={},

        ),
        # РљРћР“Р”Рђ: 1П Р·Р°РЅСЏС‚Р°, СЃС‚СЂРµР»РєРё РІСЃС‘ С‚Р°Рє Р¶Рµ РІ РјРёРЅСѓСЃРµ
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            switch_states={"87": 9, "88": 9, "110": 3},
            signal_states={},
            modes={},
  
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            switch_states={"87": 9, "88": 9, "110": 3},
            signal_states={},
            modes={},

        ),
        # Р—Р°РІРµСЂС€РµРЅРёРµ: 1П СЃРЅРѕРІР° СЃРІРѕР±РѕРґРЅР°, СЃС‚СЂРµР»РєРё РїРѕвЂ‘РїСЂРµР¶РЅРµРјСѓ РІ РјРёРЅСѓСЃРµ
        ScenarioStep(
            t=15.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 9, "88": 9, "110": 3},
            signal_states={},
            modes={},

        ),
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 9, "88": 9, "110": 3},
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

    assert any("llz_v7_open" in s.flags for s in timeline)
    assert any("llz_v7" in s.flags and s.lz_variant == 7 for s in timeline)
    assert any("llz_v7_closed" in s.flags for s in timeline)


def test_v7_108_minus_branch_from_json():
    """
    Р¦РёРєР» v7 РЅР° 1П РїСЂРё РґРІРёР¶РµРЅРёРё РїРѕ РјРёРЅСѓСЃРѕРІРѕРјСѓ РЅР°РїСЂР°РІР»РµРЅРёСЋ:
    С€Р°РіРё РїРѕР»РЅРѕСЃС‚СЊСЋ СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓСЋС‚ РІС‚РѕСЂРѕРјСѓ JSON-СЃС†РµРЅР°СЂРёСЋ.
    РћР¶РёРґР°РµРј РѕРґРёРЅ РїРѕР»РЅС‹Р№ С†РёРєР» v3.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        ts01_lz1=0.0,
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        ts01_lz2=0.0,
        ts02_lz2=0.0,
        tlz_lz2=0.0,
        tkon_lz2=0.0,

        ts01_lz3=2.0,
        ts02_lz3=2.0,
        tlz_lz3=2.0,
        tkon_lz3=3.0,

        ts01_lz7=3.0,
        tlz_lz7=3.0,
        tkon_lz7=3.0,
        ts01_lz8 = 3.0,
    ts02_lz8 = 3.0,
    tlz_lz8 = 3.0,
    tkon_lz8 = 3.0,
	enable_lz8 = False,

        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz7=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # Р”РђРќРћ: 1П СЃРІРѕР±РѕРґРЅР°, СЃС‚СЂРµР»РєРё РЅРµ РІРµРґСѓС‚ (РІ РјРёРЅСѓСЃРµ)
        ScenarioStep(
            t=35.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 9, "88": 9, "110": 9},
            signal_states={},
            modes={},

        ),
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 9, "88": 9, "110": 9},
            signal_states={},
            modes={},

        ),
        # РљРћР“Р”Рђ: 1П Р·Р°РЅСЏС‚Р°, СЃС‚СЂРµР»РєРё РІСЃС‘ С‚Р°Рє Р¶Рµ РІ РјРёРЅСѓСЃРµ
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            switch_states={"87": 9, "88": 9, "110": 9},
            signal_states={},
            modes={},
  
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 6, "83": 3},
            switch_states={"87": 9, "88": 9, "110": 9},
            signal_states={},
            modes={},

        ),
        # Р—Р°РІРµСЂС€РµРЅРёРµ: 1П СЃРЅРѕРІР° СЃРІРѕР±РѕРґРЅР°, СЃС‚СЂРµР»РєРё РїРѕвЂ‘РїСЂРµР¶РЅРµРјСѓ РІ РјРёРЅСѓСЃРµ
        ScenarioStep(
            t=15.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 9, "88": 9, "110": 9},
            signal_states={},
            modes={},

        ),
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"87": 9, "88": 9, "110": 9},
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

    assert any("llz_v7_open" in s.flags for s in timeline)
    assert any("llz_v7" in s.flags and s.lz_variant == 7 for s in timeline)
    assert any("llz_v7_closed" in s.flags for s in timeline)


def test_v7_user_json_on_1p_must_not_open() -> None:
    """
    Регрессия по пользовательскому JSON:
    - контролируемая РЦ: 1П (ID=108),
    - соседи заданы через топологию (10-12СП и 1-7СП),
    - стрелки в плюсе,
    - 1П переключается занято/свободно.

    Ожидаем: LZ7 не должна открываться, потому что у 1П есть смежные РЦ.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz7=True,
        ts01_lz7=3.0,
        tlz_lz7=3.0,
        tkon_lz7=3.0,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    # Sw10=87, Sw1=88, Sw5=110 (в плюсе).
    sw_plus = {"87": 3, "88": 3, "110": 3}
    scenario = [
        ScenarioStep(
            t=5.0,
            rc_states={"59": 6, "108": 6, "83": 3},
            switch_states=sw_plus,
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=7.0,
            rc_states={"59": 6, "108": 3, "83": 3},
            switch_states=sw_plus,
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=7.0,
            rc_states={"59": 6, "108": 6, "83": 3},
            switch_states=sw_plus,
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=9.0,
            rc_states={"59": 6, "108": 6, "83": 3},
            switch_states=sw_plus,
            signal_states={},
            modes={},
        ),
    ]

    timeline = list(SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108").run())

    assert not any("llz_v7_open" in s.flags for s in timeline)
    assert not any("llz_v7" in s.flags and s.lz_variant == 7 for s in timeline)
    assert not any("llz_v7_closed" in s.flags for s in timeline)


def test_v7_must_not_open_when_both_neighbors_exist_and_free() -> None:
    """
    Regression for false-positive v7:
    when both effective neighbors exist and are free, v7 must not open
    (no_adjacent/no_prev/no_next branches are inapplicable).
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz7=True,
        ts01_lz7=3.0,
        tlz_lz7=3.0,
        tkon_lz7=3.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)
    sw_plus = {"87": 3, "88": 3, "110": 3}
    scenario = [
        ScenarioStep(t=3.0, rc_states={"59": 3, "108": 6, "83": 3}, switch_states=sw_plus, signal_states={}, modes={}),
        ScenarioStep(t=3.0, rc_states={"59": 3, "108": 3, "83": 3}, switch_states=sw_plus, signal_states={}, modes={}),
        ScenarioStep(t=6.0, rc_states={"59": 3, "108": 6, "83": 3}, switch_states=sw_plus, signal_states={}, modes={}),
    ]
    timeline = list(SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108").run())
    assert not any("llz_v7_open" in s.flags for s in timeline)
    assert not any("llz_v7" in s.flags and s.lz_variant == 7 for s in timeline)



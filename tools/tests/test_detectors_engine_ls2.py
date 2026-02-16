# -*- coding: utf-8 -*-
"""
РўРµСЃС‚С‹ РґР»СЏ РІР°СЂРёР°РЅС‚Р° LS2 (РђСЃРёРјРјРµС‚СЂРёС‡РЅР°СЏ Р»РѕР¶РЅР°СЏ СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ)

LS2 РґРµС‚РµРєС‚РёСЂСѓРµС‚ Р»РѕР¶РЅСѓСЋ СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ РїРѕ РґРІСѓРј РІРµС‚РєР°Рј:
- Р’РµС‚РєР° 1 (Prev): 110 в†’ 100 в†’ 110
- Р’РµС‚РєР° 2 (Next): 011 в†’ 001 в†’ 011

Р¤Р°Р·С‹:
    0: (110 РёР»Рё 011) в†’ ts01_ls2
    1: (100 РёР»Рё 001 - С†РµРЅС‚СЂ РѕСЃРІРѕР±РѕРґРёР»СЃСЏ) в†’ tlz_ls2
    2: (110 РёР»Рё 011 - С†РµРЅС‚СЂ СЃРЅРѕРІР° Р·Р°РЅСЏС‚) в†’ ts02_ls2 в†’ РѕС‚РєСЂС‹С‚РёРµ
    Р—Р°РІРµСЂС€РµРЅРёРµ: РІСЃРµ СЃРІРѕР±РѕРґРЅС‹ в‰Ґ tkon_ls2 в†’ Р·Р°РєСЂС‹С‚РёРµ
"""

from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_ls2_108_prev_branch_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» LS2 РЅР° 108 (1Рџ) РїРѕ РІРµС‚РєРµ Prev (110 в†’ 100 в†’ 110).
    
    РЎС†РµРЅР°СЂРёР№:
    - 3 С€Р°РіР°: 110 (10-12РЎРџ Рё 1Рџ Р·Р°РЅСЏС‚С‹)
    - 3 С€Р°РіР°: 100 (10-12РЎРџ Р·Р°РЅСЏС‚Р°, 1Рџ РѕСЃРІРѕР±РѕРґРёР»Р°СЃСЊ)
    - 4 С€Р°РіР°: 110 (СЃРЅРѕРІР° РѕР±Рµ Р·Р°РЅСЏС‚С‹) в†’ РѕС‚РєСЂС‹С‚РёРµ
    - 4 С€Р°РіР°: 000 (РІСЃРµ СЃРІРѕР±РѕРґРЅС‹) в†’ Р·Р°РєСЂС‹С‚РёРµ
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",  # 10-12РЎРџ
        ctrl_rc_name="108",
        next_rc_name="83",  # 1-7РЎРџ
        enable_lz1=False, enable_lz2=False, enable_lz3=False,
        enable_ls2=True,
        ts01_ls2=2.0, tlz_ls2=2.0, ts02_ls2=2.0, tkon_ls2=3.0,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-3СЃ: Р¤Р°Р·Р° 0 - 110 (Prev=59, Ctrl=108)
        ScenarioStep(
            t=3.0,
            rc_states={"59": 6, "108": 6, "83": 3},
            switch_states={"110": 3, "88": 3}, # РЎРѕСЃРµРґРё Р°РєС‚РёРІРЅС‹
            signal_states={}, modes={},
        ),
        # 3-6СЃ: Р¤Р°Р·Р° 1 - 100 (59 Р·Р°РЅСЏС‚Р°, 108 РѕСЃРІРѕР±РѕРґРёР»Р°СЃСЊ)
        ScenarioStep(
            t=3.0,
            rc_states={"59": 6, "108": 3, "83": 3},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 6-10СЃ: Р¤Р°Р·Р° 2 - 110 (СЃРЅРѕРІР° Р·Р°РЅСЏС‚С‹) в†’ РѕС‚РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=4.0,
            rc_states={"59": 6, "108": 6, "83": 3},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
        # 10-15СЃ: Р—Р°РІРµСЂС€РµРЅРёРµ - 000 (РІСЃРµ СЃРІРѕР±РѕРґРЅС‹) в†’ Р·Р°РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=5.0,
            rc_states={"59": 3, "108": 3, "83": 3},
            switch_states={"110": 3, "88": 3},
            signal_states={}, modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()

    print("\n=== LS2 Test: 108 (1Рџ) - Prev Branch ===")
    for i, st in enumerate(timeline, start=1):
        print(f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59',0)}, rc_108={st.rc_states.get('108',0)}, "
              f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}")

    assert any("lls_2_open" in s.flags for s in timeline), "РќРµС‚ lls_2_open"
    assert any("lls_2" in s.flags and s.lz_variant == 102 for s in timeline), "LLS_2 РЅРµ Р°РєС‚РёРІРЅР°"
    assert any("lls_2_closed" in s.flags for s in timeline), "РќРµС‚ lls_1_closed"


def test_ls2_59_next_branch_full_cycle():
    """
    РџРѕР»РЅС‹Р№ С†РёРєР» LS2 РЅР° 59 (10-12РЎРџ) РїРѕ РІРµС‚РєРµ Next (011 в†’ 001 в†’ 011).
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",
        prev_rc_name="47", 
        ctrl_rc_name="59",
        next_rc_name="108",
        enable_lz1=False, enable_ls2=True,
        ts01_ls2=1.5, tlz_ls2=1.5, ts02_ls2=1.5, tkon_ls2=2.0,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-2СЃ: Р¤Р°Р·Р° 0 - 011 (Ctrl=59, Next=108)
        ScenarioStep(
            t=2.0,
            rc_states={"47": 3, "59": 6, "108": 6},
            switch_states={"110": 3},
            signal_states={}, modes={},
        ),
        # 2-4СЃ: Р¤Р°Р·Р° 1 - 001 (59 РѕСЃРІРѕР±РѕРґРёР»Р°СЃСЊ, 108 Р·Р°РЅСЏС‚Р°)
        ScenarioStep(
            t=2.0,
            rc_states={"47": 3, "59": 3, "108": 6},
            switch_states={"110": 3},
            signal_states={}, modes={},
        ),
        # 4-6СЃ: Р¤Р°Р·Р° 2 - 011 (СЃРЅРѕРІР° Р·Р°РЅСЏС‚С‹) в†’ РѕС‚РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=2.0,
            rc_states={"47": 3, "59": 6, "108": 6},
            switch_states={"110": 3},
            signal_states={}, modes={},
        ),
        # 6-9СЃ: Р—Р°РІРµСЂС€РµРЅРёРµ - 000 в†’ Р·Р°РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=3.0,
            rc_states={"47": 3, "59": 3, "108": 3},
            switch_states={"110": 3},
            signal_states={}, modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="59")
    timeline = ctx.run()

    print("\n=== LS2 Test: 59 (10-12РЎРџ) - Next Branch ===")
    for i, st in enumerate(timeline, start=1):
        print(f"{i}: t={st.t:.1f}, rc_59={st.rc_states.get('59',0)}, rc_108={st.rc_states.get('108',0)}, "
              f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}")

    assert any("lls_2_open" in s.flags for s in timeline), "РќРµС‚ lls_2_open"
    assert any("lls_2" in s.flags and s.lz_variant == 102 for s in timeline), "LLS_2 РЅРµ Р°РєС‚РёРІРЅР°"
    assert any("lls_2_closed" in s.flags for s in timeline), "РќРµС‚ lls_2_closed"


def test_ls2_user_scenario_split_1s_open_and_close():
    """
    Проверка user-сценария (5s -> 7s -> 7s -> 9s) для LS2 на 1П:
    - должно быть открытие LS2;
    - закрытие должно происходить только после добавленного хвоста свободного
      состояния ctrl на время >= tkon_ls2.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz4=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        enable_lz9=False,
        enable_lz10=False,
        enable_lz11=False,
        enable_lz12=False,
        enable_lz13=False,
        enable_ls1=False,
        enable_ls2=True,
        ts01_ls2=2.0,
        ts02_ls2=2.0,
        tlz_ls2=2.0,
        tkon_ls2=10.0,
        enable_ls4=False,
        enable_ls5=False,
        enable_ls6=False,
        enable_ls9=False,
        enable_lz_exc_mu=False,
        enable_lz_exc_recent_ls=False,
        enable_lz_exc_dsp=False,
        enable_ls_exc_mu=False,
        enable_ls_exc_after_lz=False,
        enable_ls_exc_dsp=False,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = []
    # 5s: 110
    for _ in range(5):
        scenario.append(
            ScenarioStep(
                t=1.0,
                rc_states={"59": 6, "108": 6, "83": 3},
                switch_states={"110": 3, "88": 3},
                signal_states={},
                modes={},
            )
        )
    # 7s: 100
    for _ in range(7):
        scenario.append(
            ScenarioStep(
                t=1.0,
                rc_states={"59": 6, "108": 3, "83": 3},
                switch_states={"110": 3, "88": 3},
                signal_states={},
                modes={},
            )
        )
    # 7s: 110
    for _ in range(7):
        scenario.append(
            ScenarioStep(
                t=1.0,
                rc_states={"59": 6, "108": 6, "83": 3},
                switch_states={"110": 3, "88": 3},
                signal_states={},
                modes={},
            )
        )
    # 9s: 110
    for _ in range(9):
        scenario.append(
            ScenarioStep(
                t=1.0,
                rc_states={"59": 6, "108": 6, "83": 3},
                switch_states={"110": 3, "88": 3},
                signal_states={},
                modes={},
            )
        )
    # +10s: 000 (добавлено для гарантированного закрытия по tkon_ls2)
    for _ in range(10):
        scenario.append(
            ScenarioStep(
                t=1.0,
                rc_states={"59": 3, "108": 3, "83": 3},
                switch_states={"110": 3, "88": 3},
                signal_states={},
                modes={},
            )
        )

    timeline = list(SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108").run())

    assert any("lls_2_open" in s.flags for s in timeline), "Нет lls_2_open на user-сценарии"
    assert any("lls_2_closed" in s.flags for s in timeline), "Нет lls_2_closed после free-хвоста >= tkon_ls2"


def test_ls2_not_open_when_sw10_control_lost_longer_than_tpk():
    """
    Негативный кейс по user-сценарию:
    при потере контроля Sw10 дольше T_PK детектор LS2 должен сбрасываться,
    и последующее восстановление занятости ctrl не должно открыть LS2.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 1П
        prev_rc_name="59",         # 10-12СП
        ctrl_rc_name="108",
        next_rc_name="83",         # 1-7СП
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz4=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        enable_lz9=False,
        enable_lz10=False,
        enable_lz11=False,
        enable_lz12=False,
        enable_lz13=False,
        enable_ls1=False,
        enable_ls2=True,
        ts01_ls2=3.0,
        ts02_ls2=3.0,
        tlz_ls2=3.0,
        tkon_ls2=3.0,
        enable_ls4=False,
        enable_ls5=False,
        enable_ls6=False,
        enable_ls9=False,
        enable_lz_exc_mu=False,
        enable_lz_exc_recent_ls=False,
        enable_lz_exc_dsp=False,
        enable_ls_exc_mu=False,
        enable_ls_exc_after_lz=False,
        enable_ls_exc_dsp=False,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 011 (phase-0 branch for LS2) -> set precondition
        ScenarioStep(
            t=1.0,
            rc_states={"83": 6, "59": 3, "108": 6},
            switch_states={"87": 3, "110": 3, "88": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=2.0,
            rc_states={"83": 6, "59": 3, "108": 6},
            switch_states={"87": 3, "110": 3, "88": 3},
            signal_states={},
            modes={},
        ),
        # 001-like phase + перевод стрелок, затем длительная потеря контроля Sw10 (>T_PK)
        ScenarioStep(
            t=1.0,
            rc_states={"83": 6, "59": 3, "108": 3},
            switch_states={"87": 6, "110": 6, "88": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=32.0,
            rc_states={"83": 6, "59": 3, "108": 3},
            switch_states={"87": 6, "110": 15, "88": 3},  # Sw10 no-control > T_PK
            signal_states={},
            modes={},
        ),
        # Возврат занятости ctrl после истечения T_PK не должен открыть LS2
        ScenarioStep(
            t=1.0,
            rc_states={"83": 6, "59": 3, "108": 6},
            switch_states={"87": 6, "110": 3, "88": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"83": 6, "59": 3, "108": 6},
            switch_states={"87": 6, "110": 3, "88": 3},
            signal_states={},
            modes={},
        ),
    ]

    timeline = list(SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108").run())

    assert not any("lls_2_open" in s.flags for s in timeline), \
        "LS2 не должна открываться после потери контроля Sw10 дольше T_PK"


def test_ls2_not_open_user_case_with_long_no_control_interval():
    """
    Регрессия по пользовательскому сценарию:
    - формируется начало паттерна LS2;
    - затем длительный шаг с no-control по Sw10 (t=32) обнуляет топологическую
      валидность соседей для ветки;
    - после восстановления control LS2 не должна открываться.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 1П
        prev_rc_name="59",         # 10-12СП
        ctrl_rc_name="108",
        next_rc_name="83",         # 1-7СП
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz4=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        enable_lz9=False,
        enable_lz10=False,
        enable_lz11=False,
        enable_lz12=False,
        enable_lz13=False,
        enable_ls1=False,
        enable_ls2=True,
        ts01_ls2=3.0,
        ts02_ls2=3.0,
        tlz_ls2=3.0,
        tkon_ls2=3.0,
        enable_ls4=False,
        enable_ls5=False,
        enable_ls6=False,
        enable_ls9=False,
        enable_lz_exc_mu=False,
        enable_lz_exc_recent_ls=False,
        enable_lz_exc_dsp=False,
        enable_ls_exc_mu=False,
        enable_ls_exc_after_lz=False,
        enable_ls_exc_dsp=False,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0..1: стартовая занятость ctrl (подготовка)
        ScenarioStep(
            t=1.0,
            rc_states={"83": 6, "59": 3, "108": 6},
            switch_states={"87": 3, "110": 3, "89": 3},
            signal_states={},
            modes={},
        ),
        # 1..3: продолжаем фазу с ctrl=1
        ScenarioStep(
            t=2.0,
            rc_states={"83": 6, "59": 3, "108": 6},
            switch_states={"87": 3, "110": 3, "89": 3},
            signal_states={},
            modes={},
        ),
        # 3..4: ctrl освобождается + перевод стрелок
        ScenarioStep(
            t=1.0,
            rc_states={"83": 6, "59": 3, "108": 3},
            switch_states={"87": 6, "110": 6, "89": 3},
            signal_states={},
            modes={},
        ),
        # 4..36: длительная потеря контроля Sw10 (no-control)
        ScenarioStep(
            t=32.0,
            rc_states={"83": 6, "59": 3, "108": 3},
            switch_states={"87": 6, "110": 15, "89": 3},
            signal_states={},
            modes={},
        ),
        # 36..41: возврат занятости ctrl при восстановленном управлении
        ScenarioStep(
            t=1.0,
            rc_states={"83": 6, "59": 3, "108": 6},
            switch_states={"87": 6, "110": 3, "89": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"83": 6, "59": 3, "108": 6},
            switch_states={"87": 6, "110": 3, "89": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"83": 6, "59": 3, "108": 6},
            switch_states={"87": 6, "110": 3, "89": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"83": 6, "59": 3, "108": 6},
            switch_states={"87": 6, "110": 3, "89": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"83": 6, "59": 3, "108": 6},
            switch_states={"87": 6, "110": 3, "89": 3},
            signal_states={},
            modes={},
        ),
    ]

    timeline = list(SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108").run())
    assert not any("lls_2_open" in s.flags for s in timeline), \
        "LS2 не должна открываться в сценарии с длительной потерей контроля Sw10"


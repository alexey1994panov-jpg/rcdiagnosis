# -*- coding: utf-8 -*-
from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig

def test_lz13_full_cycle_prev():
    """
    РўРµСЃС‚ LZ13 (РІРµС‚РєР° Prev).
    01: adj free+locked (4), ctrl free (3), sig closed (15)
    02: adj occ+locked (7), ctrl free (3), sig closed (15)
    РљРћР“Р”Рђ: adj occ+locked (7), ctrl occ (6), sig closed (15) -> РѕС‚РєСЂС‹С‚РёРµ Р›Р—13
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",
        prev_rc_name="47", # Adj
        next_rc_name="57",
        enable_lz13=True,
        ts01_lz13=2.0,
        ts02_lz13=2.0,
        tlz_lz13=2.0,
        tkon_lz13=3.0,
        sig_lz13_prev="114", # Р§1
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0-3СЃ: Р¤Р°Р·Р° 01 (adj free+locked=4)
        ScenarioStep(
            t=3.0,
            rc_states={"47": 4, "59": 3, "57": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
        # 3-6СЃ: Р¤Р°Р·Р° 02 (adj occ+locked=7, ctrl free=3)
        ScenarioStep(
            t=3.0,
            rc_states={"47": 7, "59": 3, "57": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
        # 6-9СЃ: Р¤Р°Р·Р° РљРћР“Р”Рђ (adj occ+locked=7, ctrl occ=6) -> РѕС‚РєСЂС‹С‚РёРµ
        ScenarioStep(
            t=3.0,
            rc_states={"47": 7, "59": 6, "57": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
        # 9-13СЃ: РЎРІРѕР±РѕРґРЅР° -> Р·Р°РєСЂС‹С‚РёРµ РїРѕ tkon=3.0
        ScenarioStep(
            t=4.0,
            rc_states={"47": 3, "59": 3, "57": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="59",
    )

    timeline = ctx.run()

    print("\n=== LZ13 Test: 59 (branch Prev) ===")
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t:.1f}, rc_47={st.rc_states.get('47', 0)}, rc_59={st.rc_states.get('59', 0)}, "
            f"sig_114={st.signal_states.get('114', 0)}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("llz_v13_open" in s.flags for s in timeline), "РќРµС‚ llz_v13_open"
    assert any("llz_v13" in s.flags and s.lz_variant == 13 for s in timeline), "llz_v13 Р±РµР· variant=13"
    assert any("llz_v13_closed" in s.flags for s in timeline), "РќРµС‚ llz_v13_closed"

def test_lz13_no_open_not_locked():
    """
    LZ13 РЅРµ РґРѕР»Р¶РЅР° РѕС‚РєСЂС‹РІР°С‚СЊСЃСЏ РµСЃР»Рё adj РЅРµ Р·Р°РјРєРЅСѓС‚Р°.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",
        prev_rc_name="47",
        enable_lz13=True,
        ts01_lz13=1.0, ts02_lz13=1.0, tlz_lz13=1.0, tkon_lz13=1.0,
        sig_lz13_prev="114",
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # adj free РЅРѕ РќР• Р·Р°РјРєРЅСѓС‚Р° (3 РІРјРµСЃС‚Рѕ 4)
        ScenarioStep(
            t=2.0,
            rc_states={"47": 3, "59": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
        # adj occ РЅРѕ РќР• Р·Р°РјРєРЅСѓС‚Р° (6 РІРјРµСЃС‚Рѕ 7)
        ScenarioStep(
            t=2.0,
            rc_states={"47": 6, "59": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
        # Р·Р°РЅСЏС‚РёРµ ctrl
        ScenarioStep(
            t=2.0,
            rc_states={"47": 6, "59": 6},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="59")
    timeline = ctx.run()

    assert not any("llz_v13_open" in s.flags for s in timeline), "llz_v13_open Р±РµР· Р·Р°РјС‹РєР°РЅРёСЏ!"


def test_lz13_open_when_adj_occupied_without_lock_on_phase2_and_kogda():
    """
    Новое правило: в фазах 02/КОГДА для соседней РЦ достаточно занятости (6/7/8),
    замыкание не обязательно.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",
        prev_rc_name="47",
        enable_lz13=True,
        ts01_lz13=2.0,
        ts02_lz13=2.0,
        tlz_lz13=2.0,
        tkon_lz13=2.0,
        sig_lz13_prev="114",
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # Фаза 01: adj free+locked (4), ctrl free
        ScenarioStep(
            t=2.0,
            rc_states={"47": 4, "59": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
        # Фаза 02: adj occupied without lock (6), ctrl free
        ScenarioStep(
            t=2.0,
            rc_states={"47": 6, "59": 3},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
        # КОГДА: adj occupied without lock (6), ctrl occupied
        ScenarioStep(
            t=2.0,
            rc_states={"47": 6, "59": 6},
            switch_states={},
            signal_states={"114": 15},
            modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="59")
    timeline = ctx.run()

    assert any("llz_v13_open" in s.flags for s in timeline), "Нет llz_v13_open при adj=6 на фазах 02/КОГДА"


def test_lz13_dynamic_signal_for_rc_1_7sp_prev_1p():
    """
    Регресс: для ctrl=1-7СП (83) сигнал должен подтягиваться динамически (Ч1=114,
    связь 108 -> 83 через текущее положение стрелок), без ручного sig_lz13_prev.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="83",      # 1-7СП
        prev_rc_name="108",   # 1П
        next_rc_name="81",
        enable_lz13=True,
        ts01_lz13=3.0,
        ts02_lz13=3.0,
        tlz_lz13=3.0,
        tkon_lz13=3.0,
        sig_lz13_prev=None,
        sig_lz13_next=None,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    sw = {"87": 3, "88": 3, "110": 3, "111": 3}
    scenario = [
        # Фаза 01: prev=1П свободная+замкнутая, ctrl=1-7СП свободная, Ч1 закрыт
        ScenarioStep(
            t=3.0,
            rc_states={"108": 4, "83": 3, "81": 3},
            switch_states=sw,
            signal_states={"114": 15},
            modes={},
        ),
        # Фаза 02: prev занята, ctrl свободная
        ScenarioStep(
            t=3.0,
            rc_states={"108": 7, "83": 3, "81": 3},
            switch_states=sw,
            signal_states={"114": 15},
            modes={},
        ),
        # КОГДА: prev занята, ctrl занята -> открыть LZ13
        ScenarioStep(
            t=3.0,
            rc_states={"108": 7, "83": 6, "81": 3},
            switch_states=sw,
            signal_states={"114": 15},
            modes={},
        ),
        # Закрытие по tkon
        ScenarioStep(
            t=4.0,
            rc_states={"108": 3, "83": 3, "81": 3},
            switch_states=sw,
            signal_states={"114": 15},
            modes={},
        ),
    ]

    timeline = list(SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="83").run())
    assert any("llz_v13_open" in s.flags for s in timeline), "Нет llz_v13_open для ctrl=83 с Ч1"


def test_lz13_dynamic_signal_for_rc_10_12sp_next_1p():
    """
    Регресс: для ctrl=10-12СП (59) и adj=1П (108) LZ13 должна брать сигнал
    в направлении adj->ctrl (НМ1=107), а не ctrl->adj.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",      # 10-12СП
        prev_rc_name="47",    # 1АП
        next_rc_name="108",   # 1П
        enable_lz13=True,
        ts01_lz13=3.0,
        ts02_lz13=3.0,
        tlz_lz13=3.0,
        tkon_lz13=3.0,
        sig_lz13_prev=None,
        sig_lz13_next=None,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # Фаза 01: adj(next)=1П свободна+замкнута, ctrl свободна, НМ1 закрыт
        ScenarioStep(
            t=3.0,
            rc_states={"47": 3, "59": 3, "108": 4},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={"107": 15},
            modes={},
        ),
        # Фаза 02: adj(next)=1П занята, ctrl свободна
        ScenarioStep(
            t=3.0,
            rc_states={"47": 3, "59": 3, "108": 7},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={"107": 15},
            modes={},
        ),
        # КОГДА: adj(next)=1П занята, ctrl занята -> открыть LZ13
        ScenarioStep(
            t=3.0,
            rc_states={"47": 3, "59": 6, "108": 7},
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={"107": 15},
            modes={},
        ),
    ]

    timeline = list(SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="59").run())
    assert any("llz_v13_open" in s.flags for s in timeline), "Нет llz_v13_open для ctrl=59 с adj=108/НМ1"


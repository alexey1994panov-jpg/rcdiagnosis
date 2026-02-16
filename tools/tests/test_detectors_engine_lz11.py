# -*- coding: utf-8 -*-
import pytest

from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def test_lz11_full_cycle():
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",
        ctrl_rc_name="59",
        enable_lz11=True,
        ts01_lz11=2.0,
        tlz_lz11=2.0,
        tkon_lz11=3.0,
        sig_lz11_a="114",  # Ч1
        sig_lz11_b="107",  # НМ1
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3},
            switch_states={},
            signal_states={"114": 15, "107": 15},
            modes={},
        ),
        ScenarioStep(
            t=6.0,
            rc_states={"59": 6},
            switch_states={},
            signal_states={"114": 15, "107": 15},
            modes={},
        ),
        ScenarioStep(
            t=10.0,
            rc_states={"59": 3},
            switch_states={},
            signal_states={"114": 15, "107": 15},
            modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="59")
    timeline = ctx.run()

    assert any("llz_v11_open" in s.flags for s in timeline), "Нет llz_v11_open"
    assert any("llz_v11" in s.flags and s.lz_variant == 11 for s in timeline), "llz_v11 без variant=11"
    assert any("llz_v11_closed" in s.flags for s in timeline), "Нет llz_v11_closed"


def test_lz11_no_open_signal_open():
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",
        ctrl_rc_name="59",
        enable_lz11=True,
        ts01_lz11=2.0,
        tlz_lz11=2.0,
        tkon_lz11=3.0,
        sig_lz11_a="114",  # Ч1
        sig_lz11_b="107",  # НМ1
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        ScenarioStep(
            t=3.0,
            rc_states={"59": 3},
            switch_states={},
            signal_states={"114": 3, "107": 15},
            modes={},
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"59": 6},
            switch_states={},
            signal_states={"114": 3, "107": 15},
            modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="59")
    timeline = ctx.run()

    assert not any("llz_v11_open" in s.flags for s in timeline), "llz_v11_open при открытом сигнале!"


def test_lz11_2p_no_open_when_adj_signals_open():
    """
    LZ11 на 2П не должна открываться, если смежные светофоры открыты.

    2П: RC=90
    Сигналы: Ч2=92, НМ2=89
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="90",
        ctrl_rc_name="90",
        enable_lz11=True,
        ts01_lz11=2.0,
        tlz_lz11=2.0,
        tkon_lz11=3.0,
        sig_lz11_a="92",   # Ч2
        sig_lz11_b="89",   # НМ2
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        ScenarioStep(
            t=3.0,
            rc_states={"90": 3, "94": 3, "86": 3},
            switch_states={"73": 3, "150": 3},
            signal_states={"92": 11, "89": 11},
            modes={},
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"90": 6, "94": 3, "86": 3},
            switch_states={"73": 3, "150": 3},
            signal_states={"92": 11, "89": 11},
            modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="90")
    timeline = ctx.run()

    assert not any("llz_v11_open" in s.flags for s in timeline), (
        "LZ11 не должна открываться на 2П при открытых смежных сигналах"
    )


@pytest.mark.xfail(
    reason="Заготовка: требуется топологическая проверка 'стрелки ведут на ctrl' в LZ11.",
    strict=False,
)
def test_lz11_2p_no_open_when_route_not_to_2p_and_signals_closed():
    """
    Заготовка под условие:
    при закрытых сигналах, но маршруте мимо 2П — LZ11 не должна формироваться.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="90",
        ctrl_rc_name="90",
        enable_lz11=True,
        ts01_lz11=2.0,
        tlz_lz11=2.0,
        tkon_lz11=3.0,
        sig_lz11_a="92",
        sig_lz11_b="89",
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        ScenarioStep(
            t=3.0,
            rc_states={"90": 3, "94": 3, "86": 3},
            switch_states={"73": 9, "150": 9},
            signal_states={"92": 15, "89": 15},
            modes={},
        ),
        ScenarioStep(
            t=3.0,
            rc_states={"90": 6, "94": 3, "86": 3},
            switch_states={"73": 9, "150": 9},
            signal_states={"92": 15, "89": 15},
            modes={},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="90")
    timeline = ctx.run()

    assert not any("llz_v11_open" in s.flags for s in timeline), (
        "При маршруте мимо 2П LZ11 не должна открываться"
    )

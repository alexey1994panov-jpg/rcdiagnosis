# tests/test_variant7_1p.py

import pytest

from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p
from engine.types_1p import ScenarioStep


@pytest.fixture(scope="session")
def station():
    return get_station_model_1p()


def test_variant7_no_adjacent_with_sw_minus(station):
    # опции, максимально близкие к твоему JSON, плюс включаем v7
    options = {
        "t_s0101": 3,
        "t_lz01": 3,
        "t_kon_v1": 3,
        "t_pause_v1": 0,
        "enable_v1": True,
        "t_s0102": 3,
        "t_s0202": 3,
        "t_lz02": 3,
        "t_kon_v2": 3,
        "t_pause_v2": 0,
        "enable_v2": True,
        "t_s0103": 3,
        "t_s0203": 3,
        "t_lz03": 3,
        "t_kon_v3": 3,
        "t_pause_v3": 0,
        "enable_v3": True,
        # v5 выключаем, чтобы не мешал
        "enable_v5": False,
        # v6 оставим как есть
        "t_s06": 10,
        "t_lz06": 600,
        "t_kon_v6": 10,
        "t_pause_v6": 0,
        "enable_v6": True,
        # v7 — целевой вариант
        "t_s07": 2,
        "t_lz07": 2,
        "t_kon_v7": 2,
        "t_pause_v7": 0,
        "enable_v7": True,
        # v8
        "t_s0108": 3,
        "t_s0208": 3,
        "t_lz08": 3,
        "t_kon_v8": 3,
        "t_pause_v8": 0,
        "enable_v8": True,
        # LS v1
        "t_c0101_ls": 3,
        "t_ls01": 3,
        "t_kon_ls1": 3,
        "t_pause_ls1": 0,
        "enable_ls1": True,
        # LS v2
        "t_s0102_ls": 3,
        "t_s0202_ls": 3,
        "t_ls0102": 2,
        "t_ls0202": 10,
        "t_kon_ls2": 3,
        "t_pause_ls2": 0,
        "enable_ls2": True,
        # LS v4
        "t_s0104_ls": 3,
        "t_s0204_ls": 3,
        "t_ls0104": 3,
        "t_ls0204": 10,
        "t_kon_ls4": 3,
        "t_pause_ls4": 0,
        "enable_ls4": True,
        # LS v9
        "t_s0109_ls": 2,
        "t_s0209_ls": 2,
        "t_ls0109": 1,
        "t_ls0209": 3,
        "t_kon_ls9": 3,
        "t_pause_ls9": 0,
        "enable_ls9": True,
        # исключения
        "t_mu": 15,
        "t_recent_ls": 30,
        "t_min_maneuver_v8": 600,
        "enable_lz_exc_mu": True,
        "enable_lz_exc_recent_ls": True,
        "enable_lz_exc_dsp": True,
        "enable_ls_exc_mu": True,
        "enable_ls_exc_after_lz": True,
        "enable_ls_exc_dsp": True,
    }

    # шаги: как в JSON, но Sw10/Sw1/Sw5 всегда 9 (минус, свободна, не замкнута)
    steps = [
        # ДАНО: 1P свободна, стрелки не ведут (в минусе)
        ScenarioStep(
            t=1,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 9, "Sw1": 9, "Sw5": 9},
            modes={},
            mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
        ),
        ScenarioStep(
            t=1,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 9, "Sw1": 9, "Sw5": 9},
            modes={},
            mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
        ),
        # КОГДА: 1P занята, стрелки всё так же в минусе
        ScenarioStep(
            t=1,
            rc_states={"10-12SP": 3, "1P": 6, "1-7SP": 3},
            switch_states={"Sw10": 9, "Sw1": 9, "Sw5": 9},
            modes={},
            mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
        ),
        ScenarioStep(
            t=1,
            rc_states={"10-12SP": 3, "1P": 6, "1-7SP": 3},
            switch_states={"Sw10": 9, "Sw1": 9, "Sw5": 9},
            modes={},
            mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
        ),
        # Завершение: 1P снова свободна, стрелки по‑прежнему в минусе
        ScenarioStep(
            t=1,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 9, "Sw1": 9, "Sw5": 9},
            modes={},
            mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
        ),
        ScenarioStep(
            t=1,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 9, "Sw1": 9, "Sw5": 9},
            modes={},
            mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
        ),
    ]

    timeline = simulate_1p(station, steps, dt=1.0, options=options)

    opens = [s for s in timeline if "llz_v7_open" in s.flags]
    closes = [s for s in timeline if "llz_v7_closed" in s.flags]

    # базовые проверки работы варианта 7
    assert opens, "Нет llz_v7_open при стрелках в положении 9"
    assert closes, "Нет llz_v7_closed при стрелках в положении 9"
    assert any("llz_v7" in s.flags for s in timeline), "Нет активного llz_v7"
    assert any(s.lz_state and s.variant == 7 for s in timeline), "ЛЗ v7 не формируется при стрелках в положении 9"

# tests/test_variant7_from_json_1p.py

import pytest

from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p
from engine.types_1p import ScenarioStep


@pytest.fixture(scope="session")
def station():
    return get_station_model_1p()


def test_variant7_from_json(station):
    # опции — взяты из твоего JSON, важное: enable_v7 = True
    options = {
        "t_s0101": 3,
        "t_lz01": 3,
        "t_kon_v1": 3,
        "t_pause_v1": 0,
        "enable_v1": False,
        "t_s0102": 3,
        "t_s0202": 3,
        "t_lz02": 3,
        "t_kon_v2": 3,
        "t_pause_v2": 0,
        "enable_v2": False,
        "t_s0103": 3,
        "t_s0203": 3,
        "t_lz03": 3,
        "t_kon_v3": 3,
        "t_pause_v3": 0,
        "enable_v3": False,
        "t_s0401": 3,
        "t_lz04": 3,
        "t_kon_v4": 3,
        "t_pause_v4": 0,
        "enable_v4": False,
        "t_s05": 1,
        "t_lz05": 1,
        "t_pk": 30,
        "t_kon_v5": 3,
        "t_pause_v5": 0,
        "enable_v5": False,
        "t_s06": 10,
        "t_lz06": 600,
        "t_kon_v6": 10,
        "t_pause_v6": 0,
        "enable_v6": False,
        "t_s07": 3,
        "t_lz07": 3,
        "t_kon_v7": 3,
        "t_pause_v7": 0,
        "enable_v7": True,
        "t_s0108": 3,
        "t_s0208": 3,
        "t_lz08": 3,
        "t_kon_v8": 3,
        "t_pause_v8": 0,
        "enable_v8": False,
        "t_s0109": 3,
        "t_lz09": 3,
        "t_kon_v9": 3,
        "t_pause_v9": 0,
        "enable_v9": False,
        "t_s0110": 3,
        "t_s0210": 3,
        "t_s0310": 3,
        "t_lz10": 3,
        "t_kon_v10": 3,
        "t_pause_v10": 0,
        "enable_v10": False,
        "t_s11": 3,
        "t_lz11": 3,
        "t_kon_v11": 3,
        "t_pause_v11": 0,
        "enable_v11": False,
        "t_s0112": 3,
        "t_s0212": 3,
        "t_lz12": 3,
        "t_kon_v12": 3,
        "t_pause_v12": 0,
        "enable_v12": False,
        "t_s0113": 10,
        "t_s0213": 10,
        "t_lz13": 10,
        "t_kon_v13": 10,
        "t_pause_v13": 0,
        "enable_v13": False,
        "v13_ctrl_rc_id": "10-12SP",
        "t_c0101_ls": 3,
        "t_ls01": 3,
        "t_kon_ls1": 3,
        "t_pause_ls1": 0,
        "enable_ls1": False,
        "t_s0102_ls": 3,
        "t_s0202_ls": 3,
        "t_ls0102": 2,
        "t_ls0202": 10,
        "t_kon_ls2": 3,
        "t_pause_ls2": 0,
        "enable_ls2": False,
        "t_s0104_ls": 3,
        "t_s0204_ls": 3,
        "t_ls0104": 3,
        "t_ls0204": 10,
        "t_kon_ls4": 3,
        "t_pause_ls4": 0,
        "enable_ls4": False,
        "t_s0109_ls": 2,
        "t_s0209_ls": 2,
        "t_ls0109": 1,
        "t_ls0209": 3,
        "t_kon_ls9": 3,
        "t_pause_ls9": 0,
        "enable_ls9": False,
        "t_mu": 0,
        "t_recent_ls": 0,
        "t_min_maneuver_v8": 0,
        "enable_lz_exc_mu": True,
        "enable_lz_exc_recent_ls": True,
        "enable_lz_exc_dsp": True,
        "t_ls_mu": 0,
        "t_ls_after_lz": 0,
        "t_ls_dsp": 0,
        "enable_ls_exc_mu": True,
        "enable_ls_exc_after_lz": True,
        "enable_ls_exc_dsp": True,
    }

    # шаги 1-в-1 из твоего JSON
    steps = [
        ScenarioStep(
            t=3,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 9, "Sw1": 9, "Sw5": 3},
            modes={},
            mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
            signal_states={"Ч1": 0, "НМ1": 0, "ЧМ1": 0, "М1": 0},
        ),
        ScenarioStep(
            t=3,
            rc_states={"10-12SP": 3, "1P": 6, "1-7SP": 3},
            switch_states={"Sw10": 9, "Sw1": 9, "Sw5": 3},
            modes={},
            mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
            signal_states={"Ч1": 0, "НМ1": 0, "ЧМ1": 0, "М1": 0},
        ),
        ScenarioStep(
            t=3,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 9, "Sw1": 9, "Sw5": 3},
            modes={},
            mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
            signal_states={"Ч1": 0, "НМ1": 0, "ЧМ1": 0, "М1": 0},
        ),
    ]

    timeline = simulate_1p(station, steps, dt=1.0, options=options)

    opens = [s for s in timeline if "llz_v7_open" in s.flags]
    closes = [s for s in timeline if "llz_v7_closed" in s.flags]

    # базовые проверки работы варианта 7 в этом сценарии
    assert opens, "Нет llz_v7_open в сценарии из JSON"
    assert closes, "Нет llz_v7_closed в сценарии из JSON"
    assert any("llz_v7" in s.flags for s in timeline), "Нет активного llz_v7 в сценарии из JSON"
    assert any(s.lz_state and s.variant == 7 for s in timeline), "ЛЗ v7 не формируется в сценарии из JSON"

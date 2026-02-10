import pytest

from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p
from engine.types_1p import ScenarioStep


@pytest.fixture(scope="session")
def station():
    return get_station_model_1p()


def test_variant6_from_json_front_scenario(station):
    options = {
        "t_s0101": 3.0,
        "t_lz01": 3.0,
        "t_kon_v1": 3.0,
        "t_pause_v1": 0.0,
        "enable_v1": False,
        "t_s0102": 3.0,
        "t_s0202": 3.0,
        "t_lz02": 3.0,
        "t_kon_v2": 3.0,
        "t_pause_v2": 0.0,
        "enable_v2": False,
        "t_s0103": 3.0,
        "t_s0203": 3.0,
        "t_lz03": 3.0,
        "t_kon_v3": 3.0,
        "t_pause_v3": 0.0,
        "enable_v3": False,
        # ЛЗ v6
        "t_s06": 1.0,
        "t_lz06": 1.0,
        "t_kon_v6": 1.0,
        "enable_v6": True,
        # ЛЗ v8
        "t_s0108": 3.0,
        "t_s0208": 3.0,
        "t_lz08": 3.0,
        "t_kon_v8": 3.0,
        "t_pause_v8": 0.0,
        "enable_v8": False,
        # ЛС v1
        "t_c0101_ls": 3.0,
        "t_ls01": 3.0,
        "t_kon_ls1": 3.0,
        "t_pause_ls1": 0.0,
        "enable_ls1": True,
        # ЛС v2
        "t_s0102_ls": 3.0,
        "t_s0202_ls": 3.0,
        "t_ls0102": 2.0,
        "t_ls0202": 10.0,
        "t_kon_ls2": 3.0,
        "t_pause_ls2": 0.0,
        "enable_ls2": True,
        # ЛС v4
        "t_s0104_ls": 3.0,
        "t_s0204_ls": 3.0,
        "t_ls0104": 3.0,
        "t_ls0204": 10.0,
        "t_kon_ls4": 3.0,
        "t_pause_ls4": 0.0,
        "enable_ls4": True,
        # ЛС v9
        "t_s0109_ls": 2.0,
        "t_s0209_ls": 2.0,
        "t_ls0109": 1.0,
        "t_ls0209": 3.0,
        "t_kon_ls9": 3.0,
        "t_pause_ls9": 0.0,
        "enable_ls9": True,
        # Исключения ЛЗ
        "t_mu": 15.0,
        "t_recent_ls": 30.0,
        "t_min_maneuver_v8": 600.0,
        "enable_lz_exc_mu": True,
        "enable_lz_exc_recent_ls": True,
        "enable_lz_exc_dsp": True,
        # Исключения ЛС
        "enable_ls_exc_mu": True,
        "enable_ls_exc_after_lz": True,
        "enable_ls_exc_dsp": True,
    }

    steps = [
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
            mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 6, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
            mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
            mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
        ),
    ]

    timeline = simulate_1p(station, steps, dt=1.0, options=options)

    opens = [s for s in timeline if "llz_v6_open" in s.flags]
    closes = [s for s in timeline if "llz_v6_closed" in s.flags]

    assert opens, "Нет llz_v6_open"
    assert closes, "Нет llz_v6_closed"
    assert any("llz_v6" in s.flags for s in timeline), "Нет активного llz_v6"
    # проверим, что ЛЗ действительно есть на шаге с детектором
    assert any(s.lz_state and s.variant == 6 for s in timeline), "ЛЗ v6 не формируется"

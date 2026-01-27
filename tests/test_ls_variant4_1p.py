import pytest
from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p
from engine.types_1p import ScenarioStep


@pytest.fixture(scope="session")
def station():
    return get_station_model_1p()


def make_step(t, rc_1012, rc_1p, rc_17):
    return ScenarioStep(
        t=float(t),
        rc_states={"10-12SP": rc_1012, "1P": rc_1p, "1-7SP": rc_17},
        switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
        modes={},
        mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
        dispatcher_control_state=4,
        auto_actions={"NAS": 4, "CHAS": 4},
    )


def test_ls_variant4_from_json(station):
    # Опции под ЛС4
    opts = {
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
        "t_s0108": 3.0,
        "t_s0208": 3.0,
        "t_lz08": 3.0,
        "t_kon_v8": 3.0,
        "t_pause_v8": 0.0,
        "enable_v8": False,
        "t_c0101_ls": 3.0,
        "t_ls01": 3.0,
        "t_kon_ls1": 3.0,
        "t_pause_ls1": 0.0,
        "enable_ls1": False,
        "t_s0102_ls": 3.0,
        "t_s0202_ls": 3.0,
        "t_ls0102": 3.0,
        "t_ls0202": 12.0,
        "t_kon_ls2": 3.0,
        "t_pause_ls2": 0.0,
        "enable_ls2": False,
        "t_s0104_ls": 3.0,
        "t_s0204_ls": 3.0,
        "t_ls0104": 3.0,
        "t_ls0204": 12.0,
        "t_kon_ls4": 3.0,
        "t_pause_ls4": 0.0,
        "enable_ls4": True,
        "t_s0109_ls": 3.0,
        "t_s0209_ls": 3.0,
        "t_ls0109": 3.0,
        "t_ls0209": 3.0,
        "t_kon_ls9": 3.0,
        "t_pause_ls9": 0.0,
        "enable_ls9": False,
        "t_mu": 0.0,
        "t_recent_ls": 0.0,
        "t_min_maneuver_v8": 0.0,
        "enable_lz_exc_mu": True,
        "enable_lz_exc_recent_ls": True,
        "enable_lz_exc_dsp": True,
        "t_ls_mu": 0.0,
        "t_ls_after_lz": 0.0,
        "t_ls_dsp": 0.0,
        "enable_ls_exc_mu": True,
        "enable_ls_exc_after_lz": True,
        "enable_ls_exc_dsp": True,
    }

    # 4 шага S0104: Prev=1, Curr=1, Next=1 (1-1-1)
    s0104_steps = [
        make_step(1, rc_1012=6, rc_1p=6, rc_17=6),
        make_step(1, rc_1012=6, rc_1p=6, rc_17=6),
        make_step(1, rc_1012=6, rc_1p=6, rc_17=6),
        make_step(1, rc_1012=6, rc_1p=6, rc_17=6),
    ]

    # 4 шага хвоста: Prev=1, Curr=0, Next=1 (1-0-1)
    tail_steps = [
        make_step(1, rc_1012=6, rc_1p=3, rc_17=6),
        make_step(1, rc_1012=6, rc_1p=3, rc_17=6),
        make_step(1, rc_1012=6, rc_1p=3, rc_17=6),
        make_step(1, rc_1012=6, rc_1p=3, rc_17=6),
    ]

    # 6 шагов S0204 + завершение: снова 1-1-1
    s0204_and_close_steps = [
        make_step(1, rc_1012=6, rc_1p=6, rc_17=6),
        make_step(1, rc_1012=6, rc_1p=6, rc_17=6),
        make_step(1, rc_1012=6, rc_1p=6, rc_17=6),
        make_step(1, rc_1012=6, rc_1p=6, rc_17=6),
        make_step(1, rc_1012=6, rc_1p=6, rc_17=6),
        make_step(1, rc_1012=6, rc_1p=6, rc_17=6),
    ]

    steps = s0104_steps + tail_steps + s0204_and_close_steps

    timeline = simulate_1p(station, steps, dt=1.0, options=opts)

    # ЛС4 должна открыться и быть активной
    assert any("lls_v4_open" in s.flags for s in timeline), "Нет lls_v4_open"
    assert any("lls_v4" in s.flags for s in timeline), "Нет активного lls_v4"

    # И успеть завершиться (закрыться) в конце сценария
    assert any("lls_v4_closed" in s.flags for s in timeline), "Нет lls_v4_closed"

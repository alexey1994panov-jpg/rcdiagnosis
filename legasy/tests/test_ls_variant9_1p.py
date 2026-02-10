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
        modes={},  # prev/next control ok
        mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
        dispatcher_control_state=4,
        auto_actions={"NAS": 4, "CHAS": 4},
    )


def test_ls_variant9_from_json(station):
    # Опции из JSON-сценария для v9
    opts = {
        "t_s0101": 15.0,
        "t_lz01": 5.0,
        "t_kon_v1": 10.0,
        "t_pause_v1": 0.0,
        "enable_v1": False,
        "t_s0102": 5.0,
        "t_s0202": 15.0,
        "t_lz02": 10.0,
        "t_kon_v2": 10.0,
        "t_pause_v2": 0.0,
        "enable_v2": False,
        "t_s0103": 5.0,
        "t_s0203": 15.0,
        "t_lz03": 10.0,
        "t_kon_v3": 10.0,
        "t_pause_v3": 0.0,
        "enable_v3": False,
        "t_s0108": 10.0,
        "t_s0208": 10.0,
        "t_lz08": 10.0,
        "t_kon_v8": 10.0,
        "t_pause_v8": 0.0,
        "enable_v8": False,
        "t_c0101_ls": 20.0,
        "t_ls01": 10.0,
        "t_kon_ls1": 10.0,
        "t_pause_ls1": 0.0,
        "enable_ls1": False,
        # В JSON для v9 свои ключи, здесь включаем только v9
        "t_s0102_ls": 5.0,
        "t_s0202_ls": 15.0,
        "t_ls0102": 2.0,
        "t_ls0202": 10.0,
        "t_kon_ls2": 10.0,
        "t_pause_ls2": 0.0,
        "enable_ls2": False,
        "t_s0104_ls": 2.0,
        "t_s0204_ls": 2.0,
        "t_ls0104": 2.0,
        "t_ls0204": 10.0,
        "t_kon_ls4": 3.0,
        "t_pause_ls4": 0.0,
        "enable_ls4": False,
        "t_s0109_ls": 2.0,
        "t_s0209_ls": 2.0,
        "t_ls0109": 2.0,
        "t_ls0209": 6.0,
        "t_kon_ls9": 3.0,
        "t_pause_ls9": 0.0,
        "enable_ls9": True,
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

    # Сценарий из JSON:
    # 3 шага: 10-12SP свободна, 1P занята (3-6-3),
    # 3 шага: 10-12SP и 1P свободны (3-3-3),
    # 6 шагов: снова 10-12SP свободна, 1P занята (3-6-3).
    steps = [
        make_step(1, rc_1012=3, rc_1p=6, rc_17=3),
        make_step(1, rc_1012=3, rc_1p=6, rc_17=3),
        make_step(1, rc_1012=3, rc_1p=6, rc_17=3),
        make_step(1, rc_1012=3, rc_1p=3, rc_17=3),
        make_step(1, rc_1012=3, rc_1p=3, rc_17=3),
        make_step(1, rc_1012=3, rc_1p=3, rc_17=3),
        make_step(1, rc_1012=3, rc_1p=6, rc_17=3),
        make_step(1, rc_1012=3, rc_1p=6, rc_17=3),
        make_step(1, rc_1012=3, rc_1p=6, rc_17=3),
        make_step(1, rc_1012=3, rc_1p=6, rc_17=3),
        make_step(1, rc_1012=3, rc_1p=6, rc_17=3),
        make_step(1, rc_1012=3, rc_1p=6, rc_17=3),
    ]

    timeline = simulate_1p(station, steps, dt=1.0, options=opts)

    # ЛС v9 должна открыться, быть активной и завершиться в пределах сценария
    assert any("lls_v9_open" in s.flags for s in timeline), "Нет lls_v9_open"
    assert any("lls_v9" in s.flags for s in timeline), "Нет активного lls_v9"
    assert any("lls_v9_closed" in s.flags for s in timeline), "Нет lls_v9_closed"

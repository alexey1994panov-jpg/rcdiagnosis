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
        # Стрелки фиксируем в контролируемом положении (плюс/норма),
        # чтобы для замкнутой 1P смежные определялись по стрелкам (ветка 3.1).
        switch_states={"Sw10": 9, "Sw1": 9, "Sw5": 9},
        modes={},
        mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
        dispatcher_control_state=4,
        auto_actions={"NAS": 4, "CHAS": 4},
        signal_states={},
    )


def test_variant9_1_lock_scenario(station):
    opts = {
        "enable_v1": False,
        "enable_v2": False,
        "enable_v3": False,
        "enable_v5": False,
        "enable_v6": False,
        "enable_v7": False,
        "enable_v8": False,
        "enable_v10": False,
        "enable_v11": False,
        "enable_v12": False,
        "enable_ls1": False,
        "enable_ls2": False,
        "enable_ls4": False,
        "enable_ls9": False,
        "enable_v9": True,
        "t_s0109": 3.0,
        "t_lz09": 3.0,
        "t_kon_v9": 3.0,
        "t_pause_v9": 0.0,
    }

    steps = [
        make_step(3.0, rc_1012=3, rc_1p=4, rc_17=3),
        make_step(1.0, rc_1012=3, rc_1p=7, rc_17=6),
        make_step(1.0, rc_1012=3, rc_1p=7, rc_17=6),
        make_step(3.0, rc_1012=3, rc_1p=7, rc_17=6),
        make_step(3.0, rc_1012=3, rc_1p=3, rc_17=3),
    ]

    timeline = simulate_1p(station, steps, dt=1.0, options=opts)

    # В этом сценарии 9.1 НЕ должен сработать:
    # стрелки всегда в положении, когда смежные не ведут на 1П,
    # значит смежность для замкнутой ctrl не определяется и ДС не формируется.
    assert all(s.variant != 9 for s in timeline), "variant 9 не должен срабатывать в этом сценарии"
    assert all("llz_v9" not in s.flags for s in timeline), "ЛЗ9 не должно быть активно в этом сценарии"
    assert all("llz_v9_open" not in s.flags for s in timeline), "Не должно быть открытия v9"
    assert all("llz_v9_closed" not in s.flags for s in timeline), "Не должно быть закрытия v9"
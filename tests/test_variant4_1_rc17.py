import pytest

from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p
from engine.types_1p import ScenarioStep


@pytest.fixture(scope="session")
def station():
    return get_station_model_1p()


def make_step(t, rc_1012, rc_1p, rc_17, m1_state=3):
    return ScenarioStep(
        t=float(t),
        rc_states={"10-12SP": rc_1012, "1P": rc_1p, "1-7SP": rc_17},
        switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
        signal_states={"М1": m1_state},
        modes={},
        mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
        dispatcher_control_state=4,
        auto_actions={"NAS": 4, "CHAS": 4},
    )


def test_variant4_for_17sp(station):
    # включаем только v4, остальные ЛЗ/ЛС вырубаем
    opts = {
        "enable_v1": False,
        "enable_v2": False,
        "enable_v3": False,
        "enable_v4": True,
        "enable_v5": False,
        "enable_v6": False,
        "enable_v7": False,
        "enable_v8": False,
        "enable_v9": False,
        "enable_v10": False,
        "enable_v11": False,
        "enable_v12": False,
        "enable_ls1": False,
        "enable_ls2": False,
        "enable_ls4": False,
        "enable_ls9": False,
        "t_s0401": 3.0,
        "t_lz04": 3.0,
        "t_kon_v4": 3.0,
        "t_pause_v4": 0.0,
    }

    steps = [
        # ДАНО: prev NC (край), curr свободна, next свободна (1P), М1 закрыт, 3 сек
        make_step(3.0, rc_1012=3, rc_1p=3, rc_17=3, m1_state=3),
        # КОГДА: curr занята, М1 закрыт, 3 сек
        make_step(3.0, rc_1012=3, rc_1p=3, rc_17=6, m1_state=3),
        # Завершение: curr свободна, 3 сек
        make_step(3.0, rc_1012=3, rc_1p=3, rc_17=3, m1_state=3),
    ]

    timeline = simulate_1p(station, steps, dt=1.0, options=opts)

    # Должен быть хотя бы один шаг с вариантом 4
    assert any(s.variant == 4 for s in timeline), "Нет шага с variant == 4"

    # Активное состояние v4
    assert any("llz_v4" in s.flags for s in timeline), "Нет активного v4 (llz_v4)"

    # Открытие ДС v4
    assert any("llz_v4_open" in s.flags for s in timeline), "Нет открытия v4 (llz_v4_open)"

    # Закрытие ДС v4
    assert any("llz_v4_closed" in s.flags for s in timeline), "Нет закрытия v4 (llz_v4_closed)"

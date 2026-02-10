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
        switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
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

    # Ветка 3.1 (ctrl замкнута):
    # 1) 3 cек: ctrl свободна, замкнута, смежные свободны (ДАНО)
    # 2) 1 сек: prev занята, ctrl и next свободны
    # 3) 1 сек: prev занята, ctrl занята, next свободна (|Δt| ≤ t_lz09 -> открытие v9)
    # 4) 3 сек: prev занята, ctrl занята, next свободна (ДС активно)
    # 5) 3 сек: prev свободна, ctrl свободна, next свободна (Tкон9 -> закрытие v9)
    steps = [
        make_step(3.0, rc_1012=3, rc_1p=4, rc_17=3),
        make_step(1.0, rc_1012=3, rc_1p=7, rc_17=6),
        make_step(1.0, rc_1012=3, rc_1p=7, rc_17=6),
        make_step(3.0, rc_1012=3, rc_1p=7, rc_17=6),
        make_step(3.0, rc_1012=3, rc_1p=3, rc_17=3),
    ]

    timeline = simulate_1p(station, steps, dt=1.0, options=opts)

    assert any(s.variant == 9 for s in timeline), "Нет шага с variant == 9"
    assert any("llz_v9" in s.flags and s.variant == 9 for s in timeline), "Нет активного v9 (llz_v9)"
    assert any("llz_v9_open" in s.flags for s in timeline), "Нет открытия v9 (llz_v9_open)"
    assert any("llz_v9_closed" in s.flags for s in timeline), "Нет закрытия v9 (llz_v9_closed)"

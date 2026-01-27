# tests/test_variant5_1p.py

import pytest

from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p
from engine.types_1p import ScenarioStep


@pytest.fixture(scope="session")
def station():
    return get_station_model_1p()


def test_variant5_from_json_front_scenario(station):
    options = {
        # ЛЗ v1–v3 выключены
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

        # ЛЗ v5 (с замыканием) — включаем
        "t_s05": 1.0,
        "t_lz05": 1.0,
        "t_kon_v5": 1.0,
        "t_pause_v5": 0.0,
        "enable_v5": True,

        # ЛЗ v6, v8 выключены
        "t_s06": 10.0,
        "t_lz06": 600.0,
        "t_kon_v6": 10.0,
        "enable_v6": False,

        "t_s0108": 3.0,
        "t_s0208": 3.0,
        "t_lz08": 3.0,
        "t_kon_v8": 3.0,
        "t_pause_v8": 0.0,
        "enable_v8": False,

        # ЛС как в твоём тесте (можно оставить включёнными)
        "t_c0101_ls": 3.0,
        "t_ls01": 3.0,
        "t_kon_ls1": 3.0,
        "t_pause_ls1": 0.0,
        "enable_ls1": True,

        "t_s0102_ls": 3.0,
        "t_s0202_ls": 3.0,
        "t_ls0102": 2.0,
        "t_ls0202": 10.0,
        "t_kon_ls2": 3.0,
        "t_pause_ls2": 0.0,
        "enable_ls2": True,

        "t_s0104_ls": 3.0,
        "t_s0204_ls": 3.0,
        "t_ls0104": 3.0,
        "t_ls0204": 10.0,
        "t_kon_ls4": 3.0,
        "t_pause_ls4": 0.0,
        "enable_ls4": True,

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
        # Разрешаем рассматривать состояния с замыканием (4,5,7,8) как свободные/занятые
        "allow_route_lock_states": True,
    }

    # Будем работать по РЦ 1-7SP (у неё rc_has_route_lock == True).[file:8]
    rc_id = "1-7SP"

    steps = [
        # ДАНО: РЦ свободна (3) >= Ts05=1.0
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, rc_id: 3},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
            mu={"10-12SP": 3, "1P": 3, rc_id: 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
        ),
        # КОГДА: РЦ занята (6) >= Tlz05=1.0 → открытие v5
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, rc_id: 6},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
            mu={"10-12SP": 3, "1P": 3, rc_id: 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
        ),
        # Завершение: снова свободна (3) >= Tkon_v5=1.0 → закрытие v5
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, rc_id: 3},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
            mu={"10-12SP": 3, "1P": 3, rc_id: 3},
            dispatcher_control_state=4,
            auto_actions={"NAS": 4, "CHAS": 4},
        ),
    ]

    timeline = simulate_1p(station, steps, dt=1.0, options=options)

    opens = [s for s in timeline if "llz_v5_open" in s.flags]
    closes = [s for s in timeline if "llz_v5_closed" in s.flags]

    assert opens, "Нет llz_v5_open"
    assert closes, "Нет llz_v5_closed"
    assert any("llz_v5" in s.flags for s in timeline), "Нет активного llz_v5"
    assert any(s.lz_state and s.variant == 5 for s in timeline), "ЛЗ v5 не формируется"

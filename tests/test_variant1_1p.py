import pytest
from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p
from engine.types_1p import ScenarioStep


@pytest.fixture(scope="session")
def station():
    return get_station_model_1p()


def test_variant1_from_json(station):
    # Опции ровно как в JSON
    opts_dict = {
        "t_s0101": 2.0,
        "t_lz01": 2.0,
        "t_kon_v1": 3.0,
        "t_pause_v1": 0.0,
        "enable_v1": True,
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
    }

    steps = [
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 6, "1-7SP": 3},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 6, "1-7SP": 3},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
    ]

    timeline = simulate_1p(station, steps, dt=1.0, options=opts_dict)

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # Проверки по ЛЗ v1
    assert any("llz_v1_open" in s.flags for s in timeline), "Нет llz_v1_open"
    assert any("llz_v1" in s.flags and s.variant == 1 for s in timeline), "llz_v1 без variant=1"
    assert any("llz_v1_closed" in s.flags for s in timeline), "Нет llz_v1_closed"

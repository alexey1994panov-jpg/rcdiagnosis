import pytest
from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p
from engine.types_1p import ScenarioStep


@pytest.fixture(scope="session")
def station():
    return get_station_model_1p()


def test_variant1_no_adjacent_no_ds(station):
    # Опции ровно как в JSON
    opts_dict = {
        "t_s0101": 3.0,
        "t_lz01": 3.0,
        "t_kon_v1": 3.0,
        "t_pause_v1": 0.0,
        "enable_v1": True,
        "t_s0102": 3.0,
        "t_s0202": 3.0,
        "t_lz02": 3.0,
        "t_kon_v2": 3.0,
        "t_pause_v2": 0.0,
        "enable_v2": True,
        "t_s0103": 3.0,
        "t_s0203": 3.0,
        "t_lz03": 3.0,
        "t_kon_v3": 3.0,
        "t_pause_v3": 0.0,
        "enable_v3": True,
        "t_s0401": 0.0,
        "t_lz04": 0.0,
        "t_kon_v4": 0.0,
        "t_pause_v4": 0.0,
        "enable_v4": True,
        "t_s05": 0.0,
        "t_lz05": 0.0,
        "t_pk": 0.0,
        "t_kon_v5": 0.0,
        "t_pause_v5": 0.0,
        "enable_v5": False,
        "t_s06": 0.0,
        "t_lz06": 0.0,
        "t_kon_v6": 0.0,
        "t_pause_v6": 0.0,
        "enable_v6": False,
        "t_s07": 0.0,
        "t_lz07": 0.0,
        "t_kон_v7": 0.0,  # как в JSON
        "t_pause_v7": 0.0,
        "enable_v7": False,
        "t_s0108": 0.0,
        "t_s0208": 0.0,
        "t_lz08": 0.0,
        "t_kon_v8": 0.0,
        "t_pause_v8": 0.0,
        "enable_v8": True,
        "t_s0109": 0.0,
        "t_lz09": 0.0,
        "t_kon_v9": 0.0,
        "t_pause_v9": 0.0,
        "enable_v9": True,
        "t_s0110": 0.0,
        "t_s0210": 0.0,
        "t_s0310": 0.0,
        "t_lz10": 0.0,
        "t_kon_v10": 0.0,
        "t_pause_v10": 0.0,
        "enable_v10": True,
        "t_s11": 0.0,
        "t_lz11": 0.0,
        "t_kon_v11": 0.0,
        "t_pause_v11": 0.0,
        "enable_v11": True,
        "t_s0112": 0.0,
        "t_s0212": 0.0,
        "t_lz12": 0.0,
        "t_kon_v12": 0.0,
        "t_pause_v12": 0.0,
        "enable_v12": True,
        "t_s0113": 0.0,
        "t_s0213": 0.0,
        "t_lz13": 0.0,
        "t_kon_v13": 0.0,
        "t_pause_v13": 0.0,
        "enable_v13": True,
        "t_c0101_ls": 0.0,
        "t_ls01": 0.0,
        "t_kon_ls1": 0.0,
        "t_pause_ls1": 0.0,
        "enable_ls1": True,
        "t_s0102_ls": 0.0,
        "t_s0202_ls": 0.0,
        "t_ls0102": 0.0,
        "t_ls0202": 0.0,
        "t_kon_ls2": 0.0,
        "t_pause_ls2": 0.0,
        "enable_ls2": True,
        "t_s0104_ls": 0.0,
        "t_s0204_ls": 0.0,
        "t_ls0104": 0.0,
        "t_ls0204": 0.0,
        "t_kon_ls4": 0.0,
        "t_pause_ls4": 0.0,
        "enable_ls4": True,
        "t_s0109_ls": 0.0,
        "t_s0209_ls": 0.0,
        "t_ls0109": 0.0,
        "t_ls0209": 0.0,
        "t_kon_ls9": 0.0,
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

    steps = [
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 15, "Sw1": 15, "Sw5": 15},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 15, "Sw1": 15, "Sw5": 15},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states={"10-12SP": 3, "1P": 3, "1-7SP": 3},
            switch_states={"Sw10": 9, "Sw1": 3, "Sw5": 3},
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
            f"variant={st.variant}, lz={st.lz_state}, flags={st.flags}, "
            f"prev={st.effective_prev_rc}, next={st.effective_next_rc}"
        )

    # Вариант 1 не должен формироваться
    assert not any("llz_v1_open" in s.flags for s in timeline), "В1 не должен открываться"
    assert not any("llz_v1" in s.flags and s.variant == 1 for s in timeline), "variant=1 недопустим"
    assert not any("llz_v1_closed" in s.flags for s in timeline), "В1 не должен закрываться"

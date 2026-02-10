import pytest
from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p, TimelineStep
from engine.types_1p import ScenarioStep

@pytest.fixture(scope="session")
def station():
    return get_station_model_1p()

def _build_steps_v3_from_json() -> list[ScenarioStep]:
    switch_states = {"Sw10": 3, "Sw1": 3, "Sw5": 3}
    mu = {"10-12SP": 3, "1P": 3, "1-7SP": 3}
    auto_actions = {"NAS": 4, "CHAS": 4}
    signal_states = {"Ч1": 0, "НМ1": 0, "ЧМ1": 0, "М1": 0}

    # Ровно как в JSON
    rc_seq = [
        (6, 3, 6),
        (6, 3, 6),
        (6, 3, 6),
        (6, 6, 6),
        (6, 6, 6),
        (6, 6, 6),
        (6, 3, 6),
        (6, 3, 6),
        (6, 3, 6),
        (6, 3, 6),
        (6, 3, 6),
        (6, 3, 6),
    ]

    steps: list[ScenarioStep] = []
    for rc_1012, rc_1p, rc_17 in rc_seq:
        steps.append(
            ScenarioStep(
                t=1.0,
                rc_states={"10-12SP": rc_1012, "1P": rc_1p, "1-7SP": rc_17},
                switch_states=dict(switch_states),
                modes={},
                mu=dict(mu),
                dispatcher_control_state=4,
                auto_actions=dict(auto_actions),
                signal_states=dict(signal_states),
            )
        )
    return steps

def test_variant3_from_json_exact(station):
    opts = {
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
        "enable_v2": False,   # как в JSON: v2 выключен
        "t_s0103": 3.0,
        "t_s0203": 3.0,
        "t_lz03": 3.0,
        "t_kon_v3": 3.0,      # исправь t_kон_v3 -> t_kon_v3
        "t_pause_v3": 0.0,
        "enable_v3": True,
        "enable_v12": False,
        "t_s0108": 3.0,
        "t_s0208": 3.0,
        "t_lz08": 3.0,
        "t_kon_v8": 3.0,
        "t_pause_v8": 0.0,
        "enable_v8": True,
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
        "t_mu": 15.0,
        "t_recent_ls": 30.0,
        "t_min_maneuver_v8": 600.0,
    }

    steps = _build_steps_v3_from_json()

    timeline: list[TimelineStep] = simulate_1p(
        station=station,
        scenario_steps=steps,
        dt=1.0,
        options=opts,
    )

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("llz_v3_open" in s.flags and s.variant == 3 for s in timeline), "Нет открытия v3"
    assert any("llz_v3" in s.flags and s.variant == 3 for s in timeline), "Нет активного v3"
    assert any("llz_v3_closed" in s.flags for s in timeline), "Нет закрытия v3"

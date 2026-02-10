import pytest

from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p, TimelineStep
from engine.types_1p import ScenarioStep
from engine.detectors_runner_1p import DetectorsState  # если нужно дебажить
from engine import detectors_runner_1p


@pytest.fixture(scope="session")
def station():
    return get_station_model_1p()


def test_paths():
    import engine.simulate_1p as sim_module
    import engine.detectors_runner_1p as det_module
    from engine.variants.variant8_1p import Variant8Detector

    print("simulate_1p file:", sim_module.__file__)
    print("detectors_runner_1p file:", det_module.__file__)
    print("Variant8Detector module:", Variant8Detector.__module__)
    assert True


# === JSON → options ===
OPTIONS_V8_JSON: dict = {
    "t_s0101": 3,
    "t_lz01": 3,
    "t_kon_v1": 3,
    "t_pause_v1": 0,
    "enable_v1": True,
    "t_s0102": 3,
    "t_s0202": 3,
    "t_lz02": 3,
    "t_kon_v2": 3,
    "t_pause_v2": 0,
    "enable_v2": True,
    "t_s0103": 3,
    "t_s0203": 3,
    "t_lz03": 3,
    "t_kon_v3": 3,
    "t_pause_v3": 0,
    "enable_v3": True,
    "t_s0401": 3,
    "t_lz04": 3,
    "t_kon_v4": 3,
    "t_pause_v4": 0,
    "enable_v4": True,
    "t_s05": 1,
    "t_lz05": 1,
    "t_pk": 0,
    "t_kon_v5": 3,
    "t_pause_v5": 0,
    "enable_v5": False,
    "t_s06": 10,
    "t_lz06": 600,
    "t_kon_v6": 10,
    "t_pause_v6": 0,
    "enable_v6": False,
    "t_s07": 3,
    "t_lz07": 3,
    "t_kон_v7": 3,  # как в JSON
    "t_pause_v7": 0,
    "enable_v7": True,
    "t_s0108": 3,
    "t_s0208": 3,
    "t_lz08": 3,
    "t_kon_v8": 3,
    "t_pause_v8": 0,
    "enable_v8": True,
    "t_s0109": 3,
    "t_lz09": 3,
    "t_kon_v9": 3,
    "t_pause_v9": 0,
    "enable_v9": True,
    "t_s0110": 3,
    "t_s0210": 3,
    "t_s0310": 3,
    "t_lz10": 3,
    "t_kon_v10": 3,
    "t_pause_v10": 0,
    "enable_v10": True,
    "t_s11": 3,
    "t_lz11": 3,
    "t_kon_v11": 3,
    "t_pause_v11": 0,
    "enable_v11": True,
    "t_s0112": 3,
    "t_s0212": 3,
    "t_lz12": 3,
    "t_kon_v12": 3,
    "t_pause_v12": 0,
    "enable_v12": True,
    "t_s0113": 10,
    "t_s0213": 10,
    "t_lz13": 10,
    "t_kon_v13": 10,
    "t_pause_v13": 0,
    "enable_v13": True,
    "t_c0101_ls": 3,
    "t_ls01": 3,
    "t_kon_ls1": 3,
    "t_pause_ls1": 0,
    "enable_ls1": True,
    "t_s0102_ls": 3,
    "t_s0202_ls": 3,
    "t_ls0102": 2,
    "t_ls0202": 10,
    "t_kon_ls2": 3,
    "t_pause_ls2": 0,
    "enable_ls2": True,
    "t_s0104_ls": 3,
    "t_s0204_ls": 3,
    "t_ls0104": 3,
    "t_ls0204": 10,
    "t_kon_ls4": 3,
    "t_pause_ls4": 0,
    "enable_ls4": True,
    "t_s0109_ls": 2,
    "t_s0209_ls": 2,
    "t_ls0109": 1,
    "t_ls0209": 3,
    "t_kon_ls9": 3,
    "t_pause_ls9": 0,
    "enable_ls9": True,
    "t_mu": 15,
    "t_recent_ls": 30,
    "t_min_maneuver_v8": 600,
    "enable_lz_exc_mu": True,
    "enable_lz_exc_recent_ls": True,
    "enable_lz_exc_dsp": True,
    "t_ls_mu": 15,
    "t_ls_after_lz": 30,
    "t_ls_dsp": 600,
    "enable_ls_exc_mu": True,
    "enable_ls_exc_after_lz": True,
    "enable_ls_exc_dsp": True,
}


STEPS_V8_JSON = [
    {"t": 1, "rc_states": {"10-12SP": 6, "1P": 6, "1-7SP": 3}},
    {"t": 1, "rc_states": {"10-12SP": 6, "1P": 6, "1-7SP": 3}},
    {"t": 1, "rc_states": {"10-12SP": 6, "1P": 6, "1-7SP": 6}},
    {"t": 1, "rc_states": {"10-12SP": 6, "1P": 6, "1-7SP": 6}},
    {"t": 1, "rc_states": {"10-12SP": 3, "1P": 6, "1-7SP": 6}},
    {"t": 1, "rc_states": {"10-12SP": 3, "1P": 6, "1-7SP": 6}},
    {"t": 1, "rc_states": {"10-12SP": 3, "1P": 6, "1-7SP": 6}},
    {"t": 1, "rc_states": {"10-12SP": 3, "1P": 6, "1-7SP": 3}},
    {"t": 1, "rc_states": {"10-12SP": 3, "1P": 6, "1-7SP": 3}},
    {"t": 1, "rc_states": {"10-12SP": 3, "1P": 6, "1-7SP": 3}},
    {"t": 1, "rc_states": {"10-12SP": 3, "1P": 3, "1-7SP": 3}},
    {"t": 1, "rc_states": {"10-12SP": 3, "1P": 3, "1-7SP": 3}},
    {"t": 1, "rc_states": {"10-12SP": 3, "1P": 3, "1-7SP": 3}},
]


def _build_steps_from_json() -> list[ScenarioStep]:
    switch_states = {"Sw10": 3, "Sw1": 3, "Sw5": 3}
    mu = {"10-12SP": 3, "1P": 3, "1-7SP": 3}
    auto_actions = {"NAS": 4, "CHAS": 4}
    signal_states = {"Ч1": 0, "НМ1": 0, "ЧМ1": 0, "М1": 0}

    steps: list[ScenarioStep] = []
    for s in STEPS_V8_JSON:
        steps.append(
            ScenarioStep(
                t=float(s["t"]),
                rc_states=dict(s["rc_states"]),
                switch_states=dict(switch_states),
                modes={},
                mu=dict(mu),
                dispatcher_control_state=4,
                auto_actions=dict(auto_actions),
                signal_states=dict(signal_states),
            )
        )
    return steps


def test_variant8_from_json_exact(station):
    options = dict(OPTIONS_V8_JSON)
    steps = _build_steps_from_json()

    timeline: list[TimelineStep] = simulate_1p(
        station=station,
        scenario_steps=steps,
        dt=1.0,
        options=options,
    )

    # временный вывод для сравнения с фронтом
    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # пока только проверяем, что вообще есть LZ по ходу сценария
    assert any(s.lz_state for s in timeline), "По сценарию ни разу не включилась LZ"

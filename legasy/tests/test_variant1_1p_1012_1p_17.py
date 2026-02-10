import pytest
from tests.utils import has_flag
from engine.station_visochino_1p import (
    get_station_model_1p,
    get_station_model_1012_ctrl,
    get_station_model_17_ctrl,
)
from engine.simulate_1p import simulate_1p
from engine.types_1p import ScenarioStep


OPTS_V1 = {
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


def _build_steps_for_v1(ctrl_rc_id: str) -> list[ScenarioStep]:
    """
    Строим один и тот же сценарий:
    1) все РЦ свободны
    2) ctrl_rc занята
    3) снова свободна.
    Остальные РЦ остаются в состоянии 3.
    """
    base_rc = {"10-12SP": 3, "1P": 3, "1-7SP": 3}

    def rc_state(ctrl_state: int) -> dict[str, int]:
        d = dict(base_rc)
        d[ctrl_rc_id] = ctrl_state
        return d

    return [
        ScenarioStep(
            t=1.0,
            rc_states=rc_state(3),
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states=rc_state(3),
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states=rc_state(6),
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states=rc_state(6),
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states=rc_state(3),
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states=rc_state(3),
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
        ScenarioStep(
            t=1.0,
            rc_states=rc_state(3),
            switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
            modes={},
        ),
    ]


@pytest.mark.parametrize(
    "factory, ctrl_rc_id",
    [
        (get_station_model_1p, "1P"),
        (get_station_model_1012_ctrl, "10-12SP"),
        (get_station_model_17_ctrl, "1-7SP"),
    ],
)
def test_variant1_all_ctrl_rc(factory, ctrl_rc_id):
    station = factory()
    assert station.ctrl_rc_id == ctrl_rc_id

    steps = _build_steps_for_v1(ctrl_rc_id)
    timeline = simulate_1p(station, steps, dt=1.0, options=OPTS_V1)

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.variant}, lz={st.lz_state}, flags={st.flags}"
        )

    flags = [f for st in timeline for f in st.flags]

    # sanity: нет явных ошибок ЛЗ
    assert "false_lz" not in flags
    assert "no_lz_when_occupied" not in flags

    # старые флаги (для совместимости с фронтом/старым форматом)
    assert has_flag(flags, "llz_v1_open"), f"Нет llz_v1_open для {ctrl_rc_id}"
    assert has_flag(flags, "llz_v1"), f"Нет llz_v1 для {ctrl_rc_id}"
    assert has_flag(flags, "llz_v1_closed"), f"Нет llz_v1_closed для {ctrl_rc_id}"

    # новые флаги с явной РЦ
    assert has_flag(flags, "llz_v1_open", rc=ctrl_rc_id), f"Нет llz_v1_open:rc={ctrl_rc_id}"
    assert has_flag(flags, "llz_v1", rc=ctrl_rc_id), f"Нет llz_v1:rc={ctrl_rc_id}"
    assert has_flag(flags, "llz_v1_closed", rc=ctrl_rc_id), f"Нет llz_v1_closed:rc={ctrl_rc_id}"

    # хотя бы на одном шаге variant == 1 и есть llz_v1 по этой РЦ
    assert any(
        st.variant == 1 and has_flag(st.flags, "llz_v1", rc=ctrl_rc_id)
        for st in timeline
    ), f"Нет variant=1 с llz_v1 по {ctrl_rc_id}"

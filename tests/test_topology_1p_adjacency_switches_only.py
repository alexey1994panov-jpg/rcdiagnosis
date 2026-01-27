import pytest

from engine.topology_1p import compute_local_adjacency
from engine.station_visochino_1p import get_station_model_1p
from engine.types_1p import ScenarioStep

def _step(rc_states=None, switch_states=None, t=0.0):
    return ScenarioStep(
        t,
        rc_states or {},
        switch_states or {},
        {},  # modes
    )



SW_PLUS = 3      # ПК: любой код 3–8
SW_NOT_PLUS = 9  # !=ПК: берём 9 как представитель МК


# --- ctrl_rc_id = "1P" ---


@pytest.mark.parametrize(
    "case_id, sw10, sw1, sw5, expect_prev, expect_next",
    [
        ("1", SW_PLUS, SW_PLUS, SW_PLUS, True, True),
        ("2", SW_PLUS, SW_PLUS, SW_NOT_PLUS, True, False),
        ("3", SW_PLUS, SW_NOT_PLUS, SW_NOT_PLUS, True, False),
        ("4", SW_NOT_PLUS, SW_NOT_PLUS, SW_NOT_PLUS, False, False),
        ("5", SW_NOT_PLUS, SW_PLUS, SW_PLUS, False, True),
        ("6", SW_NOT_PLUS, SW_NOT_PLUS, SW_PLUS, False, False),
    ],
)
def test_adjacency_1p_by_switches_only(case_id, sw10, sw1, sw5, expect_prev, expect_next):
    station = get_station_model_1p()

    step = _step(
        rc_states={
            "10-12SP": 3,
            "1P": 4,
            "1-7SP": 3,
        },
        switch_states={
            "Sw10": sw10,
            "Sw1": sw1,
            "Sw5": sw5,
        },
    )

    adj = compute_local_adjacency(station, step, ctrl_rc_id="1P")

    assert adj.prev_rc_id == "10-12SP"
    assert adj.next_rc_id == "1-7SP"

    if expect_prev:
        assert adj.prev_state == 3, f"case {case_id}: ожидаем связь с 10-12SP"
        assert adj.prev_nc is False
    else:
        assert adj.prev_state == 0, f"case {case_id}: связь с 10-12SP не должна определяться"
        assert adj.prev_nc is True

    if expect_next:
        assert adj.next_state == 3, f"case {case_id}: ожидаем связь с 1-7SP"
        assert adj.next_nc is False
    else:
        assert adj.next_state == 0, f"case {case_id}: связь с 1-7SP не должна определяться"
        assert adj.next_nc is True


# --- ctrl_rc_id = "10-12SP" ---


@pytest.mark.parametrize(
    "case_id, sw10, expect_next",
    [
        ("1", SW_PLUS, True),
        ("2", SW_NOT_PLUS, False),
    ],
)
def test_adjacency_1012_by_switches_only(case_id, sw10, expect_next):
    station = get_station_model_1p()

    step = _step(
        rc_states={
            "10-12SP": 3,
            "1P": 3,
        },
        switch_states={
            "Sw10": sw10,
        },
    )

    adj = compute_local_adjacency(station, step, ctrl_rc_id="10-12SP")

    assert adj.prev_rc_id == "1AP"
    assert adj.prev_state == 0
    assert adj.prev_nc is True

    assert adj.next_rc_id == "1P"

    if expect_next:
        assert adj.next_state == 3, f"case {case_id}: ожидаем связь с 1P"
        assert adj.next_nc is False
    else:
        assert adj.next_state == 0, f"case {case_id}: связь с 1P не должна определяться"
        assert adj.next_nc is True


# --- ctrl_rc_id = "1-7SP" ---


@pytest.mark.parametrize(
    "case_id, sw1, sw5, expect_next",
    [
        ("1", SW_PLUS, SW_PLUS, True),
        ("2", SW_PLUS, SW_NOT_PLUS, False),
        ("3", SW_NOT_PLUS, SW_PLUS, False),
        ("4", SW_NOT_PLUS, SW_NOT_PLUS, False),
    ],
)
def test_adjacency_17_by_switches_only(case_id, sw1, sw5, expect_next):
    station = get_station_model_1p()

    step = _step(
        rc_states={
            "1-7SP": 4,
            "1P": 3,
        },
        switch_states={
            "Sw1": sw1,
            "Sw5": sw5,
        },
    )

    adj = compute_local_adjacency(station, step, ctrl_rc_id="1-7SP")

    assert adj.prev_rc_id == "NP"
    assert adj.prev_state == 0
    assert adj.prev_nc is True

    assert adj.next_rc_id == "1P"

    if expect_next:
        assert adj.next_state == 3, f"case {case_id}: ожидаем связь с 1P"
        assert adj.next_nc is False
    else:
        assert adj.next_state == 0, f"case {case_id}: связь с 1P не должна определяться"
        assert adj.next_nc is True

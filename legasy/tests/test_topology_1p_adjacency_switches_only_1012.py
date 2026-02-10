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


# ...existing tests...


@pytest.mark.parametrize(
    "case_id, sw10, expect_next_state, expect_next_nc",
    [
        ("plus", SW_PLUS, 3, False),
        ("minus", SW_NOT_PLUS, 0, True),
    ],
)
def test_adjacency_1012_prev_1ap_always_visible(
    case_id, sw10, expect_next_state, expect_next_nc
):
    """
    ctrl=10-12SP:
    - prev_rc_id всегда 1AP, prev_state берётся из rc_states["1AP"],
      prev_nc определяется только через rc_no_control(prev_state) и
      не зависит от положения Sw10.
    - next_rc_id всегда 1P, а видимость next зависит от Sw10.
    """
    station = get_station_model_1p()

    step = _step(
        rc_states={
            "1AP": 3,        # 1AP контролируется и свободна
            "10-12SP": 3,
            "1P": 3,
        },
        switch_states={
            "Sw10": sw10,
        },
    )

    adj = compute_local_adjacency(station, step, ctrl_rc_id="10-12SP")

    # prev: всегда 1AP, независимо от Sw10
    assert adj.prev_rc_id == "1AP", f"{case_id}: prev_rc_id должен быть 1AP"
    assert adj.prev_state == 3, f"{case_id}: prev_state должен быть 3 (из 1AP)"
    assert adj.prev_nc is False, f"{case_id}: prev_nc должен быть False (1AP контролируется)"

    # next: всегда 1P, но видимость зависит от Sw10
    assert adj.next_rc_id == "1P", f"{case_id}: next_rc_id должен быть 1P"
    assert (
        adj.next_state == expect_next_state
    ), f"{case_id}: next_state должен быть {expect_next_state}"
    assert (
        adj.next_nc is expect_next_nc
    ), f"{case_id}: next_nc должен быть {expect_next_nc}"

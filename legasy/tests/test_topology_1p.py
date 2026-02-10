import pytest
from tests.utils import has_flag

from engine.station_visochino_1p import get_station_model_1p
from engine.topology_1p import RC_TOPOLOGY_1P, SW_TOPOLOGY_1P, compute_local_adjacency
from engine.types_1p import ScenarioStep


def test_station_topology_consistency():
    station = get_station_model_1p()

    # Все RC из топологии должны присутствовать в модели станции
    for rc_id in RC_TOPOLOGY_1P.keys():
        assert rc_id in station.rc_ids, f"RC {rc_id} missing in station.rc_ids"

    # Все стрелки из SW_TOPOLOGY_1P должны быть в station.switch_ids
    for sw_id in SW_TOPOLOGY_1P.keys():
        assert sw_id in station.switch_ids, f"Switch {sw_id} missing in station.switch_ids"

    # Сигналы, используемые в детекторах — должны быть в station.signal_ids
    required_signals = ["Ч1", "НМ1", "ЧМ1", "М1", "M1"]
    for sig in required_signals:
        assert sig in (station.signal_ids or []), f"Signal {sig} missing in station.signal_ids"

    # Для этих сигналов, prev/next либо None, либо присутствуют в station.rc_ids
    for sig in required_signals:
        prev = (station.signal_prev_by_id or {}).get(sig)
        nxt = (station.signal_next_by_id or {}).get(sig)
        if prev is not None:
            assert prev in station.rc_ids, f"Signal {sig} prev {prev} not in station.rc_ids"
        if nxt is not None:
            assert nxt in station.rc_ids, f"Signal {sig} next {nxt} not in station.rc_ids"


def make_step(rc_states=None, switch_states=None):
    return ScenarioStep(
        t=0.0,
        rc_states=rc_states or {},
        switch_states=switch_states or {},
        modes={},
    )


@pytest.mark.parametrize("ctrl_rc", ["10-12SP", "1P", "1-7SP"])
def test_basic_adjacency_1p_section(ctrl_rc):
    station = get_station_model_1p()

    # baseline rc states: mark all RCs as 'free' (code 3)
    baseline_rc_states = {rc: 3 for rc in station.rc_ids}

    # 1) All switches in plus (3) -> adjacency should be active between 10-12SP <-> 1P <-> 1-7SP
    sw_plus = {"Sw10": 3, "Sw1": 3, "Sw5": 3}
    step_all_plus = make_step(rc_states=baseline_rc_states, switch_states=sw_plus)
    adj = compute_local_adjacency(station, step_all_plus, ctrl_rc)

    if ctrl_rc == "1P":
        assert adj.prev_state != 0, "with all plus Sw10 expected prev active for 1P"
        assert adj.next_state != 0, "with all plus Sw1/Sw5 expected next active for 1P"
    elif ctrl_rc == "10-12SP":
        # 10-12SP next -> 1P should be active
        assert adj.next_state != 0
    elif ctrl_rc == "1-7SP":
        # 1-7SP prev -> NP (mapped) or 1P depends on topology; ensure prev is active when switches plus
        assert adj.prev_state != 0

    # 2) Sw10 in minus -> 1P should lose prev (connection to 10-12SP)
    sw10_minus = {"Sw10": 9, "Sw1": 3, "Sw5": 3}
    step_sw10_minus = make_step(rc_states=baseline_rc_states, switch_states=sw10_minus)
    adj2 = compute_local_adjacency(station, step_sw10_minus, "1P")
    assert adj2.prev_state == 0, "Sw10 minus should break prev adjacency for 1P"

    # 3) Sw1 in minus -> 1P should lose next
    sw1_minus = {"Sw10": 3, "Sw1": 9, "Sw5": 3}
    step_sw1_minus = make_step(rc_states=baseline_rc_states, switch_states=sw1_minus)
    adj3 = compute_local_adjacency(station, step_sw1_minus, "1P")
    assert adj3.next_state == 0, "Sw1 minus should break next adjacency for 1P"

    # 4) Sw5 in minus -> 1P should lose next
    sw5_minus = {"Sw10": 3, "Sw1": 3, "Sw5": 9}
    step_sw5_minus = make_step(rc_states=baseline_rc_states, switch_states=sw5_minus)
    adj4 = compute_local_adjacency(station, step_sw5_minus, "1P")
    assert adj4.next_state == 0, "Sw5 minus should break next adjacency for 1P"

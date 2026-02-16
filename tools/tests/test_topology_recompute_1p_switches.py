# -*- coding: utf-8 -*-
from station.station_model import load_station_from_config
from core.topology_manager import UniversalTopologyManager


def test_topology_recomputes_neighbors_for_1p_when_switch_changes():
    model = load_station_from_config()
    topo = UniversalTopologyManager(model, t_pk=30.0)

    # 1P (108): expected neighbors with plus positions.
    sw_plus = {
        "110": 3,  # Sw10 plus
        "88": 3,   # Sw5 plus
        "79": 3,
        "55": 3,
        "150": 3,
        "72": 3,
        "74": 3,
        "73": 3,
    }
    prev_plus, next_plus = topo.get_active_neighbors("108", sw_plus, dt=1.0)
    assert prev_plus == "59"
    assert next_plus == "83"

    # Move key switches to minus -> in current model 1P gets disconnected.
    sw_minus = dict(sw_plus)
    sw_minus["110"] = 9
    sw_minus["88"] = 9
    prev_minus, next_minus = topo.get_active_neighbors("108", sw_minus, dt=1.0)
    assert prev_minus == ""
    assert next_minus == ""

    # Back to plus -> neighbors must be restored (recomputed again).
    prev_back, next_back = topo.get_active_neighbors("108", sw_plus, dt=1.0)
    assert prev_back == "59"
    assert next_back == "83"

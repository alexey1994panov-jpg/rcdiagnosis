from api_contract.api import get_metadata, run_simulation


def test_api_run_simulation_single_rc_contract():
    payload = {
        "t_pk": 30.0,
        "ctrl_rc_id": "108",
        "detectors_config": {
            "ctrl_rc_id": "108",
            "prev_rc_name": "59",
            "next_rc_name": "83",
            "enable_lz10": True,
            "ts01_lz10": 1.0,
            "ts02_lz10": 1.0,
            "ts03_lz10": 1.0,
            "tlz_lz10": 1.0,
            "tkon_lz10": 2.0,
            "sig_lz10_to_next": "114",
        },
        "scenario": [
            {
                "t": 2.0,
                "rc_states": {"59": 3, "108": 6, "83": 3},
                "switch_states": {"110": 3, "88": 3},
                "signal_states": {"114": 3},
                "modes": {},
            },
            {
                "t": 2.0,
                "rc_states": {"59": 3, "108": 6, "83": 6},
                "switch_states": {"110": 3, "88": 3},
                "signal_states": {"114": 3},
                "modes": {},
            },
            {
                "t": 2.0,
                "rc_states": {"59": 3, "108": 6, "83": 6},
                "switch_states": {"110": 3, "88": 3},
                "signal_states": {"114": 15},
                "modes": {},
            },
            {
                "t": 2.0,
                "rc_states": {"59": 3, "108": 6, "83": 3},
                "switch_states": {"110": 3, "88": 3},
                "signal_states": {"114": 15},
                "modes": {},
            },
        ],
    }

    resp = run_simulation(payload)

    assert resp["mode"] == "single"
    assert resp["ctrl_rc_ids"] == ["108"]
    assert len(resp["timeline"]) == 4
    assert len(resp["frames"]) == 4
    assert any("llz_v10_open" in step["flags"] for step in resp["timeline"])


def test_api_metadata_contract():
    meta = get_metadata()
    assert "variants" in meta
    assert "flags" in meta
    assert "masks" in meta
    assert meta["variants"]["10"] == "LZ10"
    assert "llz_v10_open" in meta["flags"]



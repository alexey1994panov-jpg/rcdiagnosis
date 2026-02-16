# -*- coding: utf-8 -*-
import json
from pathlib import Path

from exceptions.exceptions_objects_registry import ExceptionsObjectsRegistry


def test_registry_load_and_evaluate():
    cfg = {
        "version": 1,
        "objects": [
            {
                "id": "mu_1",
                "kind": "MU",
                "target_rc_ids": ["108"],
                "active_states": [6],
            },
            {
                "id": "dsp_1",
                "kind": "DSP",
                "target_rc_ids": [],
                "active_states": [6],
            },
        ],
    }
    p = Path("tools/_test_exceptions_objects_registry.json")
    p.write_text(json.dumps(cfg), encoding="utf-8")

    try:
        reg = ExceptionsObjectsRegistry.load(str(p))
        assert len(reg.objects) == 2

        r1 = reg.evaluate({"mu_1": 6, "dsp_1": 6}, "108")
        assert r1["mu_active"] is True
        assert r1["dsp_active"] is True

        r2 = reg.evaluate({"mu_1": 6, "dsp_1": 3}, "59")
        assert r2["mu_active"] is False
        assert r2["dsp_active"] is False
    finally:
        p.unlink(missing_ok=True)


def test_registry_default_active_state_is_6():
    cfg = {
        "version": 1,
        "objects": [
            {
                "id": "mu_2",
                "kind": "MU",
                "target_rc_ids": ["108"]
            }
        ],
    }
    p = Path("tools/_test_exceptions_objects_registry_default.json")
    p.write_text(json.dumps(cfg), encoding="utf-8")
    try:
        reg = ExceptionsObjectsRegistry.load(str(p))
        assert reg.evaluate({"mu_2": 6}, "108")["mu_active"] is True
        assert reg.evaluate({"mu_2": 3}, "108")["mu_active"] is False
    finally:
        p.unlink(missing_ok=True)


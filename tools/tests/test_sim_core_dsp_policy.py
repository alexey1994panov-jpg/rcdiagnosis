# -*- coding: utf-8 -*-
import json
from pathlib import Path

from core.detectors_engine import DetectorsConfig
from core.sim_core import ScenarioStep, SimulationConfig, SimulationContext


def test_dsp_policy_detector_global_blocks_lz8_open():
    policy_path = Path("tools/_test_dsp_policy.json")
    cfg = {
        "version": 1,
        "dsp_policy": {
            "default": {
                "enabled": True,
                "mode": "detector_global",
                "count_scope": "ctrl_occupied",
                "variants": [8],
                "t_maneuver": 2.0,
            }
        },
        "objects": [
            {
                "id": "dsp_obj",
                "kind": "DSP",
                "target_rc_ids": [],
                "active_states": [6],
            }
        ],
    }
    policy_path.write_text(json.dumps(cfg), encoding="utf-8")
    try:
        det_cfg = DetectorsConfig(
            ctrl_rc_id="108",
            prev_rc_name="59",
            ctrl_rc_name="108",
            next_rc_name="83",
            enable_lz8=True,
            ts01_lz8=1.0,
            ts02_lz8=1.0,
            tlz_lz8=1.0,
            tkon_lz8=1.0,
        )
        sim_cfg = SimulationConfig(
            t_pk=30.0,
            detectors_config=det_cfg,
            exceptions_objects_path=str(policy_path),
        )
        scenario = [
            ScenarioStep(
                t=1.0,
                rc_states={"59": 6, "108": 6, "83": 3},
                switch_states={"87": 3, "88": 3, "110": 3},
                signal_states={},
                modes={},
                auto_actions={"nas": 0},
                indicator_states={"dsp_obj": 6},
            ),
            ScenarioStep(
                t=1.0,
                rc_states={"59": 6, "108": 6, "83": 6},
                switch_states={"87": 3, "88": 3, "110": 3},
                signal_states={},
                modes={},
                auto_actions={"nas": 0},
                indicator_states={"dsp_obj": 6},
            ),
            ScenarioStep(
                t=1.0,
                rc_states={"59": 3, "108": 6, "83": 3},
                switch_states={"87": 3, "88": 3, "110": 3},
                signal_states={},
                modes={},
                auto_actions={"nas": 0},
                indicator_states={"dsp_obj": 6},
            ),
        ]

        ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
        timeline = ctx.run()

        assert not any("llz_v8_open" in s.flags for s in timeline)
        assert any("lz_suppressed:dsp_detector_gate" in s.flags for s in timeline)
    finally:
        policy_path.unlink(missing_ok=True)


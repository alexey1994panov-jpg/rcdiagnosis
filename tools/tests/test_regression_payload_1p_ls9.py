# -*- coding: utf-8 -*-
"""
Regression reproduction for user payload:
- ctrl RC 1P (id=108)
- first second neighbors are connected
- then switches are translated so topology disconnects neighbors
- result: LS9 opens, LZ1 does not open.
"""

from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def _build_user_like_context() -> SimulationContext:
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        ts01_lz1=3.0,
        tlz_lz1=3.0,
        tkon_lz1=3.0,
        enable_lz1=True,
        ts01_lz2=3.0,
        ts02_lz2=3.0,
        tlz_lz2=3.0,
        tkon_lz2=3.0,
        enable_lz2=True,
        ts01_lz3=3.0,
        ts02_lz3=3.0,
        tlz_lz3=3.0,
        tkon_lz3=3.0,
        enable_lz3=True,
        ts01_lz8=3.0,
        ts02_lz8=3.0,
        tlz_lz8=3.0,
        tkon_lz8=3.0,
        enable_lz8=True,
        ts01_lz9=3.0,
        tlz_lz9=3.0,
        tkon_lz9=3.0,
        enable_lz9=True,
        ts01_lz10=3.0,
        ts02_lz10=3.0,
        ts03_lz10=3.0,
        tlz_lz10=3.0,
        tkon_lz10=3.0,
        enable_lz10=True,
        ts01_lz11=3.0,
        tlz_lz11=3.0,
        tkon_lz11=3.0,
        enable_lz11=True,
        sig_lz11_a="",
        sig_lz11_b="",
        ts01_lz12=3.0,
        tlz_lz12=3.0,
        tkon_lz12=3.0,
        enable_lz12=True,
        ts01_lz13=3.0,
        ts02_lz13=3.0,
        tlz_lz13=3.0,
        tkon_lz13=3.0,
        enable_lz13=True,
        enable_ls1=True,
        enable_ls2=True,
        enable_ls4=True,
        enable_ls5=True,
        enable_ls6=True,
        sig_ls6_prev="",
        enable_ls9=True,
        ts01_ls1=0.0,
        tlz_ls1=0.0,
        tkon_ls1=0.0,
        ts01_ls2=0.0,
        ts02_ls2=0.0,
        tlz_ls2=0.0,
        tkon_ls2=0.0,
        ts01_ls4=0.0,
        tlz01_ls4=0.0,
        tlz02_ls4=0.0,
        tkon_ls4=0.0,
        ts01_ls5=0.0,
        tlz_ls5=0.0,
        tkon_ls5=0.0,
        ts01_ls6=0.0,
        tlz_ls6=0.0,
        tkon_ls6=0.0,
        ts01_ls9=0.0,
        tlz_ls9=0.0,
        tkon_ls9=0.0,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    base_rc = {
        "83": 3, "59": 3, "94": 3, "47": 3, "108": 3, "56": 3, "62": 3, "90": 3,
        "104": 3, "86": 3, "65": 3, "58": 3, "98": 3, "81": 3, "57": 3, "40": 3,
    }
    base_sig = {
        "112": 3, "37": 3, "39": 3, "38": 3, "78": 3, "46": 3, "61": 3, "64": 3,
        "100": 3, "107": 3, "89": 3, "103": 3, "42": 3, "114": 3, "92": 3, "117": 3,
        "53": 3, "50": 3, "68": 3, "75": 3,
    }

    steps = []
    # 0..3 sec occupied
    for i in range(4):
        rc = dict(base_rc)
        rc["108"] = 6
        sw = {
            "79": 3 if i == 0 else 9,  # Sw1
            "55": 3,                   # Sw2
            "150": 3,                  # Sw3
            "72": 3,                   # Sw4
            "88": 3 if i == 0 else 9,  # Sw5
            "74": 3,                   # Sw6
            "110": 3 if i == 0 else 9, # Sw10
            "73": 3,                   # Sw16
        }
        steps.append(ScenarioStep(t=1.0, rc_states=rc, switch_states=sw, signal_states=dict(base_sig), modes={}))

    # 4..6 sec free
    for _ in range(3):
        rc = dict(base_rc)
        rc["108"] = 3
        sw = {"79": 9, "55": 3, "150": 3, "72": 3, "88": 9, "74": 3, "110": 9, "73": 3}
        steps.append(ScenarioStep(t=1.0, rc_states=rc, switch_states=sw, signal_states=dict(base_sig), modes={}))

    # 7..9 sec occupied
    for _ in range(3):
        rc = dict(base_rc)
        rc["108"] = 6
        sw = {"79": 9, "55": 3, "150": 3, "72": 3, "88": 9, "74": 3, "110": 9, "73": 3}
        steps.append(ScenarioStep(t=1.0, rc_states=rc, switch_states=sw, signal_states=dict(base_sig), modes={}))

    return SimulationContext(config=sim_cfg, scenario=steps, ctrl_rc_id="108")


def test_reproduce_payload_behavior_ls9_without_lz1():
    ctx = _build_user_like_context()
    timeline = ctx.run()

    # 10 intervals * 1 sec => timeline steps are t in [0..9]
    assert len(timeline) == 10
    assert timeline[-1].t == 9.0

    # After first switch translation, neighbors are disconnected for ctrl=108.
    assert timeline[1].effective_prev_rc is None
    assert timeline[1].effective_next_rc is None

    # In this payload LS9 opens, LZ1 does not.
    assert any("lls_9_open" in s.flags for s in timeline)
    assert not any("llz_v1_open" in s.flags for s in timeline)

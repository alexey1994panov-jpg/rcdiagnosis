# -*- coding: utf-8 -*-
"""
Regression for user scenario on ctrl=1-7СП (id=83):
- LZ2 opens when one neighbor is occupied.
- LZ2 closes by FREE_TIME of ctrl RC, not by neighbor state.
"""

from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep
from core.detectors_engine import DetectorsConfig


def _build_ctx(np_free_steps: int) -> SimulationContext:
    det_cfg = DetectorsConfig(
        ctrl_rc_id="83",          # 1-7СП
        prev_rc_name="108",       # 1П
        ctrl_rc_name="83",
        next_rc_name="81",        # НП
        ts01_lz2=3.0,
        ts02_lz2=3.0,
        tlz_lz2=3.0,
        tkon_lz2=3.0,
        enable_lz2=True,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    base_rc = {
        "83": 3, "108": 3, "81": 6,
        "59": 3, "94": 3, "47": 3, "56": 3, "62": 3, "90": 3,
        "104": 3, "86": 3, "65": 3, "58": 3, "98": 3, "57": 3, "40": 3,
    }
    sw = {"79": 3, "55": 3, "150": 3, "72": 3, "88": 3, "74": 3, "110": 3, "73": 3}

    steps = []
    # 0..2 sec: 001
    for _ in range(3):
        steps.append(ScenarioStep(t=1.0, rc_states=dict(base_rc), switch_states=dict(sw), signal_states={}, modes={}))

    # 3..5 sec: 011
    for _ in range(3):
        rc = dict(base_rc)
        rc["83"] = 6
        steps.append(ScenarioStep(t=1.0, rc_states=rc, switch_states=dict(sw), signal_states={}, modes={}))

    # 6..7 sec: 001
    for _ in range(2):
        steps.append(ScenarioStep(t=1.0, rc_states=dict(base_rc), switch_states=dict(sw), signal_states={}, modes={}))

    # neighbor (НП) becomes free; ctrl remains free
    for _ in range(np_free_steps):
        rc = dict(base_rc)
        rc["81"] = 3
        steps.append(ScenarioStep(t=1.0, rc_states=rc, switch_states=dict(sw), signal_states={}, modes={}))

    return SimulationContext(config=sim_cfg, scenario=steps, ctrl_rc_id="83")


def test_lz2_user_like_on_1_7sp_opens_but_not_closed_by_t10():
    """User-length scenario: open appears at t=8, close does not yet appear by t=10."""
    tl = _build_ctx(np_free_steps=3).run()

    assert any("llz_v2_open" in s.flags for s in tl)
    assert not any("llz_v2_closed" in s.flags for s in tl)

    opened_step = next(s for s in tl if "llz_v2_open" in s.flags)
    assert opened_step.t == 8.0
    assert opened_step.effective_prev_rc == "108"
    assert opened_step.effective_next_rc == "81"


def test_lz2_user_like_on_1_7sp_closes_after_extra_step():
    """With one extra second after open, FREE_TIME reaches tkon_lz2 and detector closes."""
    tl = _build_ctx(np_free_steps=4).run()

    assert any("llz_v2_open" in s.flags for s in tl)
    assert any("llz_v2_closed" in s.flags for s in tl)

    closed_step = next(s for s in tl if "llz_v2_closed" in s.flags)
    assert closed_step.t == 11.0

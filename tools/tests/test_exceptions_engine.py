# -*- coding: utf-8 -*-
from exceptions.exceptions_engine import ExceptionsConfig, apply_exceptions
from core.sim_core import ScenarioStep, TimelineStep


def _mk_scenario_step(
    t: float,
    rc_state: int,
    ctrl_rc_id: str = "108",
    mu_value: int = 0,
    dsp: int | None = None,
    nas: int | None = None,
):
    auto_actions = {}
    if nas is not None:
        auto_actions["nas"] = nas
    return ScenarioStep(
        t=t,
        rc_states={ctrl_rc_id: rc_state},
        switch_states={},
        signal_states={},
        modes={"dispatcher_control_state": dsp} if dsp is not None else {},
        mu={ctrl_rc_id: mu_value} if mu_value else {},
        dispatcher_control_state=dsp,
        auto_actions=auto_actions,
    )


def _mk_timeline_step(
    flags: list[str],
    lz_variant: int,
    lz_state: bool = True,
    step_duration: float = 1.0,
    ctrl_rc_id: str = "108",
):
    return TimelineStep(
        t=0.0,
        step_duration=step_duration,
        ctrl_rc_id=ctrl_rc_id,
        effective_prev_rc="59",
        effective_next_rc="83",
        rc_states={ctrl_rc_id: 6},
        switch_states={},
        signal_states={},
        modes={},
        lz_state=lz_state,
        lz_variant=lz_variant,
        flags=list(flags),
    )


def test_exceptions_noop_when_disabled():
    current = _mk_timeline_step(flags=["llz_v2_open"], lz_variant=2)
    scenario_history = [_mk_scenario_step(t=5.0, rc_state=6, mu_value=1)]
    out = apply_exceptions(
        ctrl_rc_id="108",
        current=current,
        scenario_history=scenario_history,
        timeline_history=[],
        cfg=ExceptionsConfig(),
    )
    assert "llz_v2_open" in out.flags
    assert out.lz_state is True
    assert out.lz_variant == 2


def test_lz_suppressed_by_local_mu():
    current = _mk_timeline_step(flags=["llz_v9_open"], lz_variant=9)
    scenario_history = [_mk_scenario_step(t=5.0, rc_state=6, mu_value=1)]
    out = apply_exceptions(
        ctrl_rc_id="108",
        current=current,
        scenario_history=scenario_history,
        timeline_history=[],
        cfg=ExceptionsConfig(enable_lz_exc_mu=True, t_mu=10.0),
    )
    assert not any(f.startswith("llz_v") for f in out.flags)
    assert "lz_suppressed:local_mu" in out.flags
    assert out.lz_state is False
    assert out.lz_variant == 0


def test_ls_suppressed_after_recent_lz():
    current = _mk_timeline_step(flags=["lls_1_open"], lz_variant=101)
    past = _mk_timeline_step(flags=["llz_v2_open"], lz_variant=2, step_duration=2.0)
    scenario_history = [_mk_scenario_step(t=2.0, rc_state=3)]
    out = apply_exceptions(
        ctrl_rc_id="108",
        current=current,
        scenario_history=scenario_history,
        timeline_history=[past],
        cfg=ExceptionsConfig(enable_ls_exc_after_lz=True, t_ls_after_lz=10.0),
    )
    assert not any(f.startswith("lls_") for f in out.flags)
    assert "ls_suppressed:after_lz" in out.flags
    assert out.lz_state is False
    assert out.lz_variant == 0


def test_lz_suppressed_by_dsp_timeout():
    current = _mk_timeline_step(flags=["llz_v8_open"], lz_variant=8)
    scenario_history = [
        _mk_scenario_step(t=5.0, rc_state=6, dsp=4, nas=0),
        _mk_scenario_step(t=6.0, rc_state=6, dsp=4, nas=0),
    ]
    out = apply_exceptions(
        ctrl_rc_id="108",
        current=current,
        scenario_history=scenario_history,
        timeline_history=[],
        cfg=ExceptionsConfig(
            enable_lz_exc_dsp=True,
            t_min_maneuver_v8=10.0,
        ),
    )
    assert not any(f.startswith("llz_v") for f in out.flags)
    assert "lz_suppressed:dsp_autoaction_timeout" in out.flags
    assert out.lz_state is False
    assert out.lz_variant == 0


def test_arbitration_lz_over_ls_when_both_present():
    current = _mk_timeline_step(flags=["llz_v2_open", "lls_1_open"], lz_variant=101)
    scenario_history = [_mk_scenario_step(t=1.0, rc_state=6)]
    out = apply_exceptions(
        ctrl_rc_id="108",
        current=current,
        scenario_history=scenario_history,
        timeline_history=[],
        cfg=ExceptionsConfig(),
    )
    assert any(f.startswith("llz_v2") for f in out.flags)
    assert not any(f.startswith("lls_") for f in out.flags)
    assert "ls_suppressed:priority_lz" in out.flags
    assert "ls_suppressed:v1:priority_lz" in out.flags
    assert out.lz_state is True
    assert out.lz_variant == 2


def test_arbitration_lz_over_ls_same_time_across_steps():
    # LZ was opened at absolute t=5.0 in a previous timeline step.
    past = _mk_timeline_step(flags=["llz_v2_open"], lz_variant=2, step_duration=1.0)
    past.t = 5.0

    # LS opens now at the same absolute t=5.0, but in a different processing step.
    current = _mk_timeline_step(flags=["lls_1_open"], lz_variant=101)
    current.t = 5.0

    scenario_history = [_mk_scenario_step(t=1.0, rc_state=6)]
    out = apply_exceptions(
        ctrl_rc_id="108",
        current=current,
        scenario_history=scenario_history,
        timeline_history=[past],
        cfg=ExceptionsConfig(),
    )
    assert not any(f.startswith("lls_") for f in out.flags)
    assert "ls_suppressed:priority_lz_same_time" in out.flags
    assert "ls_suppressed:v1:priority_lz_same_time" in out.flags


# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple, cast

from core.detectors_engine import DetectorsConfig
from core.sim_core import ScenarioStep, SimulationConfig, SimulationContext, TimelineStep


# RC ids for Visochino from tools/station/station_config.py
RC_10_12SP = "59"
RC_1P = "108"
RC_1_7SP = "83"
RC_3P = "104"
RC_3SP = "86"
RC_NDP = "98"


@dataclass
class FlagSummary:
    by_ctrl: Dict[str, Dict[str, int]]


def _make_cfg(ctrl_rc_id: str) -> DetectorsConfig:
    # Intentionally keeps many variants enabled exactly like the user scenario
    # to reproduce multi-variant interactions on one timeline.
    return DetectorsConfig(
        ctrl_rc_id=ctrl_rc_id,
        # LZ
        enable_lz1=True,
        ts01_lz1=3.0,
        tlz_lz1=3.0,
        tkon_lz1=3.0,
        enable_lz2=True,
        ts01_lz2=3.0,
        ts02_lz2=3.0,
        tlz_lz2=3.0,
        tkon_lz2=3.0,
        enable_lz3=True,
        ts01_lz3=3.0,
        ts02_lz3=3.0,
        tlz_lz3=3.0,
        tkon_lz3=3.0,
        enable_lz4=True,
        ts01_lz4=3.0,
        tlz_lz4=3.0,
        tkon_lz4=3.0,
        enable_lz5=True,
        ts01_lz5=3.0,
        tlz_lz5=3.0,
        tkon_lz5=3.0,
        enable_lz6=True,
        ts01_lz6=3.0,
        tlz_lz6=3.0,
        tkon_lz6=3.0,
        enable_lz7=True,
        ts01_lz7=3.0,
        tlz_lz7=3.0,
        tkon_lz7=3.0,
        enable_lz8=True,
        ts01_lz8=3.0,
        ts02_lz8=3.0,
        tlz_lz8=3.0,
        tkon_lz8=3.0,
        enable_lz9=True,
        ts01_lz9=3.0,
        tlz_lz9=3.0,
        tkon_lz9=3.0,
        enable_lz10=True,
        ts01_lz10=3.0,
        ts02_lz10=3.0,
        ts03_lz10=3.0,
        tlz_lz10=3.0,
        tkon_lz10=3.0,
        enable_lz11=True,
        ts01_lz11=3.0,
        tlz_lz11=3.0,
        tkon_lz11=3.0,
        enable_lz12=True,
        ts01_lz12=3.0,
        ts02_lz12=3.0,
        tlz_lz12=3.0,
        tkon_lz12=3.0,
        enable_lz13=True,
        ts01_lz13=3.0,
        ts02_lz13=3.0,
        tlz_lz13=3.0,
        tkon_lz13=3.0,
        # LS
        enable_ls1=True,
        ts01_ls1=3.0,
        tlz_ls1=3.0,
        tkon_ls1=3.0,
        enable_ls2=True,
        ts01_ls2=3.0,
        ts02_ls2=3.0,
        tlz_ls2=3.0,
        tkon_ls2=3.0,
        enable_ls4=True,
        ts01_ls4=3.0,
        tlz01_ls4=3.0,
        tlz02_ls4=3.0,
        tkon_ls4=3.0,
        enable_ls5=True,
        ts01_ls5=3.0,
        tlz_ls5=3.0,
        tkon_ls5=3.0,
        enable_ls6=True,
        ts01_ls6=3.0,
        tlz_ls6=3.0,
        tkon_ls6=3.0,
        enable_ls9=True,
        ts01_ls9=3.0,
        tlz_ls9=3.0,
        tkon_ls9=3.0,
        # Exceptions
        t_mu=3.0,
        t_recent_ls=3.0,
        t_min_maneuver_v8=3.0,
        enable_lz_exc_mu=False,
        enable_lz_exc_recent_ls=False,
        enable_lz_exc_dsp=False,
        t_ls_mu=3.0,
        t_ls_after_lz=3.0,
        t_ls_dsp=3.0,
        enable_ls_exc_mu=False,
        enable_ls_exc_after_lz=False,
        enable_ls_exc_dsp=False,
    )


def _base_steps_grouped() -> List[ScenarioStep]:
    # Scenario basis: t=5,7,7,9 with occupancy toggles.
    # Uses >= 6 RC and explicit adjacent sections for ctrl RC 1P (108) and 3P (104).
    # Switches are fixed in plus where used by this scenario.
    return [
        ScenarioStep(
            t=5.0,
            rc_states={
                RC_10_12SP: 6,
                RC_1P: 6,
                RC_1_7SP: 3,
                RC_3P: 6,
                RC_3SP: 6,
                RC_NDP: 3,
            },
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=7.0,
            rc_states={
                RC_10_12SP: 6,
                RC_1P: 3,
                RC_1_7SP: 3,
                RC_3P: 3,
                RC_3SP: 6,
                RC_NDP: 3,
            },
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=7.0,
            rc_states={
                RC_10_12SP: 6,
                RC_1P: 6,
                RC_1_7SP: 3,
                RC_3P: 6,
                RC_3SP: 6,
                RC_NDP: 3,
            },
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=9.0,
            rc_states={
                RC_10_12SP: 6,
                RC_1P: 6,
                RC_1_7SP: 3,
                RC_3P: 6,
                RC_3SP: 6,
                RC_NDP: 3,
            },
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        # Free both ctrl RC long enough to observe detector closure by tkon
        ScenarioStep(
            t=5.0,
            rc_states={
                RC_10_12SP: 3,
                RC_1P: 3,
                RC_1_7SP: 3,
                RC_3P: 3,
                RC_3SP: 3,
                RC_NDP: 3,
            },
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=5.0,
            rc_states={
                RC_10_12SP: 3,
                RC_1P: 3,
                RC_1_7SP: 3,
                RC_3P: 3,
                RC_3SP: 3,
                RC_NDP: 3,
            },
            switch_states={"87": 3, "88": 3, "110": 3},
            signal_states={},
            modes={},
        ),
    ]


def _expand_to_1s(steps: Iterable[ScenarioStep]) -> List[ScenarioStep]:
    expanded: List[ScenarioStep] = []
    for s in steps:
        secs = int(round(float(s.t)))
        assert secs >= 1
        for _ in range(secs):
            expanded.append(
                ScenarioStep(
                    t=1.0,
                    rc_states=dict(s.rc_states),
                    switch_states=dict(s.switch_states),
                    signal_states=dict(s.signal_states),
                    modes=dict(s.modes),
                )
            )
    return expanded


def _collect_summary(timeline: List[Dict[str, TimelineStep]], ctrl_ids: List[str]) -> FlagSummary:
    interesting_prefixes: Tuple[str, ...] = (
        "llz_v",
        "lls_",
        "exc_",
        "lz_suppressed:",
        "ls_suppressed:",
    )
    by_ctrl: Dict[str, Dict[str, int]] = {cid: {} for cid in ctrl_ids}

    for frame in timeline:
        for cid in ctrl_ids:
            step = frame[cid]
            for flag in step.flags:
                if not flag.startswith(interesting_prefixes):
                    continue
                by_ctrl[cid][flag] = by_ctrl[cid].get(flag, 0) + 1

    return FlagSummary(by_ctrl=by_ctrl)


def _collect_open_close_events(timeline: List[Dict[str, TimelineStep]]) -> List[Tuple[str, float, str]]:
    events: List[Tuple[str, float, str]] = []
    for frame in timeline:
        for rc_id, step in frame.items():
            for flag in step.flags:
                if flag.endswith("_open") or flag.endswith("_closed"):
                    events.append((rc_id, round(float(step.t), 6), flag))
    return events


def _run(steps: List[ScenarioStep], ctrl_ids: List[str]) -> List[Dict[str, TimelineStep]]:
    cfg = SimulationConfig(
        t_pk=3.0,
        detectors_configs={cid: _make_cfg(cid) for cid in ctrl_ids},
    )
    result = SimulationContext(config=cfg, scenario=steps, ctrl_rc_ids=ctrl_ids).run()
    return cast(List[Dict[str, TimelineStep]], result)


def test_user_multivariant_grouped_scenario_runs() -> None:
    ctrl_ids = [RC_1P, RC_3P]
    timeline = _run(_base_steps_grouped(), ctrl_ids)

    assert timeline
    summary = _collect_summary(timeline, ctrl_ids)

    # Minimal sanity: there must be at least one detector event in grouped mode.
    total_events = sum(sum(events.values()) for events in summary.by_ctrl.values())
    assert total_events > 0


def test_user_multivariant_grouped_equals_expanded_by_event_time() -> None:
    ctrl_ids = [RC_1P, RC_3P]

    grouped = _run(_base_steps_grouped(), ctrl_ids)
    expanded = _run(_expand_to_1s(_base_steps_grouped()), ctrl_ids)
    assert _collect_open_close_events(grouped) == _collect_open_close_events(expanded)

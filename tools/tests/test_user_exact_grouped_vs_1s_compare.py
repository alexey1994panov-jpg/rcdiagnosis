# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from core.detectors_engine import DetectorsConfig
from core.sim_core import ScenarioStep, SimulationConfig, SimulationContext, TimelineStep


# RC IDs (Visochino)
RC_1_7SP = "83"
RC_10_12SP = "59"
RC_14_16SP = "94"
RC_1AP = "47"
RC_1P = "108"
RC_2_8SP = "36"
RC_2AP = "62"
RC_2P = "90"
RC_3P = "104"
RC_3SP = "86"
RC_4P = "65"
RC_4SP = "58"
RC_6SP = "37"
RC_NDP = "98"
RC_NP = "81"
RC_CHDP = "57"
RC_CHP = "40"

# Switch IDs
SW1 = "87"
SW2 = "112"
SW3 = "97"
SW4 = "78"
SW5 = "106"
SW6 = "80"
SW10 = "88"
SW16 = "110"


def _config(ctrl_rc_id: str) -> DetectorsConfig:
    # All variants enabled with uniform timings = 3.0, exceptions disabled.
    return DetectorsConfig(
        ctrl_rc_id=ctrl_rc_id,
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


def _base_rc_all_free() -> Dict[str, int]:
    return {
        RC_1_7SP: 3,
        RC_10_12SP: 3,
        RC_14_16SP: 3,
        RC_1AP: 3,
        RC_1P: 3,
        RC_2_8SP: 3,
        RC_2AP: 3,
        RC_2P: 3,
        RC_3P: 3,
        RC_3SP: 3,
        RC_4P: 3,
        RC_4SP: 3,
        RC_6SP: 3,
        RC_NDP: 3,
        RC_NP: 3,
        RC_CHDP: 3,
        RC_CHP: 3,
    }


def _switch_all_plus() -> Dict[str, int]:
    return {
        SW1: 3,
        SW2: 3,
        SW3: 3,
        SW4: 3,
        SW5: 3,
        SW6: 3,
        SW10: 3,
        SW16: 3,
    }


def _signals_default() -> Dict[str, int]:
    return {
        "1": 3,
        "2": 3,
        "3": 3,
        "4": 3,
        "82": 15,
        "69": 15,
        "75": 15,
        "49": 15,
        "100": 15,
        "107": 15,
        "95": 15,
        "103": 15,
        "79": 15,
        "114": 15,
        "102": 15,
        "96": 15,
        "89": 15,
        "50": 15,
        "63": 15,
        "34": 15,
    }


def _mk_step(t: float, rc_overrides: Dict[str, int]) -> ScenarioStep:
    rc = _base_rc_all_free()
    rc.update(rc_overrides)
    return ScenarioStep(
        t=t,
        rc_states=rc,
        switch_states=_switch_all_plus(),
        signal_states=_signals_default(),
        modes={},
    )


def _grouped_steps() -> List[ScenarioStep]:
    # User scenario basis: 5,7,7,9 seconds.
    return [
        _mk_step(5.0, {RC_10_12SP: 6, RC_1P: 6, RC_3P: 6, RC_3SP: 6}),
        _mk_step(7.0, {RC_10_12SP: 6, RC_1P: 3, RC_3P: 3, RC_3SP: 6}),
        _mk_step(7.0, {RC_10_12SP: 6, RC_1P: 6, RC_3P: 6, RC_3SP: 6}),
        _mk_step(9.0, {RC_10_12SP: 6, RC_1P: 6, RC_3P: 6, RC_3SP: 6}),
    ]


def _expand_to_1s(steps: Sequence[ScenarioStep]) -> List[ScenarioStep]:
    out: List[ScenarioStep] = []
    for step in steps:
        secs = int(round(float(step.t)))
        for _ in range(secs):
            out.append(
                ScenarioStep(
                    t=1.0,
                    rc_states=dict(step.rc_states),
                    switch_states=dict(step.switch_states),
                    signal_states=dict(step.signal_states),
                    modes=dict(step.modes),
                )
            )
    return out


def _run(steps: List[ScenarioStep]) -> List[Dict[str, TimelineStep]]:
    ctrl_ids = [RC_1P, RC_3P]
    cfg = SimulationConfig(
        t_pk=30.0,
        detectors_configs={cid: _config(cid) for cid in ctrl_ids},
    )
    return list(SimulationContext(config=cfg, scenario=steps, ctrl_rc_ids=ctrl_ids).run())


def _events(frames: List[Dict[str, TimelineStep]], only_open_close: bool) -> List[Tuple[str, float, str]]:
    out: List[Tuple[str, float, str]] = []
    for frame in frames:
        for rc_id, step in frame.items():
            for flag in step.flags:
                if only_open_close:
                    if flag.endswith("_open") or flag.endswith("_closed"):
                        out.append((rc_id, round(float(step.t), 6), flag))
                else:
                    if flag.startswith("llz_v") or flag.startswith("lls_"):
                        out.append((rc_id, round(float(step.t), 6), flag))
    return out


def _diff(a: List[Tuple[str, float, str]], b: List[Tuple[str, float, str]]) -> str:
    sa = set(a)
    sb = set(b)
    only_a = sorted(sa - sb)
    only_b = sorted(sb - sa)
    lines: List[str] = []
    lines.append(f"only_grouped={len(only_a)}")
    lines.extend([f"  G {x}" for x in only_a[:40]])
    lines.append(f"only_expanded={len(only_b)}")
    lines.extend([f"  E {x}" for x in only_b[:40]])
    return "\n".join(lines)


def test_exact_user_scenario_grouped_vs_1s_open_close() -> None:
    grouped = _run(_grouped_steps())
    expanded = _run(_expand_to_1s(_grouped_steps()))

    g = _events(grouped, only_open_close=True)
    e = _events(expanded, only_open_close=True)

    assert set(g) == set(e), _diff(g, e)


def test_exact_user_scenario_grouped_vs_1s_all_lz_ls_flags() -> None:
    grouped = _run(_grouped_steps())
    expanded = _run(_expand_to_1s(_grouped_steps()))

    g = _events(grouped, only_open_close=False)
    e = _events(expanded, only_open_close=False)

    sg = set(g)
    se = set(e)
    only_grouped = sg - se
    only_expanded = se - sg

    # Current known behavior: lifecycle open/close matches,
    # but active-state tails differ for grouped vs expanded mode.
    assert not only_grouped
    assert only_expanded, "Expected active-tail diff, but sets are equal"

    expanded_flag_names = {flag for (_, _, flag) in only_expanded}
    assert {"llz_v5", "llz_v6", "llz_v7", "lls_9"}.issubset(expanded_flag_names), _diff(g, e)

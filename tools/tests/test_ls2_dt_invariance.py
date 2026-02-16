# -*- coding: utf-8 -*-
from typing import List, Tuple

from core.detectors_engine import DetectorsConfig
from core.sim_core import ScenarioStep, SimulationConfig, SimulationContext, TimelineStep


def _events(timeline: List[TimelineStep]) -> List[Tuple[str, float]]:
    out: List[Tuple[str, float]] = []
    for s in timeline:
        if "lls_2_open" in s.flags:
            out.append(("open", s.t))
        if "lls_2_closed" in s.flags:
            out.append(("closed", s.t))
    return out


def test_ls2_invariant_for_grouped_and_expanded_steps() -> None:
    """
    Один и тот же профиль состояний, заданный:
    1) крупными интервалами и
    2) эквивалентным разбиением по 1 секунде,
    должен давать одинаковые события LS2 (open/closed).
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False,
        enable_lz2=False,
        enable_lz3=False,
        enable_lz4=False,
        enable_lz5=False,
        enable_lz6=False,
        enable_lz7=False,
        enable_lz8=False,
        enable_lz9=False,
        enable_lz10=False,
        enable_lz11=False,
        enable_lz12=False,
        enable_lz13=False,
        enable_ls1=False,
        enable_ls2=True,
        ts01_ls2=2.0,
        tlz_ls2=2.0,
        ts02_ls2=2.0,
        tkon_ls2=3.0,
        enable_ls4=False,
        enable_ls5=False,
        enable_ls6=False,
        enable_ls9=False,
        enable_lz_exc_mu=False,
        enable_lz_exc_recent_ls=False,
        enable_lz_exc_dsp=False,
        enable_ls_exc_mu=False,
        enable_ls_exc_after_lz=False,
        enable_ls_exc_dsp=False,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    # 110 -> 100 -> 110 -> 000
    s110 = {"59": 6, "108": 6, "83": 3}
    s100 = {"59": 6, "108": 3, "83": 3}
    s000 = {"59": 3, "108": 3, "83": 3}
    sw = {"110": 3, "88": 3}

    grouped = [
        ScenarioStep(t=3.0, rc_states=s110, switch_states=sw, signal_states={}, modes={}),
        ScenarioStep(t=3.0, rc_states=s100, switch_states=sw, signal_states={}, modes={}),
        ScenarioStep(t=4.0, rc_states=s110, switch_states=sw, signal_states={}, modes={}),
        ScenarioStep(t=5.0, rc_states=s000, switch_states=sw, signal_states={}, modes={}),
    ]
    expanded = (
        [ScenarioStep(t=1.0, rc_states=s110, switch_states=sw, signal_states={}, modes={}) for _ in range(3)]
        + [ScenarioStep(t=1.0, rc_states=s100, switch_states=sw, signal_states={}, modes={}) for _ in range(3)]
        + [ScenarioStep(t=1.0, rc_states=s110, switch_states=sw, signal_states={}, modes={}) for _ in range(4)]
        + [ScenarioStep(t=1.0, rc_states=s000, switch_states=sw, signal_states={}, modes={}) for _ in range(5)]
    )

    tl_grouped = list(SimulationContext(sim_cfg, grouped, ctrl_rc_id="108").run())
    tl_expanded = list(SimulationContext(sim_cfg, expanded, ctrl_rc_id="108").run())

    events_grouped = _events(tl_grouped)
    events_expanded = _events(tl_expanded)
    assert [k for (k, _) in events_grouped] == [k for (k, _) in events_expanded]
    assert len(events_grouped) == len(events_expanded)
    assert any("lls_2_open" in s.flags for s in tl_grouped)
    assert any("lls_2_closed" in s.flags for s in tl_grouped)

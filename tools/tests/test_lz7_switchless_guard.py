from core.detectors_engine import DetectorsConfig
from core.sim_core import ScenarioStep, SimulationConfig, SimulationContext


def test_lz7_does_not_open_on_switch_connected_rc_1p() -> None:
    """
    Business rule: LZ7 must work only on switchless RC.
    1P (id=108) is switch-connected, so LZ7 must not open.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",          # 1P
        prev_rc_name="10-12СП",
        ctrl_rc_name="1П",
        next_rc_name="1-7СП",
        enable_lz7=True,
        ts01_lz7=3.0,
        tlz_lz7=3.0,
        tkon_lz7=3.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    sw_plus = {"87": 3, "88": 3, "110": 3}
    scenario = [
        ScenarioStep(
            t=4.0,
            rc_states={"10-12СП": 6, "1П": 3, "1-7СП": 3},
            switch_states=sw_plus,
            signal_states={},
            modes={},
        ),
        ScenarioStep(
            t=4.0,
            rc_states={"10-12СП": 6, "1П": 6, "1-7СП": 3},
            switch_states=sw_plus,
            signal_states={},
            modes={},
        ),
    ]

    timeline = list(SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108").run())
    assert not any("llz_v7_open" in step.flags for step in timeline)
    assert not any("llz_v7" in step.flags for step in timeline)
    assert not any("llz_v7_closed" in step.flags for step in timeline)

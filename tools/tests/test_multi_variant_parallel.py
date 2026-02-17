# -*- coding: utf-8 -*-
from core.detectors_engine import DetectorsConfig
from core.sim_core import ScenarioStep, SimulationConfig, SimulationContext


def test_multi_variants_parallel_on_different_ctrl_rc() -> None:
    """
    Один общий сценарий для нескольких ctrl RC одновременно:
    - RC 108: LS9 (1 -> 0 -> 1, затем закрытие по tkon)
    - RC 83:  LZ6 (0 -> 1, затем закрытие по tkon)
    - RC 59:  LZ11 (ctrl 0 -> 1 при закрытых сигналах, затем закрытие по tkon)
    """
    cfg_108 = DetectorsConfig(
        ctrl_rc_id="108",
        enable_ls9=True,
        ts01_ls9=1.0,
        tlz_ls9=1.0,
        tkon_ls9=1.0,
        enable_lz_exc_mu=False,
        enable_lz_exc_recent_ls=False,
        enable_lz_exc_dsp=False,
        enable_ls_exc_mu=False,
        enable_ls_exc_after_lz=False,
        enable_ls_exc_dsp=False,
    )
    cfg_83 = DetectorsConfig(
        ctrl_rc_id="83",
        enable_lz6=True,
        ts01_lz6=1.0,
        tlz_lz6=1.0,
        tkon_lz6=1.0,
        enable_lz_exc_mu=False,
        enable_lz_exc_recent_ls=False,
        enable_lz_exc_dsp=False,
        enable_ls_exc_mu=False,
        enable_ls_exc_after_lz=False,
        enable_ls_exc_dsp=False,
    )
    cfg_59 = DetectorsConfig(
        ctrl_rc_id="59",
        enable_lz11=True,
        ts01_lz11=1.0,
        tlz_lz11=1.0,
        tkon_lz11=1.0,
        sig_lz11_a="114",  # Ч1
        sig_lz11_b="107",  # НМ1
        enable_lz_exc_mu=False,
        enable_lz_exc_recent_ls=False,
        enable_lz_exc_dsp=False,
        enable_ls_exc_mu=False,
        enable_ls_exc_after_lz=False,
        enable_ls_exc_dsp=False,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_configs={
            "108": cfg_108,
            "83": cfg_83,
            "59": cfg_59,
        },
    )

    scenario = [
        # t0..t1
        # 108=occ (LS9 phase0), 83=free (LZ6 phase0), 59=free (LZ11 phase0), sigs closed
        ScenarioStep(
            t=1.0,
            rc_states={"108": 6, "83": 3, "59": 3},
            switch_states={},
            signal_states={"114": 15, "107": 15},
            modes={},
        ),
        # t1..t2
        # 108=free (LS9 phase1), 83=occ (LZ6 open), 59=occ (LZ11 open)
        ScenarioStep(
            t=1.0,
            rc_states={"108": 3, "83": 6, "59": 6},
            switch_states={},
            signal_states={"114": 15, "107": 15},
            modes={},
        ),
        # t2..t3
        # 108=occ (LS9 open), 83=free (LZ6 close), 59=free (LZ11 close)
        ScenarioStep(
            t=1.0,
            rc_states={"108": 6, "83": 3, "59": 3},
            switch_states={},
            signal_states={"114": 15, "107": 15},
            modes={},
        ),
        # t3..t4
        # 108=free (LS9 close trigger step 1)
        ScenarioStep(
            t=1.0,
            rc_states={"108": 3, "83": 3, "59": 3},
            switch_states={},
            signal_states={"114": 15, "107": 15},
            modes={},
        ),
        # t4..t5
        # 108=occ (LS9 close trigger step 2 - OCCUPIED_TIME)
        ScenarioStep(
            t=1.0,
            rc_states={"108": 6, "83": 3, "59": 3},
            switch_states={},
            signal_states={"114": 15, "107": 15},
            modes={},
        ),
    ]

    timeline = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_ids=["108", "83", "59"]).run()

    flags_108 = [f for frame in timeline for f in frame["108"].flags]
    flags_83 = [f for frame in timeline for f in frame["83"].flags]
    flags_59 = [f for frame in timeline for f in frame["59"].flags]

    assert "lls_9_open" in flags_108
    assert "lls_9_closed" in flags_108

    assert "llz_v6_open" in flags_83
    assert "llz_v6_closed" in flags_83

    assert "llz_v11_open" in flags_59
    assert "llz_v11_closed" in flags_59

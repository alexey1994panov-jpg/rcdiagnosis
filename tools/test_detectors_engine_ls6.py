# -*- coding: utf-8 -*-
from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig

def run_ls6_test(ctrl_rc_id, adj_rc_id, nc_side, sig_id, sw_states, branch="6.1"):
    """
    Утилита для запуска теста LS6.
    nc_side: "prev" или "next"
    branch: "6.1" (Prev NC) или "6.2" (Next NC)
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id=ctrl_rc_id,
        # Мы НЕ инициализируем имена соседей в конфиге, 
        # чтобы проверить работу динамической топологии!
        enable_ls6=True,
        ts01_ls6=1.0,
        tlz_ls6=1.0,
        tkon_ls6=2.0,
        sig_ls6_prev=sig_id,
    )

    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    rc_states_p1 = {ctrl_rc_id: 4, adj_rc_id: 4} # locked
    rc_states_kogda = {ctrl_rc_id: 4, adj_rc_id: 7} # adj occupied+locked
    
    scenario = [
        # Phase 01: 0-2с
        ScenarioStep(
            t=2.0,
            rc_states=rc_states_p1,
            switch_states=sw_states,
            signal_states={sig_id: 3},
            modes={f"{nc_side}_nc": True},
        ),
        # Phase KOGDA: 2-4с -> открытие
        ScenarioStep(
            t=2.0,
            rc_states=rc_states_kogda,
            switch_states=sw_states,
            signal_states={sig_id: 3},
            modes={f"{nc_side}_nc": True},
        ),
        # Завершение: 4-7с -> закрытие
        ScenarioStep(
            t=3.0,
            rc_states={ctrl_rc_id: 6, adj_rc_id: 7},
            switch_states=sw_states,
            signal_states={sig_id: 3},
            modes={f"{nc_side}_nc": True},
        ),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id=ctrl_rc_id)
    timeline = ctx.run()
    
    opened = any("lls_6_open" in s.flags for s in timeline)
    closed = any("lls_6_closed" in s.flags for s in timeline)
    
    return opened, closed

def test_ls6_endpoints():
    print("\n=== Testing LS6 on endpoints ===")
    
    # 1. ЧП (40). Neighbor 36. Switch 2 (32).
    # Link 40 <-> 36 depends on Switch 2 (req=-1 in our Part 3).
    ok40_o, ok40_c = run_ls6_test("40", "36", "prev", "42", {"32": 3}, "6.1")
    print(f"ChP (40): opened={ok40_o}, closed={ok40_c}")

    # 2. ЧДП (57). Neighbor 58. Switch 4 (33).
    ok57_o, ok57_c = run_ls6_test("57", "58", "prev", "53", {"33": 3}, "6.1")
    print(f"ChDP (57): opened={ok57_o}, closed={ok57_c}")

    # 3. НП (81). Neighbor 83. Switch 1 (87).
    ok81_o, ok81_c = run_ls6_test("81", "83", "next", "78", {"87": 3}, "6.2")
    print(f"NP (81): opened={ok81_o}, closed={ok81_c}")

    # 4. НДП (98). Neighbor 86. Switch 3 (150).
    ok98_o, ok98_c = run_ls6_test("98", "86", "next", "100", {"150": 3}, "6.2")
    print(f"NDP (98): opened={ok98_o}, closed={ok98_c}")

    assert ok40_o, "ChP should pass with switch control"
    assert ok57_o, "ChDP should pass with switch control"
    assert ok81_o, "NP should pass with switch control"
    assert ok98_o, "NDP should pass with switch control"

def test_ls6_rc65_failure():
    print("\n=== Testing LS6 on RC 65 (Cannot be locked) ===")
    # 4П (65). Neighbor 36. Switch 2 (32). Position Minus (0).
    # 65 has can_lock: False. LS6 mask check _is_locked should fail.
    # state 4 for 65 is technically "locked" if we set it, but capabilities say it can't.
    # Actually, in our masks: _is_locked(ctrl_id, step)
    
    # Branch 6.1 (Prev NC)
    # 36 -> 65 is Switch 2 Minus (0).
    ok65_o, ok65_c = run_ls6_test("65", "36", "prev", "64", {"32": 9}, "6.1")
    print(f"RC 65: opened={ok65_o}, closed={ok65_c}")
    
    assert not ok65_o, "RC 65 should NOT activate LS6 (no locking capability)"

if __name__ == "__main__":
    test_ls6_endpoints()
    test_ls6_rc65_failure()

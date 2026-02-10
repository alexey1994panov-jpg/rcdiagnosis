# -*- coding: utf-8 -*-
"""
Тесты для варианта LZ9 (Пробой изолирующего стыка) с поддержкой NC.

Логика: Почти одновременное занятие центра и соседа (|dt| <= tlz_lz9).
Соседи проверяются по маске (Free | NC).
"""

from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig


def test_lz9_1p_ctrl_then_adj():
    """Центр занялся, через 1с занялся сосед -> LZ9."""
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz1=False, enable_lz9=True,
        ts01_lz9=2.0, tlz_lz9=2.0, tkon_lz9=2.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-3с: Дано (0-0-0)
        ScenarioStep(t=3.0, rc_states={"59": 3, "108": 3, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        # 3-4с: Центр занялся (t=0)
        ScenarioStep(t=1.0, rc_states={"59": 3, "108": 6, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        # 4-5с: Сосед занялся (t=1, delta=1 <= 2) -> Открытие
        ScenarioStep(t=1.0, rc_states={"59": 6, "108": 6, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        # 5-8с: Ткон
        ScenarioStep(t=3.0, rc_states={"59": 3, "108": 3, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()

    print("\n=== LZ9 Test: Ctrl First ===")
    for s in timeline:
        print(f"t={s.t:.1f}, lz={s.lz_state}, variant={s.lz_variant}, flags={s.flags}")

    assert any("llz_v9_open" in s.flags for s in timeline)
    assert any(s.lz_variant == 9 for s in timeline)
    assert any("llz_v9_closed" in s.flags for s in timeline)


def test_lz9_1p_adj_then_ctrl():
    """Сосед занялся, через 1.5с занялся центр -> LZ9."""
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108", prev_rc_name="59", ctrl_rc_name="108", next_rc_name="83",
        enable_lz9=True, ts01_lz9=1.0, tlz_lz9=2.0, tkon_lz9=2.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        ScenarioStep(t=2.0, rc_states={"59": 3, "108": 3, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        ScenarioStep(t=1.5, rc_states={"59": 6, "108": 3, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        ScenarioStep(t=0.5, rc_states={"59": 6, "108": 6, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
        ScenarioStep(t=3.0, rc_states={"59": 3, "108": 3, "83": 3}, switch_states={"110": 3, "88": 3}, signal_states={}, modes={}),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()
    assert any("llz_v9_open" in s.flags for s in timeline)


def test_lz9_nc_neighbor():
    """Один сосед NC (тупик). Центр занялся -> Проверяем, что NC не блокирует."""
    # РЦ 59 (обычная)
    det_cfg_59 = DetectorsConfig(
        ctrl_rc_id="59", prev_rc_name="47", ctrl_rc_name="59", next_rc_name="108",
        enable_lz9=True, ts01_lz9=1.0, tlz_lz9=2.0, tkon_lz9=2.0,
    )
    # РЦ 57 (ЧДП, крайняя)
    det_cfg_57 = DetectorsConfig(
        ctrl_rc_id="57", prev_rc_name="NONE", ctrl_rc_name="57", next_rc_name="58",
        enable_lz9=True, ts01_lz9=1.0, tlz_lz9=2.0, tkon_lz9=2.0,
    )
    
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_configs={"59": det_cfg_59, "57": det_cfg_57})

    scenario = [
        # 0-2с: Все свободны
        ScenarioStep(t=2.0, rc_states={"47": 3, "59": 3, "57": 3, "58": 3}, switch_states={"110": 3}, signal_states={}, modes={}),
        # 2-3с: Занятие 47 и 58 (соседи)
        ScenarioStep(t=1.0, rc_states={"47": 6, "59": 3, "57": 3, "58": 6}, switch_states={"110": 3}, signal_states={}, modes={}),
        # 3-3.5с: Занятие центров 59 и 57 (BREAKDOWN)
        ScenarioStep(t=0.5, rc_states={"47": 6, "59": 6, "57": 6, "58": 6}, switch_states={"110": 3}, signal_states={}, modes={}),
        # 3.5-6.5с: Свободны
        ScenarioStep(t=3.0, rc_states={"47": 3, "59": 3, "57": 3, "58": 3}, switch_states={"110": 3}, signal_states={}, modes={}),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_ids=["59", "57"])
    timeline = ctx.run()
    
    # Проверяем 57 (крайнюю)
    results_57 = [step["57"] for step in timeline]
    assert any("llz_v9_open" in s.flags for s in results_57)
    assert any(s.lz_variant == 9 for s in results_57)

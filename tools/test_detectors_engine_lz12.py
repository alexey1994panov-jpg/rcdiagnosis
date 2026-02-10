# -*- coding: utf-8 -*-
"""
Тесты для варианта LZ12 (Крайние секции / NC).

Логика: Секция является крайней (нет связей в топологии) -> NC=True.
Занятие такой секции после свободности -> LZ12.
"""

from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig


def test_lz12_endpoint_81():
    """РЦ 81 - крайняя (is_endpoint=True). Занятие -> LZ12."""
    det_cfg = DetectorsConfig(
        ctrl_rc_id="81",
        enable_lz1=False, enable_lz12=True,
        ts01_lz12=2.0, tlz_lz12=1.0, tkon_lz12=2.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # 0-3с: Дано (свободна). 81 крайняя -> next_nc/prev_nc=True.
        # В Visochino 1P: 81 ('НП') NextSec=None.
        ScenarioStep(t=3.0, rc_states={"81": 3, "83": 3}, switch_states={}, signal_states={}, modes={}),
        # 3-5с: Занятие.
        ScenarioStep(t=2.0, rc_states={"81": 6, "83": 3}, switch_states={}, signal_states={}, modes={}),
        # 5-8с: Ткон -> Закрытие
        ScenarioStep(t=3.0, rc_states={"81": 3, "83": 3}, switch_states={}, signal_states={}, modes={}),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="81")
    timeline = ctx.run()

    print("\n=== LZ12 Test: Endpoint 81 ===")
    for s in timeline:
        prev_nc = s.modes.get("prev_nc")
        next_nc = s.modes.get("next_nc")
        print(f"t={s.t:.1f}, lz={s.lz_state}, variant={s.lz_variant}, prev_nc={prev_nc}, next_nc={next_nc}, flags={s.flags}")

    # У 81 в Visochino 1P: is_endpoint=True.
    assert any("llz_v12_open" in s.flags for s in timeline)
    assert any(s.lz_variant == 12 for s in timeline)

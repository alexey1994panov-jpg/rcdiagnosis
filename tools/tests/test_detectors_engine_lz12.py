# -*- coding: utf-8 -*-
"""
РўРµСЃС‚С‹ РґР»СЏ РІР°СЂРёР°РЅС‚Р° LZ12 (РљСЂР°Р№РЅРёРµ СЃРµРєС†РёРё / NC).

Р›РѕРіРёРєР°: РЎРµРєС†РёСЏ СЏРІР»СЏРµС‚СЃСЏ РєСЂР°Р№РЅРµР№ (РЅРµС‚ СЃРІСЏР·РµР№ РІ С‚РѕРїРѕР»РѕРіРёРё) -> NC=True.
Р—Р°РЅСЏС‚РёРµ С‚Р°РєРѕР№ СЃРµРєС†РёРё РїРѕСЃР»Рµ СЃРІРѕР±РѕРґРЅРѕСЃС‚Рё -> LZ12.
"""

from typing import List, cast

from core.sim_core import SimulationConfig, SimulationContext, ScenarioStep, TimelineStep
from core.detectors_engine import DetectorsConfig


def test_lz12_endpoint_81():
    """Р Р¦ 81 - РєСЂР°Р№РЅСЏСЏ (is_endpoint=True). Ctrl Р·Р°РЅСЏС‚Р° РІРѕ РІСЃРµС… С„Р°Р·Р°С….,
    Р° СЃРјРµР¶РЅР°СЏ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјР°СЏ Р Р¦ Р·Р°РЅРёРјР°РµС‚СЃСЏ РЅР° С„Р°Р·Рµ 2."""
    det_cfg = DetectorsConfig(
        ctrl_rc_id="81",
        enable_lz1=False, enable_lz12=True,
        ts01_lz12=2.0, ts02_lz12=1.0, tlz_lz12=1.0, tkon_lz12=2.0,
    )
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)

    scenario = [
        # Фаза 1 (TS01): ctrl=занята+замкнута (7), смежная=свободна+замкнута (4).
        ScenarioStep(t=2.0, rc_states={"81": 7, "83": 4}, switch_states={}, signal_states={}, modes={}),
        # Фаза 2 (TS02): ctrl=занята+замкнута (7), смежная=занята+замкнута (7).
        ScenarioStep(t=1.0, rc_states={"81": 7, "83": 7}, switch_states={}, signal_states={}, modes={}),
        # Фаза 3 (TLZ): ctrl=занята+замкнута (7), смежная=свободна+замкнута (4).
        ScenarioStep(t=1.0, rc_states={"81": 7, "83": 4}, switch_states={}, signal_states={}, modes={}),
        # Закрытие по TKON: ctrl свободна+замкнута (4).
        ScenarioStep(t=3.0, rc_states={"81": 4, "83": 4}, switch_states={}, signal_states={}, modes={}),
    ]

    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="81")
    timeline = cast(List[TimelineStep], ctx.run())

    print("\n=== LZ12 Test: Endpoint 81 ===")
    for s in timeline:
        prev_nc = s.modes.get("prev_nc")
        next_nc = s.modes.get("next_nc")
        print(f"t={s.t:.1f}, lz={s.lz_state}, variant={s.lz_variant}, prev_nc={prev_nc}, next_nc={next_nc}, flags={s.flags}")

    # РЈ 81 РІ Visochino 1P: is_endpoint=True.
    assert any("llz_v12_open" in s.flags for s in timeline)
    assert any("llz_v12_closed" in s.flags for s in timeline)
    assert any(s.lz_variant == 12 for s in timeline)


from core.sim_core import ScenarioStep, SimulationConfig, SimulationContext

def make_demo_scenario():
    steps = []

    # t=0: РІСЃС‘ СЃРІРѕР±РѕРґРЅРѕ
    steps.append(
        ScenarioStep(
            t=0.0,
            rc_states={"108": 3},      # 1Рџ СЃРІРѕР±РѕРґРЅР° (СѓСЃР»РѕРІРЅС‹Р№ РєРѕРґ)
            switch_states={"87": 3},   # СЃС‚СЂРµР»РєР° РІ РїР»СЋСЃРµ
            signal_states={},          # РїРѕРєР° РїСѓСЃС‚Рѕ
            modes={},
        )
    )

    # t=5: 1Рџ Р·Р°РЅСЏС‚Р°
    steps.append(
        ScenarioStep(
            t=5.0,
            rc_states={"108": 6},      # 1Рџ Р·Р°РЅСЏС‚Р°
            switch_states={"87": 3},
            signal_states={},
            modes={},
        )
    )

    # t=20: 1Рџ СЃРЅРѕРІР° СЃРІРѕР±РѕРґРЅР°
    steps.append(
        ScenarioStep(
            t=20.0,
            rc_states={"108": 3},
            switch_states={"87": 3},
            signal_states={},
            modes={},
        )
    )

    return steps


if __name__ == "__main__":
    cfg = SimulationConfig(t_pk=30.0)
    scenario = make_demo_scenario()
    ctx = SimulationContext(config=cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()

    for step in timeline:
        print(step)


import json
from pathlib import Path

from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p
from engine.types_1p import ScenarioStep


def _build_steps_from_json(data: dict) -> tuple[dict, list[ScenarioStep]]:
    options = data.get("options", {})
    steps: list[ScenarioStep] = []
    for raw in data["steps"]:
        steps.append(
            ScenarioStep(
                t=raw["t"],
                rc_states=raw["rc_states"],
                switch_states=raw["switch_states"],
                modes=raw.get("modes", {}),
                mu=raw.get("mu"),
                dispatcher_control_state=raw.get("dispatcher_control_state"),
                auto_actions=raw.get("auto_actions"),
                signal_states=raw.get("signal_states"),
            )
        )
    return options, steps


def test_variant10_scenario(tmp_path: Path):
    # сценарий из условия: 4 шага, только вариант 10 включён
    scenario_json = {
        "options": {
            "t_s0110": 3.0,
            "t_s0210": 3.0,
            "t_s0310": 3.0,
            "t_lz10": 3.0,
            "t_kon_v10": 3.0,
            "enable_v10": True,
            "enable_v1": False,
            "enable_v2": False,
            "enable_v3": False,
            "enable_v5": False,
            "enable_v6": False,
            "enable_v7": False,
            "enable_v8": False,
            "enable_ls1": False,
            "enable_ls2": False,
            "enable_ls4": False,
            "enable_ls9": False,
        },
        "steps": [
            {
                # T_S0110: prev=3, curr=6, next=3, Ч1 открыт
                "t": 3.0,
                "rc_states": {"10-12SP": 3, "1P": 6, "1-7SP": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "signal_states": {"Ч1": 3, "НМ1": 15},
                "modes": {}
            },
            {
                # T_S0210: prev=3, curr=6, next=6, Ч1 открыт
                "t": 3.0,
                "rc_states": {"10-12SP": 3, "1P": 6, "1-7SP": 6},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "signal_states": {"Ч1": 3, "НМ1": 15},
                "modes": {}
            },
            {
                # T_S0310: prev=3, curr=6, next=6, Ч1 закрыт
                "t": 3.0,
                "rc_states": {"10-12SP": 3, "1P": 6, "1-7SP": 6},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "signal_states": {"Ч1": 15, "НМ1": 15},
                "modes": {}
            },
            {
                # T_LZ10: prev=3, curr=6, next=3, Ч1 закрыт
                "t": 3.0,
                "rc_states": {"10-12SP": 3, "1P": 6, "1-7SP": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "signal_states": {"Ч1": 15, "НМ1": 15},
                "modes": {}
            }
        ]
    }

    # опционально можно писать/читать файл, но для теста достаточно in-memory
    options, steps = _build_steps_from_json(scenario_json)

    station = get_station_model_1p()
    timeline = simulate_1p(station, steps, dt=1.0, options=options)

    # симуляция должна дать 4 шага
    assert len(timeline) == 4

    variants = [st.variant for st in timeline]
    all_flags = [f for st in timeline for f in st.flags]

    # вариант 10 должен участвовать в формировании ЛЗ
    assert any("llz_v10" in st.flags for st in timeline)

    # должна быть ЛЗ, помеченная как v10
    assert any(st.lz_state and "llz_v10" in st.flags for st in timeline)

    # и на каком-то шаге variant должен быть 10 (так как остальные выключены)
    assert 10 in variants

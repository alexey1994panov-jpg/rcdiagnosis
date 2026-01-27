# tests/test_variant11_1p.py

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


def test_variant11_scenario(tmp_path: Path):
    # Сценарий для v11: ДАНО (2 шага), КОГДА, завершение
    scenario_json = {
        "options": {
            # v11 timings
            "t_s11": 3.0,
            "t_lz11": 3.0,
            "t_kon_v11": 3.0,
            "enable_v11": True,
            # все остальные варианты ЛЗ/ЛС выключены
            "enable_v1": False,
            "enable_v2": False,
            "enable_v3": False,
            "enable_v5": False,
            "enable_v6": False,
            "enable_v7": False,
            "enable_v8": False,
            "enable_v10": False,
            "enable_ls1": False,
            "enable_ls2": False,
            "enable_ls4": False,
            "enable_ls9": False,
        },
        "steps": [
            # ДАНО шаг 1: РЦ свободна (3), светофоры Ч1/НМ1 = 15, 3 секунды
            {
                "t": 3.0,
                "rc_states": {"1P": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "signal_states": {"Ч1": 15, "НМ1": 15},
                "modes": {},
            },
            # ДАНО шаг 2: то же самое, ещё 3 секунды
            {
                "t": 3.0,
                "rc_states": {"1P": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "signal_states": {"Ч1": 15, "НМ1": 15},
                "modes": {},
            },
            # КОГДА: РЦ занята (6), светофоры закрыты 15, 3 секунды
            {
                "t": 3.0,
                "rc_states": {"1P": 6},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "signal_states": {"Ч1": 15, "НМ1": 15},
                "modes": {},
            },
            # Завершение: РЦ снова свободна (3), 3 секунды
            {
                "t": 3.0,
                "rc_states": {"1P": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "signal_states": {"Ч1": 15, "НМ1": 15},
                "modes": {},
            },
        ],
    }

    options, steps = _build_steps_from_json(scenario_json)
    station = get_station_model_1p()
    timeline = simulate_1p(station, steps, dt=1.0, options=options)

    # симуляция должна дать 4 шага
    assert len(timeline) == 4

    variants = [st.variant for st in timeline]

    # вариант 11 должен участвовать в формировании ЛЗ
    assert any("llz_v11" in st.flags for st in timeline)

    # должна быть ЛЗ, помеченная как v11
    assert any(st.lz_state and "llz_v11" in st.flags for st in timeline)

    # и на каком-то шаге variant должен быть 11 (так как остальные выключены)
    assert 11 in variants

    # ДС должен завершиться: на последнем шаге ЛЗ нет
    assert not timeline[-1].lz_state

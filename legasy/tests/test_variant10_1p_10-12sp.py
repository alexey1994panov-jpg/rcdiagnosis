# tests/test_variant10_10_12sp_direction_from_json.py

from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p
from engine.types_1p import ScenarioStep


def _build_steps_from_json(data: dict) -> tuple[dict, list[ScenarioStep]]:
    options = data.get("options", {})
    options.pop("v13_ctrl_rc_id", None)  # игнорируем устаревшее поле, если придёт

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


def test_variant10_scenario_prev_direction():
    """
    Вариант 10, ветка 10.2:
      - curr=1P занята,
      - prev=10-12SP становится занятой,
      - next=1-7SP свободна,
      - сначала НМ1 открыт, затем закрывается.
    Ожидаем: формируется ДС v10 (llz_v10, variant=10).
    """

    scenario_json = {
        "station": "Visochino",
        "target_rc": "1P",
        "dt": 1,
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
            "enable_v4": False,
            "enable_v5": False,
            "enable_v6": False,
            "enable_v7": False,
            "enable_v8": False,
            "enable_v9": False,
            "enable_v11": False,
            "enable_v12": False,
            "enable_v13": False,
            "enable_ls1": False,
            "enable_ls2": False,
            "enable_ls4": False,
            "enable_ls9": False,
        },
        "steps": [
            {
                "t": 3.0,
                "rc_states": {"10-12SP": 3, "1P": 6, "1-7SP": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 15, "НМ1": 3, "ЧМ1": 0, "М1": 0},
            },
            {
                "t": 3.0,
                "rc_states": {"10-12SP": 6, "1P": 6, "1-7SP": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 15, "НМ1": 3, "ЧМ1": 0, "М1": 0},
            },
            {
                "t": 3.0,
                "rc_states": {"10-12SP": 6, "1P": 6, "1-7SP": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 15, "НМ1": 15, "ЧМ1": 0, "М1": 0},
            },
            {
                "t": 3.0,
                "rc_states": {"10-12SP": 3, "1P": 6, "1-7SP": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 15, "НМ1": 15, "ЧМ1": 0, "М1": 0},
            },
        ],
    }

    options, steps = _build_steps_from_json(scenario_json)
    station = get_station_model_1p()
    timeline = simulate_1p(station, steps, dt=1.0, options=options)

    print("\n=== TIMELINE v10 prev_direction ===")
    for i, st in enumerate(timeline):
        print(f"Step {i}: t={st.t}, variant={st.variant}, lz={st.lz_state}, flags={st.flags}")

    assert any("llz_v10" in st.flags for st in timeline)
    assert any(st.lz_state and "llz_v10" in st.flags for st in timeline)
    assert 10 in [st.variant for st in timeline]
    assert any("llz_v10_open" in st.flags for st in timeline)

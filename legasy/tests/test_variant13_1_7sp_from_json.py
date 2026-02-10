# tests/test_variant13_1_7sp_from_json.py

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


def test_variant13_scenario_for_1_7sp():
    """
    Вариант 13 с контролируемой 1-7SP, смежная 1P, сигнал Ч1 закрыт.

    Фазы:
    1) 1-7SP 3 (ctrl_free), 1P 3 (adj_free+locked), Ч1 15 — S0113
    2) 1-7SP 3 (ctrl_free), 1P 7 (adj_occ+locked), Ч1 15 — S0213
    3) 1-7SP 6 (ctrl_occ), 1P 7 (adj_occ+locked), Ч1 15 — LZ13 (открытие)
    4) 1-7SP 3 (ctrl_free), 1P 7 (adj_occ+locked), Ч1 15 — завершение
    """

    scenario_json = {
        "station": "Visochino",
        "target_rc": "1P",
        "dt": 1,
        "options": {
            "t_s0113": 3.0,
            "t_s0213": 3.0,
            "t_lz13": 3.0,
            "t_kon_v13": 3.0,
            "enable_v13": True,
            "v13_ctrl_rc_id": "1-7SP",

            # вырубаем всё остальное, чтобы не мешало
            "enable_v1": False,
            "enable_v2": False,
            "enable_v3": False,
            "enable_v4": False,
            "enable_v5": False,
            "enable_v6": False,
            "enable_v7": False,
            "enable_v8": False,
            "enable_v9": False,
            "enable_v10": False,
            "enable_v11": False,
            "enable_v12": False,
            "enable_ls1": False,
            "enable_ls2": False,
            "enable_ls4": False,
            "enable_ls9": False,
        },
        "steps": [
            {
                # --- фаза 01: ctrl_free, adj_free+locked, Ч1 закрыт ---
                "t": 3.0,
                "rc_states": {"10-12SP": 3, "1P": 4, "1-7SP": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 15, "НМ1": 3, "ЧМ1": 0, "М1": 0},
            },
            {
                # --- фаза 02: ctrl_free, adj_occ+locked, Ч1 закрыт ---
                "t": 3.0,
                "rc_states": {"10-12SP": 3, "1P": 7, "1-7SP": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 15, "НМ1": 3, "ЧМ1": 0, "М1": 0},
            },
            {
                # --- LZ13: ctrl_occ, adj_occ+locked, Ч1 закрыт ---
                "t": 3.0,
                "rc_states": {"10-12SP": 3, "1P": 7, "1-7SP": 6},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 15, "НМ1": 3, "ЧМ1": 0, "М1": 0},
            },
            {
                # --- завершение: ctrl_free после LZ ---
                "t": 3.0,
                "rc_states": {"10-12SP": 3, "1P": 7, "1-7SP": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 15, "НМ1": 3, "ЧМ1": 0, "М1": 0},
            },
        ],
    }

    options, steps = _build_steps_from_json(scenario_json)
    station = get_station_model_1p()
    timeline = simulate_1p(station, steps, dt=1.0, options=options)

    # отладка — удобно посмотреть при падении
    print("\n=== TIMELINE v13 ctrl=1-7SP ===")
    for i, st in enumerate(timeline):
        print(f"Step {i}: t={st.t}, variant={st.variant}, lz={st.lz_state}, flags={st.flags}")

    # ожидаем, что вариант 13 участвовал
    assert any("llz_v13" in st.flags for st in timeline)

    # хотя бы один шаг с ЛЗ и пометкой v13
    assert any(st.lz_state and "llz_v13" in st.flags for st in timeline)

    # и хотя бы один шаг с variant == 13
    assert 13 in [st.variant for st in timeline]

    # плюс явно проверяем открытие и закрытие
    assert any("llz_v13_open" in st.flags for st in timeline)
    assert any("llz_v13_closed" in st.flags for st in timeline)

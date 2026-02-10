# tests/test_variant12_1p.py

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


def test_variant12_scenario_prev_nc_for_10_12sp(tmp_path: Path):
    """
    Идеальный сценарий для ДС по ветке 12.1 (предыдущая не контролируется)
    для контролируемой РЦ 10-12SP.

    prev  = тупик со стороны 10-12SP (нет контролируемой смежной РЦ)
    curr  = 10-12SP (контролируемая v12)
    next  = 1P
    """

    scenario_json = {
        "options": {
            # v12 timings
            "t_s0112": 3.0,
            "t_s0212": 3.0,
            "t_lz12": 3.0,
            "t_kon_v12": 3.0,
            "enable_v12": True,
            # отключаем остальные варианты, чтобы не шумели
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
            "enable_v13": False,
            "enable_ls1": False,
            "enable_ls2": False,
            "enable_ls4": False,
            "enable_ls9": False,
        },
        "steps": [
            # Шаг 1 — фаза S0112 ветки 12.1:
            # prev NC (край со стороны 10-12SP, задаётся логикой simulate_1p),
            # curr занята (10-12SP = 7),
            # next свободна, замкнута (1P = 4)
            {
                "t": 3.0,
                "rc_states": {"10-12SP": 7, "1P": 4, "1-7SP": 4},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 0, "НМ1": 0, "ЧМ1": 0, "М1": 0},
            },
            # Шаг 2 — фаза S0212 ветки 12.1:
            # prev NC (край),
            # curr занята (10-12SP = 7),
            # next занята (1P = 7)
            {
                "t": 3.0,
                "rc_states": {"10-12SP": 7, "1P": 7, "1-7SP": 4},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 0, "НМ1": 0, "ЧМ1": 0, "М1": 0},
            },
            # Шаг 3 — фаза LZ12 ветки 12.1:
            # prev NC (край),
            # curr занята (10-12SP = 7),
            # next снова свободна (1P = 4)
            {
                "t": 3.0,
                "rc_states": {"10-12SP": 7, "1P": 4, "1-7SP": 4},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 0, "НМ1": 0, "ЧМ1": 0, "М1": 0},
            },
            # Шаг 4 — завершение ДС:
            # curr (10-12SP) освобождается (10-12SP = 4),
            # держим T_kon_v12 = 3.0
            {
                "t": 3.0,
                "rc_states": {"10-12SP": 4, "1P": 4, "1-7SP": 3},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 0, "НМ1": 0, "ЧМ1": 0, "М1": 0},
            },
        ],
    }

    options, steps = _build_steps_from_json(scenario_json)
    station = get_station_model_1p()
    timeline = simulate_1p(station, steps, dt=1.0, options=options)

    assert len(timeline) == 4
    variants = [st.variant for st in timeline]

    # Для конфигурации rc_has_route_lock["10-12SP"] = False
    # вариант 12 на 10-12SP НЕ должен формироваться вообще.

    # Ни на одном шаге не должно быть флагов v12
    assert all("llz_v12" not in st.flags for st in timeline)
    assert all("llz_v12_open" not in st.flags for st in timeline)
    assert all("llz_v12_closed" not in st.flags for st in timeline)

    # Ни один шаг не должен иметь variant == 12
    assert 12 not in variants

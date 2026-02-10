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


def test_variant12_scenario_next_nc_for_1_7sp_from_json(tmp_path: Path):
    """
    Идеальный сценарий для ДС по ветке 12.2 (следующая не контролируется)
    для контролируемой РЦ 1-7SP.

    prev = 1P
    curr = 1-7SP (контролируемая v12)
    next = край со стороны 1-7SP (нет смежной РЦ, next_nc=True по схеме)
    """

    scenario_json = {
        "options": {
            "t_s0101": 3,
            "t_lz01": 3,
            "t_kon_v1": 3,
            "t_pause_v1": 0,
            "enable_v1": False,
            "t_s0102": 3,
            "t_s0202": 3,
            "t_lz02": 3,
            "t_kon_v2": 3,
            "t_pause_v2": 0,
            "enable_v2": False,
            "t_s0103": 3,
            "t_s0203": 3,
            "t_lz03": 3,
            "t_kon_v3": 3,
            "t_pause_v3": 0,
            "enable_v3": False,
            "t_s0401": 0,
            "t_lz04": 0,
            "t_kon_v4": 0,
            "t_pause_v4": 0,
            "enable_v4": False,
            "t_s05": 0,
            "t_lz05": 0,
            "t_pk": 0,
            "t_kon_v5": 0,
            "t_pause_v5": 0,
            "enable_v5": False,
            "t_s06": 0,
            "t_lz06": 0,
            "t_kon_v6": 0,
            "t_pause_v6": 0,
            "enable_v6": False,
            "t_s07": 0,
            "t_lz07": 0,
            "t_kon_v7": 0,
            "t_pause_v7": 0,
            "enable_v7": False,
            "t_s0108": 0,
            "t_s0208": 0,
            "t_lz08": 0,
            "t_kon_v8": 0,
            "t_pause_v8": 0,
            "enable_v8": False,
            "t_s0109": 0,
            "t_lz09": 0,
            "t_kon_v9": 0,
            "t_pause_v9": 0,
            "enable_v9": False,
            "t_s0110": 0,
            "t_s0210": 0,
            "t_s0310": 0,
            "t_lz10": 0,
            "t_kon_v10": 0,
            "t_pause_v10": 0,
            "enable_v10": False,
            "t_s11": 0,
            "t_lz11": 0,
            "t_kon_v11": 0,
            "t_pause_v11": 0,
            "enable_v11": False,
            # v12
            "t_s0112": 3,
            "t_s0212": 3,
            "t_lz12": 3,
            "t_kon_v12": 3,
            "t_pause_v12": 0,
            "enable_v12": True,
            # v13
            "t_s0113": 3,
            "t_s0213": 3,
            "t_lz13": 3,
            "t_kon_v13": 3,
            "t_pause_v13": 0,
            "enable_v13": False,
            "v13_ctrl_rc_id": "10-12SP",
            # LS (выключены по факту таймингов=0, но явно не мешают)
            "t_c0101_ls": 0,
            "t_ls01": 0,
            "t_kon_ls1": 0,
            "t_pause_ls1": 0,
            "enable_ls1": True,
            "t_s0102_ls": 0,
            "t_s0202_ls": 0,
            "t_ls0102": 0,
            "t_ls0202": 0,
            "t_kon_ls2": 0,
            "t_pause_ls2": 0,
            "enable_ls2": True,
            "t_s0104_ls": 0,
            "t_s0204_ls": 0,
            "t_ls0104": 0,
            "t_ls0204": 0,
            "t_kon_ls4": 0,
            "t_pause_ls4": 0,
            "enable_ls4": True,
            "t_s0109_ls": 0,
            "t_s0209_ls": 0,
            "t_ls0109": 0,
            "t_ls0209": 0,
            "t_kon_ls9": 0,
            "t_pause_ls9": 0,
            "enable_ls9": True,
            # исключения
            "t_mu": 0,
            "t_recent_ls": 0,
            "t_min_maneuver_v8": 0,
            "enable_lz_exc_mu": True,
            "enable_lz_exc_recent_ls": True,
            "enable_lz_exc_dsp": True,
            "t_ls_mu": 0,
            "t_ls_after_lz": 0,
            "t_ls_dsp": 0,
            "enable_ls_exc_mu": True,
            "enable_ls_exc_after_lz": True,
            "enable_ls_exc_dsp": True,
        },
        "steps": [
            # Шаг 1 — фаза S0112 ветки 12.2:
            # prev свободна (1P = 4), curr занята (1-7SP = 7),
            # next NC по схеме (край со стороны 1-7SP, задаётся simulate_1p)
            {
                "t": 3,
                "rc_states": {"10-12SP": 4, "1P": 4, "1-7SP": 7},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 0, "НМ1": 0, "ЧМ1": 0, "М1": 0},
            },
            # Шаг 2 — фаза S0212 ветки 12.2:
            # prev занята (1P = 7), curr занята (1-7SP = 7),
            # next всё так же NC по схеме
            {
                "t": 3,
                "rc_states": {"10-12SP": 4, "1P": 7, "1-7SP": 7},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 0, "НМ1": 0, "ЧМ1": 0, "М1": 0},
            },
            # Шаг 3 — фаза LZ12 ветки 12.2:
            # prev снова свободна (1P = 4), curr занята (1-7SP = 7),
            # next по-прежнему NC по схеме
            {
                "t": 3,
                "rc_states": {"10-12SP": 4, "1P": 4, "1-7SP": 7},
                "switch_states": {"Sw10": 3, "Sw1": 3, "Sw5": 3},
                "modes": {},
                "mu": {"10-12SP": 3, "1P": 3, "1-7SP": 3},
                "dispatcher_control_state": 4,
                "auto_actions": {"NAS": 4, "CHAS": 4},
                "signal_states": {"Ч1": 0, "НМ1": 0, "ЧМ1": 0, "М1": 0},
            },
            # Шаг 4 — завершение ДС:
            # curr (1-7SP) освобождается (1-7SP = 3), выдерживаем T_kon_v12 = 3
            {
                "t": 3,
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

    # Вариант 12 должен участвовать
    assert any("llz_v12" in st.flags for st in timeline)

    # На каком-то шаге должна быть ЛЗ с пометкой v12
    assert any(st.lz_state and "llz_v12" in st.flags for st in timeline)

    # Хотя бы один шаг с variant == 12
    assert 12 in variants

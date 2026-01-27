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


def test_ls_variant6_not_formed_on_1012_without_route_lock(tmp_path: Path) -> None:
    """
    ЛС6 не должна формироваться на 10-12SP,
    т.к. rc_has_route_lock['10-12SP'] = False.
    """

    scenario_json = {
        "options": {
            # все ЛЗ-детекторы выключены
            "t_s0101": 0,
            "t_lz01": 0,
            "t_kon_v1": 0,
            "t_pause_v1": 0,
            "enable_v1": False,
            "t_s0102": 0,
            "t_s0202": 0,
            "t_lz02": 0,
            "t_kon_v2": 0,
            "t_pause_v2": 0,
            "enable_v2": False,
            "t_s0103": 0,
            "t_s0203": 0,
            "t_lz03": 0,
            "t_kon_v3": 0,
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
            "t_s0112": 0,
            "t_s0212": 0,
            "t_lz12": 0,
            "t_kon_v12": 0,
            "t_pause_v12": 0,
            "enable_v12": False,
            "t_s0113": 0,
            "t_s0213": 0,
            "t_lz13": 0,
            "t_kon_v13": 0,
            "t_pause_v13": 0,
            "enable_v13": False,
            # все ЛС, кроме ЛС6, по нулям
            "t_c0101_ls": 0,
            "t_ls01": 0,
            "t_kon_ls1": 0,
            "t_pause_ls1": 0,
            "enable_ls1": False,
            "t_s0102_ls": 0,
            "t_s0202_ls": 0,
            "t_ls0102": 0,
            "t_ls0202": 0,
            "t_kon_ls2": 0,
            "t_pause_ls2": 0,
            "enable_ls2": False,
            "t_s0104_ls": 0,
            "t_s0204_ls": 0,
            "t_ls0104": 0,
            "t_ls0204": 0,
            "t_kon_ls4": 0,
            "t_pause_ls4": 0,
            "enable_ls4": False,
            "t_s0105_ls": 0,
            "t_ls05": 0,
            "t_kon_ls5": 0,
            "t_pause_ls5": 0,
            "enable_ls5": False,
            "t_s0109_ls": 0,
            "t_s0209_ls": 0,
            "t_ls0109": 0,
            "t_ls0209": 0,
            "t_kon_ls9": 0,
            "t_pause_ls9": 0,
            "enable_ls9": False,
            # включаем только ЛС6
            "t_s0106_ls": 3,
            "t_ls06": 3,
            "t_kon_ls6": 3,
            "t_pause_ls6": 0,
            "enable_ls6": True,
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
            {
                "t": 3,
                "rc_states": {
                    "10-12SP": 4,
                    "1P": 4,
                    "1-7SP": 4,
                },
                "switch_states": {
                    "Sw10": 3,
                    "Sw1": 3,
                    "Sw5": 3,
                },
                "modes": {},
                "mu": {
                    "10-12SP": 3,
                    "1P": 3,
                    "1-7SP": 3,
                },
                "dispatcher_control_state": 4,
                "auto_actions": {
                    "NAS": 4,
                    "CHAS": 4,
                },
                "signal_states": {
                    "Ч1": 0,
                    "НМ1": 0,
                    "ЧМ1": 0,
                    "М1": 4,
                },
            },
            {
                "t": 3,
                "rc_states": {
                    "10-12SP": 4,
                    "1P": 7,
                    "1-7SP": 7,
                },
                "switch_states": {
                    "Sw10": 3,
                    "Sw1": 3,
                    "Sw5": 3,
                },
                "modes": {},
                "mu": {
                    "10-12SP": 3,
                    "1P": 3,
                    "1-7SP": 3,
                },
                "dispatcher_control_state": 4,
                "auto_actions": {
                    "NAS": 4,
                    "CHAS": 4,
                },
                "signal_states": {
                    "Ч1": 0,
                    "НМ1": 0,
                    "ЧМ1": 0,
                    "М1": 0,
                },
            },
            {
                "t": 3,
                "rc_states": {
                    "10-12SP": 7,
                    "1P": 7,
                    "1-7SP": 7,
                },
                "switch_states": {
                    "Sw10": 3,
                    "Sw1": 3,
                    "Sw5": 3,
                },
                "modes": {},
                "mu": {
                    "10-12SP": 3,
                    "1P": 3,
                    "1-7SP": 3,
                },
                "dispatcher_control_state": 4,
                "auto_actions": {
                    "NAS": 4,
                    "CHAS": 4,
                },
                "signal_states": {
                    "Ч1": 0,
                    "НМ1": 0,
                    "ЧМ1": 0,
                    "М1": 0,
                },
            },
        ],
    }

    options, steps = _build_steps_from_json(scenario_json)
    station = get_station_model_1p()
    timeline = simulate_1p(station, steps, dt=1.0, options=options)

    # фильтруем по контролируемой РЦ 10-12SP
    steps_for_1012 = [st for st in timeline if st.ctrl_rc_id == "10-12SP"]

    for st in steps_for_1012:
        assert all(
            f not in st.flags for f in ("lls_v6", "lls_v6_open", "lls_v6_closed")
        ), f"LS6 сформировалась на 10-12SP: {st.flags}"

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
try:
    from .station_layout import build_station_layout
except ImportError:
    from station_layout import build_station_layout


ROOT_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT_DIR / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from tools.station.station_config import NODES
from tools.station.station_rc_sections import RC_SECTIONS
from api.contract import run_simulation_contract
from api.sim.helpers import (
    ID_TO_NAME,
    LEGACY_TO_CANONICAL_OPTION_KEYS,
    _build_detectors_config,
    _canonicalize_options,
    _convert_rc_states,
    _convert_signal_states,
    _convert_switch_states,
    _fix_mojibake,
    _parse_flag,
    _resolve_rc_id,
    _states_ids_to_names,
    _to_float,
)


FRONTEND_DIR = ROOT_DIR / "frontend"
TESTS_DIR = FRONTEND_DIR / "tests"
TESTS_DIR.mkdir(parents=True, exist_ok=True)
XML_DIR = ROOT_DIR / "xml"
EXCEPTIONS_CONFIG_PATH = TOOLS_DIR / "exceptions" / "exceptions_objects.json"
_LAYOUT_CACHE: Dict[str, Dict[str, Any]] = {}
API_BUILD = "2026-02-11-layout-catalog-v2"

DEFAULT_OPTIONS: Dict[str, Any] = {
    "t_pk": 30.0,
    "t_s0101": 3.0, "t_lz01": 3.0, "t_kon_v1": 3.0, "t_pause_v1": 0.0, "enable_v1": True,
    "t_s0102": 3.0, "t_s0202": 3.0, "t_lz02": 3.0, "t_kon_v2": 3.0, "t_pause_v2": 0.0, "enable_v2": True,
    "t_s0103": 3.0, "t_s0203": 3.0, "t_lz03": 3.0, "t_kon_v3": 3.0, "t_pause_v3": 0.0, "enable_v3": True,
    "t_s0401": 3.0, "t_lz04": 3.0, "t_kon_v4": 3.0, "t_pause_v4": 0.0, "enable_v4": True,
    "t_s05": 3.0, "t_lz05": 3.0, "t_kon_v5": 3.0, "t_pause_v5": 0.0, "enable_v5": False,
    "t_s06": 3.0, "t_lz06": 3.0, "t_kon_v6": 3.0, "t_pause_v6": 0.0, "enable_v6": False,
    "t_s07": 3.0, "t_lz07": 3.0, "t_kon_v7": 3.0, "t_pause_v7": 0.0, "enable_v7": True,
    "t_s0108": 3.0, "t_s0208": 3.0, "t_lz08": 3.0, "t_kon_v8": 3.0, "t_pause_v8": 0.0, "enable_v8": True,
    "t_s0109": 3.0, "t_lz09": 3.0, "t_kon_v9": 3.0, "t_pause_v9": 0.0, "enable_v9": True,
    "t_s0110": 3.0, "t_s0210": 3.0, "t_s0310": 3.0, "t_lz10": 3.0, "t_kon_v10": 3.0, "t_pause_v10": 0.0, "enable_v10": True,
    "t_s11": 3.0, "t_lz11": 3.0, "t_kon_v11": 3.0, "t_pause_v11": 0.0, "enable_v11": True,
    "t_s0112": 3.0, "t_s0212": 3.0, "t_lz12": 3.0, "t_kon_v12": 3.0, "t_pause_v12": 0.0, "enable_v12": True,
    "t_s0113": 3.0, "t_s0213": 3.0, "t_lz13": 3.0, "t_kon_v13": 3.0, "t_pause_v13": 0.0, "enable_v13": True,
    "sig_lz4_prev_to_ctrl": "", "sig_lz4_ctrl_to_next": "",
    "sig_lz10_to_next": "", "sig_lz10_to_prev": "",
    "sig_lz11_a": "", "sig_lz11_b": "",
    "sig_lz13_prev": "", "sig_lz13_next": "",
    "t_c0101_ls": 3.0, "t_ls01": 3.0, "t_kon_ls1": 3.0, "t_pause_ls1": 0.0, "enable_ls1": True,
    "t_s0102_ls": 3.0, "t_s0202_ls": 3.0, "t_ls0102": 3.0, "t_kon_ls2": 3.0, "t_pause_ls2": 0.0, "enable_ls2": True,
    "t_s0104_ls": 3.0, "t_s0204_ls": 3.0, "t_ls0104": 3.0, "t_ls0204": 10.0, "t_kon_ls4": 3.0, "t_pause_ls4": 0.0, "enable_ls4": True,
    "t_s0105_ls": 3.0, "t_ls05": 3.0, "t_kon_ls5": 3.0, "t_pause_ls5": 0.0, "enable_ls5": True,
    "t_s0106_ls": 3.0, "t_ls06": 3.0, "t_kon_ls6": 3.0, "t_pause_ls6": 0.0, "enable_ls6": True,
    "sig_ls6_prev": "",
    "t_s0109_ls": 3.0, "t_s0209_ls": 3.0, "t_ls0109": 3.0, "t_ls0209": 10.0, "t_kon_ls9": 3.0, "t_pause_ls9": 0.0, "enable_ls9": True,
    "t_mu": 15.0, "t_recent_ls": 30.0, "t_min_maneuver_v8": 600.0,
    "enable_lz_exc_mu": True, "enable_lz_exc_recent_ls": True, "enable_lz_exc_dsp": True,
    "lz_exc_dsp_variants": [],
    "t_ls_mu": 15.0, "t_ls_after_lz": 30.0, "t_ls_dsp": 600.0,
    "enable_ls_exc_mu": True, "enable_ls_exc_after_lz": True, "enable_ls_exc_dsp": True,
}


from api.routes import (
    register_layout_routes,
    register_simulate_routes,
    register_system_routes,
    register_tests_routes,
)

app = FastAPI(title="RC Diagnosis MVP")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")
app.mount("/xml-json", StaticFiles(directory=ROOT_DIR / "xml" / "Json"), name="xml-json")
app.mount("/xml", StaticFiles(directory=ROOT_DIR / "xml"), name="xml")

_ROUTE_CTX: Dict[str, Any] = {
    "ROOT_DIR": ROOT_DIR,
    "FRONTEND_DIR": FRONTEND_DIR,
    "TESTS_DIR": TESTS_DIR,
    "XML_DIR": XML_DIR,
    "EXCEPTIONS_CONFIG_PATH": EXCEPTIONS_CONFIG_PATH,
    "_LAYOUT_CACHE": _LAYOUT_CACHE,
    "API_BUILD": API_BUILD,
    "NODES": NODES,
    "RC_SECTIONS": RC_SECTIONS,
    "DEFAULT_OPTIONS": DEFAULT_OPTIONS,
    "LEGACY_TO_CANONICAL_OPTION_KEYS": LEGACY_TO_CANONICAL_OPTION_KEYS,
    "build_station_layout": build_station_layout,
    "run_simulation_contract": run_simulation_contract,
    "_fix_mojibake": _fix_mojibake,
    "_canonicalize_options": _canonicalize_options,
    "_resolve_rc_id": _resolve_rc_id,
    "_build_detectors_config": _build_detectors_config,
    "_to_float": _to_float,
    "_convert_rc_states": _convert_rc_states,
    "_convert_switch_states": _convert_switch_states,
    "_convert_signal_states": _convert_signal_states,
    "_parse_flag": _parse_flag,
    "_states_ids_to_names": _states_ids_to_names,
    "ID_TO_NAME": ID_TO_NAME,
}

register_system_routes(app, _ROUTE_CTX)
register_layout_routes(app, _ROUTE_CTX)
register_simulate_routes(app, _ROUTE_CTX)
register_tests_routes(app, _ROUTE_CTX)

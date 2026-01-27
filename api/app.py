from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import json
import os
from datetime import datetime

from engine.station_visochino_1p import (
    get_station_model_1p,
    get_station_model_17_ctrl,
    get_station_model_1012_ctrl,
)
from engine.simulate_1p import ScenarioStep, simulate_1p, TimelineStep
from engine.config_1p import (
    T_S0101,
    T_LZ01,
    T_KON,
    T_S0102_DEFAULT,
    T_S0202_DEFAULT,
    T_LZ02_DEFAULT,
    T_S0103_DEFAULT,
    T_S0203_DEFAULT,
    T_LZ03_DEFAULT,
    T_S0401_DEFAULT,
    T_LZ04_DEFAULT,
    T_KON_V4_DEFAULT,
    T_S05_DEFAULT,
    T_LZ05_DEFAULT,
    T_KON_V5_DEFAULT,
    T_S06_DEFAULT,
    T_LZ06_DEFAULT,
    T_KON_V6_DEFAULT,
    T_S07_DEFAULT,
    T_LZ07_DEFAULT,
    T_KON_V7_DEFAULT,
    T_S0108_DEFAULT,
    T_S0208_DEFAULT,
    T_LZ08_DEFAULT,
    T_S0109_DEFAULT,
    T_LZ09_DEFAULT,
    T_KON_V9_DEFAULT,
    TS0110_DEFAULT,
    TS0210_DEFAULT,
    TS0310_DEFAULT,
    TLZ10_DEFAULT,
    TKON_V10_DEFAULT,
    T_S11_DEFAULT,
    T_LZ11_DEFAULT,
    T_KON_V11_DEFAULT,
    T_S0112_DEFAULT,
    T_S0212_DEFAULT,
    T_LZ12_DEFAULT,
    T_KON_V12_DEFAULT,
    T_S0113_DEFAULT,
    T_S0213_DEFAULT,
    T_LZ13_DEFAULT,
    T_KON_V13_DEFAULT,
    T_C0101_LS_DEFAULT,
    T_LS01_DEFAULT,
    T_KON_LS_DEFAULT,
    T_S0102_LS_DEFAULT,
    T_S0202_LS_DEFAULT,
    T_LS0102_DEFAULT,
    T_LS0202_DEFAULT,
    T_KON_LS2_DEFAULT,
    T_S0104_LS_DEFAULT,
    T_S0204_LS_DEFAULT,
    T_LS0104_DEFAULT,
    T_LS0204_DEFAULT,
    T_KON_LS4_DEFAULT,
    T_S0105_LS_DEFAULT,
    T_LS05_DEFAULT,
    T_KON_LS5_DEFAULT,
    T_S0106_LS_DEFAULT,
    T_LS06_DEFAULT,
    T_KON_LS6_DEFAULT,
    T_S0109_LS_DEFAULT,
    T_S0209_LS_DEFAULT,
    T_LS0109_DEFAULT,
    T_LS0209_DEFAULT,
    T_KON_LS9_DEFAULT,
    T_PAUSE_DEFAULT,
    T_MU,
    T_RECENT_LS,
    T_MIN_MANEUVER_V8,
    T_LS_MU,
    T_LS_AFTER_LZ,
    T_LS_DSP,
    T_PK,
)

ALLOWED_CTRL_RCS = {"1P", "1-7SP", "10-12SP"}


def get_station_for_target_rc(target_rc: str):
    if target_rc == "1P":
        return get_station_model_1p()
    if target_rc == "1-7SP":
        return get_station_model_17_ctrl()
    if target_rc == "10-12SP":
        return get_station_model_1012_ctrl()
    # по умолчанию — 1P
    return get_station_model_1p()


app = FastAPI(title="RC Diagnosis MVP")


# --- Pydantic-модели для JSON ---


class ScenarioStepIn(BaseModel):
    t: float
    rc_states: Dict[str, int] = {}
    switch_states: Dict[str, int] = {}
    modes: Dict[str, Any] = {}
    # новые поля управления
    mu: Dict[str, int] = {}
    dispatcher_control_state: int | None = None
    auto_actions: Dict[str, int] = {}
    # НОВОЕ: состояния светофоров (универсальные Uni_State_ID по имени светофора)
    signal_states: Dict[str, int] = {}


class ScenarioOptionsIn(BaseModel):
    # Вариант 1 ЛЗ
    t_s0101: int | float = T_S0101
    t_lz01: int | float = T_LZ01
    t_kon_v1: int | float = T_KON
    t_pause_v1: int | float = T_PAUSE_DEFAULT
    enable_v1: bool = True

    # Вариант 2 ЛЗ
    t_s0102: int | float = T_S0102_DEFAULT
    t_s0202: int | float = T_S0202_DEFAULT
    t_lz02: int | float = T_LZ02_DEFAULT
    t_kon_v2: int | float = T_KON
    t_pause_v2: int | float = T_PAUSE_DEFAULT
    enable_v2: bool = True

    # Вариант 3 ЛЗ
    t_s0103: int | float = T_S0103_DEFAULT
    t_s0203: int | float = T_S0203_DEFAULT
    t_lz03: int | float = T_LZ03_DEFAULT
    t_kon_v3: int | float = T_KON
    t_pause_v3: int | float = T_PAUSE_DEFAULT
    enable_v3: bool = True

    # Вариант 4 ЛЗ
    t_s0401: int | float = T_S0401_DEFAULT
    t_lz04: int | float = T_LZ04_DEFAULT
    t_kon_v4: int | float = T_KON_V4_DEFAULT
    t_pause_v4: int | float = T_PAUSE_DEFAULT
    enable_v4: bool = False

    # Вариант 5 ЛЗ
    t_s05: int | float = T_S05_DEFAULT
    t_lz05: int | float = T_LZ05_DEFAULT
    t_kon_v5: int | float = T_KON_V5_DEFAULT
    t_pause_v5: int | float = T_PAUSE_DEFAULT
    enable_v5: bool = False

    # Вариант 6 ЛЗ (одноРЦ без замыкания)
    t_s06: int | float = T_S06_DEFAULT
    t_lz06: int | float = T_LZ06_DEFAULT
    t_kon_v6: int | float = T_KON_V6_DEFAULT
    t_pause_v6: int | float = T_PAUSE_DEFAULT
    enable_v6: bool = True

    # Вариант 7 ЛЗ
    t_s07: int | float = T_S07_DEFAULT
    t_lz07: int | float = T_LZ07_DEFAULT
    t_kon_v7: int | float = T_KON_V7_DEFAULT
    t_pause_v7: int | float = T_PAUSE_DEFAULT
    enable_v7: bool = False

    # Вариант 8 ЛЗ
    t_s0108: int | float = T_S0108_DEFAULT
    t_s0208: int | float = T_S0208_DEFAULT
    t_lz08: int | float = T_LZ08_DEFAULT
    t_kon_v8: int | float = T_KON
    t_pause_v8: int | float = T_PAUSE_DEFAULT
    enable_v8: bool = True

    # Вариант 9 ЛЗ
    t_s0109: int | float = T_S0109_DEFAULT
    t_lz09: int | float = T_LZ09_DEFAULT
    t_kon_v9: int | float = T_KON_V9_DEFAULT
    t_pause_v9: int | float = T_PAUSE_DEFAULT
    enable_v9: bool = False

    # Вариант 10 ЛЗ
    t_s0110: int | float = TS0110_DEFAULT
    t_s0210: int | float = TS0210_DEFAULT
    t_s0310: int | float = TS0310_DEFAULT
    t_lz10: int | float = TLZ10_DEFAULT
    t_kon_v10: int | float = TKON_V10_DEFAULT
    t_pause_v10: int | float = T_PAUSE_DEFAULT
    enable_v10: bool = False

    # Вариант 11 ЛЗ (по светофорам)
    t_s11: int | float = T_S11_DEFAULT
    t_lz11: int | float = T_LZ11_DEFAULT
    t_kon_v11: int | float = T_KON_V11_DEFAULT
    t_pause_v11: int | float = T_PAUSE_DEFAULT
    enable_v11: bool = False

    # Вариант 12 ЛЗ
    t_s0112: int | float = T_S0112_DEFAULT
    t_s0212: int | float = T_S0212_DEFAULT
    t_lz12: int | float = T_LZ12_DEFAULT
    t_kon_v12: int | float = T_KON_V12_DEFAULT
    t_pause_v12: int | float = T_PAUSE_DEFAULT
    enable_v12: bool = False

    # Вариант 13 ЛЗ
    t_s0113: int | float = T_S0113_DEFAULT
    t_s0213: int | float = T_S0213_DEFAULT
    t_lz13: int | float = T_LZ13_DEFAULT
    t_kon_v13: int | float = T_KON_V13_DEFAULT
    t_pause_v13: int | float = T_PAUSE_DEFAULT
    enable_v13: bool = False

    # Вариант 1 ЛС
    t_c0101_ls: int | float = T_C0101_LS_DEFAULT
    t_ls01: int | float = T_LS01_DEFAULT
    t_kon_ls1: int | float = T_KON_LS_DEFAULT
    t_pause_ls1: int | float = T_PAUSE_DEFAULT
    enable_ls1: bool = True

    # Вариант 2 ЛС
    t_s0102_ls: int | float = T_S0102_LS_DEFAULT
    t_s0202_ls: int | float = T_S0202_LS_DEFAULT
    t_ls0102: int | float = T_LS0102_DEFAULT
    t_ls0202: int | float = T_LS0202_DEFAULT
    t_kon_ls2: int | float = T_KON_LS2_DEFAULT
    t_pause_ls2: int | float = T_PAUSE_DEFAULT
    enable_ls2: bool = True

    # Вариант 4 ЛС
    t_s0104_ls: int | float = T_S0104_LS_DEFAULT
    t_s0204_ls: int | float = T_S0204_LS_DEFAULT
    t_ls0104: int | float = T_LS0104_DEFAULT
    t_ls0204: int | float = T_LS0204_DEFAULT
    t_kon_ls4: int | float = T_KON_LS4_DEFAULT
    t_pause_ls4: int | float = T_PAUSE_DEFAULT
    enable_ls4: bool = True

    # Вариант 5 ЛС
    t_s0105_ls: int | float = T_S0105_LS_DEFAULT
    t_ls05: int | float = T_LS05_DEFAULT
    t_kon_ls5: int | float = T_KON_LS5_DEFAULT
    t_pause_ls5: int | float = T_PAUSE_DEFAULT
    enable_ls5: bool = True

    # Вариант 6 ЛС
    t_s0106_ls: int | float = T_S0106_LS_DEFAULT
    t_ls06: int | float = T_LS06_DEFAULT
    t_kon_ls6: int | float = T_KON_LS6_DEFAULT
    t_pause_ls6: int | float = T_PAUSE_DEFAULT
    enable_ls6: bool = True


    # Вариант 9 ЛС
    t_s0109_ls: int | float = T_S0109_LS_DEFAULT
    t_s0209_ls: int | float = T_S0209_LS_DEFAULT
    t_ls0109: int | float = T_LS0109_DEFAULT
    t_ls0209: int | float = T_LS0209_DEFAULT
    t_kon_ls9: int | float = T_KON_LS9_DEFAULT
    t_pause_ls9: int | float = T_PAUSE_DEFAULT
    enable_ls9: bool = True

    # Исключения ЛЗ
    t_mu: int | float = T_MU
    t_recent_ls: int | float = T_RECENT_LS
    t_min_maneuver_v8: int | float = T_MIN_MANEUVER_V8

    # Включение/выключение исключений ЛЗ
    enable_lz_exc_mu: bool = True
    enable_lz_exc_recent_ls: bool = True
    enable_lz_exc_dsp: bool = True

    # Исключения ЛС: тайминги
    t_ls_mu: int | float = T_LS_MU
    t_ls_after_lz: int | float = T_LS_AFTER_LZ
    t_ls_dsp: int | float = T_LS_DSP

    # Включение/выключение исключений ЛС
    enable_ls_exc_mu: bool = True
    enable_ls_exc_after_lz: bool = True
    enable_ls_exc_dsp: bool = True


class ScenarioIn(BaseModel):
    station: str = "Visochino"
    target_rc: str = "1P"
    dt: float = 1.0
    options: ScenarioOptionsIn | None = None
    steps: List[ScenarioStepIn]


class TimelineStepOut(BaseModel):
    t: float
    step_duration: float
    lz_state: bool
    variant: int
    effective_prev_rc: str
    effective_next_rc: str
    flags: List[str]
    rc_states: Dict[str, int]
    switch_states: Dict[str, int]
    # НОВОЕ: состояния светофоров по шагу
    signal_states: Dict[str, int] = {}
    # новые поля для визуализации станции
    mu_state: int | None = None
    nas_state: int | None = None
    chas_state: int | None = None
    dsp_state: int | None = None


# --- Фронтенд и статика ---
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
TESTS_DIR = FRONTEND_DIR / "tests"
TESTS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("... index.html not found", status_code=500)
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


@app.get("/defaults")
def get_defaults() -> Dict[str, Any]:
    return {
        # ЛЗ v1
        "t_s0101": T_S0101,
        "t_lz01": T_LZ01,
        "t_kon_v1": T_KON,
        "t_pause_v1": T_PAUSE_DEFAULT,
        "enable_v1": True,
        # ЛЗ v2
        "t_s0102": T_S0102_DEFAULT,
        "t_s0202": T_S0202_DEFAULT,
        "t_lz02": T_LZ02_DEFAULT,
        "t_kon_v2": T_KON,
        "t_pause_v2": T_PAUSE_DEFAULT,
        "enable_v2": True,
        # ЛЗ v3
        "t_s0103": T_S0103_DEFAULT,
        "t_s0203": T_S0203_DEFAULT,
        "t_lz03": T_LZ03_DEFAULT,
        "t_kon_v3": T_KON,
        "t_pause_v3": T_PAUSE_DEFAULT,
        "enable_v3": True,
        # ЛЗ v4
        "t_s0401": T_S0401_DEFAULT,
        "t_lz04": T_LZ04_DEFAULT,
        "t_kon_v4": T_KON_V4_DEFAULT,
        "t_pause_v4": T_PAUSE_DEFAULT,
        "enable_v4": True,
        # ЛЗ v5
        "t_s05": T_S05_DEFAULT,
        "t_lz05": T_LZ05_DEFAULT,
        "t_kon_v5": T_KON_V5_DEFAULT,
        "t_pause_v5": T_PAUSE_DEFAULT,
        "enable_v5": False,
        # ЛЗ v6
        "t_s06": T_S06_DEFAULT,
        "t_lz06": T_LZ06_DEFAULT,
        "t_kon_v6": T_KON_V6_DEFAULT,
        "enable_v6": False,
        # ЛЗ v7
        "t_s07": T_S07_DEFAULT,
        "t_lz07": T_LZ07_DEFAULT,
        "t_kon_v7": T_KON_V7_DEFAULT,
        "t_pause_v7": T_PAUSE_DEFAULT,
        "enable_v7": True,
        # ЛЗ v8
        "t_s0108": T_S0108_DEFAULT,
        "t_s0208": T_S0208_DEFAULT,
        "t_lz08": T_LZ08_DEFAULT,
        "t_kon_v8": T_KON,
        "t_pause_v8": T_PAUSE_DEFAULT,
        "enable_v8": True,
        # ЛЗ v9
        "t_s0109": T_S0109_DEFAULT,
        "t_lz09": T_LZ09_DEFAULT,
        "t_kon_v9": T_KON_V9_DEFAULT,
        "t_pause_v9": T_PAUSE_DEFAULT,
        "enable_v9": True,
        # ЛЗ v10
        "t_s0110": TS0110_DEFAULT,
        "t_s0210": TS0210_DEFAULT,
        "t_s0310": TS0310_DEFAULT,
        "t_lz10": TLZ10_DEFAULT,
        "t_kon_v10": TKON_V10_DEFAULT,
        "t_pause_v10": T_PAUSE_DEFAULT,
        "enable_v10": True,
        # ЛЗ v11
        "t_s11": T_S11_DEFAULT,
        "t_lz11": T_LZ11_DEFAULT,
        "t_kon_v11": T_KON_V11_DEFAULT,
        "t_pause_v11": T_PAUSE_DEFAULT,
        "enable_v11": True,
        # ЛЗ v12
        "t_s0112": T_S0112_DEFAULT,
        "t_s0212": T_S0212_DEFAULT,
        "t_lz12": T_LZ12_DEFAULT,
        "t_kon_v12": T_KON_V12_DEFAULT,
        "t_pause_v12": T_PAUSE_DEFAULT,
        "enable_v12": True,
        # ЛЗ v13
        "t_s0113": T_S0113_DEFAULT,
        "t_s0213": T_S0213_DEFAULT,
        "t_lz13": T_LZ13_DEFAULT,
        "t_kon_v13": T_KON_V13_DEFAULT,
        "t_pause_v13": T_PAUSE_DEFAULT,
        "enable_v13": True,
        "v13_ctrl_rc_id": "10-12SP",
        # ЛС v1
        "t_c0101_ls": T_C0101_LS_DEFAULT,
        "t_ls01": T_LS01_DEFAULT,
        "t_kon_ls1": T_KON_LS_DEFAULT,
        "t_pause_ls1": T_PAUSE_DEFAULT,
        "enable_ls1": True,
        # ЛС v2
        "t_s0102_ls": T_S0102_LS_DEFAULT,
        "t_s0202_ls": T_S0202_LS_DEFAULT,
        "t_ls0102": T_LS0102_DEFAULT,
        "t_ls0202": T_LS0202_DEFAULT,
        "t_kon_ls2": T_KON_LS2_DEFAULT,
        "t_pause_ls2": T_PAUSE_DEFAULT,
        "enable_ls2": True,
        # ЛС v4
        "t_s0104_ls": T_S0104_LS_DEFAULT,
        "t_s0204_ls": T_S0204_LS_DEFAULT,
        "t_ls0104": T_LS0104_DEFAULT,
        "t_ls0204": T_LS0204_DEFAULT,
        "t_kon_ls4": T_KON_LS4_DEFAULT,
        "t_pause_ls4": T_PAUSE_DEFAULT,
        "enable_ls4": True,
        # ЛС v5
        "t_s0105_ls": T_S0105_LS_DEFAULT,
        "t_ls05": T_LS05_DEFAULT,
        "t_kon_ls5":T_KON_LS5_DEFAULT,
        "t_pause_ls5": T_PAUSE_DEFAULT,
        "enable_ls5": True,
        # ЛС v6
        "t_s0106_ls": T_S0106_LS_DEFAULT,
        "t_ls06": T_LS06_DEFAULT,
        "t_kon_ls6": T_KON_LS6_DEFAULT,
        "t_pause_ls6": T_PAUSE_DEFAULT,
        "enable_ls6": True,
        # ЛС v9
        "t_s0109_ls": T_S0109_LS_DEFAULT,
        "t_s0209_ls": T_S0209_LS_DEFAULT,
        "t_ls0109": T_LS0109_DEFAULT,
        "t_ls0209": T_LS0209_DEFAULT,
        "t_kon_ls9": T_KON_LS9_DEFAULT,
        "t_pause_ls9": T_PAUSE_DEFAULT,
        "enable_ls9": True,
        # Исключения ЛЗ
        "t_mu": T_MU,
        "t_recent_ls": T_RECENT_LS,
        "t_min_maneuver_v8": T_MIN_MANEUVER_V8,
        "enable_lz_exc_mu": True,
        "enable_lz_exc_recent_ls": True,
        "enable_lz_exc_dsp": True,
        # Исключения ЛС
        "t_ls_mu": T_LS_MU,
        "t_ls_after_lz": T_LS_AFTER_LZ,
        "t_ls_dsp": T_LS_DSP,
        "enable_ls_exc_mu": True,
        "enable_ls_exc_after_lz": True,
        "enable_ls_exc_dsp": True,
    }


@app.post("/simulate", response_model=List[TimelineStepOut])
def simulate_endpoint(scenario: ScenarioIn):
    # 1. Больше не опираемся на target_rc для выбора модели
    #    Всегда используем базовую модель 1P — детекторы внутри уже навешены на нужные РЦ
    station = get_station_model_1p()

    steps_internal: List[ScenarioStep] = []
    for s in scenario.steps:
        steps_internal.append(
            ScenarioStep(
                t=float(s.t),
                rc_states=dict(s.rc_states),
                switch_states=dict(s.switch_states),
                modes=dict(s.modes),
                mu=dict(s.mu),
                dispatcher_control_state=s.dispatcher_control_state,
                auto_actions=dict(s.auto_actions),
                signal_states=dict(getattr(s, "signal_states", {}) or {}),
            )
        )

    opt_in = scenario.options
    if opt_in is not None:
        options: Dict[str, Any] = {
            # ЛЗ v1
            "t_s0101": float(opt_in.t_s0101),
            "t_lz01": float(opt_in.t_lz01),
            "t_kon_v1": float(opt_in.t_kon_v1),
            "t_pause_v1": float(opt_in.t_pause_v1),
            "enable_v1": bool(opt_in.enable_v1),
            # ЛЗ v2
            "t_s0102": float(opt_in.t_s0102),
            "t_s0202": float(opt_in.t_s0202),
            "t_lz02": float(opt_in.t_lz02),
            "t_kon_v2": float(opt_in.t_kon_v2),
            "t_pause_v2": float(opt_in.t_pause_v2),
            "enable_v2": bool(opt_in.enable_v2),
            # ЛЗ v3
            "t_s0103": float(opt_in.t_s0103),
            "t_s0203": float(opt_in.t_s0203),
            "t_lz03": float(opt_in.t_lz03),
            "t_kon_v3": float(opt_in.t_kon_v3),
            "t_pause_v3": float(opt_in.t_pause_v3),
            "enable_v3": bool(opt_in.enable_v3),
            # ЛЗ v4
            "t_s0401": float(opt_in.t_s0401),
            "t_lz04": float(opt_in.t_lz04),
            "t_kon_v4": float(opt_in.t_kon_v4),
            "t_pause_v4": float(opt_in.t_pause_v4),
            "enable_v4": bool(opt_in.enable_v4),
            # ЛЗ v5
            "t_s05": float(opt_in.t_s05),
            "t_lz05": float(opt_in.t_lz05),
            "t_kon_v5": float(opt_in.t_kon_v5),
            "t_pause_v5": float(opt_in.t_pause_v5),
            "enable_v5": bool(opt_in.enable_v5),
            # ЛЗ v6
            "t_s06": float(opt_in.t_s06),
            "t_lz06": float(opt_in.t_lz06),
            "t_kon_v6": float(opt_in.t_kon_v6),
            "enable_v6": bool(opt_in.enable_v6),
            # ЛЗ v7
            "t_s07": float(opt_in.t_s07),
            "t_lz07": float(opt_in.t_lz07),
            "t_kon_v7": float(opt_in.t_kon_v7),
            "t_pause_v7": float(opt_in.t_pause_v7),
            "enable_v7": bool(opt_in.enable_v7),
            # ЛЗ v8
            "t_s0108": float(opt_in.t_s0108),
            "t_s0208": float(opt_in.t_s0208),
            "t_lz08": float(opt_in.t_lz08),
            "t_kon_v8": float(opt_in.t_kon_v8),
            "t_pause_v8": float(opt_in.t_pause_v8),
            "enable_v8": bool(opt_in.enable_v8),
            # ЛЗ v9
            "t_s0109": float(opt_in.t_s0109),
            "t_lz09": float(opt_in.t_lz09),
            "t_kon_v9": float(opt_in.t_kon_v9),
            "t_pause_v9": float(opt_in.t_pause_v9),
            "enable_v9": bool(opt_in.enable_v9),
            # ЛЗ v10
            "t_s0110": float(opt_in.t_s0110),
            "t_s0210": float(opt_in.t_s0210),
            "t_s0310": float(opt_in.t_s0310),
            "t_lz10": float(opt_in.t_lz10),
            "t_kon_v10": float(opt_in.t_kon_v10),
            "t_pause_v10": float(opt_in.t_pause_v10),
            "enable_v10": bool(opt_in.enable_v10),
            # ЛЗ v11
            "t_s11": float(opt_in.t_s11),
            "t_lz11": float(opt_in.t_lz11),
            "t_kon_v11": float(opt_in.t_kon_v11),
            "t_pause_v11": float(opt_in.t_pause_v11),
            "enable_v11": bool(opt_in.enable_v11),
            # ЛЗ v12
            "t_s0112": float(opt_in.t_s0112),
            "t_s0212": float(opt_in.t_s0212),
            "t_lz12": float(opt_in.t_lz12),
            "t_kon_v12": float(opt_in.t_kon_v12),
            "t_pause_v12": float(opt_in.t_pause_v12),
            "enable_v12": bool(opt_in.enable_v12),
            # ЛЗ v13
            "t_s0113": float(opt_in.t_s0113),
            "t_s0213": float(opt_in.t_s0213),
            "t_lz13": float(opt_in.t_lz13),
            "t_kon_v13": float(opt_in.t_kon_v13),
            "t_pause_v13": float(opt_in.t_pause_v13),
            "enable_v13": bool(opt_in.enable_v13),
            # ЛС v1
            "t_c0101_ls": float(opt_in.t_c0101_ls),
            "t_ls01": float(opt_in.t_ls01),
            "t_kon_ls1": float(opt_in.t_kon_ls1),
            "t_pause_ls1": float(opt_in.t_pause_ls1),
            "enable_ls1": bool(opt_in.enable_ls1),
            # ЛС v2
            "t_s0102_ls": float(opt_in.t_s0102_ls),
            "t_s0202_ls": float(opt_in.t_s0202_ls),
            "t_ls0102": float(opt_in.t_ls0102),
            "t_ls0202": float(opt_in.t_ls0202),
            "t_kon_ls2": float(opt_in.t_kon_ls2),
            "t_pause_ls2": float(opt_in.t_pause_ls2),
            "enable_ls2": bool(opt_in.enable_ls2),
            # ЛС v4
            "t_s0104_ls": float(opt_in.t_s0104_ls),
            "t_s0204_ls": float(opt_in.t_s0204_ls),
            "t_ls0104": float(opt_in.t_ls0104),
            "t_ls0204": float(opt_in.t_ls0204),
            "t_kon_ls4": float(opt_in.t_kon_ls4),
            "t_pause_ls4": float(opt_in.t_pause_ls4),
            "enable_ls4": bool(opt_in.enable_ls4),
            # ЛС v5
            "t_s0105_ls": float(opt_in.t_s0105_ls),
            "t_ls05": float(opt_in.t_ls05),
            "t_kon_ls5": float(opt_in.t_kon_ls5),
            "t_pause_ls5": float(opt_in.t_pause_ls5),
            "enable_ls5": bool(opt_in.enable_ls5),
            # ЛС v6
            "t_s0106_ls": float(opt_in.t_s0106_ls),
            "t_ls06": float(opt_in.t_ls06),
            "t_kon_ls6": float(opt_in.t_kon_ls6),
            "t_pause_ls6": float(opt_in.t_pause_ls6),   
            "enable_ls6": bool(opt_in.enable_ls6),
            # ЛС v9
            "t_s0109_ls": float(opt_in.t_s0109_ls),
            "t_s0209_ls": float(opt_in.t_s0209_ls),
            "t_ls0109": float(opt_in.t_ls0109),
            "t_ls0209": float(opt_in.t_ls0209),
            "t_kon_ls9": float(opt_in.t_kon_ls9),
            "t_pause_ls9": float(opt_in.t_pause_ls9),
            "enable_ls9": bool(opt_in.enable_ls9),
            # Исключения ЛЗ
            "t_mu": float(opt_in.t_mu),
            "t_recent_ls": float(opt_in.t_recent_ls),
            "t_min_maneuver_v8": float(opt_in.t_min_maneuver_v8),
            "enable_lz_exc_mu": bool(opt_in.enable_lz_exc_mu),
            "enable_lz_exc_recent_ls": bool(opt_in.enable_lz_exc_recent_ls),
            "enable_lz_exc_dsp": bool(opt_in.enable_lz_exc_dsp),
            # Исключения ЛС
            "t_ls_mu": float(opt_in.t_ls_mu),
            "t_ls_after_lz": float(opt_in.t_ls_after_lz),
            "t_ls_dsp": float(opt_in.t_ls_dsp),
            "enable_ls_exc_mu": bool(opt_in.enable_ls_exc_mu),
            "enable_ls_exc_after_lz": bool(opt_in.enable_ls_exc_after_lz),
            "enable_ls_exc_dsp": bool(opt_in.enable_ls_exc_dsp),
        }
    else:
        options = {}

    timeline: List[TimelineStep] = simulate_1p(
        station=station,
        scenario_steps=steps_internal,
        dt=float(scenario.dt),
        options=options,
    )

    result: List[TimelineStepOut] = []
    for row in timeline:
        result.append(
            TimelineStepOut(
                t=float(row.t),
                step_duration=float(row.step_duration),
                lz_state=bool(row.lz_state),
                variant=int(row.variant),
                effective_prev_rc=row.effective_prev_rc,
                effective_next_rc=row.effective_next_rc,
                flags=list(row.flags),
                rc_states=dict(row.rc_states),
                switch_states=dict(row.switch_states),
                signal_states=dict(getattr(row, "signal_states", {}) or {}),
                mu_state=getattr(row, "mu_state", None),
                nas_state=getattr(row, "nas_state", None),
                chas_state=getattr(row, "chas_state", None),
                dsp_state=getattr(row, "dsp_state", None),
            )
        )
    return result


@app.get("/tests")
def list_tests():
    tests = []
    for test_file in sorted(TESTS_DIR.glob("*.json")):
        try:
            raw = test_file.read_text(encoding="utf-8")
            data = json.loads(raw)
        except Exception:
            tests.append(
                {
                    "id": test_file.stem,
                    "name": f"{test_file.stem} (INVALID JSON)",
                    "variant": None,
                    "direction": None,
                    "lastStatus": "unknown",
                    "comment": "",
                }
            )
            continue

        test_id = data.get("id") or test_file.stem
        name = data.get("name") or test_file.stem
        tests.append(
            {
                "id": test_id,
                "name": name,
                "variant": data.get("variant"),
                "direction": data.get("direction"),
                "lastStatus": data.get("lastStatus", "unknown"),
                "comment": data.get("comment", ""),
            }
        )
    return tests


@app.get("/tests/{test_id}")
def get_test(test_id: str) -> Dict[str, Any]:
    test_path = TESTS_DIR / f"{test_id}.json"
    if not test_path.exists():
        raise HTTPException(status_code=404, detail="Test not found")
    try:
        data = json.loads(test_path.read_text(encoding="utf-8"))
    except Exception:
        raise HTTPException(status_code=500, detail="Cannot read test file")
    data.setdefault("id", test_id)
    return data


@app.post("/tests")
def save_test(test_data: Dict[str, Any]):
    test_id = test_data.get("id")
    if not test_id:
        test_id = f"test_{int(datetime.now().timestamp())}"
        test_data["id"] = test_id

    test_path = TESTS_DIR / f"{test_id}.json"
    test_path.write_text(
        json.dumps(test_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"id": test_id}


@app.post("/tests/{test_id}/status")
def update_test_status(test_id: str, status_data: Dict[str, Any]):
    test_path = TESTS_DIR / f"{test_id}.json"
    if not test_path.exists():
        raise HTTPException(status_code=404, detail="Test not found")

    data = json.loads(test_path.read_text(encoding="utf-8"))

    status = status_data.get("status")
    if status is not None:
        data["lastStatus"] = status

    if "comment" in status_data:
        data["comment"] = status_data["comment"]

    test_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"status": "updated"}


@app.delete("/tests/{test_id}")
def delete_test(test_id: str):
    test_path = TESTS_DIR / f"{test_id}.json"
    if not test_path.exists():
        raise HTTPException(status_code=404, detail="Test not found")

    try:
        os.remove(test_path)
    except OSError:
        raise HTTPException(status_code=500, detail="Cannot delete test file")

    return {"status": "deleted", "id": test_id}

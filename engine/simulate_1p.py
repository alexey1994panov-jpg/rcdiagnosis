from dataclasses import dataclass
from typing import Dict, List

from engine.occupancy.exceptions.exc_recent_ls_on_adjacent import (
    RecentLsOnAdjacentException,
)
from engine.occupancy.exceptions.exc_dsp_autoaction_timeout import (
    DspAutoActionTimeoutException,
)

from .station_visochino_1p import StationModel1P
from .station_visochino_1p import rc_is_free, rc_is_occupied, sw_lost_control
from .config_1p import (
    VariantOptions,
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
from .adjacency_1p import AdjacencyState, update_adjacency, compute_local_adjacency
from .detectors_runner_1p import (
    DetectorsState,
    DetectorsResult,
    init_detectors,
    run_detectors,
)
from .types_1p import ScenarioStep


@dataclass
class TimelineStep:
    t: float
    step_duration: float
    lz_state: bool
    variant: int
    effective_prev_rc: str
    effective_next_rc: str
    flags: List[str]
    rc_states: Dict[str, int]
    switch_states: Dict[str, int]
    signal_states: Dict[str, int] | None = None
    mu_state: int | None = None
    nas_state: int | None = None
    chas_state: int | None = None
    dsp_state: int | None = None
    ctrl_rc_id: str | None = None


def _build_variant_options(opts: dict) -> VariantOptions:
    return VariantOptions(
        t_s0101=float(opts.get("t_s0101", T_S0101)),
        t_lz01=float(opts.get("t_lz01", T_LZ01)),
        t_kon_v1=float(opts.get("t_kon_v1", T_KON)),
        enable_v1=bool(opts.get("enable_v1", True)),

        t_s0102=float(opts.get("t_s0102", T_S0102_DEFAULT)),
        t_s0202=float(opts.get("t_s0202", T_S0202_DEFAULT)),
        t_lz02=float(opts.get("t_lz02", T_LZ02_DEFAULT)),
        t_kon_v2=float(opts.get("t_kon_v2", T_KON)),
        enable_v2=bool(opts.get("enable_v2", True)),

        t_s0103=float(opts.get("t_s0103", T_S0103_DEFAULT)),
        t_s0203=float(opts.get("t_s0203", T_S0203_DEFAULT)),
        t_lz03=float(opts.get("t_lz03", T_LZ03_DEFAULT)),
        t_kon_v3=float(opts.get("t_kon_v3", T_KON)),
        enable_v3=bool(opts.get("enable_v3", True)),

        t_s0401=float(opts.get("t_s0401", T_S0401_DEFAULT)),
        t_lz04=float(opts.get("t_lz04", T_LZ04_DEFAULT)),
        t_kon_v4=float(opts.get("t_kon_v4", T_KON_V4_DEFAULT)),
        enable_v4=bool(opts.get("enable_v4", True)),

        t_s05=float(opts.get("t_s05", T_S05_DEFAULT)),
        t_lz05=float(opts.get("t_lz05", T_LZ05_DEFAULT)),
        t_pk=float(opts.get("t_pk", T_PK)),
        t_kon_v5=float(opts.get("t_kon_v5", T_KON_V5_DEFAULT)),
        enable_v5=bool(opts.get("enable_v5", True)),

        t_s06=float(opts.get("t_s06", T_S06_DEFAULT)),
        t_lz06=float(opts.get("t_lz06", T_LZ06_DEFAULT)),
        t_kon_v6=float(opts.get("t_kon_v6", T_KON_V6_DEFAULT)),
        enable_v6=bool(opts.get("enable_v6", True)),

        t_s07=float(opts.get("t_s07", T_S07_DEFAULT)),
        t_lz07=float(opts.get("t_lz07", T_LZ07_DEFAULT)),
        t_kon_v7=float(opts.get("t_kon_v7", T_KON_V7_DEFAULT)),
        enable_v7=bool(opts.get("enable_v7", True)),

        t_s0108=float(opts.get("t_s0108", T_S0108_DEFAULT)),
        t_s0208=float(opts.get("t_s0208", T_S0208_DEFAULT)),
        t_lz08=float(opts.get("t_lz08", T_LZ08_DEFAULT)),
        t_kon_v8=float(opts.get("t_kon_v8", T_KON)),
        enable_v8=bool(opts.get("enable_v8", True)),

        t_s0109=float(opts.get("t_s0109", T_S0109_DEFAULT)),
        t_lz09=float(opts.get("t_lz09", T_LZ09_DEFAULT)),
        t_kon_v9=float(opts.get("t_kon_v9", T_KON_V9_DEFAULT)),
        enable_v9=bool(opts.get("enable_v9", True)),

        t_s0110=float(opts.get("t_s0110", TS0110_DEFAULT)),
        t_s0210=float(opts.get("t_s0210", TS0210_DEFAULT)),
        t_s0310=float(opts.get("t_s0310", TS0310_DEFAULT)),
        t_lz10=float(opts.get("t_lz10", TLZ10_DEFAULT)),
        t_kon_v10=float(opts.get("t_kon_v10", TKON_V10_DEFAULT)),
        enable_v10=bool(opts.get("enable_v10", True)),

        t_s11=float(opts.get("t_s11", T_S11_DEFAULT)),
        t_lz11=float(opts.get("t_lz11", T_LZ11_DEFAULT)),
        t_kon_v11=float(opts.get("t_kon_v11", T_KON_V11_DEFAULT)),
        enable_v11=bool(opts.get("enable_v11", True)),

        t_s0112=float(opts.get("t_s0112", T_S0112_DEFAULT)),
        t_s0212=float(opts.get("t_s0212", T_S0212_DEFAULT)),
        t_lz12=float(opts.get("t_lz12", T_LZ12_DEFAULT)),
        t_kon_v12=float(opts.get("t_kon_v12", T_KON_V12_DEFAULT)),
        enable_v12=bool(opts.get("enable_v12", True)),

        t_s0113=float(opts.get("t_s0113", T_S0113_DEFAULT)),
        t_s0213=float(opts.get("t_s0213", T_S0213_DEFAULT)),
        t_lz13=float(opts.get("t_lz13", T_LZ13_DEFAULT)),
        t_kon_v13=float(opts.get("t_kon_v13", T_KON_V13_DEFAULT)),
        enable_v13=bool(opts.get("enable_v13", True)),

        t_c0101_ls=float(opts.get("t_c0101_ls", T_C0101_LS_DEFAULT)),
        t_ls01=float(opts.get("t_ls01", T_LS01_DEFAULT)),
        t_kon_ls1=float(opts.get("t_kon_ls1", T_KON_LS_DEFAULT)),
        enable_ls1=bool(opts.get("enable_ls1", True)),

        t_s0102_ls=float(opts.get("t_s0102_ls", opts.get("ts0102ls", T_S0102_LS_DEFAULT))),
        t_s0202_ls=float(opts.get("t_s0202_ls", opts.get("ts0202ls", T_S0202_LS_DEFAULT))),
        t_ls0102=float(opts.get("t_ls0102", opts.get("tls0102", T_LS0102_DEFAULT))),
        t_ls0202=float(opts.get("t_ls0202", opts.get("tls0202", T_LS0202_DEFAULT))),
        t_kon_ls2=float(opts.get("t_kon_ls2", opts.get("tkonls2", T_KON_LS2_DEFAULT))),
        enable_ls2=bool(opts.get("enable_ls2", opts.get("enablels2", True))),

        t_s0104_ls=float(opts.get("t_s0104_ls", T_S0104_LS_DEFAULT)),
        t_s0204_ls=float(opts.get("t_s0204_ls", T_S0204_LS_DEFAULT)),
        t_ls0104=float(opts.get("t_ls0104", T_LS0104_DEFAULT)),
        t_ls0204=float(opts.get("t_ls0204", T_LS0204_DEFAULT)),
        t_kon_ls4=float(opts.get("t_kon_ls4", T_KON_LS4_DEFAULT)),
        enable_ls4=bool(opts.get("enable_ls4", True)),

        t_s0105_ls=float(opts.get("t_s0105_ls", T_S0105_LS_DEFAULT)),
        t_ls05=float(opts.get("t_ls05", T_LS05_DEFAULT)),
        t_kon_ls5=float(opts.get("t_kon_ls5", T_KON_LS5_DEFAULT)),
        enable_ls5=bool(opts.get("enable_ls5", True)),

        t_s0106_ls=float(opts.get("t_s0106_ls", T_S0106_LS_DEFAULT)),
        t_ls06=float(opts.get("t_ls06", T_LS06_DEFAULT)),
        t_kon_ls6=float(opts.get("t_kon_ls6", T_KON_LS6_DEFAULT)),
        enable_ls6=bool(opts.get("enable_ls6", True)),

        t_s0109_ls=float(opts.get("t_s0109_ls", T_S0109_LS_DEFAULT)),
        t_s0209_ls=float(opts.get("t_s0209_ls", T_S0209_LS_DEFAULT)),
        t_ls0109=float(opts.get("t_ls0109", T_LS0109_DEFAULT)),
        t_ls0209=float(opts.get("t_ls0209", T_LS0209_DEFAULT)),
        t_kon_ls9=float(opts.get("t_kon_ls9", T_KON_LS9_DEFAULT)),
        enable_ls9=bool(opts.get("enable_ls9", True)),

        t_pause_v1=float(opts.get("t_pause_v1", T_PAUSE_DEFAULT)),
        t_pause_v2=float(opts.get("t_pause_v2", T_PAUSE_DEFAULT)),
        t_pause_v3=float(opts.get("t_pause_v3", T_PAUSE_DEFAULT)),
        t_pause_v4=float(opts.get("t_pause_v4", T_PAUSE_DEFAULT)),
        t_pause_v5=float(opts.get("t_pause_v5", T_PAUSE_DEFAULT)),
        t_pause_v6=float(opts.get("t_pause_v6", T_PAUSE_DEFAULT)),
        t_pause_v7=float(opts.get("t_pause_v7", T_PAUSE_DEFAULT)),
        t_pause_v8=float(opts.get("t_pause_v8", T_PAUSE_DEFAULT)),
        t_pause_v9=float(opts.get("t_pause_v9", T_PAUSE_DEFAULT)),
        t_pause_v10=float(opts.get("t_pause_v10", T_PAUSE_DEFAULT)),
        t_pause_v11=float(opts.get("t_pause_v11", T_PAUSE_DEFAULT)),
        t_pause_v12=float(opts.get("t_pause_v12", T_PAUSE_DEFAULT)),
        t_pause_v13=float(opts.get("t_pause_v13", T_PAUSE_DEFAULT)),

        t_pause_ls1=float(opts.get("t_pause_ls1", T_PAUSE_DEFAULT)),
        t_pause_ls2=float(opts.get("t_pause_ls2", opts.get("tpausels2", T_PAUSE_DEFAULT))),
        t_pause_ls4=float(opts.get("t_pause_ls4", T_PAUSE_DEFAULT)),
        t_pause_ls5=float(opts.get("t_pause_ls5", T_PAUSE_DEFAULT)),
        t_pause_ls6=float(opts.get("t_pause_ls6", T_PAUSE_DEFAULT)),
        t_pause_ls9=float(opts.get("t_pause_ls9", T_PAUSE_DEFAULT)),

        t_mu=float(opts.get("t_mu", T_MU)),
        t_recent_ls=float(opts.get("t_recent_ls", T_RECENT_LS)),
        t_min_maneuver_v8=float(opts.get("t_min_maneuver_v8", T_MIN_MANEUVER_V8)),

        enable_lz_exc_mu=bool(opts.get("enable_lz_exc_mu", True)),
        enable_lz_exc_recent_ls=bool(opts.get("enable_lz_exc_recent_ls", True)),
        enable_lz_exc_dsp=bool(opts.get("enable_lz_exc_dsp", True)),
        enable_ls_exc_mu=bool(opts.get("enable_ls_exc_mu", True)),
        enable_ls_exc_after_lz=bool(opts.get("enable_ls_exc_after_lz", True)),
        enable_ls_exc_dsp=bool(opts.get("enable_ls_exc_dsp", True)),

        t_ls_mu=float(opts.get("t_ls_mu", T_LS_MU)),
        t_ls_after_lz=float(opts.get("t_ls_after_lz", T_LS_AFTER_LZ)),
        t_ls_dsp=float(opts.get("t_ls_dsp", T_LS_DSP)),

        allow_route_lock_states=bool(opts.get("allow_route_lock_states", False)),
    )


def simulate_1p(
    station: StationModel1P,
    scenario_steps: List[ScenarioStep],
    dt: float = 1.0,
    options: dict | None = None,
) -> List[TimelineStep]:
    opts = options or {}
    var_opts = _build_variant_options(opts)

    station.t_mu = getattr(var_opts, "t_mu", T_MU)
    station.t_recent_ls = getattr(var_opts, "t_recent_ls", T_RECENT_LS)
    station.t_min_maneuver_v8 = getattr(
        var_opts, "t_min_maneuver_v8", T_MIN_MANEUVER_V8
    )

    station.t_ls_mu = getattr(var_opts, "t_ls_mu", T_LS_MU)
    station.t_ls_after_lz = getattr(var_opts, "t_ls_after_lz", T_LS_AFTER_LZ)
    station.t_ls_dsp = getattr(var_opts, "t_ls_dsp", T_LS_DSP)

    adjacency_state = AdjacencyState()
    detectors_state: DetectorsState = init_detectors(
        var_opts,
        station.rc_ids,
        rc_has_route_lock=getattr(station, "rc_has_route_lock", None),
        station=station,
    )
    timeline: List[TimelineStep] = []

    in_pause = False
    pause_left = 0.0
    current_time: float = 0.0

    for idx, step in enumerate(scenario_steps):
        raw_dur = float(step.t)
        if raw_dur <= 0.0:
            continue

        dt_interval = raw_dur

        # MU / dispatcher / auto actions
        mu_map: Dict[str, int] = getattr(step, "mu", None) or {}
        if hasattr(station, "rc_mu_by_rc"):
            for rc_id, mu_state in mu_map.items():
                mu_obj = station.rc_mu_by_rc.get(rc_id)
                if mu_obj is not None:
                    mu_obj.state = int(mu_state)

        dsp_state_val = getattr(step, "dispatcher_control_state", None)
        if dsp_state_val is not None and hasattr(station, "dispatcher_control_state"):
            station.dispatcher_control_state = int(dsp_state_val)

        aa_map: Dict[str, int] = getattr(step, "auto_actions", None) or {}
        auto_actions = getattr(station, "auto_actions", []) or []
        for aa in auto_actions:
            aa_id = getattr(aa, "id", None)
            if aa_id and aa_id in aa_map:
                aa.state = int(aa_map[aa_id])

        # ctrl_rc_id из модели станции
        step_ctrl_rc_id = station.ctrl_rc_id

        # нормализация modes + запись ctrl_rc_id
        if step.modes is None:
            step.modes = {}
        else:
            step.modes = dict(step.modes)
        step.modes["ctrl_rc_id"] = step_ctrl_rc_id

        # глобальная смежность
        current_prev, current_next, prev_ok, next_ok = update_adjacency(
            adjacency_state,
            station,
            step,
            dt_interval,
        )

        if current_prev:
            step.modes["prev_state"] = step.rc_states.get(current_prev, 0)
        else:
            step.modes["prev_state"] = 0

        if current_next:
            step.modes["next_state"] = step.rc_states.get(current_next, 0)
        else:
            step.modes["next_state"] = 0

        # состояние контролируемой РЦ
        ctrl_state = step.rc_states.get(step_ctrl_rc_id, 0)

        is_tip_minus = not prev_ok
        is_tip_plus = not next_ok

        step.modes["prev_control_ok"] = prev_ok
        step.modes["next_control_ok"] = next_ok
        step.modes["is_tip_minus"] = is_tip_minus
        step.modes["is_tip_plus"] = is_tip_plus

        # локальная смежность для per‑РЦ вариантов
        per_rc_ids: set[str] = set()
        if detectors_state.v4_by_rc:
            per_rc_ids.update(detectors_state.v4_by_rc.keys())
        if detectors_state.v12_by_rc:
            per_rc_ids.update(detectors_state.v12_by_rc.keys())
        if detectors_state.v13_by_rc:
            per_rc_ids.update(detectors_state.v13_by_rc.keys())
        if detectors_state.ls6_by_rc:
            per_rc_ids.update(detectors_state.ls6_by_rc.keys())

        for rc_id in per_rc_ids:
            adj_local = compute_local_adjacency(station, step, rc_id)
            key = rc_id
            step.modes[f"{key}_prev_state"] = adj_local.prev_state
            step.modes[f"{key}_next_state"] = adj_local.next_state
            step.modes[f"{key}_prev_nc"] = adj_local.prev_nc
            step.modes[f"{key}_next_nc"] = adj_local.next_nc

        # паузы
        if in_pause:
            pause_left = max(0.0, pause_left - dt_interval)
            if pause_left == 0.0:
                in_pause = False

        opened_any = False
        closed_any = False
        res = DetectorsResult()

        if not in_pause:
            detectors_state, res = run_detectors(
                detectors_state,
                step,
                dt_interval,
                history=scenario_steps,
                idx=idx,
            )

            opened_any = any(
                [
                    res.opened_v1,
                    res.opened_v2,
                    res.opened_v3,
                    res.opened_v4,
                    res.opened_v5,
                    res.opened_v6,
                    res.opened_v7,
                    res.opened_v8,
                    res.opened_v9,
                    res.opened_v10,
                    res.opened_v11,
                    res.opened_v12,
                    res.opened_v13,
                    res.opened_ls1,
                    res.opened_ls2,
                    res.opened_ls4,
                    res.opened_ls5,
                    res.opened_ls6,
                    res.opened_ls9,
                ]
            )

            closed_any = any(
                [
                    res.closed_v1,
                    res.closed_v2,
                    res.closed_v3,
                    res.closed_v4,
                    res.closed_v5,
                    res.closed_v6,
                    res.closed_v7,
                    res.closed_v8,
                    res.closed_v9,
                    res.closed_v10,
                    res.closed_v11,
                    res.closed_v12,
                    res.closed_v13,
                    res.closed_ls1,
                    res.closed_ls2,
                    res.closed_ls4,
                    res.closed_ls5,
                    res.closed_ls6,
                    res.closed_ls9,
                ]
            )

            if opened_any:
                pause_candidates: List[float] = []
                if res.opened_v1:
                    pause_candidates.append(var_opts.t_pause_v1)
                if res.opened_v2:
                    pause_candidates.append(var_opts.t_pause_v2)
                if res.opened_v3:
                    pause_candidates.append(var_opts.t_pause_v3)
                if res.opened_v4:
                    pause_candidates.append(var_opts.t_pause_v4)
                if res.opened_v5:
                    pause_candidates.append(var_opts.t_pause_v5)
                if res.opened_v6:
                    pause_candidates.append(var_opts.t_pause_v6)
                if res.opened_v7:
                    pause_candidates.append(var_opts.t_pause_v7)
                if res.opened_v8:
                    pause_candidates.append(var_opts.t_pause_v8)
                if res.opened_v9:
                    pause_candidates.append(var_opts.t_pause_v9)
                if res.opened_v10:
                    pause_candidates.append(var_opts.t_pause_v10)
                if res.opened_v11:
                    pause_candidates.append(var_opts.t_pause_v11)
                if res.opened_v12:
                    pause_candidates.append(var_opts.t_pause_v12)
                if res.opened_v13:
                    pause_candidates.append(var_opts.t_pause_v13)
                if res.opened_ls1:
                    pause_candidates.append(var_opts.t_pause_ls1)
                if res.opened_ls2:
                    pause_candidates.append(var_opts.t_pause_ls2)
                if res.opened_ls4:
                    pause_candidates.append(var_opts.t_pause_ls4)
                if res.opened_ls5:
                    pause_candidates.append(var_opts.t_pause_ls5)
                if res.opened_ls6:
                    pause_candidates.append(var_opts.t_pause_ls6) 
                if res.opened_ls9:
                    pause_candidates.append(var_opts.t_pause_ls9)
                # для ЛС6 пока отдельной паузы нет в конфиге; если добавишь t_pause_ls6, добавь сюда

                if pause_candidates:
                    pause_val = max(pause_candidates)
                    if pause_val > 0.0:
                        in_pause = True
                        pause_left = pause_val

        if closed_any:
            in_pause = False
            pause_left = 0.0

        # контролируемая РЦ для исключений
        exc_ctrl_rc_id = step_ctrl_rc_id
        if getattr(detectors_state, "ds_ctrl_rc_v13", None):
            exc_ctrl_rc_id = detectors_state.ds_ctrl_rc_v13
        elif getattr(detectors_state, "ds_ctrl_rc_v12", None):
            exc_ctrl_rc_id = detectors_state.ds_ctrl_rc_v12
        elif getattr(detectors_state, "ds_ctrl_rc_v6", None):
            exc_ctrl_rc_id = detectors_state.ds_ctrl_rc_v6
        elif getattr(detectors_state, "ds_ctrl_rc_v5", None):
            exc_ctrl_rc_id = detectors_state.ds_ctrl_rc_v5
        elif getattr(detectors_state, "ds_ctrl_rc_v4", None):
            exc_ctrl_rc_id = detectors_state.ds_ctrl_rc_v4

        flags: List[str] = []
        variant = 0

        curr_free = rc_is_free(ctrl_state)
        curr_occ = rc_is_occupied(ctrl_state)

        sw10_state = step.switch_states.get("Sw10", 0)

        # выбор варианта по активным детекторам (ЛЗ)
        if detectors_state.ds_active_v1:
            variant = 1
            flags.append("llz_v1")
        if detectors_state.ds_active_v2:
            variant = 2
            flags.append("llz_v2")
        if detectors_state.ds_active_v3:
            variant = 3
            flags.append("llz_v3")

        ds4 = getattr(detectors_state, "ds_active_v4_by_rc", None)
        if ds4 and any(ds4.values()):
            variant = 4
            flags.append("llz_v4")

        ds5 = getattr(detectors_state, "ds_active_v5_by_rc", None)
        if ds5 and any(ds5.values()):
            variant = 5
            flags.append("llz_v5")

        ds6 = getattr(detectors_state, "ds_active_v6_by_rc", None)
        if ds6 and any(ds6.values()):
            variant = 6
            flags.append("llz_v6")

        if getattr(detectors_state, "ds_active_v7", False):
            variant = 7
            flags.append("llz_v7")
        if detectors_state.ds_active_v8:
            variant = 8
            flags.append("llz_v8")
        if getattr(detectors_state, "ds_active_v9", False):
            variant = 9
            flags.append("llz_v9")
        if detectors_state.ds_active_v10:
            variant = 10
            flags.append("llz_v10")
        if getattr(detectors_state, "ds_active_v11", False):
            variant = 11
            flags.append("llz_v11")

        ds12 = getattr(detectors_state, "ds_active_v12_by_rc", None)
        if ds12 and any(ds12.values()):
            variant = 12
            flags.append("llz_v12")
        if getattr(detectors_state, "ds_active_v13", False):
            variant = 13
            flags.append("llz_v13")

        # ЛС-флаги (без изменения номера варианта)
        if detectors_state.ls_active_v1:
            flags.append("lls_v1")
        if detectors_state.ls_active_v2:
            flags.append("lls_v2")
        if detectors_state.ls_active_v4:
            flags.append("lls_v4")
        if detectors_state.ls_active_v5:
            flags.append("lls_v5")
        if (
            detectors_state.ls_active_v9_by_rc
            and any(detectors_state.ls_active_v9_by_rc.values())
        ):
            flags.append("lls_v9")
        if (
            detectors_state.ls_active_v6_by_rc
            and any(detectors_state.ls_active_v6_by_rc.values())
        ):
            flags.append("lls_v6")

        # события открытий/закрытий
        if res.opened_v1:
            flags.append("llz_v1_open")
        if res.opened_v2:
            flags.append("llz_v2_open")
        if res.opened_v3:
            flags.append("llz_v3_open")
        if res.opened_v4:
            flags.append("llz_v4_open")
        if res.opened_v5:
            flags.append("llz_v5_open")
        if res.opened_v6:
            flags.append("llz_v6_open")
        if res.opened_v7:
            flags.append("llz_v7_open")
        if res.opened_v8:
            flags.append("llz_v8_open")
        if res.opened_v9:
            flags.append("llz_v9_open")
        if res.opened_v10:
            flags.append("llz_v10_open")
        if res.opened_v11:
            flags.append("llz_v11_open")
        if res.opened_v12:
            flags.append("llz_v12_open")
        if res.opened_v13:
            flags.append("llz_v13_open")
        if res.opened_ls1:
            flags.append("lls_v1_open")
        if res.opened_ls2:
            flags.append("lls_v2_open")
        if res.opened_ls4:
            flags.append("lls_v4_open")
        if res.opened_ls5:
            flags.append("lls_v5_open")
        if res.opened_ls6:
            flags.append("lls_v6_open")
        if res.opened_ls9:
            flags.append("lls_v9_open")

        if res.closed_v1:
            flags.append("llz_v1_closed")
        if res.closed_v2:
            flags.append("llz_v2_closed")
        if res.closed_v3:
            flags.append("llz_v3_closed")
        if res.closed_v4:
            flags.append("llz_v4_closed")
        if res.closed_v5:
            flags.append("llz_v5_closed")
        if res.closed_v6:
            flags.append("llz_v6_closed")
        if res.closed_v7:
            flags.append("llz_v7_closed")
        if res.closed_v8:
            flags.append("llz_v8_closed")
        if res.closed_v9:
            flags.append("llz_v9_closed")
        if res.closed_v10:
            flags.append("llz_v10_closed")
        if res.closed_v11:
            flags.append("llz_v11_closed")
        if res.closed_v12:
            flags.append("llz_v12_closed")
        if res.closed_v13:
            flags.append("llz_v13_closed")
        if res.closed_ls1:
            flags.append("lls_v1_closed")
        if res.closed_ls2:
            flags.append("lls_v2_closed")
        if res.closed_ls4:
            flags.append("lls_v4_closed")
        if res.closed_ls5:
            flags.append("lls_v5_closed")
        if res.closed_ls6:
            flags.append("lls_v6_closed")
        if res.closed_ls9:
            flags.append("lls_v9_closed")

        v1_free_ok = detectors_state.ds_active_v1 and curr_free

        lz = (
            curr_occ
            or detectors_state.ds_active_v1
            or detectors_state.ds_active_v2
            or detectors_state.ds_active_v3
            or (ds4 and any(ds4.values()))
            or (ds5 and any(ds5.values()))
            or (ds6 and any(ds6.values()))
            or getattr(detectors_state, "ds_active_v7", False)
            or detectors_state.ds_active_v8
            or getattr(detectors_state, "ds_active_v9", False)
            or detectors_state.ds_active_v10
            or getattr(detectors_state, "ds_active_v11", False)
            or (ds12 and any(ds12.values()))
            or getattr(detectors_state, "ds_active_v13", False)
        )

        ls_active = any(
            [
                detectors_state.ls_active_v1,
                detectors_state.ls_active_v2,
                detectors_state.ls_active_v4,
                detectors_state.ls_active_v5,
                bool(
                    detectors_state.ls_active_v9_by_rc
                    and any(detectors_state.ls_active_v9_by_rc.values())
                ),
                #bool(
                #    detectors_state.ls_active_v6_by_rc
                #    and any(detectors_state.ls_active_v6_by_rc.values())
                #),
            ]
        )

        # исключения для ЛЗ
        if lz:
            exceptions = station.get_lz_exceptions_for_rc(exc_ctrl_rc_id)
            for exc in exceptions:
                if isinstance(exc, DspAutoActionTimeoutException):
                    if not var_opts.enable_lz_exc_dsp or variant != 8:
                        continue
                elif isinstance(exc, RecentLsOnAdjacentException):
                    if not var_opts.enable_lz_exc_recent_ls:
                        continue
                else:
                    if not var_opts.enable_lz_exc_mu:
                        continue

                if exc.should_suppress(
                    station=station,
                    history=scenario_steps,
                    idx=idx,
                    ctrl_rc_id=exc_ctrl_rc_id,
                    timeline=timeline,
                ):
                    lz = False
                    flags = [f for f in flags if not f.startswith("llz_v")]
                    flags.append(f"lz_suppressed:{exc.id}")
                    break

        if not lz:
            had_suppression_before = any(
                any(f.startswith("lz_suppressed:") for f in prev_step.flags)
                for prev_step in timeline
            )
            if had_suppression_before:
                flags = [f for f in flags if not f.startswith("llz_v")]

        had_dsp_suppression = any(
            any(f == "lz_suppressed:dsp_autoaction_timeout" for f in prev_step.flags)
            for prev_step in timeline
        )
        if had_dsp_suppression:
            lz = False
            flags = [f for f in flags if not f.startswith("llz_v")]
            if "lz_suppressed:dsp_autoaction_timeout" not in flags:
                flags.append("lz_suppressed:dsp_autoaction_timeout")

        if lz and curr_free and not v1_free_ok:
            flags.append("false_lz")
        if (not lz) and curr_occ and not any(
            f.startswith("lz_suppressed:") for f in flags
        ):
            flags.append("no_lz_when_occupied")

        # потеря контроля стрелок
        if step_ctrl_rc_id == "10-12SP":
            ctrl_sw_lost = sw_lost_control(step.switch_states.get("Sw10", 0))
        elif step_ctrl_rc_id == "1-7SP":
            sw1_lost = sw_lost_control(step.switch_states.get("Sw1", 0))
            sw5_lost = sw_lost_control(step.switch_states.get("Sw5", 0))
            ctrl_sw_lost = sw1_lost or sw5_lost
        else:
            ctrl_sw_lost = (
                sw_lost_control(step.switch_states.get("Sw10", 0))
                or sw_lost_control(step.switch_states.get("Sw1", 0))
                or sw_lost_control(step.switch_states.get("Sw5", 0))
            )

        if lz and ctrl_sw_lost:
            flags.append("switch_lost_control_with_lz")

        # исключения для ЛС
        if ls_active:
            ls_exceptions = station.get_ls_exceptions_for_rc(exc_ctrl_rc_id)
            for exc in ls_exceptions:
                exc_id = getattr(exc, "id", "")
                if exc_id == "ls_exc_mu" and not var_opts.enable_ls_exc_mu:
                    continue
                if exc_id == "ls_exc_after_lz" and not var_opts.enable_ls_exc_after_lz:
                    continue
                if exc_id == "ls_exc_dsp_autoaction" and not var_opts.enable_ls_exc_dsp:
                    continue

                if exc.should_suppress(
                    station=station,
                    history=scenario_steps,
                    idx=idx,
                    ctrl_rc_id=exc_ctrl_rc_id,
                    timeline=timeline,
                ):
                    flags = [f for f in flags if not f.startswith("lls_v")]
                    flags.append(f"ls_suppressed:{exc.id}")
                    ls_active = False
                    break

        current_time += dt_interval
        t_val = current_time

        mu_state = getattr(station, "rc_mu", None)
        mu_val = getattr(mu_state, "state", 3) if mu_state is not None else 3

        nas_val: int | None = None
        chas_val: int | None = None
        for aa in getattr(station, "auto_actions", []) or []:
            if getattr(aa, "id", "") == "NAS":
                nas_val = getattr(aa, "state", 4)
            elif getattr(aa, "id", "") == "CHAS":
                chas_val = getattr(aa, "state", 4)

        dsp_val: int | None = getattr(station, "dispatcher_control_state", None)

        timeline.append(
            TimelineStep(
                t=t_val,
                step_duration=dt_interval,
                lz_state=lz,
                variant=variant,
                effective_prev_rc=current_prev,
                effective_next_rc=current_next,
                flags=flags,
                rc_states=dict(step.rc_states),
                switch_states={
                    "Sw10": sw10_state,
                    "Sw1": step.switch_states.get("Sw1", 0),
                    "Sw5": step.switch_states.get("Sw5", 0),
                },
                signal_states=dict(getattr(step, "signal_states", {}) or {}),
                mu_state=mu_val,
                nas_state=nas_val,
                chas_state=chas_val,
                dsp_state=dsp_val,
                ctrl_rc_id=step_ctrl_rc_id,
            )
        )

    return timeline

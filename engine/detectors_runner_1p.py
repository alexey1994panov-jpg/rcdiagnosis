from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict

from .variants.variant1_1p import Variant1Detector
from .variants.variant2_1p import Variant2Detector
from .variants.variant3_1p import Variant3Detector
from .variants.variant4_1p import Variant4Detector
from .variants.variant5_1p import Variant5Detector
from .variants.variant6_1p import Variant6Detector
from .variants.variant7_1p import Variant7Detector
from .variants.variant8_1p import Variant8Detector
from .variants.variant9_1p import Variant9Detector
from .variants.variant10_1p import Variant10Detector
from .variants.variant11_1p import Variant11Detector
from .variants.variant12_1p import Variant12Detector
from .variants.variant13_1p import Variant13Detector
from .variants.ls_variant1_1p import VariantLS1Detector
from .variants.ls_variant2_1p import VariantLS2Detector
from .variants.ls_variant4_1p import VariantLS4Detector
from .variants.ls_variant5_1p import VariantLS5Detector
from .variants.ls_variant6_1p import VariantLS6Detector
from .variants.ls_variant9_1p import VariantLS9Detector
from .station_visochino_1p import StationModel1P

from .variants.common_1p import get_mode
from .types_1p import ScenarioStep
from .config_1p import VariantOptions


@dataclass
class DetectorsState:
    v1: Optional[Variant1Detector]
    v2: Optional[Variant2Detector]
    v3: Optional[Variant3Detector]
    v4_by_rc: Dict[str, Variant4Detector]
    v5_by_rc: Dict[str, Variant5Detector]
    v6_by_rc: Dict[str, Variant6Detector]
    v7: Optional[Variant7Detector]
    v8: Optional[Variant8Detector]
    v9: Optional[Variant9Detector]
    v10: Optional[Variant10Detector]
    v11: Optional[Variant11Detector]
    v12_by_rc: Dict[str, Variant12Detector]
    v13_by_rc: Dict[str, Variant13Detector]

    ls1: Optional[VariantLS1Detector]
    ls2: Optional[VariantLS2Detector]
    ls4: Optional[VariantLS4Detector]
    ls5: Optional[VariantLS5Detector]
    ls6_by_rc: Dict[str, VariantLS6Detector]

    # ЛС v9 по всем РЦ
    ls9_by_rc: Dict[str, VariantLS9Detector]

    # агрегированная активность ЛЗ
    ds_active_v1: bool = False
    ds_active_v2: bool = False
    ds_active_v3: bool = False
    ds_active_v4: bool = False
    ds_active_v7: bool = False
    ds_active_v8: bool = False
    ds_active_v9: bool = False
    ds_active_v10: bool = False
    ds_active_v11: bool = False
    ds_active_v12: bool = False
    ds_active_v13: bool = False

    # активность per‑РЦ вариантов ЛЗ
    ds_active_v6_by_rc: Dict[str, bool] | None = None
    ds_active_v5_by_rc: Dict[str, bool] | None = None
    ds_active_v12_by_rc: Dict[str, bool] | None = None
    ds_active_v13_by_rc: Dict[str, bool] | None = None
    ds_active_v4_by_rc: Dict[str, bool] | None = None

    # «активная контролируемая РЦ» для исключений ЛЗ
    ds_ctrl_rc_v4: str | None = None
    ds_ctrl_rc_v5: str | None = None
    ds_ctrl_rc_v6: str | None = None
    ds_ctrl_rc_v12: str | None = None
    ds_ctrl_rc_v13: str | None = None

    # ЛС (агрегированные)
    ls_active_v1: bool = False
    ls_active_v2: bool = False
    ls_active_v4: bool = False
    ls_active_v5: bool = False

    # активность ЛС по РЦ
    ls_active_v9_by_rc: Dict[str, bool] | None = None
    ls_active_v6_by_rc: Dict[str, bool] | None = None


@dataclass
class DetectorsResult:
    opened_v1: bool = False
    closed_v1: bool = False

    opened_v2: bool = False
    closed_v2: bool = False

    opened_v3: bool = False
    closed_v3: bool = False

    opened_v4: bool = False
    closed_v4: bool = False

    opened_v5: bool = False
    closed_v5: bool = False

    opened_v6: bool = False
    closed_v6: bool = False

    opened_v7: bool = False
    closed_v7: bool = False

    opened_v8: bool = False
    closed_v8: bool = False

    opened_v9: bool = False
    closed_v9: bool = False

    opened_v10: bool = False
    closed_v10: bool = False

    opened_v11: bool = False
    closed_v11: bool = False

    opened_v12: bool = False
    closed_v12: bool = False

    opened_v13: bool = False
    closed_v13: bool = False

    opened_ls1: bool = False
    closed_ls1: bool = False

    opened_ls2: bool = False
    closed_ls2: bool = False

    opened_ls4: bool = False
    closed_ls4: bool = False

    opened_ls5: bool = False
    closed_ls5: bool = False

    opened_ls6: bool = False
    closed_ls6: bool = False

    opened_ls9: bool = False
    closed_ls9: bool = False


def init_detectors(
    opts: VariantOptions,
    rc_ids: List[str],
    rc_has_route_lock: Dict[str, bool] | None = None,
    station: StationModel1P | None = None,
) -> DetectorsState:
    """
    Инициализация детекторов.

    v4/v5/v6/v12/v13/ls6/ls9 создаются per‑РЦ, завязки на target_rc нет.
    """

    v4_by_rc: Dict[str, Variant4Detector] = {}
    ds_active_v4_by_rc: Dict[str, bool] = {}

    v5_by_rc: Dict[str, Variant5Detector] = {}
    ds_active_v5_by_rc: Dict[str, bool] = {}

    v6_by_rc: Dict[str, Variant6Detector] = {}
    ds_active_v6_by_rc: Dict[str, bool] = {}

    v12_by_rc: Dict[str, Variant12Detector] = {}
    ds_active_v12_by_rc: Dict[str, bool] = {}

    v13_by_rc: Dict[str, Variant13Detector] = {}
    ds_active_v13_by_rc: Dict[str, bool] = {}

    ls6_by_rc: Dict[str, VariantLS6Detector] = {}
    ls_active_v6_by_rc: Dict[str, bool] = {}

    ls9_by_rc: Dict[str, VariantLS9Detector] = {}
    ls_active_v9_by_rc: Dict[str, bool] = {}

    # ЛЗ v4 — по РЦ
    if getattr(opts, "enable_v4", False):
        det_v4_1012 = Variant4Detector(
            prev_rc_id="",
            ctrl_rc_id="10-12SP",
            next_rc_id="1P",
            t_s0401=opts.t_s0401,
            t_lz04=opts.t_lz04,
            t_kon=opts.t_kon_v4,
            signal_prev_to_ctrl_id="ЧМ1",
            signal_ctrl_to_next_id="Ч1",
            ctrl_to_next_is_shunting=False,
        )
        v4_by_rc["10-12SP"] = det_v4_1012
        ds_active_v4_by_rc["10-12SP"] = False

        det_v4_17 = Variant4Detector(
            prev_rc_id="",
            ctrl_rc_id="1-7SP",
            next_rc_id="1P",
            t_s0401=opts.t_s0401,
            t_lz04=opts.t_lz04,
            t_kon=opts.t_kon_v4,
            signal_prev_to_ctrl_id="Ч1",
            signal_ctrl_to_next_id="М1",
            ctrl_to_next_is_shunting=True,
        )
        v4_by_rc["1-7SP"] = det_v4_17
        ds_active_v4_by_rc["1-7SP"] = False

    # ЛЗ v6 по всем РЦ без замыкания
    if getattr(opts, "enable_v6", False):
        for rc_id in rc_ids:
            has_lock = False
            if rc_has_route_lock is not None:
                has_lock = rc_has_route_lock.get(rc_id, False)
            if has_lock:
                continue
            v6_by_rc[rc_id] = Variant6Detector(
                rc_id=rc_id,
                ts06=opts.t_s06,
                tlz06=opts.t_lz06,
                tkon=opts.t_kon_v6,
            )
            ds_active_v6_by_rc[rc_id] = False

    # ЛЗ v5 по всем РЦ с замыканием
    if getattr(opts, "enable_v5", False):
        for rc_id in rc_ids:
            has_lock = False
            if rc_has_route_lock is not None:
                has_lock = rc_has_route_lock.get(rc_id, False)
            if not has_lock:
                continue
            v5_by_rc[rc_id] = Variant5Detector(
                rc_id=rc_id,
                ts05=opts.t_s05,
                tlz05=opts.t_lz05,
                tkon=opts.t_kon_v5,
                allow_route_lock_states=getattr(
                    opts,
                    "allow_route_lock_states",
                    False,
                ),
            )
            ds_active_v5_by_rc[rc_id] = False

    # ЛЗ v7 — для бесстрелочной 1P
    v7: Optional[Variant7Detector] = None
    if getattr(opts, "enable_v7", False):
        v7 = Variant7Detector(
            ctrl_rc_id="1P",
            prev_rc_id="10-12SP",
            next_rc_id="1-7SP",
            ts07=opts.t_s07,
            tlz07=opts.t_lz07,
            tkon_v7=opts.t_kon_v7,
            mode="no_adjacent",
        )

    # ЛЗ v9 — один детектор для 1P и её смежных
    v9: Optional[Variant9Detector] = None
    if getattr(opts, "enable_v9", False):
        from .station_visochino_1p import get_station_model_1p

        station_model = get_station_model_1p()
        v9 = Variant9Detector(
            station=station_model,
            ctrl_rc_id="1P",
            adjacent_rc_ids=["10-12SP", "1-7SP"],
            t_s0109=opts.t_s0109,
            t_lz09=opts.t_lz09,
            t_kon_v9=opts.t_kon_v9,
        )

    # ЛС v9 по всем РЦ
    if getattr(opts, "enable_ls9", False):
        for rc_id in rc_ids:
            ls9_by_rc[rc_id] = VariantLS9Detector(
                rc_id=rc_id,
                t_s0109=opts.t_s0109_ls,
                t_s0209=opts.t_s0209_ls,
                t_ls0109=opts.t_ls0109,
                t_ls0209=opts.t_ls0209,
                t_kon=opts.t_kon_ls9,
            )
            ls_active_v9_by_rc[rc_id] = False

    # ЛС v6 — per‑РЦ по аналогии с v12, но через VariantLS6Detector
    if getattr(opts, "enable_ls6", False):
        # для 1-7SP есть замыкание
        if rc_has_route_lock is None or rc_has_route_lock.get("1-7SP", False):
            det_ls6_17 = VariantLS6Detector(
                prev_rc_id="",
                ctrl_rc_id="1-7SP",
                next_rc_id="1P",
                t_s0106=opts.t_s0106_ls,
                t_ls06=opts.t_ls06,
                t_kon=opts.t_kon_ls6,
                signal_prev_to_ctrl_id="М1",
                signal_ctrl_to_next_id="M1",
                ctrl_to_next_is_shunting=True,
            )
            ls6_by_rc["1-7SP"] = det_ls6_17
            ls_active_v6_by_rc["1-7SP"] = False

        # для 10-12SP замыкания нет — не создаём детектор, если явно запрещено
        if rc_has_route_lock is None or rc_has_route_lock.get("10-12SP", False):
            det_ls6_1012 = VariantLS6Detector(
                prev_rc_id="",
                ctrl_rc_id="10-12SP",
                next_rc_id="1P",
                t_s0106=opts.t_s0106_ls,
                t_ls06=opts.t_ls06,
                t_kon=opts.t_kon_ls6,
                signal_prev_to_ctrl_id="ЧМ1",
                signal_ctrl_to_next_id="ЧМ1",
                ctrl_to_next_is_shunting=False,
            )
            ls6_by_rc["10-12SP"] = det_ls6_1012
            ls_active_v6_by_rc["10-12SP"] = False

    # ЛЗ v10
    v10: Optional[Variant10Detector] = None
    if getattr(opts, "enable_v10", False):
        v10 = Variant10Detector(
            ts0110=opts.t_s0110,
            ts0210=opts.t_s0210,
            ts0310=opts.t_s0310,
            tlz10=opts.t_lz10,
            tkon=opts.t_kon_v10,
        )

    # ЛЗ v11
    v11: Optional[Variant11Detector] = None
    if getattr(opts, "enable_v11", False):
        v11 = Variant11Detector(
            ctrl_rc_id="1P",
            sig_ids=("Ч1", "НМ1"),
            t_s11=opts.t_s11,
            t_lz11=opts.t_lz11,
            t_kon=opts.t_kon_v11,
        )

    # ЛЗ v12 — per‑РЦ
    if getattr(opts, "enable_v12", False):
        # для 1-7SP есть замыкание
        if rc_has_route_lock is None or rc_has_route_lock.get("1-7SP", False):
            det_v12_17 = Variant12Detector(
                prev_rc_id="",
                ctrl_rc_id="1-7SP",
                next_rc_id="1P",
                t_s0112=opts.t_s0112,
                t_s0212=opts.t_s0212,
                t_lz12=opts.t_lz12,
                t_kon=opts.t_kon_v12,
            )
            v12_by_rc["1-7SP"] = det_v12_17
            ds_active_v12_by_rc["1-7SP"] = False

        # для 10-12SP замыкания нет — не создаём детектор
        if rc_has_route_lock is None or rc_has_route_lock.get("10-12SP", False):
            det_v12_1012 = Variant12Detector(
                prev_rc_id="",
                ctrl_rc_id="10-12SP",
                next_rc_id="1P",
                t_s0112=opts.t_s0112,
                t_s0212=opts.t_s0212,
                t_lz12=opts.t_lz12,
                t_kon=opts.t_kon_v12,
            )
            v12_by_rc["10-12SP"] = det_v12_1012
            ds_active_v12_by_rc["10-12SP"] = False

    # ЛЗ v13 — per‑РЦ
    if getattr(opts, "enable_v13", False):
        det_v13_1012 = Variant13Detector(
            ctrl_rc_id="10-12SP",
            adj_rc_id="1P",
            signal_id="НМ1",
            t_s0113=opts.t_s0113,
            t_s0213=opts.t_s0213,
            t_lz13=opts.t_lz13,
            t_kon=opts.t_kon_v13,
        )
        v13_by_rc["10-12SP"] = det_v13_1012
        ds_active_v13_by_rc["10-12SP"] = False

        det_v13_17 = Variant13Detector(
            ctrl_rc_id="1-7SP",
            adj_rc_id="1P",
            signal_id="Ч1",
            t_s0113=opts.t_s0113,
            t_s0213=opts.t_s0213,
            t_lz13=opts.t_lz13,
            t_kon=opts.t_kon_v13,
        )
        v13_by_rc["1-7SP"] = det_v13_17
        ds_active_v13_by_rc["1-7SP"] = False

    return DetectorsState(
        v1=Variant1Detector(opts.t_s0101, opts.t_lz01, opts.t_kon_v1)
        if opts.enable_v1
        else None,
        v2=Variant2Detector(
            opts.t_s0102,
            opts.t_s0202,
            opts.t_lz02,
            opts.t_kon_v2,
        )
        if opts.enable_v2
        else None,
        v3=Variant3Detector(
            opts.t_s0103,
            opts.t_s0203,
            opts.t_lz03,
            opts.t_kon_v3,
        )
        if opts.enable_v3
        else None,
        v4_by_rc=v4_by_rc,
        v5_by_rc=v5_by_rc,
        v6_by_rc=v6_by_rc,
        v7=v7,
        v8=Variant8Detector(
            opts.t_s0108,
            opts.t_s0208,
            opts.t_lz08,
            opts.t_kon_v8,
        )
        if opts.enable_v8
        else None,
        v9=v9,
        v10=v10,
        v11=v11,
        v12_by_rc=v12_by_rc,
        v13_by_rc=v13_by_rc,
        ls1=VariantLS1Detector(
            opts.t_c0101_ls,
            opts.t_ls01,
            opts.t_kon_ls1,
        )
        if opts.enable_ls1
        else None,
        ls2=VariantLS2Detector(
            t_s0102=opts.t_s0102_ls,
            t_s0202=opts.t_s0202_ls,
            t_ls0102=opts.t_ls0102,
            t_ls0202=opts.t_ls0202,
            t_kon_ls2=opts.t_kon_ls2,
        )
        if opts.enable_ls2
        else None,
        ls4=VariantLS4Detector(
            opts.t_s0104_ls,
            opts.t_s0204_ls,
            opts.t_ls0104,
            opts.t_ls0204,
            opts.t_kon_ls4,
        )
        if opts.enable_ls4
        else None,
        ls5=VariantLS5Detector(
            prev_rc_id="10-12SP",
            ctrl_rc_id="1P",
            next_rc_id="1-7SP",
            t_s0105=opts.t_s0105_ls,
            t_ls05=opts.t_ls05,
            t_kon=opts.t_kon_ls5,
            ever_closed=True,
        )
        if opts.enable_ls5
        else None,
        ls6_by_rc=ls6_by_rc,
        ls9_by_rc=ls9_by_rc,
        ls_active_v9_by_rc=ls_active_v9_by_rc if ls9_by_rc else None,
        ls_active_v6_by_rc=ls_active_v6_by_rc if ls6_by_rc else None,
        ds_active_v6_by_rc=ds_active_v6_by_rc if v6_by_rc else None,
        ds_active_v5_by_rc=ds_active_v5_by_rc if v5_by_rc else None,
        ds_active_v12_by_rc=ds_active_v12_by_rc if v12_by_rc else None,
        ds_active_v13_by_rc=ds_active_v13_by_rc if v13_by_rc else None,
        ds_active_v4_by_rc=ds_active_v4_by_rc if v4_by_rc else None,
    )


def run_detectors(
    state: DetectorsState,
    step: ScenarioStep,
    dt_interval: float,
    history: List[ScenarioStep] | None = None,
    idx: int | None = None,
) -> Tuple[DetectorsState, DetectorsResult]:
    res = DetectorsResult()

    modes = getattr(step, "modes", {}) or {}
    step_ctrl_rc_id = modes.get("ctrl_rc_id", None)

    # ЛЗ v1
    if state.v1 is not None:
        o_v1, c_v1 = state.v1.update(step, dt_interval)
        if o_v1:
            state.ds_active_v1 = True
            res.opened_v1 = True
        if c_v1:
            state.ds_active_v1 = False
            res.closed_v1 = True

    # ЛЗ v2
    if state.v2 is not None:
        o_v2, c_v2 = state.v2.update(step, dt_interval)
        if o_v2:
            state.ds_active_v2 = True
            res.opened_v2 = True
        if c_v2:
            state.ds_active_v2 = False
            res.closed_v2 = True

    # ЛЗ v3
    if state.v3 is not None:
        o_v3, c_v3 = state.v3.update(step, dt_interval)
        if o_v3:
            state.ds_active_v3 = True
            res.opened_v3 = True
        if c_v3:
            state.ds_active_v3 = False
            res.closed_v3 = True

    # ЛЗ v4 — per‑РЦ
    state.ds_active_v4 = False
    state.ds_ctrl_rc_v4 = None
    if state.v4_by_rc:
        if state.ds_active_v4_by_rc is None:
            state.ds_active_v4_by_rc = {}
        for rc_id, det in state.v4_by_rc.items():
            o_v4, c_v4 = det.update(step, dt_interval)
            if o_v4:
                state.ds_active_v4_by_rc[rc_id] = True
                state.ds_ctrl_rc_v4 = rc_id
                res.opened_v4 = True
            if c_v4:
                state.ds_active_v4_by_rc[rc_id] = False
                res.closed_v4 = True

        if state.ds_active_v4_by_rc:
            state.ds_active_v4 = any(state.ds_active_v4_by_rc.values())
            if not state.ds_active_v4:
                state.ds_ctrl_rc_v4 = None

    # ЛЗ v5 — per‑РЦ с замыканием
    if state.v5_by_rc:
        if state.ds_active_v5_by_rc is None:
            state.ds_active_v5_by_rc = {}
        for rc_id, det in state.v5_by_rc.items():
            o_v5, c_v5 = det.update(step, dt_interval)
            if o_v5:
                state.ds_active_v5_by_rc[rc_id] = True
                state.ds_ctrl_rc_v5 = rc_id
                res.opened_v5 = True
            if c_v5:
                state.ds_active_v5_by_rc[rc_id] = False
                res.closed_v5 = True
        if state.ds_active_v5_by_rc and not any(state.ds_active_v5_by_rc.values()):
            state.ds_ctrl_rc_v5 = None

    # ЛЗ v6 — per‑РЦ без замыкания
    if state.v6_by_rc:
        if state.ds_active_v6_by_rc is None:
            state.ds_active_v6_by_rc = {}
        for rc_id, det in state.v6_by_rc.items():
            o_v6, c_v6 = det.update(step, dt_interval)
            if o_v6:
                state.ds_active_v6_by_rc[rc_id] = True
                state.ds_ctrl_rc_v6 = rc_id
                res.opened_v6 = True
            if c_v6:
                state.ds_active_v6_by_rc[rc_id] = False
                res.closed_v6 = True
        if state.ds_active_v6_by_rc and not any(state.ds_active_v6_by_rc.values()):
            state.ds_ctrl_rc_v6 = None

    # ЛЗ v7
    if state.v7 is not None:
        o_v7, c_v7 = state.v7.update(step, dt_interval)
        if o_v7:
            state.ds_active_v7 = True
            res.opened_v7 = True
        if c_v7:
            state.ds_active_v7 = False
            res.closed_v7 = True

    # ЛЗ v8
    if state.v8 is not None:
        o_v8, c_v8 = state.v8.update(step, dt_interval)
        if o_v8:
            state.ds_active_v8 = True
            res.opened_v8 = True
        if c_v8:
            state.ds_active_v8 = False
            res.closed_v8 = True

    # ЛЗ v9
    if state.v9 is not None:
        o_v9, c_v9 = state.v9.update(step, dt_interval)
        if o_v9:
            state.ds_active_v9 = True
            res.opened_v9 = True
        if c_v9:
            state.ds_active_v9 = False
            res.closed_v9 = True

    # ЛЗ v10
    if state.v10 is not None:
        o_v10, c_v10 = state.v10.update(step, dt_interval)
        if o_v10:
            state.ds_active_v10 = True
            res.opened_v10 = True
        if c_v10:
            state.ds_active_v10 = False
            res.closed_v10 = True

    # ЛЗ v11
    if state.v11 is not None:
        o_v11, c_v11 = state.v11.update(step, dt_interval)
        if o_v11:
            state.ds_active_v11 = True
            res.opened_v11 = True
        if c_v11:
            state.ds_active_v11 = False
            res.closed_v11 = True

    # ЛЗ v12 — per‑РЦ
    state.ds_active_v12 = False
    state.ds_ctrl_rc_v12 = None
    if state.v12_by_rc:
        if state.ds_active_v12_by_rc is None:
            state.ds_active_v12_by_rc = {}
        for rc_id, det in state.v12_by_rc.items():
            o_v12, c_v12 = det.update(step, dt_interval)
            if o_v12:
                state.ds_active_v12_by_rc[rc_id] = True
                state.ds_ctrl_rc_v12 = rc_id
                res.opened_v12 = True
            if c_v12:
                state.ds_active_v12_by_rc[rc_id] = False
                res.closed_v12 = True

        if state.ds_active_v12_by_rc:
            state.ds_active_v12 = any(state.ds_active_v12_by_rc.values())
            if not state.ds_active_v12:
                state.ds_ctrl_rc_v12 = None

    # ЛЗ v13 — per‑РЦ
    state.ds_active_v13 = False
    state.ds_ctrl_rc_v13 = None
    if state.v13_by_rc:
        if state.ds_active_v13_by_rc is None:
            state.ds_active_v13_by_rc = {}
        for rc_id, det in state.v13_by_rc.items():
            o_v13, c_v13 = det.update(step, dt_interval)
            if o_v13:
                state.ds_active_v13_by_rc[rc_id] = True
                state.ds_ctrl_rc_v13 = rc_id
                res.opened_v13 = True
            if c_v13:
                state.ds_active_v13_by_rc[rc_id] = False
                res.closed_v13 = True

        if state.ds_active_v13_by_rc:
            state.ds_active_v13 = any(state.ds_active_v13_by_rc.values())
            if not state.ds_active_v13:
                state.ds_ctrl_rc_v13 = None

    # ЛС v1
    if state.ls1 is not None:
        o_ls1, c_ls1 = state.ls1.update(step, dt_interval)
        if o_ls1:
            state.ls_active_v1 = True
            res.opened_ls1 = True
        if c_ls1:
            state.ls_active_v1 = False
            res.closed_ls1 = True

    # ЛС v2
    if state.ls2 is not None:
        o_ls2, c_ls2 = state.ls2.update(step, dt_interval)
        if o_ls2:
            state.ls_active_v2 = True
            res.opened_ls2 = True
        if c_ls2:
            state.ls_active_v2 = False
            res.closed_ls2 = True

    # ЛС v4
    if state.ls4 is not None:
        test_ls4_active = get_mode(step, "test_check_ls4_active")
        if not test_ls4_active:
            o_ls4, c_ls4 = state.ls4.update(step, dt_interval)
            if o_ls4:
                state.ls_active_v4 = True
                res.opened_ls4 = True
            if c_ls4:
                state.ls_active_v4 = False
                res.closed_ls4 = True

    # ЛС v5
    if state.ls5 is not None:
        test_ls5_active = get_mode(step, "test_check_ls5_active")
        if not test_ls5_active:
            o_ls5, a_ls5, c_ls5 = state.ls5.update(step, dt_interval)
            if o_ls5:
                state.ls_active_v5 = True
                res.opened_ls5 = True
            state.ls_active_v5 = a_ls5
            if c_ls5:
                state.ls_active_v5 = False
                res.closed_ls5 = True

    # ЛС v6 — per‑РЦ
    if state.ls6_by_rc:
        if state.ls_active_v6_by_rc is None:
            state.ls_active_v6_by_rc = {}
        for rc_id, det in state.ls6_by_rc.items():
            o_ls6, c_ls6 = det.update(step, dt_interval)
            if o_ls6:
                state.ls_active_v6_by_rc[rc_id] = True
                res.opened_ls6 = True
            if c_ls6:
                state.ls_active_v6_by_rc[rc_id] = False
                res.closed_ls6 = True

    # ЛС v9 — per‑РЦ
    if state.ls9_by_rc and history is not None and idx is not None:
        test_ls9_active = get_mode(step, "test_check_ls9_active")
        if not test_ls9_active:
            for rc_id, det in state.ls9_by_rc.items():
                o_ls9, c_ls9 = det.update(history, idx, dt_interval)
                if o_ls9:
                    state.ls_active_v9_by_rc[rc_id] = True
                    res.opened_ls9 = True
                if c_ls9:
                    state.ls_active_v9_by_rc[rc_id] = False
                    res.closed_ls9 = True

    return state, res

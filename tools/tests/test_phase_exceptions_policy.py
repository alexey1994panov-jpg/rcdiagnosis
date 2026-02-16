# -*- coding: utf-8 -*-
from core.detectors_engine import (
    DetectorsConfig,
    init_detectors_engine,
    update_detectors,
)


def test_ls1_final_phase_has_exception_keys():
    cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_ls1=True,
        ts01_ls1=1.0,
        tlz_ls1=1.0,
        tkon_ls1=3.0,
        enable_ls_exc_mu=True,
    )
    state = init_detectors_engine(cfg=cfg, rc_ids=["59", "108", "83"])
    assert state.ls1 is not None
    final_phases = [p for p in state.ls1.config.phases if int(p.next_phase_id) < 0]
    assert final_phases, "У LS1 должна быть финальная фаза открытия"
    assert "exc_ls_mu_active" in final_phases[0].abort_exception_keys


def test_ls1_open_blocked_by_phase_exception():
    cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_ls1=True,
        ts01_ls1=1.0,
        tlz_ls1=1.0,
        tkon_ls1=3.0,
        enable_ls_exc_mu=True,
    )
    state = init_detectors_engine(cfg=cfg, rc_ids=["59", "108", "83"])

    # Шаг 1: фаза 0 LS1 (C0101) выполняется.
    state, _ = update_detectors(
        det_state=state,
        t=0.0,
        dt=1.0,
        rc_states={"59": 3, "108": 6, "83": 3},
        switch_states={"87": 3, "88": 3, "110": 3},
        signal_states={},
        topology_info={"ctrl_rc_id": "108", "effective_prev_rc": "59", "effective_next_rc": "83"},
        cfg=cfg,
        modes={"prev_nc": True, "next_nc": False},
    )

    # Шаг 2: маска финальной фазы выполнена, но исключение должно блокировать открытие.
    state, result = update_detectors(
        det_state=state,
        t=1.0,
        dt=1.0,
        rc_states={"59": 3, "108": 3, "83": 3},
        switch_states={"87": 3, "88": 3, "110": 3},
        signal_states={},
        topology_info={"ctrl_rc_id": "108", "effective_prev_rc": "59", "effective_next_rc": "83"},
        cfg=cfg,
        modes={"prev_nc": True, "next_nc": False, "exc_ls_mu_active": True},
    )

    assert "lls_1_open" not in result.flags


def test_lz3_phase2_blocked_by_dsp_timeout_before_phase3():
    cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz3=True,
        ts01_lz3=1.0,
        tlz_lz3=1.0,
        ts02_lz3=1.0,
        tkon_lz3=2.0,
        enable_lz_exc_dsp=True,
    )
    state = init_detectors_engine(cfg=cfg, rc_ids=["59", "108", "83"])
    assert state.v3 is not None

    # Шаг 1: фаза 1 (id=0 -> id=1) по маске 101.
    state, _ = update_detectors(
        det_state=state,
        t=0.0,
        dt=1.0,
        rc_states={"59": 6, "108": 3, "83": 6},
        switch_states={"87": 3, "88": 3, "110": 3},
        signal_states={},
        topology_info={"ctrl_rc_id": "108", "effective_prev_rc": "59", "effective_next_rc": "83"},
        cfg=cfg,
        modes={},
    )
    assert state.v3.current_phase_id == 1

    # Шаг 2: на фазе 2 (id=1, маска 111) активируем exc_lz_dsp_timeout.
    # Детектор не должен перейти на следующую фазу (id=2), открытие запрещено.
    state, result = update_detectors(
        det_state=state,
        t=1.0,
        dt=1.0,
        rc_states={"59": 6, "108": 6, "83": 6},
        switch_states={"87": 3, "88": 3, "110": 3},
        signal_states={},
        topology_info={"ctrl_rc_id": "108", "effective_prev_rc": "59", "effective_next_rc": "83"},
        cfg=cfg,
        modes={"exc_lz_dsp_timeout": True},
    )
    assert state.v3.current_phase_id != 2
    assert "llz_v3_open" not in result.flags


def test_lz_dsp_exception_applies_only_for_selected_variants():
    cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108",
        next_rc_name="83",
        enable_lz3=True,
        enable_lz8=True,
        ts01_lz3=1.0,
        ts02_lz3=1.0,
        tlz_lz3=1.0,
        tkon_lz3=1.0,
        ts01_lz8=1.0,
        ts02_lz8=1.0,
        tlz_lz8=1.0,
        tkon_lz8=1.0,
        enable_lz_exc_dsp=True,
        lz_exc_dsp_variants=[8],
    )
    state = init_detectors_engine(cfg=cfg, rc_ids=["59", "108", "83"])
    assert state.v3 is not None
    assert state.v8 is not None

    v3_has_dsp = any(
        "exc_lz_dsp_timeout" in tuple(p.abort_exception_keys or ())
        for p in state.v3.config.phases
    )
    v8_has_dsp = any(
        "exc_lz_dsp_timeout" in tuple(p.abort_exception_keys or ())
        for p in state.v8.detectors[0].config.phases
    )
    assert v3_has_dsp is False
    assert v8_has_dsp is True

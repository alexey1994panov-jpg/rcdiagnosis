from engine.station_visochino_1p import get_station_model_1p
from engine.detectors_runner_1p import init_detectors, run_detectors
from engine.config_1p import VariantOptions
import engine.config_1p as cfg
from engine.types_1p import ScenarioStep


def make_step(rc_states=None, switch_states=None, signal_states=None, modes=None):
    return ScenarioStep(
        t=0.0,
        rc_states=rc_states or {},
        switch_states=switch_states or {},
        modes=modes or {},
        signal_states=signal_states or {},
    )


def make_opts(**overrides) -> VariantOptions:
    vals = dict(
        # v1–v4, v7–v13 выключаем
        t_s0101=cfg.T_S0101,
        t_lz01=cfg.T_LZ01,
        t_kon_v1=cfg.T_KON,
        enable_v1=False,

        t_s0102=cfg.T_S0102_DEFAULT,
        t_s0202=cfg.T_S0202_DEFAULT,
        t_lz02=cfg.T_LZ02_DEFAULT,
        t_kon_v2=cfg.T_KON,
        enable_v2=False,

        t_s0103=cfg.T_S0103_DEFAULT,
        t_s0203=cfg.T_S0203_DEFAULT,
        t_lz03=cfg.T_LZ03_DEFAULT,
        t_kon_v3=cfg.T_KON,
        enable_v3=False,

        t_s0401=cfg.T_S0401_DEFAULT,
        t_lz04=cfg.T_LZ04_DEFAULT,
        t_kon_v4=cfg.T_KON_V4_DEFAULT,
        enable_v4=False,

        # v5 (важен t_pk)
        t_s05=cfg.T_S05_DEFAULT,
        t_lz05=cfg.T_LZ05_DEFAULT,
        t_pk=cfg.T_PK,
        t_kon_v5=cfg.T_KON_V5_DEFAULT,
        enable_v5=False,

        # v6
        t_s06=cfg.T_S06_DEFAULT,
        t_lz06=cfg.T_LZ06_DEFAULT,
        t_kon_v6=cfg.T_KON_V6_DEFAULT,
        enable_v6=False,

        # v7
        t_s07=cfg.T_S07_DEFAULT,
        t_lz07=cfg.T_LZ07_DEFAULT,
        t_kon_v7=cfg.T_KON_V7_DEFAULT,
        enable_v7=False,

        # v8
        t_s0108=cfg.T_S0108_DEFAULT,
        t_s0208=cfg.T_S0208_DEFAULT,
        t_lz08=cfg.T_LZ08_DEFAULT,
        t_kon_v8=getattr(cfg, "T_KON_V8_DEFAULT", cfg.T_KON),
        enable_v8=False,

        # v9
        t_s0109=cfg.T_S0109_DEFAULT,
        t_lz09=cfg.T_LZ09_DEFAULT,
        t_kon_v9=cfg.T_KON_V9_DEFAULT,
        enable_v9=False,

        # v10
        t_s0110=getattr(cfg, "TS0110_DEFAULT", 3.0),
        t_s0210=getattr(cfg, "TS0210_DEFAULT", 3.0),
        t_s0310=getattr(cfg, "TS0310_DEFAULT", 3.0),
        t_lz10=getattr(cfg, "TLZ10_DEFAULT", 3.0),
        t_kon_v10=getattr(cfg, "TKON_V10_DEFAULT", 3.0),
        enable_v10=False,

        # v11
        t_s11=cfg.T_S11_DEFAULT,
        t_lz11=cfg.T_LZ11_DEFAULT,
        t_kon_v11=cfg.T_KON_V11_DEFAULT,
        enable_v11=False,

        # v12
        t_s0112=cfg.T_S0112_DEFAULT,
        t_s0212=cfg.T_S0212_DEFAULT,
        t_lz12=cfg.T_LZ12_DEFAULT,
        t_kon_v12=cfg.T_KON_V12_DEFAULT if hasattr(cfg, "ТКОН_V12_DEFAULT") else cfg.T_KON_V12_DEFAULT,
        enable_v12=False,

        # v13
        t_s0113=cfg.T_S0113_DEFAULT,
        t_s0213=cfg.T_S0213_DEFAULT,
        t_lz13=cfg.T_LZ13_DEFAULT,
        t_kon_v13=cfg.T_KON_V13_DEFAULT if hasattr(cfg, "ТКОН_V13_DEFAULT") else cfg.T_KON_V13_DEFAULT,
        enable_v13=False,

        # все ЛС выключены
        t_c0101_ls=cfg.T_C0101_LS_DEFAULT,
        t_ls01=cfg.T_LS01_DEFAULT,
        t_kon_ls1=cfg.T_KON_LS_DEFAULT,
        enable_ls1=False,

        t_s0102_ls=cfg.T_S0102_LS_DEFAULT,
        t_s0202_ls=cfg.T_S0202_LS_DEFAULT,
        t_ls0102=cfg.T_LS0102_DEFAULT,
        t_ls0202=cfg.T_LS0202_DEFAULT,
        t_kon_ls2=getattr(cfg, "T_KON_LS2_DEFAULT", cfg.T_KON_LS_DEFAULT),
        enable_ls2=False,

        t_s0104_ls=cfg.T_S0104_LS_DEFAULT,
        t_s0204_ls=cfg.T_S0204_LS_DEFAULT,
        t_ls0104=cfg.T_LS0104_DEFAULT,
        t_ls0204=cfg.T_LS0204_DEFAULT,
        t_kon_ls4=cfg.T_KON_LS4_DEFAULT,
        enable_ls4=False,

        t_s0105_ls=cfg.T_S0105_LS_DEFAULT,
        t_ls05=cfg.T_LS05_DEFAULT,
        t_kon_ls5=cfg.T_KON_LS5_DEFAULT,
        enable_ls5=False,

        t_s0106_ls=cfg.T_S0106_LS_DEFAULT,
        t_ls06=cfg.T_LS06_DEFAULT,
        t_kon_ls6=cfg.T_KON_LS6_DEFAULT,
        enable_ls6=False,

        t_s0109_ls=cfg.T_S0109_LS_DEFAULT,
        t_s0209_ls=cfg.T_S0209_LS_DEFAULT,
        t_ls0109=cfg.T_LS0109_DEFAULT,
        t_ls0209=cfg.T_LS0209_DEFAULT,
        t_kon_ls9=cfg.T_KON_LS9_DEFAULT,
        enable_ls9=False,

        # паузы
        t_pause_v1=cfg.T_PAUSE_DEFAULT,
        t_pause_v2=cfg.T_PAUSE_DEFAULT,
        t_pause_v3=cfg.T_PAUSE_DEFAULT,
        t_pause_v4=cfg.T_PAUSE_DEFAULT,
        t_pause_v5=cfg.T_PAUSE_DEFAULT,
        t_pause_v6=cfg.T_PAUSE_DEFAULT,
        t_pause_v7=cfg.T_PAUSE_DEFAULT,
        t_pause_v8=cfg.T_PAUSE_DEFAULT,
        t_pause_v9=cfg.T_PAUSE_DEFAULT,
        t_pause_v10=cfg.T_PAUSE_DEFAULT,
        t_pause_v11=cfg.T_PAUSE_DEFAULT,
        t_pause_v12=cfg.T_PAUSE_DEFAULT,
        t_pause_v13=cfg.T_PAUSE_DEFAULT,
        t_pause_ls1=cfg.T_PAUSE_DEFAULT,
        t_pause_ls2=cfg.T_PAUSE_DEFAULT,
        t_pause_ls4=cfg.T_PAUSE_DEFAULT,
        t_pause_ls5=cfg.T_PAUSE_DEFAULT,
        t_pause_ls6=cfg.T_PAUSE_DEFAULT,
        t_pause_ls9=cfg.T_PAUSE_DEFAULT,

        # исключения
        t_mu=cfg.T_MU,
        t_recent_ls=cfg.T_RECENT_LS,
        t_min_maneuver_v8=cfg.T_MIN_MANEUVER_V8,
        enable_lz_exc_mu=False,
        enable_lz_exc_recent_ls=False,
        enable_lz_exc_dsp=False,
        enable_ls_exc_mu=False,
        enable_ls_exc_after_lz=False,
        enable_ls_exc_dsp=False,
        t_ls_mu=cfg.T_LS_MU,
        t_ls_after_lz=cfg.T_LS_AFTER_LZ,
        t_ls_dsp=cfg.T_LS_DSP,
        allow_route_lock_states=False,
    )
    vals.update(overrides)
    return VariantOptions(**vals)


def test_v5_v6_on_locked_and_unlocked_rc():
    station = get_station_model_1p()

    # Включаем только v5 и v6 (таймеры можно оставить дефолтные)
    opts = make_opts(
        enable_v5=True,
        enable_v6=True,
    )

    state = init_detectors(opts, station.rc_ids, station.rc_has_route_lock, station)

    # --- проверяем распределение v5/v6 по РЦ ---

    # v5 только на РЦ с route_lock == True
    for rc_id in state.v5_by_rc.keys():
        assert station.rc_has_route_lock.get(rc_id, False), f"v5 создан на немаршрутной РЦ {rc_id}"

    # v6 только на РЦ с route_lock == False
    for rc_id in state.v6_by_rc.keys():
        assert not station.rc_has_route_lock.get(rc_id, False), f"v6 создан на маршрутной РЦ {rc_id}"

    # sanity: в модели должен быть хотя бы один locked и один unlocked РЦ с соответствующими вариантами
    assert any(station.rc_has_route_lock.get(rc, False) for rc in state.v5_by_rc.keys()), \
        "v5 не привязан ни к одной маршрутной РЦ"
    assert any(not station.rc_has_route_lock.get(rc, False) for rc in state.v6_by_rc.keys()), \
        "v6 не привязан ни к одной немаршрутной РЦ"

    # --- лёгкий прогон нескольких шагов, чтобы убедиться, что детекторы живые ---

    free_states = {rc: 3 for rc in station.rc_ids}
    # шаг 1: всё свободно
    state, _ = run_detectors(state, make_step(rc_states=free_states), 1.0)

    # шаг 2: занимаем любую locked РЦ (если есть) и любую unlocked
    locked_rc_ids = [rc for rc, locked in station.rc_has_route_lock.items() if locked]
    unlocked_rc_ids = [rc for rc, locked in station.rc_has_route_lock.items() if not locked]

    rc_states = dict(free_states)
    if locked_rc_ids:
        rc_states[locked_rc_ids[0]] = 6
    if unlocked_rc_ids:
        rc_states[unlocked_rc_ids[0]] = 6

    state, _ = run_detectors(state, make_step(rc_states=rc_states), 1.0)

    # шаг 3: снова всё свободно — главное, что ничего не упало
    state, _ = run_detectors(state, make_step(rc_states=free_states), 1.0)

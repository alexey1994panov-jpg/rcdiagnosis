# -*- coding: utf-8 -*-
# station_detectors_factory.py вЂ” СЃР±РѕСЂРєР° DetectorsConfig РґР»СЏ РІР°СЂРёР°РЅС‚РѕРІ lz1/lz2

from station.station_model import load_station_from_config
from station.station_detectors_config import DETECTORS_CONFIG
from core.detectors_engine import DetectorsConfig as LocalDetectorsConfig
from station.station_config import NODES  # С‡С‚РѕР±С‹ РІР·СЏС‚СЊ NAME РїРѕ ID


def _get_rc_name(rc_id: str) -> str:
    raw = NODES.get(rc_id, {})
    return raw.get("name", rc_id)


def build_detectors_config_for_rc(ctrl_rc_id: str) -> LocalDetectorsConfig:
    """
    РЎС‚СЂРѕРёС‚ Р»РѕРєР°Р»СЊРЅС‹Р№ DetectorsConfig РґР»СЏ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕР№ Р Р¦.

    РСЃРїРѕР»СЊР·СѓРµС‚:
    - РёРјРµРЅР° prev/ctrl/next РёР· StationModel (РїРѕ РЅРѕРІРѕР№ С‚РѕРїРѕР»РѕРіРёРё),
    - С‚Р°Р№РјРёРЅРіРё lz1/lz2 Рё enable_lz1/enable_lz2 РёР· DETECTORS_CONFIG.
    """
    model = load_station_from_config()
    node = model.rc_nodes.get(ctrl_rc_id)
    if node is None:
        raise ValueError(f"Unknown RC id {ctrl_rc_id!r} in StationModel")

    # РРјСЏ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕР№ СЃРµРєС†РёРё
    ctrl_rc_name = _get_rc_name(ctrl_rc_id)

    # prev/next: Р±РµСЂС‘Рј РїРµСЂРІРѕРіРѕ СЃРѕСЃРµРґР° РїРѕ prev_links/next_links РёР· РјРѕРґРµР»Рё
    prev_rc_name = ""
    next_rc_name = None

    if node.prev_links:
        prev_rc_id = node.prev_links[0][0]
        prev_rc_name = _get_rc_name(prev_rc_id)

    if node.next_links:
        next_rc_id = node.next_links[0][0]
        next_rc_name = _get_rc_name(next_rc_id)

    # Р“Р»РѕР±Р°Р»СЊРЅС‹Рµ С‚Р°Р№РјРёРЅРіРё Рё per-RC РІРєР»СЋС‡РµРЅРёРµ
    global_cfg = DETECTORS_CONFIG
    rc_cfg = global_cfg.get_rc_config(ctrl_rc_id)

    gt = global_cfg.global_timings

    # lz1
    ts01_lz1 = gt.ts01_lz1
    tlz_lz1 = gt.tlz_lz1
    tkon_lz1 = gt.tkon_lz1
    enable_lz1 = rc_cfg.enable_lz1

    # lz2
    ts01_lz2 = gt.ts01_lz2
    ts02_lz2 = gt.ts02_lz2
    tlz_lz2 = gt.tlz_lz2
    tkon_lz2 = gt.tkon_lz2
    enable_lz2 = rc_cfg.enable_lz2
    # lz3
    ts01_lz3 = gt.ts01_lz3
    ts02_lz3 = gt.ts02_lz3
    tlz_lz3 = gt.tlz_lz3
    tkon_lz3 = gt.tkon_lz3
    enable_lz3 = rc_cfg.enable_lz3

    # lz4
    ts01_lz4 = gt.ts01_lz4
    tlz_lz4 = gt.tlz_lz4
    tkon_lz4 = gt.tkon_lz4
    enable_lz4 = rc_cfg.enable_lz4

    # lz7
    ts01_lz7 = gt.ts01_lz7
    tlz_lz7 = gt.tlz_lz7
    tkon_lz7 = gt.tkon_lz7
    enable_lz7 = rc_cfg.enable_lz7

    # lz9
    enable_lz9 = rc_cfg.enable_lz9
    ts01_lz9 = gt.ts01_lz9
    tlz_lz9 = gt.tlz_lz9
    tkon_lz9 = gt.tkon_lz9

    # lz11
    enable_lz11 = rc_cfg.enable_lz11
    ts01_lz11 = gt.ts01_lz11
    tlz_lz11 = gt.tlz_lz11
    tkon_lz11 = gt.tkon_lz11
    # Р”Р»СЏ LZ11/13/10 Р·Р°С‚С‹РєР°РµРј СЃРёРіРЅР°Р»С‹ РїРѕРєР° С‡С‚Рѕ None, РµСЃР»Рё РјРѕРґРµР»СЊ РЅРµ РґР°РµС‚
    # (Р’ СЂРµР°Р»СЊРЅРѕСЃС‚Рё РѕРЅРё РїСЂРёРґСѓС‚ РёР· config РёР»Рё Р»РѕРіРёРєРё РїРѕРґР±РѕСЂР°)

    # lz13
    enable_lz13 = rc_cfg.enable_lz13
    ts01_lz13 = gt.ts01_lz13
    ts02_lz13 = gt.ts02_lz13
    tlz_lz13 = gt.tlz_lz13
    tkon_lz13 = gt.tkon_lz13

    # lz10
    enable_lz10 = rc_cfg.enable_lz10
    ts01_lz10 = gt.ts01_lz10
    ts02_lz10 = gt.ts02_lz10
    ts03_lz10 = gt.ts03_lz10
    tlz_lz10 = gt.tlz_lz10
    tkon_lz10 = gt.tkon_lz10

    # ls6
    enable_ls6 = rc_cfg.enable_ls6
    ts01_ls6 = gt.ts01_ls6
    tlz_ls6 = gt.tlz_ls6
    tkon_ls6 = gt.tkon_ls6

    # ls4
    enable_ls4 = rc_cfg.enable_ls4
    ts01_ls4 = gt.ts01_ls4
    tlz_ls4 = gt.tlz_ls4
    tkon_ls4 = gt.tkon_ls4

    # ls5
    enable_ls5 = rc_cfg.enable_ls5
    ts01_ls5 = gt.ts01_ls5
    tlz_ls5 = gt.tlz_ls5
    tkon_ls5 = gt.tkon_ls5

    return LocalDetectorsConfig(
        ctrl_rc_id=ctrl_rc_id,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
        ts01_lz1=ts01_lz1, tlz_lz1=tlz_lz1, tkon_lz1=tkon_lz1, enable_lz1=enable_lz1,
        ts01_lz2=ts01_lz2, ts02_lz2=ts02_lz2, tlz_lz2=tlz_lz2, tkon_lz2=tkon_lz2, enable_lz2=enable_lz2,
        ts01_lz3=ts01_lz3, ts02_lz3=ts02_lz3, tlz_lz3=tlz_lz3, tkon_lz3=tkon_lz3, enable_lz3=enable_lz3,
        ts01_lz4=ts01_lz4, tlz_lz4=tlz_lz4, tkon_lz4=tkon_lz4, enable_lz4=enable_lz4,
        ts01_lz7=ts01_lz7, tlz_lz7=tlz_lz7, tkon_lz7=tkon_lz7, enable_lz7=enable_lz7,
        enable_lz9=enable_lz9, ts01_lz9=ts01_lz9, tlz_lz9=tlz_lz9, tkon_lz9=tkon_lz9,
        enable_lz11=enable_lz11, ts01_lz11=ts01_lz11, tlz_lz11=tlz_lz11, tkon_lz11=tkon_lz11,
        enable_lz13=enable_lz13, ts01_lz13=ts01_lz13, ts02_lz13=ts02_lz13, tlz_lz13=tlz_lz13, tkon_lz13=tkon_lz13,
        enable_lz10=enable_lz10, ts01_lz10=ts01_lz10, ts02_lz10=ts02_lz10, ts03_lz10=ts03_lz10, tlz_lz10=tlz_lz10, tkon_lz10=tkon_lz10,
        enable_ls6=enable_ls6, ts01_ls6=ts01_ls6, tlz_ls6=tlz_ls6, tkon_ls6=tkon_ls6,
        enable_ls4=enable_ls4, ts01_ls4=ts01_ls4, tlz_ls4=tlz_ls4, tkon_ls4=tkon_ls4,
        enable_ls5=enable_ls5, ts01_ls5=ts01_ls5, tlz_ls5=tlz_ls5, tkon_ls5=tkon_ls5,
        enable_lz_exc_mu=gt.enable_lz_exc_mu,
        enable_lz_exc_recent_ls=gt.enable_lz_exc_recent_ls,
        enable_lz_exc_dsp=gt.enable_lz_exc_dsp,
        enable_ls_exc_mu=gt.enable_ls_exc_mu,
        enable_ls_exc_after_lz=gt.enable_ls_exc_after_lz,
        enable_ls_exc_dsp=gt.enable_ls_exc_dsp,
        t_mu=gt.t_mu,
        t_recent_ls=gt.t_recent_ls,
        t_min_maneuver_v8=gt.t_min_maneuver_v8,
        t_ls_mu=gt.t_ls_mu,
        t_ls_after_lz=gt.t_ls_after_lz,
        t_ls_dsp=gt.t_ls_dsp,
    )


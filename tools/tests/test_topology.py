# -*- coding: utf-8 -*-
"""
РќР°Р±РѕСЂ smokeвЂ‘ Рё РєРѕРЅСЃРёСЃС‚РµРЅС‚вЂ‘С‚РµСЃС‚РѕРІ РґР»СЏ С‚РѕРїРѕР»РѕРіРёРё СЃС‚Р°РЅС†РёРё.

РџСЂРѕРІРµСЂСЏРµС‚:
- С†РµР»РѕСЃС‚РЅРѕСЃС‚СЊ NODES/GROUPS;
- РєРѕСЂСЂРµРєС‚РЅРѕСЃС‚СЊ SWITCH_LOGIC РѕС‚РЅРѕСЃРёС‚РµР»СЊРЅРѕ NODES/RC_SECTIONS;
- РєРѕСЂСЂРµРєС‚РЅРѕСЃС‚СЊ SIGNALS_LOGIC РѕС‚РЅРѕСЃРёС‚РµР»СЊРЅРѕ NODES/SWITCH_LOGIC;
- Р±Р°Р·РѕРІСѓСЋ СЃРѕРіР»Р°СЃРѕРІР°РЅРЅРѕСЃС‚СЊ СЃ station_model/UniversalTopologyManager.
"""

import importlib

from station import station_config as cfg
from station import station_rc_sections as rc_sections_mod
from station import station_switch_logic as sw_logic_mod
from station import station_signals_logic as sig_logic_mod
from station import station_model as model_mod
from core.topology_manager import UniversalTopologyManager


def test_groups_rc_ids_exist():
    """Р’СЃРµ rc_ids РёР· GROUPS РµСЃС‚СЊ РІ NODES Рё РёРјРµСЋС‚ type == 1."""
    rc_ids = cfg.GROUPS["rc_ids"]
    for rc_id in rc_ids:
        assert rc_id in cfg.NODES, f"rc_id {rc_id} РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ РІ NODES"
        node = cfg.NODES[rc_id]
        assert node.get("type") == 1, f"rc_id {rc_id} РЅРµ type=1 (Р Р¦), Р° {node.get('type')}"


def test_switch_ids_exist_and_types():
    """Р’СЃРµ switches_ids РµСЃС‚СЊ РІ NODES Рё РёРјРµСЋС‚ type == 2."""
    sw_ids = cfg.GROUPS["switches_ids"]
    for sw_id in sw_ids:
        assert sw_id in cfg.NODES, f"switch_id {sw_id} РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ РІ NODES"
        node = cfg.NODES[sw_id]
        assert node.get("type") == 2, f"switch_id {sw_id} РЅРµ type=2, Р° {node.get('type')}"


def test_signal_ids_exist_and_types():
    """Р’СЃРµ СЃРёРіРЅР°Р»С‹ РёР· GROUPS РѕС‚РЅРѕСЃСЏС‚СЃСЏ Рє type 3 РёР»Рё 4 Рё РµСЃС‚СЊ РІ NODES."""
    for sig_id in cfg.GROUPS["shunt_signals_ids"]:
        assert sig_id in cfg.NODES, f"shunt signal {sig_id} РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ РІ NODES"
        node = cfg.NODES[sig_id]
        assert node.get("type") == 3, f"РјР°РЅРµРІСЂРѕРІС‹Р№ {sig_id} РЅРµ type=3, Р° {node.get('type')}"
    for sig_id in cfg.GROUPS["train_signals_ids"]:
        assert sig_id in cfg.NODES, f"train signal {sig_id} РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ РІ NODES"
        node = cfg.NODES[sig_id]
        assert node.get("type") == 4, f"РїРѕРµР·РґРЅРѕР№ {sig_id} РЅРµ type=4, Р° {node.get('type')}"


def test_switch_logic_sections_exist():
    """
    РљР°Р¶РґС‹Р№ РєР»СЋС‡ РІ SWITCH_LOGIC:
    - СЃСѓС‰РµСЃС‚РІСѓРµС‚ РєР°Рє Р Р¦ (name) РІ NODES;
    - РµРіРѕ PrevSec/NextSec (РµСЃР»Рё РЅРµ None) С‚РѕР¶Рµ СЃСѓС‰РµСЃС‚РІСѓСЋС‚ РІ SWITCH_LOGIC/NODES.
    """
    name_to_id = {n["name"]: nid for nid, n in cfg.NODES.items()}

    for sec_name, data in sw_logic_mod.SWITCH_LOGIC.items():
        # СЃР°РјР° СЃРµРєС†РёСЏ РґРѕР»Р¶РЅР° СЃСѓС‰РµСЃС‚РІРѕРІР°С‚СЊ РєР°Рє Р Р¦
        assert sec_name in name_to_id, f"СЃРµРєС†РёСЏ {sec_name} РЅРµ РЅР°Р№РґРµРЅР° РІ NODES"
        rc_id = name_to_id[sec_name]
        assert cfg.NODES[rc_id]["type"] == 1, f"{sec_name} РІ SWITCH_LOGIC РЅРµ СЏРІР»СЏРµС‚СЃСЏ type=1 (Р Р¦)"

        prev_sec = data.get("PrevSec")
        next_sec = data.get("NextSec")

        if prev_sec is not None:
            assert prev_sec in sw_logic_mod.SWITCH_LOGIC, f"PrevSec={prev_sec} РЅРµС‚ РІ SWITCH_LOGIC"
        if next_sec is not None:
            assert next_sec in sw_logic_mod.SWITCH_LOGIC, f"NextSec={next_sec} РЅРµС‚ РІ SWITCH_LOGIC"


def test_switch_logic_stem_switches_exist():
    """Р’СЃРµ СЃС‚СЂРµР»РєРё РІ stem/plus_rc/minus_rc РєРѕСЂСЂРµРєС‚РЅРѕ СЃСЃС‹Р»Р°СЋС‚СЃСЏ РЅР° СЃСѓС‰РµСЃС‚РІСѓСЋС‰РёРµ NODES."""
    name_to_id = {n["name"]: nid for nid, n in cfg.NODES.items()}

    for sec_name, data in sw_logic_mod.SWITCH_LOGIC.items():
        # stem: РёРјРµРЅР° СЃС‚СЂРµР»РѕРє
        for sw_name in data.get("stem", []):
            assert sw_name in name_to_id, f"СЃС‚СЂРµР»РєР° {sw_name} РёР· stem СЃРµРєС†РёРё {sec_name} РЅРµ РЅР°Р№РґРµРЅР° РІ NODES"
            sw_id = name_to_id[sw_name]
            assert cfg.NODES[sw_id]["type"] == 2, f"{sw_name} РІ stem РЅРµ type=2, Р° {cfg.NODES[sw_id]['type']}"

        # plus_rc / minus_rc: РёРјРµРЅР° Р Р¦
        for rc_name in data.get("plus_rc", []):
            assert rc_name in sw_logic_mod.SWITCH_LOGIC, f"plus_rc {rc_name} СЃРµРєС†РёРё {sec_name} РЅРµС‚ РІ SWITCH_LOGIC"
        for rc_name in data.get("minus_rc", []):
            assert rc_name in sw_logic_mod.SWITCH_LOGIC, f"minus_rc {rc_name} СЃРµРєС†РёРё {sec_name} РЅРµС‚ РІ SWITCH_LOGIC"


def test_signals_logic_refs_exist_and_types():
    """
    Р”Р»СЏ РєР°Р¶РґРѕРіРѕ СЃРёРіРЅР°Р»Р°:
    - node_id РµСЃС‚СЊ РІ NODES Рё РёРјРµРµС‚ РєРѕСЂСЂРµРєС‚РЅС‹Р№ type (3 РёР»Рё 4);
    - PrevSec/NextSec (РµСЃР»Рё РЅРµ None) СЃСѓС‰РµСЃС‚РІСѓСЋС‚ РєР°Рє СЃРµРєС†РёСЏ РІ SWITCH_LOGIC.
    """
    name_to_id = {n["name"]: nid for nid, n in cfg.NODES.items()}

    for sig_name, data in sig_logic_mod.SIGNALS_LOGIC.items():
        node_id = data["node_id"]
        assert node_id in cfg.NODES, f"signal {sig_name} СЃ node_id={node_id} РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ РІ NODES"
        node = cfg.NODES[node_id]

        if data["type"] == "SIG":
            assert node["type"] == 3, f"signal {sig_name} РѕР¶РёРґР°РµС‚СЃСЏ type=3, Р° {node['type']}"
        else:
            assert node["type"] == 4, f"signal {sig_name} РѕР¶РёРґР°РµС‚СЃСЏ type=4, Р° {node['type']}"

        prev_sec = data.get("PrevSec")
        next_sec = data.get("NextSec")

        if prev_sec is not None:
            assert (
                prev_sec in sw_logic_mod.SWITCH_LOGIC
            ), f"PrevSec={prev_sec} СЃРёРіРЅР°Р»Р° {sig_name} РЅРµ РЅР°Р№РґРµРЅР° РІ SWITCH_LOGIC"
        if next_sec is not None:
            assert (
                next_sec in sw_logic_mod.SWITCH_LOGIC
            ), f"NextSec={next_sec} СЃРёРіРЅР°Р»Р° {sig_name} РЅРµ РЅР°Р№РґРµРЅР° РІ SWITCH_LOGIC"


def test_rc_sections_vs_switch_logic():
    """
    RC_SECTIONS Рё SWITCH_LOGIC РґРѕР»Р¶РЅС‹ Р±С‹С‚СЊ СЃРѕРіР»Р°СЃРѕРІР°РЅС‹:
    - РѕРґРёРЅР°РєРѕРІС‹Р№ РЅР°Р±РѕСЂ СЃРµРєС†РёР№;
    - PrevSec/NextSec СЃРѕРІРїР°РґР°СЋС‚ РґР»СЏ РєР°Р¶РґРѕР№ СЃРµРєС†РёРё.
    """
    rc_sec = rc_sections_mod.RC_SECTIONS
    sw_sec = sw_logic_mod.SWITCH_LOGIC

    assert set(rc_sec.keys()) == set(
        sw_sec.keys()
    ), "РќР°Р±РѕСЂ СЃРµРєС†РёР№ РІ RC_SECTIONS Рё SWITCH_LOGIC РЅРµ СЃРѕРІРїР°РґР°РµС‚"

    for name in rc_sec.keys():
        assert (
            rc_sec[name]["PrevSec"] == sw_sec[name]["PrevSec"]
        ), f"PrevSec СЂР°Р·Р»РёС‡Р°РµС‚СЃСЏ РґР»СЏ СЃРµРєС†РёРё {name}"
        assert (
            rc_sec[name]["NextSec"] == sw_sec[name]["NextSec"]
        ), f"NextSec СЂР°Р·Р»РёС‡Р°РµС‚СЃСЏ РґР»СЏ СЃРµРєС†РёРё {name}"


def test_station_model_builds_without_errors():
    """
    Р‘Р°Р·РѕРІС‹Р№ smokeвЂ‘С‚РµСЃС‚: StationModel Рё UniversalTopologyManager РёРјРїРѕСЂС‚РёСЂСѓСЋС‚СЃСЏ,
    Р° РєР»Р°СЃСЃ StationModel РґРѕСЃС‚СѓРїРµРЅ СЃ РѕР¶РёРґР°РµРјРѕР№ СЃРёРіРЅР°С‚СѓСЂРѕР№.
    """
    # РїСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ Сѓ StationModel РµСЃС‚СЊ РЅСѓР¶РЅС‹Рµ Р°СЂРіСѓРјРµРЅС‚С‹
    from inspect import signature

    sig = signature(model_mod.StationModel)
    params = list(sig.parameters.keys())
    # РѕР¶РёРґР°РµРј С…РѕС‚СЏ Р±С‹ СЌС‚Рё С‚СЂРё Р°СЂРіСѓРјРµРЅС‚Р°
    for name in ("rc_nodes", "switches", "signals"):
        assert name in params, f"РЈ StationModel РЅРµС‚ Р°СЂРіСѓРјРµРЅС‚Р° {name}"

    # РїСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ UniversalTopologyManager РјРѕР¶РЅРѕ СЃРѕР·РґР°С‚СЊ СЃ С„РёРєС‚РёРІРЅРѕР№ РјРѕРґРµР»СЊСЋ
    class DummyModel:
        rc_nodes = {}
        switch_nodes = {}

    topo = UniversalTopologyManager(DummyModel())
    assert topo.T_PK > 0



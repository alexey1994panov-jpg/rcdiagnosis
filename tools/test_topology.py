# -*- coding: utf-8 -*-
"""
Набор smoke‑ и консистент‑тестов для топологии станции.

Проверяет:
- целостность NODES/GROUPS;
- корректность SWITCH_LOGIC относительно NODES/RC_SECTIONS;
- корректность SIGNALS_LOGIC относительно NODES/SWITCH_LOGIC;
- базовую согласованность с station_model/UniversalTopologyManager.
"""

import importlib

import station_config as cfg
import station_rc_sections as rc_sections_mod
import station_switch_logic as sw_logic_mod
import station_signals_logic as sig_logic_mod
import station_model as model_mod
from topology_manager import UniversalTopologyManager


def test_groups_rc_ids_exist():
    """Все rc_ids из GROUPS есть в NODES и имеют type == 1."""
    rc_ids = cfg.GROUPS["rc_ids"]
    for rc_id in rc_ids:
        assert rc_id in cfg.NODES, f"rc_id {rc_id} отсутствует в NODES"
        node = cfg.NODES[rc_id]
        assert node.get("type") == 1, f"rc_id {rc_id} не type=1 (РЦ), а {node.get('type')}"


def test_switch_ids_exist_and_types():
    """Все switches_ids есть в NODES и имеют type == 2."""
    sw_ids = cfg.GROUPS["switches_ids"]
    for sw_id in sw_ids:
        assert sw_id in cfg.NODES, f"switch_id {sw_id} отсутствует в NODES"
        node = cfg.NODES[sw_id]
        assert node.get("type") == 2, f"switch_id {sw_id} не type=2, а {node.get('type')}"


def test_signal_ids_exist_and_types():
    """Все сигналы из GROUPS относятся к type 3 или 4 и есть в NODES."""
    for sig_id in cfg.GROUPS["shunt_signals_ids"]:
        assert sig_id in cfg.NODES, f"shunt signal {sig_id} отсутствует в NODES"
        node = cfg.NODES[sig_id]
        assert node.get("type") == 3, f"маневровый {sig_id} не type=3, а {node.get('type')}"
    for sig_id in cfg.GROUPS["train_signals_ids"]:
        assert sig_id in cfg.NODES, f"train signal {sig_id} отсутствует в NODES"
        node = cfg.NODES[sig_id]
        assert node.get("type") == 4, f"поездной {sig_id} не type=4, а {node.get('type')}"


def test_switch_logic_sections_exist():
    """
    Каждый ключ в SWITCH_LOGIC:
    - существует как РЦ (name) в NODES;
    - его PrevSec/NextSec (если не None) тоже существуют в SWITCH_LOGIC/NODES.
    """
    name_to_id = {n["name"]: nid for nid, n in cfg.NODES.items()}

    for sec_name, data in sw_logic_mod.SWITCH_LOGIC.items():
        # сама секция должна существовать как РЦ
        assert sec_name in name_to_id, f"секция {sec_name} не найдена в NODES"
        rc_id = name_to_id[sec_name]
        assert cfg.NODES[rc_id]["type"] == 1, f"{sec_name} в SWITCH_LOGIC не является type=1 (РЦ)"

        prev_sec = data.get("PrevSec")
        next_sec = data.get("NextSec")

        if prev_sec is not None:
            assert prev_sec in sw_logic_mod.SWITCH_LOGIC, f"PrevSec={prev_sec} нет в SWITCH_LOGIC"
        if next_sec is not None:
            assert next_sec in sw_logic_mod.SWITCH_LOGIC, f"NextSec={next_sec} нет в SWITCH_LOGIC"


def test_switch_logic_stem_switches_exist():
    """Все стрелки в stem/plus_rc/minus_rc корректно ссылаются на существующие NODES."""
    name_to_id = {n["name"]: nid for nid, n in cfg.NODES.items()}

    for sec_name, data in sw_logic_mod.SWITCH_LOGIC.items():
        # stem: имена стрелок
        for sw_name in data.get("stem", []):
            assert sw_name in name_to_id, f"стрелка {sw_name} из stem секции {sec_name} не найдена в NODES"
            sw_id = name_to_id[sw_name]
            assert cfg.NODES[sw_id]["type"] == 2, f"{sw_name} в stem не type=2, а {cfg.NODES[sw_id]['type']}"

        # plus_rc / minus_rc: имена РЦ
        for rc_name in data.get("plus_rc", []):
            assert rc_name in sw_logic_mod.SWITCH_LOGIC, f"plus_rc {rc_name} секции {sec_name} нет в SWITCH_LOGIC"
        for rc_name in data.get("minus_rc", []):
            assert rc_name in sw_logic_mod.SWITCH_LOGIC, f"minus_rc {rc_name} секции {sec_name} нет в SWITCH_LOGIC"


def test_signals_logic_refs_exist_and_types():
    """
    Для каждого сигнала:
    - node_id есть в NODES и имеет корректный type (3 или 4);
    - PrevSec/NextSec (если не None) существуют как секция в SWITCH_LOGIC.
    """
    name_to_id = {n["name"]: nid for nid, n in cfg.NODES.items()}

    for sig_name, data in sig_logic_mod.SIGNALS_LOGIC.items():
        node_id = data["node_id"]
        assert node_id in cfg.NODES, f"signal {sig_name} с node_id={node_id} отсутствует в NODES"
        node = cfg.NODES[node_id]

        if data["type"] == "SIG":
            assert node["type"] == 3, f"signal {sig_name} ожидается type=3, а {node['type']}"
        else:
            assert node["type"] == 4, f"signal {sig_name} ожидается type=4, а {node['type']}"

        prev_sec = data.get("PrevSec")
        next_sec = data.get("NextSec")

        if prev_sec is not None:
            assert (
                prev_sec in sw_logic_mod.SWITCH_LOGIC
            ), f"PrevSec={prev_sec} сигнала {sig_name} не найдена в SWITCH_LOGIC"
        if next_sec is not None:
            assert (
                next_sec in sw_logic_mod.SWITCH_LOGIC
            ), f"NextSec={next_sec} сигнала {sig_name} не найдена в SWITCH_LOGIC"


def test_rc_sections_vs_switch_logic():
    """
    RC_SECTIONS и SWITCH_LOGIC должны быть согласованы:
    - одинаковый набор секций;
    - PrevSec/NextSec совпадают для каждой секции.
    """
    rc_sec = rc_sections_mod.RC_SECTIONS
    sw_sec = sw_logic_mod.SWITCH_LOGIC

    assert set(rc_sec.keys()) == set(
        sw_sec.keys()
    ), "Набор секций в RC_SECTIONS и SWITCH_LOGIC не совпадает"

    for name in rc_sec.keys():
        assert (
            rc_sec[name]["PrevSec"] == sw_sec[name]["PrevSec"]
        ), f"PrevSec различается для секции {name}"
        assert (
            rc_sec[name]["NextSec"] == sw_sec[name]["NextSec"]
        ), f"NextSec различается для секции {name}"


def test_station_model_builds_without_errors():
    """
    Базовый smoke‑тест: StationModel и UniversalTopologyManager импортируются,
    а класс StationModel доступен с ожидаемой сигнатурой.
    """
    # проверяем, что у StationModel есть нужные аргументы
    from inspect import signature

    sig = signature(model_mod.StationModel)
    params = list(sig.parameters.keys())
    # ожидаем хотя бы эти три аргумента
    for name in ("rc_nodes", "switches", "signals"):
        assert name in params, f"У StationModel нет аргумента {name}"

    # проверяем, что UniversalTopologyManager можно создать с фиктивной моделью
    class DummyModel:
        rc_nodes = {}
        switch_nodes = {}

    topo = UniversalTopologyManager(DummyModel())
    assert topo.T_PK > 0

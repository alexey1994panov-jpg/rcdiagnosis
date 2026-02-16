from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from tools.core.detectors_engine import DetectorsConfig
from tools.station.station_config import NODES


def _norm_name(value: str) -> str:
    s = (value or "").upper()
    s = s.replace("&SOL;", "/")
    s = s.replace("РЎРџ", "SP")
    s = s.replace("РђРџ", "AP")
    s = s.replace("РќРџ", "NP")
    s = s.replace("Р§Рџ", "CHP")
    s = s.replace("РќР”Рџ", "NDP")
    s = s.replace("Рџ", "P")
    s = s.replace("Р§", "CH")
    s = s.replace("Рќ", "N")
    return re.sub(r"[^A-Z0-9/_-]+", "", s)


def _fix_mojibake(value: str) -> str:
    """
    Recover cp1251->utf8 mojibake strings like 'Р РЋР Сџ' -> 'РЎРџ'.
    If conversion fails, return original value unchanged.
    """
    s = str(value or "")
    try:
        repaired = s.encode("cp1251").decode("utf-8")
        return repaired or s
    except Exception:
        return s


NAME_TO_ID: Dict[str, str] = {}
NORM_TO_ID: Dict[str, str] = {}
ID_TO_NAME: Dict[str, str] = {}
SW_NAME_TO_ID: Dict[str, str] = {}
SIG_NAME_TO_ID: Dict[str, str] = {}
for oid, data in NODES.items():
    name = str(data.get("name", ""))
    ntype = int(data.get("type", 0))
    ID_TO_NAME[oid] = name
    NAME_TO_ID[name] = oid
    NORM_TO_ID[_norm_name(name)] = oid
    NORM_TO_ID[_norm_name(oid)] = oid
    if ntype == 2:
        SW_NAME_TO_ID[name] = oid
        NORM_TO_ID[_norm_name(f"SW{name}")] = oid
    if ntype in (3, 4):
        SIG_NAME_TO_ID[name] = oid

RC_TARGET_ALIASES = {
    "1P": "108",
    "1-7SP": "83",
    "10-12SP": "59",
}

LEGACY_TO_CANONICAL_OPTION_KEYS: Dict[str, str] = {
    "t_s0101": "ts01_lz1",
    "t_lz01": "tlz_lz1",
    "t_kon_v1": "tkon_lz1",
    "enable_v1": "enable_lz1",
    "t_s0102": "ts01_lz2",
    "t_s0202": "ts02_lz2",
    "t_lz02": "tlz_lz2",
    "t_kon_v2": "tkon_lz2",
    "enable_v2": "enable_lz2",
    "t_s0103": "ts01_lz3",
    "t_s0203": "ts02_lz3",
    "t_lz03": "tlz_lz3",
    "t_kon_v3": "tkon_lz3",
    "enable_v3": "enable_lz3",
    "t_s0401": "ts01_lz4",
    "t_lz04": "tlz_lz4",
    "t_kon_v4": "tkon_lz4",
    "enable_v4": "enable_lz4",
    "t_s05": "ts01_lz5",
    "t_lz05": "tlz_lz5",
    "t_kon_v5": "tkon_lz5",
    "enable_v5": "enable_lz5",
    "t_s06": "ts01_lz6",
    "t_lz06": "tlz_lz6",
    "t_kon_v6": "tkon_lz6",
    "enable_v6": "enable_lz6",
    "t_s07": "ts01_lz7",
    "t_lz07": "tlz_lz7",
    "t_kon_v7": "tkon_lz7",
    "enable_v7": "enable_lz7",
    "t_s0108": "ts01_lz8",
    "t_s0208": "ts02_lz8",
    "t_lz08": "tlz_lz8",
    "t_kon_v8": "tkon_lz8",
    "enable_v8": "enable_lz8",
    "t_s0109": "ts01_lz9",
    "t_lz09": "tlz_lz9",
    "t_kon_v9": "tkon_lz9",
    "enable_v9": "enable_lz9",
    "t_s0110": "ts01_lz10",
    "t_s0210": "ts02_lz10",
    "t_s0310": "ts03_lz10",
    "t_lz10": "tlz_lz10",
    "t_kon_v10": "tkon_lz10",
    "enable_v10": "enable_lz10",
    "t_s11": "ts01_lz11",
    "t_lz11": "tlz_lz11",
    "t_kon_v11": "tkon_lz11",
    "enable_v11": "enable_lz11",
    "t_s0112": "ts01_lz12",
    "t_s0212": "ts02_lz12",
    "t_lz12": "tlz_lz12",
    "t_kon_v12": "tkon_lz12",
    "enable_v12": "enable_lz12",
    "t_s0113": "ts01_lz13",
    "t_s0213": "ts02_lz13",
    "t_lz13": "tlz_lz13",
    "t_kon_v13": "tkon_lz13",
    "enable_v13": "enable_lz13",
    "t_c0101_ls": "ts01_ls1",
    "t_ls01": "tlz_ls1",
    "t_kon_ls1": "tkon_ls1",
    "t_s0102_ls": "ts01_ls2",
    "t_s0202_ls": "ts02_ls2",
    "t_ls0102": "tlz_ls2",
    "t_kon_ls2": "tkon_ls2",
    "t_s0104_ls": "ts01_ls4",
    "t_s0204_ls": "ts02_ls4",
    "t_ls0104": "tlz01_ls4",
    "t_ls0204": "tlz02_ls4",
    "t_kon_ls4": "tkon_ls4",
    "t_s0105_ls": "ts01_ls5",
    "t_ls05": "tlz_ls5",
    "t_kon_ls5": "tkon_ls5",
    "t_s0106_ls": "ts01_ls6",
    "t_ls06": "tlz_ls6",
    "t_kon_ls6": "tkon_ls6",
    "t_s0109_ls": "ts01_ls9",
    "t_ls0109": "tlz_ls9",
    "t_kon_ls9": "tkon_ls9",
}


def _canonicalize_options(options: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(options or {})
    for legacy, canonical in LEGACY_TO_CANONICAL_OPTION_KEYS.items():
        # Canonical key has priority if both are present.
        if canonical in out:
            out[legacy] = out[canonical]
        elif legacy in out:
            out[canonical] = out[legacy]
    return out


def _resolve_rc_id(value: str) -> Optional[str]:
    if not value:
        return None
    if value in NODES and int(NODES[value].get("type", 0)) == 1:
        return value
    if value in NAME_TO_ID:
        oid = NAME_TO_ID[value]
        if int(NODES.get(oid, {}).get("type", 0)) == 1:
            return oid
    alias = RC_TARGET_ALIASES.get(value.upper())
    if alias:
        return alias
    oid = NORM_TO_ID.get(_norm_name(value))
    if oid and int(NODES.get(oid, {}).get("type", 0)) == 1:
        return oid
    return None


def _resolve_switch_id(value: str) -> Optional[str]:
    if not value:
        return None
    if value in NODES and int(NODES[value].get("type", 0)) == 2:
        return value
    raw = str(value)
    if raw.startswith(("Sw", "SW", "sw")):
        raw = raw[2:]
    if raw in SW_NAME_TO_ID:
        return SW_NAME_TO_ID[raw]
    oid = NORM_TO_ID.get(_norm_name(f"SW{raw}")) or NORM_TO_ID.get(_norm_name(raw))
    if oid and int(NODES.get(oid, {}).get("type", 0)) == 2:
        return oid
    return None


def _resolve_signal_id(value: str) -> Optional[str]:
    if not value:
        return None
    if value in NODES and int(NODES[value].get("type", 0)) in (3, 4):
        return value
    if value in SIG_NAME_TO_ID:
        return SIG_NAME_TO_ID[value]
    oid = NORM_TO_ID.get(_norm_name(value))
    if oid and int(NODES.get(oid, {}).get("type", 0)) in (3, 4):
        return oid
    return None


def _parse_flag(raw: str, ctrl_rc_id: Optional[str]) -> Dict[str, Any]:
    variant = ""
    ftype = ""
    phase: Optional[str] = None

    if raw.startswith("llz_v"):
        ftype = "LZ"
        body = raw[len("llz_"):]
        if body.endswith("_open"):
            phase = "opened"
            variant = body[: -len("_open")]
        elif body.endswith("_closed"):
            phase = "closed"
            variant = body[: -len("_closed")]
        else:
            variant = body
    elif raw.startswith("lls_"):
        ftype = "LS"
        body = raw[len("lls_"):]
        if body.endswith("_open"):
            phase = "opened"
            variant = body[: -len("_open")]
        elif body.endswith("_closed"):
            phase = "closed"
            variant = body[: -len("_closed")]
        else:
            variant = body

    return {
        "variant": variant,
        "type": ftype,
        "rc_id": ctrl_rc_id,
        "phase": phase,
        "raw": raw,
    }


def _to_float(options: Dict[str, Any], key: str, default: float) -> float:
    try:
        return float(options.get(key, default))
    except Exception:
        return default


def _to_bool(options: Dict[str, Any], key: str, default: bool) -> bool:
    value = options.get(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _to_int_list(options: Dict[str, Any], key: str) -> Optional[List[int]]:
    raw = options.get(key, None)
    if raw is None:
        return None
    if isinstance(raw, list):
        out: List[int] = []
        for item in raw:
            try:
                iv = int(item)
            except Exception:
                continue
            if iv not in out:
                out.append(iv)
        return out
    if isinstance(raw, str):
        txt = raw.strip()
        if not txt:
            return []
        out: List[int] = []
        for part in txt.replace(";", ",").split(","):
            p = part.strip()
            if not p:
                continue
            if p.isdigit():
                iv = int(p)
                if iv not in out:
                    out.append(iv)
        return out
    try:
        return [int(raw)]
    except Exception:
        return None


def _build_detectors_config(ctrl_rc_id: str, options: Dict[str, Any]) -> DetectorsConfig:
    from tools.station.station_model import load_station_from_config

    model = load_station_from_config()
    node = model.rc_nodes.get(ctrl_rc_id)
    if node is None:
        raise HTTPException(status_code=400, detail=f"Unknown target RC id: {ctrl_rc_id}")

    prev_rc_id = node.prev_links[0][0] if node.prev_links else ""
    next_rc_id = node.next_links[0][0] if node.next_links else ""

    def _pick_signal(prev_sec: Optional[str], next_sec: Optional[str]) -> Optional[str]:
        # Strict match only. Loose matching by only one side can produce
        # wrong static signal for dynamic topology RCs (e.g. 1-7РЎРџ/Р§1).
        if not prev_sec or not next_sec:
            return None
        for sig in model.signal_nodes.values():
            ps = sig.prev_sec
            ns = sig.next_sec
            if ps == prev_sec and ns == next_sec:
                return sig.signal_id
        return None

    sig10_next = _resolve_signal_id(str(options.get("sig_lz10_to_next", ""))) if options.get("sig_lz10_to_next") else None
    sig10_prev = _resolve_signal_id(str(options.get("sig_lz10_to_prev", ""))) if options.get("sig_lz10_to_prev") else None
    sig11a = _resolve_signal_id(str(options.get("sig_lz11_a", ""))) if options.get("sig_lz11_a") else None
    sig11b = _resolve_signal_id(str(options.get("sig_lz11_b", ""))) if options.get("sig_lz11_b") else None
    sig13_prev = _resolve_signal_id(str(options.get("sig_lz13_prev", ""))) if options.get("sig_lz13_prev") else None
    sig13_next = _resolve_signal_id(str(options.get("sig_lz13_next", ""))) if options.get("sig_lz13_next") else None
    sig6_prev = _resolve_signal_id(str(options.get("sig_ls6_prev", ""))) if options.get("sig_ls6_prev") else None
    sig4_prev = _resolve_signal_id(str(options.get("sig_lz4_prev_to_ctrl", ""))) if options.get("sig_lz4_prev_to_ctrl") else None
    sig4_next = _resolve_signal_id(str(options.get("sig_lz4_ctrl_to_next", ""))) if options.get("sig_lz4_ctrl_to_next") else None

    # Auto-fill topology-dependent signals when manual overrides are not provided.
    if sig4_prev is None:
        sig4_prev = _pick_signal(prev_rc_id or None, ctrl_rc_id)
    if sig4_next is None:
        sig4_next = _pick_signal(ctrl_rc_id, next_rc_id or None)
    if sig10_next is None:
        sig10_next = _pick_signal(ctrl_rc_id, next_rc_id or None) or _pick_signal(None, next_rc_id or None)
    if sig10_prev is None:
        sig10_prev = (
            _pick_signal(ctrl_rc_id, prev_rc_id or None)
            or _pick_signal(None, prev_rc_id or None)
            or _pick_signal(prev_rc_id or None, ctrl_rc_id)
        )
    # LZ11 requires two closed signals around ctrl RC:
    # one towards prev side and one towards next side.
    if sig11a is None:
        sig11a = _pick_signal(ctrl_rc_id, prev_rc_id or None)
    if sig11b is None:
        sig11b = _pick_signal(ctrl_rc_id, next_rc_id or None)
    if sig13_prev is None:
        sig13_prev = _pick_signal(prev_rc_id or None, ctrl_rc_id) or _pick_signal(None, prev_rc_id or None)
    if sig13_next is None:
        sig13_next = _pick_signal(ctrl_rc_id, next_rc_id or None) or _pick_signal(None, next_rc_id or None)

    return DetectorsConfig(
        ctrl_rc_id=ctrl_rc_id,
        prev_rc_name=prev_rc_id,
        ctrl_rc_name=ctrl_rc_id,
        next_rc_name=next_rc_id,
        ts01_lz1=_to_float(options, "ts01_lz1", 3.0),
        tlz_lz1=_to_float(options, "tlz_lz1", 3.0),
        tkon_lz1=_to_float(options, "tkon_lz1", 3.0),
        enable_lz1=_to_bool(options, "enable_lz1", True),
        ts01_lz2=_to_float(options, "ts01_lz2", 3.0),
        ts02_lz2=_to_float(options, "ts02_lz2", 3.0),
        tlz_lz2=_to_float(options, "tlz_lz2", 3.0),
        tkon_lz2=_to_float(options, "tkon_lz2", 3.0),
        enable_lz2=_to_bool(options, "enable_lz2", True),
        ts01_lz3=_to_float(options, "ts01_lz3", 3.0),
        ts02_lz3=_to_float(options, "ts02_lz3", 3.0),
        tlz_lz3=_to_float(options, "tlz_lz3", 3.0),
        tkon_lz3=_to_float(options, "tkon_lz3", 3.0),
        enable_lz3=_to_bool(options, "enable_lz3", True),
        ts01_lz4=_to_float(options, "ts01_lz4", 3.0),
        tlz_lz4=_to_float(options, "tlz_lz4", 3.0),
        tkon_lz4=_to_float(options, "tkon_lz4", 3.0),
        enable_lz4=_to_bool(options, "enable_lz4", False),
        sig_lz4_prev_to_ctrl=sig4_prev,
        sig_lz4_ctrl_to_next=sig4_next,
        ts01_lz5=_to_float(options, "ts01_lz5", 3.0),
        tlz_lz5=_to_float(options, "tlz_lz5", 3.0),
        tkon_lz5=_to_float(options, "tkon_lz5", 3.0),
        enable_lz5=_to_bool(options, "enable_lz5", False),
        ts01_lz6=_to_float(options, "ts01_lz6", 3.0),
        tlz_lz6=_to_float(options, "tlz_lz6", 3.0),
        tkon_lz6=_to_float(options, "tkon_lz6", 3.0),
        enable_lz6=_to_bool(options, "enable_lz6", False),
        ts01_lz7=_to_float(options, "ts01_lz7", 3.0),
        tlz_lz7=_to_float(options, "tlz_lz7", 3.0),
        tkon_lz7=_to_float(options, "tkon_lz7", 3.0),
        enable_lz7=_to_bool(options, "enable_lz7", False),
        ts01_lz8=_to_float(options, "ts01_lz8", 3.0),
        ts02_lz8=_to_float(options, "ts02_lz8", 3.0),
        tlz_lz8=_to_float(options, "tlz_lz8", 3.0),
        tkon_lz8=_to_float(options, "tkon_lz8", 3.0),
        enable_lz8=_to_bool(options, "enable_lz8", True),
        enable_lz9=_to_bool(options, "enable_lz9", True),
        ts01_lz9=_to_float(options, "ts01_lz9", 3.0),
        tlz_lz9=_to_float(options, "tlz_lz9", 3.0),
        tkon_lz9=_to_float(options, "tkon_lz9", 3.0),
        enable_lz10=_to_bool(options, "enable_lz10", True),
        ts01_lz10=_to_float(options, "ts01_lz10", 3.0),
        ts02_lz10=_to_float(options, "ts02_lz10", 3.0),
        ts03_lz10=_to_float(options, "ts03_lz10", 3.0),
        tlz_lz10=_to_float(options, "tlz_lz10", 3.0),
        tkon_lz10=_to_float(options, "tkon_lz10", 3.0),
        sig_lz10_to_next=sig10_next,
        sig_lz10_to_prev=sig10_prev,
        enable_lz11=_to_bool(options, "enable_lz11", True),
        ts01_lz11=_to_float(options, "ts01_lz11", 3.0),
        tlz_lz11=_to_float(options, "tlz_lz11", 3.0),
        tkon_lz11=_to_float(options, "tkon_lz11", 3.0),
        sig_lz11_a=sig11a,
        sig_lz11_b=sig11b,
        enable_lz12=_to_bool(options, "enable_lz12", True),
        ts01_lz12=_to_float(options, "ts01_lz12", 3.0),
        ts02_lz12=_to_float(options, "ts02_lz12", 3.0),
        tlz_lz12=_to_float(options, "tlz_lz12", 3.0),
        tkon_lz12=_to_float(options, "tkon_lz12", 3.0),
        enable_lz13=_to_bool(options, "enable_lz13", True),
        ts01_lz13=_to_float(options, "ts01_lz13", 3.0),
        ts02_lz13=_to_float(options, "ts02_lz13", 3.0),
        tlz_lz13=_to_float(options, "tlz_lz13", 3.0),
        tkon_lz13=_to_float(options, "tkon_lz13", 3.0),
        sig_lz13_prev=sig13_prev,
        sig_lz13_next=sig13_next,
        enable_ls1=_to_bool(options, "enable_ls1", True),
        ts01_ls1=_to_float(options, "ts01_ls1", 3.0),
        tlz_ls1=_to_float(options, "tlz_ls1", 3.0),
        tkon_ls1=_to_float(options, "tkon_ls1", 3.0),
        enable_ls2=_to_bool(options, "enable_ls2", True),
        ts01_ls2=_to_float(options, "ts01_ls2", 3.0),
        ts02_ls2=_to_float(options, "ts02_ls2", 3.0),
        tlz_ls2=_to_float(options, "tlz_ls2", 3.0),
        tkon_ls2=_to_float(options, "tkon_ls2", 3.0),
        enable_ls4=_to_bool(options, "enable_ls4", True),
        ts01_ls4=_to_float(options, "ts01_ls4", 3.0),
        ts02_ls4=_to_float(options, "ts02_ls4", _to_float(options, "tlz02_ls4", 3.0)),
        tlz01_ls4=_to_float(options, "tlz01_ls4", 3.0),
        tlz02_ls4=_to_float(options, "tlz02_ls4", 10.0),
        tkon_ls4=_to_float(options, "tkon_ls4", 3.0),
        enable_ls5=_to_bool(options, "enable_ls5", True),
        ts01_ls5=_to_float(options, "ts01_ls5", 3.0),
        tlz_ls5=_to_float(options, "tlz_ls5", 3.0),
        tkon_ls5=_to_float(options, "tkon_ls5", 3.0),
        enable_ls6=_to_bool(options, "enable_ls6", True),
        ts01_ls6=_to_float(options, "ts01_ls6", 3.0),
        tlz_ls6=_to_float(options, "tlz_ls6", 3.0),
        tkon_ls6=_to_float(options, "tkon_ls6", 3.0),
        sig_ls6_prev=sig6_prev,
        enable_ls9=_to_bool(options, "enable_ls9", True),
        ts01_ls9=_to_float(options, "ts01_ls9", 3.0),
        tlz_ls9=_to_float(options, "tlz_ls9", 3.0),
        tkon_ls9=_to_float(options, "tkon_ls9", 3.0),
        enable_lz_exc_mu=_to_bool(options, "enable_lz_exc_mu", True),
        enable_lz_exc_recent_ls=_to_bool(options, "enable_lz_exc_recent_ls", True),
        enable_lz_exc_dsp=_to_bool(options, "enable_lz_exc_dsp", True),
        lz_exc_dsp_variants=_to_int_list(options, "lz_exc_dsp_variants"),
        enable_ls_exc_mu=_to_bool(options, "enable_ls_exc_mu", True),
        enable_ls_exc_after_lz=_to_bool(options, "enable_ls_exc_after_lz", True),
        enable_ls_exc_dsp=_to_bool(options, "enable_ls_exc_dsp", True),
        t_mu=_to_float(options, "t_mu", 15.0),
        t_recent_ls=_to_float(options, "t_recent_ls", 30.0),
        t_min_maneuver_v8=_to_float(options, "t_min_maneuver_v8", 600.0),
        t_ls_mu=_to_float(options, "t_ls_mu", 15.0),
        t_ls_after_lz=_to_float(options, "t_ls_after_lz", 30.0),
        t_ls_dsp=_to_float(options, "t_ls_dsp", 600.0),
    )


def _convert_rc_states(payload: Dict[str, int]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for key, value in (payload or {}).items():
        rc_id = _resolve_rc_id(str(key))
        norm_key = rc_id or str(key)
        iv = int(value)
        if norm_key in out and out[norm_key] != iv:
            raise HTTPException(
                status_code=400,
                detail=f"Conflicting RC values for '{norm_key}' in one step ({out[norm_key]} vs {iv}). "
                f"Remove mixed aliases like '1Рџ'/'1P'.",
            )
        out[norm_key] = iv
    return out


def _convert_switch_states(payload: Dict[str, int]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for key, value in (payload or {}).items():
        sw_id = _resolve_switch_id(str(key))
        norm_key = sw_id or str(key)
        iv = int(value)
        if norm_key in out and out[norm_key] != iv:
            raise HTTPException(
                status_code=400,
                detail=f"Conflicting switch values for '{norm_key}' in one step ({out[norm_key]} vs {iv}).",
            )
        out[norm_key] = iv
    return out


def _convert_signal_states(payload: Dict[str, int]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for key, value in (payload or {}).items():
        sig_id = _resolve_signal_id(str(key))
        norm_key = sig_id or str(key)
        iv = int(value)
        if norm_key in out and out[norm_key] != iv:
            raise HTTPException(
                status_code=400,
                detail=f"Conflicting signal values for '{norm_key}' in one step ({out[norm_key]} vs {iv}).",
            )
        out[norm_key] = iv
    return out


def _states_ids_to_names(states: Dict[str, int], type_codes: set[int]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for key, value in (states or {}).items():
        name = str(key)
        node = NODES.get(str(key))
        if node and int(node.get("type", 0)) in type_codes:
            name = _fix_mojibake(str(node.get("name", key)))
        out[name] = int(value)
    return out

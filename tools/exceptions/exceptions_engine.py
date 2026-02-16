from __future__ import annotations

from dataclasses import dataclass
import re
from typing import List, Iterable, Set, TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from core.sim_core import ScenarioStep, TimelineStep


@dataclass
class ExceptionsConfig:
    enable_lz_exc_mu: bool = False
    enable_lz_exc_recent_ls: bool = False
    enable_lz_exc_dsp: bool = False
    enable_ls_exc_mu: bool = False
    enable_ls_exc_after_lz: bool = False
    enable_ls_exc_dsp: bool = False
    t_mu: float = 15.0
    t_recent_ls: float = 30.0
    t_min_maneuver_v8: float = 600.0
    t_ls_mu: float = 15.0
    t_ls_after_lz: float = 30.0
    t_ls_dsp: float = 600.0


def _sum_time(history: Iterable[ScenarioStep]) -> float:
    return sum(float(s.t) for s in history)


def _adjacent_ids(curr: TimelineStep, ctrl_rc_id: str) -> Set[str]:
    out = {ctrl_rc_id}
    if curr.effective_prev_rc:
        out.add(curr.effective_prev_rc)
    if curr.effective_next_rc:
        out.add(curr.effective_next_rc)
    return out


def _auto_action_off(step: ScenarioStep) -> bool:
    auto = getattr(step, "auto_actions", None) or {}
    # Support both generic NAS/CHAS and keyed map by rc if present.
    vals = list(auto.values()) if isinstance(auto, dict) else []
    return any(int(v) in (0, 3) for v in vals if isinstance(v, (int, float)))


def _is_dsp_mode(step: ScenarioStep) -> bool:
    d = getattr(step, "dispatcher_control_state", None)
    if d is None:
        d = (step.modes or {}).get("dispatcher_control_state", None)
    return int(d) == 4 if d is not None else False


def _mu_active_in_window(
    history: List[ScenarioStep],
    rc_ids: Set[str],
    t_now: float,
    t_window: float,
) -> bool:
    if not history or t_window <= 0.0:
        return False
    t_start = max(0.0, t_now - t_window)
    t_acc = 0.0
    for step in history:
        dt = float(step.t)
        t_next = t_acc + dt
        if t_next > t_start and t_acc <= t_now:
            mu = getattr(step, "mu", None) or {}
            for rc_id in rc_ids:
                val = int(mu.get(rc_id, 0))
                # Legacy used both 1 and 4 as MU-active depending on path.
                if val in (1, 4):
                    return True
        t_acc = t_next
        if t_acc >= t_now:
            break
    return False


def _occupied_continuously(
    history: List[ScenarioStep],
    rc_id: str,
    t_now: float,
    t_window: float,
) -> bool:
    if not history or t_window <= 0.0:
        return False
    t_start = max(0.0, t_now - t_window)
    t_acc = 0.0
    for step in history:
        dt = float(step.t)
        t_next = t_acc + dt
        if t_next > t_start and t_acc <= t_now:
            state = int(step.rc_states.get(rc_id, 0))
            if state not in (6, 7, 8):
                return False
        t_acc = t_next
        if t_acc >= t_now:
            break
    return (t_now - t_start) >= t_window


def _recent_flag(history: List[TimelineStep], prefix: str, t_window: float) -> bool:
    if not history or t_window <= 0.0:
        return False
    t_now = sum(float(x.step_duration) for x in history)
    t_start = max(0.0, t_now - t_window)
    t_acc = 0.0
    for step in history:
        dt = float(step.step_duration)
        t_next = t_acc + dt
        if t_next > t_start and any(f.startswith(prefix) for f in (step.flags or [])):
            return True
        t_acc = t_next
    return False


def _recompute_state(step: TimelineStep) -> None:
    flags = step.flags or []
    has_ls = any(f.startswith("lls_") for f in flags)
    has_lz = any(f.startswith("llz_v") for f in flags)
    step.lz_state = bool(has_ls or has_lz)
    if not step.lz_state:
        step.lz_variant = 0
        return
    # Prefer explicit variant parsed from detector flags.
    if has_lz:
        lz_variants = _extract_suppressed_variants(flags, "llz_v")
        if lz_variants:
            step.lz_variant = int(lz_variants[0])
        elif step.lz_variant >= 100:
            step.lz_variant = 0
        return
    if has_ls:
        ls_variants = _extract_suppressed_variants(flags, "lls_")
        if ls_variants:
            step.lz_variant = 100 + int(ls_variants[0])
        elif step.lz_variant < 100:
            step.lz_variant = 100


def _suppress_prefix(step: TimelineStep, prefix: str) -> None:
    step.flags = [f for f in (step.flags or []) if not f.startswith(prefix)]


def _extract_suppressed_variants(flags: List[str], prefix: str) -> List[int]:
    out: List[int] = []
    for f in flags or []:
        raw = str(f)
        if prefix == "llz_v":
            m = re.match(r"^llz_v(\d+)(?:_|$)", raw)
        else:
            m = re.match(r"^lls_(?:v)?(\d+)(?:_|$)", raw)
        if m:
            v = int(m.group(1))
            if v not in out:
                out.append(v)
    return out


def _has_open_flag(flags: List[str], prefix: str) -> bool:
    return any(str(f).startswith(prefix) and "_open" in str(f) for f in (flags or []))


def _opened_at_same_time(
    history: List[TimelineStep],
    prefix: str,
    t_current: float,
    eps: float = 1e-9,
) -> bool:
    for step in history or []:
        if abs(float(step.t) - float(t_current)) > eps:
            continue
        if _has_open_flag(step.flags or [], prefix):
            return True
    return False


def make_exceptions_config(det_cfg: Any) -> ExceptionsConfig:
    if det_cfg is None:
        return ExceptionsConfig()
    return ExceptionsConfig(
        enable_lz_exc_mu=bool(getattr(det_cfg, "enable_lz_exc_mu", False)),
        enable_lz_exc_recent_ls=bool(getattr(det_cfg, "enable_lz_exc_recent_ls", False)),
        enable_lz_exc_dsp=bool(getattr(det_cfg, "enable_lz_exc_dsp", False)),
        enable_ls_exc_mu=bool(getattr(det_cfg, "enable_ls_exc_mu", False)),
        enable_ls_exc_after_lz=bool(getattr(det_cfg, "enable_ls_exc_after_lz", False)),
        enable_ls_exc_dsp=bool(getattr(det_cfg, "enable_ls_exc_dsp", False)),
        t_mu=float(getattr(det_cfg, "t_mu", 15.0)),
        t_recent_ls=float(getattr(det_cfg, "t_recent_ls", 30.0)),
        t_min_maneuver_v8=float(getattr(det_cfg, "t_min_maneuver_v8", 600.0)),
        t_ls_mu=float(getattr(det_cfg, "t_ls_mu", 15.0)),
        t_ls_after_lz=float(getattr(det_cfg, "t_ls_after_lz", 30.0)),
        t_ls_dsp=float(getattr(det_cfg, "t_ls_dsp", 600.0)),
    )


def build_exception_context(
    ctrl_rc_id: str,
    current_step: ScenarioStep,
    scenario_history: List[ScenarioStep],
    timeline_history: List[TimelineStep],
    cfg: ExceptionsConfig,
) -> Dict[str, bool]:
    t_now = _sum_time(scenario_history)
    current = current_step
    # Build adjacent set from topology hints in timeline history if available.
    adj = {ctrl_rc_id}
    if timeline_history:
        last = timeline_history[-1]
        if last.effective_prev_rc:
            adj.add(last.effective_prev_rc)
        if last.effective_next_rc:
            adj.add(last.effective_next_rc)

    lz_mu = cfg.enable_lz_exc_mu and _mu_active_in_window(scenario_history, adj, t_now, cfg.t_mu)
    lz_recent_ls = cfg.enable_lz_exc_recent_ls and _recent_flag(timeline_history, "lls_", cfg.t_recent_ls)
    lz_dsp = (
        cfg.enable_lz_exc_dsp
        and _is_dsp_mode(current)
        and _auto_action_off(current)
        and _occupied_continuously(scenario_history, ctrl_rc_id, t_now, cfg.t_min_maneuver_v8)
    )

    ls_mu = cfg.enable_ls_exc_mu and _mu_active_in_window(scenario_history, adj, t_now, cfg.t_ls_mu)
    ls_after_lz = cfg.enable_ls_exc_after_lz and _recent_flag(timeline_history, "llz_v", cfg.t_ls_after_lz)
    ls_dsp = (
        cfg.enable_ls_exc_dsp
        and _is_dsp_mode(current)
        and _auto_action_off(current)
        and _occupied_continuously(scenario_history, ctrl_rc_id, t_now, cfg.t_ls_dsp)
    )

    return {
        "exc_lz_mu_active": bool(lz_mu),
        "exc_lz_recent_ls": bool(lz_recent_ls),
        "exc_lz_dsp_timeout": bool(lz_dsp),
        
        "exc_ls_mu_active": bool(ls_mu),
        "exc_ls_after_lz": bool(ls_after_lz),
        "exc_ls_dsp_timeout": bool(ls_dsp),
    }


def apply_exceptions(
    ctrl_rc_id: str,
    current: TimelineStep,
    scenario_history: List[ScenarioStep],
    timeline_history: List[TimelineStep],
    cfg: ExceptionsConfig,
) -> TimelineStep:
    out = current
    t_now = _sum_time(scenario_history)
    current_step = scenario_history[-1] if scenario_history else None
    adj = _adjacent_ids(out, ctrl_rc_id)

    # LZ suppressors.
    has_lz_now = any(f.startswith("llz_v") for f in (out.flags or []))
    has_lz8_now = any(f.startswith("llz_v8") for f in (out.flags or []))
    if has_lz_now and current_step is not None:
        if cfg.enable_lz_exc_mu and _mu_active_in_window(scenario_history, adj, t_now, cfg.t_mu):
            suppressed = _extract_suppressed_variants(out.flags or [], "llz_v")
            _suppress_prefix(out, "llz_v")
            out.flags.append("lz_suppressed:local_mu")
            for v in suppressed:
                out.flags.append(f"lz_suppressed:v{v}:local_mu")
        elif cfg.enable_lz_exc_recent_ls and _recent_flag(timeline_history, "lls_", cfg.t_recent_ls):
            suppressed = _extract_suppressed_variants(out.flags or [], "llz_v")
            _suppress_prefix(out, "llz_v")
            out.flags.append("lz_suppressed:recent_ls")
            for v in suppressed:
                out.flags.append(f"lz_suppressed:v{v}:recent_ls")
        elif has_lz8_now and cfg.enable_lz_exc_dsp and _is_dsp_mode(current_step) and _auto_action_off(current_step):
            if _occupied_continuously(scenario_history, ctrl_rc_id, t_now, cfg.t_min_maneuver_v8):
                suppressed = _extract_suppressed_variants(out.flags or [], "llz_v8")
                _suppress_prefix(out, "llz_v8")
                out.flags.append("lz_suppressed:dsp_autoaction_timeout")
                for v in suppressed:
                    out.flags.append(f"lz_suppressed:v{v}:dsp_autoaction_timeout")

    # LS suppressors.
    has_ls_now = any(f.startswith("lls_") for f in (out.flags or []))
    if has_ls_now and current_step is not None:
        if cfg.enable_ls_exc_mu and _mu_active_in_window(scenario_history, adj, t_now, cfg.t_ls_mu):
            suppressed = _extract_suppressed_variants(out.flags or [], "lls_")
            _suppress_prefix(out, "lls_")
            out.flags.append("ls_suppressed:local_mu")
            for v in suppressed:
                out.flags.append(f"ls_suppressed:v{v}:local_mu")
        elif cfg.enable_ls_exc_after_lz and _recent_flag(timeline_history, "llz_v", cfg.t_ls_after_lz):
            suppressed = _extract_suppressed_variants(out.flags or [], "lls_")
            _suppress_prefix(out, "lls_")
            out.flags.append("ls_suppressed:after_lz")
            for v in suppressed:
                out.flags.append(f"ls_suppressed:v{v}:after_lz")
        elif cfg.enable_ls_exc_dsp and _is_dsp_mode(current_step) and _auto_action_off(current_step):
            if _occupied_continuously(scenario_history, ctrl_rc_id, t_now, cfg.t_ls_dsp):
                suppressed = _extract_suppressed_variants(out.flags or [], "lls_")
                _suppress_prefix(out, "lls_")
                out.flags.append("ls_suppressed:dsp_autoaction")
                for v in suppressed:
                    out.flags.append(f"ls_suppressed:v{v}:dsp_autoaction")

    # Arbitration rule: if LZ and LS are detected simultaneously, keep LZ.
    has_lz_now = any(f.startswith("llz_v") for f in (out.flags or []))
    has_ls_now = any(f.startswith("lls_") for f in (out.flags or []))
    if has_lz_now and has_ls_now:
        suppressed = _extract_suppressed_variants(out.flags or [], "lls_")
        _suppress_prefix(out, "lls_")
        out.flags.append("ls_suppressed:priority_lz")
        for v in suppressed:
            out.flags.append(f"ls_suppressed:v{v}:priority_lz")
    else:
        # Time-based arbitration: same absolute open moment, even if recorded in different steps.
        has_ls_open_now = _has_open_flag(out.flags or [], "lls_")
        if has_ls_open_now and _opened_at_same_time(timeline_history, "llz_v", out.t):
            suppressed = _extract_suppressed_variants(out.flags or [], "lls_")
            _suppress_prefix(out, "lls_")
            out.flags.append("ls_suppressed:priority_lz_same_time")
            for v in suppressed:
                out.flags.append(f"ls_suppressed:v{v}:priority_lz_same_time")

    _recompute_state(out)
    return out



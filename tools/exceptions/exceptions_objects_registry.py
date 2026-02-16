from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from exceptions.indicator_states import INDICATOR_ON


VALID_KINDS = {"MU", "NAS", "CHAS", "DSP"}


@dataclass(frozen=True)
class ExceptionObject:
    obj_id: str
    kind: str
    target_rc_ids: Set[str]
    active_states: Set[int]
    name: str = ""
    description: str = ""

    def is_active(self, state: int) -> bool:
        return int(state) in self.active_states

    def applies_to_rc(self, rc_id: str) -> bool:
        # DSP is global by contract.
        if self.kind == "DSP":
            return True
        return rc_id in self.target_rc_ids


@dataclass
class ExceptionsObjectsRegistry:
    objects: List[ExceptionObject]
    by_id: Dict[str, ExceptionObject]
    dsp_policy_default: Dict[str, Any]
    dsp_policy_rc_overrides: Dict[str, Dict[str, Any]]

    @staticmethod
    def empty() -> "ExceptionsObjectsRegistry":
        return ExceptionsObjectsRegistry(
            objects=[],
            by_id={},
            dsp_policy_default={},
            dsp_policy_rc_overrides={},
        )

    @staticmethod
    def load(path: Optional[str]) -> "ExceptionsObjectsRegistry":
        if not path:
            return ExceptionsObjectsRegistry.empty()
        p = Path(path)
        if not p.exists():
            return ExceptionsObjectsRegistry.empty()
        data = json.loads(p.read_text(encoding="utf-8"))
        items = data.get("objects", [])
        dsp_policy = data.get("dsp_policy", {}) or {}
        dsp_default = dsp_policy.get("default", {}) or {}
        dsp_rc_overrides = dsp_policy.get("rc_overrides", {}) or {}

        out: List[ExceptionObject] = []
        by_id: Dict[str, ExceptionObject] = {}

        for raw in items:
            obj_id = str(raw.get("id", "")).strip()
            kind = str(raw.get("kind", "")).upper().strip()
            if not obj_id or kind not in VALID_KINDS:
                continue
            if obj_id in by_id:
                raise ValueError(f"Duplicate exception object id: {obj_id}")

            target_rc_ids = {str(x) for x in (raw.get("target_rc_ids") or []) if str(x)}
            raw_states = raw.get("active_states")
            if raw_states is None:
                # Canonical default: "on" indicator state.
                active_states = {INDICATOR_ON}
            else:
                active_states = {int(x) for x in raw_states}
            if not active_states:
                continue

            obj = ExceptionObject(
                obj_id=obj_id,
                kind=kind,
                target_rc_ids=target_rc_ids,
                active_states=active_states,
                name=str(raw.get("name", "")),
                description=str(raw.get("description", "")),
            )
            out.append(obj)
            by_id[obj_id] = obj

        return ExceptionsObjectsRegistry(
            objects=out,
            by_id=by_id,
            dsp_policy_default=dsp_default,
            dsp_policy_rc_overrides=dsp_rc_overrides,
        )

    def evaluate(self, indicator_states: Dict[str, int], rc_id: str) -> Dict[str, bool]:
        mu_active = False
        nas_active = False
        chas_active = False
        dsp_active = False

        for obj in self.objects:
            if not obj.applies_to_rc(rc_id):
                continue
            state = int(indicator_states.get(obj.obj_id, 0))
            if not obj.is_active(state):
                continue

            if obj.kind == "MU":
                mu_active = True
            elif obj.kind == "NAS":
                nas_active = True
            elif obj.kind == "CHAS":
                chas_active = True
            elif obj.kind == "DSP":
                dsp_active = True

        return {
            "mu_active": mu_active,
            "nas_active": nas_active,
            "chas_active": chas_active,
            "dsp_active": dsp_active,
        }

    def get_dsp_policy(self, rc_id: str, det_cfg: Any) -> Dict[str, Any]:
        policy = dict(self.dsp_policy_default or {})
        policy.update(dict(self.dsp_policy_rc_overrides.get(rc_id, {}) or {}))

        if "enabled" not in policy:
            policy["enabled"] = bool(getattr(det_cfg, "enable_lz_exc_dsp", False))
        if "mode" not in policy:
            policy["mode"] = "detector_global"
        if "count_scope" not in policy:
            policy["count_scope"] = "ctrl_occupied"
        if "variants" not in policy:
            policy["variants"] = [8]
        if "t_maneuver" not in policy:
            policy["t_maneuver"] = float(getattr(det_cfg, "t_min_maneuver_v8", 600.0))
        return policy


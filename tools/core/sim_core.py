"""
sim_core.py вЂ” РѕР±С‰РёР№ РєР°СЂРєР°СЃ СЃРёРјСѓР»СЏС†РёРё СЃ РїРѕРґРґРµСЂР¶РєРѕР№ РјРЅРѕР¶РµСЃС‚РІРµРЅРЅС‹С… РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹С… Р Р¦
Рё РґРёРЅР°РјРёС‡РµСЃРєРѕР№ С‚РѕРїРѕР»РѕРіРёРё.

Р’РµСЂСЃРёСЏ: 2.0 (СЃ РѕР±СЂР°С‚РЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚СЊСЋ РґР»СЏ СЃС‚Р°СЂС‹С… С‚РµСЃС‚РѕРІ)

Р”Р»СЏ C: СЃС‚СЂСѓРєС‚СѓСЂС‹ СЃ РїР»РѕСЃРєРёРјРё РїРѕР»СЏРјРё, СЏРІРЅРѕРµ СѓРїСЂР°РІР»РµРЅРёРµ РїР°РјСЏС‚СЊСЋ, Р±РµР· РІРёСЂС‚СѓР°Р»СЊРЅС‹С… РјРµС‚РѕРґРѕРІ.
"""

from typing import Dict, List, Any, Optional, Iterable, Tuple, Union

from station.station_model import load_station_from_config, StationModel
from core.topology_manager import UniversalTopologyManager

from core.detectors_engine import (
    DetectorsState,
    init_detectors_engine,
)
from core.sim_types import ScenarioStep, SimulationConfig, TimelineStep
from exceptions.exceptions_engine import (
    build_exception_context,
    make_exceptions_config,
)
from exceptions.exceptions_objects_registry import ExceptionsObjectsRegistry
from core.sim_result import SingleResultWrapper
from core.sim_runner import run_context
from core.sim_step_runner import step_single_rc




class SimulationContext:
    """
    РљРѕРЅС‚РµРєСЃС‚ СЃРёРјСѓР»СЏС†РёРё СЃ РїРѕРґРґРµСЂР¶РєРѕР№ РјРЅРѕР¶РµСЃС‚РІР° РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹С… Р Р¦.
    
    Р”Р»СЏ C: СЃС‚СЂСѓРєС‚СѓСЂР° SimulationContext СЃ РјР°СЃСЃРёРІРѕРј СЃРѕСЃС‚РѕСЏРЅРёР№ РґРµС‚РµРєС‚РѕСЂРѕРІ,
    РєР°Р¶РґС‹Р№ СЌР»РµРјРµРЅС‚ СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓРµС‚ РѕРґРЅРѕР№ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕР№ Р Р¦.
    """

    def __init__(
        self,
        config: SimulationConfig,
        scenario: Iterable[ScenarioStep],
        # NEW: РѕРїС†РёРѕРЅР°Р»СЊРЅРѕ вЂ” СЃРїРёСЃРѕРє РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹С… Р Р¦ (Р±РµСЂС‘С‚СЃСЏ РёР· config РµСЃР»Рё РЅРµ СѓРєР°Р·Р°РЅ)
        ctrl_rc_ids: Optional[List[str]] = None,
        # DEPRECATED: СЃС‚Р°СЂС‹Р№ РїР°СЂР°РјРµС‚СЂ РґР»СЏ РѕР±СЂР°С‚РЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё
        ctrl_rc_id: Optional[str] = None,
    ) -> None:
        self.config = config
        self.scenario_steps: List[ScenarioStep] = list(scenario)
        
        # РћРїСЂРµРґРµР»СЏРµРј СЃРїРёСЃРѕРє РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹С… Р Р¦
        if ctrl_rc_id is not None:
            # DEPRECATED: СЃС‚Р°СЂС‹Р№ API
            self.ctrl_rc_ids = [ctrl_rc_id]
            # РљРѕРЅРІРµСЂС‚РёСЂСѓРµРј РѕРґРёРЅРѕС‡РЅС‹Р№ РєРѕРЅС„РёРі РµСЃР»Рё РЅСѓР¶РЅРѕ
            if not config.detectors_configs and config.detectors_config:
                config.detectors_configs[ctrl_rc_id] = config.detectors_config
        elif ctrl_rc_ids is not None:
            # NEW: РЅРѕРІС‹Р№ API
            self.ctrl_rc_ids = ctrl_rc_ids
        else:
            # Р‘РµСЂС‘Рј РёР· РєРѕРЅС„РёРіРѕРІ РґРµС‚РµРєС‚РѕСЂРѕРІ
            self.ctrl_rc_ids = list(config.detectors_configs.keys())
        
        if not self.ctrl_rc_ids:
            raise ValueError("РќРµ СѓРєР°Р·Р°РЅС‹ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹Рµ Р Р¦ (ctrl_rc_ids РёР»Рё ctrl_rc_id)")
        
        # РњРѕРґРµР»СЊ СЃС‚Р°РЅС†РёРё + С‚РѕРїРѕР»РѕРіРёСЏ (РѕРґРЅР° РЅР° РІСЃРµ Р Р¦)
        self.model: StationModel = load_station_from_config()
        self.topology = UniversalTopologyManager(self.model, t_pk=config.t_pk)
        self.exceptions_registry = ExceptionsObjectsRegistry.load(config.exceptions_objects_path)

        # РўРµРєСѓС‰РµРµ РІСЂРµРјСЏ Рё СЃРѕСЃС‚РѕСЏРЅРёСЏ (РѕР±С‰РёРµ РґР»СЏ РІСЃРµС… Р Р¦)
        self.time: float = 0.0
        self.rc_states: Dict[str, int] = {}
        self.switch_states: Dict[str, int] = {}
        self.signal_states: Dict[str, int] = {}

        # NEW: СЃРѕСЃС‚РѕСЏРЅРёСЏ РґРµС‚РµРєС‚РѕСЂРѕРІ РґР»СЏ РєР°Р¶РґРѕР№ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕР№ Р Р¦
        # Р”Р»СЏ C: РјР°СЃСЃРёРІ СЃС‚СЂСѓРєС‚СѓСЂ DetectorsState, РёРЅРґРµРєСЃ = ctrl_rc_id
        self.detectors_states: Dict[str, DetectorsState] = {}
        for rc_id in self.ctrl_rc_ids:
            cfg = config.detectors_configs.get(rc_id)
            if cfg:
                self.detectors_states[rc_id] = init_detectors_engine(
                    cfg=cfg,
                    rc_ids=list(self.model.rc_nodes.keys()),
                )
            else:
                raise ValueError(f"РќРµС‚ РєРѕРЅС„РёРіСѓСЂР°С†РёРё РґР»СЏ Р Р¦ {rc_id}")

        # РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РЅР°С‡Р°Р»СЊРЅС‹РјРё РґР°РЅРЅС‹РјРё
        if self.scenario_steps:
            first = self.scenario_steps[0]
            self.rc_states = dict(first.rc_states)
            self.switch_states = dict(first.switch_states)
            self.signal_states = dict(first.signal_states)

        # Runtime histories for dynamic exception checks inside phase logic.
        self._scenario_history_runtime: List[ScenarioStep] = []
        self._timeline_history_runtime: Dict[str, List[TimelineStep]] = {rc_id: [] for rc_id in self.ctrl_rc_ids}
        self._scenario_history_by_rc: Dict[str, List[ScenarioStep]] = {rc_id: [] for rc_id in self.ctrl_rc_ids}
        self._dsp_maneuver_timer_by_rc: Dict[str, float] = {rc_id: 0.0 for rc_id in self.ctrl_rc_ids}

    def _compute_effective_neighbors_with_control(
        self,
        ctrl_rc_id: str,
        dt: float,
    ) -> Tuple[Optional[str], Optional[str], bool, bool, bool, bool]:
        """
        Р’С‹С‡РёСЃР»СЏРµС‚ СЃРѕСЃРµРґРµР№ Рё С„Р»Р°РіРё РєРѕРЅС‚СЂРѕР»СЏ/РєСЂР°Р№РЅРѕСЃС‚Рё (NC) РґР»СЏ РєРѕРЅРєСЂРµС‚РЅРѕР№ Р Р¦.
        """
        prev_rc, next_rc, prev_ok, next_ok, prev_nc, next_nc = self.topology.get_neighbors_with_control(
            ctrl_rc_id,
            switch_states=self.switch_states,
            dt=dt,
        )
        return prev_rc or None, next_rc or None, prev_ok, next_ok, prev_nc, next_nc

    def _pick_signal(
        self,
        prev_sec: Optional[str],
        next_sec: Optional[str],
    ) -> Optional[str]:
        exact: Optional[str] = None
        by_next: Optional[str] = None
        by_prev: Optional[str] = None
        for sig in self.model.signal_nodes.values():
            ps = sig.prev_sec
            ns = sig.next_sec
            if prev_sec and next_sec and ps == prev_sec and ns == next_sec:
                exact = sig.signal_id
                break
            if by_next is None and next_sec and ns == next_sec:
                by_next = sig.signal_id
            if by_prev is None and prev_sec and ps == prev_sec:
                by_prev = sig.signal_id
        return exact or by_next or by_prev

    def _compute_dynamic_signal_modes(
        self,
        ctrl_rc_id: str,
        effective_prev_rc: Optional[str],
        effective_next_rc: Optional[str],
    ) -> Dict[str, Optional[str]]:
        sig_prev_to_ctrl = self._pick_signal(effective_prev_rc, ctrl_rc_id) if effective_prev_rc else None
        sig_ctrl_to_prev = self._pick_signal(ctrl_rc_id, effective_prev_rc) if effective_prev_rc else None
        sig_ctrl_to_next = self._pick_signal(ctrl_rc_id, effective_next_rc) if effective_next_rc else None
        sig_next_to_ctrl = self._pick_signal(effective_next_rc, ctrl_rc_id) if effective_next_rc else None
        return {
            "sig_prev_to_ctrl": sig_prev_to_ctrl,
            "sig_ctrl_to_prev": sig_ctrl_to_prev,
            "sig_ctrl_to_next": sig_ctrl_to_next,
            "sig_next_to_ctrl": sig_next_to_ctrl,
        }

    def _step_single_rc(
        self,
        ctrl_rc_id: str,
        step: ScenarioStep,
        dt: float,
        exception_context: Optional[Dict[str, bool]] = None,
        step_override: Optional[ScenarioStep] = None,
    ) -> TimelineStep:
        return step_single_rc(
            self,
            ctrl_rc_id,
            step,
            dt,
            exception_context=exception_context,
            step_override=step_override,
        )

    def _rc_is_occupied(self, rc_id: str, step: ScenarioStep) -> bool:
        st = int(step.rc_states.get(rc_id, 0))
        return st in (6, 7, 8)

    def _reset_variant_detector(self, det_state: DetectorsState, variant: int) -> None:
        mapping = {
            1: "v1",
            2: "v2",
            3: "v3",
            4: "v4",
            5: "v5",
            6: "v6",
            7: "v7",
            8: "v8",
            9: "lz9",
            10: "lz10",
            11: "lz11",
            12: "lz12",
            13: "lz13",
        }
        attr = mapping.get(int(variant))
        if not attr:
            return
        det = getattr(det_state, attr, None)
        if det is not None and hasattr(det, "reset"):
            det.reset()

    def _apply_dsp_detector_gate(
        self,
        rc_id: str,
        step_for_exc: ScenarioStep,
        det_cfg: Optional[DetectorsConfig],
        dt: float,
    ) -> Dict[str, object]:
        policy = self.exceptions_registry.get_dsp_policy(rc_id, det_cfg)
        if not bool(policy.get("enabled", False)):
            self._dsp_maneuver_timer_by_rc[rc_id] = 0.0
            return {"triggered": False, "variants": [], "policy": policy}

        dsp_state = (
            int(step_for_exc.dispatcher_control_state)
            if step_for_exc.dispatcher_control_state is not None
            else int(step_for_exc.modes.get("dispatcher_control_state"))
            if "dispatcher_control_state" in step_for_exc.modes
            else 0
        )
        dsp_active = dsp_state == 4
        auto_vals = list((step_for_exc.auto_actions or {}).values())
        auto_off = any(int(v) in (0, 3) for v in auto_vals if isinstance(v, (int, float)))
        count_scope = str(policy.get("count_scope", "ctrl_occupied"))
        if count_scope == "always":
            scope_ok = True
        else:
            scope_ok = self._rc_is_occupied(rc_id, step_for_exc)

        if dsp_active and auto_off and scope_ok:
            self._dsp_maneuver_timer_by_rc[rc_id] = self._dsp_maneuver_timer_by_rc.get(rc_id, 0.0) + dt
        else:
            self._dsp_maneuver_timer_by_rc[rc_id] = 0.0

        t_maneuver = float(policy.get("t_maneuver", 600.0))
        triggered = self._dsp_maneuver_timer_by_rc[rc_id] >= t_maneuver > 0.0
        variants = [int(v) for v in (policy.get("variants") or [])]
        if triggered:
            det_state = self.detectors_states.get(rc_id)
            if det_state is not None:
                for v in variants:
                    self._reset_variant_detector(det_state, v)
        return {"triggered": triggered, "variants": variants, "policy": policy}

    def _build_overlay_step_for_rc(self, step: ScenarioStep, rc_id: str) -> ScenarioStep:
        obj_eval = self.exceptions_registry.evaluate(step.indicator_states or {}, rc_id)
        merged_mu = dict(step.mu)
        if obj_eval["mu_active"]:
            merged_mu[rc_id] = 1
        merged_auto = dict(step.auto_actions)
        if obj_eval["nas_active"] and "nas" not in merged_auto:
            merged_auto["nas"] = 0
        if obj_eval["chas_active"] and "chas" not in merged_auto:
            merged_auto["chas"] = 0
        merged_dsp = step.dispatcher_control_state
        if merged_dsp is None and obj_eval["dsp_active"]:
            merged_dsp = 4
        return ScenarioStep(
            t=step.t,
            rc_states=dict(step.rc_states),
            switch_states=dict(step.switch_states),
            signal_states=dict(step.signal_states),
            modes=dict(step.modes),
            mu=merged_mu,
            dispatcher_control_state=merged_dsp,
            auto_actions=merged_auto,
            indicator_states=dict(step.indicator_states),
        )

    def step(self, step: ScenarioStep) -> Union[TimelineStep, Dict[str, TimelineStep]]:
        """
        РћРґРёРЅ С€Р°Рі СЃРёРјСѓР»СЏС†РёРё РґР»СЏ РІСЃРµС… РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹С… Р Р¦.
        
        NEW: РІРѕР·РІСЂР°С‰Р°РµС‚ Dict[str, TimelineStep] РІРјРµСЃС‚Рѕ РѕРґРЅРѕРіРѕ С€Р°РіР°.
        Р”Р»СЏ РѕР±СЂР°С‚РЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё: РµСЃР»Рё РѕРґРЅР° Р Р¦ вЂ” РјРѕР¶РЅРѕ РїРѕР»СѓС‡РёС‚СЊ РїРѕ [0] РёР»Рё .get()
        
        Р”Р»СЏ C: С†РёРєР» РїРѕ РјР°СЃСЃРёРІСѓ ctrl_rc_ids, Р·Р°РїРѕР»РЅРµРЅРёРµ РјР°СЃСЃРёРІР° СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ.
        """
        dt = max(0.0, float(step.t))

        # РћР±РЅРѕРІР»СЏРµРј СЃРѕСЃС‚РѕСЏРЅРёСЏ (РѕР±С‰РёРµ РґР»СЏ РІСЃРµС… Р Р¦)
        self.rc_states = dict(step.rc_states)
        self.switch_states = dict(step.switch_states)
        self.signal_states = dict(step.signal_states)

        # NEW: РІС‹С‡РёСЃР»СЏРµРј С€Р°Рі РґР»СЏ РєР°Р¶РґРѕР№ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕР№ Р Р¦
        results: Dict[str, TimelineStep] = {}
        for rc_id in self.ctrl_rc_ids:
            det_cfg = self.config.detectors_configs.get(rc_id)
            exc_cfg = make_exceptions_config(det_cfg)
            step_for_exc = self._build_overlay_step_for_rc(step, rc_id)
            dsp_gate = self._apply_dsp_detector_gate(rc_id, step_for_exc, det_cfg, dt)
            scenario_hist_current = self._scenario_history_by_rc.get(rc_id, []) + [step_for_exc]
            exc_ctx = build_exception_context(
                ctrl_rc_id=rc_id,
                current_step=step_for_exc,
                scenario_history=scenario_hist_current,
                timeline_history=self._timeline_history_runtime.get(rc_id, []),
                cfg=exc_cfg,
            )
            if bool(dsp_gate.get("triggered", False)):
                exc_ctx["exc_dsp_detector_gate"] = True
            results[rc_id] = self._step_single_rc(
                rc_id,
                step,
                dt,
                exception_context=exc_ctx,
                step_override=step_for_exc,
            )
            if bool(dsp_gate.get("triggered", False)):
                vset = set(int(x) for x in (dsp_gate.get("variants") or []))
                if vset:
                    results[rc_id].flags = [
                        f for f in results[rc_id].flags
                        if not any(f.startswith(f"llz_v{v}") for v in vset)
                    ]
                    results[rc_id].flags.append("lz_suppressed:dsp_detector_gate")
                    has_lz = any(fl.startswith("llz_v") for fl in results[rc_id].flags)
                    has_ls = any(fl.startswith("lls_") for fl in results[rc_id].flags)
                    results[rc_id].lz_state = bool(has_lz or has_ls)
                    if not results[rc_id].lz_state:
                        results[rc_id].lz_variant = 0

        # РЎРґРІРёРіР°РµРј РІСЂРµРјСЏ (РѕРґРЅРѕ РЅР° РІСЃРµ Р Р¦)
        self.time += dt
        self._scenario_history_runtime.append(step)
        for rc_id, tl in results.items():
            self._timeline_history_runtime.setdefault(rc_id, []).append(tl)
        for rc_id in self.ctrl_rc_ids:
            self._scenario_history_by_rc.setdefault(rc_id, []).append(
                self._build_overlay_step_for_rc(step, rc_id)
            )

        # Р”Р»СЏ РѕР±СЂР°С‚РЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё: РµСЃР»Рё РѕРґРЅР° Р Р¦ вЂ” РІРѕР·РІСЂР°С‰Р°РµРј РµС‘ РЅР°РїСЂСЏРјСѓСЋ
        # РќРѕ СЃРѕС…СЂР°РЅСЏРµРј РІРѕР·РјРѕР¶РЅРѕСЃС‚СЊ РїРѕР»СѓС‡РёС‚СЊ РєР°Рє СЃР»РѕРІР°СЂСЊ
        if len(self.ctrl_rc_ids) == 1:
            # Р’РѕР·РІСЂР°С‰Р°РµРј РѕР±СЉРµРєС‚ СЃ РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅС‹Рј РјРµС‚РѕРґРѕРј/Р°С‚СЂРёР±СѓС‚РѕРј РґР»СЏ РґРѕСЃС‚СѓРїР° РєР°Рє Рє dict
            single_result = results[self.ctrl_rc_ids[0]]
            # РЎРѕР·РґР°С‘Рј РѕР±С‘СЂС‚РєСѓ РґР»СЏ РґРѕСЃС‚СѓРїР° РїРѕ РёРЅРґРµРєСЃСѓ
            return SingleResultWrapper(single_result, results)
        
        return results

    def run(self) -> Union[List[TimelineStep], List[Dict[str, TimelineStep]]]:
        """
        РџСЂРѕРіРѕРЅСЏРµС‚ РІРµСЃСЊ СЃС†РµРЅР°СЂРёР№.
        
        NEW: РІРѕР·РІСЂР°С‰Р°РµС‚ List[Dict[str, TimelineStep]] вЂ” 
        РєР°Р¶РґС‹Р№ СЌР»РµРјРµРЅС‚ СЃРїРёСЃРєР° = РѕРґРёРЅ РІСЂРµРјРµРЅРЅРѕР№ С€Р°Рі, 
        РІРЅСѓС‚СЂРё СЃР»РѕРІР°СЂСЊ РїРѕ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹Рј Р Р¦.
        
        Р”Р»СЏ РѕР±СЂР°С‚РЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё: РµСЃР»Рё РѕРґРЅР° Р Р¦ вЂ” List[TimelineStep]
        
        Р”Р»СЏ C: РґРІСѓРјРµСЂРЅС‹Р№ РјР°СЃСЃРёРІ РёР»Рё РјР°СЃСЃРёРІ СЃС‚СЂСѓРєС‚СѓСЂ СЃ РїРѕР»РµРј rc_id.
        """
        return run_context(self)



# РћР±РЅРѕРІР»С‘РЅРЅС‹Р№ sim_core.py СЃ РѕР±СЂР°С‚РЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚СЊСЋ


"""
sim_core.py вЂ” РѕР±С‰РёР№ РєР°СЂРєР°СЃ СЃРёРјСѓР»СЏС†РёРё СЃ РїРѕРґРґРµСЂР¶РєРѕР№ РјРЅРѕР¶РµСЃС‚РІРµРЅРЅС‹С… РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹С… Р Р¦
Рё РґРёРЅР°РјРёС‡РµСЃРєРѕР№ С‚РѕРїРѕР»РѕРіРёРё.

Р’РµСЂСЃРёСЏ: 2.0 (СЃ РѕР±СЂР°С‚РЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚СЊСЋ РґР»СЏ СЃС‚Р°СЂС‹С… С‚РµСЃС‚РѕРІ)

Р”Р»СЏ C: СЃС‚СЂСѓРєС‚СѓСЂС‹ СЃ РїР»РѕСЃРєРёРјРё РїРѕР»СЏРјРё, СЏРІРЅРѕРµ СѓРїСЂР°РІР»РµРЅРёРµ РїР°РјСЏС‚СЊСЋ, Р±РµР· РІРёСЂС‚СѓР°Р»СЊРЅС‹С… РјРµС‚РѕРґРѕРІ.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Iterable, Tuple, Union

from station.station_model import load_station_from_config, StationModel
from core.topology_manager import UniversalTopologyManager

from core.detectors_engine import (
    DetectorsConfig,
    DetectorsState,
    init_detectors_engine,
    update_detectors,
)
from core.flags_engine import build_flags_simple


@dataclass
class ScenarioStep:
    """
    РћРїРёСЃР°РЅРёРµ РІС…РѕРґРЅС‹С… РґР°РЅРЅС‹С… РЅР° РёРЅС‚РµСЂРІР°Р»Рµ [t, t_next).
    
    Р”Р»СЏ C: СЃС‚СЂСѓРєС‚СѓСЂР° ScenarioStep СЃ РїРѕР»СЏРјРё t, rc_states[], switch_states[] Рё С‚.Рґ.
    """
    t: float                          # Р”Р›РРўР•Р›Р¬РќРћРЎРўР¬ РёРЅС‚РµСЂРІР°Р»Р° (СЃРµРє)
    rc_states: Dict[str, int]         # Uni_State_ID РїРѕ ID Р Р¦
    switch_states: Dict[str, int]     # Uni_State_ID РїРѕ ID СЃС‚СЂРµР»РѕРє
    signal_states: Dict[str, int]     # Uni_State_ID РїРѕ ID СЃРІРµС‚РѕС„РѕСЂРѕРІ
    modes: Dict[str, Any]             # Р РµР¶РёРјС‹/РїР°СЂР°РјРµС‚СЂС‹


@dataclass
class TimelineStep:
    """
    Р РµР·СѓР»СЊС‚Р°С‚ СЃРёРјСѓР»СЏС†РёРё РґР»СЏ РѕРґРЅРѕР№ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕР№ Р Р¦ РЅР° РѕРґРЅРѕРј С€Р°РіРµ.
    
    Р”Р»СЏ C: СЃС‚СЂСѓРєС‚СѓСЂР° TimelineStep, РјР°СЃСЃРёРІ С‚Р°РєРёС… СЃС‚СЂСѓРєС‚СѓСЂ вЂ” РІСЂРµРјРµРЅРЅР°СЏ Р»РёРЅРёСЏ.
    """
    t: float
    step_duration: float
    ctrl_rc_id: str                   # NEW: РєР°РєР°СЏ Р Р¦ РєРѕРЅС‚СЂРѕР»РёСЂРѕРІР°Р»Р°СЃСЊ
    
    # РўРѕРїРѕР»РѕРіРёС‡РµСЃРєРёРµ СЃРѕСЃРµРґРё (РёР· topology_manager)
    effective_prev_rc: Optional[str]
    effective_next_rc: Optional[str]
    
    # РЎС‹СЂС‹Рµ СЃРѕСЃС‚РѕСЏРЅРёСЏ
    rc_states: Dict[str, int]
    switch_states: Dict[str, int]
    signal_states: Dict[str, int]
    modes: Dict[str, Any]
    
    # Р РµР·СѓР»СЊС‚Р°С‚С‹ РґРµС‚РµРєС‚РѕСЂРѕРІ/С„Р»Р°РіРѕРІ
    lz_state: bool
    lz_variant: int
    flags: List[str]


@dataclass
class SimulationConfig:
    """
    РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ СЃРёРјСѓР»СЏС†РёРё РґР»СЏ РјРЅРѕР¶РµСЃС‚РІР° РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹С… Р Р¦.
    
    Р”Р»СЏ C: РјР°СЃСЃРёРІ РєРѕРЅС„РёРіСѓСЂР°С†РёР№, РєР°Р¶РґР°СЏ СЃРѕ СЃРІРѕРёРј ctrl_rc_id.
    """
    t_pk: float
    # NEW: СЃР»РѕРІР°СЂСЊ {rc_id: DetectorsConfig} РґР»СЏ РјРЅРѕР¶РµСЃС‚РІР° РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјС‹С…
    detectors_configs: Dict[str, DetectorsConfig] = field(default_factory=dict)
    
    # DEPRECATED: РѕРґРёРЅРѕС‡РЅР°СЏ РєРѕРЅС„РёРіСѓСЂР°С†РёСЏ (РґР»СЏ РѕР±СЂР°С‚РЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё)
    detectors_config: Optional[DetectorsConfig] = None
    
    def __post_init__(self):
        # NEW: Р°РІС‚РѕРєРѕРЅРІРµСЂС‚Р°С†РёСЏ РѕРґРёРЅРѕС‡РЅРѕР№ РєРѕРЅС„РёРіСѓСЂР°С†РёРё РІ СЃР»РѕРІР°СЂСЊ
        if self.detectors_config is not None and not self.detectors_configs:
            self.detectors_configs[self.detectors_config.ctrl_rc_id] = self.detectors_config


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

    def _compute_effective_neighbors_with_control(
        self,
        ctrl_rc_id: str,  # NEW: РїР°СЂР°РјРµС‚СЂ вЂ” РґР»СЏ РєР°РєРѕР№ Р Р¦ РІС‹С‡РёСЃР»СЏРµРј
        dt: float,
    ) -> Tuple[Optional[str], Optional[str], bool, bool]:
        """
        Р’С‹С‡РёСЃР»СЏРµС‚ СЃРѕСЃРµРґРµР№ РґР»СЏ РєРѕРЅРєСЂРµС‚РЅРѕР№ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕР№ Р Р¦.
        
        Р”Р»СЏ C: С„СѓРЅРєС†РёСЏ РїСЂРёРЅРёРјР°РµС‚ rc_id, РІРѕР·РІСЂР°С‰Р°РµС‚ СЃС‚СЂСѓРєС‚СѓСЂСѓ СЃ СЃРѕСЃРµРґСЏРјРё.
        """
        prev_rc, next_rc, prev_ok, next_ok = self.topology.get_neighbors_with_control(
            ctrl_rc_id,
            switch_states=self.switch_states,
            dt=dt,
        )
        return prev_rc or None, next_rc or None, prev_ok, next_ok

    def _step_single_rc(
        self,
        ctrl_rc_id: str,
        step: ScenarioStep,
        dt: float,
    ) -> TimelineStep:
        """
        РћРґРёРЅ С€Р°Рі СЃРёРјСѓР»СЏС†РёРё РґР»СЏ РѕРґРЅРѕР№ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕР№ Р Р¦.
        
        Р”Р»СЏ C: РѕС‚РґРµР»СЊРЅР°СЏ С„СѓРЅРєС†РёСЏ РёР»Рё inline РІ РѕСЃРЅРѕРІРЅРѕРј С†РёРєР»Рµ.
        """
        # 1. Р’С‹С‡РёСЃР»СЏРµРј С‚РѕРїРѕР»РѕРіРёСЋ РґР»СЏ СЌС‚РѕР№ РєРѕРЅРєСЂРµС‚РЅРѕР№ Р Р¦
        effective_prev_rc, effective_next_rc, prev_ok, next_ok = \
            self._compute_effective_neighbors_with_control(ctrl_rc_id, dt)

        # 2. Р¤РѕСЂРјРёСЂСѓРµРј topology_info РґР»СЏ РґРµС‚РµРєС‚РѕСЂРѕРІ
        topology_info = {
            "ctrl_rc_id": ctrl_rc_id,
            "effective_prev_rc": effective_prev_rc,
            "effective_next_rc": effective_next_rc,
        }

        # 3. Р“РѕС‚РѕРІРёРј modes
        modes_for_detectors = dict(step.modes)
        modes_for_detectors.setdefault("prev_control_ok", prev_ok)
        modes_for_detectors.setdefault("next_control_ok", next_ok)

        # 4. РџРѕР»СѓС‡Р°РµРј СЃРѕСЃС‚РѕСЏРЅРёРµ РґРµС‚РµРєС‚РѕСЂРѕРІ РґР»СЏ СЌС‚РѕР№ Р Р¦
        det_state = self.detectors_states.get(ctrl_rc_id)
        
        # 5. РћР±РЅРѕРІР»СЏРµРј РґРµС‚РµРєС‚РѕСЂС‹
        if det_state:
            new_det_state, det_result = update_detectors(
                det_state=det_state,
                t=self.time,
                dt=dt,
                rc_states=self.rc_states,
                switch_states=self.switch_states,
                signal_states=self.signal_states,
                topology_info=topology_info,
                cfg=self.config.detectors_configs[ctrl_rc_id],
                modes=modes_for_detectors,
            )
            self.detectors_states[ctrl_rc_id] = new_det_state
        else:
            # РќРµС‚ РґРµС‚РµРєС‚РѕСЂРѕРІ вЂ” СЃРѕР·РґР°С‘Рј РїСѓСЃС‚РѕР№ СЂРµР·СѓР»СЊС‚Р°С‚
            from core.detectors_engine import DetectorsResult
            det_result = DetectorsResult()

        # 6. РЎС‚СЂРѕРёРј С„Р»Р°РіРё
        flags_res = build_flags_simple(
            ctrl_rc_id=ctrl_rc_id,
            det_state=det_state or DetectorsState(),
            det_result=det_result,
            rc_states=self.rc_states,
            switch_states=self.switch_states,
        )

        # 7. РЎРѕР±РёСЂР°РµРј СЂРµР·СѓР»СЊС‚Р°С‚
        return TimelineStep(
            t=self.time,
            step_duration=dt,
            ctrl_rc_id=ctrl_rc_id,  # NEW
            effective_prev_rc=effective_prev_rc,
            effective_next_rc=effective_next_rc,
            rc_states=dict(self.rc_states),
            switch_states=dict(self.switch_states),
            signal_states=dict(self.signal_states),
            modes=dict(step.modes),
            lz_state=flags_res.lz,
            lz_variant=flags_res.variant,
            flags=list(flags_res.flags),
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
            results[rc_id] = self._step_single_rc(rc_id, step, dt)

        # РЎРґРІРёРіР°РµРј РІСЂРµРјСЏ (РѕРґРЅРѕ РЅР° РІСЃРµ Р Р¦)
        self.time += dt

        # Р”Р»СЏ РѕР±СЂР°С‚РЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё: РµСЃР»Рё РѕРґРЅР° Р Р¦ вЂ” РІРѕР·РІСЂР°С‰Р°РµРј РµС‘ РЅР°РїСЂСЏРјСѓСЋ
        # РќРѕ СЃРѕС…СЂР°РЅСЏРµРј РІРѕР·РјРѕР¶РЅРѕСЃС‚СЊ РїРѕР»СѓС‡РёС‚СЊ РєР°Рє СЃР»РѕРІР°СЂСЊ
        if len(self.ctrl_rc_ids) == 1:
            # Р’РѕР·РІСЂР°С‰Р°РµРј РѕР±СЉРµРєС‚ СЃ РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅС‹Рј РјРµС‚РѕРґРѕРј/Р°С‚СЂРёР±СѓС‚РѕРј РґР»СЏ РґРѕСЃС‚СѓРїР° РєР°Рє Рє dict
            single_result = results[self.ctrl_rc_ids[0]]
            # РЎРѕР·РґР°С‘Рј РѕР±С‘СЂС‚РєСѓ РґР»СЏ РґРѕСЃС‚СѓРїР° РїРѕ РёРЅРґРµРєСЃСѓ
            return _SingleResultWrapper(single_result, results)
        
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
        timeline: List[Dict[str, TimelineStep]] = []

        if not self.scenario_steps:
            return timeline

        for step in self.scenario_steps:
            step_results = self.step(step)
            if isinstance(step_results, _SingleResultWrapper):
                timeline.append(step_results._dict)
            else:
                timeline.append(step_results)

        # Р”Р»СЏ РѕР±СЂР°С‚РЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё: РµСЃР»Рё РѕРґРЅР° Р Р¦ вЂ” РІРѕР·РІСЂР°С‰Р°РµРј РїР»РѕСЃРєРёР№ СЃРїРёСЃРѕРє
        if len(self.ctrl_rc_ids) == 1:
            single_rc_id = self.ctrl_rc_ids[0]
            return [_SingleResultWrapper(t[single_rc_id], t) for t in timeline]
        
        return timeline


class _SingleResultWrapper:
    """
    РћР±С‘СЂС‚РєР° РґР»СЏ РѕР±СЂР°С‚РЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё РїСЂРё РѕРґРЅРѕР№ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕР№ Р Р¦.
    
    РџРѕР·РІРѕР»СЏРµС‚ РѕР±СЂР°С‰Р°С‚СЊСЃСЏ Рє СЂРµР·СѓР»СЊС‚Р°С‚Сѓ РєР°Рє:
    - result.lz_state (Р°С‚СЂРёР±СѓС‚С‹ TimelineStep)
    - result[0] РёР»Рё result["108"] (РєР°Рє dict)
    """
    def __init__(self, step: TimelineStep, dict_view: Dict[str, TimelineStep]):
        self._step = step
        self._dict = dict_view
        
        # РџСЂРѕРєСЃРёСЂСѓРµРј Р°С‚СЂРёР±СѓС‚С‹ TimelineStep
        self.t = step.t
        self.step_duration = step.step_duration
        self.ctrl_rc_id = step.ctrl_rc_id
        self.effective_prev_rc = step.effective_prev_rc
        self.effective_next_rc = step.effective_next_rc
        self.rc_states = step.rc_states
        self.switch_states = step.switch_states
        self.signal_states = step.signal_states
        self.modes = step.modes
        self.lz_state = step.lz_state
        self.lz_variant = step.lz_variant
        self.flags = step.flags
    
    def __getitem__(self, key):
        """РџРѕРґРґРµСЂР¶РєР° РґРѕСЃС‚СѓРїР° РєР°Рє Рє СЃР»РѕРІР°СЂСЋ: result["108"] РёР»Рё result[0]"""
        if isinstance(key, int):
            # result[0] -> РїРµСЂРІС‹Р№ (Рё РµРґРёРЅСЃС‚РІРµРЅРЅС‹Р№) СЌР»РµРјРµРЅС‚
            return list(self._dict.values())[key]
        return self._dict[key]
    
    def __contains__(self, key):
        """РџРѕРґРґРµСЂР¶РєР° РѕРїРµСЂР°С‚РѕСЂР° in: "108" in result"""
        return key in self._dict
    
    def get(self, key, default=None):
        """РџРѕРґРґРµСЂР¶РєР° РјРµС‚РѕРґР° get: result.get("108")"""
        return self._dict.get(key, default)
    
    def __iter__(self):
        """РС‚РµСЂР°С†РёСЏ РїРѕ РєР»СЋС‡Р°Рј (РґР»СЏ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё СЃ С†РёРєР»Р°РјРё)"""
        return iter(self._dict)
    
    def items(self):
        return self._dict.items()
    
    def keys(self):
        return self._dict.keys()
    
    def values(self):
        return self._dict.values()
    
    def __repr__(self):
        return f"TimelineStep({self.ctrl_rc_id}, t={self.t}, lz={self.lz_state}, flags={self.flags})"

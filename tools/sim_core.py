"""
sim_core.py — общий каркас симуляции с поддержкой множественных контролируемых РЦ
и динамической топологии.

Версия: 2.0 (с обратной совместимостью для старых тестов)

Для C: структуры с плоскими полями, явное управление памятью, без виртуальных методов.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Iterable, Tuple, Union

from station_model import load_station_from_config, StationModel
from topology_manager import UniversalTopologyManager

from detectors_engine import (
    DetectorsConfig,
    DetectorsState,
    init_detectors_engine,
    update_detectors,
)
from flags_engine import build_flags_simple


@dataclass
class ScenarioStep:
    """
    Описание входных данных на интервале [t, t_next).
    
    Для C: структура ScenarioStep с полями t, rc_states[], switch_states[] и т.д.
    """
    t: float                          # ДЛИТЕЛЬНОСТЬ интервала (сек)
    rc_states: Dict[str, int]         # Uni_State_ID по ID РЦ
    switch_states: Dict[str, int]     # Uni_State_ID по ID стрелок
    signal_states: Dict[str, int]     # Uni_State_ID по ID светофоров
    modes: Dict[str, Any]             # Режимы/параметры


@dataclass
class TimelineStep:
    """
    Результат симуляции для одной контролируемой РЦ на одном шаге.
    
    Для C: структура TimelineStep, массив таких структур — временная линия.
    """
    t: float
    step_duration: float
    ctrl_rc_id: str                   # NEW: какая РЦ контролировалась
    
    # Топологические соседи (из topology_manager)
    effective_prev_rc: Optional[str]
    effective_next_rc: Optional[str]
    
    # Сырые состояния
    rc_states: Dict[str, int]
    switch_states: Dict[str, int]
    signal_states: Dict[str, int]
    modes: Dict[str, Any]
    
    # Результаты детекторов/флагов
    lz_state: bool
    lz_variant: int
    flags: List[str]


@dataclass
class SimulationConfig:
    """
    Конфигурация симуляции для множества контролируемых РЦ.
    
    Для C: массив конфигураций, каждая со своим ctrl_rc_id.
    """
    t_pk: float
    # NEW: словарь {rc_id: DetectorsConfig} для множества контролируемых
    detectors_configs: Dict[str, DetectorsConfig] = field(default_factory=dict)
    
    # DEPRECATED: одиночная конфигурация (для обратной совместимости)
    detectors_config: Optional[DetectorsConfig] = None
    
    def __post_init__(self):
        # NEW: автоконвертация одиночной конфигурации в словарь
        if self.detectors_config is not None and not self.detectors_configs:
            self.detectors_configs[self.detectors_config.ctrl_rc_id] = self.detectors_config


class SimulationContext:
    """
    Контекст симуляции с поддержкой множества контролируемых РЦ.
    
    Для C: структура SimulationContext с массивом состояний детекторов,
    каждый элемент соответствует одной контролируемой РЦ.
    """

    def __init__(
        self,
        config: SimulationConfig,
        scenario: Iterable[ScenarioStep],
        # NEW: опционально — список контролируемых РЦ (берётся из config если не указан)
        ctrl_rc_ids: Optional[List[str]] = None,
        # DEPRECATED: старый параметр для обратной совместимости
        ctrl_rc_id: Optional[str] = None,
    ) -> None:
        self.config = config
        self.scenario_steps: List[ScenarioStep] = list(scenario)
        
        # Определяем список контролируемых РЦ
        if ctrl_rc_id is not None:
            # DEPRECATED: старый API
            self.ctrl_rc_ids = [ctrl_rc_id]
            # Конвертируем одиночный конфиг если нужно
            if not config.detectors_configs and config.detectors_config:
                config.detectors_configs[ctrl_rc_id] = config.detectors_config
        elif ctrl_rc_ids is not None:
            # NEW: новый API
            self.ctrl_rc_ids = ctrl_rc_ids
        else:
            # Берём из конфигов детекторов
            self.ctrl_rc_ids = list(config.detectors_configs.keys())
        
        if not self.ctrl_rc_ids:
            raise ValueError("Не указаны контролируемые РЦ (ctrl_rc_ids или ctrl_rc_id)")
        
        # Модель станции + топология (одна на все РЦ)
        self.model: StationModel = load_station_from_config()
        self.topology = UniversalTopologyManager(self.model, t_pk=config.t_pk)

        # Текущее время и состояния (общие для всех РЦ)
        self.time: float = 0.0
        self.rc_states: Dict[str, int] = {}
        self.switch_states: Dict[str, int] = {}
        self.signal_states: Dict[str, int] = {}

        # NEW: состояния детекторов для каждой контролируемой РЦ
        # Для C: массив структур DetectorsState, индекс = ctrl_rc_id
        self.detectors_states: Dict[str, DetectorsState] = {}
        for rc_id in self.ctrl_rc_ids:
            cfg = config.detectors_configs.get(rc_id)
            if cfg:
                self.detectors_states[rc_id] = init_detectors_engine(
                    cfg=cfg,
                    rc_ids=list(self.model.rc_nodes.keys()),
                )
            else:
                raise ValueError(f"Нет конфигурации для РЦ {rc_id}")

        # Инициализация начальными данными
        if self.scenario_steps:
            first = self.scenario_steps[0]
            self.rc_states = dict(first.rc_states)
            self.switch_states = dict(first.switch_states)
            self.signal_states = dict(first.signal_states)

    def _compute_effective_neighbors_with_control(
        self,
        ctrl_rc_id: str,
        dt: float,
    ) -> Tuple[Optional[str], Optional[str], bool, bool, bool, bool]:
        """
        Вычисляет соседей и флаги контроля/крайности (NC) для конкретной РЦ.
        """
        prev_rc, next_rc, prev_ok, next_ok, prev_nc, next_nc = self.topology.get_neighbors_with_control(
            ctrl_rc_id,
            switch_states=self.switch_states,
            dt=dt,
        )
        return prev_rc or None, next_rc or None, prev_ok, next_ok, prev_nc, next_nc

    def _step_single_rc(
        self,
        ctrl_rc_id: str,
        step: ScenarioStep,
        dt: float,
    ) -> TimelineStep:
        """
        Один шаг симуляции для одной контролируемой РЦ.
        
        Для C: отдельная функция или inline в основном цикле.
        """
        from detectors_engine import _ensure_rc_states_by_id
        rc_states_by_id = _ensure_rc_states_by_id(self.rc_states)
        
        # 1. Вычисляем топологию для этой конкретной РЦ
        effective_prev_rc, effective_next_rc, prev_ok, next_ok, prev_nc, next_nc = \
            self._compute_effective_neighbors_with_control(ctrl_rc_id, dt)

        # 2. Формируем topology_info для детекторов
        topology_info = {
            "ctrl_rc_id": ctrl_rc_id,
            "effective_prev_rc": effective_prev_rc,
            "effective_next_rc": effective_next_rc,
        }

        # 3. Готовим modes
        modes_for_detectors = dict(step.modes)
        modes_for_detectors["prev_control_ok"] = prev_ok
        modes_for_detectors["next_control_ok"] = next_ok
        modes_for_detectors["prev_nc"] = prev_nc
        modes_for_detectors["next_nc"] = next_nc

        # 4. Получаем состояние детекторов для этой РЦ
        det_state = self.detectors_states.get(ctrl_rc_id)
        
        # 5. Обновляем детекторы
        if det_state:
            new_det_state, det_result = update_detectors(
                det_state=det_state,
                station_model=self.model,
                t=self.time,
                dt=dt,
                rc_states=rc_states_by_id, 
                switch_states=self.switch_states,
                signal_states=self.signal_states,
                topology_info=topology_info,
                cfg=self.config.detectors_configs[ctrl_rc_id],
                modes=modes_for_detectors,
            )
            self.detectors_states[ctrl_rc_id] = new_det_state
        else:
            # Нет детекторов — создаём пустой результат
            from detectors_engine import DetectorsResult
            det_result = DetectorsResult()

        # 6. Строим флаги
        flags_res = build_flags_simple(
            ctrl_rc_id=ctrl_rc_id,
            det_state=det_state or DetectorsState(),
            det_result=det_result,
            rc_states=rc_states_by_id,
            switch_states=self.switch_states,
        )

        # 7. Собираем результат
        return TimelineStep(
            t=self.time,
            step_duration=dt,
            ctrl_rc_id=ctrl_rc_id,  # NEW
            effective_prev_rc=effective_prev_rc,
            effective_next_rc=effective_next_rc,
            rc_states=dict(self.rc_states),
            switch_states=dict(self.switch_states),
            signal_states=dict(self.signal_states),
            modes=dict(modes_for_detectors),
            lz_state=flags_res.lz,
            lz_variant=flags_res.variant,
            flags=list(flags_res.flags),
        )

    def step(self, step: ScenarioStep) -> Union[TimelineStep, Dict[str, TimelineStep]]:
        """
        Один шаг симуляции для всех контролируемых РЦ.
        
        NEW: возвращает Dict[str, TimelineStep] вместо одного шага.
        Для обратной совместимости: если одна РЦ — можно получить по [0] или .get()
        
        Для C: цикл по массиву ctrl_rc_ids, заполнение массива результатов.
        """
        dt = max(0.0, float(step.t))

        # Обновляем состояния (общие для всех РЦ)
        self.rc_states = dict(step.rc_states)
        self.switch_states = dict(step.switch_states)
        self.signal_states = dict(step.signal_states)

        # NEW: вычисляем шаг для каждой контролируемой РЦ
        results: Dict[str, TimelineStep] = {}
        for rc_id in self.ctrl_rc_ids:
            results[rc_id] = self._step_single_rc(rc_id, step, dt)

        # Сдвигаем время (одно на все РЦ)
        self.time += dt

        # Для обратной совместимости: если одна РЦ — возвращаем её напрямую
        # Но сохраняем возможность получить как словарь
        if len(self.ctrl_rc_ids) == 1:
            # Возвращаем объект с дополнительным методом/атрибутом для доступа как к dict
            single_result = results[self.ctrl_rc_ids[0]]
            # Создаём обёртку для доступа по индексу
            return _SingleResultWrapper(single_result, results)
        
        return results

    def run(self) -> Union[List[TimelineStep], List[Dict[str, TimelineStep]]]:
        """
        Прогоняет весь сценарий.
        
        NEW: возвращает List[Dict[str, TimelineStep]] — 
        каждый элемент списка = один временной шаг, 
        внутри словарь по контролируемым РЦ.
        
        Для обратной совместимости: если одна РЦ — List[TimelineStep]
        
        Для C: двумерный массив или массив структур с полем rc_id.
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

        # Для обратной совместимости: если одна РЦ — возвращаем плоский список
        if len(self.ctrl_rc_ids) == 1:
            single_rc_id = self.ctrl_rc_ids[0]
            return [_SingleResultWrapper(t[single_rc_id], t) for t in timeline]
        
        return timeline


class _SingleResultWrapper:
    """
    Обёртка для обратной совместимости при одной контролируемой РЦ.
    
    Позволяет обращаться к результату как:
    - result.lz_state (атрибуты TimelineStep)
    - result[0] или result["108"] (как dict)
    """
    def __init__(self, step: TimelineStep, dict_view: Dict[str, TimelineStep]):
        self._step = step
        self._dict = dict_view
        
        # Проксируем атрибуты TimelineStep
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
        """Поддержка доступа как к словарю: result["108"] или result[0]"""
        if isinstance(key, int):
            # result[0] -> первый (и единственный) элемент
            return list(self._dict.values())[key]
        return self._dict[key]
    
    def __contains__(self, key):
        """Поддержка оператора in: "108" in result"""
        return key in self._dict
    
    def get(self, key, default=None):
        """Поддержка метода get: result.get("108")"""
        return self._dict.get(key, default)
    
    def __iter__(self):
        """Итерация по ключам (для совместимости с циклами)"""
        return iter(self._dict)
    
    def items(self):
        return self._dict.items()
    
    def keys(self):
        return self._dict.keys()
    
    def values(self):
        return self._dict.values()
    
    def __repr__(self):
        return f"TimelineStep({self.ctrl_rc_id}, t={self.t}, lz={self.lz_state}, flags={self.flags})"
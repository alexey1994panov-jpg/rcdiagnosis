# base_detector.py — РЕФАКТОРИНГ: поддержка декларативных масок + динамическая топология

from enum import Enum
from typing import Any, Callable, List, Optional, Tuple, Dict
from dataclasses import dataclass, field


class CompletionMode(Enum):
    FREE_TIME = "free_time"
    OCCUPIED_TIME = "occupied_time"

from enum import Enum

class NeighborRequirement(Enum):
    BOTH = "both"   # Оба соседа достоверны (v1,v2,v3,v8)
    NONE = "none"   # Соседей нет (v7)
    ONLY_CTRL = "only_ctrl"
    ONE_NC = "one_nc"       # Требуется хотя бы один сосед с флагом NC (LS6, LZ12)
    ONE_ADJ = "one_adj"     # Требуется хотя бы один валидный сосед (LZ13)

@dataclass
class PhaseConfig:
    """
    Расширенная конфигурация фазы с поддержкой декларативных масок.
    """
    phase_id: int
    duration: float
    next_phase_id: int
    timer_mode: str = "continuous"  # "continuous" / "cumulative"
    reset_on_exit: bool = False
    
    # Идентификатор маски (для отладки и сериализации)
    mask_id: Optional[int] = None
    
    # Функция-проверка условия фазы: (step, prev, ctrl, next) -> bool
    # step содержит rc_states, modes, effective_prev_rc, effective_next_rc
    mask_fn: Optional[Callable[[Any, Optional[str], str, Optional[str]], bool]] = None
    
    # Требования к достоверности соседей (None = не проверять)
    requires_neighbors: NeighborRequirement = NeighborRequirement.BOTH


@dataclass
class DetectorConfig:
    initial_phase_id: int
    phases: List[PhaseConfig]
    t_kon: float
    completion_mode: CompletionMode
    variant_name: Optional[str] = None  # для отладки


# Типы для обратной совместимости (классический режим)
ConditionFn = Callable[[int, Any], bool]
CompletionStateFn = Callable[[Any], Tuple[bool, bool]]


class BaseDetector:
    """
    Универсальный детектор с поддержкой двух режимов:
    
    1. КЛАССИЧЕСКИЙ: через condition_fn (для сложной логики)
    2. ДЕКЛАРАТИВНЫЙ: через PhaseConfig.mask_fn (для масок 000/010 и т.д.)
    
    Для C: структура Detector с указателями на функции, union для режимов.
    """

    def __init__(
        self,
        config: DetectorConfig,
        condition_fn: Optional[ConditionFn] = None,
        completion_state_fn: Optional[CompletionStateFn] = None,
        # Декларативный способ: имена РЦ из конфига как fallback/для логирования
        prev_rc_name: Optional[str] = None,
        ctrl_rc_name: Optional[str] = None,
        next_rc_name: Optional[str] = None,
    ):
        self.config = config
        
        # Имена из конфига — используются только если в step нет effective_*_rc
        # Для C: строковые поля для отладки, основная логика на effective из step
        self._config_prev_rc = prev_rc_name
        self._config_ctrl_rc = ctrl_rc_name
        self._config_next_rc = next_rc_name
        
        # Определяем режим работы
        self._declarative_mode = self._detect_declarative_mode()
        
        # Строим condition_fn
        if condition_fn is not None:
            self._cond = condition_fn
        elif self._declarative_mode:
            self._cond = self._build_condition_from_masks()
        else:
            raise ValueError("Neither condition_fn nor declarative masks provided")
        
        # Строим completion_state_fn
        if completion_state_fn is not None:
            self._compl_state = completion_state_fn
        elif self._declarative_mode:
            self._compl_state = self._build_completion_from_config()
        else:
            raise ValueError("Neither completion_state_fn nor ctrl_rc_name provided")

        # Состояние конечного автомата
        # Для C: отдельная структура DetectorState
        self.current_phase_id: int = config.initial_phase_id
        self.timer: float = 0.0
        self.active: bool = False
        self.completion_timer: float = 0.0

    def _detect_declarative_mode(self) -> bool:
        """Проверяем, есть ли хотя бы одна фаза с mask_fn"""
        for phase in self.config.phases:
            if phase.mask_fn is not None:
                return True
        return False

    def _get_phase(self, phase_id: int) -> Optional[PhaseConfig]:
        for p in self.config.phases:
            if p.phase_id == phase_id:
                return p
        return None

    # base_detector.py — _get_effective_neighbors

    def _get_effective_neighbors(self, step: Any) -> Tuple[Optional[str], str, Optional[str]]:
        """
        Получает эффективных соседей из step.
        ВСЕ значения — ID (для C: целочисленные или строковые идентификаторы).
        """
        # prev/next из топологии — уже ID
        # Если атрибуты есть в step (даже если они None/пустые), 
        # значит мы в режиме динамической топологии и НЕ должны делать fallback.
        prev = getattr(step, "effective_prev_rc", None)
        if prev is None and not hasattr(step, "effective_prev_rc"):
            prev = self._config_prev_rc
            
        # ctrl — ID контролируемой РЦ
        ctrl = self._config_ctrl_rc
        if not ctrl:
            ctrl = getattr(step, "ctrl_rc_name", None) or ""
            
        nxt = getattr(step, "effective_next_rc", None)
        if nxt is None and not hasattr(step, "effective_next_rc"):
            nxt = self._config_next_rc
        
        return prev, ctrl, nxt  # все ID!

    def _build_condition_from_masks(self) -> ConditionFn:
        """
        Строит condition_fn автоматически из масок в PhaseConfig.
        
        Для C: кодогенерация или таблица указателей на функции-маки.
        """
        def condition_fn(phase_id: int, step: Any) -> bool:
            phase = self._get_phase(phase_id)
            if phase is None or phase.mask_fn is None:
                return False
            
            
            # ШАГ 1: Проверка достоверности соседей через modes
            # Для C: чтение полей из step.modes (структура с флагами)
            modes = getattr(step, "modes", {}) or {}

            # Локальная правка для v5/v6:
            if phase.requires_neighbors == NeighborRequirement.ONLY_CTRL:
                # Проверяем только то, что контролируемая РЦ существует в rc_states
                # (для v5 соседи не важны, важно только состояние самой РЦ)
                prev, ctrl, nxt = self._get_effective_neighbors(step)
                if not ctrl or ctrl not in step.rc_states:
                    return False
            
            if phase.requires_neighbors == NeighborRequirement.BOTH:
                # Для v1, v2, v3, v8 проверяем флаги соседей
                if not modes.get("prev_control_ok", True) or not modes.get("next_control_ok", True):
                    return False
            
            if phase.requires_neighbors == NeighborRequirement.ONE_NC:
                # Требуется хотя бы один NC (край)
                if not modes.get("prev_nc", False) and not modes.get("next_nc", False):
                    return False

            if phase.requires_neighbors == NeighborRequirement.ONE_ADJ:
                 # Требуется хотя бы один сосед
                prev, ctrl, nxt = self._get_effective_neighbors(step)
                if not prev and not nxt:
                    return False

            # NONE — не проверяем
            
            # ШАГ 2: Проверка маски состояний РЦ
            # Для C: вызов функции-маски с аргументами (step, prev, ctrl, next)
            prev, ctrl, nxt = self._get_effective_neighbors(step)
            
            if not ctrl:
                return False
            
            return phase.mask_fn(step, prev, ctrl, nxt)
        
        return condition_fn

    def _build_completion_from_config(self) -> CompletionStateFn:
        """
        Стандартная функция завершения: проверяет свободность ctrl РЦ.
        
        Для C: inline функция или макрос.
        """
        from uni_states import rc_is_free, rc_is_occupied
        
        def completion_fn(step: Any) -> Tuple[bool, bool]:
            # Берём ctrl из конфига (контролируемая РЦ фиксирована)
            ctrl = self._config_ctrl_rc
            
            if not ctrl:
                # Fallback: пробуем получить из step
                ctrl = getattr(step, "ctrl_rc_name", None) or ""
            
            if not ctrl:
                # Не удалось определить ctrl — считаем свободной
                return True, False
            
            st = step.rc_states.get(ctrl, 0)
            return rc_is_free(st), rc_is_occupied(st)
        
        return completion_fn

    def _update_formation(self, step: Any, dt: float) -> bool:
        """Обновление фаз формирования (до открытия ДС)"""
        phase = self._get_phase(self.current_phase_id)
        if phase is None:
            return False

        cond = self._cond(self.current_phase_id, step)

        if cond:
            self.timer += dt
            if self.timer >= phase.duration:
                if phase.next_phase_id < 0:
                    # Финальная фаза — открываем ДС
                    self.active = True
                    self.completion_timer = 0.0
                    self.timer = 0.0
                    return True  # opened=True
                else:
                    # Переход к следующей фазе
                    self.current_phase_id = phase.next_phase_id
                    if phase.reset_on_exit:
                        self.timer = 0.0
        else:
            # Условие не выполнено
            if phase.timer_mode == "continuous":
                self.timer = 0.0
            # При "cumulative" таймер не сбрасывается

        return False

    def _update_completion(self, dt: float, step: Any) -> bool:
        """Обновление фазы завершения (после открытия ДС)"""
        if not self.active:
            return False

        is_free, is_occ = self._compl_state(step)

        if self.config.completion_mode == CompletionMode.FREE_TIME:
            if is_free:
                self.completion_timer += dt
            else:
                self.completion_timer = 0.0
        else:  # OCCUPIED_TIME
            if is_occ:
                self.completion_timer += dt
            else:
                self.completion_timer = 0.0

        if self.completion_timer >= self.config.t_kon:
            self.reset()
            return True  # closed=True

        return False

    def reset(self) -> None:
        """Сброс детектора в начальное состояние"""
        self.current_phase_id = self.config.initial_phase_id
        self.timer = 0.0
        self.active = False
        self.completion_timer = 0.0

    def update(self, step: Any, dt: float) -> Tuple[bool, bool]:
        """
        Основной метод обновления.
        
        Returns:
            (opened, closed): флаги переходов состояний
        """
        opened = False
        closed = False

        if not self.active:
            opened = self._update_formation(step, dt)
        else:
            closed = self._update_completion(dt, step)

        return opened, closed

    def get_current_mask_id(self) -> Optional[int]:
        """Возвращает ID маски текущей фазы (для отладки)"""
        phase = self._get_phase(self.current_phase_id)
        return phase.mask_id if phase else None
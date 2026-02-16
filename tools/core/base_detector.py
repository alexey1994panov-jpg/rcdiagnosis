# base_detector.py вЂ” Р Р•Р¤РђРљРўРћР РРќР“: РїРѕРґРґРµСЂР¶РєР° РґРµРєР»Р°СЂР°С‚РёРІРЅС‹С… РјР°СЃРѕРє + РґРёРЅР°РјРёС‡РµСЃРєР°СЏ С‚РѕРїРѕР»РѕРіРёСЏ

from enum import Enum
from typing import Any, Callable, List, Optional, Tuple, Dict
from dataclasses import dataclass, field


class CompletionMode(Enum):
    FREE_TIME = "free_time"
    OCCUPIED_TIME = "occupied_time"

from enum import Enum

class NeighborRequirement(Enum):
    BOTH = "both"   # РћР±Р° СЃРѕСЃРµРґР° РґРѕСЃС‚РѕРІРµСЂРЅС‹ (v1,v2,v3,v8)
    NONE = "none"   # РЎРѕСЃРµРґРµР№ РЅРµС‚ (v7)
    ONLY_CTRL = "only_ctrl"
    ONE_NC = "one_nc"       # РўСЂРµР±СѓРµС‚СЃСЏ С…РѕС‚СЏ Р±С‹ РѕРґРёРЅ СЃРѕСЃРµРґ СЃ С„Р»Р°РіРѕРј NC (LS6, LZ12)
    ONE_ADJ = "one_adj"     # РўСЂРµР±СѓРµС‚СЃСЏ С…РѕС‚СЏ Р±С‹ РѕРґРёРЅ РІР°Р»РёРґРЅС‹Р№ СЃРѕСЃРµРґ (LZ13)

@dataclass
class PhaseConfig:
    """
    Р Р°СЃС€РёСЂРµРЅРЅР°СЏ РєРѕРЅС„РёРіСѓСЂР°С†РёСЏ С„Р°Р·С‹ СЃ РїРѕРґРґРµСЂР¶РєРѕР№ РґРµРєР»Р°СЂР°С‚РёРІРЅС‹С… РјР°СЃРѕРє.
    """
    phase_id: int
    duration: float
    next_phase_id: int
    timer_mode: str = "continuous"  # "continuous" / "cumulative"
    reset_on_exit: bool = False
    
    # РРґРµРЅС‚РёС„РёРєР°С‚РѕСЂ РјР°СЃРєРё (РґР»СЏ РѕС‚Р»Р°РґРєРё Рё СЃРµСЂРёР°Р»РёР·Р°С†РёРё)
    mask_id: Optional[int] = None
    
    # Р¤СѓРЅРєС†РёСЏ-РїСЂРѕРІРµСЂРєР° СѓСЃР»РѕРІРёСЏ С„Р°Р·С‹: (step, prev, ctrl, next) -> bool
    # step СЃРѕРґРµСЂР¶РёС‚ rc_states, modes, effective_prev_rc, effective_next_rc
    mask_fn: Optional[Callable[[Any, Optional[str], str, Optional[str]], bool]] = None
    
    # РўСЂРµР±РѕРІР°РЅРёСЏ Рє РґРѕСЃС‚РѕРІРµСЂРЅРѕСЃС‚Рё СЃРѕСЃРµРґРµР№ (None = РЅРµ РїСЂРѕРІРµСЂСЏС‚СЊ)
    requires_neighbors: NeighborRequirement = NeighborRequirement.BOTH
    # РљР»СЋС‡Рё РёСЃРєР»СЋС‡РµРЅРёР№ РёР· step.modes. Р•СЃР»Рё Р»СЋР±РѕР№ True, С„Р°Р·Р° РїСЂРµСЂС‹РІР°РµС‚СЃСЏ.
    abort_exception_keys: Tuple[str, ...] = ()
    # РџСЂРё РїСЂРµСЂС‹РІР°РЅРёРё С„Р°Р·С‹ СЃР±СЂР°СЃС‹РІР°РµРј РґРµС‚РµРєС‚РѕСЂ РІ initial phase.
    reset_on_exception: bool = True


@dataclass
class DetectorConfig:
    initial_phase_id: int
    phases: List[PhaseConfig]
    t_kon: float
    completion_mode: CompletionMode
    variant_name: Optional[str] = None  # РґР»СЏ РѕС‚Р»Р°РґРєРё


# РўРёРїС‹ РґР»СЏ РѕР±СЂР°С‚РЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё (РєР»Р°СЃСЃРёС‡РµСЃРєРёР№ СЂРµР¶РёРј)
ConditionFn = Callable[[int, Any], bool]
CompletionStateFn = Callable[[Any], Tuple[bool, bool]]


class BaseDetector:
    """
    РЈРЅРёРІРµСЂСЃР°Р»СЊРЅС‹Р№ РґРµС‚РµРєС‚РѕСЂ СЃ РїРѕРґРґРµСЂР¶РєРѕР№ РґРІСѓС… СЂРµР¶РёРјРѕРІ:
    
    1. РљР›РђРЎРЎРР§Р•РЎРљРР™: С‡РµСЂРµР· condition_fn (РґР»СЏ СЃР»РѕР¶РЅРѕР№ Р»РѕРіРёРєРё)
    2. Р”Р•РљР›РђР РђРўРР’РќР«Р™: С‡РµСЂРµР· PhaseConfig.mask_fn (РґР»СЏ РјР°СЃРѕРє 000/010 Рё С‚.Рґ.)
    
    Р”Р»СЏ C: СЃС‚СЂСѓРєС‚СѓСЂР° Detector СЃ СѓРєР°Р·Р°С‚РµР»СЏРјРё РЅР° С„СѓРЅРєС†РёРё, union РґР»СЏ СЂРµР¶РёРјРѕРІ.
    """

    def __init__(
        self,
        config: DetectorConfig,
        condition_fn: Optional[ConditionFn] = None,
        completion_state_fn: Optional[CompletionStateFn] = None,
        # Р”РµРєР»Р°СЂР°С‚РёРІРЅС‹Р№ СЃРїРѕСЃРѕР±: РёРјРµРЅР° Р Р¦ РёР· РєРѕРЅС„РёРіР° РєР°Рє fallback/РґР»СЏ Р»РѕРіРёСЂРѕРІР°РЅРёСЏ
        prev_rc_name: Optional[str] = None,
        ctrl_rc_name: Optional[str] = None,
        next_rc_name: Optional[str] = None,
    ):
        self.config = config
        
        # РРјРµРЅР° РёР· РєРѕРЅС„РёРіР° вЂ” РёСЃРїРѕР»СЊР·СѓСЋС‚СЃСЏ С‚РѕР»СЊРєРѕ РµСЃР»Рё РІ step РЅРµС‚ effective_*_rc
        # Р”Р»СЏ C: СЃС‚СЂРѕРєРѕРІС‹Рµ РїРѕР»СЏ РґР»СЏ РѕС‚Р»Р°РґРєРё, РѕСЃРЅРѕРІРЅР°СЏ Р»РѕРіРёРєР° РЅР° effective РёР· step
        self._config_prev_rc = prev_rc_name
        self._config_ctrl_rc = ctrl_rc_name
        self._config_next_rc = next_rc_name
        
        # РћРїСЂРµРґРµР»СЏРµРј СЂРµР¶РёРј СЂР°Р±РѕС‚С‹
        self._declarative_mode = self._detect_declarative_mode()
        
        # РЎС‚СЂРѕРёРј condition_fn
        if condition_fn is not None:
            self._cond = condition_fn
        elif self._declarative_mode:
            self._cond = self._build_condition_from_masks()
        else:
            raise ValueError("Neither condition_fn nor declarative masks provided")
        
        # РЎС‚СЂРѕРёРј completion_state_fn
        if completion_state_fn is not None:
            self._compl_state = completion_state_fn
        elif self._declarative_mode:
            self._compl_state = self._build_completion_from_config()
        else:
            raise ValueError("Neither completion_state_fn nor ctrl_rc_name provided")

        # РЎРѕСЃС‚РѕСЏРЅРёРµ РєРѕРЅРµС‡РЅРѕРіРѕ Р°РІС‚РѕРјР°С‚Р°
        # Р”Р»СЏ C: РѕС‚РґРµР»СЊРЅР°СЏ СЃС‚СЂСѓРєС‚СѓСЂР° DetectorState
        self.current_phase_id: int = config.initial_phase_id
        self.timer: float = 0.0
        self.active: bool = False
        self.completion_timer: float = 0.0
        self.last_open_offset: Optional[float] = None
        self.last_close_offset: Optional[float] = None

    def _detect_declarative_mode(self) -> bool:
        """РџСЂРѕРІРµСЂСЏРµРј, РµСЃС‚СЊ Р»Рё С…РѕС‚СЏ Р±С‹ РѕРґРЅР° С„Р°Р·Р° СЃ mask_fn"""
        for phase in self.config.phases:
            if phase.mask_fn is not None:
                return True
        return False

    def _get_phase(self, phase_id: int) -> Optional[PhaseConfig]:
        for p in self.config.phases:
            if p.phase_id == phase_id:
                return p
        return None

    # base_detector.py вЂ” _get_effective_neighbors

    def _get_effective_neighbors(self, step: Any) -> Tuple[Optional[str], str, Optional[str]]:
        """
        РџРѕР»СѓС‡Р°РµС‚ СЌС„С„РµРєС‚РёРІРЅС‹С… СЃРѕСЃРµРґРµР№ РёР· step.
        Р’РЎР• Р·РЅР°С‡РµРЅРёСЏ вЂ” ID (РґР»СЏ C: С†РµР»РѕС‡РёСЃР»РµРЅРЅС‹Рµ РёР»Рё СЃС‚СЂРѕРєРѕРІС‹Рµ РёРґРµРЅС‚РёС„РёРєР°С‚РѕСЂС‹).
        """
        # prev/next РёР· С‚РѕРїРѕР»РѕРіРёРё вЂ” СѓР¶Рµ ID
        # Р•СЃР»Рё Р°С‚СЂРёР±СѓС‚С‹ РµСЃС‚СЊ РІ step (РґР°Р¶Рµ РµСЃР»Рё РѕРЅРё None/РїСѓСЃС‚С‹Рµ), 
        # Р·РЅР°С‡РёС‚ РјС‹ РІ СЂРµР¶РёРјРµ РґРёРЅР°РјРёС‡РµСЃРєРѕР№ С‚РѕРїРѕР»РѕРіРёРё Рё РќР• РґРѕР»Р¶РЅС‹ РґРµР»Р°С‚СЊ fallback.
        prev = getattr(step, "effective_prev_rc", None)
        if prev is None and not hasattr(step, "effective_prev_rc"):
            prev = self._config_prev_rc
            
        # ctrl вЂ” ID РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕР№ Р Р¦
        ctrl = self._config_ctrl_rc
        if not ctrl:
            ctrl = getattr(step, "ctrl_rc_name", None) or ""
            
        nxt = getattr(step, "effective_next_rc", None)
        if nxt is None and not hasattr(step, "effective_next_rc"):
            nxt = self._config_next_rc
        
        return prev, ctrl, nxt  # РІСЃРµ ID!

    def _build_condition_from_masks(self) -> ConditionFn:
        """
        РЎС‚СЂРѕРёС‚ condition_fn Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё РёР· РјР°СЃРѕРє РІ PhaseConfig.
        
        Р”Р»СЏ C: РєРѕРґРѕРіРµРЅРµСЂР°С†РёСЏ РёР»Рё С‚Р°Р±Р»РёС†Р° СѓРєР°Р·Р°С‚РµР»РµР№ РЅР° С„СѓРЅРєС†РёРё-РјР°РєРё.
        """
        def condition_fn(phase_id: int, step: Any) -> bool:
            phase = self._get_phase(phase_id)
            if phase is None or phase.mask_fn is None:
                return False
            
            
            # РЁРђР“ 1: РџСЂРѕРІРµСЂРєР° РґРѕСЃС‚РѕРІРµСЂРЅРѕСЃС‚Рё СЃРѕСЃРµРґРµР№ С‡РµСЂРµР· modes
            # Р”Р»СЏ C: С‡С‚РµРЅРёРµ РїРѕР»РµР№ РёР· step.modes (СЃС‚СЂСѓРєС‚СѓСЂР° СЃ С„Р»Р°РіР°РјРё)
            modes = getattr(step, "modes", {}) or {}

            # Р›РѕРєР°Р»СЊРЅР°СЏ РїСЂР°РІРєР° РґР»СЏ v5/v6:
            if phase.requires_neighbors == NeighborRequirement.ONLY_CTRL:
                # РџСЂРѕРІРµСЂСЏРµРј С‚РѕР»СЊРєРѕ С‚Рѕ, С‡С‚Рѕ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјР°СЏ Р Р¦ СЃСѓС‰РµСЃС‚РІСѓРµС‚ РІ rc_states
                # (РґР»СЏ v5 СЃРѕСЃРµРґРё РЅРµ РІР°Р¶РЅС‹, РІР°Р¶РЅРѕ С‚РѕР»СЊРєРѕ СЃРѕСЃС‚РѕСЏРЅРёРµ СЃР°РјРѕР№ Р Р¦)
                prev, ctrl, nxt = self._get_effective_neighbors(step)
                if not ctrl or ctrl not in step.rc_states:
                    return False
            
            if phase.requires_neighbors == NeighborRequirement.BOTH:
                # Р”Р»СЏ v1, v2, v3, v8 РїСЂРѕРІРµСЂСЏРµРј С„Р»Р°РіРё СЃРѕСЃРµРґРµР№
                if not modes.get("prev_control_ok", True) or not modes.get("next_control_ok", True):
                    return False
            
            if phase.requires_neighbors == NeighborRequirement.ONE_NC:
                # РўСЂРµР±СѓРµС‚СЃСЏ С…РѕС‚СЏ Р±С‹ РѕРґРёРЅ NC (РєСЂР°Р№)
                if not modes.get("prev_nc", False) and not modes.get("next_nc", False):
                    return False

            if phase.requires_neighbors == NeighborRequirement.ONE_ADJ:
                 # РўСЂРµР±СѓРµС‚СЃСЏ С…РѕС‚СЏ Р±С‹ РѕРґРёРЅ СЃРѕСЃРµРґ
                prev, ctrl, nxt = self._get_effective_neighbors(step)
                if not prev and not nxt:
                    return False

            # NONE вЂ” РЅРµ РїСЂРѕРІРµСЂСЏРµРј
            
            # РЁРђР“ 2: РџСЂРѕРІРµСЂРєР° РјР°СЃРєРё СЃРѕСЃС‚РѕСЏРЅРёР№ Р Р¦
            # Р”Р»СЏ C: РІС‹Р·РѕРІ С„СѓРЅРєС†РёРё-РјР°СЃРєРё СЃ Р°СЂРіСѓРјРµРЅС‚Р°РјРё (step, prev, ctrl, next)
            prev, ctrl, nxt = self._get_effective_neighbors(step)
            
            if not ctrl:
                return False
            
            return phase.mask_fn(step, prev, ctrl, nxt)
        
        return condition_fn

    def _build_completion_from_config(self) -> CompletionStateFn:
        """
        РЎС‚Р°РЅРґР°СЂС‚РЅР°СЏ С„СѓРЅРєС†РёСЏ Р·Р°РІРµСЂС€РµРЅРёСЏ: РїСЂРѕРІРµСЂСЏРµС‚ СЃРІРѕР±РѕРґРЅРѕСЃС‚СЊ ctrl Р Р¦.
        
        Р”Р»СЏ C: inline С„СѓРЅРєС†РёСЏ РёР»Рё РјР°РєСЂРѕСЃ.
        """
        from core.uni_states import rc_is_free, rc_is_occupied
        
        def completion_fn(step: Any) -> Tuple[bool, bool]:
            # Р‘РµСЂС‘Рј ctrl РёР· РєРѕРЅС„РёРіР° (РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјР°СЏ Р Р¦ С„РёРєСЃРёСЂРѕРІР°РЅР°)
            ctrl = self._config_ctrl_rc
            
            if not ctrl:
                # Fallback: РїСЂРѕР±СѓРµРј РїРѕР»СѓС‡РёС‚СЊ РёР· step
                ctrl = getattr(step, "ctrl_rc_name", None) or ""
            
            if not ctrl:
                # РќРµ СѓРґР°Р»РѕСЃСЊ РѕРїСЂРµРґРµР»РёС‚СЊ ctrl вЂ” СЃС‡РёС‚Р°РµРј СЃРІРѕР±РѕРґРЅРѕР№
                return True, False
            
            st = step.rc_states.get(ctrl, 0)
            return rc_is_free(st), rc_is_occupied(st)
        
        return completion_fn

    def _update_formation(self, step: Any, dt: float) -> Tuple[bool, float]:
        """
        РћР±РЅРѕРІР»РµРЅРёРµ С„Р°Р· С„РѕСЂРјРёСЂРѕРІР°РЅРёСЏ (РґРѕ РѕС‚РєСЂС‹С‚РёСЏ Р”РЎ).

        Возвращает:
            (opened, remaining_dt)
        remaining_dt — часть интервала шага, которая осталась после открытия детектора.
        """
        opened = False
        remaining = float(dt)
        eps = 1e-9
        guard = 0

        while remaining > eps and not self.active:
            guard += 1
            if guard > 32:
                break

            phase = self._get_phase(self.current_phase_id)
            if phase is None:
                break

            # Универсальный фазовый hook исключений.
            if self._is_phase_excluded(step, phase):
                self.timer = 0.0
                if phase.reset_on_exception:
                    self.current_phase_id = self.config.initial_phase_id
                break

            cond = self._cond(self.current_phase_id, step)
            if not cond:
                # Для фаз, требующих валидных соседей с обеих сторон, потеря контроля
                # над любой стороной должна сбрасывать прогресс варианта полностью.
                # Иначе возможен "доскок" до открытия из поздней фазы после долгого
                # no-control на стрелке (например, LS2/LZ2/LZ3 при BOTH).
                modes = getattr(step, "modes", {}) or {}
                if (
                    phase.requires_neighbors == NeighborRequirement.BOTH
                    and (
                        not modes.get("prev_control_ok", True)
                        or not modes.get("next_control_ok", True)
                    )
                ):
                    self.timer = 0.0
                    self.current_phase_id = self.config.initial_phase_id
                    break

                if phase.timer_mode == "continuous":
                    self.timer = 0.0
                # При "cumulative" таймер не сбрасывается.
                break

            # cond=True: накапливаем только до порога текущей фазы.
            need = max(phase.duration - self.timer, 0.0)
            consume = remaining if need <= eps else min(remaining, need)
            self.timer += consume
            remaining -= consume

            if self.timer + eps < phase.duration:
                break

            # Порог фазы достигнут.
            if phase.next_phase_id < 0:
                self.active = True
                self.completion_timer = 0.0
                self.timer = 0.0
                opened = True
                break

            # Переход к следующей фазе.
            self.current_phase_id = phase.next_phase_id
            if phase.reset_on_exit:
                self.timer = 0.0

            # Если на этой итерации не потрачено время (переход "мгновенный"),
            # продолжаем цикл с тем же remaining — это делает поведение
            # инвариантным к размеру dt при константном состоянии шага.

        return opened, remaining

    def _is_phase_excluded(self, step: Any, phase: PhaseConfig) -> bool:
        keys = phase.abort_exception_keys or ()
        if not keys:
            return False
        modes = getattr(step, "modes", {}) or {}
        for key in keys:
            if bool(modes.get(key, False)):
                return True
        return False

    def _update_completion(self, dt: float, step: Any) -> Tuple[bool, float]:
        """РћР±РЅРѕРІР»РµРЅРёРµ С„Р°Р·С‹ Р·Р°РІРµСЂС€РµРЅРёСЏ (РїРѕСЃР»Рµ РѕС‚РєСЂС‹С‚РёСЏ Р”РЎ)"""
        if not self.active:
            return False, 0.0

        is_free, is_occ = self._compl_state(step)
        prev_timer = self.completion_timer

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
            need = max(self.config.t_kon - prev_timer, 0.0)
            close_offset = min(float(dt), need)
            self.reset()
            return True, close_offset  # closed=True

        return False, 0.0

    def reset(self) -> None:
        """РЎР±СЂРѕСЃ РґРµС‚РµРєС‚РѕСЂР° РІ РЅР°С‡Р°Р»СЊРЅРѕРµ СЃРѕСЃС‚РѕСЏРЅРёРµ"""
        self.current_phase_id = self.config.initial_phase_id
        self.timer = 0.0
        self.active = False
        self.completion_timer = 0.0
        self.last_open_offset = None
        self.last_close_offset = None

    def update(self, step: Any, dt: float) -> Tuple[bool, bool]:
        """
        РћСЃРЅРѕРІРЅРѕР№ РјРµС‚РѕРґ РѕР±РЅРѕРІР»РµРЅРёСЏ.
        
        Returns:
            (opened, closed): С„Р»Р°РіРё РїРµСЂРµС…РѕРґРѕРІ СЃРѕСЃС‚РѕСЏРЅРёР№
        """
        opened = False
        closed = False
        self.last_open_offset = None
        self.last_close_offset = None

        if not self.active:
            opened, remaining = self._update_formation(step, dt)
            if opened:
                self.last_open_offset = float(dt) - float(remaining)
            # Если детектор открылся внутри большого dt, даём остаток интервала
            # на фазу завершения. Это делает поведение независимым от разбиения.
            if opened and self.active and remaining > 0.0:
                closed, close_off = self._update_completion(remaining, step)
                if closed:
                    open_off = self.last_open_offset
                    if open_off is None:
                        open_off = float(dt) - float(remaining)
                    self.last_close_offset = float(open_off) + float(close_off)
        else:
            closed, close_off = self._update_completion(dt, step)
            if closed:
                self.last_close_offset = float(close_off)

        return opened, closed

    def get_current_mask_id(self) -> Optional[int]:
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ ID РјР°СЃРєРё С‚РµРєСѓС‰РµР№ С„Р°Р·С‹ (РґР»СЏ РѕС‚Р»Р°РґРєРё)"""
        phase = self._get_phase(self.current_phase_id)
        return phase.mask_id if phase else None


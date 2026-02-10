from typing import Any, Tuple, List
from base_detector import BaseDetector

class BaseVariantWrapper:
    """Базовый класс для многоветочных детекторов (v2, v7, v8)."""
    
    def __init__(self, detectors: List[BaseDetector]) -> None:
        self.detectors = detectors
        self.active = False
    
    def reset(self) -> None:
        for det in self.detectors:
            det.reset()
        self.active = False
    
    def update(self, step: Any, dt: float) -> Tuple[bool, bool]:
        results = [det.update(step, dt) for det in self.detectors]
        
        was_active = self.active
        self.active = any(det.active for det in self.detectors)
        
        opened = (not was_active) and self.active
        closed = was_active and (any(r[1] for r in results) or not self.active)
        
        return opened, closed
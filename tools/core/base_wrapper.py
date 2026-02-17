from typing import Any, Tuple, List
from core.base_detector import BaseDetector

class BaseVariantWrapper:
    """Р‘Р°Р·РѕРІС‹Р№ РєР»Р°СЃСЃ РґР»СЏ РјРЅРѕРіРѕРІРµС‚РѕС‡РЅС‹С… РґРµС‚РµРєС‚РѕСЂРѕРІ (v2, v7, v8)."""
    
    def __init__(self, detectors: List[BaseDetector]) -> None:
        self.detectors = detectors
        self.active = False
        self.last_open_offset = None
        self.last_close_offset = None
    
    def reset(self) -> None:
        for det in self.detectors:
            det.reset()
        self.active = False
        self.last_open_offset = None
        self.last_close_offset = None
    
    def update(self, step: Any, dt: float) -> Tuple[bool, bool]:
        self.last_open_offset = None
        self.last_close_offset = None
        results = [det.update(step, dt) for det in self.detectors]
        
        was_active = self.active
        self.active = any(det.active for det in self.detectors)
        
        # Р˜РЎРџР РђР’Р›Р•РќРћ: opened/closed РґРѕР»Р¶РЅС‹ СѓС‡РёС‚С‹РІР°С‚СЊ СЂРµР·СѓР»СЊС‚Р°С‚С‹ РІРµС‚РѕРє, 
        # Р° РЅРµ С‚РѕР»СЊРєРѕ С„РёРЅР°Р»СЊРЅС‹Р№ СЃС‚РµР№С‚ self.active (РІР°Р¶РЅРѕ РґР»СЏ РґР»РёРЅРЅС‹С… dt)
        opened = any(r[0] for r in results)
        closed = any(r[1] for r in results)

        if opened:
            opened_offsets = [
                float(det.last_open_offset)
                for det, (op, _) in zip(self.detectors, results)
                if op and det.last_open_offset is not None
            ]
            if opened_offsets:
                self.last_open_offset = min(opened_offsets)

        if closed:
            closed_offsets = [
                float(det.last_close_offset)
                for det, (_, cl) in zip(self.detectors, results)
                if cl and det.last_close_offset is not None
            ]
            if closed_offsets:
                self.last_close_offset = min(closed_offsets)
        
        return opened, closed

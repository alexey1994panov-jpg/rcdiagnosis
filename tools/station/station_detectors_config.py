# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import Dict

from station.station_config import GROUPS, NODES


# ================================
#  Р“Р»РѕР±Р°Р»СЊРЅС‹Рµ С‚Р°Р№РјРёРЅРіРё (РєР°Рє РІ С‚РµСЃС‚Р°С…)
#  Р­С‚Рё Р·РЅР°С‡РµРЅРёСЏ РїРѕС‚РѕРј РјРѕР¶РЅРѕ РїСЂР°РІРёС‚СЊ СЃ С„СЂРѕРЅС‚Р°.
# ================================

@dataclass
class GlobalTimings:
    # РћР±С‰РёРµ РєРѕРЅСЃС‚Р°РЅС‚С‹
    t_pkp: float = 13.0        # РўРїРєРї
    t_pk: float = 30.0         # РўРїРє
    t_sv: float = 12.0         # РўСЃРІ
    t_min_otcep: float = 600.0  # РўРјРёРЅ.РѕС‚С†РµРї.

    # Р›Р— v1 (lz1)
    ts01_lz1: float = 3.0
    tlz_lz1: float = 3.0
    tkon_lz1: float = 3.0

    # Р›Р— v2 (lz2)
    ts01_lz2: float = 3.0
    ts02_lz2: float = 3.0
    tlz_lz2: float = 3.0
    tkon_lz2: float = 3.0

    # Р›Р— v3 (lz3)
    ts01_lz3: float = 3.0
    ts02_lz3: float = 3.0
    tlz_lz3: float = 3.0
    tkon_lz3: float = 3.0

    # Р›Р— v4 (lz4)
    ts01_lz4: float = 3.0
    ts02_lz4: float = 3.0
    tlz_lz4: float = 3.0
    tkon_lz4: float = 3.0

    # Р›Р— v5 (lz5)
    ts01_lz5: float = 1.0
    ts02_lz5: float = 1.0
    tlz_lz5: float = 1.0
    tkon_lz5: float = 3.0

    # Р›Р— v6 (lz6)
    ts01_lz6: float = 10.0
    ts02_lz6: float = 10.0
    tlz_lz6: float = 600.0
    tkon_lz6: float = 10.0

    # Р›Р— v7 (lz7)
    ts01_lz7: float = 3.0
    tlz_lz7: float = 3.0
    tkon_lz7: float = 3.0

    # Р›Р— v8 (lz8)
    ts01_lz8: float = 3.0
    ts02_lz8: float = 3.0
    tlz_lz8: float = 3.0
    tkon_lz8: float = 3.0

    # Р›Р— v9 (lz9)
    ts01_lz9: float = 3.0
    ts02_lz9: float = 3.0
    tlz_lz9: float = 3.0
    tkon_lz9: float = 3.0

    # Р›Р— v10 (lz10)
    ts01_lz10: float = 3.0
    ts02_lz10: float = 3.0
    ts03_lz10: float = 3.0
    tlz_lz10: float = 3.0
    tkon_lz10: float = 3.0

    # Р›Р— v11 (lz11)
    ts01_lz11: float = 3.0
    ts02_lz11: float = 3.0
    tlz_lz11: float = 3.0
    tkon_lz11: float = 3.0

    # Р›Р— v12 (lz12)
    ts01_lz12: float = 3.0
    ts02_lz12: float = 3.0
    tlz_lz12: float = 3.0
    tkon_lz12: float = 3.0

    # Р›Р— v13 (lz13)
    ts01_lz13: float = 10.0
    ts02_lz13: float = 10.0
    tlz_lz13: float = 10.0
    tkon_lz13: float = 10.0

    # Р›РЎ v1 (ls1)
    ts01_ls1: float = 3.0
    ts02_ls1: float = 3.0
    tls_ls1: float = 3.0
    tkon_ls1: float = 3.0

    # Р›РЎ v2 (ls2)
    ts01_ls2: float = 3.0
    ts02_ls2: float = 3.0
    tls01_ls2: float = 2.0
    tls02_ls2: float = 10.0
    tkon_ls2: float = 3.0

    # Р›РЎ v4 (ls4)
    ts01_ls4: float = 3.0
    ts02_ls4: float = 3.0
    tls01_ls4: float = 3.0
    tls02_ls4: float = 10.0
    tkon_ls4: float = 3.0

    # Р›РЎ v5 (ls5)
    ts01_ls5: float = 3.0
    ts02_ls5: float = 3.0
    tls_ls5: float = 3.0
    tkon_ls5: float = 3.0

    # Р›РЎ v6 (ls6)
    ts01_ls6: float = 3.0
    ts02_ls6: float = 3.0
    tls_ls6: float = 3.0
    tkon_ls6: float = 3.0

    # Р›РЎ v9 (ls9)
    ts01_ls9: float = 2.0
    ts02_ls9: float = 2.0
    tls01_ls9: float = 1.0
    tls02_ls9: float = 3.0
    tkon_ls9: float = 3.0

    # РџР°СѓР·С‹ (РґР»СЏ РІСЃРµС… РІР°СЂРёР°РЅС‚РѕРІ РѕРґРёРЅР°РєРѕРІС‹Рµ РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ)
    t_pause_default: float = 0.0

    # РСЃРєР»СЋС‡РµРЅРёСЏ Р›Р—
    enable_lz_exc_mu: bool = False
    enable_lz_exc_recent_ls: bool = False
    enable_lz_exc_dsp: bool = False
    t_mu: float = 15.0
    t_recent_ls: float = 30.0
    t_min_maneuver_v8: float = 600.0

    # РСЃРєР»СЋС‡РµРЅРёСЏ Р›РЎ
    enable_ls_exc_mu: bool = False
    enable_ls_exc_after_lz: bool = False
    enable_ls_exc_dsp: bool = False
    t_ls_mu: float = 15.0
    t_ls_after_lz: float = 30.0
    t_ls_dsp: float = 600.0

    # Р”РѕРїСѓСЃРє СЃРѕСЃС‚РѕСЏРЅРёР№ СЃ Р·Р°РјС‹РєР°РЅРёРµРј (РґР»СЏ v5)
    allow_route_lock_states_default: bool = False


# ================================
#  Per-RC РІРєР»СЋС‡РµРЅРёРµ РІР°СЂРёР°РЅС‚РѕРІ
# ================================

@dataclass
class RcVariantConfig:
    """
    Р”Р»СЏ РєРѕРЅРєСЂРµС‚РЅРѕР№ Р Р¦: РєР°РєРёРµ РІР°СЂРёР°РЅС‚С‹ Р›Р—/Р›РЎ СЂР°Р·СЂРµС€РµРЅС‹.
    РўР°Р№РјРёРЅРіРё Р±РµСЂСѓС‚СЃСЏ РёР· GlobalTimings.
    """

    # Р›Р—
    enable_lz1: bool = False
    enable_lz2: bool = False
    enable_lz3: bool = False
    enable_lz4: bool = False
    enable_lz5: bool = False
    enable_lz6: bool = False
    enable_lz7: bool = False
    enable_lz8: bool = False
    enable_lz9: bool = False
    enable_lz10: bool = False
    enable_lz11: bool = False
    enable_lz12: bool = False
    enable_lz13: bool = False

    # Р›РЎ
    enable_ls1: bool = False
    enable_ls2: bool = False
    enable_ls4: bool = False
    enable_ls5: bool = False
    enable_ls6: bool = False
    enable_ls9: bool = False


@dataclass
class DetectorsConfig:
    """
    РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ РґРµС‚РµРєС‚РѕСЂРѕРІ РїРѕ СЃС‚Р°РЅС†РёРё:
    - global_timings: РѕР±С‰РёРµ РІСЂРµРјРµРЅР° РґР»СЏ РІСЃРµС… Р Р¦
    - rc_configs: РІРєР»СЋС‡РµРЅРёРµ РІР°СЂРёР°РЅС‚РѕРІ РґР»СЏ РєР°Р¶РґРѕР№ Р Р¦
    """

    global_timings: GlobalTimings = field(default_factory=GlobalTimings)

    # РќР°СЃС‚СЂРѕР№РєРё РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ РІРєР»СЋС‡РµРЅРёСЏ РІР°СЂРёР°РЅС‚РѕРІ (РµСЃР»Рё Р Р¦ РЅРµС‚ РІ rc_configs)
    default_rc_config: RcVariantConfig = field(default_factory=RcVariantConfig)

    # РРЅРґРёРІРёРґСѓР°Р»СЊРЅС‹Рµ РЅР°СЃС‚СЂРѕР№РєРё {rc_id: RcVariantConfig}
    rc_configs: Dict[str, RcVariantConfig] = field(default_factory=dict)

    def get_rc_config(self, rc_id: str) -> RcVariantConfig:
        return self.rc_configs.get(rc_id, self.default_rc_config)


# Р“Р»РѕР±Р°Р»СЊРЅС‹Р№ РѕР±СЉРµРєС‚ РєРѕРЅС„РёРіСѓСЂР°С†РёРё РґРµС‚РµРєС‚РѕСЂРѕРІ
DETECTORS_CONFIG = DetectorsConfig()


# ============================================
#  РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РІРєР»СЋС‡РµРЅРёСЏ РІР°СЂРёР°РЅС‚РѕРІ РїРѕ Р Р¦
# ============================================

# Р‘Р°Р·РѕРІРѕРµ РІРєР»СЋС‡РµРЅРёРµ: lz1 + ls1 РґР»СЏ РІСЃРµС… Р Р¦
for rc_id in GROUPS["rc_ids"]:
    DETECTORS_CONFIG.rc_configs[rc_id] = RcVariantConfig(
        enable_lz1=True,
        enable_lz2=True,
    )

# РћС‚РєР»СЋС‡РµРЅРёРµ Р›Р— РЅР° РєСЂР°Р№РЅРёС… Р Р¦ (РЅРµС‚ prev РёР»Рё next)
for rc_id in GROUPS["rc_ids"]:
    node = NODES.get(rc_id, {})
    prev_links = node.get("prev_links") or []
    next_links = node.get("next_links") or []

    is_edge = not prev_links or not next_links

    if is_edge:
        cfg = DETECTORS_CONFIG.rc_configs.get(rc_id)
        if cfg is None:
            cfg = RcVariantConfig()
            DETECTORS_CONFIG.rc_configs[rc_id] = cfg

        cfg.enable_lz1 = False
        cfg.enable_lz2 = False
        cfg.enable_lz3 = False
        cfg.enable_lz4 = False
        cfg.enable_lz5 = False
        cfg.enable_lz6 = False
        cfg.enable_lz7 = False
        cfg.enable_lz8 = False
        cfg.enable_lz9 = False
        cfg.enable_lz10 = False
        cfg.enable_lz11 = False
        cfg.enable_lz12 = False
        cfg.enable_lz13 = False
        # РїСЂРё РЅРµРѕР±С…РѕРґРёРјРѕСЃС‚Рё РјРѕР¶РЅРѕ С‚Р°РєР¶Рµ РѕС‚РєР»СЋС‡РёС‚СЊ Р›РЎ РЅР° РєСЂР°Р№РЅРёС… Р Р¦
        # cfg.enable_ls1 = False
        # cfg.enable_ls2 = False
        # cfg.enable_ls4 = False
        # cfg.enable_ls5 = False
        # cfg.enable_ls6 = False
        # cfg.enable_ls9 = False


if __name__ == "__main__":
    # РџСЂРѕСЃС‚РµР№С€Р°СЏ РїСЂРѕРІРµСЂРєР°
    for rc_id in GROUPS["rc_ids"]:
        node = NODES.get(rc_id, {})
        name = node.get("name", "?")
        cfg = DETECTORS_CONFIG.get_rc_config(rc_id)
        print(
            f"RC {name} (ID={rc_id}): "
            f"lz1={cfg.enable_lz1}, lz2={cfg.enable_lz2}, ls1={cfg.enable_ls1}"
        )


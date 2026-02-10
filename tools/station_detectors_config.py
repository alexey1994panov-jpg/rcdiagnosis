# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import Dict

from station_config import GROUPS, NODES


# ================================
#  Глобальные тайминги (как в тестах)
#  Эти значения потом можно править с фронта.
# ================================

@dataclass
class GlobalTimings:
    # Общие константы
    t_pkp: float = 13.0        # Тпкп
    t_pk: float = 30.0         # Тпк
    t_sv: float = 12.0         # Тсв
    t_min_otcep: float = 600.0  # Тмин.отцеп.

    # ЛЗ v1 (lz1)
    ts01_lz1: float = 3.0
    tlz_lz1: float = 3.0
    tkon_lz1: float = 3.0

    # ЛЗ v2 (lz2)
    ts01_lz2: float = 3.0
    ts02_lz2: float = 3.0
    tlz_lz2: float = 3.0
    tkon_lz2: float = 3.0

    # ЛЗ v3 (lz3)
    ts01_lz3: float = 3.0
    ts02_lz3: float = 3.0
    tlz_lz3: float = 3.0
    tkon_lz3: float = 3.0

    # ЛЗ v4 (lz4)
    ts01_lz4: float = 3.0
    ts02_lz4: float = 3.0
    tlz_lz4: float = 3.0
    tkon_lz4: float = 3.0

    # ЛЗ v5 (lz5)
    ts01_lz5: float = 1.0
    ts02_lz5: float = 1.0
    tlz_lz5: float = 1.0
    tkon_lz5: float = 3.0

    # ЛЗ v6 (lz6)
    ts01_lz6: float = 10.0
    ts02_lz6: float = 10.0
    tlz_lz6: float = 600.0
    tkon_lz6: float = 10.0

    # ЛЗ v7 (lz7)
    ts01_lz7: float = 3.0
    tlz_lz7: float = 3.0
    tkon_lz7: float = 3.0

    # ЛЗ v8 (lz8)
    ts01_lz8: float = 3.0
    ts02_lz8: float = 3.0
    tlz_lz8: float = 3.0
    tkon_lz8: float = 3.0

    # ЛЗ v9 (lz9)
    ts01_lz9: float = 3.0
    ts02_lz9: float = 3.0
    tlz_lz9: float = 3.0
    tkon_lz9: float = 3.0

    # ЛЗ v10 (lz10)
    ts01_lz10: float = 3.0
    ts02_lz10: float = 3.0
    ts03_lz10: float = 3.0
    tlz_lz10: float = 3.0
    tkon_lz10: float = 3.0

    # ЛЗ v11 (lz11)
    ts01_lz11: float = 3.0
    ts02_lz11: float = 3.0
    tlz_lz11: float = 3.0
    tkon_lz11: float = 3.0

    # ЛЗ v12 (lz12)
    ts01_lz12: float = 3.0
    ts02_lz12: float = 3.0
    tlz_lz12: float = 3.0
    tkon_lz12: float = 3.0

    # ЛЗ v13 (lz13)
    ts01_lz13: float = 10.0
    ts02_lz13: float = 10.0
    tlz_lz13: float = 10.0
    tkon_lz13: float = 10.0

    # ЛС v1 (ls1)
    ts01_ls1: float = 3.0
    ts02_ls1: float = 3.0
    tls_ls1: float = 3.0
    tkon_ls1: float = 3.0

    # ЛС v2 (ls2)
    ts01_ls2: float = 3.0
    ts02_ls2: float = 3.0
    tls01_ls2: float = 2.0
    tls02_ls2: float = 10.0
    tkon_ls2: float = 3.0

    # ЛС v4 (ls4)
    ts01_ls4: float = 3.0
    ts02_ls4: float = 3.0
    tls01_ls4: float = 3.0
    tls02_ls4: float = 10.0
    tkon_ls4: float = 3.0

    # ЛС v5 (ls5)
    ts01_ls5: float = 3.0
    ts02_ls5: float = 3.0
    tls_ls5: float = 3.0
    tkon_ls5: float = 3.0

    # ЛС v6 (ls6)
    ts01_ls6: float = 3.0
    ts02_ls6: float = 3.0
    tls_ls6: float = 3.0
    tkon_ls6: float = 3.0

    # ЛС v9 (ls9)
    ts01_ls9: float = 2.0
    ts02_ls9: float = 2.0
    tls01_ls9: float = 1.0
    tls02_ls9: float = 3.0
    tkon_ls9: float = 3.0

    # Паузы (для всех вариантов одинаковые по умолчанию)
    t_pause_default: float = 0.0

    # Исключения ЛЗ
    t_mu: float = 15.0
    t_recent_ls: float = 30.0
    t_min_maneuver_v8: float = 600.0

    # Исключения ЛС
    t_ls_mu: float = 15.0
    t_ls_after_lz: float = 30.0
    t_ls_dsp: float = 600.0

    # Допуск состояний с замыканием (для v5)
    allow_route_lock_states_default: bool = False


# ================================
#  Per-RC включение вариантов
# ================================

@dataclass
class RcVariantConfig:
    """
    Для конкретной РЦ: какие варианты ЛЗ/ЛС разрешены.
    Тайминги берутся из GlobalTimings.
    """

    # ЛЗ
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

    # ЛС
    enable_ls1: bool = False
    enable_ls2: bool = False
    enable_ls4: bool = False
    enable_ls5: bool = False
    enable_ls6: bool = False
    enable_ls9: bool = False


@dataclass
class DetectorsConfig:
    """
    Конфигурация детекторов по станции:
    - global_timings: общие времена для всех РЦ
    - rc_configs: включение вариантов для каждой РЦ
    """

    global_timings: GlobalTimings = field(default_factory=GlobalTimings)

    # Настройки по умолчанию включения вариантов (если РЦ нет в rc_configs)
    default_rc_config: RcVariantConfig = field(default_factory=RcVariantConfig)

    # Индивидуальные настройки {rc_id: RcVariantConfig}
    rc_configs: Dict[str, RcVariantConfig] = field(default_factory=dict)

    def get_rc_config(self, rc_id: str) -> RcVariantConfig:
        return self.rc_configs.get(rc_id, self.default_rc_config)


# Глобальный объект конфигурации детекторов
DETECTORS_CONFIG = DetectorsConfig()


# ============================================
#  Инициализация включения вариантов по РЦ
# ============================================

# Базовое включение: lz1 + ls1 для всех РЦ
for rc_id in GROUPS["rc_ids"]:
    DETECTORS_CONFIG.rc_configs[rc_id] = RcVariantConfig(
        enable_lz1=True,
        enable_lz2=True,
    )

# Отключение ЛЗ на крайних РЦ (нет prev или next)
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
        # при необходимости можно также отключить ЛС на крайних РЦ
        # cfg.enable_ls1 = False
        # cfg.enable_ls2 = False
        # cfg.enable_ls4 = False
        # cfg.enable_ls5 = False
        # cfg.enable_ls6 = False
        # cfg.enable_ls9 = False


if __name__ == "__main__":
    # Простейшая проверка
    for rc_id in GROUPS["rc_ids"]:
        node = NODES.get(rc_id, {})
        name = node.get("name", "?")
        cfg = DETECTORS_CONFIG.get_rc_config(rc_id)
        print(
            f"RC {name} (ID={rc_id}): "
            f"lz1={cfg.enable_lz1}, lz2={cfg.enable_lz2}, ls1={cfg.enable_ls1}"
        )

from dataclasses import dataclass

# Общие константы
T_PKP: float = 13.0          # Тпкп
T_PK: float = 30.0           # Тпк
T_SV: float = 12.0           # Тсв
T_MIN_OTCEP: float = 600.0   # Тмин.отцеп.

# ЛЗ v1
T_S0101: float = 3.0
T_LZ01: float = 3.0
T_KON: float = 3.0

# ЛЗ v2
T_S0102_DEFAULT: float = 3.0
T_S0202_DEFAULT: float = 3.0
T_LZ02_DEFAULT: float = 3.0

# ЛЗ v3
T_S0103_DEFAULT: float = 3.0
T_S0203_DEFAULT: float = 3.0
T_LZ03_DEFAULT: float = 3.0

# ЛЗ v4
T_S0401_DEFAULT: float = 3.0   # Тс0401
T_LZ04_DEFAULT: float = 3.0    # Тлз04
T_KON_V4_DEFAULT: float = 3.0  # Ткон для v4


# ЛЗ v5 (с замыканием)
T_S05_DEFAULT: float = 1.0        # Тс05
T_LZ05_DEFAULT: float = 1.0       # Тлз05
T_KON_V5_DEFAULT: float = 3.0     # Ткон для v5

# ЛЗ v6 (одноРЦ без замыкания)
T_S06_DEFAULT: float = 10.0       # Тс06
T_LZ06_DEFAULT: float = 600.0     # Тлз06
T_KON_V6_DEFAULT: float = 10.0    # Ткон для v6

# ЛЗ v7 (бесстрелочная с учётом смежных)
T_S07_DEFAULT: float = 3.0        # Тс07
T_LZ07_DEFAULT: float = 3.0       # Тлз07
T_KON_V7_DEFAULT: float = 3.0     # Ткон для v7

# ЛЗ v8
T_S0108_DEFAULT: float = 3.0
T_S0208_DEFAULT: float = 3.0
T_LZ08_DEFAULT: float = 3.0

# ЛЗ v9
T_S0109_DEFAULT: float = 3.0      # Тс0109
T_S0209_DEFAULT: float = 3.0      # Тс0209 (резерв, по ТЗ не используется)
T_LZ09_DEFAULT: float = 3.0       # Тлз09 (окно между занятиями)
T_KON_V9_DEFAULT: float = 3.0     # Ткон для v9

# --- LZ v10 ---
TS0110_DEFAULT: float = 3.0
TS0210_DEFAULT: float = 3.0
TS0310_DEFAULT: float = 3.0
TLZ10_DEFAULT: float = 3.0
TKON_V10_DEFAULT: float = 3.0

# --- LZ v11 (по светофорам) ---
T_S11_DEFAULT: float = 3.0        # Тс11
T_LZ11_DEFAULT: float = 3.0       # Тлз11
T_KON_V11_DEFAULT: float = 3.0    # Ткон для v11

# --- LZ v12 (смежная не контролируется) ---
T_S0112_DEFAULT: float = 3.0      # Тс0112
T_S0212_DEFAULT: float = 3.0      # Тс0212
T_LZ12_DEFAULT: float = 3.0       # Тлз12
T_KON_V12_DEFAULT: float = 3.0    # Ткон для v12

# --- LZ v13 (пред/след замкнута) ---    # <--- НОВОЕ
T_S0113_DEFAULT: float = 10.0     # Тс0113 
T_S0213_DEFAULT: float = 10.0     # Тс0213 
T_LZ13_DEFAULT: float = 10.0      # Тлз13 
T_KON_V13_DEFAULT: float = 10.0   # Ткон для v13

# ЛС v1
T_C0101_LS_DEFAULT: float = 3.0
T_LS01_DEFAULT: float = 3.0
T_KON_LS_DEFAULT: float = 3.0

# ЛС v2
T_S0102_LS_DEFAULT: float = 3.0
T_S0202_LS_DEFAULT: float = 3.0
T_LS0102_DEFAULT: float = 2.0
T_LS0202_DEFAULT: float = 10.0
T_KON_LS2_DEFAULT: float = 3.0

# ЛС v4
T_S0104_LS_DEFAULT: float = 3.0
T_S0204_LS_DEFAULT: float = 3.0
T_LS0104_DEFAULT: float = 3.0
T_LS0204_DEFAULT: float = 10.0
T_KON_LS4_DEFAULT: float = 3.0

# ЛС v5
T_S0105_LS_DEFAULT: float = 3.0
T_LS05_DEFAULT: float = 3.0
T_KON_LS5_DEFAULT: float = 3.0

# ЛС v6
T_S0106_LS_DEFAULT: float = 3.0
T_LS06_DEFAULT: float = 3.0
T_KON_LS6_DEFAULT: float = 3.0

# ЛС v9 (упрощённая ЛС без смежных)
T_S0109_LS_DEFAULT: float = 2.0
T_S0209_LS_DEFAULT: float = 2.0
T_LS0109_DEFAULT: float = 1.0
T_LS0209_DEFAULT: float = 3.0
T_KON_LS9_DEFAULT: float = 3.0

T_PAUSE_DEFAULT: float = 0.0

# Исключения ЛЗ
T_MU: float = 15.0
T_RECENT_LS: float = 30.0
T_MIN_MANEUVER_V8: float = 600.0

# Исключения ЛС
T_LS_MU: float = 15.0         # окно по МУ для ЛС
T_LS_AFTER_LZ: float = 30.0   # окно после ЛЗ для ЛС
T_LS_DSP: float = 600.0       # манёвр по ДСП для ЛС


@dataclass
class VariantOptions:
    # ЛЗ v1
    t_s0101: float
    t_lz01: float
    t_kon_v1: float
    enable_v1: bool

    # ЛЗ v2
    t_s0102: float
    t_s0202: float
    t_lz02: float
    t_kon_v2: float
    enable_v2: bool

    # ЛЗ v3
    t_s0103: float
    t_s0203: float
    t_lz03: float
    t_kon_v3: float
    enable_v3: bool

    # ЛЗ v4                        # <--- НОВОЕ
    t_s0401: float                # Тс0401
    t_lz04: float                 # Тлз04
    t_kon_v4: float               # Ткон
    enable_v4: bool    

    # ЛЗ v5 (с замыканием)
    t_s05: float          # Тс05
    t_lz05: float         # Тлз05
    t_pk: float           # Тпк
    t_kon_v5: float       # Ткон
    enable_v5: bool

    # ЛЗ v6 
    t_s06: float
    t_lz06: float
    t_kon_v6: float
    enable_v6: bool

    # ЛЗ v7 (бесстрелочная с учётом смежных)
    t_s07: float          # Тс07
    t_lz07: float         # Тлз07
    t_kon_v7: float       # Ткон
    enable_v7: bool

    # ЛЗ v8
    t_s0108: float
    t_s0208: float
    t_lz08: float
    t_kon_v8: float
    enable_v8: bool

    # ЛЗ v9
    t_s0109: float        # Тс0109
    t_lz09: float         # Тлз09
    t_kon_v9: float       # Ткон
    enable_v9: bool

    # v10
    t_s0110: float
    t_s0210: float
    t_s0310: float
    t_lz10: float
    t_kon_v10: float
    enable_v10: bool

    # v11 (по светофорам)
    t_s11: float          # Тс11
    t_lz11: float         # Тлз11
    t_kon_v11: float      # Ткон
    enable_v11: bool

    # v12 (смежная не контролируется)
    t_s0112: float        # Тс0112
    t_s0212: float        # Тс0212
    t_lz12: float         # Тлз12
    t_kon_v12: float      # Ткон
    enable_v12: bool

    # v13 (пред/след замкнута)          # <--- НОВОЕ
    t_s0113: float        # Тс0113
    t_s0213: float        # Тс0213
    t_lz13: float         # Тлз13
    t_kon_v13: float      # Ткон
    enable_v13: bool
    

    # ЛС v1
    t_c0101_ls: float
    t_ls01: float
    t_kon_ls1: float
    enable_ls1: bool

    # ЛС v2
    t_s0102_ls: float
    t_s0202_ls: float
    t_ls0102: float
    t_ls0202: float
    t_kon_ls2: float
    enable_ls2: bool

    # ЛС v4
    t_s0104_ls: float
    t_s0204_ls: float
    t_ls0104: float
    t_ls0204: float
    t_kon_ls4: float
    enable_ls4: bool

    # ЛС v5
    t_s0105_ls: float
    t_ls05: float
    t_kon_ls5: float
    enable_ls5: bool

    # ЛС v6
    t_s0106_ls: float
    t_ls06: float
    t_kon_ls6: float
    enable_ls6: bool

    # ЛС v9
    t_s0109_ls: float
    t_s0209_ls: float
    t_ls0109: float
    t_ls0209: float
    t_kon_ls9: float
    enable_ls9: bool

    # Паузы
    t_pause_v1: float
    t_pause_v2: float
    t_pause_v3: float
    t_pause_v4: float
    t_pause_v5: float
    t_pause_v6: float
    t_pause_v7: float
    t_pause_v8: float
    t_pause_v9: float      # пауза для v9
    t_pause_v10: float
    t_pause_v11: float
    t_pause_v12: float
    t_pause_v13: float 
    t_pause_ls1: float
    t_pause_ls2: float
    t_pause_ls4: float
    t_pause_ls5: float
    t_pause_ls6: float
    t_pause_ls9: float
    

    # Исключения ЛЗ
    t_mu: float
    t_recent_ls: float
    t_min_maneuver_v8: float

    # Включение/выключение исключений ЛЗ
    enable_lz_exc_mu: bool
    enable_lz_exc_recent_ls: bool
    enable_lz_exc_dsp: bool

    # Включение/выключение исключений ЛС
    enable_ls_exc_mu: bool
    enable_ls_exc_after_lz: bool
    enable_ls_exc_dsp: bool

    # Тайминги исключений ЛС
    t_ls_mu: float
    t_ls_after_lz: float
    t_ls_dsp: float

    # Флаг допуска состояний с замыканием в вариантах с замыканием (v5)
    allow_route_lock_states: bool

    # v13_ctrl_rc_id: str = "10-12SP"

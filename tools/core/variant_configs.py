# variant_configs.py
from core.base_detector import PhaseConfig, DetectorConfig, CompletionMode

# СѓР¶Рµ РµСЃС‚СЊ
MASK_000 = 1
MASK_010 = 2

# РґРѕР±Р°РІРёРј РјР°СЃРєРё РґР»СЏ v2
MASK_V2_PREV_P1 = 10
MASK_V2_PREV_P2 = 11
MASK_V2_PREV_P3 = 12
MASK_V2_NEXT_P1 = 20
MASK_V2_NEXT_P2 = 21
MASK_V2_NEXT_P3 = 22

# РјР°СЃРєРё РґР»СЏ v7
MASK_V7_GIVEN_NO_ADJACENT = 70
MASK_V7_GIVEN_NO_PREV = 71
MASK_V7_GIVEN_NO_NEXT = 72
MASK_V7_WHEN_NO_ADJACENT = 73
MASK_V7_WHEN_NO_PREV = 74
MASK_V7_WHEN_NO_NEXT = 75


def make_lz1_config(ts01_lz1: float, tlz_lz1: float, tkon_lz1: float) -> DetectorConfig:
    return DetectorConfig(
        variant_id=1,
        initial_phase_id=0,
        phases=[
            PhaseConfig(
                phase_id=0,
                name="idle",
                mask_id=MASK_000,
                duration=float(ts01_lz1),
                next_phase_id=1,
                timer_mode="continuous",
                reset_on_exit=True,
            ),
            PhaseConfig(
                phase_id=1,
                name="s0101_done",
                mask_id=MASK_010,
                duration=float(tlz_lz1),
                next_phase_id=-1,
                timer_mode="continuous",
                reset_on_exit=True,
            ),
        ],
        t_kon=float(tkon_lz1),
        completion_mode=CompletionMode.FREE_TIME,
        requires_adjacent=True,
        parallel_branches={},
    )


def make_lz2_config(ts01_lz2: float, ts02_lz2: float, tlz_lz2: float, tkon_lz2: float) -> DetectorConfig:
    """
    Р’Р°СЂРёР°РЅС‚ 2 вЂ” РґРІРµ РїР°СЂР°Р»Р»РµР»СЊРЅС‹Рµ РІРµС‚РєРё:
      РІРµС‚РєР° prev: p1(10) -> p2(11) -> p3(12)
      РІРµС‚РєР° next: p1(20) -> p2(21) -> p3(22)
    Р¤РёРЅР°Р»СЊРЅР°СЏ С„Р°Р·Р° p3 -> РѕС‚РєСЂС‹С‚РёРµ Р”РЎ, Р·Р°РІРµСЂС€РµРЅРёРµ РїРѕ FREE_TIME Рё tkon_lz2.
    """
    # РѕСЃРЅРѕРІРЅР°СЏ РІРµС‚РєР° РґР»СЏ v2 РЅРµ РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ, РІСЃС‘ РІ РїР°СЂР°Р»Р»РµР»СЊРЅС‹С…
    phases_main: list[PhaseConfig] = [
        PhaseConfig(
            phase_id=0,
            name="idle",
            mask_id=MASK_000,
            duration=0.0,
            next_phase_id=0,
            timer_mode="continuous",
            reset_on_exit=False,
        )
    ]

    # РІРµС‚РєР° "РїСЂРµРґС‹РґСѓС‰Р°СЏ Р·Р°РЅСЏС‚Р°"
    prev_branch = [
        PhaseConfig(
            phase_id=0,
            name="prev_p1",
            mask_id=MASK_V2_PREV_P1,
            duration=float(ts01_lz2),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=1,
            name="prev_p2",
            mask_id=MASK_V2_PREV_P2,
            duration=float(tlz_lz2),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=2,
            name="prev_p3",
            mask_id=MASK_V2_PREV_P3,
            duration=float(ts02_lz2),
            next_phase_id=-1,  # С„РёРЅР°Р» -> open
            timer_mode="continuous",
            reset_on_exit=True,
        ),
    ]

    # РІРµС‚РєР° "СЃР»РµРґСѓСЋС‰Р°СЏ Р·Р°РЅСЏС‚Р°"
    next_branch = [
        PhaseConfig(
            phase_id=0,
            name="next_p1",
            mask_id=MASK_V2_NEXT_P1,
            duration=float(ts01_lz2),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=1,
            name="next_p2",
            mask_id=MASK_V2_NEXT_P2,
            duration=float(tlz_lz2),
            next_phase_id=2,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=2,
            name="next_p3",
            mask_id=MASK_V2_NEXT_P3,
            duration=float(ts02_lz2),
            next_phase_id=-1,  # С„РёРЅР°Р» -> open
            timer_mode="continuous",
            reset_on_exit=True,
        ),
    ]

    return DetectorConfig(
        variant_id=2,
        initial_phase_id=0,
        phases=phases_main,
        t_kon=float(tkon_lz2),
        completion_mode=CompletionMode.FREE_TIME,
        requires_adjacent=False,  # РґР»СЏ v2 Р»РѕРіРёРєР° РґРѕСЃС‚РѕРІРµСЂРЅРѕСЃС‚Рё СЃРІРѕСЏ
        parallel_branches={
            1: prev_branch,
            2: next_branch,
        },
    )


def make_lz7_config(ts01_lz7: float, tlz_lz7: float, tkon_lz7: float) -> DetectorConfig:
    """
    Р’Р°СЂРёР°РЅС‚ 7 вЂ” С‚СЂРё РїР°СЂР°Р»Р»РµР»СЊРЅС‹Рµ РІРµС‚РєРё:
      - РІРµС‚РєР° no_adjacent: РЅРµС‚ СЃРјРµР¶РЅС‹С… Р Р¦ (v6)
      - РІРµС‚РєР° no_prev: РЅРµС‚ РїСЂРµРґС‹РґСѓС‰РµР№ РїРѕ РїРѕР»РѕР¶РµРЅРёСЋ СЃС‚СЂРµР»РєРё (v7.1)
      - РІРµС‚РєР° no_next: РЅРµС‚ СЃР»РµРґСѓСЋС‰РµР№ РїРѕ РїРѕР»РѕР¶РµРЅРёСЋ СЃС‚СЂРµР»РєРё (v7.2)
    
    РљР°Р¶РґР°СЏ РІРµС‚РєР° РёРјРµРµС‚ 2 С„Р°Р·С‹:
      - phase 0 (given): Р”РђРќРћ вЂ” СѓСЃР»РѕРІРёСЏ СЃРІРѕР±РѕРґРЅРѕСЃС‚Рё в‰Ґ ts01_lz7
      - phase 1 (when): РљРћР“Р”Рђ вЂ” СѓСЃР»РѕРІРёСЏ Р·Р°РЅСЏС‚РѕСЃС‚Рё в‰Ґ tlz_lz7
    
    Р—Р°РІРµСЂС€РµРЅРёРµ РїРѕ FREE_TIME СЃ t_kon = tkon_lz7.
    """
    # РћСЃРЅРѕРІРЅР°СЏ РІРµС‚РєР° РЅРµ РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ, РІСЃС‘ РІ РїР°СЂР°Р»Р»РµР»СЊРЅС‹С…
    phases_main: list[PhaseConfig] = [
        PhaseConfig(
            phase_id=0,
            name="idle",
            mask_id=MASK_000,
            duration=0.0,
            next_phase_id=0,
            timer_mode="continuous",
            reset_on_exit=False,
        )
    ]

    # Р’РµС‚РєР° "РЅРµС‚ СЃРјРµР¶РЅС‹С… Р Р¦" (v6)
    no_adjacent_branch = [
        PhaseConfig(
            phase_id=0,
            name="no_adjacent_given",
            mask_id=MASK_V7_GIVEN_NO_ADJACENT,
            duration=float(ts01_lz7),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=1,
            name="no_adjacent_when",
            mask_id=MASK_V7_WHEN_NO_ADJACENT,
            duration=float(tlz_lz7),
            next_phase_id=-1,  # С„РёРЅР°Р» -> open
            timer_mode="continuous",
            reset_on_exit=True,
        ),
    ]

    # Р’РµС‚РєР° v7.1: РЅРµС‚ РїСЂРµРґС‹РґСѓС‰РµР№ РїРѕ РїРѕР»РѕР¶РµРЅРёСЋ СЃС‚СЂРµР»РєРё
    no_prev_branch = [
        PhaseConfig(
            phase_id=0,
            name="no_prev_given",
            mask_id=MASK_V7_GIVEN_NO_PREV,
            duration=float(ts01_lz7),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=1,
            name="no_prev_when",
            mask_id=MASK_V7_WHEN_NO_PREV,
            duration=float(tlz_lz7),
            next_phase_id=-1,  # С„РёРЅР°Р» -> open
            timer_mode="continuous",
            reset_on_exit=True,
        ),
    ]

    # Р’РµС‚РєР° v7.2: РЅРµС‚ СЃР»РµРґСѓСЋС‰РµР№ РїРѕ РїРѕР»РѕР¶РµРЅРёСЋ СЃС‚СЂРµР»РєРё
    no_next_branch = [
        PhaseConfig(
            phase_id=0,
            name="no_next_given",
            mask_id=MASK_V7_GIVEN_NO_NEXT,
            duration=float(ts01_lz7),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
        ),
        PhaseConfig(
            phase_id=1,
            name="no_next_when",
            mask_id=MASK_V7_WHEN_NO_NEXT,
            duration=float(tlz_lz7),
            next_phase_id=-1,  # С„РёРЅР°Р» -> open
            timer_mode="continuous",
            reset_on_exit=True,
        ),
    ]

    return DetectorConfig(
        variant_id=7,
        initial_phase_id=0,
        phases=phases_main,
        t_kon=float(tkon_lz7),
        completion_mode=CompletionMode.FREE_TIME,
        requires_adjacent=False,  # РґР»СЏ v7 Р»РѕРіРёРєР° РґРѕСЃС‚РѕРІРµСЂРЅРѕСЃС‚Рё СЃРІРѕСЏ (С‡РµСЂРµР· С„Р»Р°РіРё)
        parallel_branches={
            1: no_adjacent_branch,
            2: no_prev_branch,
            3: no_next_branch,
        },
    )


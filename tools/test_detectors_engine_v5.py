# -*- coding: utf-8 -*-
from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig


def test_v5_59_full_cycle():
    """
    Полный цикл v5 на 59 (1-7СП, can_lock=True).
    ts05_lz5=1.0, tlz_lz5=1.0, tkon_lz5=1.0.
    Ожидаем: есть open, активная ЛЗ v5, есть closed.
    Соседи не требуются — NeighborRequirement.NONE.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="59",           # 1-7СП (ID), can_lock=True
        prev_rc_name=None,         # соседи не нужны
        ctrl_rc_name="59",
        next_rc_name=None,
        # Отключаем все остальные варианты
        ts01_lz1=0.0,
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=0.0,
        ts02_lz2=0.0,
        tlz_lz2=0.0,
        tkon_lz2=0.0,
        enable_lz2=False,
        ts01_lz3=0.0,
        ts02_lz3=0.0,
        tlz_lz3=0.0,
        tkon_lz3=0.0,
        enable_lz3=False,
        ts01_lz7=0.0,
        tlz_lz7=0.0,
        tkon_lz7=0.0,
        enable_lz7=False,
        ts01_lz8=0.0,
        ts02_lz8=0.0,
        tlz_lz8=0.0,
        tkon_lz8=0.0,
        enable_lz8=False,
        # Включаем v5
        ts01_lz5=1.0,
        tlz_lz5=1.0,
        tkon_lz5=1.0,
        enable_lz5=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0–2 с: ДАНО — ctrl free без lock (3) ≥ ts05=1.0
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3},  # только ctrl, соседи не важны
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2–4 с: КОГДА — ctrl occupied без lock (6) ≥ tlz=1.0 → open
        ScenarioStep(
            t=2.0,
            rc_states={"59": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 4–6 с: Завершение — ctrl free (3) ≥ tkon=1.0 → closed
        ScenarioStep(
            t=2.0,
            rc_states={"59": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="59",
    )

    timeline = ctx.run()

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    assert any("llz_v5_open" in s.flags for s in timeline), "Нет llz_v5_open"
    assert any("llz_v5" in s.flags and s.lz_variant == 5 for s in timeline), "llz_v5 без variant=5"
    assert any("llz_v5_closed" in s.flags for s in timeline), "Нет llz_v5_closed"

def test_v5_65_should_not_trigger():
    """
    Проверка что v5 НЕ срабатывает на РЦ 65 (4П), где can_lock=False.
    v5 требует can_lock=True (замыкание возможно).
    Ожидаем: нет open, variant=0, флаги не содержат llz_v5.
    """
    det_cfg = DetectorsConfig(
        ctrl_rc_id="65",           # 4П (ID), can_lock=False
        prev_rc_name=None,
        ctrl_rc_name="65",
        next_rc_name=None,
        # Отключаем все остальные варианты
        ts01_lz1=0.0,
        tlz_lz1=0.0,
        tkon_lz1=0.0,
        enable_lz1=False,
        ts01_lz2=0.0,
        ts02_lz2=0.0,
        tlz_lz2=0.0,
        tkon_lz2=0.0,
        enable_lz2=False,
        ts01_lz3=0.0,
        ts02_lz3=0.0,
        tlz_lz3=0.0,
        tkon_lz3=0.0,
        enable_lz3=False,
        ts01_lz7=0.0,
        tlz_lz7=0.0,
        tkon_lz7=0.0,
        enable_lz7=False,
        ts01_lz8=0.0,
        ts02_lz8=0.0,
        tlz_lz8=0.0,
        tkon_lz8=0.0,
        enable_lz8=False,
        # Включаем v5
        ts01_lz5=1.0,
        tlz_lz5=1.0,
        tkon_lz5=1.0,
        enable_lz5=True,
    )

    sim_cfg = SimulationConfig(
        t_pk=30.0,
        detectors_config=det_cfg,
    )

    scenario = [
        # 0–2 с: ДАНО — ctrl free (3)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 2–4 с: КОГДА — ctrl occupied (6)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 6},
            switch_states={},
            signal_states={},
            modes={},
        ),
        # 4–6 с: Завершение — ctrl free (3)
        ScenarioStep(
            t=2.0,
            rc_states={"65": 3},
            switch_states={},
            signal_states={},
            modes={},
        ),
    ]

    ctx = SimulationContext(
        config=sim_cfg,
        scenario=scenario,
        ctrl_rc_id="65",
    )

    timeline = ctx.run()

    for i, st in enumerate(timeline, start=1):
        print(
            f"{i}: t={st.t}, rc={st.rc_states}, "
            f"variant={st.lz_variant}, lz={st.lz_state}, flags={st.flags}"
        )

    # Проверяем что v5 НЕ сработал
    assert not any("llz_v5_open" in s.flags for s in timeline), "v5 сработал, но не должен (can_lock=False)"
    assert not any(s.lz_variant == 5 for s in timeline), "variant=5, но не должен быть"
    assert not any("llz_v5" in s.flags for s in timeline), "Есть флаг llz_v5, но не должен быть"
    print("✅ v5 корректно НЕ сработал на РЦ без замыкания")
import pytest
from engine.station_visochino_1p import get_station_model_1p
from engine.simulate_1p import simulate_1p
from engine.types_1p import ScenarioStep


@pytest.fixture(scope="session")
def station():
    return get_station_model_1p()


def make_step(t, rc_1012, rc_1p, rc_17):
    return ScenarioStep(
        t=float(t),
        rc_states={"10-12SP": rc_1012, "1P": rc_1p, "1-7SP": rc_17},
        switch_states={"Sw10": 3, "Sw1": 3, "Sw5": 3},
        modes={},
        mu={"10-12SP": 3, "1P": 3, "1-7SP": 3},
        dispatcher_control_state=4,
        auto_actions={"NAS": 4, "CHAS": 4},
    )


def test_ls_variant5_from_json(station):
    """Тест ЛС v5: полный цикл по предоставленным шагам (случай 5.2: следующая занята)."""
    
    # Опции только для ЛС v5, все остальные отключены
    opts = {
        # ЛС v5 включена с параметрами по ТЗ
        "enable_ls5": True,
        "t_s0105_ls": 3.0,      # Тс0105=6с (2 шага × 3с)
        "t_ls05": 3.0,          # Тлс05=3с (1 шаг)
       
        "t_kon_ls5": 3.0,       # Ткон=9с (3 шага)
        
        # Все остальные ЛС выключены
        "enable_ls1": False,
        "enable_ls2": False,
        "enable_ls4": False,
        "enable_ls9": False,
        
        # Все ЛЗ выключены
        "enable_v1": False, "enable_v2": False, "enable_v3": False,
        "enable_v4": False, "enable_v5": False, "enable_v6": False,
        "enable_v7": False, "enable_v8": False, "enable_v9": False,
        "enable_v10": False, "enable_v11": False, "enable_v12": False, "enable_v13": False,
        
        # Исключения отключены
        "enable_lz_exc_mu": False,
        "enable_lz_exc_recent_ls": False,
        "enable_lz_exc_dsp": False,
        "enable_ls_exc_mu": False,
        "enable_ls_exc_after_lz": False,
        "enable_ls_exc_dsp": False,
        
        # Паузы нулевые
        "t_pause_ls5": 0.0,
    }

    # Предоставленные шаги (случай 5.2: следующая занята)
    steps = [
        # Шаг 1: GIVEN 5.2 (prev=1,curr=0,next=0? → но по шагам это 1-0-1 уже!)
        make_step(3, rc_1012=7, rc_1p=4, rc_17=4),  # 1-0-0? по состояниям нужно проверить
        
        # Шаг 2: WHEN начало (1-0-1)
        make_step(3, rc_1012=7, rc_1p=4, rc_17=7),
        
        # Шаги 3+: завершение по занятию 1P
        make_step(3, rc_1012=7, rc_1p=7, rc_17=7),
    ]

    timeline = simulate_1p(station, steps, dt=3.0, options=opts)

    # Проверки: должна открыться и закрыться ЛС v5
    assert len(timeline) == 3, f"Ожидалось 3 шага, получено {len(timeline)}"
    
    # Флаги по шагам
    has_open = any("lls_v5_open" in s.flags for s in timeline)
    has_active = any("lls_v5" in s.flags for s in timeline)
    has_closed = any("lls_v5_closed" in s.flags for s in timeline)
    
    assert has_open, "НЕТ lls_v5_open!"
    assert has_active, "НЕТ активного lls_v5!"
    assert has_closed, "НЕТ lls_v5_closed!"
    
    # НЕ должно быть других ЛС/ЛЗ
    forbidden_flags = {"lls_v1", "lls_v2", "lls_v4", "lls_v9"} | {f"llz_v{i}" for i in range(1, 14)}
    for step in timeline:
        for flag in step.flags:
            if any(f in flag for f in forbidden_flags):
                pytest.fail(f"Недопустимый флаг '{flag}' в {step.t=}")
    
    print("✅ ЛС v5: open ✓ active ✓ closed ✓ — другие ЛС/ЛЗ отсутствуют!")

 Внесу корректировки в README для варианта 6 и добавлю разделы про времена Т и состояния.

```markdown
# Детекторы Ложной Занятости (ЛЗ) — Архитектура Проекта

## Общее назначение

Система детекторов ложной занятости (ЛЗ) для железнодорожной станции. Каждый детектор анализирует состояние рельсовых цепей (РЦ) и определяет, является ли занятость секции "ложной" (технологическая ошибка) или реальной.

**Ключевые понятия:**
- **РЦ** — рельсовая цепь (секция пути)
- **ЛЗ** — ложная занятость (детектируемое состояние)
- **Вариант** — алгоритм детекции (v1, v2, v3, v5, v6, v7, v8...)
- **Маска** — битовое/логическое условие состояний соседних РЦ (000, 010, 101 и т.д.)
- **Фаза** — этап формирования ЛЗ с таймером
- **Топология** — динамическое определение соседей через стрелки

---

## Структура проекта
```
├── base_detector.py          # Базовый класс детектора (конечный автомат)
├── base_wrapper.py           # Обертка для многоветочных детекторов
├── variants_common.py        # Маски состояний РЦ (все варианты)
├── variant1_lz_factory.py    # Фабрика варианта 1 (классическая ЛЗ)
├── variant2_lz_factory.py    # Фабрика варианта 2 (один сосед занят)
├── variant3_lz_factory.py    # Фабрика варианта 3 (шунтовое движение)
├── variant5_lz_factory.py    # Фабрика варианта 5 (без соседей, по замыканию)
├── variant6_lz_factory.py    # Фабрика варианта 6 (длительная занятость, без соседей)
├── variant7_lz_factory.py    # Фабрика варианта 7 (бесстрелочные секции)
├── variant8_lz_factory.py    # Фабрика варианта 8 (сложные условия)
├── variant_configs.py        # Конфигурации фаз для всех вариантов
├── detectors_engine.py       # Движок: инициализация и обновление детекторов
├── flags_engine.py           # Сборка флагов результатов
├── sim_core.py               # Ядро симуляции
├── topology_manager.py       # Динамическая топология соседей
├── station_model.py          # Модель станции
└── uni_states.py             # Утилиты для интерпретации состояний
```

---

## Базовая архитектура

### 1. BaseDetector (`base_detector.py`)

**Назначение:** Универсальный конечный автомат для одного варианта ЛЗ.

**Ключевые классы:**

```python
@dataclass
class PhaseConfig:
    phase_id: int           # ID фазы (0, 1, 2...)
    duration: float         # Требуемая длительность фазы
    next_phase_id: int      # Следующая фаза (-1 = финал → открытие ДС)
    timer_mode: str         # "continuous" (сброс при нарушении) или "cumulative"
    reset_on_exit: bool     # Сброс таймера при выходе из фазы
    mask_id: int            # ID маски для отладки
    mask_fn: callable       # Функция проверки условия фазы
    requires_neighbors: NeighborRequirement  # Требования к соседям

@dataclass
class DetectorConfig:
    initial_phase_id: int
    phases: List[PhaseConfig]
    t_kon: float                    # Время на завершение после открытия
    completion_mode: CompletionMode # FREE_TIME или OCCUPIED_TIME
    variant_name: str

class BaseDetector:
    def __init__(self, config: DetectorConfig, 
                 prev_rc_name, ctrl_rc_name, next_rc_name)
    def update(step, dt) -> (opened, closed)  # Основной метод
```

**Режимы работы:**
- **Формирование (до открытия):** проверка масок → накопление времени → переход фаз
- **Завершение (после открытия):** отсчет t_kon → закрытие при условии свободности

**Требования к соседям (NeighborRequirement):**
- `BOTH` — оба соседа должны быть достоверны (v1, v2, v3, v8)
- `NONE` — соседи не важны (v7)
- `ONLY_CTRL` — только контролируемая РЦ (v5, v6)

---

### 2. Маски состояний (`variants_common.py`)

**Обозначения в масках:**
- `0` — РЦ свободна
- `1` — РЦ занята
- `X` или `x` — любое состояние (игнорируется, не важно)
- `|` — логическое ИЛИ для альтернативных состояний

**ТАБЛИЦА МАСОК:**

| Маска | Код | Условие | Требует соседей |
|-------|-----|---------|-----------------|
| `mask_000` | 0 | Все свободны | **ДА** — оба соседа должны существовать и быть свободны |
| `mask_010` | 1 | Центр занят, края свободны | **ДА** — оба соседа должны существовать и быть свободны |
| `mask_101` | 2 | Края заняты, центр свободен | **ДА** — оба соседа должны существовать |
| `mask_111` | 3 | Все заняты | **ДА** — оба соседа должны существовать |
| `mask_100` | 4 | Prev занят, ctrl и next свободны | **ДА** — prev должен существовать |
| `mask_110` | 5 | Prev и ctrl заняты, next свободен | **ДА** — prev должен существовать |
| `mask_001` | 6 | Next занят, prev и ctrl свободны | **ДА** — next должен существовать |
| `mask_011` | 7 | Ctrl и next заняты, prev свободен | **ДА** — next должен существовать |
| `mask_100_or_000` | 104 | 100 ИЛИ 000 | Как у 100 |
| `mask_001_or_000` | 106 | 001 ИЛИ 000 | Как у 001 |

**Маски для v7 (бесстрелочные, X = игнорируется):**

| Маска | Код | Условие | Когда используется |
|-------|-----|---------|-------------------|
| `mask_x0x` | 200 | Центр свободен (соседи **любые/не важны**) | no_adjacent (нет соседей вообще) |
| `mask_x0x_occ` | 201 | Центр занят (соседи **любые/не важны**) | no_adjacent, фаза 2 |
| `mask_00x` | 202 | prev и ctrl свободны, next **не важен** | no_prev (нет предыдущей) |
| `mask_00x_occ` | 203 | prev свободен, ctrl занят, next **не важен** | no_prev, фаза 2 |
| `mask_x00` | 204 | ctrl и next свободны, prev **не важен** | no_next (нет следующей) |
| `mask_x00_occ` | 205 | next свободен, ctrl занят, prev **не важен** | no_next, фаза 2 |

> **Важно:** X означает "любое состояние" — сосед может быть занят, свободен, отсутствовать или быть недостоверным. Это НЕ то же самое, что отсутствие соседа!

**Маски для v8 (составные):**

| Маска | Код | Условие |
|-------|-----|---------|
| `mask_110_or_111` | 208 | (prev занят И ctrl занят) И (next любой) |
| `mask_011_or_111` | 209 | (ctrl занят И next занят) И (prev любой) |
| `mask_01x_or_x10` | 210 | ctrl занят И (prev свободен ИЛИ next свободен) |

**Маски для v5 (замыкание):**

| Маска | Код | Условие |
|-------|-----|---------|
| `mask_0_not_locked` | 500 | ctrl свободна И НЕ замкнута И can_lock=True |
| `mask_1_not_locked` | 501 | ctrl занята И НЕ замкнута И can_lock=True |

**Маски для v6 (длительная занятость, без соседей):**

| Маска | Код | Условие | Примечание |
|-------|-----|---------|------------|
| `mask_ctrl_free` | 600 | ctrl свободна | Не проверяет соседей, только состояние ctrl |
| `mask_ctrl_occupied` | 601 | ctrl занята | Не проверяет соседей, только состояние ctrl |

> **Особенность v6:** Работает на **любой** РЦ, независимо от `can_lock`. Не требует соседей (`NeighborRequirement.ONLY_CTRL`).

---

### 3. Фабрики вариантов

**Общая структура каждой фабрики**

Каждая фабрика (`variant{N}_lz_factory.py`) содержит:
- Константы масок — числовые ID для отладки
- `make_lz{N}_detector()` — основная фабричная функция
- Вспомогательные `_make_*_detector()` — для многоветочных вариантов
- `V{N}_SCHEMA` — JSON-схема для документации/валидации

**Возвращаемые типы:**
- **Одноветочные** (v1, v3, v5, v6): возвращают `BaseDetector`
- **Многоветочные** (v2, v7, v8): возвращают `BaseVariantWrapper([det1, det2, ...])`

**Сравнение фабрик:**

| Вариант | Тип | Ветки | Требует соседей | Особенности |
|---------|-----|-------|-----------------|-------------|
| **v1** | Одноветочный | 1 | `BOTH` | Классика: 000→010 |
| **v2** | Многоветочный | 2 (prev/next) | `BOTH` | Один сосед занят: 100→110→(100\|000) ИЛИ 001→011→(001\|000) |
| **v3** | Одноветочный | 1 | `BOTH` | Шунтовое: 101→111→101 |
| **v5** | Одноветочный | 1 | `ONLY_CTRL` | Без соседей, по замыканию: свободна→занята. Требует `can_lock=True` |
| **v6** | Одноветочный | 1 | `ONLY_CTRL` | Без соседей, длительная занятость: свободна→занята. **Не требует `can_lock`** |
| **v7** | Многоветочный | 3 (no_adj/no_prev/no_next) | `NONE` | Бесстрелочные: X0X→X0X_OCC и т.д. |
| **v8** | Многоветочный | 3 (prev/next/mid) | `BOTH` | Сложные условия: 110\|111→011\|111→010 |

**Подробное описание каждой фабрики**

**variant1_lz_factory.py**
```python
def make_lz1_detector(prev_rc_name, ctrl_rc_name, next_rc_name,
                      ts01_lz1, tlz_lz1, tkon_lz1) -> BaseDetector
```
- Фазы: 0 (idle, mask_000, ts01) → 1 (active, mask_010, tlz) → открытие
- Логика: Все свободны → Центр занят при свободных краях
- Схема: Простая цепочка из 2 фаз

**variant2_lz_factory.py**
```python
def make_lz2_detector(...) -> BaseVariantWrapper
```
- Ветки:
  - det_prev: 100→110→100_or_000 (prev занят)
  - det_next: 001→011→001_or_000 (next занят)
- Особенность: Две независимые цепочки, любая может активироваться
- Возврат: `BaseVariantWrapper([det_prev, det_next])`

**variant3_lz_factory.py**
```python
def make_lz3_detector(...) -> BaseDetector
```
- Фазы: 0 (101, ts01) → 1 (111, tlz) → 2 (101, ts02) → открытие
- Логика: Шунтовое движение через секцию (въезд→проезд→выезд)

**variant5_lz_factory.py**
```python
def make_lz5_detector(ctrl_rc_name, ts01_lz5, tlz_lz5, tkon_lz5) -> BaseDetector
```
- Особенность: Не использует соседей! prev_rc_name=None, next_rc_name=None
- Условие: `can_lock=True` для РЦ (из rc_capabilities)
- Фазы: 0 (свободна, не замкнута) → 1 (занята, не замкнута) → открытие

**variant6_lz_factory.py**
```python
def make_lz6_detector(ctrl_rc_name, ts01_lz6, tlz_lz6, tkon_lz6) -> BaseDetector
```
- Особенность: Не использует соседей! prev_rc_name=None, next_rc_name=None
- Условие: **Нет проверки can_lock** — работает на любой РЦ
- Фазы: 0 (свободна, ts01) → 1 (занята, tlz) → открытие
- Логика: Длительная занятость после предварительной свободности

> **Разница v5 vs v6:** v5 проверяет `can_lock` и состояние замыкания; v6 только состояние свободна/занята. v5 для РЦ с возможностью замыкания, v6 для любых РЦ.

**variant7_lz_factory.py**
```python
def make_lz7_detector(...) -> BaseVariantWrapper
```
- Ветки:
  - det_no_adjacent: X0X→X0X_OCC (нет соседей вообще)
  - det_no_prev: 00X→00X_OCC (нет prev)
  - det_no_next: X00→X00_OCC (нет next)
- Особенность: requires_neighbors=NeighborRequirement.NONE
- Логика выбора ветки: Определяется топологией (какие соседи отсутствуют)

**variant8_lz_factory.py**
```python
def make_lz8_detector(...) -> BaseVariantWrapper
```
- Ветки:
  - det_prev: 110_or_111→011_or_111→010 (prev занят)
  - det_next: 011_or_111→01x_or_x10→010 (next занят)
  - det_mid: 010→011→010 (средний вариант)
- Особенность: Самые сложные маски с "любыми" состояниями

---

### 4. BaseVariantWrapper (`base_wrapper.py`)

**Назначение:** Управление несколькими детекторами как одним.

```python
class BaseVariantWrapper:
    def __init__(self, detectors: List[BaseDetector])
    def update(step, dt) -> (opened, closed)
```

**Логика:**
- `opened=True` — если хотя бы один детектор открылся (был неактивен, стал активен)
- `closed=True` — если был активен и любой детектор закрылся ИЛИ все неактивны
- `self.active = any(det.active for det in self.detectors)`

---

### 5. Движок детекторов (`detectors_engine.py`)

**Ключевые структуры:**

```python
@dataclass
class DetectorsConfig:
    ctrl_rc_id: str           # ID контролируемой РЦ
    prev_rc_name: Optional[str]
    ctrl_rc_name: str
    next_rc_name: Optional[str]
    # Тайминги и enable-флаги для каждого варианта
    ts01_lz1, tlz_lz1, tkon_lz1, enable_lz1: ...
    ts01_lz2, ts02_lz2, tlz_lz2, tkon_lz2, enable_lz2: ...
    # ... и т.д. для всех вариантов

@dataclass
class DetectorsState:
    v1: Optional[BaseDetector]
    v2: Optional[BaseVariantWrapper]  # или BaseDetector для одноветочных
    v3: Optional[BaseDetector]
    v5: Optional[BaseDetector]
    v6: Optional[BaseDetector]        # ← НОВОЕ: v6 детектор
    v7: Optional[BaseVariantWrapper]
    v8: Optional[BaseVariantWrapper]
```

**Основные функции:**

```python
def init_detectors_engine(cfg: DetectorsConfig, rc_ids: List[str]) -> DetectorsState:
    # Создает детекторы по конфигурации, вызывает соответствующие make_lz{N}_detector()

def update_detectors(det_state, t, dt, rc_states, switch_states, 
                     signal_states, topology_info, cfg, modes) -> (DetectorsState, DetectorsResult):
    # Обновляет все детекторы, конвертирует rc_states в ID, проверяет смену топологии
```

**Динамическая топология:**
- `effective_prev_rc`, `effective_next_rc` — определяются topology_manager
- При смене соседей — сброс фаз формирования (неактивных детекторов)
- rc_states конвертируется из имен в ID через `_ensure_rc_states_by_id()`

---

### 6. Топология (`topology_manager.py`)

**UniversalTopologyManager:**
- Определяет физических соседей с учетом положения стрелок
- Реализует "latch" — удержание соседа при временной потере контроля (T_PK)
- Возвращает `prev_control_ok`, `next_control_ok` — флаги достоверности

**StationModel (`station_model.py`):**
- RcNode — узел с prev_links/next_links в формате `(target_id, switch_id, required_state)`
- `required_state`: 1=плюс, 0=минус, -1=безусловно

---

## Как добавить новый вариант (vN)

### Шаг 1: Создать `variantN_lz_factory.py`

**Шаблон для одноветочного варианта:**
```python
# variantN_lz_factory.py
from base_detector import BaseDetector, PhaseConfig, DetectorConfig, CompletionMode, NeighborRequirement
from variants_common import mask_XXX  # импорт нужных масок

MASK_XXX = N00  # уникальный ID маски

def make_lzN_detector(
    prev_rc_name: Optional[str],
    ctrl_rc_name: str,
    next_rc_name: Optional[str],
    ts01_lzN: float,
    tlz_lzN: float,
    tkon_lzN: float,
) -> BaseDetector:
    
    phases = [
        PhaseConfig(
            phase_id=0,
            duration=float(ts01_lzN),
            next_phase_id=1,
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_XXX,
            mask_fn=mask_XXX,  # из variants_common
            requires_neighbors=NeighborRequirement.BOTH,  # или NONE/ONLY_CTRL
        ),
        PhaseConfig(
            phase_id=1,
            duration=float(tlz_lzN),
            next_phase_id=-1,  # -1 = финал, открытие
            timer_mode="continuous",
            reset_on_exit=True,
            mask_id=MASK_YYY,
            mask_fn=mask_YYY,
            requires_neighbors=NeighborRequirement.BOTH,
        ),
    ]
    
    config = DetectorConfig(
        initial_phase_id=0,
        phases=phases,
        t_kon=float(tkon_lzN),
        completion_mode=CompletionMode.FREE_TIME,
        variant_name=f"v{N}",
    )
    
    return BaseDetector(
        config=config,
        prev_rc_name=prev_rc_name,
        ctrl_rc_name=ctrl_rc_name,
        next_rc_name=next_rc_name,
    )

VN_SCHEMA = {
    "variant_id": N,
    "variant_name": f"lz{N}",
    "description": "Описание варианта",
    "phases": [...],
    "parameters": ["ts01_lzN", "tlz_lzN", "tkon_lzN"],
    "topology": "dynamic",
}
```

**Шаблон для многоветочного варианта:**
```python
from base_wrapper import BaseVariantWrapper

def _make_branch_detector(...) -> BaseDetector:
    # Создает детектор одной ветки
    ...

def make_lzN_detector(...) -> BaseVariantWrapper:
    det_branch1 = _make_branch_detector(...)
    det_branch2 = _make_branch_detector(...)
    return BaseVariantWrapper([det_branch1, det_branch2])
```

---

### Шаг 2: Добавить маски в `variants_common.py`

```python
def mask_XXX(step, prev, ctrl, next) -> bool:
    """Описание условия"""
    if not ctrl:
        return False
    # ... логика проверки состояний
    return result

# Добавить в get_mask_by_id():
mask_map = {
    ...
    N00: mask_XXX,
}

# Добавить в mask_to_string():
names = {
    ...
    N00: "XXX",
}
```

---

### Шаг 3: Обновить `detectors_engine.py`

**В `DetectorsConfig`:**
```python
@dataclass
class DetectorsConfig:
    # ... существующие поля ...
    
    # vN
    ts01_lzN: float = 0.0
    tlz_lzN: float = 0.0
    tkon_lzN: float = 0.0
    enable_lzN: bool = False
```

**В `DetectorsState`:**
```python
@dataclass
class DetectorsState:
    # ... существующие поля ...
    vN: Optional[BaseDetector] = None  # или BaseVariantWrapper
```

**В `init_detectors_engine()`:**
```python
if cfg.enable_lzN:
    from variantN_lz_factory import make_lzN_detector
    state.vN = make_lzN_detector(
        prev_rc_name=cfg.prev_rc_name,
        ctrl_rc_name=cfg.ctrl_rc_name,
        next_rc_name=cfg.next_rc_name,
        ts01_lzN=cfg.ts01_lzN,
        tlz_lzN=cfg.tlz_lzN,
        tkon_lzN=cfg.tkon_lzN,
    )
```

**В `update_detectors()`:**
```python
# vN
if det_state.vN:
    opened, closed = det_state.vN.update(step_adapter, dt)
    if opened:
        result.opened = True
        result.flags.append("llz_vN_open")
    if closed:
        result.closed = True
        result.flags.append("llz_vN_closed")
    if det_state.vN.active:
        variants_active.append(N)
```

---

### Шаг 4: Обновить `flags_engine.py`

```python
# В build_flags_simple():
vN_active = det_state.vN.active if det_state.vN else False

# В определении variant (приоритет):
if vN_active:
    variant = N  # или max существующего + 1

# Добавить флаг:
if vN_active and "llz_vN" not in flags:
    flags.append("llz_vN")
```

---

### Шаг 5: Обновить конфигурацию

**В `station_detectors_config.py`** — добавить тайминги:
```python
@dataclass
class GlobalTimings:
    # ... существующие ...
    ts01_lzN: float = 3.0
    tlz_lzN: float = 3.0
    tkon_lzN: float = 3.0
```

**В `RcVariantConfig`:**
```python
enable_lzN: bool = False
```

**В `station_detectors_factory.py`** — добавить маппинг:
```python
# В build_detectors_config_for_rc():
ts01_lzN = gt.ts01_lzN
tlz_lzN = gt.tlz_lzN
tkon_lzN = gt.tkon_lzN
enable_lzN = rc_cfg.enable_lzN

return LocalDetectorsConfig(
    # ... существующие ...
    ts01_lzN=ts01_lzN,
    tlz_lzN=tlz_lzN,
    tkon_lzN=tkon_lzN,
    enable_lzN=enable_lzN,
)
```

---

### Шаг 6: Создать тест `test_detectors_engine_vN.py`

```python
from sim_core import SimulationConfig, SimulationContext, ScenarioStep
from detectors_engine import DetectorsConfig

def test_vN_full_cycle():
    det_cfg = DetectorsConfig(
        ctrl_rc_id="108",
        prev_rc_name="59",
        ctrl_rc_name="108", 
        next_rc_name="83",
        # Отключаем другие варианты...
        enable_lzN=True,
        ts01_lzN=2.0,
        tlz_lzN=2.0,
        tkon_lzN=3.0,
    )
    
    sim_cfg = SimulationConfig(t_pk=30.0, detectors_config=det_cfg)
    
    scenario = [
        # Шаги сценария...
    ]
    
    ctx = SimulationContext(config=sim_cfg, scenario=scenario, ctrl_rc_id="108")
    timeline = ctx.run()
    
    assert any("llz_vN_open" in s.flags for s in timeline)
    assert any("llz_vN" in s.flags and s.lz_variant == N for s in timeline)
    assert any("llz_vN_closed" in s.flags for s in timeline)
```

---

## Правила именования

| Элемент | Формат | Пример |
|---------|--------|--------|
| Файл фабрики | `variant{N}_lz_factory.py` | `variant9_lz_factory.py` |
| Функция | `make_lz{N}_detector` | `make_lz9_detector` |
| Константа маски | `MASK_XXX` | `MASK_010` |
| ID маски | `N00` (N=вариант) | `900`, `901`... |
| Параметр времени | `t{suffix}_lz{N}` | `ts01_lz9`, `tlz_lz9` |
| Флаг открытия | `llz_v{N}_open` | `llz_v9_open` |
| Флаг активности | `llz_v{N}` | `llz_v9` |
| Флаг закрытия | `llz_v{N}_closed` | `llz_v9_closed` |

---

## Назначение временных параметров (Т)

Чтобы не ошибаться при настройке времени, следуйте принципу:

| Параметр | Когда отсчитывается | Что означает | Пример |
|----------|---------------------|--------------|--------|
| **ts01** (или ts0) | От начала выполнения условия фазы 0 | Сколько секунд должно длиться состояние "ДАНО" до перехода к фазе 1 | РЦ свободна ≥ ts01 секунд |
| **ts02** (или ts1) | От начала выполнения условия фазы 1 | Дополнительное время накопления (если есть промежуточная фаза) | РЦ в промежуточном состоянии ≥ ts02 секунд |
| **tlz** | От начала выполнения условия финальной фазы | Сколько секунд длится формирование ЛЗ перед открытием | РЦ занята ≥ tlz секунд |
| **tkon** | От момента открытия ЛЗ | Сколько секунд РЦ должна быть свободна для закрытия ЛЗ | РЦ свободна ≥ tkon секунд → закрытие |

**Правила расчета общего времени:**

```
Общее время формирования ЛЗ = ts01 + tlz        (для 2-фазных: v1, v5, v6)
Общее время формирования ЛЗ = ts01 + ts02 + tlz (для 3-фазных: v3)
```

**Важно:**
- Времена **не суммируются автоматически** — каждое отсчитывается от своего условия
- Если условие прерывается → таймер сбрасывается (при `timer_mode="continuous"`)
- `t_kon` отсчитывается только **после открытия** ЛЗ, не во время формирования

**Пример для v6:**
```python
ts01_lz6 = 2.0  # РЦ свободна ≥ 2 сек → переход к фазе 1
tlz_lz6 = 2.0   # РЦ занята ≥ 2 сек → открытие ЛЗ
tkon_lz6 = 3.0  # После открытия: РЦ свободна ≥ 3 сек → закрытие

# Итого: ЛЗ откроется через 4 секунды после начала (2+2)
# И закроется через 3 секунды после освобождения РЦ
```

---

## Состояния РЦ и их интерпретация

В системе используется единая нумерация состояний (UniStateID):

| UniStateID | Состояние | Интерпретация для ЛЗ |
|------------|-----------|----------------------|
| **0** | Нет контроля / неопределено | Не свободна и не занята (прерывает таймеры) |
| **1** | Замыкание | Специальное состояние (для v5) |
| **2** | Зарезервировано | — |
| **3** | Свободна, нет замыкания | **Свободна** (rc_is_free=True) |
| **4** | Свободна, замыкание | **Свободна** (rc_is_free=True) + locked |
| **5** | Свободна, неисправность | **Свободна** (rc_is_free=True) |
| **6** | Занята, нет замыкания | **Занята** (rc_is_occupied=True) |
| **7** | Занята, замыкание | **Занята** (rc_is_occupied=True) + locked |
| **8** | Занята, неисправность | **Занята** (rc_is_occupied=True) |

**Функции проверки (из `uni_states.py`):**
```python
def rc_is_free(state: int) -> bool:
    """Состояния 3, 4, 5 считаются свободными."""
    return state in (3, 4, 5)

def rc_is_occupied(state: int) -> bool:
    """Состояния 6, 7, 8 считаются занятыми."""
    return state in (6, 7, 8)

def rc_is_locked(state: int) -> bool:
    """Состояния 4, 7 имеют признак замыкания."""
    return state in (4, 7)
```

**Важные моменты для масок:**

1. **Маска проверяет `rc_is_free()` / `rc_is_occupied()`**, а не конкретные ID
2. **Состояние 0 (нет контроля)** — не свободно и не занято! Оно прерывает таймеры формирования.
3. **Состояния 4 и 7 (замыкание)** — учитываются в v5 через `rc_is_locked()`, для остальных вариантов игнорируются.

**Пример в маске:**
```python
def mask_010(step, prev, ctrl, next) -> bool:
    # Центр должен быть "занят" (6, 7, или 8)
    s_ctrl = step.rc_states.get(ctrl, 0)
    return rc_is_occupied(s_ctrl)  # True для 6,7,8; False для 0,1,2,3,4,5
```

---

## Особенности реализации

### Обработка None в масках

В масках `mask_000`, `mask_010` и др.:
- `if prev is None: prev_ok = True` — отсутствие соседа считается "свободным"
- Но `requires_neighbors=NeighborRequirement.BOTH` требует, чтобы сосед существовал (не None) и был достоверен

**Это различие критично:**
- **Маска** определяет логическое условие (свободен/занят)
- **NeighborRequirement** определяет требование к достоверности соседа для работы детектора

### Динамическая топология vs Fallback

```python
# В BaseDetector._get_effective_neighbors():
prev = getattr(step, "effective_prev_rc", None)  # Из topology_manager
if prev is None:
    prev = self._config_prev_rc  # Fallback из конфига
```
Топология имеет приоритет, но fallback имена используются при отсутствии динамической информации.

### Конвертация имен в ID

```python
# В update_detectors():
rc_states_by_id = _ensure_rc_states_by_id(rc_states)
# Если ключи уже ID (есть в NODES) — возвращает как есть
# Иначе конвертирует имена в ID через name_to_id маппинг
```
Это позволяет тестам использовать удобные имена ("108", "1П"), а движок работает с ID.
```

Основные изменения:
1. **Добавлен v6** в структуру проекта и таблицы сравнения
2. **Добавлены маски v6** (600, 601) с описанием
3. **Добавлено описание фабрики v6** с различиями от v5
4. **Новый раздел "Назначение временных параметров (Т)"** — подробно объясняю каждый параметр и как не ошибаться
5. **Новый раздел "Состояния РЦ и их интерпретация"** — таблица UniStateID, функции проверки, важные моменты для масок
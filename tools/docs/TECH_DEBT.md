# Техдолг / бэклог рефакторинга

Дата: 2026-02-16  
Область: `api`, `frontend`, `tools`

## Высокий приоритет (до встраивания в прод)

1. Перевести исключения на полностью фазовую модель (без оконного post-suppress как основной логики).
- Риск сейчас: смешанная модель (`abort` в фазе + `post-step` подавление по окнам) плохо объяснима и неравномерна по семействам ДС.
- Цель:
  - базовая навеска на фазы открытия (`next_phase_id < 0`) уже реализована для ЛЗ/ЛС через `abort_exception_keys`;
  - проверки исключений встроены в фазы формирования для всех ДС;
  - исключения детерминированно блокируют открытие/переход нужных фаз;
  - post-processing оставить только как временный fallback на период миграции.
- Охват: не только ЛЗ/ЛС, но и другие группы ДС с аналогичной логикой.

2. Зафиксировать арбитраж одновременного формирования ДС.
- Риск сейчас: несколько ДС могут сработать в одном шаге, но политика показа не формализована.
- Цель:
  - базовое правило: если ЛЗ и ЛС формируются одновременно, приоритет у ЛЗ (уже реализовано в `exceptions_engine.py`);
  - явная матрица приоритетов по типам и вариантам ДС;
  - детерминированные правила winner/suppressed;
  - стабильный API-контракт на выдачу победителя и подавленных кандидатов;
  - регрессионные тесты конфликтных сценариев.

3. Разбить `frontend/static/schema-mvp.js` (~1300 строк).
- Риск: парсинг топологии, рендер, визуальные состояния и UI-контролы сильно сцеплены.
- План декомпозиции:
  - `schema/parser.js` (XML + парсинг топологии)
  - `schema/render.js` (SVG-отрисовка + стили)
  - `schema/state.js` (нормализация состояний, маппинг цветов)
  - `schema/ui.js` (zoom/select/step взаимодействия)

4. Разбить `api/engine_app.py` (~900 строк).
- Риск: endpoint-слой, нормализация, сборка config и оркестрация симуляции в одном файле.
- План декомпозиции:
  - `api/routes/simulate.py`
  - `api/routes/layout.py`
  - `api/routes/tests.py`
  - `api/services/normalization.py`
  - `api/services/scenario_mapper.py`

5. Разбить `tools/core/detectors_engine.py` (~900 строк).
- Риск: dataclass-структуры, init/update, обработка смены топологии и compat-слой смешаны.
- План декомпозиции:
  - `core/detectors/types.py`
  - `core/detectors/init.py`
  - `core/detectors/update.py`
  - `core/detectors/compat.py`

6. Разбить `tools/core/sim_core.py` (~650 строк).
- Риск: контекст симуляции, расчет топологии, DSP gate и run-поток в одном месте.
- План декомпозиции:
  - `core/sim/context.py`
  - `core/sim/topology.py`
  - `core/sim/step_runner.py`
  - `core/sim/run.py`

## Средний приоритет (MVP+1)

1. Починить кодировки комментариев/докстрингов в variant-файлах.
- Примеры: `tools/variants/lz/variant1_lz_factory.py`, `tools/variants/lz/variant2_lz_factory.py`,
  `tools/variants/lz/variant3_lz_factory.py`, `tools/variants/lz/variant7_lz_factory.py`,
  `tools/variants/lz/variant8_lz_factory.py`, `tools/variants/ls/variant_ls1_lz_factory.py`,
  `tools/variants/ls/variant_ls2_lz_factory.py`.
- Статус: логика стабильна, битые тексты остаются локально в комментариях.

2. Ввести строгую валидацию сценария и options payload.
- Добавить единый слой валидации до запуска симуляции.
- Возвращать явные field-level ошибки.

3. Унифицировать имена опций.
- Проблема: смешение стилей (`enable_ls2`, `enablels2`, legacy-алиасы).
- Цель: один канонический ключ + прозрачная alias-карта.

4. Добавить отдельные тесты для station layout + schema MVP mapping.
- Проверять подсветку ветви по положению стрелок.
- Проверять фильтрацию linked-индикаторов (`prev/next`).

## Низкий приоритет

1. Нормализовать стратегию логирования.
- Убрать `print` из variant-масок, перейти на структурированный logger.

2. Добавить версионирование API-контрактов фронтенда.
- Для `/station-layout`, `/simulate`, `/tests`.

3. Добавить baseline-профилирование производительности.
- Замеры `simulate` и рендера мнемосхемы на длинных сценариях.

## Не сделано сейчас (зафиксировано)

1. Полная миграция прод-интерфейса на новый schema MVP renderer.
- Причина: сначала нужен безопасный этап в sandbox, без риска для текущего прод-потока.

2. Глубокая переработка внутренней логики детекторов.
- Причина: приоритет MVP-сроков; в этом цикле делалась документация и безопасная подготовка.

3. Полная перепись всех исторических документов с битой кодировкой.
- Причина: приоритет отдан активной документации и требованиям реализации.

## Обновление 2026-02-16 (факт)

- MVP-вкладка `Schema MVP` удалена из прод-фронта (`frontend/index.html`, `frontend/static/tabs.js`, удалён `frontend/static/schema-mvp.js`).
- В `tools/core` начата декомпозиция:
  - `tools/core/detectors/types.py`
  - `tools/core/detectors/phase_exceptions.py`
  - `tools/core/sim_types.py`
- В `api` вынесены API-схемы в `api/sim/schemas.py`, добавлен адаптер `api/contract.py`.

### Осталось по рефакторингу

1. Декомпозировать `api/engine_app.py` по маршрутам и сервисам (normalize/map/layout/tests).
2. Декомпозировать `tools/core/detectors_engine.py` на init/update/compat.
3. Декомпозировать `tools/core/sim_core.py` на context/step_runner/run.
4. Провести полный прогон регрессий по всем `tools/tests` после полной декомпозиции.

## Обновление 2026-02-16 (декомпозиция, этап 2)

- Вынесены API-хелперы из `api/engine_app.py` в `api/sim/helpers.py`:
  нормализация, резолверы, канонизация options, сборка `DetectorsConfig`, конвертеры state.
- В `tools/core` вынесена совместимая обертка single-RC результата в `tools/core/sim_result.py`.
- `api/engine_app.py` и `tools/core/sim_core.py` сокращены без изменения внешнего поведения.
- Выполнен этап декомпозиции API по роутам: добавлены `api/routes/system.py`, `api/routes/layout.py`, `api/routes/simulate.py`, `api/routes/tests.py`.
- Добавлен сервисный слой API: `api/services/simulate_service.py`, `api/services/layout_service.py`, `api/services/tests_service.py`; роуты упрощены до thin-controller.
- В `tools/core` вынесен раннер `SimulationContext.run()` в `tools/core/sim_runner.py`; в `sim_core.py` убрано дублирование overlay-сборки шага для исключений.
- В `tools/core` вынесена подшаговая обработка одной РЦ в `tools/core/sim_step_runner.py`; `SimulationContext._step_single_rc` стал делегатом.

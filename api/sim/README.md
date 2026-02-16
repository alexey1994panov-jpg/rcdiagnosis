# API Simulation Helpers

Вспомогательные модули API-слоя для симуляции.

- `schemas.py`: Pydantic-модели входа/выхода API (`ScenarioIn`, `TimelineStepOut` и др.).
- `helpers.py`: нормализация имен и alias, резолв id объектов, канонизация options,
  сборка `DetectorsConfig`, конвертеры state payload.

Назначение:
- разгрузить `api/engine_app.py`;
- держать контракты и маппинг отдельно от endpoint-логики.

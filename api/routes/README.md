# API Routes

Маршруты API вынесены из `api/engine_app.py` в отдельные модули:

- `system.py`: `/`, `/defaults`, `/health`, `/exceptions-config`.
- `layout.py`: `/station-layout`, `/node-catalog`.
- `simulate.py`: `/simulate`.
- `tests.py`: `/tests*`.

Точка входа и регистрация роутов остаются в `api/engine_app.py`.

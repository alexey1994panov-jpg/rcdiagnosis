# API

HTTP-слой проекта.

- `app.py`: точка входа ASGI.
- `engine_app.py`: создание `FastAPI`, mounting static и регистрация роутов.
- `routes/`: endpoint-модули по доменам (`system`, `layout`, `simulate`, `tests`).
- `services/`: сервисная логика API (без HTTP-оберток).
- `station_layout.py`: построение layout для схемы станции.
- `contract.py`: адаптер к `tools.api_contract`.
- `sim/`: схемы и вспомогательные функции API-симуляции.

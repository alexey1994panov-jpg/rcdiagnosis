# API Services

Сервисный слой API (бизнес-логика вне HTTP-оберток):

- `simulate_service.py`: сборка payload контракта и маппинг результата `/simulate`.
- `layout_service.py`: подготовка ответа layout и каталога узлов.
- `tests_service.py`: CRUD-операции тестовых сценариев.

Роуты в `api/routes/*` должны оставаться тонкими и вызывать сервисы.

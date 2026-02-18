# RC Diagnosis

Проект для моделирования станции, расчета состояний РЦ/стрелок/сигналов и детектирования ДС (ЛЗ/ЛС) по сценариям.

## Быстрый старт (5 минут)
Требования:
- Windows + PowerShell
- Python `3.11–3.13` (рекомендуется)

```powershell
git clone https://github.com/alexey1994panov-jpg/rcdiagnosis.git
cd rcdiagnosis
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\scripts\run_server.ps1
```

После запуска откройте:
- локально: `http://127.0.0.1:8000/`
- в сети: `http://<IP_СЕРВЕРА>:8000/`

Быстрая проверка установки:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```
Ожидаемый результат: `[smoke] SUCCESS`.

## Цель MVP
- воспроизводить сценарии по шагам времени;
- рассчитывать флаги детекторов ЛЗ/ЛС;
- применять исключения (MU / после противоположной ДС / DSP);
- отдавать результат в API и отображать во фронтенде.

## Архитектура

### 1. API слой (`api/`)
- `api/engine_app.py`: точка входа FastAPI.
- `api/routes/`: HTTP-маршруты (`simulate`, `layout`, `tests`, `system`).
- `api/services/`: сервисный слой (бизнес-операции без HTTP-логики).
- `api/sim/`: схемы и нормализация входного сценария.
- `api/contract.py`: адаптер к контракту API (`tools/api_contract`).

### 2. Ядро расчета (`tools/core/`)
- `sim_core.py`: контекст симуляции и orchestration.
- `sim_runner.py`, `sim_step_runner.py`: исполнение шагов и RC-итераций.
- `detectors_engine.py`: жизненный цикл детекторов и фазы.
- `detectors/phase_exceptions.py`: фазовая политика исключений.
- `flags_engine.py`: свертка флагов в итоговый state/variant.
- `topology_manager.py`: связи control/prev/next и зависимость от стрелок.

### 3. Варианты детекторов (`tools/variants/`)
- `tools/variants/lz/`: фабрики ЛЗ (варианты 1..13).
- `tools/variants/ls/`: фабрики ЛС (варианты 1/2/4/5/6/9).
- каждый вариант задает фазовую машину и тайминги через `PhaseConfig`.

### 4. Исключения (`tools/exceptions/`)
- расчет активации исключений и подавлений;
- объектный реестр MU/NAS/CHAS/DSP;
- политика DSP и привязка к вариантам.

### 5. Станционные данные (`tools/station/` и `xml/`)
- `tools/station/`: runtime-конфиг станции для симуляции.
- `xml/`: парсеры XML, подготовка совместимых JSON, sandbox-мнемосхема.

## Поток данных
1. Фронтенд отправляет сценарий в `/simulate`.
2. API нормализует payload в канонический формат шага.
3. `tools/core/sim_core.py` выполняет симуляцию по времени.
4. Для каждой RC и шага:
   - обновляются фазы вариантов ЛЗ/ЛС;
   - применяются фазовые гейты исключений;
   - формируются флаги открытия/активности/закрытия.
5. `flags_engine` вычисляет итог `lz_state` и `lz_variant`.
6. API возвращает timeline и диагностические поля.

## Ключевые сущности сценария
- `rc_states`: состояния РЦ.
- `switch_states`: состояния стрелок.
- `signal_states`: состояния светофоров.
- `indicator_states`: состояния индикаторов (в т.ч. объектные исключения).
- `options`: тайминги и включение вариантов/исключений.
- `steps[]`: шаги с длительностью `t`.

## Проверка проекта
```powershell
python -m pytest -q
```

Локальная проверка API-импорта:
```powershell
python -c "import api.engine_app as e; print(bool(e.app))"
```

Smoke-проверка запуска API (одной командой):
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```

## Где что смотреть
- Детекторы и фазы: `tools/core/detectors_engine.py`
- Фазовые исключения: `tools/core/detectors/phase_exceptions.py`
- Общие исключения: `tools/exceptions/exceptions_engine.py`
- Варианты ЛЗ: `tools/variants/lz/`
- Варианты ЛС: `tools/variants/ls/`
- Тесты: `tools/tests/`

## Установка на другом компьютере
1. Установить Python 3.11+.
2. Клонировать репозиторий:
```powershell
git clone https://github.com/alexey1994panov-jpg/rcdiagnosis.git
cd rcdiagnosis
```
3. Создать и активировать виртуальное окружение:
```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe --version
```
4. Установить базовые зависимости:
```powershell
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Параллельная копия (проверка инструкции рядом с текущим проектом)
```powershell
cd ..
git clone https://github.com/alexey1994panov-jpg/rcdiagnosis.git rcdiagnosis_smoke
cd .\rcdiagnosis_smoke
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```
Ожидаемый результат в конце: `[smoke] SUCCESS`.

## Запуск как сервер (доступ с другого ПК)
1. На компьютере-сервере запустить:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_server.ps1
```
Явное задание адреса и порта:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_server.ps1 -BindHost 0.0.0.0 -Port 8000
```

Или напрямую:
```powershell
& .\.venv\Scripts\python.exe -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```
Для dev-режима со слежением: `powershell -ExecutionPolicy Bypass -File .\scripts\run_server.ps1 -Reload`.
2. Разрешить входящее правило в брандмауэре Windows для порта `8000` (TCP).
3. Узнать IP сервера:
```powershell
ipconfig
```
4. На другом ПК открыть фронт:
- `http://<IP_СЕРВЕРА>:8000/`

Пример:
- `http://192.168.1.50:8000/`

## Важно по фронтенду
- Фронтенд раздается этим же FastAPI-приложением (маршрут `/`), поэтому отдельный веб-сервер для статики не нужен.
- Если открывать фронтенд не через `http://<IP>:8000/`, а как отдельный origin, может понадобиться настройка CORS.

## Troubleshooting
- Ошибка PowerShell `VariableNotWritable` / `Не удается перезаписать переменную Host`:
  используйте обновлённый параметр `-BindHost` (или запускайте скрипт без `-Host`).
- Если не работает активация `.venv\Scripts\activate` из-за ExecutionPolicy:
  не активируйте окружение, а запускайте команды через `& .\.venv\Scripts\python.exe ...`.
- Если в окружении нет `pip` после `python -m venv .venv`:
  попробуйте другой Python (рекомендуется 3.11–3.13) или переустановите Python с компонентом `pip`.
- Для полной smoke-проверки с тестами:
  `powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1 -RunPytest`.

## Текущий статус
- MVP рабочий: симуляция + детекторы + исключения + API + фронтенд-панель сценариев.
- Мнемосхема и XML-пайплайн развиваются в `xml/sandbox` и `xml/integration_prep`.

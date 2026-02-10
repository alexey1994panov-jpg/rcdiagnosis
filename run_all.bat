@echo off
cd /d %~dp0tools

python generate_station_from_objects.py || goto :error
python build_switch_logic.py || goto :error
python build_signals_logic.py || goto :error
python -m pytest -q || goto :error

echo.
echo Все шаги успешно выполнены.
goto :eof

:error
echo.
echo Ошибка при выполнении одного из шагов.
exit /b 1


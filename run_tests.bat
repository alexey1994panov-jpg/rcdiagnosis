@echo off
setlocal

rem при необходимости раскомментируй строку ниже, если используешь виртуальное окружение
rem call venv\Scripts\activate.bat

python -m pytest -q
endlocal
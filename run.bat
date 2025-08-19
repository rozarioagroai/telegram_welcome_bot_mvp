@echo off
setlocal
set "ROOT=%~dp0"
set "VENV_PY=%ROOT%\.venv\Scripts\python.exe"

REM 1) Создать venv, если нет
if not exist "%VENV_PY%" (
  py -3.11 -m venv "%ROOT%\.venv"
)

REM 2) Установить/обновить зависимости (быстро, если уже стоят)
"%VENV_PY%" -m pip install -r "%ROOT%requirements.txt"

REM 3) Запустить бота
"%VENV_PY%" -m src.bot_app
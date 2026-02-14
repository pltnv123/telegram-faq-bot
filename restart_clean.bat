@echo off
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul
for /d /r "%~dp0" %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q "%~dp0\*.pyc" 2>nul
timeout /t 3 >nul
start "" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python -m src.main"

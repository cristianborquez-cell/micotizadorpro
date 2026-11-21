@echo off
cd /d "%~dp0"
call "%~dp0EJECUTAR_PYTHON.bat" "%~dp0respaldo_local.py"
if errorlevel 1 echo ERROR: No se pudo completar el respaldo.
pause

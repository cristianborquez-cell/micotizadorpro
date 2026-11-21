@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0local_server.py" (
 echo ERROR: No se encuentra local_server.py en "%~dp0".
 pause
 exit /b 1
)
echo Iniciando Cotizador desde: %CD%
echo El servidor elegira el primer puerto libre entre 8765 y 8794.
echo Si la version antigua esta abierta, se iniciara en el siguiente puerto libre.
echo Mantenga esta ventana abierta mientras utiliza el cotizador.
call "%~dp0EJECUTAR_PYTHON.bat" "%~dp0local_server.py" --open
if errorlevel 1 echo ERROR: El cotizador no pudo iniciarse. Revise el mensaje anterior.
pause

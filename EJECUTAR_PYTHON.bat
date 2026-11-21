@echo off
setlocal
set "PYTHON_EXE=%~dp0runtime\python.exe"
if exist "%PYTHON_EXE%" goto ejecutar
set "PYTHON_EXE=D:\InnovatecAndroid32\python.exe"
if exist "%PYTHON_EXE%" goto ejecutar
where python >nul 2>&1 && (set "PYTHON_EXE=python" && goto ejecutar)
where py >nul 2>&1 && (set "PYTHON_EXE=py" && goto ejecutar)
echo ERROR: No se encuentra Python en D: ni en el PATH del sistema.
echo Rutas revisadas:
echo   %~dp0runtime\python.exe
echo   D:\InnovatecAndroid32\python.exe
echo   python / py (PATH)
exit /b 1
:ejecutar
echo Usando Python: %PYTHON_EXE%
"%PYTHON_EXE%" %*
exit /b %errorlevel%

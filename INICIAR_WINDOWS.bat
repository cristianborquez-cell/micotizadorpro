@echo off
cd /d %~dp0
where docker >nul 2>nul || (echo Docker Desktop no esta instalado.&pause&exit /b 1)
if not exist .env copy .env.example .env >nul
findstr /C:"CAMBIA_" .env >nul && echo IMPORTANTE: edita .env y cambia las claves antes de usar Internet.&pause

docker compose up -d --build
if errorlevel 1 (echo Error iniciando servidor.&pause&exit /b 1)
echo.
echo COTIZADOR PRO HIBRIDO V3.1 iniciado.
echo Local: http://localhost
start http://localhost
pause

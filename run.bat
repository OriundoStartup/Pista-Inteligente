@echo off
echo ==========================================
echo   🏇 SISTEMA DE HIPICA INTELIGENTE 🏇
echo ==========================================

REM Activar entorno virtual
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [WARN] No se encontro venv, intentando usar python global...
)

REM Ejecutar Sincronizacion
echo.
echo [1/3] Ejecutando Sincronizacion de Datos...
python sync_system.py

REM El script sync_system.py ya intenta abrir el navegador, 
REM pero por si acaso y para asegurar que el servidor este listo:
echo.
echo [2/3] Iniciando Servidor Web...
echo        -> El navegador se abrira automaticamente cuando el servidor este listo (si sync lo hizo)
echo        -> Si no, accede a: http://localhost:5000
echo.

REM Iniciar Flask (Bloqueante)
python app.py --host=0.0.0.0 --port=5000

pause

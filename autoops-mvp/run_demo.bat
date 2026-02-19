@echo off
setlocal EnableDelayedExpansion

echo ==========================================
echo      🚀 AutoOps MVP - Demo Launcher
echo ==========================================

REM Check if .venv exists, if so activate it
if exist .venv\Scripts\activate.bat (
    echo [INFO] Activating Virtual Environment...
    call .venv\Scripts\activate.bat
) else (
    echo [WARNING] .venv not found. Assuming Python is in PATH.
)

echo.
echo [1/5] Building Docker Image (This may take a moment)...
cd victim-app
docker build -t victim-app .
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker build failed. Is Docker Desktop running?
    pause
    exit /b %ERRORLEVEL%
)
cd ..

echo.
echo [2/5] Starting Victim Container...
REM Stop any existing instance first just in case
docker stop victim-instance-1 >nul 2>&1
docker rm victim-instance-1 >nul 2>&1
docker run -d -p 5000:5000 --name victim-instance-1 victim-app

echo.
echo [3/5] Launching Commander...
REM Launch in a new window
start "AutoOps Commander" cmd /k "call .venv\Scripts\activate.bat && python commander/main.py"

echo.
echo [4/5] Launching Dashboard...
REM Launch in a new window
start "AutoOps Dashboard" cmd /k "call .venv\Scripts\activate.bat && streamlit run commander/dashboard.py"

echo.
echo [5/5] Launching Chaos Monkey...
echo.
echo    ⚠️  The Chaos Monkey window will open.
echo    ⚠️  You must manually select options in it to trigger attacks.
echo.
start "AutoOps Chaos" cmd /k "call .venv\Scripts\activate.bat && python chaos/attack.py"

echo.
echo ==========================================
echo    ✅ SYSTEM RUNNING
echo ==========================================
echo.
echo    The following windows should be open:
echo    1. Commander (Orchestrator Logs)
echo    2. Dashboard (Streamlit UI)
echo    3. Chaos Monkey (Attack Tool)
echo.
echo    PRESS ANY KEY HERE TO STOP THE DEMO AND CLEAN UP EVERYTHING.
echo ==========================================
pause

echo.
echo ==========================================
echo      🧹 CLEANUP INITIATED
echo ==========================================
echo.

echo [1/3] Stopping Victim Containers...
docker stop victim-instance-1
REM Try to stop any replicas created by the Commander
for /f "tokens=*" %%i in ('docker ps -q --filter name^=replica') do (
    echo Stopping replica %%i...
    docker stop %%i
)

echo.
echo [2/3] Removing Containers...
docker rm victim-instance-1
for /f "tokens=*" %%i in ('docker ps -a -q --filter name^=replica') do (
    echo Removing replica %%i...
    docker rm %%i
)

echo.
echo [3/3] Removing Docker Image...
docker rmi victim-app:latest

echo.
echo ==========================================
echo      ✅ CLEANUP COMPLETE
echo ==========================================
echo.
echo You may close the other terminal windows now.
pause

@echo off
REM Master Email Processing Script for Windows
REM 
REM This script:
REM 1. Starts Gmail Watcher (monitors for new emails)
REM 2. Starts Email Auto-Processor (processes and replies)
REM 3. Optionally starts Email MCP server (for sending)
REM
REM Usage:
REM   run_email_system.bat              REM Interactive mode
REM   run_email_system.bat --daemon     REM Background mode
REM   run_email_system.bat --help       REM Show help

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "VAULT_PATH=%SCRIPT_DIR%"
set "LOG_DIR=%VAULT_PATH%logs"
set "CHECK_INTERVAL=120"
set "PROCESS_INTERVAL=60"

REM Create log directory
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Parse arguments
set "DAEMON_MODE=false"
set "ACTION=start"

:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="--daemon" (
    set "DAEMON_MODE=true"
    shift
    goto :parse_args
)
if /i "%~1"=="--stop" (
    set "ACTION=stop"
    shift
    goto :parse_args
)
if /i "%~1"=="--status" (
    set "ACTION=status"
    shift
    goto :parse_args
)
if /i "%~1"=="--logs" (
    set "ACTION=logs"
    shift
    goto :parse_args
)
if /i "%~1"=="--help" (
    set "ACTION=help"
    shift
    goto :parse_args
)
echo Unknown option: %~1
set "ACTION=help"
shift
goto :parse_args

:args_done

REM Find Python
where python >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON=python"
) else (
    where python3 >nul 2>&1
    if %errorlevel%==0 (
        set "PYTHON=python3"
    ) else (
        echo [ERROR] Python not found! Please install Python 3.8+
        pause
        exit /b 1
    )
)

if "%ACTION%"=="start" goto :start
if "%ACTION%"=="stop" goto :stop
if "%ACTION%"=="status" goto :status
if "%ACTION%"=="logs" goto :logs
if "%ACTION%"=="help" goto :help

:start
echo.
echo ============================================================
echo   AI Employee - Autonomous Email Processing System
echo ============================================================
echo.
echo [INFO] Python found: %PYTHON%
echo.

REM Check MCP Server
curl -s http://localhost:8809/tools/list >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Email MCP server is running on port 8809
) else (
    echo [!] Email MCP server is NOT running
    echo.
    echo To start the MCP server:
    echo   1. Set up Gmail API credentials:
    echo      - Go to https://console.cloud.google.com/
    echo      - Enable Gmail API
    echo      - Create OAuth 2.0 credentials
    echo      - Download credentials.json to %%USERPROFILE%%\.ai_employee\gmail_credentials.json
    echo.
    echo   2. Start the server:
    echo      bash .qwen/skills/email-mcp/scripts/start-server.sh
    echo.
    echo [!] Emails will be saved as drafts for manual sending until MCP is running
)

echo.
echo [INFO] Starting Gmail Watcher (check interval: %CHECK_INTERVAL%s)...
start "Gmail Watcher" /min %PYTHON% "%VAULT_PATH%scripts\watchers\gmail_watcher.py" "%VAULT_PATH%" --interval %CHECK_INTERVAL% --verbose

echo [INFO] Starting Email Auto-Processor (check interval: %PROCESS_INTERVAL%s)...
start "Email Processor" /min %PYTHON% "%VAULT_PATH%scripts\email_auto_processor.py" "%VAULT_PATH%" --loop --loop-interval %PROCESS_INTERVAL% --auto-send --use-qwen --verbose

echo.
echo ============================================================
echo [OK] All services started successfully!
echo ============================================================
echo.
echo Gmail Watcher: Checking every %CHECK_INTERVAL%s
echo Email Processor: Checking every %PROCESS_INTERVAL%s
echo.
echo Services are running in minimized windows.
echo Close those windows to stop the services.
echo.
pause
goto :end

:stop
echo [INFO] Stopping all services...

REM Find and kill Gmail Watcher processes
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr /i "gmail_watcher"') do (
    echo [INFO] Stopping Gmail Watcher (PID: %%i)
    taskkill /PID %%i /F >nul 2>&1
)

REM Find and kill Email Processor processes
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr /i "email_auto_processor"') do (
    echo [INFO] Stopping Email Processor (PID: %%i)
    taskkill /PID %%i /F >nul 2>&1
)

echo [OK] All services stopped
pause
goto :end

:status
echo.
echo ============================================================
echo   System Status
echo ============================================================
echo.

REM Check running Python processes
echo Checking running services...
tasklist /fi "imagename eq python.exe" /fo csv | findstr /i "gmail_watcher" >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Gmail Watcher: Running
) else (
    echo [!] Gmail Watcher: Not running
)

tasklist /fi "imagename eq python.exe" /fo csv | findstr /i "email_auto_processor" >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Email Auto-Processor: Running
) else (
    echo [!] Email Auto-Processor: Not running
)

curl -s http://localhost:8809/tools/list >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Email MCP Server: Running (port 8809)
) else (
    echo [!] Email MCP Server: Not running
)

REM Count pending emails
set "pending=0"
for %%f in ("%VAULT_PATH%Needs_Action\EMAIL_*.md") do set /a pending+=1
echo.
echo [INFO] Pending emails in Needs_Action: %pending%

REM Count pending approvals
set "approvals=0"
for %%f in ("%VAULT_PATH%Pending_Approval\*.md") do set /a approvals+=1
echo [INFO] Pending approvals: %approvals%

echo.
pause
goto :end

:logs
echo.
echo ============================================================
echo   Recent Logs
echo ============================================================
echo.

if exist "%LOG_DIR%\gmail_watcher.log" (
    echo --- Gmail Watcher Log (last 20 lines) ---
    more +1 "%LOG_DIR%\gmail_watcher.log" | tail -20
    echo.
)

if exist "%LOG_DIR%\email_processor.log" (
    echo --- Email Processor Log (last 20 lines) ---
    more +1 "%LOG_DIR%\email_processor.log" | tail -20
    echo.
)

pause
goto :end

:help
echo.
echo ============================================================
echo   AI Employee - Autonomous Email Processing System
echo ============================================================
echo.
echo Usage: run_email_system.bat [OPTIONS]
echo.
echo Options:
echo   --daemon      Run in background mode (minimized windows)
echo   --stop        Stop all services
echo   --status      Show service status
echo   --logs        Show recent logs
echo   --help        Show this help message
echo.
echo Examples:
echo   # Run interactively
echo   run_email_system.bat
echo.
echo   # Run in background
echo   run_email_system.bat --daemon
echo.
echo   # Check status
echo   run_email_system.bat --status
echo.
echo   # View logs
echo   run_email_system.bat --logs
echo.
echo   # Stop all services
echo   run_email_system.bat --stop
echo.
pause
goto :end

:end

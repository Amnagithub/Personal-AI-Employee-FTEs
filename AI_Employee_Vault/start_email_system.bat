@echo off
echo ============================================
echo   AI Employee Email System - Starting
echo ============================================
echo.

cd /d "C:\Users\Saif\Documents\GitHub\Personal AI Employee FTEs\AI_Employee_Vault"

echo [1/2] Starting Gmail Watcher...
echo        Monitoring Gmail every 2 minutes...
echo.
start "Gmail Watcher" cmd /k "python scripts\watchers\gmail_watcher.py . --interval 120"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Email Auto-Processor...
echo        Processing emails every 60 seconds...
echo.
start "Email Auto-Processor" cmd /k "python scripts\email_auto_processor.py . --loop --loop-interval 60"

echo.
echo ============================================
echo   Email system started successfully!
echo ============================================
echo.
echo Two terminal windows opened:
echo   - Gmail Watcher: Monitors your Gmail inbox
echo   - Auto-Processor: Handles detected emails
echo.
echo To stop: Close both terminal windows or press Ctrl+C in each
echo.
timeout /t 5
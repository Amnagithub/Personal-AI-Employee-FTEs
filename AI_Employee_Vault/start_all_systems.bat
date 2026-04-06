@echo off
echo ============================================
echo   AI Employee - Full System Start
echo   (Email + WhatsApp)
echo ============================================
echo.

cd /d "C:\Users\Saif\Documents\GitHub\Personal AI Employee FTEs\AI_Employee_Vault"

echo [1/4] Starting Gmail Watcher...
echo        Monitoring Gmail every 2 minutes...
echo.
start "Gmail Watcher" cmd /k "python scripts\watchers\gmail_watcher.py . --interval 120"

timeout /t 2 /nobreak >nul

echo [2/4] Starting Email Auto-Processor...
echo        Processing emails every 60 seconds...
echo.
start "Email Auto-Processor" cmd /k "python scripts\email_auto_processor.py . --loop --loop-interval 60 --auto-send"

timeout /t 2 /nobreak >nul

echo [3/4] Starting WhatsApp Watcher...
echo        Monitoring WhatsApp Web every 30 seconds...
echo.
start "WhatsApp Watcher" cmd /k "python scripts\watchers\whatsapp_watcher.py . --interval 30"

timeout /t 2 /nobreak >nul

echo [4/4] Starting WhatsApp Auto-Processor...
echo        Processing messages every 60 seconds...
echo.
start "WhatsApp Auto-Processor" cmd /k "python scripts\whatsapp_processor.py . --loop --loop-interval 60 --auto-send"

echo.
echo ============================================
echo   All systems started successfully!
echo ============================================
echo.
echo Four terminal windows opened:
echo   1. Gmail Watcher - Monitors Gmail inbox
echo   2. Email Auto-Processor - Handles emails
echo   3. WhatsApp Watcher - Monitors WhatsApp Web
echo   4. WhatsApp Auto-Processor - Handles messages
echo.
echo FIRST TIME SETUP:
echo   - WhatsApp will open a browser window
echo   - Scan QR code from WhatsApp mobile app
echo   - Session saved automatically
echo.
echo To stop: Close all terminal windows or press Ctrl+C in each
echo.
timeout /t 10
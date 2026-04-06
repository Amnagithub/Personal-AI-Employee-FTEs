@echo off
echo ============================================
echo   AI Employee WhatsApp System - Starting
echo ============================================
echo.

cd /d "C:\Users\Saif\Documents\GitHub\Personal AI Employee FTEs\AI_Employee_Vault"

echo [1/2] Starting WhatsApp Watcher...
echo        Monitoring WhatsApp Web every 30 seconds...
echo.
start "WhatsApp Watcher" cmd /k "python scripts\watchers\whatsapp_watcher.py . --interval 30"

timeout /t 3 /nobreak >nul

echo [2/2] Starting WhatsApp Auto-Processor...
echo        Processing messages every 60 seconds...
echo.
start "WhatsApp Auto-Processor" cmd /k "python scripts\whatsapp_processor.py . --loop --loop-interval 60 --auto-send"

echo.
echo ============================================
echo   WhatsApp system started successfully!
echo ============================================
echo.
echo Two terminal windows opened:
echo   - WhatsApp Watcher: Monitors WhatsApp Web
echo   - Auto-Processor: Handles detected messages
echo.
echo IMPORTANT: First time setup:
echo   1. WhatsApp Watcher will open a browser
echo   2. Scan QR code from WhatsApp mobile app
echo   3. Session will be saved for future use
echo.
echo To stop: Close both terminal windows or press Ctrl+C in each
echo.
timeout /t 8
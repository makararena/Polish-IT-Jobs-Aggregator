@echo off
setlocal

REM Define paths
set "PROJECT_DIR=%cd%"
set "LOG_DIR=%PROJECT_DIR%\logs"
set "BOT_LOG_FILE=%LOG_DIR%\bot.log"
set "EMAIL=makararena@gmail.com"
set "PID_FILE=%LOG_DIR%\bot.pid"
set "MAIN_LOG_FILE=%LOG_DIR%\main.log"
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set dt=%%i
set "TODAYS_DATE=%dt:~0,8%_%dt:~8,6%"

REM Ensure the log directory exists
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Function to log messages with timestamps
setlocal enabledelayedexpansion
set "log_message="
for %%a in (%*) do set log_message=!log_message! %%a

echo %log_message% at %date% %time% >> "%MAIN_LOG_FILE%"

REM Function to start the bot
:start_bot
echo Starting bot and generating figures >> "%MAIN_LOG_FILE%"
cd /d "%PROJECT_DIR%\bot" || (echo Failed to change directory to bot >> "%MAIN_LOG_FILE%" & exit /b 1)
python generate_figures.py
python bot.py >> "%BOT_LOG_FILE%" 2>&1 &
echo %! > "%PID_FILE%"
echo Bot started with PID ! >> "%MAIN_LOG_FILE%"

REM Function to stop the bot
:stop_bot
if exist "%PID_FILE%" (
  set /p PID=<"%PID_FILE%"
  tasklist /fi "PID eq %PID%" 2>NUL | find /i "%PID%" >NUL && (
    echo Stopping bot with PID %PID% >> "%MAIN_LOG_FILE%"
    taskkill /F /PID %PID%
    del "%PID_FILE%"
    echo Bot stopped >> "%MAIN_LOG_FILE%"
  ) || (
    echo PID %PID% is not running >> "%MAIN_LOG_FILE%"
  )
) else (
  echo PID file not found >> "%MAIN_LOG_FILE%"
)

REM Function to send bot logs via email
:send_bot_logs
echo Sending bot logs via email >> "%MAIN_LOG_FILE%"
cd /d "%PROJECT_DIR%"
python email_sender.py --subject "Bot Logs - %TODAYS_DATE%" ^
                      --body "Bot logs attached." ^
                      --to "%EMAIL%" ^
                      --attachment "%BOT_LOG_FILE%"
echo Email with bot logs sent >> "%MAIN_LOG_FILE%"

REM Start script
echo Bot control script started at %date% %time% >> "%MAIN_LOG_FILE%"
call :stop_bot
call :start_bot

REM Wait for background processes (e.g., handle signals)
REM (Windows doesn't have native signal handling for scripts like Linux does, so we'll skip this part)

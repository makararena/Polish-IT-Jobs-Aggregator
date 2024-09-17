@echo off
setlocal

REM Check if a project directory was passed
if "%1"=="" (
  echo Error: No project directory provided.
  exit /b 1
)

set "PROJECT_DIR=%~1"
set "LOG_DIR=%PROJECT_DIR%\logs"
set "MAIN_LOG_FILE=%LOG_DIR%\main.log"
set "BOT_LOG_FILE=%LOG_DIR%\bot.log"
set "ZIP_FILE=%LOG_DIR%\logs.zip"
set "EMAIL=makararena@gmail.com"
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set dt=%%i
set "TODAYS_DATE=%dt:~0,8%_%dt:~8,6%"

REM Ensure the logs directory exists
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Clear existing logs
type nul > "%MAIN_LOG_FILE%"
type nul > "%BOT_LOG_FILE%"

REM Remove existing ZIP file if it exists
if exist "%ZIP_FILE%" (
  del "%ZIP_FILE%"
  echo Existing ZIP file removed at %date% %time% >> "%MAIN_LOG_FILE%"
)

echo Log files cleared at %date% %time% >> "%MAIN_LOG_FILE%"

REM Navigate to project directory
cd /d "%PROJECT_DIR%" || (echo Failed to change directory to %PROJECT_DIR% >> "%MAIN_LOG_FILE%" & exit /b 1)

REM Create virtual environment if not already present
if not exist "venv" (
  python -m venv venv
  echo Virtual environment created at %date% %time% >> "%MAIN_LOG_FILE%"
) else (
  echo Virtual environment already exists at %date% %time% >> "%MAIN_LOG_FILE%"
)

REM Activate virtual environment and upgrade pip
call venv\Scripts\activate.bat || (echo Failed to activate virtual environment >> "%MAIN_LOG_FILE%" & exit /b 1)
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies at %date% %time% >> "%MAIN_LOG_FILE%"
pip install -r requirements.txt
echo Dependencies installed at %date% %time% >> "%MAIN_LOG_FILE%"

REM Run Scrapy spiders
set "SPIDERS_DIR=workscrapper\workscrapper"
if exist "%SPIDERS_DIR%" (
  cd /d "%SPIDERS_DIR%" || (echo Failed to change directory to %SPIDERS_DIR% >> "%MAIN_LOG_FILE%" & exit /b 1)
  echo Running Scrapy spiders at %date% %time% >> "%MAIN_LOG_FILE%"
  start /b scrapy crawl pracuj_pl_spider >> "%MAIN_LOG_FILE%" 2>&1
  REM Wait for the spiders to finish
  timeout /t 30
  echo Scrapy spiders completed at %date% %time% >> "%MAIN_LOG_FILE%"
) else (
  echo Directory %SPIDERS_DIR% not found >> "%MAIN_LOG_FILE%"
  exit /b 1
)

REM Navigate back to project root
cd /d "%PROJECT_DIR%" || (echo Failed to change directory back to %PROJECT_DIR% >> "%MAIN_LOG_FILE%" & exit /b 1)

REM Run preprocessing script
echo Starting preprocessing at %date% %time% >> "%MAIN_LOG_FILE%"
python job_data_processing.py >> "%MAIN_LOG_FILE%" 2>&1
echo Preprocessing completed at %date% %time% >> "%MAIN_LOG_FILE%"

REM Send email with logs
echo Sending email with logs at %date% %time% >> "%MAIN_LOG_FILE%"
python email_sender.py --subject "Bot Launch - Daily Logs and Status - %TODAYS_DATE%" ^
                      --body "Program logs attached." ^
                      --to "%EMAIL%" ^
                      --attachment "%MAIN_LOG_FILE%"

REM Start bot
echo Starting bot at %date% %time% >> "%MAIN_LOG_FILE%"
call "%PROJECT_DIR%\control_bot.bat" >> "%BOT_LOG_FILE%" 2>&1

echo Script completed at %date% %time% >> "%MAIN_LOG_FILE%"

#!/bin/bash

set -e

# Usage: ./script.sh <project_directory>
# Script to set up and run a project, clear logs, run Scrapy spiders, preprocess data, and start a bot.

# Check if a project directory was passed
if [ -z "$1" ]; then
  echo "Error: No project directory provided."
  exit 1
fi

PROJECT_DIR="$1"
LOG_DIR="$PROJECT_DIR/logs"
MAIN_LOG_FILE="$LOG_DIR/main.log"
BOT_LOG_FILE="$LOG_DIR/bot.log"
ZIP_FILE="$LOG_DIR/logs.zip"
EMAIL="makararena@gmail.com"
TODAYS_DATE=$(date +"%Y-%m-%d_%H-%M-%S")

# Ensure the logs directory exists
mkdir -p "$LOG_DIR"

# Clear existing logs
: > "$MAIN_LOG_FILE"
: > "$BOT_LOG_FILE"

# Remove existing ZIP file if it exists
if [ -f "$ZIP_FILE" ]; then
  rm "$ZIP_FILE"
  echo "Existing ZIP file removed at $(date)" | tee -a "$MAIN_LOG_FILE"
fi

echo "Log files cleared at $(date)" | tee -a "$MAIN_LOG_FILE"

# Navigate to project directory
cd "$PROJECT_DIR" || { echo "Failed to change directory to $PROJECT_DIR at $(date)" | tee -a "$MAIN_LOG_FILE"; exit 1; }

# Create virtual environment if not already present
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "Virtual environment created at $(date)" | tee -a "$MAIN_LOG_FILE"
else
  echo "Virtual environment already exists at $(date)" | tee -a "$MAIN_LOG_FILE"
fi

# Activate virtual environment and upgrade pip
source venv/bin/activate || { echo "Failed to activate virtual environment at $(date)" | tee -a "$MAIN_LOG_FILE"; exit 1; }
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies at $(date)" | tee -a "$MAIN_LOG_FILE"
pip install -r requirements.txt
echo "Dependencies installed at $(date)" | tee -a "$MAIN_LOG_FILE"

# # Run Scrapy spiders
# SPIDERS_DIR="workscrapper/workscrapper"
# if [ -d "$SPIDERS_DIR" ]; then
#   cd "$SPIDERS_DIR" || { echo "Failed to change directory to $SPIDERS_DIR at $(date)" | tee -a "$MAIN_LOG_FILE"; exit 1; }
#   echo "Running Scrapy spiders at $(date)" | tee -a "$MAIN_LOG_FILE"
#   {
#     scrapy crawl pracuj_pl_spider >> "$MAIN_LOG_FILE" 2>&1 &
#     SPIDER1_PID=$!

#     scrapy crawl theprotocol_spider >> "$MAIN_LOG_FILE" 2>&1 &
#     SPIDER2_PID=$!

#     scrapy crawl buldogjob_spider >> "$MAIN_LOG_FILE" 2>&1 &
#     SPIDER3_PID=$!

#     # Wait for all spiders to complete
#     wait $SPIDER1_PID $SPIDER2_PID $SPIDER3_PID
#   } >> "$MAIN_LOG_FILE" 2>&1
#   echo "Scrapy spiders completed at $(date)" | tee -a "$MAIN_LOG_FILE"
# else
#   echo "Directory $SPIDERS_DIR not found at $(date)" | tee -a "$MAIN_LOG_FILE"
#   exit 1
# fi

# Navigate back to project root
cd "$PROJECT_DIR" || { echo "Failed to change directory back to $PROJECT_DIR at $(date)" | tee -a "$MAIN_LOG_FILE"; exit 1; }

# Run preprocessing script
echo "Starting preprocessing at $(date)" | tee -a "$MAIN_LOG_FILE"
python3 job_data_processing.py >> "$MAIN_LOG_FILE" 2>&1
echo "Preprocessing completed at $(date)" | tee -a "$MAIN_LOG_FILE"

# Send email with logs
echo "Sending email with logs at $(date)" | tee -a "$MAIN_LOG_FILE"
python3 email_sender.py --subject "Bot Launch - Daily Logs and Status - $TODAYS_DATE" \
                     --body "Program logs attached." \
                     --to "$EMAIL" \
                     --attachment "$MAIN_LOG_FILE"

# Start bot
echo "Starting bot at $(date)" | tee -a "$MAIN_LOG_FILE"
"$PROJECT_DIR/control_bot.sh" >> "$BOT_LOG_FILE" 2>&1

# Log completion
echo "Script completed at $(date)" | tee -a "$MAIN_LOG_FILE"

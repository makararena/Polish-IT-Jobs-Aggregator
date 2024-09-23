#!/bin/bash

set -e

# Function to log messages
log_message() {
  local MESSAGE=$1
  echo "$MESSAGE at $(date)" | tee -a "$MAIN_LOG_FILE"
}

# Check if a project directory was provided
if [ -z "$1" ]; then
  echo "Error: No project directory provided."
  exit 1
fi

PROJECT_DIR="$1"
LOG_DIR="$PROJECT_DIR/logs"
MAIN_LOG_FILE="$LOG_DIR/main.log"
ZIP_FILE="$LOG_DIR/logs.zip"
EMAIL="makararena@gmail.com"
TODAYS_DATE=$(date +"%Y-%m-%d_%H-%M-%S")

# Ensure the logs directory exists
mkdir -p "$LOG_DIR"

# Clear existing log files
> "$MAIN_LOG_FILE"

# Remove existing ZIP file if it exists
if [ -f "$ZIP_FILE" ]; then
  rm "$ZIP_FILE"
  log_message "Existing ZIP file removed"
fi

log_message "Log files cleared"

# Navigate to the project directory
if ! cd "$PROJECT_DIR"; then
  log_message "Failed to change directory to $PROJECT_DIR"
  exit 1
fi

# Create virtual environment if not already present
if [ ! -d "venv" ]; then
  python3 -m venv venv
  log_message "Virtual environment created"
else
  log_message "Virtual environment already exists"
fi

# Activate virtual environment and upgrade pip
if ! source venv/bin/activate; then
  log_message "Failed to activate virtual environment"
  exit 1
fi
pip install --upgrade pip

# Install dependencies
log_message "Installing dependencies"
if ! pip install -r requirements.txt; then
  log_message "Failed to install dependencies"
  exit 1
fi
log_message "Dependencies installed"

# Run Scrapy spiders
SPIDERS_DIR="workscrapper/workscrapper"
if [ -d "$SPIDERS_DIR" ]; then
  if ! cd "$SPIDERS_DIR"; then
    log_message "Failed to change directory to $SPIDERS_DIR"
    exit 1
  fi

  log_message "Running Scrapy spiders"
  
  scrapy crawl pracuj_pl_spider >> "$MAIN_LOG_FILE" 2>&1 &
  SPIDER1_PID=$!
  
  scrapy crawl theprotocol_spider >> "$MAIN_LOG_FILE" 2>&1 &
  SPIDER2_PID=$!
  
  scrapy crawl buldogjob_spider >> "$MAIN_LOG_FILE" 2>&1 &
  SPIDER3_PID=$!

  # Wait for all spiders to complete
  wait $SPIDER1_PID $SPIDER2_PID $SPIDER3_PID 

  log_message "Scrapy spiders completed"
else
  log_message "Directory $SPIDERS_DIR not found"
  exit 1
fi

# Navigate back to the project root directory
if ! cd "$PROJECT_DIR"; then
  log_message "Failed to change directory back to $PROJECT_DIR"
  exit 1
fi

# Run preprocessing script
log_message "Starting preprocessing"
if ! python3 job_data_processing.py >> "$MAIN_LOG_FILE" 2>&1; then
  log_message "Preprocessing failed"
  exit 1
fi
log_message "Preprocessing completed"

# Change directory to the bot folder and run generate_figures.py
BOT_DIR="bot"
if [ -d "$BOT_DIR" ]; then
  if ! cd "$BOT_DIR"; then
    log_message "Failed to change directory to $BOT_DIR"
    exit 1
  fi
  
  log_message "Running generate_figures.py"
  if ! python3 generate_figures.py >> "$MAIN_LOG_FILE" 2>&1; then
    log_message "Failed to run generate_figures.py"
    exit 1
  fi
  log_message "generate_figures.py completed"
else
  log_message "Directory $BOT_DIR not found"
  exit 1
fi

# Navigate back to the project root directory
if ! cd "$PROJECT_DIR"; then
  log_message "Failed to change directory back to $PROJECT_DIR"
  exit 1
fi

# Send email with logs
log_message "Sending email with logs"
if ! python3 email_sender.py --subject "Bot Launch - Daily Logs and Status - $TODAYS_DATE" \
                             --body "Program logs attached." \
                             --to "$EMAIL" \
                             --attachment "$MAIN_LOG_FILE"; then
  log_message "Failed to send email"
  exit 1
fi

# Log completion
log_message "Script completed successfully"

#!/bin/bash

# Define paths
PROJECT_DIR="$(pwd)"
LOG_DIR="$PROJECT_DIR/logs"
MAIN_LOG_FILE="$LOG_DIR/main.log"
BOT_LOG_FILE="$LOG_DIR/bot.log"
ZIP_FILE="/tmp/logs.zip"
EMAIL="makararena@gmail.com"
CRON_PATTERN="57 15 * * * $PROJECT_DIR/main.sh"

# Ensure the script exits on any error
set -e

# Create the logs directory if it does not exist
mkdir -p "$LOG_DIR"

# Clear existing logs
: > "$MAIN_LOG_FILE"
: > "$BOT_LOG_FILE"

# Log start time
echo "Cron job started at $(date)" | tee -a "$MAIN_LOG_FILE"

# Exclude the current cron job pattern
crontab -l | grep -v "$CRON_PATTERN" | crontab - 2>> "$MAIN_LOG_FILE"

# Navigate to the project directory
cd "$PROJECT_DIR" || { echo "Failed to change directory to $PROJECT_DIR" | tee -a "$MAIN_LOG_FILE"; exit 1; }

# Create the virtual environment if it does not exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "Virtual environment created at $(date)" | tee -a "$MAIN_LOG_FILE"
fi

# Activate the virtual environment
source venv/bin/activate || { echo "Failed to activate virtual environment" | tee -a "$MAIN_LOG_FILE"; exit 1; }

# Install the dependencies
pip install -r requirements.txt 2>> "$MAIN_LOG_FILE"
echo "Dependencies installed at $(date)" | tee -a "$MAIN_LOG_FILE"

# Clone the repository if it does not exist
if [ ! -d "argos-translate" ]; then
  git clone https://github.com/argosopentech/argos-translate.git 2>> "$MAIN_LOG_FILE"
  echo "Repository cloned at $(date)" | tee -a "$MAIN_LOG_FILE"
fi

# Move the script into the cloned repository if it doesn't already exist there
if [ ! -f "argos-translate/translate.py" ]; then
  mv translate.py argos-translate/
  echo "Script moved to repository at $(date)" | tee -a "$MAIN_LOG_FILE"
fi

# Navigate to the Scrapy project directory
if [ -d "workscrapper/workscrapper" ]; then
  cd workscrapper/workscrapper || { echo "Failed to change directory to workscrapper/workscrapper" | tee -a "$MAIN_LOG_FILE"; exit 1; }
else
  echo "Directory workscrapper/workscrapper not found" | tee -a "$MAIN_LOG_FILE"
  exit 1
fi

# Run the Scrapy spiders in parallel and log output in real time
echo "Running Scrapy spiders at $(date)" | tee -a "$MAIN_LOG_FILE"

# Start each spider in the background and redirect output to individual log files
{
  scrapy crawl pracuj_pl_spider >> "$MAIN_LOG_FILE" 2>&1 &
  SPIDER1_PID=$!
  
  scrapy crawl theprotocol_spider >> "$MAIN_LOG_FILE" 2>&1 &
  SPIDER2_PID=$!
  
  scrapy crawl buldogjob_spider >> "$MAIN_LOG_FILE" 2>&1 &
  SPIDER3_PID=$!

  # Wait for all spiders to finish
  wait $SPIDER1_PID
  wait $SPIDER2_PID
  wait $SPIDER3_PID
} >> "$MAIN_LOG_FILE" 2>&1

# Navigate back to the parent project directory
cd "$PROJECT_DIR"

# Run the preprocess script
python3 preprocess.py >> "$MAIN_LOG_FILE" 2>&1
echo "Preprocessing completed at $(date)" | tee -a "$MAIN_LOG_FILE"

# Move the script back to the root directory if needed
mv argos-translate/translate.py .

# Send email with the main logs before starting the bot
python3 send_mail.py --subject "Daily Logs and Status" --body "Program logs attached." --to "$EMAIL" --attachment "$MAIN_LOG_FILE"
echo "Email with main logs sent at $(date)" | tee -a "$MAIN_LOG_FILE"

# Run the bot control script
"$PROJECT_DIR/control_bot.sh" >> "$BOT_LOG_FILE" 2>&1

# Create a ZIP of the logs directory
zip -r "$ZIP_FILE" "$LOG_DIR" >> "$MAIN_LOG_FILE" 2>&1
echo "ZIP created at $(date)" | tee -a "$MAIN_LOG_FILE"

# Send the email with the ZIP file attached
python3 send_mail.py --subject "Daily Logs and Status" --body "Task completed. Logs attached." --to "$EMAIL" --attachment "$ZIP_FILE"
echo "Email with ZIP sent at $(date)" | tee -a "$MAIN_LOG_FILE"

# Log end time
echo "Cron job ended at $(date)" | tee -a "$MAIN_LOG_FILE"
#!/bin/bash

set -e

cd ~/dev/test/Polish-IT-Jobs-Aggregator/

# Define paths
PROJECT_DIR="$(pwd)"
LOG_DIR="$PROJECT_DIR/logs"
MAIN_LOG_FILE="$LOG_DIR/main.log"
BOT_LOG_FILE="$LOG_DIR/bot.log"
ZIP_FILE="$LOG_DIR/logs.zip"
EMAIL="makararena@gmail.com"
TORCH_USE_CUDA_DSA=1
TODAYS_DATE=$(date +"%Y-%m-%d_%H-%M-%S")
# Log start time
echo "Script started at $(date)" >> "$MAIN_LOG_FILE"

# Create the logs directory if it does not exist
mkdir -p "$LOG_DIR"

# Clear existing logs
: > "$MAIN_LOG_FILE"
: > "$BOT_LOG_FILE"

if [ -f "$ZIP_FILE" ]; then
  rm "$ZIP_FILE"
  echo "Existing ZIP file removed at $(date)" | tee -a "$MAIN_LOG_FILE"
fi

# Log start of log clearing
echo "Log files cleared at $(date)" | tee -a "$MAIN_LOG_FILE"

# Navigate to the project directory
cd "$PROJECT_DIR" || { echo "Failed to change directory to $PROJECT_DIR at $(date)" | tee -a "$MAIN_LOG_FILE"; exit 1; }
echo "Changed directory to $PROJECT_DIR at $(date)" | tee -a "$MAIN_LOG_FILE"

# Create the virtual environment if it does not exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "Virtual environment created at $(date)" | tee -a "$MAIN_LOG_FILE"
else
  echo "Virtual environment already exists at $(date)" | tee -a "$MAIN_LOG_FILE"
fi

# Activate the virtual environment
source venv/bin/activate || { echo "Failed to activate virtual environment at $(date)" | tee -a "$MAIN_LOG_FILE"; exit 1; }
echo "Virtual environment activated at $(date)" | tee -a "$MAIN_LOG_FILE"

# Log the start of dependency installation
echo "Starting to install dependencies at $(date)" | tee -a "$MAIN_LOG_FILE"
# Install the dependencies and display the output in real-time
pip install -r requirements.txt
# Log the completion of dependency installation
echo "Finished installing dependencies at $(date)" | tee -a "$MAIN_LOG_FILE"

# Navigate to the Scrapy project directory
if [ -d "workscrapper/workscrapper" ]; then
  cd workscrapper/workscrapper || { echo "Failed to change directory to workscrapper/workscrapper at $(date)" | tee -a "$MAIN_LOG_FILE"; exit 1; }
  echo "Changed directory to workscrapper/workscrapper at $(date)" | tee -a "$MAIN_LOG_FILE"
else
  echo "Directory workscrapper/workscrapper not found at $(date)" | tee -a "$MAIN_LOG_FILE"
  exit 1
fi

echo $(pwd) >> "$MAIN_LOG_FILE" 2>&1
# Run the Scrapy spiders in parallel and log output in real time
echo "Running Scrapy spiders at $(date)" | tee -a "$MAIN_LOG_FILE"
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

echo "Scrapy spiders completed at $(date)" | tee -a "$MAIN_LOG_FILE"

# Navigate back to the parent project directory
cd "$PROJECT_DIR" || { echo "Failed to change directory to $PROJECT_DIR at $(date)" | tee -a "$MAIN_LOG_FILE"; exit 1; }
echo "Changed directory back to $PROJECT_DIR at $(date)" | tee -a "$MAIN_LOG_FILE"

# Run the preprocess script
python3 preprocess.py >> "$MAIN_LOG_FILE" 2>&1
echo "Preprocessing completed at $(date)" | tee -a "$MAIN_LOG_FILE"

# Move the script back to the root directory if needed
if [ -f "argos-translate/translate.py" ]; then
  mv argos-translate/translate.py .
  echo "Script moved back to root directory at $(date)" | tee -a "$MAIN_LOG_FILE"
else
  echo "Script not found in repository to move at $(date)" | tee -a "$MAIN_LOG_FILE"
fi

# Send email with the main logs before starting the bot

python3 send_mail.py --subject "Daily Logs and Status - $TODAYS_DATE" --body "Program logs attached." --to "$EMAIL" --attachment "$MAIN_LOG_FILE"
echo "Email with main logs sent at $(date)" | tee -a "$MAIN_LOG_FILE"

# Start the bot script
"$PROJECT_DIR/control_bot.sh" >> "$BOT_LOG_FILE" 2>&1
echo "Bot script started at $(date)" | tee -a "$MAIN_LOG_FILE"

# Log end time
echo "Script ended at $(date)" | tee -a "$MAIN_LOG_FILE"
#!/bin/bash

# Define absolute paths
LOG_DIR="/Users/ivanivsnov/Work-Analysis/logs"
MAIN_LOG_FILE="$LOG_DIR/main.log"
BOT_LOG_FILE="$LOG_DIR/bot.log"
ZIP_FILE="/tmp/logs.zip"
EMAIL="makararena@gmail.com"
CRON_PATTERN="57 15 * * * ~/Work-Analysis/main.sh"

# Ensure that the script exits on any error
set -e

# Create the logs directory if it does not exist
mkdir -p "$LOG_DIR"

# Create empty log files if they do not exist
touch "$MAIN_LOG_FILE"
touch "$BOT_LOG_FILE"

# Delete all previous logs
rm -f "$MAIN_LOG_FILE" "$BOT_LOG_FILE"

# Log start time
echo "Cron job started at $(date)" >> "$MAIN_LOG_FILE"

# Exclude the current cron job pattern
crontab -l | grep -v "$CRON_PATTERN" | crontab -  >> "$MAIN_LOG_FILE"

# Navigate to the project directory
cd ~/Work-Analysis 

# Create the virtual environment if it does not exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate  >> "$MAIN_LOG_FILE"

# Install the dependencies
pip install -r requirements.txt  >> "$MAIN_LOG_FILE"

# Clone the repository if it does not exist
if [ ! -d "argos-translate" ]; then
  git clone https://github.com/argosopentech/argos-translate.git
fi

# Move the script into the cloned repository if it doesn't already exist there
if [ ! -f "argos-translate/translate.py" ]; then
  mv translate.py argos-translate/
fi

# Navigate to the Scrapy project directory
if [ -d "workscrapper/workscrapper" ]; then
  cd workscrapper/workscrapper
else
  echo "Directory workscrapper/workscrapper not found" >> "$MAIN_LOG_FILE"
  exit 1
fi

# Run the Scrapy spiders and log output in real time
echo "Running Scrapy spiders at $(date)"  >> "$MAIN_LOG_FILE"
# scrapy crawl pracuj_pl_spider  >> "$MAIN_LOG_FILE"
# scrapy crawl theprotocol_spider  >> "$MAIN_LOG_FILE"
# scrapy crawl buldogjob_spider  >> "$MAIN_LOG_FILE"

# Navigate back to the parent project directory
cd ../..

# Run the preprocess script
python3 preprocess.py >> "$MAIN_LOG_FILE" 2>&1

# Move the script back to the root directory if needed
mv argos-translate/translate.py .

# Send email with the main logs before starting the bot
python3 send_mail.py --subject "Daily Logs and Status" --body "Program logs attached." --to "$EMAIL" --attachment "$MAIN_LOG_FILE"
echo "Email with main logs sent at $(date)" >> "$MAIN_LOG_FILE"

# Run the bot control script
~/Work-Analysis/control_bot.sh

# Create a ZIP of the logs directory
zip -r "$ZIP_FILE" "$LOG_DIR" >> "$MAIN_LOG_FILE" 2>&1
echo "ZIP created at $(date)" >> "$MAIN_LOG_FILE"

# Send the email with the ZIP file attached
python3 send_mail.py --subject "Daily Logs and Status" --body "Task completed. Logs attached." --to "$EMAIL" --attachment "$ZIP_FILE"
echo "Email with ZIP sent at $(date)" >> "$MAIN_LOG_FILE"

# Log end time
echo "Cron job ended at $(date)" >> "$MAIN_LOG_FILE"
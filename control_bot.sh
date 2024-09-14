#!/bin/bash

# Define paths
PROJECT_DIR="$(pwd)"
LOG_DIR="$PROJECT_DIR/logs"
BOT_LOG_FILE="$LOG_DIR/bot.log"
EMAIL="makararena@gmail.com"
PID_FILE="$LOG_DIR/bot.pid"
MAIN_LOG_FILE="$LOG_DIR/main.log"
TODAYS_DATE=$(date +"%Y-%m-%d_%H-%M-%S")

# Ensure the log directory exists
mkdir -p "$LOG_DIR"

# Function to log messages with timestamps
log_message() {
  local message="$1"
  echo "$message at $(date)" | tee -a "$MAIN_LOG_FILE"
}

# Function to start the bot
start_bot() {
  log_message "Starting bot and generating figures"
  cd "$PROJECT_DIR/bot" || { log_message "Failed to change directory to bot"; exit 1; }

  {
    python3 generate_figures.py
    python3 bot.py >> "$BOT_LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
  } >> "$BOT_LOG_FILE" 2>&1
  log_message "Bot started with PID $(cat "$PID_FILE")"
}

# Function to stop the bot
stop_bot() {
  if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 $PID 2>/dev/null; then
      log_message "Stopping bot with PID $PID"
      kill $PID
      wait $PID 2>/dev/null
      log_message "Bot stopped"
    else
      log_message "PID $PID is not running"
    fi
    rm "$PID_FILE"
  else
    log_message "PID file not found"
  fi
}

# Function to send bot logs via email
send_bot_logs() {
  log_message "Sending bot logs via email"
  cd "$PROJECT_DIR" || { log_message "Failed to change directory"; exit 1; }
  python3 send_mail.py --subject "Bot Logs - $TODAYS_DATE" \
                       --body "Bot logs attached." \
                       --to "$EMAIL" \
                       --attachment "$BOT_LOG_FILE"
  log_message "Email with bot logs sent"
}

# Log script start
log_message "Bot control script started"

# Stop any currently running bot
stop_bot

# Start the bot
start_bot

# Handle signals such as SIGINT (Ctrl+C) and SIGTERM to stop the bot and send logs
trap 'send_bot_logs; exit' SIGINT SIGTERM

# Wait for background processes
wait

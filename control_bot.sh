#!/bin/bash

# Define paths
LOG_DIR="$HOME/Work-Analysis/logs"
BOT_LOG_FILE="$LOG_DIR/bot.log"
EMAIL="makararena@gmail.com"
PID_FILE="/tmp/bot.pid"
MAIN_LOG_FILE="$LOG_DIR/main.log"

# Function to log messages with timestamps
log_message() {
  local message="$1"
  echo "$message at $(date)" | tee -a "$MAIN_LOG_FILE"
}

# Function to start the bot
start_bot() {
  log_message "Starting bot and generating figures" >> "$BOT_LOG_FILE"
  cd bot || { log_message "Failed to change directory to bot"; exit 1; }

  # Run generate_figures.py and bot.py
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
  cd .. || { log_message "Failed to change directory"; exit 1; }
  python3 send_mail.py --subject "Bot Logs" --body "Bot logs attached." --to "$EMAIL" --attachment "$BOT_LOG_FILE"
  log_message "Email with bot logs sent"
}

# Ensure the log directory exists
mkdir -p "$LOG_DIR"

# Log script start
log_message "Script started"

# Stop any currently running bot
stop_bot

# Start the bot
start_bot

# Ensure the bot is stopped when the script is interrupted
trap 'stop_bot; send_bot_logs' EXIT

# Keep the script running to handle interruptions
wait

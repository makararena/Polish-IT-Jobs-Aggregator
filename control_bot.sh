#!/bin/bash

# Define absolute paths
LOG_DIR="/Users/ivanivsnov/Work-Analysis/logs"
BOT_LOG_FILE="$LOG_DIR/bot.log"
EMAIL="makararena@gmail.com"
PID_FILE="/tmp/bot.pid"

# Function to start the bot
start_bot() {
  echo "Starting bot and generating figures at $(date)" >> "$BOT_LOG_FILE"
  cd bot 
  python3 generate_figures.py >> "$BOT_LOG_FILE" 2>&1
  python3 bot.py >> "$BOT_LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
}

# Function to stop the bot
stop_bot() {
  if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 $PID 2>/dev/null; then
      echo "Stopping bot with PID $PID at $(date)" >> "$BOT_LOG_FILE"
      kill $PID
      wait $PID 2>/dev/null
    fi
    rm "$PID_FILE"
  fi
}

# Function to send bot logs via email
send_bot_logs() {
  cd .. 
  python3 send_mail.py --subject "Bot Logs" --body "Bot logs attached." --to "$EMAIL" --attachment "$BOT_LOG_FILE"
  echo "Email with bot logs sent at $(date)" >> "$LOG_DIR/main.log"
}

# Stop any currently running bot
stop_bot

# Start the bot
start_bot

# Ensure the bot is stopped when the script is interrupted
trap 'stop_bot; send_bot_logs' EXIT

# Keep the script running to handle interruptions
wait
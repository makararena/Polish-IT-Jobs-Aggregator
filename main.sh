#!/bin/bash

# Ensure that the script exits on any error
set -e

# Navigate to the project directory
cd ~/Work-Analysis

# Create the virtual environment if it does not exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

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
  echo "Directory workscrapper/workscrapper not found"
  exit 1
fi

# Run the Scrapy spiders
scrapy crawl pracuj_pl_spider
scrapy crawl theprotocol_spider
scrapy crawl buldogjob_spider

# Navigate to the parent project directory
cd ../..

# Run the preprocess script
python3 preprocess.py

# Move the script back to the root directory if needed
mv argos-translate/translate.py .

cd ./Bot

python3 generate_figures.py
python3 bot.py >> ~/Work-Analysis/Bot/bot.log 2>&1


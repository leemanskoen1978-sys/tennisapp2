#!/bin/bash
# Cron script: draai op de 1e van elke maand om 6u 's ochtends
# Voeg toe aan crontab: 0 6 1 * * /pad/naar/Webscraping/schedule_tennis_scraper.sh

cd "$(dirname "$0")"
source venv_tennis/bin/activate
python run_tennis_scraper.py --cron >> tennis_scraper.log 2>&1

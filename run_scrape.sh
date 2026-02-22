#!/bin/bash
# Run de tennis scraper met alle opgeslagen credentials.
# Laadt .env voor Google Calendar, rest staat in versleutelde bestanden.

cd "$(dirname "$0")"
source venv_tennis/bin/activate

if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

python run_tennis_scraper.py --scrape

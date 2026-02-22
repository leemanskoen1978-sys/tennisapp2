#!/bin/bash
# Start de Tennis lessen scraper (activeert venv automatisch)
cd "$(dirname "$0")"
source venv_tennis/bin/activate
python run_tennis_scraper.py "$@"

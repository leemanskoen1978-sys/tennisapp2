#!/bin/bash
# Sla alle credentials op (eenmalig).
# Vraagt om: Tennis login, Gmail wachtwoord, Google Calendar IDs.

cd "$(dirname "$0")"
source venv_tennis/bin/activate
python setup_all_credentials.py

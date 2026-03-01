#!/bin/bash
cd "$(dirname "$0")"
../venv_tennis/bin/python calendar_importer.py "$@"

#!/bin/bash
# Laadt Google Calendar credentials in de huidige shell.
# Gebruik: source load_google_creds.sh
# Of:     . load_google_creds.sh

cd "$(dirname "$0")"

ENV_FILE=".env"

if [ -f "$ENV_FILE" ] && grep -q "GOOGLE_CLIENT_ID" "$ENV_FILE" 2>/dev/null; then
    echo "Laadt credentials uit .env..."
    set -a
    # .env gebruikt KEY=value (geen export) - set -a exporteert ze
    source "$ENV_FILE"
    set +a
    echo "Google credentials geladen."
else
    echo "Google Calendar credentials instellen (eenmalig)"
    echo "-----------------------------------------------"
    read -p "GOOGLE_CLIENT_ID: " GOOGLE_CLIENT_ID
    read -p "GOOGLE_CLIENT_SECRET: " GOOGLE_CLIENT_SECRET
    read -p "GOOGLE_REFRESH_TOKEN: " GOOGLE_REFRESH_TOKEN

    if [ -n "$GOOGLE_CLIENT_ID" ] && [ -n "$GOOGLE_CLIENT_SECRET" ] && [ -n "$GOOGLE_REFRESH_TOKEN" ]; then
        cat > "$ENV_FILE" << EOF
export GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID"
export GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET"
export GOOGLE_REFRESH_TOKEN="$GOOGLE_REFRESH_TOKEN"
EOF
        chmod 600 "$ENV_FILE"
        export GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET GOOGLE_REFRESH_TOKEN
        echo ""
        echo "Opgeslagen in .env. Volgende keer worden ze automatisch geladen."
    else
        echo "Fout: alle drie de velden zijn verplicht."
        return 1 2>/dev/null || exit 1
    fi
fi

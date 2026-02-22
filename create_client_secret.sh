#!/bin/bash
# Maakt client_secret.json aan voor Google Calendar OAuth

cd "$(dirname "$0")"

echo "Google Calendar - client_secret.json aanmaken"
echo "---------------------------------------------"
echo ""
read -p "Client ID (bijv. xxx.apps.googleusercontent.com): " CLIENT_ID
read -p "Client Secret (bijv. GOCSPX-xxx): " CLIENT_SECRET

if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    echo "Fout: beide velden zijn verplicht."
    exit 1
fi

cat > client_secret.json << EOF
{
  "installed": {
    "client_id": "$CLIENT_ID",
    "client_secret": "$CLIENT_SECRET",
    "redirect_uris": ["http://localhost"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
EOF

echo ""
echo "client_secret.json is aangemaakt."
echo "Run nu: python setup_google_calendar.py"

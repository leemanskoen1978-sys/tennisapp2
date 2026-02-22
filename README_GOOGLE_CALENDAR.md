# Google Calendar – privé lessen toevoegen

Om privé lessen uit je Google Calendar in het Excel-bestand te krijgen.

**→ Zie [README_GOOGLE_CALENDAR_KOMPLEET.md](README_GOOGLE_CALENDAR_KOMPLEET.md) voor een stapsgewijze handleiding van A tot Z.**

Korte samenvatting:

## 1. Google Cloud Console

1. Ga naar [console.cloud.google.com](https://console.cloud.google.com/)
2. Maak een nieuw project (of kies bestaand)
3. Zoek **"Google Calendar API"** → **Enable**
4. Ga naar **APIs & Services** → **Credentials**
5. **Create Credentials** → **OAuth client ID**
6. Configureer het **OAuth consent screen** als dat nog niet gedaan is (Internal of External)
7. **Application type:** Desktop app
8. Klik **Create** → **Download** (rechter muisknop op de client → Download JSON)
9. Hernoem het bestand naar `client_secret.json`
10. Plaats het in de map `Webscraping/`

## 2. Setup-script uitvoeren

```bash
cd "/Users/leko/Downloads/Cursor februari/Webscraping"
source venv_tennis/bin/activate
python setup_google_calendar.py
```

Er opent een browser. Log in met leemanskoen1978@gmail.com en geef toegang. Het script toont daarna drie regels die je nodig hebt.

## 3. Lokaal: environment variables zetten

Voor elke scrape-sessie (of permanent in je shell config):

```bash
export GOOGLE_CLIENT_ID="jouw-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="jouw-client-secret"
export GOOGLE_REFRESH_TOKEN="1//..."
```

Of maak een bestand `.env` in Webscraping/ met:

```
GOOGLE_CLIENT_ID=jouw-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=jouw-client-secret
GOOGLE_REFRESH_TOKEN=1//...
```

En run vóór de scrape:

```bash
set -a; source .env; set +a
python run_tennis_scraper.py --scrape
```

## 4. GitHub Actions

Voeg de drie waarden toe als **Secrets** in je repo: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`.

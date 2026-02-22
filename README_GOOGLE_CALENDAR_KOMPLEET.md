# Google Calendar API – Complete setup van A tot Z

Stapsgewijze handleiding om de credentials opnieuw aan te maken.

---

## Deel 1: Google Cloud Console

### Stap 1.1 – Project aanmaken

1. Ga naar [console.cloud.google.com](https://console.cloud.google.com/)
2. Klik linksboven op het **projectdropdown** (naast "Google Cloud")
3. Klik op **Nieuw project**
4. Naam: bijv. `tennis-scraper` (of kies een bestaand project)
5. Klik **Maken**
6. Wacht tot het project klaar is en selecteer het

---

### Stap 1.2 – Google Calendar API inschakelen

1. Zoek in de zoekbalk: **Google Calendar API**
2. Klik op **Google Calendar API**
3. Klik op **Inschakelen** / **Enable**
4. Wacht tot het bevestigd is

---

### Stap 1.3 – OAuth consent screen (External)

1. Zoek in de zoekbalk: **OAuth consent screen** of ga naar [console.cloud.google.com/apis/credentials/consent](https://console.cloud.google.com/apis/credentials/consent)
2. Kies **External** (voor je eigen Gmail-account)
3. Klik **Maken** / **Create**
4. **App-informatie:**
   - Appnaam: `Tennis Scraper`
   - User support e-mail: jouw e-mail (leemanskoen1978@gmail.com)
   - Developer contact: zelfde e-mail
5. Klik **Opslaan en doorgaan**
6. **Scopes:**
   - Klik **Toevoegen of scopes verwijderen**
   - Zoek `calendar.readonly`
   - Vink **.../auth/calendar.readonly** aan
   - Klik **Bijwerken** → **Opslaan en doorgaan**
7. **Testgebruikers:**
   - Klik **+ Toevoegen**
   - Voer in: `leemanskoen1978@gmail.com`
   - Klik **Opslaan en doorgaan**
8. Klik **Terug naar dashbord** / **Back to dashboard**

---

### Stap 1.4 – OAuth 2.0 Client ID aanmaken

1. Ga naar **Credentials** (APIs & Services → Credentials)  
   of [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
2. Klik **+ Create credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Naam: `Tennis Scraper`
5. Klik **Create** / **Maken**
6. Er verschijnt een popup met **Client ID** en **Client secret**
7. **Belangrijk:** kopieer beide meteen (je kunt het secret daarna niet meer zien)
8. Klik **Download JSON** (rechtermuisknop op de client → Download) – of noteer de waarden handmatig

---

## Deel 2: Lokaal bestand aanmaken

### Stap 2.1 – client_secret.json

1. Open een teksteditor en maak een nieuw bestand
2. Plak dit (vervang de waarden):

```json
{
  "installed": {
    "client_id": "JOUW-CLIENT-ID.apps.googleusercontent.com",
    "client_secret": "JOUW-CLIENT-SECRET",
    "redirect_uris": ["http://localhost"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

3. Vervang:
   - `JOUW-CLIENT-ID` → het eerste deel van je Client ID (bijv. `123456789-abc...`)
   - `JOUW-CLIENT-SECRET` → je volledige Client secret (bijv. `GOCSPX-xxxx`)

4. Sla op als: `/Users/leko/Downloads/Cursor februari/Webscraping/client_secret.json`

**Of gebruik het script:**
```bash
cd "/Users/leko/Downloads/Cursor februari/Webscraping"
./create_client_secret.sh
```
Voer Client ID en Client secret in wanneer gevraagd.

---

## Deel 3: Refresh token verkrijgen

### Stap 3.1 – Setup-script draaien

1. Open Terminal
2. Voer uit:

```bash
cd "/Users/leko/Downloads/Cursor februari/Webscraping"
source venv_tennis/bin/activate
python setup_google_calendar.py
```

3. Er opent een browservenster
4. Log in met **leemanskoen1978@gmail.com**
5. Klik **Doorgaan** / **Continue** bij de waarschuwing (Testing app)
6. Geef toegang als dat gevraagd wordt
7. De browser kan een “Connection closed” melding tonen – dat is normaal

### Stap 3.2 – Waarden opslaan

In de terminal verschijnt iets zoals:

```
GOOGLE_CLIENT_ID="123456789-xxx.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="GOCSPX-xxxx"
GOOGLE_REFRESH_TOKEN="1//0gXXXXXXXXxxxx"
```

Kopieer alle drie en bewaar ze (bijv. in een notitie – alleen jij hebt ze nodig).

---

## Deel 4: Credentials opslaan in de scraper

### Stap 4.1 – setup_credentials.sh

```bash
cd "/Users/leko/Downloads/Cursor februari/Webscraping"
./setup_credentials.sh
```

Vul in:
- Tennis login (indien nog niet gedaan)
- Gmail wachtwoord (indien nog niet gedaan)
- **GOOGLE_CLIENT_ID:** plak de volledige waarde
- **GOOGLE_CLIENT_SECRET:** plak de volledige waarde
- **GOOGLE_REFRESH_TOKEN:** plak de volledige waarde (begint vaak met `1//`)

---

## Deel 5: Testen

```bash
./run_scrape.sh
```

De scraper zou nu ook privélessen uit Google Calendar moeten ophalen en in het blad `lessen_privaat` schrijven.

---

## Probleemoplossing

| Fout | Oplossing |
|------|-----------|
| `org_internal` | OAuth consent screen op **External** zetten |
| `access_denied` | Je e-mail als **Test user** toevoegen |
| `deleted_client` | Nieuwe OAuth-client aanmaken, nieuw Client secret |
| `invalid_client` | Client ID en Client secret controleren |
| `invalid_grant` | Nieuwe refresh token ophalen met `python setup_google_calendar.py` |
| Geen refresh token | `client_secret.json` controleren en setup-script opnieuw draaien |

---

## Overzicht bestanden

| Bestand | Doel |
|---------|------|
| `client_secret.json` | OAuth Client ID + secret (na setup_google_calendar één keer nodig) |
| `.env` | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` |

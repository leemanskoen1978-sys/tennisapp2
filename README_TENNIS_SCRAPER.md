# Tennis en Padel Vlaanderen - Lessen Scraper

Scrapt je gegeven lessen van de Tennis Vlaanderen academy-pagina en schrijft ze naar Excel.

## Installatie

```bash
cd Webscraping
python3 -m venv venv_tennis
source venv_tennis/bin/activate
pip install -r tennis_lessen_scraper/requirements.txt
playwright install chromium
```

## Eerste keer gebruik

### 0. Alle credentials opslaan (aanbevolen)
```bash
./setup_credentials.sh
```
Vraagt om: Tennis login, Gmail wachtwoord, Google Calendar Client ID/Secret/Refresh token. Daarna hoeft u niets meer in te voeren.

### 1. Inloggegevens opslaan (indien niet via 0)
```bash
source venv_tennis/bin/activate
python run_tennis_scraper.py --setup
```
De gegevens worden **versleuteld** opgeslagen in `tennis_lessen_scraper/credentials.enc`.

### 2. E-mail (optioneel)
Bij het versturen wordt je Gmail wachtwoord gevraagd (leemanskoen1978@gmail.com). Gebruik een [app-wachtwoord](https://myaccount.google.com/apppasswords) als je 2FA hebt.

### 3. Lessen ophalen
```bash
./run_scrape.sh
```
Of handmatig: `python run_tennis_scraper.py --scrape` (laad eerst `.env` voor Google Calendar: `source .env`)

Met zichtbare browser (aanbevolen eerste keer):
```bash
python run_tennis_scraper.py --scrape --visible
```

## Output

- **Excel**: `/Users/leko/Documents/Python/origineel factuur.xlsm`
- **Tabblad**: `lessen_data`
- **Kolommen**: Club, Aanbod, Doelgroep, Groep, Dag + uur, Trainer, Aanwezigh., Uur/locatie gewijzigd?, Status, Bedrag

De datumrange is steeds **de vorige maand** (1e t/m laatste dag).

## Automatisch draaien (1e van de maand)

```bash
chmod +x schedule_tennis_scraper.sh
crontab -e
# Voeg toe: 0 6 1 * * /pad/naar/Webscraping/schedule_tennis_scraper.sh
```

## Overige opties

- `--clear-credentials` : Verwijder opgeslagen inloggegevens
- `--start-date DD-MM-YYYY` : Startdatum
- `--end-date DD-MM-YYYY` : Einddatum

## Configuratie

In `tennis_lessen_scraper/config.py`:
- `TRAINER_ID`: trainer-ID (standaard 639541)
- `STATUS_ID`: filter op lesstatus (5 = afgewerkt)
- `EXCEL_OUTPUT`: pad naar Excel-bestand

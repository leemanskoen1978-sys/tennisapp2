# Racso calendar-export (automatisch)

Exporteert elke maand racso-events uit de kalender **Family** naar een .xls-bestand.

## Wat het doet (zonder keuzes)

- **Kalender:** altijd Family  
- **Periode:** vorige kalendermaand (1e t/m laatste dag)  
- **Export:** altijd .xls in deze map  
- Geen vragen, volledig automatisch

## Handmatig draaien

```bash
cd "/Users/leko/Downloads/Cursor februari/projects/Webscraping/racso_calendar_export"
../venv_tennis/bin/python calendar_importer.py
```

Het .xls-bestand komt in dezelfde map als `calendar_importer.py`.

## Automatisch: 1e van elke maand om 07:00

1. Plist kopiëren naar LaunchAgents:
   ```bash
   cp "/Users/leko/Downloads/Cursor februari/projects/Webscraping/racso_calendar_export/be.racso.calendar-export.plist" ~/Library/LaunchAgents/
   ```

2. Taak laden:
   ```bash
   launchctl load ~/Library/LaunchAgents/be.racso.calendar-export.plist
   ```

3. Controleren of hij geladen is:
   ```bash
   launchctl list | grep racso
   ```

Logs staan in `/tmp/racso-export.log` en `/tmp/racso-export.err`.

**Stoppen:** `launchctl unload ~/Library/LaunchAgents/be.racso.calendar-export.plist`

**Let op:** Calendar moet toegang hebben (Systeemvoorkeuren > Privacy & beveiliging > Automatisering). Zorg dat xlwt geïnstalleerd is in venv_tennis: `pip install xlwt`

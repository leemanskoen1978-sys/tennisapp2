# Tennis Scraper op GitHub – draait zonder je PC

Met GitHub Actions draait de scraper **in de cloud** op de 1e van elke maand. Je computer hoeft niet aan te staan.

## Stap 1: Code op GitHub zetten

1. Ga naar [github.com/new](https://github.com/new)
2. Maak een **private** repository aan (bijv. `tennisapp2`)
3. Push de code:

```bash
cd Webscraping
git init
git add .
git commit -m "Tennis lessen scraper"
git branch -M main
git remote add origin https://github.com/leemanskoen1978-sys/tennisapp2.git
git push -u origin main
```

## Stap 2: Secrets instellen

1. Ga naar **Settings** → **Secrets and variables** → **Actions**
2. Voeg toe (alle vereist voor volledige werking):

| Secret naam            | Waarde |
|------------------------|--------|
| `TENNIS_USERNAME`      | Lidnummer of e-mail van Tennis Vlaanderen |
| `TENNIS_PASSWORD`      | Wachtwoord van Tennis Vlaanderen |
| `EMAIL_PASSWORD`       | App-wachtwoord van leemanskoen1978@gmail.com |
| `GOOGLE_CLIENT_ID`     | Uit `setup_google_calendar.py` (bijv. xxx.apps.googleusercontent.com) |
| `GOOGLE_CLIENT_SECRET` | Uit `setup_google_calendar.py` |
| `GOOGLE_REFRESH_TOKEN` | Uit `setup_google_calendar.py` |

## Werking

- **Schema:** Elke 1e van de maand om 6:00 UTC
- **Handmatig:** Repo → **Actions** → **Tennis Lessen Scraper** → **Run workflow**
- **Resultaat:** Excel wordt per e-mail naar leemanskoen1978@gmail.com gestuurd

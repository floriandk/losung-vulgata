# Losung & Vulgata

Täglich neu gebaute Seite (GitHub Pages): Losung und Lehrtext des Tages, zuerst der
Vulgata-Text, per Klick auf „Deutsch anzeigen“ der deutsche Wortlaut. Läuft auf dem Handy im Browser.

## Einrichten
1. Neues GitHub-Repo anlegen, diesen Ordnerinhalt hochladen (Branch `main`).
2. **Settings → Pages → Source: GitHub Actions**.
3. **Settings → Secrets and variables → Actions → Variables** → neue Variable `LOSUNGEN_URL`:
   Direktlink auf die ZIP-Datei „Losungen Free (XML)“ des aktuellen Jahres. Den Link findest du
   auf der Download-Seite von losungen.de (Link-Adresse der XML-Datei kopieren).
4. **Actions → „Losung des Tages“ → Run workflow**. Danach baut sich die Seite jeden Morgen selbst.
   Die Adresse (`https://<name>.github.io/<repo>/`) legst du auf dem Handy als Lesezeichen
   oder Home-Bildschirm-Verknüpfung ab.

## Vulgata-Daten
`data/vulgata.json` enthält nur zwei Beispielverse. Ersetze die Datei durch eine vollständige,
gemeinfreie Vulgata (Clementina) im Format `{"Buch": {"Kapitel": {"Vers": "Text"}}}`
mit englischen Buchnamen als Schlüsseln (`Genesis`, `1 Samuel`, `Psalms`, `Song of Solomon` …,
siehe `BOOKS` in `build.py`).

Psalmen: Die Losungen nutzen die hebräische Zählung, die Vulgata die griechische.
`build.py` rechnet die Kapitel um; einzelne Verse können bei Psalmen mit Überschrift
um 1–2 abweichen.

## Lokal testen
`DATE=2026-11-08 python build.py --xml pfad/zur/Losungen.xml` → `docs/index.html`

## Hinweise
- **Urheberrecht:** Die Losungstexte gehören der Herrnhuter Brüdergemeine; lies deren
  Nutzungsbedingungen auf der Download-Seite. Eine öffentliche Seite mit dem deutschen Wortlaut
  ist nicht automatisch erlaubt. Prüfe das oder frag bei losungen@ebu.de nach.
- GitHub pausiert geplante Workflows in öffentlichen Repos nach 60 Tagen ohne Aktivität;
  dann einmal „Run workflow“ klicken.

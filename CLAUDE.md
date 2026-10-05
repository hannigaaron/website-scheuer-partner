# Scheuer & Partner mbB — Website (Entwurf)

Statische Mehrseiten-Website für die Steuerberatungsgesellschaft Scheuer &
Partner mbB, Bietigheim-Bissingen. Kundenauftrag von Aaron Hannig.
Gleiches Designsystem wie personalcoachaaron.de (Repo
`hannigaaron/website-aaron-hannig`), anderes Gesicht: die drei senkrechten
Balken aus dem Kanzlei-Logo ersetzen die Dreiecke als Zeichen.

## Aufbau
- `tools/build.py` erzeugt alle `*.html` aus gemeinsamen Bausteinen.
  **HTML nie von Hand ändern, sondern in `build.py` und neu bauen:**
  `python3 tools/build.py`. Das Ergebnis wird mitcommittet, auf dem Server
  läuft kein Build.
- `styles.css`, `script.js`: ein Stylesheet, ein Skript für alle Seiten.
- `vendor/` GSAP, ScrollTrigger, Lenis. `fonts/` Archivo, Instrument Sans. Beides lokal.
- `tools/source/` Originaltexte und gesammelte Links der bisherigen Seite.
- Lokal prüfen: `python3 -m http.server 8000`

## Verbindliche Regeln
### Mobil zuerst
Geprüft wird auf Handy 390/430 px, iPad 768 hoch und 1024 quer, Desktop 1440.
- Kein horizontales Scrollen, keine Schrift unter 12 px.
- Antippziele mindestens 44 × 44 px (`@media (pointer:coarse)`).
- **Kein Text überlagert anderen Text**, auch nicht kurz in einer Animation.
  Der Zoom der Überschriften reserviert seinen Platz vorher (`.head-box`).
- Das Menü ist unter 980 px ein Vollbild-Menü. `.nav.is-open` schaltet
  `backdrop-filter` ab, sonst sperrt es das fixierte Menü im Balken ein.

### Inhalt
- **Alle Texte im Wortlaut der bisherigen Seite**, Anrede „Sie".
  Keine erfundenen Kundenstimmen, Zahlen oder Namen. Zahlen nur, wenn sie
  auf der alten Seite stehen (1961, über 60 Jahre, rund 30 Personen, 4 Bereiche).
- Keine Teamfotos vorhanden: Monogramme statt Fotos, bis echte Bilder kommen.
- Werbung muss sachlich bleiben (Berufsrecht Steuerberater). Keine Superlative.

### Farben
Wie bei Aaron: `--blue #93ddf4`, `--blue-deep #10708d`, `--ink #2e2e2e`,
`--ink-mid #585858`. Das grüne Logo steht nur als Bilddatei.

### Bilder
Alle unter `img/`. Die Fotos stammen von der bisherigen Kanzleiseite
(Stockfotos und Enzviadukt/Altstadt Bietigheim). Die Kanzlei hat die Nutzung
mündlich erlaubt. **Offen:** schriftliche Bestätigung und Lizenz der Stockfotos.
Jedes Foto bekommt eine andere Behandlung (`.media-a`, `.media-b`, `.media-c`).

### Datenschutz
Beim Aufruf geht **keine Anfrage an Dritte** hinaus. Externe Ziele
(Online-Portal, Rechner, Karten, News der alten Seite) sind nur Links, die
in einem neuen Tab öffnen. Neue externe Ressource: lokal ablegen oder hinter einen Klick.

### Animationen
Ohne GSAP und Lenis bleibt die Seite voll lesbar. `prefers-reduced-motion`
schaltet alles ab. Ruhende Zustände gehören ins CSS, animierte ins Skript.
Der Auftakt (fünf Lamellen) läuft nur auf der Startseite, einmal pro Tab.

## Vor dem Livegang
- `noindex` steht in jedem `<head>` und in `robots.txt` (Entwurf). **Beides entfernen**, plus `canonical`, `og:url`, `og:image`, `sitemap.xml` ergänzen.
- Gelb markierte `<span class="todo">` in Impressum und Datenschutz klären (Entwurf und Umsetzung der Webseite, Datenschutztext passend zur neuen Seite).
- **Abhängigkeiten von der bisherigen Seite (atikon):** Online-Rechner,
  FAQ- und Lexikonseiten, Steuernews, Steuernews-TV, Infovideos, Downloads,
  Newsletter- und Bewerbungsformular. Aktuell verlinken diese auf die alte
  Domain bzw. `rechner.atikon.de`. Zieht die Domain um, brechen diese Links,
  falls der atikon-Vertrag endet. Mit der Kanzlei klären, ob der Dienst bleibt oder ersetzt wird.
- Newsletter und Bewerbung laufen aktuell über `mailto:`. Ersatz: Formular mit Double-Opt-In.
- Der Skonto-Rechner auf der Startseite ist eine eigene Beispielrechnung (Formel: Skonto / (100 − Skonto) × 360 / (Ziel − Frist)). Mit der Kanzlei abstimmen.
- Teamfotos, Vektor-Logo (SVG), endgültige Domain.

## Wichtig: Arbeit sichern
Der Container ist flüchtig. Committen reicht nicht, es muss gepusht werden.

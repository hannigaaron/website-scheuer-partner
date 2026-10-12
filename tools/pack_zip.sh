#!/bin/sh
# Packt alles Fertige für die Kundin in EINE ZIP (ohne interne Unterlagen).
set -e
cd "$(dirname "$0")/.."
python3 tools/build.py >/dev/null && python3 tools/bundle.py
D=$(mktemp -d)/Scheuer-Partner-Entwurf
mkdir -p "$D/1 Website" "$D/2 Logo-Entwuerfe" "$D/3 Mockups"
cp Scheuer-Partner-Entwurf.html "$D/1 Website/Scheuer-Partner-Website.html"
cp design/Logo-Gesamtuebersicht-Scheuer-Partner.pdf "$D/2 Logo-Entwuerfe/"
cp -r design/logos/svg "$D/2 Logo-Entwuerfe/Runde 1 SVG"; cp -r design/logos/png "$D/2 Logo-Entwuerfe/Runde 1 PNG"
cp -r design/logos2/svg "$D/2 Logo-Entwuerfe/Runde 2 SVG"; cp -r design/logos2/png "$D/2 Logo-Entwuerfe/Runde 2 PNG"
cp design/mockups/Mockups-Scheuer-Partner.pdf design/mockups/mockup-*.png "$D/3 Mockups/"
cat > "$D/LIESMICH.txt" <<'T'
Scheuer & Partner mbB: Entwurfspaket

1 Website
  Scheuer-Partner-Website.html per Doppelklick im Browser öffnen. Läuft ohne Internet.
  Seitenwechsel über das Menü. Entwurf mit dem bisherigen Logo und den bisherigen Texten.

2 Logo-Entwuerfe
  Logo-Gesamtuebersicht-Scheuer-Partner.pdf zeigt alle 20 Entwürfe.
  Die Ordner enthalten jedes Logo als SVG (Vektor) und PNG (transparent)
  in Farbe, Negativ (für dunklen Grund), Schwarz und Weiß.
  Nummern 01 bis 10: Runde 1. Nummern 11 bis 20: Runde 2.

3 Mockups
  Briefbogen, Visitenkarte und Website-Kopf für die Logos 11, 13 und 19.
  Mockups-Scheuer-Partner.pdf (alle drei) und je Logo ein PNG.
  Texte in den Mockups sind Mustertexte. Adressdaten stammen aus dem bisherigen Impressum.

Alles ist ein Entwurf und noch nicht veröffentlicht.
T
rm -f Scheuer-Partner-Entwurf-Paket.zip
(cd "$(dirname "$D")" && zip -qr "$OLDPWD/Scheuer-Partner-Entwurf-Paket.zip" Scheuer-Partner-Entwurf)
ls -la Scheuer-Partner-Entwurf-Paket.zip

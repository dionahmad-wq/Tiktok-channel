# Stil-Leitfaden – Analyse der 3 Referenzvideos

Alle drei Videos: 1080×1920 (9:16), 60–90 s, **komplett per Code animiert** (kein KI-Videogenerator),
KI-Stimme (ElevenLabs) + Wort-für-Wort-Untertitel. Genau dieses Prinzip übernehmen wir.

---

## Referenz A – `kurzsimuliert` (475k Views, 68 s)
**„100 km/h ohne Pause gegen 160 km/h mit Stopps. Wer kommt wirklich zuerst an?“**

Das ist das direkte Vorbild für unsere Nische: **„Was passiert, wenn …?“-Simulationen auf Deutsch.**

**Visuell**
- 2D, flach, **Seitenansicht**. Nachthimmel (fast schwarz → dunkelviolett), Sterne, Mond, Stadtsilhouette, Straßenlaternen mit warmem Glow.
- Zwei Akteure mit fester Farbe: **A = Türkis (#3ED6C0)**, **B = Korallenrot (#FF5A4E)**; Buchstaben-Badge über dem Objekt.
- Akzentfarbe **Orange/Gelb (#FFB547)** für Pausen, Warnungen, Pointe.
- Datenschicht oben: Fortschrittsleiste START → ZIEL mit Punkten, Uhr (`ZEIT 0:15:04`), Live-Zähler (`VORSPRUNG B 14,9 km`).
- Kilometer-Lineal unten, Kamera folgt dem Geschehen; „ZEITRAFFER“-Badge bei Sprüngen.
- Infokarten (abgerundet, halbtransparent dunkel): Balkenvergleich, Pausen-Timer als Kreis, Rangliste.
- Schrift: fette, serifenlose Grotesk (Inter/Manrope-artig), große Zahlen, kleine Labels in VERSALIEN mit Sperrung.
- Untertitel: weiß, fett, klein, mittig **unter** der Szene, 2–4 Wörter pro Einblendung.

**Dramaturgie**
1. 0–3 s Hook: beide Autos + Frage „WER KOMMT ZUERST AN?“
2. Regeln erklären (Strecke 220 km, Pausenschema) mit Diagramm.
3. Simulation in Echtzeit/Zeitraffer, Zähler laufen, Führung wechselt mehrfach (Spannung!).
4. Knappes Finale: Zielzeiten-Tafel `2:12:00` vs `2:12:30`.
5. Erklärung der Mathe dahinter (Durchschnittsgeschwindigkeit 96 vs 100 km/h).
6. Punchline groß: **„EINE EINZIGE MINUTE.“**
- Musik: ruhiger Lo-Fi/Slowed-Track, leise unter der Stimme.

## Referenz B – `lumis.50` „Was wäre wenn?“ (Workflow-Tutorial, 92 s)
**Visuell:** dunkles Violett/Navy, Neon-Linie (Pfad) durch eine 3D-Szene, Glas-UI-Karten im
macOS-Fenster-Look (drei Punkte oben links, Titel „3 · PROJEKT“), Pill-Badge „SCHRITT 3 / 8“ +
Segment-Fortschrittsbalken, 3D-Icons über der Karte (Zahnrad, Palette, Equalizer).
Untertitel: weiß fett, **Schlüsselwort in Lila/Pink (#B16CFF / #E04CF0)**.
Ende: Speichern-Icon + Folgen-Button + „Teil 3“-Teaser → Serienbindung.

## Referenz C – `whatif.sim` (1,8 Mio Views, 63 s, Englisch)
3D-Voxel-Charakter (gelber Hoodie) + Box-Maskottchen, Blender/Three.js-Look, Navy-Gitterboden,
Bokeh-Lichter. Pill-Label oben („STEP 2 · SOURCES“, Keyword gelb). Untertitel **gelb/weiß mit
Schatten**, mittig im Bild. Starker Hook („6 views“ → „2.6 million views“), Zahlen zählen hoch, CTA „link in bio“.

---

## Gemeinsame Erfolgsformel (gilt für jedes unserer Videos)
| Element | Regel |
|---|---|
| Format | 1080×1920, 30 fps, 55–75 s |
| Hook | Frage oder Duell in den ersten **2 s**, als großer Text eingeblendet |
| Thema | Alltagsfrage mit **überraschender, zählbarer Antwort** („Wer gewinnt?“, „Was passiert, wenn …?“) |
| Visualisierung | Code-animiert, dunkler Hintergrund, 2–3 Signalfarben, echte Zahlen live hochzählend |
| Datenebene | Zähler, Uhren, Fortschrittsbalken, Diagramm-Karten – Zuschauer „sieht die Rechnung“ |
| Spannung | Führungswechsel / Wendepunkt in der Mitte |
| Auflösung | eine Zahl/ein Satz riesig als Punchline |
| Ton | KI-Stimme, sachlich-neugierig, kurze Sätze; Lo-Fi-Musik leise darunter |
| Untertitel | Wort-für-Wort-synchron, 2–4 Wörter, Keyword farbig |
| Outro | Frage an die Community („Was soll ich als Nächstes simulieren?“) |

## Technik-Pipeline (wie in Referenz B gezeigt)
Claude Code → Remotion-Projekt (React) → ElevenLabs-Stimme → Untertitel-Timing → Render (MP4).

---
name: tiktok-sim-video
description: Erstellt ein komplettes deutsches TikTok-Video im Stil „Was passiert, wenn …?“ / Simulation (Vorbild kurzsimuliert) – Thema, Recherche, Skript, deutsche KI-Stimme, wortgenaue Untertitel und code-animierte Simulation mit HyperFrames, gerendert als 1080×1920-MP4. Verwenden, wenn der Nutzer ein neues Video, eine neue Folge, ein Thema-Video oder eine Simulation für seinen TikTok-Kanal möchte.
---

# TikTok-Simulationsvideo (Deutsch, HyperFrames)

Du produzierst **allein und komplett im Code** ein fertiges Video für den Kanal. Immer **auf Deutsch**.
Look & Aufbau folgen `STYLE_GUIDE.md` im Repo-Root (Analyse der 3 Referenzvideos). Lies ihn zuerst.
Fertiges Beispiel zum Abschauen: `videos/001-tsunami/` (alle Szenentypen: Hook, Querschnitt, Rennen,
Vergleich, Lösung, Pointe, Outro).

## 0. Einrichtung (einmal pro Container)
```bash
bash .claude/skills/tiktok-sim-video/scripts/setup.sh
```
Installiert die deutsche Offline-Stimme „Thorsten“ (Piper) und die HyperFrames-CLI. Braucht Zugriff auf
github.com (Stimme) und npm/PyPI. Lies außerdem den `/hyperframes`-Skill (Render-Vertrag) bevor du Szenen schreibst.

## 1. Thema wählen
Ein gutes Thema hat **alle** diese Eigenschaften:
- betrifft viele Menschen (Natur, Körper, Weltall, Alltag, Katastrophen, Rekorde)
- lässt sich als **Duell** oder **Was-passiert-wenn** stellen („Kannst du X davonrennen?“, „100 km/h ohne Pause vs. 160 mit Stopps“)
- hat eine **zählbare Antwort**, die man live hochzählen kann (Zeit, Abstand, Tempo, Höhe)
- hat eine **Wendung** (Führungswechsel, überraschende Lösung, knappes Finale)
- endet mit **einer Zahl oder einem Satz** als Pointe („EINE EINZIGE MINUTE.“, „NICHT WEG. NACH OBEN.“)

Wenn der Nutzer kein Thema nennt: wähle selbst und sag in einem Satz, warum.

## 1b. Spannung – Pflicht für jedes Video
Jedes Video erfüllt **alle** Punkte (Vorbild: `videos/003-vakuum/`):
1. **Hook in 3 Sätzen (≤ 6 s):** *Du* + Lebensgefahr/Extrem + **Zeitlimit** + **offene Schleife**
   („Du hast 90 Sekunden. Und ein einziger Fehler tötet dich sofort.“). Bild 0 zeigt die Frage + die Zahl.
2. **Tickende Uhr:** ein durchgehender Timer/Countdown im HUD (eigene Komposition über alle Szenen per
   `"spans": {"hud": ["szeneA","szeneB"]}`), dazu ein schrumpfender Balken („Überlebensfenster“, „Abstand“).
3. **Zeitlupe / Zeitraffer** sichtbar machen (Badge `◀◀ ZEITLUPE` / `⏩ ZEITRAFFER`) – Zeit wird zum Drama.
4. **Re-Hook alle 8–12 s:** neue Phase mit Phasen-Pill, Wendung oder Mythos-Brecher („Aber du explodierst nicht.“).
5. **Fehler/Gefahr zeigen:** rote Alarm-Vignette (pulsiert mit `SIM.pulse`), Warn-Chip, `SIM.shake` bei Einschlägen.
6. **Knappes Finale:** Auflösung in letzter Sekunde, Restzeit nennen („Sechs Sekunden vor Schluss.“).
7. **Pointe = Handlung/Erkenntnis** in 1–2 Wörtern, riesig, mit Impact („AUSATMEN.“).
8. **Länge 45–60 s.** Lieber kürzer und dichter: alle 2–3 s eine neue visuelle Information.
9. **Sound ist Pflicht** (`sfx` in script.json, siehe Schritt 4b): Drone-Bett, Whoosh vor jedem
   Szenenwechsel, Impact auf Schlüsselwörtern, Herzschlag (schneller werdend) in kritischen Phasen,
   Riser in die Auflösung.
10. **Stimme:** `"fx": "dramatic"`, kurze Sätze, `speed` 1.05–1.2 auf Schlüsselsätzen, `pause` 0.5 vor Wendungen.

## 2. Fakten & Rechnung
Jede Zahl im Video muss stimmen. Rechne die Simulation selbst nach (Physik-Formeln, offizielle Werte)
und runde ehrlich („rund“, „knapp“, „bis zu“). Schreibe die Rechnung als Kommentar oben in die
Szenen-Datei und die Quellenlage in `videos/NNN-slug/POST.md`. Vereinfachungen im Outro benennen
(„Vereinfachtes Modell“); bei Sicherheitsthemen den echten Rat geben.

## 3. Projekt anlegen
```bash
cd videos && npx -y hyperframes@0.9.80 init NNN-slug --example blank && cd NNN-slug && rm -f AGENTS.md
cp ../../.claude/skills/tiktok-sim-video/assets/{sim.js,sim.css,gsap.min.js} assets/
```
`index.html` von `videos/001-tsunami/index.html` übernehmen (Nachthimmel, Sterne, Mond, Szenen-Hosts,
`#captions`, `<audio id="voice">`) und die Szenen-Hosts an die neuen Szenen anpassen
(Host-`id` = Szenenname = `data-composition-id` = Schlüssel in `window.__timelines`).

## 4. Skript → `script.json`
```json
{ "speed": 0.9, "lead_in": 0.25, "segments": [
  {"id": "h1", "scene": "hook", "text": "Kannst du einem *Tsunami* *davonrennen?*", "pause": 0.2},
  {"id": "b1", "scene": "bolt", "text": "Selbst *Usain* *Bolt* …", "say": "Selbst Jussein Bolt …"},
  {"id": "p1", "scene": "punch", "text": "Nicht weg. Nach oben.", "caption": false} ]}
```
- Kurze Sätze, gesprochene Sprache, **Zahlen als Wörter** („achthundert“), damit Stimme und Untertitel passen.
- Spannende Stimme: oben `"fx": "dramatic"` (tiefer, wuchtiger Erzähler mit Raum) und pro Satz `"speed"`
  (1.1–1.2 = langsamer für Schlüsselsätze wie „Dann: Dunkelheit.“), längere `pause` vor Wendungen.
- `*Wort*` = Untertitel-Hervorhebung (Amber). `say` = andere Aussprache, **gleiche Wortanzahl**.
  `caption: false`, wenn der Satz ohnehin groß im Bild steht (Pointe, Outro).
- Dramaturgie (55–75 s): Hook-Frage (≤3 s) → Regeln/Fakten → Simulation mit laufenden Zählern
  → Wendung → Auflösung → Pointe groß → Outro-Frage an die Community.

Dann Stimme + Timing:
```bash
S=../../.claude/skills/tiktok-sim-video/scripts
python3 $S/tts_de.py script.json assets   # → assets/voice.wav + voice-timing.json
python3 $S/sync_timing.py .               # → assets/timing.js, compositions/captions.html, Host-Zeiten in index.html
```
`sync_timing.py` nach **jeder** Skriptänderung erneut laufen lassen; Szenen-Längen folgen der Stimme.

### 4b. Sounddesign
In `index.html` im `#root` die Marker `<!-- SFX:BEGIN -->` / `<!-- SFX:END -->` setzen, in script.json
eine `"sfx"`-Liste anlegen (Format und Klänge: Kopf von `scripts/sfx.py`), dann:
```bash
python3 $S/sfx.py .        # erzeugt assets/sfx/*.wav und setzt die <audio>-Tags
```
Pegel-Richtwerte: Stimme `data-volume` 1.4, Drone 0.1 (≈ 12 dB unter Stimme), Herzschlag 0.75–0.85,
Impact 0.8–0.9, Whoosh 0.5, Riser 0.55. Nach dem Rendern messen (Ziel −14 LUFS, Spitze ≤ −1 dB) und in
einer Sprechpause prüfen, dass das Bett leiser ist als die Stimme. Die Klänge sind synthetisch und nur
gemessen, nicht gehört – das dem Nutzer so sagen.

## 5. Szenen schreiben (`compositions/<szene>.html`)
Muster (siehe `videos/001-tsunami/compositions/race.html`):
- Alles in `<template>`, Root `#root { position:absolute; inset:0 }`, IDs mit Szenen-Präfix.
- **Ein Treiber-Tween** steuert die Simulation deterministisch:
  `tl.to(S, {t: L, duration: L, ease: "none", onUpdate: draw}, 0)`; `draw()` berechnet alles aus `S.t`.
- Sprach-Anker statt fester Zeiten: `VT.seg("r4")`, `VT.seg("r4","end")`, `VT.word("r6", 6)` (Szenen-lokal),
  `VT.len("race")`. Sim-Zeit ↔ Video-Zeit per `SIM.keys([[t, wert, "out"], …], t)` (Zeitraffer).
- Bausteine aus `assets/sim.js`: `SIM.LandWorld` (Nachtstadt, Laternen, Strand, Meter-Lineal, Welle),
  `SIM.runner` (Läufer-Piktogramm mit A-Badge), `SIM.fmtInt/fmtDec/clock` (deutsche Zahlen), `SIM.rng` (Seed).
- HUD-Klassen aus `assets/sim.css`: `.ui-head/.ui-pill/.ui-segs` (Phase-Pill + Fortschritt), `.ui-card`,
  `.ui-label`, `.ui-big`, `.ui-bar.teal|coral|amber`, `.sim-tag`, `.ui-ff` (ZEITRAFFER).
- Elemente, die `draw()` per `style.transform` bewegt, **nie** zusätzlich mit GSAP animieren (überschreibt die Position).
  Statische Labels mit `left/top` positionieren, wenn GSAP sie einblendet.
- Kein `Math.random`, kein `Date.now`, keine Netzwerk-Requests.

### Layout-Raster (1080×1920)
| Zone | y (px) | Inhalt |
|---|---|---|
| Phase-Pill | 296–360 | „PHASE 2 · *DAS RENNEN*“ + 3 Segmente |
| Datenkarte | 396–700 | Zähler, Balken, Uhr |
| Welt | 700–1290 | Simulation, Boden bei y = 1200 |
| Untertitel | 1380–1450 | 2–3 Wörter, weiß, Keyword amber |
| frei | > 1500 | TikTok-Beschreibung/Buttons |

### Farben
A = Türkis `#3ED6C0` (Du/Held) · B = Korall `#FF5A4E` (Gegner/Gefahr) · Amber `#FFB547` (Pointe, Hervorhebung)
· Text `#F4F5FA` · Grau `#8A8FA8` · Hintergrund Nacht `#06070E` → `#1B1533`. Schrift: Inter 700/900.

## 6. Prüfen & Rendern
```bash
npx -y hyperframes@0.9.80 check --json      # muss ok: true sein (Fehler beheben, Warnungen abwägen)
npx -y hyperframes@0.9.80 snapshot --at 0,5,12,20,30,40,50,58 -o .snaps/x --no-end   # Bilder ANSEHEN
npx -y hyperframes@0.9.80 render -o out/NNN-slug.mp4 --fps 30
```
Bild 0 ist das Thumbnail: Hook-Frage muss ab Bild 0 voll sichtbar sein.
Lautheit prüfen: `ffmpeg -i out/X.mp4 -af ebur128=peak=true -f null -` → Ziel −16 bis −14 LUFS,
sonst `data-volume` am `<audio id="voice">` anheben (1.4 ≈ +3 dB) und neu rendern.

Eigene Welten statt Nachtstadt sind erlaubt (Beispiel Weltall: `videos/002-sonne/`) – Farben, HUD,
Untertitel und Dramaturgie bleiben gleich.

## 7. Abgabe
- `out/NNN-slug.mp4` und `POST.md` (Beschreibung, 3–5 Hashtags, Quellen/Rechnung) committen; `.snaps/` nicht.
- Dem Nutzer sagen: Musik im TikTok-Editor dazulegen (Referenzen nutzen leisen Lo-Fi-/Slowed-Sound,
  ca. 10–15 % Lautstärke) – die Stimme ist bereits im Video.
- Bessere Stimme möglich: ElevenLabs (braucht API-Schlüssel über das sichere Formular, nie im Chat).

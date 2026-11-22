#!/usr/bin/env python3
"""Sounddesign für Spannung: erzeugt Geräusche passend zur Sprachspur und setzt sie in index.html.

Nutzung (nach tts_de.py und sync_timing.py):
    python3 sfx.py <projekt>

In script.json:
  "sfx": [
    {"sound": "impact",    "at": ["h3", 3], "vol": 0.9},          # Wort 3 von Satz h3 (Start)
    {"sound": "whoosh",    "at": ["f1"], "offset": -0.3},          # Satzanfang f1, 0,3 s früher
    {"sound": "riser",     "until": ["r3", 4], "dur": 2.5},        # endet genau auf dem Wort
    {"sound": "heartbeat", "at": ["r1"], "until": ["r4"], "bpm": [70, 150], "vol": 0.8},
    {"sound": "tick",      "at": ["o1", 1], "every": 1.0, "until": ["o3", 4]}
  ]
Anker: "start" | "end" | [satz] | [satz, wort] | [satz, wort, "end"]  (+ optional "offset")

REGEL DES KANALS: keine Musik, keine Instrumente, keine Melodien oder tonalen Klangteppiche.
Erlaubt sind nur nicht-musikalische Geräusche (Herzschlag, Luftzug, Einschlag, Rauschen, Uhr-Tick).

Klänge (rein synthetisch, deterministisch – gemessen, nicht gehört):
  heartbeat  Lub-Dub, Tempo steigt von bpm[0] auf bpm[1]
  impact     tiefer Schlag mit Nachhall (für Pointe/Einschlag)
  whoosh     Luftzug (Szenenwechsel, schnelle Karten)
  riser      ansteigendes Luftrauschen (ohne Ton) bis zum Anker (Spannung vor Auflösung)
  tick       kurzer Uhr-Tick
Schreibt assets/sfx/*.wav und ersetzt in index.html den Block zwischen <!-- SFX:BEGIN --> und <!-- SFX:END -->.
"""
import json
import os
import re
import sys
import wave

import numpy as np

SR = 44100
RNG = np.random.default_rng(1234)


def lowpass(x, fc):
    """Einpoliger Tiefpass; fc als Skalar oder Array (zeitvariabel)."""
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def env_ad(n, attack, decay):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(attack, 1e-4)) * np.exp(-np.maximum(0, t - attack) / decay)
    return e


def norm(x, peak=0.89):
    m = np.abs(x).max()
    return x / m * peak if m > 0 else x


def thump(f0, dur, amp):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.6 * np.exp(-t / 0.03))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(ph) * env_ad(n, 0.004, 0.07)


def s_heartbeat(dur, bpm=(70, 140)):
    n = int(dur * SR)
    x = np.zeros(n + SR)
    t = 0.05
    while t < dur:
        k = t / dur
        rate = bpm[0] + (bpm[1] - bpm[0]) * k
        i = int(t * SR)
        a = thump(52, 0.25, 1.0)
        b = thump(46, 0.25, 0.65)
        x[i:i + len(a)] += a
        j = i + int(0.17 * SR)
        x[j:j + len(b)] += b
        t += 60.0 / rate
    x = lowpass(x[:n], 180)
    return norm(x, 0.89)


def s_impact(dur=1.8):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 40 + 70 * np.exp(-t / 0.12)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.003, 0.45)
    crack = lowpass(RNG.standard_normal(n), 3000) * env_ad(n, 0.001, 0.025) * 0.6
    tail = lowpass(RNG.standard_normal(n), 400) * env_ad(n, 0.01, 0.6) * 0.35
    return norm(boom + crack + tail)


def s_whoosh(dur=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    k = t / dur
    fc = 300 + 4200 * np.sin(np.pi * k) ** 2
    noise = RNG.standard_normal(n)
    band = lowpass(noise, fc) - lowpass(noise, fc * 0.25)
    return norm(band * np.sin(np.pi * k) ** 1.5, 0.8)


def s_riser(dur=2.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    k = t / dur
    fc = 250 + 6000 * k ** 2
    noise = RNG.standard_normal(n)
    band = lowpass(noise, fc) - lowpass(noise, fc * 0.3)
    amp = k ** 2.2
    amp[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    return norm(band * amp, 0.8)


def s_tick(dur=0.06):
    n = int(dur * SR)
    noise = RNG.standard_normal(n)
    hp = noise - lowpass(noise, 1800)
    return norm(hp * env_ad(n, 0.0005, 0.008), 0.7)


def write_wav(path, x):
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def main():
    proj = sys.argv[1]
    spec = json.load(open(os.path.join(proj, "script.json"), encoding="utf-8"))
    vt = json.load(open(os.path.join(proj, "assets/voice-timing.json"), encoding="utf-8"))
    total = vt["duration"] + 1.6
    segs = {s["id"]: s for s in vt["segments"]}

    def anchor(a, offset=0.0):
        if a == "start":
            return 0.0 + offset
        if a == "end":
            return total + offset
        sid = a[0]
        if len(a) == 1:
            return segs[sid]["start"] + offset
        ws = [w for w in vt["words"] if w["seg"] == sid]
        w = ws[min(a[1], len(ws) - 1)] if a[1] >= 0 else ws[-1]
        return w[a[2] if len(a) > 2 else "start"] + offset

    out = os.path.join(proj, "assets/sfx")
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    tags = []
    for i, e in enumerate(spec.get("sfx", [])):
        snd, off = e["sound"], e.get("offset", 0.0)
        if snd in ("drone", "music", "melody", "pad"):
            raise SystemExit(f"'{snd}' ist auf diesem Kanal nicht erlaubt (keine Musik/Klangteppiche).")
        if "at" in e and "until" in e and snd == "heartbeat":
            t0, t1 = anchor(e["at"], off), anchor(e["until"], e.get("until_offset", 0.0))
        elif "until" in e and "at" not in e:
            t1 = anchor(e["until"], off)
            t0 = t1 - e.get("dur", 2.5)
        else:
            t0 = anchor(e["at"], off)
            t1 = None
        t0 = max(0.0, t0)
        starts = [t0]
        if snd == "tick" and "every" in e:
            end = anchor(e["until"])
            starts = list(np.arange(t0, end, e["every"]))
        for k, st in enumerate(starts):
            if snd == "heartbeat":
                x = s_heartbeat(t1 - st, tuple(e.get("bpm", (70, 140))))
            elif snd == "impact":
                x = s_impact(e.get("dur", 1.8))
            elif snd == "whoosh":
                x = s_whoosh(e.get("dur", 0.7))
            elif snd == "riser":
                x = s_riser(t1 - st if t1 else e.get("dur", 2.5))
            elif snd == "tick":
                x = s_tick()
            else:
                raise SystemExit(f"Unbekannter Klang: {snd}")
            name = f"{i:02d}{chr(97 + k) if len(starts) > 1 else ''}-{snd}.wav"
            write_wav(os.path.join(out, name), x)
            d = len(x) / SR
            lane = 5 if snd == "heartbeat" else 4
            tags.append(f'      <audio id="sfx-{name[:-4]}" src="assets/sfx/{name}" data-start="{st:.3f}" '
                        f'data-duration="{d:.3f}" data-track-index="{lane}" data-volume="{e.get("vol", 0.6)}"></audio>')

    ip = os.path.join(proj, "index.html")
    doc = open(ip, encoding="utf-8").read()
    block = "<!-- SFX:BEGIN -->\n" + "\n".join(tags) + "\n      <!-- SFX:END -->"
    if "<!-- SFX:BEGIN -->" not in doc:
        raise SystemExit("index.html braucht die Marker <!-- SFX:BEGIN --> und <!-- SFX:END --> im #root")
    doc = re.sub(r"<!-- SFX:BEGIN -->.*?<!-- SFX:END -->", block, doc, flags=re.S)
    open(ip, "w", encoding="utf-8").write(doc)
    print(f"{len(tags)} Geräusche gesetzt")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Deutsche Sprachausgabe + Wort-Zeitstempel für HyperFrames-Videos.

Nutzung:
    python3 tts_de.py <projekt>/script.json <projekt>/assets

script.json:
{
  "speed": 0.9,                      # length_scale (<1 = schneller)
  "lead_in": 0.3,                    # Stille am Anfang (s)
  "segments": [
    {"id": "h1", "scene": "hook", "text": "Kannst du einem *Tsunami* ...?", "pause": 0.25},
    {"id": "b1", "scene": "bolt", "text": "Selbst Usain Bolt ...", "say": "Selbst Jussein Bolt ..."},
    {"id": "p1", "scene": "punch", "text": "...", "caption": false},
    ...
  ]
}

  *Wort*  = Wort im Untertitel farbig hervorheben
  say     = optionale Aussprache-Variante (gleiche Wortanzahl wie text!)
  caption = false → Satz bekommt keinen Untertitel (z. B. wenn der Text groß im Bild steht)

Erzeugt:
    assets/voice.wav           – komplette Sprachspur (mono, 22,05 kHz)
    assets/voice-timing.json   – {duration, scenes:{id:{start,end}}, segments:[...], words:[...]}

Die Wortzeiten werden geschätzt: Jeder Satz wird einzeln synthetisiert (exakte Satzgrenzen),
innerhalb eines Satzes werden Sprechpausen im Audio erkannt und an Kommas/Doppelpunkten verankert,
der Rest wird nach Phonem-Anzahl pro Wort verteilt. Für Untertitel mit 2–4 Wörtern reicht das.
"""
import json
import os
import re
import sys
import wave

import numpy as np
from piper import PiperVoice, SynthesisConfig

VOICE_DIR = os.environ.get(
    "PIPER_VOICE_DIR", "/home/user/tools/voices/vits-piper-de_DE-thorsten-high"
)
VOICE = os.path.join(VOICE_DIR, "de_DE-thorsten-high.onnx")


def synth(voice, text, speed):
    cfg = SynthesisConfig(length_scale=speed, noise_scale=0.6, noise_w_scale=0.7)
    audio, phonemes, sr = [], [], 22050
    for chunk in voice.synthesize(text, syn_config=cfg):
        sr = chunk.sample_rate
        audio.append(chunk.audio_float_array)
        phonemes.extend(chunk.phonemes + [" "])
    return np.concatenate(audio), phonemes, sr


def trim(a, sr, thr=0.01):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    s = max(0, idx[0] - int(0.02 * sr))
    e = min(len(a), idx[-1] + int(0.05 * sr))
    return a[s:e]


def speech_gaps(a, sr, min_gap=0.11):
    """Liefert Liste (start_s, end_s) stiller Lücken innerhalb des Satzes."""
    hop = int(0.01 * sr)
    env = np.array([np.sqrt(np.mean(a[i : i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    silent = env < max(0.012, env.max() * 0.04)
    gaps, start = [], None
    for i, s in enumerate(silent):
        if s and start is None:
            start = i
        if not s and start is not None:
            if (i - start) * 0.01 >= min_gap:
                gaps.append((start * 0.01, i * 0.01))
            start = None
    return gaps


def word_weights(words, phonemes):
    ph_words = [w for w in "".join(phonemes).split(" ") if re.search(r"\w", w)]
    if len(ph_words) == len(words):
        return [max(2, len(re.sub(r"[ˈˌː,.!?;:]", "", p))) for p in ph_words]
    return [max(2, len(re.sub(r"\W", "", w))) + 1 for w in words]


def distribute(words, weights, t0, t1):
    total = sum(weights)
    out, t = [], t0
    for w, wt in zip(words, weights):
        d = (t1 - t0) * wt / total
        out.append([w, t, t + d])
        t += d
    return out


def main():
    script_path, out_dir = sys.argv[1], sys.argv[2]
    spec = json.load(open(script_path, encoding="utf-8"))
    speed = spec.get("speed", 0.9)
    os.makedirs(out_dir, exist_ok=True)
    voice = PiperVoice.load(VOICE, VOICE + ".json")

    sr = 22050
    track = [np.zeros(int(spec.get("lead_in", 0.3) * sr), dtype=np.float32)]
    cursor = len(track[0]) / sr
    segments, words, scenes = [], [], {}

    for seg in spec["segments"]:
        raw_tokens = seg["text"].split()
        hl = [t.startswith("*") or t.rstrip(",.:;!?").endswith("*") for t in raw_tokens]
        clean = seg["text"].replace("*", "")
        audio, phonemes, sr = synth(voice, seg.get("say", clean), speed)
        audio = trim(audio, sr)
        dur = len(audio) / sr
        start, end = cursor, cursor + dur

        # Wörter in Phrasen (an , : ; – . ? !) teilen und an erkannten Pausen verankern
        tokens = clean.split()
        phrases, cur = [], []
        for tok in tokens:
            cur.append(tok)
            if re.search(r"[,:;.!?–]$", tok):
                phrases.append(cur)
                cur = []
        if cur:
            phrases.append(cur)
        gaps = speech_gaps(audio, sr)
        need = len(phrases) - 1
        gaps = sorted(sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[:need])
        bounds = [0.0]
        for g in gaps:
            bounds += [g[0], g[1]]
        bounds.append(dur)
        if len(gaps) != need:  # Fallback: ganze Zeile proportional
            phrases, bounds = [tokens], [0.0, dur]
        weights_all = word_weights(tokens, phonemes)
        hl_iter = iter(hl)
        wi = 0
        for pi, ph in enumerate(phrases):
            w = weights_all[wi : wi + len(ph)]
            wi += len(ph)
            for text, ws, we in distribute(ph, w, bounds[2 * pi], bounds[2 * pi + 1]):
                words.append(
                    {"id": f"w{len(words)}", "seg": seg["id"], "text": text,
                     "start": round(start + ws, 3), "end": round(start + we, 3),
                     "hl": next(hl_iter), "cap": seg.get("caption", True)}
                )

        segments.append({"id": seg["id"], "scene": seg["scene"], "text": clean,
                         "start": round(start, 3), "end": round(end, 3)})
        sc = scenes.setdefault(seg["scene"], {"start": round(start, 3)})
        sc["end"] = round(end, 3)

        pause = seg.get("pause", 0.25)
        track += [audio.astype(np.float32), np.zeros(int(pause * sr), dtype=np.float32)]
        cursor = end + pause

    full = np.concatenate(track)
    peak = np.abs(full).max()
    full = full / peak * 0.89  # ca. -1 dBFS
    with wave.open(os.path.join(out_dir, "voice.wav"), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((full * 32767).astype(np.int16).tobytes())

    timing = {"duration": round(len(full) / sr, 3), "scenes": scenes,
              "segments": segments, "words": words}
    json.dump(timing, open(os.path.join(out_dir, "voice-timing.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"voice.wav {timing['duration']} s, {len(segments)} Sätze, {len(words)} Wörter")
    for k, v in scenes.items():
        print(f"  {k:10s} {v['start']:6.2f} → {v['end']:6.2f}")


if __name__ == "__main__":
    main()

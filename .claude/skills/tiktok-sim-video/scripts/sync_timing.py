#!/usr/bin/env python3
"""Überträgt die Sprach-Zeitstempel auf das HyperFrames-Projekt.

Nutzung:
    python3 sync_timing.py <projekt>

Liest  <projekt>/assets/voice-timing.json (von tts_de.py) und
  1. schreibt <projekt>/assets/timing.js   → window.VT (Szenen, Sätze, Wörter; lokal je Szene abrufbar)
  2. schreibt <projekt>/compositions/captions.html (Wort-synchrone Untertitel, 2–3 Wörter pro Gruppe)
  3. setzt in <projekt>/index.html data-start/data-duration aller Szenen-Hosts (id = Szenenname),
     die Länge der Sprachspur (#voice) und des Root (#root).

Szenen-Hosts: ein Element mit id="<szene>" und data-composition-src; Szenen laufen lückenlos,
jeder Schnitt liegt CUT_LEAD Sekunden vor dem ersten Wort der nächsten Szene.
"""
import html
import json
import os
import re
import sys

CUT_LEAD = 0.12
TAIL = 1.6
MAX_WORDS = 3
MAX_CHARS = 22
CAPTION_TOP = 1380  # wie Referenz: Untertitel bei ~75 % der Höhe, über TikToks Beschreibungstext


def set_attr(tag, name, value):
    if re.search(rf'\s{name}="[^"]*"', tag):
        return re.sub(rf'(\s{name}=")[^"]*(")', rf"\g<1>{value}\g<2>", tag)
    return tag.replace(">", f' {name}="{value}">', 1) if tag.endswith(">") else tag


def patch_element(doc, el_id, **attrs):
    m = re.search(rf'<[a-z]+[^>]*\sid="{re.escape(el_id)}"[^>]*>', doc, re.S)
    if not m:
        print(f"  ! Element #{el_id} nicht in index.html gefunden")
        return doc
    tag = m.group(0)
    new = tag
    for k, v in attrs.items():
        new = set_attr(new, k.replace("_", "-"), v)
    return doc[: m.start()] + new + doc[m.end():]


def caption_groups(words):
    groups, cur = [], []
    for i, w in enumerate(words):
        if not w.get("cap", True):
            if cur:
                groups.append(cur)
                cur = []
            continue
        if cur:
            prev = cur[-1]
            chars = sum(len(x["text"]) + 1 for x in cur) + len(w["text"])
            if (len(cur) >= MAX_WORDS or chars > MAX_CHARS or w["start"] - prev["end"] >= 0.15
                    or prev["seg"] != w["seg"]):
                groups.append(cur)
                cur = []
        cur.append(w)
        if re.search(r"[.!?:,]$", w["text"]):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


def main():
    proj = sys.argv[1]
    t = json.load(open(os.path.join(proj, "assets/voice-timing.json"), encoding="utf-8"))
    scene_ids = list(t["scenes"].keys())
    total = round(t["duration"] + TAIL, 2)

    # Szenen-Slots
    slots = {}
    for i, sid in enumerate(scene_ids):
        start = 0.0 if i == 0 else round(t["scenes"][sid]["start"] - CUT_LEAD, 3)
        end = total if i == len(scene_ids) - 1 else round(t["scenes"][scene_ids[i + 1]]["start"] - CUT_LEAD, 3)
        slots[sid] = {"start": start, "end": end}

    # 1) timing.js
    vt = {"total": total, "slots": slots, "segments": {}, "words": t["words"]}
    for s in t["segments"]:
        vt["segments"][s["id"]] = {"scene": s["scene"], "start": s["start"], "end": s["end"]}
    js = (
        "// Automatisch erzeugt von sync_timing.py – nicht von Hand bearbeiten.\n"
        f"window.VT = {json.dumps(vt, ensure_ascii=False)};\n"
        "(function(VT){\n"
        "  // Zeit eines Satzes (start|end) lokal zur Szene, in der er gesprochen wird\n"
        "  VT.seg = function(id, which){ var s = VT.segments[id]; return s[which||'start'] - VT.slots[s.scene].start; };\n"
        "  // n-tes Wort (0-basiert) eines Satzes, lokal zur Szene\n"
        "  VT.word = function(id, n, which){ var s = VT.segments[id]; var ws = VT.words.filter(function(w){return w.seg===id;});\n"
        "    var w = ws[Math.min(n, ws.length-1)]; return w[which||'start'] - VT.slots[s.scene].start; };\n"
        "  VT.len = function(scene){ return VT.slots[scene].end - VT.slots[scene].start; };\n"
        "})(window.VT);\n"
    )
    open(os.path.join(proj, "assets/timing.js"), "w", encoding="utf-8").write(js)

    # 2) captions.html
    groups = caption_groups(t["words"])
    parts, tl = [], []
    for gi, g in enumerate(groups):
        start = max(0.1, g[0]["start"] - 0.06)
        nxt = groups[gi + 1][0]["start"] - 0.06 if gi + 1 < len(groups) else total
        end = min(nxt, g[-1]["end"] + 0.35)
        spans = []
        for w in g:
            cls = ' class="hl"' if w.get("hl") else ""
            spans.append(f"<span{cls}>{html.escape(w['text'])}</span>")
        parts.append(f'    <div class="cg" id="cap-{gi}">{" ".join(spans)}</div>')
        tl.append(
            f'    tl.fromTo("#cap-{gi}", {{opacity: 0, y: 14, scale: 0.96}}, '
            f'{{opacity: 1, y: 0, scale: 1, duration: 0.12, ease: "power2.out"}}, {start:.3f});\n'
            f'    tl.to("#cap-{gi}", {{opacity: 0, duration: 0.08, ease: "power2.in"}}, {end - 0.08:.3f});\n'
            f'    tl.set("#cap-{gi}", {{opacity: 0, visibility: "hidden"}}, {end:.3f});'
        )
    cap_html = f"""<!-- Automatisch erzeugt von sync_timing.py – Stil hier anpassen, Text in script.json. -->
<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cg {{
      position: absolute; left: 0; right: 0; top: {CAPTION_TOP}px;
      text-align: center; opacity: 0; overflow: visible;
      font-family: "Inter", sans-serif; font-weight: 900; font-size: 62px;
      letter-spacing: -0.01em; color: #F4F5FA; line-height: 1.1;
      text-shadow: 0 4px 18px rgba(0,0,0,0.85), 0 0 2px rgba(0,0,0,0.9);
    }}
    .cg .hl {{ color: var(--accent, #FFB547); }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(parts)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl)}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
    os.makedirs(os.path.join(proj, "compositions"), exist_ok=True)
    open(os.path.join(proj, "compositions/captions.html"), "w", encoding="utf-8").write(cap_html)

    # 3) index.html
    ip = os.path.join(proj, "index.html")
    doc = open(ip, encoding="utf-8").read()
    doc = patch_element(doc, "root", data_duration=total)
    doc = patch_element(doc, "captions", data_start=0, data_duration=total)
    doc = patch_element(doc, "voice", data_start=0, data_duration=round(t["duration"], 3))
    for sid, s in slots.items():
        doc = patch_element(doc, sid, data_start=s["start"], data_duration=round(s["end"] - s["start"], 3))
    open(ip, "w", encoding="utf-8").write(doc)

    print(f"Gesamtlänge {total} s · {len(groups)} Untertitel-Gruppen")
    for sid, s in slots.items():
        print(f"  {sid:10s} {s['start']:6.2f} → {s['end']:6.2f}")


if __name__ == "__main__":
    main()

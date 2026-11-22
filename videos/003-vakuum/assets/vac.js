/* vac.js – projektspezifisch: Vakuum-Uhr (Sekunden im All) über die globale Videozeit,
 * schwebende Figur und Raumstation. Lädt nach sim.js und timing.js. */
(function () {
  const VT = window.VT, SIM = window.SIM;
  const g = (seg, n, which) => (n == null ? VT.segments[seg][which || "start"]
    : VT.words.filter((w) => w.seg === seg)[n][which || "start"]);
  const A = [
    [VT.slots.lunge.start, 0],
    [VT.slots.lunge.end, 1.5],                       // ZEITLUPE: Sekunde 0–1,5
    [g("o1"), 8],
    [g("o1", 0, "end"), 10],                         // „Sekunde zehn.“
    [g("o3", 2), 15],                                // „fünfzehn“
    [VT.slots.ohnmacht.end, 17],
    [VT.slots.mythos.end, 40],                       // ZEITRAFFER
    [g("r3", 8), 84, "inOut"],                       // „vierundachtzig“
  ];
  const VAC = {
    /** Sekunden im Vakuum für globale Videozeit gt */
    T: (gt) => SIM.keys(A, gt),
    RESCUE: 84, WINDOW: 90, BLACKOUT: 15,
    /** Bewusstsein 0..1 */
    awake: (T) => (T < 6 ? 1 : T >= 15 ? 0 : 1 - Math.pow((T - 6) / 9, 1.6)),
    g,
    /** Schwebende Figur (Piktogramm ohne Anzug) in host */
    person(host, color) {
      const r = SIM.runner(host, color || SIM.C.teal);
      host.querySelector(".sim-badge").style.display = "none";
      host.style.transformOrigin = "30px 50px";
      return {
        set(x, y, scale, rot, t) {
          r.pose(0.25 + 0.04 * Math.sin(t * 1.7), 0.9);
          host.style.transform = `translate(${x - 30}px, ${y - 50}px) rotate(${rot}deg) scale(${scale})`;
        },
      };
    },
    /** Raumstation als SVG-Markup, Luftschleuse bei (x, y) links am Modul */
    station(x, y) {
      return `<g>
        <rect x="${x + 240}" y="${y - 170}" width="26" height="340" fill="#2B2742" />
        ${[0, 1, 2, 3].map((i) => `<rect x="${x + 196}" y="${y - 260 + i * 34 - (i > 1 ? -320 : 0)}" width="114" height="28" fill="#1C2C5A" stroke="#3C5BA8" stroke-width="2" />`).join("")}
        <rect x="${x}" y="${y - 80}" width="420" height="160" rx="40" fill="#25223A" stroke="#4A4463" stroke-width="3" />
        <line x1="${x + 90}" y1="${y - 80}" x2="${x + 90}" y2="${y + 80}" stroke="#4A4463" stroke-width="3" />
        <rect x="${x + 6}" y="${y - 46}" width="60" height="92" rx="12" fill="#0B0B14" stroke="#FFB547" stroke-width="3" />
        <circle cx="${x + 160}" cy="${y}" r="18" fill="#FFB547" opacity=".35" />
        <circle cx="${x + 330}" cy="${y}" r="18" fill="#FFB547" opacity=".35" />
      </g>`;
    },
  };
  window.VAC = VAC;
})();

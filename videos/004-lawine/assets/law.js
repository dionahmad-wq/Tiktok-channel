/* law.js – projektspezifisch: Minuten unter dem Schnee (global), Überlebenskurve, Bausteine.
 * Überlebenskurve nach Brugger et al. 2001 (Schweiz, 1981–1998): 91 % bis 18 min, 34 % bei 35 min, 7 % bei 130 min. */
(function () {
  const VT = window.VT, SIM = window.SIM;
  const g = (seg, n, which) => (n == null ? VT.segments[seg][which || "start"]
    : VT.words.filter((w) => w.seg === seg)[n][which || "start"]);
  const A = [
    [g("b3", 4, "end"), 0],
    [VT.slots.kurve.end, 6],
    [g("e4", 1), 14, "inOut"],
  ];
  const SURV = [[0, 100], [18, 91], [35, 34], [60, 27], [90, 24], [130, 7]];
  const LAW = {
    g,
    T: (gt) => SIM.keys(A, gt),               // Minuten unter dem Schnee
    surv: (m) => SIM.keys(SURV, m),           // Überlebenswahrscheinlichkeit in %
    FOUND: 14, TIP: 18,
    pine(x, y, h, fill) {
      return `<path d="M${x} ${y - h} L${x + h * 0.32} ${y - h * 0.35} L${x + h * 0.18} ${y - h * 0.35} L${x + h * 0.38} ${y} L${x - h * 0.38} ${y} L${x - h * 0.18} ${y - h * 0.35} L${x - h * 0.32} ${y - h * 0.35} Z" fill="${fill || "#14241f"}"/>`;
    },
    /** Lawinen-Pulverwolke: Pool aus Kreisen; draw(frontX, groundY, t, scale) */
    cloud(parent, n = 34, seed = 5) {
      const r = SIM.rng(seed), parts = [];
      for (let i = 0; i < n; i++) parts.push({ el: SIM.el("circle", { fill: i % 5 ? "#E9F0FA" : "#C8D5E8" }, parent), dx: -r() * 520, dy: r() * 1, rr: 40 + r() * 90, ph: r() * 6 });
      const glow = SIM.el("path", { fill: "none", stroke: "#FF5A4E", "stroke-width": 5, "stroke-linecap": "round", style: "filter: drop-shadow(0 0 10px rgba(255,90,78,.85))" }, parent);
      return {
        draw(fx, gy, t, s = 1) {
          parts.forEach((p) => {
            const rr = p.rr * s * (1 + 0.08 * Math.sin(t * 3 + p.ph));
            const x = fx + p.dx * s + 10 * Math.sin(t * 2 + p.ph);
            const hgt = (1 - Math.min(1, -p.dx / 520)) * 0.6 + 0.4;
            p.el.setAttribute("cx", x);
            p.el.setAttribute("cy", gy - rr * 0.7 - p.dy * 200 * s * hgt);
            p.el.setAttribute("r", rr);
            p.el.setAttribute("opacity", 0.92);
          });
          glow.setAttribute("d", `M${fx - 40 * s} ${gy - 230 * s} Q${fx + 60 * s} ${gy - 160 * s} ${fx + 50 * s} ${gy}`);
        },
      };
    },
  };
  window.LAW = LAW;
})();

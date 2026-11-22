/* sim.js – gemeinsame Bausteine für "Was passiert, wenn"-Simulationen (Stil: kurzsimuliert).
 * Wird einmal in index.html geladen (<script src="assets/sim.js">) und ist in allen Szenen als
 * window.SIM verfügbar. Alles ist deterministisch: gleiche Zeit → gleiches Bild.
 */
(function () {
  const SIM = {};
  const NS = "http://www.w3.org/2000/svg";

  // ---------- Farben (siehe STYLE_GUIDE.md) ----------
  SIM.C = {
    teal: "#3ED6C0", coral: "#FF5A4E", amber: "#FFB547", ink: "#F4F5FA",
    mute: "#8A8FA8", night: "#06070E", water: "#1E4C86", waterDeep: "#0B2140",
  };

  // ---------- Zahlen auf Deutsch ----------
  SIM.fmtInt = (n) => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  SIM.fmtDec = (n, d = 1) => {
    const s = n.toFixed(d).split(".");
    return SIM.fmtInt(+s[0]) + (d > 0 ? "," + s[1] : "");
  };
  SIM.clock = (sec) => {
    sec = Math.max(0, Math.floor(sec));
    const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
    const mm = h ? String(m).padStart(2, "0") : String(m);
    return (h ? h + ":" : "") + mm + ":" + String(s).padStart(2, "0");
  };

  // ---------- Interpolation ----------
  SIM.clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  SIM.lerp = (a, b, k) => a + (b - a) * k;
  SIM.ease = {
    linear: (k) => k,
    out: (k) => 1 - Math.pow(1 - k, 2),
    out3: (k) => 1 - Math.pow(1 - k, 3),
    inOut: (k) => (k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2),
  };
  /** Stückweise Interpolation: anchors = [[t, v, easeName?], ...] (sortiert nach t). */
  SIM.keys = (anchors, t) => {
    if (t <= anchors[0][0]) return anchors[0][1];
    for (let i = 1; i < anchors.length; i++) {
      const [t1, v1, e] = anchors[i];
      const [t0, v0] = anchors[i - 1];
      if (t <= t1) {
        const k = t1 === t0 ? 1 : (t - t0) / (t1 - t0);
        return SIM.lerp(v0, v1, SIM.ease[e || "linear"](k));
      }
    }
    return anchors[anchors.length - 1][1];
  };

  // ---------- Pseudozufall mit Seed ----------
  SIM.rng = (seed) => {
    let s = seed >>> 0 || 1;
    return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  };

  // ---------- SVG-Helfer ----------
  SIM.el = (tag, attrs = {}, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  };

  // ---------- Läufer-Figur ----------
  /** Baut eine Läufer-Figur (Piktogramm) in `host` (ein leeres div). */
  SIM.runner = (host, color = SIM.C.teal, label = "DU", letter = "A") => {
    host.innerHTML = `
      <div class="sim-badge" style="--c:${color}"><b>${letter}</b><span>${label}</span></div>
      <svg viewBox="0 0 60 100" width="60" height="100" style="overflow:visible;display:block">
        <g class="r-arm2" stroke="${color}" stroke-width="7" stroke-linecap="round" opacity=".55"><line x1="30" y1="32" x2="30" y2="54"/></g>
        <g class="r-leg2" stroke="${color}" stroke-width="8" stroke-linecap="round" opacity=".55"><line x1="30" y1="58" x2="30" y2="96"/></g>
        <line x1="30" y1="28" x2="30" y2="60" stroke="${color}" stroke-width="11" stroke-linecap="round"/>
        <circle cx="30" cy="13" r="10" fill="${color}"/>
        <g class="r-leg1" stroke="${color}" stroke-width="8" stroke-linecap="round"><line x1="30" y1="58" x2="30" y2="96"/></g>
        <g class="r-arm1" stroke="${color}" stroke-width="7" stroke-linecap="round"><line x1="30" y1="32" x2="30" y2="54"/></g>
      </svg>`;
    const q = (c) => host.querySelector(c);
    const parts = { a1: q(".r-arm1"), a2: q(".r-arm2"), l1: q(".r-leg1"), l2: q(".r-leg2") };
    return {
      host,
      /** phase in Schritten (z. B. Strecke/Schrittlänge), amp 0 = steht, 1 = rennt */
      pose(phase, amp = 1) {
        const s = Math.sin(phase * Math.PI * 2);
        parts.l1.setAttribute("transform", `rotate(${32 * s * amp} 30 58)`);
        parts.l2.setAttribute("transform", `rotate(${-32 * s * amp} 30 58)`);
        parts.a1.setAttribute("transform", `rotate(${-38 * s * amp - 10 * amp} 30 32)`);
        parts.a2.setAttribute("transform", `rotate(${38 * s * amp - 10 * amp} 30 32)`);
      },
      /** Position in Pixeln (Füße auf groundY), Skalierung optional */
      place(x, groundY, scale = 1, bob = 0) {
        host.style.transform = `translate(${x - 30 * scale}px, ${groundY - 100 * scale - bob}px) scale(${scale})`;
      },
    };
  };

  // ---------- Landwelt: Nacht, Stadt, Laternen, Strand, Lineal, Tsunami ----------
  /**
   * new SIM.LandWorld(svgElement, { ground: 1000, seed: 7 })
   * draw({ cam, sx, anchor, waveX, waveH, t, shoreX })
   *   cam    – Welt-Meter, die bei Bildschirm-x = anchor liegen
   *   sx     – Pixel pro Meter (horizontal)
   *   waveX  – Wellenfront in Metern (null = keine Welle)
   *   waveH  – Wellenhöhe in Pixeln
   *   t      – Animationszeit (für Schaum/Wogen)
   */
  SIM.LandWorld = function (svg, opts = {}) {
    const G = (this.G = opts.ground || 1000);
    this.svg = svg;
    this.shoreX = opts.shoreX ?? -40;
    const rnd = SIM.rng(opts.seed || 7);
    svg.setAttribute("viewBox", "0 0 1080 1920");
    const defs = SIM.el("defs", {}, svg);
    defs.innerHTML = `
      <linearGradient id="lw-water" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#2D69B0"/><stop offset=".35" stop-color="#1A477F"/><stop offset="1" stop-color="#0A1D38"/>
      </linearGradient>
      <linearGradient id="lw-ground" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#17151F"/><stop offset="1" stop-color="#06070E" stop-opacity="0"/>
      </linearGradient>
      <radialGradient id="lw-lamp"><stop offset="0" stop-color="#FFC66B" stop-opacity=".55"/><stop offset="1" stop-color="#FFC66B" stop-opacity="0"/></radialGradient>
      <linearGradient id="lw-haze" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#2A1F4D" stop-opacity="0"/><stop offset="1" stop-color="#2A1F4D" stop-opacity=".55"/>
      </linearGradient>`;

    // Hügel + Stadt (Parallaxe)
    this.far = SIM.el("g", {}, svg);
    this.city = SIM.el("g", {}, svg);
    const hills = SIM.el("path", { fill: "#151129", opacity: ".9" }, this.far);
    let d = `M0 ${G}`;
    for (let x = 0; x <= 2400; x += 60) d += ` L${x} ${G - 150 - 50 * Math.sin(x / 210) - 30 * Math.sin(x / 77)}`;
    hills.setAttribute("d", d + ` L2400 ${G} Z`);
    let bx = 0;
    while (bx < 2400) {
      const w = 34 + rnd() * 60, h = 50 + rnd() * 170;
      SIM.el("rect", { x: bx, y: G - h, width: w, height: h, fill: "#0F0D1C" }, this.city);
      for (let wy = G - h + 12; wy < G - 14; wy += 18)
        for (let wx = bx + 7; wx < bx + w - 8; wx += 13)
          if (rnd() < 0.16) SIM.el("rect", { x: wx, y: wy, width: 5, height: 7, fill: rnd() < 0.7 ? "#FFB547" : "#9DB7FF", opacity: 0.35 + rnd() * 0.4 }, this.city);
      bx += w + 4 + rnd() * 14;
    }
    SIM.el("rect", { x: 0, y: G - 260, width: 1080, height: 262, fill: "url(#lw-haze)" }, svg);

    // Laternen (Pool)
    this.lamps = [];
    const lampG = SIM.el("g", {}, svg);
    for (let i = 0; i < 14; i++) {
      const g = SIM.el("g", {}, lampG);
      SIM.el("circle", { cx: 0, cy: G - 128, r: 70, fill: "url(#lw-lamp)" }, g);
      SIM.el("line", { x1: 0, y1: G, x2: 0, y2: G - 124, stroke: "#2A2638", "stroke-width": 5 }, g);
      SIM.el("line", { x1: 0, y1: G - 124, x2: 14, y2: G - 128, stroke: "#2A2638", "stroke-width": 5 }, g);
      SIM.el("circle", { cx: 12, cy: G - 126, r: 6, fill: "#FFD58A" }, g);
      this.lamps.push(g);
    }

    // Boden, ruhiges Meer, Welle
    this.ground = SIM.el("rect", { y: G, height: 140, fill: "url(#lw-ground)" }, svg);
    this.groundLine = SIM.el("line", { y1: G, y2: G, stroke: "#3A3550", "stroke-width": 3 }, svg);
    this.sea = SIM.el("rect", { x: -20, y: G - 10, height: 150, fill: "url(#lw-water)" }, svg);
    this.seaLine = SIM.el("line", { y1: G - 10, y2: G - 10, stroke: "#5D9BE0", "stroke-width": 3, opacity: 0.7 }, svg);
    this.wave = SIM.el("path", { fill: "url(#lw-water)" }, svg);
    this.crest = SIM.el("path", { fill: "none", stroke: SIM.C.coral, "stroke-width": 5, "stroke-linecap": "round", style: "filter: drop-shadow(0 0 10px rgba(255,90,78,.8))" }, svg);
    this.foam = [];
    for (let i = 0; i < 10; i++) this.foam.push(SIM.el("circle", { r: 3 + (i % 3) * 2, fill: "#DDEBFF", opacity: 0.8 }, svg));

    // Lineal (Pool)
    this.ticks = [];
    const rulerG = SIM.el("g", { "data-layout-ignore": "" }, svg);
    for (let i = 0; i < 24; i++) {
      const g = SIM.el("g", {}, rulerG);
      SIM.el("line", { x1: 0, y1: G + 22, x2: 0, y2: G + 36, stroke: "#5B5875", "stroke-width": 2 }, g);
      const tx = SIM.el("text", { x: 0, y: G + 66, "text-anchor": "middle", fill: "#8A8FA8", "font-family": "Inter", "font-weight": 800, "font-size": 24 }, g);
      this.ticks.push({ g, tx });
    }
  };

  SIM.LandWorld.prototype.toScreen = function (X) {
    return this.anchor + (X - this.cam) * this.sx;
  };

  SIM.LandWorld.prototype.draw = function (o) {
    const G = this.G;
    this.cam = o.cam; this.sx = o.sx; this.anchor = o.anchor ?? 540;
    const t = o.t || 0;
    const shore = this.toScreen(this.shoreX);

    // Parallaxe
    const camPx = o.cam * o.sx;
    this.far.setAttribute("transform", `translate(${-(((camPx * 0.12) % 1200) + 1200) % 1200} 0)`);
    this.city.setAttribute("transform", `translate(${-(((camPx * 0.3) % 1200) + 1200) % 1200} 0)`);

    // Laternen alle 120 m, nur an Land
    const step = 120;
    let first = Math.ceil((o.cam - this.anchor / o.sx) / step) * step;
    this.lamps.forEach((g, i) => {
      const X = first + i * step;
      const x = this.toScreen(X);
      const vis = X > this.shoreX + 30 && x > -60 && x < 1140;
      g.setAttribute("display", vis ? "inline" : "none");
      g.setAttribute("transform", `translate(${x} 0)`);
    });

    // Boden & Meer
    const gx = Math.max(-20, shore);
    this.ground.setAttribute("x", gx); this.ground.setAttribute("width", Math.max(0, 1120 - gx));
    this.groundLine.setAttribute("x1", gx); this.groundLine.setAttribute("x2", 1100);
    const sw = Math.max(0, shore + 20);
    this.sea.setAttribute("width", sw);
    this.seaLine.setAttribute("x1", -20); this.seaLine.setAttribute("x2", shore);

    // Lineal
    const tickStep = [25, 50, 100, 200, 250, 500, 1000].find((st) => st * o.sx >= 125) || 1000;
    const firstT = Math.ceil((o.cam - this.anchor / o.sx) / tickStep) * tickStep;
    this.ticks.forEach((tk, i) => {
      const X = firstT + i * tickStep;
      const x = this.toScreen(X);
      const vis = X >= 0 && x > 20 && x < 1060;
      tk.g.setAttribute("display", vis ? "inline" : "none");
      tk.g.setAttribute("transform", `translate(${x} 0)`);
      tk.tx.textContent = SIM.fmtInt(X) + " m";
    });

    // Welle
    if (o.waveX == null) {
      this.wave.setAttribute("d", ""); this.crest.setAttribute("d", "");
      this.foam.forEach((f) => f.setAttribute("opacity", 0));
      return;
    }
    const fx = this.toScreen(o.waveX);
    const H = o.waveH;
    const top = G - H;
    const wob = (x) => 5 * Math.sin(x / 47 + t * 2.1) + 3 * Math.sin(x / 19 - t * 3.3);
    let p = `M-30 ${G + 140} L-30 ${top + 30 + wob(-30)}`;
    for (let x = -30; x < fx - 90; x += 30) p += ` L${x} ${top + 18 * Math.min(1, (fx - 90 - x) / 400) + wob(x)}`;
    const crestPath = `M${Math.max(-30, fx - 260)} ${top + 14 + wob(fx - 260)} Q${fx - 90} ${top + wob(fx - 90)} ${fx - 40} ${top - 12} C${fx + 4} ${top - 22} ${fx + 30} ${top - 6} ${fx + 34} ${top + 22}`;
    p += ` L${fx - 90} ${top + wob(fx - 90)} Q${fx - 60} ${top - 6} ${fx - 40} ${top - 12}`;
    p += ` C${fx + 4} ${top - 22} ${fx + 30} ${top - 6} ${fx + 34} ${top + 22}`;
    p += ` C${fx + 38} ${top + 50} ${fx + 18} ${top + 70} ${fx + 26} ${G - 8} L${fx + 40} ${G + 4} L${fx + 40} ${G + 140} Z`;
    this.wave.setAttribute("d", p);
    this.crest.setAttribute("d", crestPath);
    this.foam.forEach((f, i) => {
      const k = (i * 0.137 + t * 0.9) % 1;
      f.setAttribute("cx", fx + 30 - k * 70 + 6 * Math.sin(i * 3 + t * 4));
      f.setAttribute("cy", top - 16 + k * 60 + (i % 4) * 9);
      f.setAttribute("opacity", 0.85 * (1 - k));
    });
  };

  window.SIM = SIM;
})();

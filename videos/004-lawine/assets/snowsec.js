/* Schnee-Querschnitt für „begraben“ und „rettung“: Oberfläche bei y = 800, Person ~1 m tief. */
window.SNOWSEC = function (svg, seed) {
  const r = SIM.rng(seed || 4);
  svg.insertAdjacentHTML("beforeend", `
    <defs><linearGradient id="ss-snow-${seed}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#C9D6EA"/><stop offset=".5" stop-color="#9AAFCD"/><stop offset="1" stop-color="#5E7398"/></linearGradient></defs>
    <path d="M-20 820 Q200 790 420 812 Q700 840 1100 800 L1100 1340 L-20 1340 Z" fill="url(#ss-snow-${seed})" stroke="#EEF4FC" stroke-width="5"/>`);
  const dots = SIM.el("g", { opacity: 0.35 }, svg);
  for (let i = 0; i < 120; i++) SIM.el("circle", { cx: r() * 1080, cy: 850 + r() * 480, r: 1.5 + r() * 2.5, fill: "#FFFFFF" }, dots);
  return dots;
};

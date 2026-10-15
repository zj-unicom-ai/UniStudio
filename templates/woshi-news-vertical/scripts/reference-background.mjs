// Vector reconstruction of the supplied date-version visual reference.
// All layers remain editable; no text or photograph from the poster is baked in.
export function referenceBackground(duration, backgroundPath) {
  if (backgroundPath) return `<img id="reference-background" class="clip" data-start="0" data-duration="${duration}" data-track-index="9" src="${backgroundPath}" alt="" />`;
  return `<svg id="reference-background" class="clip" data-start="0" data-duration="${duration}" data-track-index="9" viewBox="0 0 1080 1920" aria-hidden="true">
  <defs>
    <radialGradient id="bg-top-light" cx=".9" cy="-.1" r=".85"><stop stop-color="#247ECD" stop-opacity=".74"/><stop offset=".45" stop-color="#073467" stop-opacity=".48"/><stop offset="1" stop-color="#00101F" stop-opacity="0"/></radialGradient>
    <radialGradient id="bg-bottom-light" cx=".84" cy=".02" r=".9"><stop stop-color="#123D7C" stop-opacity=".5"/><stop offset=".5" stop-color="#011D38" stop-opacity=".36"/><stop offset="1" stop-color="#000C18" stop-opacity="0"/></radialGradient>
    <linearGradient id="bg-ray" x1="1" y1="0" x2="0" y2="1"><stop stop-color="#298ADD" stop-opacity=".4"/><stop offset=".5" stop-color="#12589B" stop-opacity=".12"/><stop offset="1" stop-color="#04192E" stop-opacity="0"/></linearGradient>
    <linearGradient id="bg-edge"><stop stop-color="#12629A" stop-opacity=".3"/><stop offset=".3" stop-color="#12BEFF"/><stop offset=".65" stop-color="#2B68AD" stop-opacity=".75"/><stop offset="1" stop-color="#2797F5" stop-opacity=".38"/></linearGradient>
    <radialGradient id="bg-flare"><stop stop-color="#E8FCFF"/><stop offset=".12" stop-color="#3DDDFF"/><stop offset=".35" stop-color="#008FFF" stop-opacity=".45"/><stop offset="1" stop-color="#008FFF" stop-opacity="0"/></radialGradient>
    <filter id="bg-soft" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5"/></filter>
    <clipPath id="bg-header-cut"><rect width="1080" height="500"/></clipPath>
    <clipPath id="bg-footer-cut"><rect y="1308" width="1080" height="612"/></clipPath>
  </defs>
  <rect width="1080" height="1920" fill="#000D1B"/>
  <g clip-path="url(#bg-header-cut)">
    <rect width="1080" height="500" fill="url(#bg-top-light)"/>
    <g class="ambient-beam">
      <path d="M690-90H1070L564 500H176Z" fill="url(#bg-ray)" opacity=".25"/>
      <path d="M830-60H1130L605 500H398Z" fill="url(#bg-ray)" opacity=".26"/>
      <path d="M1140-20 714 405 1079 169Z" fill="url(#bg-ray)" opacity=".26"/>
      <path d="M980-10 868 102M1090 56 913 167M1110 390C1016 448 939 489 804 513" stroke="#179DFF" stroke-width="2" opacity=".65"/>
      <path d="M1090 56 913 167" stroke="#7064E4" stroke-width="1.2" opacity=".6"/>
    </g>
    <circle cx="1034" cy="158" r="2.7" fill="#22BDFF"/><circle cx="1040" cy="213" r="4" fill="#169FFF"/>
    <circle cx="1040" cy="213" r="11" fill="#148BFF" opacity=".46" filter="url(#bg-soft)"/>
  </g>
  <g clip-path="url(#bg-footer-cut)">
    <rect y="1308" width="1080" height="612" fill="url(#bg-bottom-light)"/>
    <path class="ambient-beam" d="M1000 1308H1170L729 1780 869 1530Z" fill="url(#bg-ray)" opacity=".22"/>
    <path d="M1084 1640C1010 1720 979 1737 881 1815M1073 1593 1010 1667M872 1310 822 1383" stroke="#1266B3" stroke-width="1.3" opacity=".33"/>
    <path d="M0 1900H1080M0 1867H1080M0 1848H1080M90 1920 437 1824M353 1920 516 1824M643 1920 581 1824M970 1920 692 1824" stroke="#135B92" stroke-width="1" opacity=".12"/>
    <ellipse cx="300" cy="1883" rx="365" ry="42" fill="#058DCA" opacity=".09" filter="url(#bg-soft)"/>
    <ellipse cx="840" cy="1885" rx="260" ry="33" fill="#2C4ABB" opacity=".09" filter="url(#bg-soft)"/>
    <circle cx="14" cy="1560" r="2.5" fill="#13CBFF"/><circle cx="1052" cy="1437" r="2" fill="#10BEFF"/>
    <circle cx="1045" cy="1585" r="2" fill="#00ACFF"/>
  </g>
  <path d="M446 133H1007" stroke="#4A77A5" stroke-width="2.5" opacity=".9"/>
  <ellipse class="bg-star" cx="829" cy="133" rx="106" ry="6" fill="url(#bg-flare)"/><ellipse cx="829" cy="133" rx="12" ry="2" fill="#B6F6FF"/>
  <path d="M0 500H1080M0 1308H1080" stroke="url(#bg-edge)" stroke-width="1.8"/>
  <ellipse class="bg-star" cx="903" cy="500" rx="160" ry="12" fill="url(#bg-flare)"/><ellipse class="bg-star" cx="323" cy="1308" rx="163" ry="13" fill="url(#bg-flare)"/>
</svg>`;
}

export function referenceAmbient(config) {
  const { waveLineCount, barCount, particleCount } = config.motion;
  const wavePaths = Array.from({ length: waveLineCount }, (_, i) => {
    const dotted = i % 4 === 3;
    return `<path class="wave-line" data-line="${i}" stroke="url(#wave-spectrum)" stroke-width="${i < 2 ? 2.8 : 1.3}" opacity="${dotted ? .43 : .78 - i * .014}" ${dotted ? 'stroke-dasharray="1.5 7"' : ''} d="M0 0"/>`;
  }).join("");
  const waveGlows = [0, 1, 5, 11, 20].filter(i => i < waveLineCount).map(i => `<path class="wave-glow" data-line="${i}" stroke="url(#wave-spectrum)" stroke-width="${i < 2 ? 9 : 5}" opacity=".43" filter="url(#wave-soft)" d="M0 0"/>`).join("");
  const waveReflections = Array.from({ length: Math.min(12, waveLineCount) }, (_, i) => `<path class="wave-reflection" data-line="${i}" stroke="url(#wave-spectrum)" stroke-width="2.3" opacity=".2" d="M0 0"/>`).join("");
  function bars(extraClass = "") {
    return Array.from({ length: barCount }, (_, i) => {
      const x = ((i + .5) * (1080 / barCount) - 1.5).toFixed(2);
      const color = i % 13 === 0 ? "#7075ED" : i % 3 === 0 ? "#1176CE" : "#00DCFF";
      return `<rect class="${extraClass || "bar"}" data-bar="${i}" x="${x}" y="1810" width="${i % 5 === 0 ? 3.5 : 2.6}" height="20" fill="${color}"/>`;
    }).join("");
  }
  const particles = Array.from({ length: particleCount }, (_, i) => `<circle class="particle" data-particle="${i}" cx="0" cy="0" r="${i % 18 === 0 ? 4.3 : i % 7 === 0 ? 2.2 : 1.05}" fill="${i % 18 === 0 && i % 36 !== 0 ? "#BB7FFF" : "#05D7FF"}"/>`).join("");
  const particleGlows = Array.from({ length: particleCount }, (_, i) => i % 18 === 0 ? `<circle class="particle-halo" data-particle="${i}" cx="0" cy="0" r="14" fill="${i % 36 === 0 ? "#00CFFF" : "#AA60FF"}" filter="url(#particle-soft)"/>` : "").join("");
  const usePlate = Boolean(config.visualStyle?.backgroundPath);
  return { wavePaths: usePlate ? "" : wavePaths, waveGlows: usePlate ? "" : waveGlows, waveReflections: usePlate ? "" : waveReflections, audioBars: bars(), barGlows: bars("bar-glow"), barReflections: bars("bar-reflection"), particles, particleGlows };
}

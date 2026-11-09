/*!
 * CTF Designs — Accessibility Preferences Toolbar (ada.js) v1
 * A lightweight, self-contained accessibility PREFERENCES widget.
 * Install: <script src="https://ctf-widgets.netlify.app/v1/ada.js" defer
 *            data-position="bottom-left" data-color="#7c3aed"
 *            data-statement="/accessibility.html"></script>
 *
 * IMPORTANT: this is a user-side display/preferences overlay (text, contrast,
 * color, reading and focus aids). It does NOT by itself make a site WCAG/ADA
 * "compliant" — real compliance lives in the site's own markup and content.
 * Do not market it as a compliance guarantee.
 */
(function () {
  "use strict";
  if (window.__ctfA11yLoaded) return;
  window.__ctfA11yLoaded = true;

  var script = document.currentScript || (function () {
    var s = document.getElementsByTagName("script"); return s[s.length - 1];
  })();
  var cfg = (script && script.dataset) || {};
  var POS = (cfg.position || "bottom-left").toLowerCase();
  var COLOR = cfg.color || "#7c3aed";
  var STATEMENT = cfg.statement || "";
  var CREDIT = cfg.credit !== "off";
  var STORE = "ctf_a11y_prefs";

  var prefs = {};
  try { prefs = JSON.parse(localStorage.getItem(STORE) || "{}") || {}; } catch (e) {}
  function save() { try { localStorage.setItem(STORE, JSON.stringify(prefs)); } catch (e) {} }

  // ---- step scales ----
  var FONT = [100, 115, 130, 150, 175];          // % (body font-size)
  var SCALE = [1, 1.1, 1.25, 1.5];               // zoom (whole page)
  var LH = [0, 1.5, 1.8, 2.2];                    // 0 = default
  var LS = [0, 0.05, 0.1, 0.18];                  // em
  var ALIGN = ["", "left", "center", "right"];
  var CURSOR = ["", "black", "white"];

  // ---- feature catalog (key + emoji icon + label) ----
  var TOGGLES = [
    ["contrast", "◐", "High Contrast"], ["dark", "🌙", "Dark Mode"],
    ["invert", "🔄", "Invert Colors"], ["mono", "⚫", "Monochrome"],
    ["satHigh", "🌈", "High Saturation"], ["satLow", "💧", "Low Saturation"],
    ["blue", "🛡", "Blue-Light Filter"], ["readable", "T", "Readable Font"],
    ["dyslexia", "Df", "Dyslexia Font"], ["links", "🔗", "Highlight Links"],
    ["titles", "H", "Highlight Titles"], ["hover", "➤", "Highlight Hover"],
    ["focus", "◎", "Highlight Focus"], ["images", "🖼", "Hide Images"],
    ["mute", "🔇", "Mute Sounds"], ["motion", "⏸", "Stop Animations"],
    ["guide", "—", "Reading Guide"], ["mask", "▭", "Reading Mask"],
    ["magnify", "🔎", "Text Magnifier"]
  ];
  var STEPS = [
    ["fontSize", "Font Size", FONT, "%"], ["scale", "Content Scaling", SCALE, "x"],
    ["lineH", "Line Height", LH, ""], ["letterS", "Letter Spacing", LS, ""]
  ];
  var CYCLES = [
    ["align", "Text Align", ALIGN], ["cursor", "Big Cursor", CURSOR]
  ];

  // ---- one-time CSS ----
  var posCss = {
    "bottom-left": "left:18px;bottom:18px", "bottom-right": "right:18px;bottom:18px",
    "top-left": "left:18px;top:18px", "top-right": "right:18px;top:18px"
  }[POS] || "left:18px;bottom:18px";
  var panelH = POS.indexOf("right") > -1 ? "right:18px" : "left:18px";
  var panelV = POS.indexOf("top") > -1 ? "top:84px" : "bottom:84px";

  var css = document.createElement("style");
  css.textContent =
    "html.ctfa11y-readable body,html.ctfa11y-readable body *{font-family:Verdana,Tahoma,Arial,sans-serif!important}" +
    "html.ctfa11y-dyslexia body,html.ctfa11y-dyslexia body *{font-family:'Comic Sans MS','OpenDyslexic',Verdana,sans-serif!important;letter-spacing:.04em!important;word-spacing:.1em!important}" +
    "html.ctfa11y-motion body *,html.ctfa11y-motion body *::before,html.ctfa11y-motion body *::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important;scroll-behavior:auto!important}" +
    "html.ctfa11y-links a{text-decoration:underline!important;text-underline-offset:2px}" +
    "html.ctfa11y-titles h1,html.ctfa11y-titles h2,html.ctfa11y-titles h3,html.ctfa11y-titles h4,html.ctfa11y-titles h5,html.ctfa11y-titles h6{background:rgba(124,92,255,.14)!important;outline:1px dashed " + COLOR + "}" +
    "html.ctfa11y-hover body *:hover{outline:2px solid " + COLOR + "!important}" +
    "html.ctfa11y-focus body :focus{outline:3px solid " + COLOR + "!important;outline-offset:2px!important}" +
    "html.ctfa11y-images body img,html.ctfa11y-images body picture{visibility:hidden!important}" +
    "html.ctfa11y-revmedia body img,html.ctfa11y-revmedia body video,html.ctfa11y-revmedia body picture,html.ctfa11y-revmedia body canvas,html.ctfa11y-revmedia body [style*='background-image']{filter:invert(1) hue-rotate(180deg)!important}" +
    "html.ctfa11y-lh body,html.ctfa11y-lh body *{line-height:var(--ctfa11y-lh)!important}" +
    "html.ctfa11y-ls body,html.ctfa11y-ls body *{letter-spacing:var(--ctfa11y-ls)!important}" +
    "html.ctfa11y-align body p,html.ctfa11y-align body li,html.ctfa11y-align body h1,html.ctfa11y-align body h2,html.ctfa11y-align body h3,html.ctfa11y-align body div{text-align:var(--ctfa11y-align)!important}" +
    "html.ctfa11y-cur-black body,html.ctfa11y-cur-black body *{cursor:url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='48' height='48' viewBox='0 0 24 24'><path d='M5 2l14 11-6 1 4 7-3 1-4-7-5 4z' fill='black' stroke='white'/></svg>\") 4 2,auto!important}" +
    "html.ctfa11y-cur-white body,html.ctfa11y-cur-white body *{cursor:url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='48' height='48' viewBox='0 0 24 24'><path d='M5 2l14 11-6 1 4 7-3 1-4-7-5 4z' fill='white' stroke='black'/></svg>\") 4 2,auto!important}" +
    "#ctfa11y-guide{position:fixed;left:0;right:0;height:14px;background:rgba(124,92,255,.28);border-top:2px solid " + COLOR + ";border-bottom:2px solid " + COLOR + ";z-index:2147483640;pointer-events:none;display:none}" +
    "#ctfa11y-mask-t,#ctfa11y-mask-b{position:fixed;left:0;right:0;background:rgba(0,0,0,.72);z-index:2147483639;pointer-events:none;display:none}" +
    "#ctfa11y-mag{position:fixed;z-index:2147483641;max-width:360px;background:#fff;color:#111;border:2px solid " + COLOR + ";border-radius:10px;padding:10px 14px;font-size:26px;line-height:1.3;box-shadow:0 10px 30px rgba(0,0,0,.3);pointer-events:none;display:none;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif}" +
    "#ctfa11y-btn{position:fixed;" + posCss + ";z-index:2147483646;width:76px;height:76px;border-radius:50%;background:transparent;border:0;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center;padding:0;overflow:hidden}" +
    "#ctfa11y-btn svg{width:100%;height:100%;display:block}" +
    "#ctfa11y-panel{position:fixed;" + panelH + ";" + panelV + ";z-index:2147483646;width:330px;max-width:calc(100vw - 28px);max-height:calc(100vh - 110px);overflow:auto;background:#fff;color:#15161f;border-radius:16px;box-shadow:0 24px 60px rgba(0,0,0,.3);padding:16px;display:none;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif}" +
    "#ctfa11y-panel.open{display:block}#ctfa11y-panel.big{width:430px;font-size:1.05em}" +
    "#ctfa11y-panel h4{margin:0 0 6px;font-size:13px;letter-spacing:.04em;text-transform:uppercase;color:#6b7280}" +
    "#ctfa11y-panel .top{display:flex;gap:8px;margin-bottom:10px}" +
    "#ctfa11y-panel .top button{flex:1;border:1px solid #e4e7ee;background:#f6f7fb;border-radius:9px;padding:8px;font-size:12px;cursor:pointer;color:#15161f;font-family:inherit}" +
    "#ctfa11y-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}" +
    "#ctfa11y-panel .tile{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;background:#f6f7fb;border:1px solid #e4e7ee;color:#15161f;border-radius:11px;padding:10px 6px;font-size:11.5px;text-align:center;cursor:pointer;font-family:inherit;min-height:64px}" +
    "#ctfa11y-panel .tile .ic{font-size:18px;line-height:1;font-weight:700}" +
    "#ctfa11y-panel .tile[aria-pressed=true]{border-color:" + COLOR + ";background:rgba(124,92,255,.1);color:" + COLOR + ";font-weight:600}" +
    "#ctfa11y-panel .step{grid-column:span 3;display:flex;align-items:center;justify-content:space-between;background:#f6f7fb;border:1px solid #e4e7ee;border-radius:11px;padding:8px 12px;font-size:12.5px}" +
    "#ctfa11y-panel .step .sv{font-weight:700;min-width:54px;text-align:center}" +
    "#ctfa11y-panel .step button{width:30px;height:30px;border-radius:50%;border:1px solid #d7dbe6;background:#fff;cursor:pointer;font-size:16px;color:#15161f}" +
    "#ctfa11y-panel .row2{display:flex;gap:8px;margin-top:8px}#ctfa11y-panel .row2 button{flex:1;border:1px solid #e4e7ee;background:#fff;border-radius:9px;padding:9px;font-size:12.5px;cursor:pointer;color:#b4232a;font-weight:600;font-family:inherit}" +
    "#ctfa11y-panel .cred{margin-top:10px;font-size:11px;color:#9aa1ad;text-align:center}#ctfa11y-panel .cred a{color:" + COLOR + ";text-decoration:none}";
  (document.head || document.documentElement).appendChild(css);

  // ---- overlay elements ----
  var guide, maskT, maskB, mag, moveBound = false;
  function el(tag, id) { var n = document.createElement(tag); if (id) n.id = id; return n; }
  function ensureOverlays() {
    if (guide) return;
    guide = el("div", "ctfa11y-guide"); maskT = el("div", "ctfa11y-mask-t");
    maskB = el("div", "ctfa11y-mask-b"); mag = el("div", "ctfa11y-mag");
    [guide, maskT, maskB, mag].forEach(function (n) { document.documentElement.appendChild(n); });
  }
  function onMove(e) {
    var y = e.clientY;
    if (prefs.guide && guide) { guide.style.top = (y - 7) + "px"; guide.style.display = "block"; } else if (guide) guide.style.display = "none";
    if (prefs.mask && maskT) {
      maskT.style.top = "0"; maskT.style.height = Math.max(0, y - 55) + "px"; maskT.style.display = "block";
      maskB.style.top = (y + 55) + "px"; maskB.style.bottom = "0"; maskB.style.display = "block";
    } else if (maskT) { maskT.style.display = "none"; maskB.style.display = "none"; }
    if (prefs.magnify && mag) {
      var t = document.elementFromPoint(e.clientX, e.clientY);
      var txt = t && (t.innerText || t.textContent || t.alt || "");
      txt = txt ? txt.trim().slice(0, 220) : "";
      if (txt) {
        mag.textContent = txt; mag.style.display = "block";
        var mx = Math.min(e.clientX + 16, window.innerWidth - 380);
        var my = Math.min(e.clientY + 16, window.innerHeight - 120);
        mag.style.left = Math.max(8, mx) + "px"; mag.style.top = Math.max(8, my) + "px";
      } else mag.style.display = "none";
    } else if (mag) mag.style.display = "none";
  }
  function applyMute() {
    var on = !!prefs.mute;
    Array.prototype.forEach.call(document.querySelectorAll("audio,video"), function (m) { m.muted = on; });
  }

  // ---- apply all prefs ----
  function apply() {
    var h = document.documentElement;
    var f = [];
    if (prefs.contrast) f.push("contrast(1.4)");
    if (prefs.mono) f.push("grayscale(1)");
    if (prefs.satHigh) f.push("saturate(1.9)");
    if (prefs.satLow) f.push("saturate(.5)");
    if (prefs.blue) f.push("sepia(.4) hue-rotate(180deg)");
    if (prefs.invert || prefs.dark) f.push("invert(1) hue-rotate(180deg)");
    if (prefs.dark && !prefs.invert) f.push("brightness(.95)");
    try { document.body.style.filter = f.join(" "); } catch (e) {}
    h.classList.toggle("ctfa11y-revmedia", !!(prefs.invert || prefs.dark));
    [["readable", prefs.readable], ["dyslexia", prefs.dyslexia], ["motion", prefs.motion],
     ["links", prefs.links], ["titles", prefs.titles], ["hover", prefs.hover],
     ["focus", prefs.focus], ["images", prefs.images]].forEach(function (p) {
      h.classList.toggle("ctfa11y-" + p[0], !!p[1]);
    });
    try { document.body.style.fontSize = FONT[prefs.fontSize || 0] + "%"; } catch (e) {}
    try { document.body.style.zoom = SCALE[prefs.scale || 0]; } catch (e) {}
    var lh = LH[prefs.lineH || 0]; h.classList.toggle("ctfa11y-lh", !!lh); if (lh) h.style.setProperty("--ctfa11y-lh", lh);
    var ls = LS[prefs.letterS || 0]; h.classList.toggle("ctfa11y-ls", !!ls); if (ls) h.style.setProperty("--ctfa11y-ls", ls + "em");
    var al = ALIGN[prefs.align || 0]; h.classList.toggle("ctfa11y-align", !!al); if (al) h.style.setProperty("--ctfa11y-align", al);
    h.classList.toggle("ctfa11y-cur-black", CURSOR[prefs.cursor || 0] === "black");
    h.classList.toggle("ctfa11y-cur-white", CURSOR[prefs.cursor || 0] === "white");
    if (prefs.guide || prefs.mask || prefs.magnify) {
      ensureOverlays();
      if (!moveBound) { document.addEventListener("mousemove", onMove); moveBound = true; }
    } else if (guide) { guide.style.display = maskT.style.display = maskB.style.display = mag.style.display = "none"; }
    applyMute(); syncUI(); save();
  }

  function syncUI() {
    if (!panel) return;
    panel.querySelectorAll("[data-tog]").forEach(function (b) { b.setAttribute("aria-pressed", prefs[b.dataset.tog] ? "true" : "false"); });
    panel.querySelectorAll("[data-cyc]").forEach(function (b) { b.setAttribute("aria-pressed", (prefs[b.dataset.cyc] || 0) > 0 ? "true" : "false"); });
    STEPS.forEach(function (s) {
      var v = document.getElementById("ctfa11y-sv-" + s[0]); if (!v) return;
      var idx = prefs[s[0]] || 0, arr = s[2], unit = s[3];
      v.textContent = s[0] === "fontSize" ? arr[idx] + "%" : (s[0] === "scale" ? Math.round(arr[idx] * 100) + "%" : (idx === 0 ? "Off" : arr[idx] + unit));
    });
  }

  // ---- build panel ----
  var ICON = '<svg viewBox="0 0 100 100" aria-hidden="true">' +
    '<circle cx="50" cy="50" r="50" fill="#3d1273"/>' +
    '<circle cx="50" cy="50" r="40" fill="none" stroke="#fff" stroke-width="6"/>' +
    '<circle cx="50" cy="33" r="7.5" fill="#fff"/>' +
    '<path d="M30 46 H70 M50 42 V60 M50 60 L38 77 M50 60 L62 77" fill="none" stroke="#fff" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var btn = document.createElement("button");
  btn.id = "ctfa11y-btn"; btn.setAttribute("aria-label", "Screen overlay options"); btn.setAttribute("aria-expanded", "false");
  btn.innerHTML = ICON;

  var panel = document.createElement("div");
  panel.id = "ctfa11y-panel"; panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", "Screen overlay options");
  if (prefs.big) panel.classList.add("big");

  var html = '<h4>Screen Overlay</h4><div class="top">' +
    '<button data-act="oversize">⤢ Oversize</button>' +
    (STATEMENT ? '<button data-act="statement">📄 Statement</button>' : '') +
    '</div><div id="ctfa11y-grid">';
  STEPS.forEach(function (s) {
    html += '<div class="step"><span>' + s[1] + '</span><span><button data-step="' + s[0] + '" data-dir="-1">−</button>' +
      '<span class="sv" id="ctfa11y-sv-' + s[0] + '">·</span><button data-step="' + s[0] + '" data-dir="1">+</button></span></div>';
  });
  TOGGLES.forEach(function (t) {
    html += '<button class="tile" data-tog="' + t[0] + '" aria-pressed="false"><span class="ic">' + t[1] + '</span>' + t[2] + '</button>';
  });
  CYCLES.forEach(function (c) {
    html += '<button class="tile" data-cyc="' + c[0] + '" aria-pressed="false"><span class="ic">↻</span>' + c[1] + '</button>';
  });
  html += '</div><div class="row2"><button data-act="reset">↺ Reset all</button><button data-act="hide">⊘ Hide widget</button></div>' +
    (CREDIT ? '<div class="cred">Screen overlay by <a href="https://ctfdesigns.com" target="_blank" rel="noopener">CTF Designs</a></div>' : '');
  panel.innerHTML = html;

  function toggleOpen(force) {
    var open = force != null ? force : !panel.classList.contains("open");
    panel.classList.toggle("open", open); btn.setAttribute("aria-expanded", open ? "true" : "false");
  }

  function mount() {
    document.documentElement.appendChild(btn);
    document.documentElement.appendChild(panel);
    btn.addEventListener("click", function () { toggleOpen(); });
    document.addEventListener("click", function (e) {
      if (panel.classList.contains("open") && !panel.contains(e.target) && e.target !== btn && !btn.contains(e.target)) toggleOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") toggleOpen(false);
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === "A" || e.key === "a")) { e.preventDefault(); toggleOpen(); }
    });
    panel.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      if (b.dataset.tog) { prefs[b.dataset.tog] = !prefs[b.dataset.tog]; apply(); }
      else if (b.dataset.cyc) { var arr = ({ align: ALIGN, cursor: CURSOR })[b.dataset.cyc]; prefs[b.dataset.cyc] = ((prefs[b.dataset.cyc] || 0) + 1) % arr.length; apply(); }
      else if (b.dataset.step) {
        var key = b.dataset.step, dir = +b.dataset.dir, max = ({ fontSize: FONT, scale: SCALE, lineH: LH, letterS: LS })[key].length - 1;
        prefs[key] = Math.max(0, Math.min(max, (prefs[key] || 0) + dir)); apply();
      } else if (b.dataset.act === "reset") { prefs = {}; try { document.body.style.filter = ""; document.body.style.fontSize = ""; document.body.style.zoom = ""; } catch (e2) {} apply(); }
      else if (b.dataset.act === "hide") { btn.style.display = "none"; toggleOpen(false); }
      else if (b.dataset.act === "oversize") { prefs.big = !prefs.big; panel.classList.toggle("big", !!prefs.big); save(); }
      else if (b.dataset.act === "statement" && STATEMENT) { window.open(STATEMENT, "_blank", "noopener"); }
    });
    apply();
  }
  if (document.body) mount();
  else document.addEventListener("DOMContentLoaded", mount);
})();

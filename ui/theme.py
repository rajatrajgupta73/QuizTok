"""Citi-branded QuizTok theme — pure local CSS (system fonts only, zero internet)."""
import streamlit as st
import streamlit.components.v1 as st_components

_CSS = """
<style>
/* ================= base ================= */
:root {
  --citi-navy: #003b70; --citi-blue: #0088ce; --citi-sky: #4db4ff;
  --citi-red: #e21836; --gold: #ffc233; --teal: #00c9a7;
  --glass: rgba(255,255,255,0.06); --stroke: rgba(255,255,255,0.14);
  --text: #eef5ff; --dim: #9db4d0;
}
html, body, [class*="css"] {
  font-family: "Segoe UI", "Trebuchet MS", Arial, sans-serif;
}
.stApp {
  background:
    radial-gradient(1100px 700px at 85% -10%, #0c2a52 0%, transparent 60%),
    radial-gradient(900px 600px at -10% 110%, #0a2246 0%, transparent 55%),
    linear-gradient(160deg, #050d1c 0%, #081c38 100%) !important;
  color: var(--text);
}
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.2rem; max-width: 1150px; }

/* floating orbs */
.qt-orb { position: fixed; border-radius: 50%; filter: blur(70px); opacity: .45; z-index: 0; pointer-events: none;
  animation: qtDrift 18s ease-in-out infinite alternate; }
@keyframes qtDrift { from { transform: translate(0,0) scale(1);} to { transform: translate(80px,50px) scale(1.12);} }

/* ================= keyframes ================= */
@keyframes qtRise { from { opacity:0; transform: translateY(24px);} to { opacity:1; transform:none;} }
@keyframes qtPop { from { opacity:0; transform: scale(.6);} to { opacity:1; transform: scale(1);} }
@keyframes qtBounce { 0%,100% { transform: translateY(0);} 50% { transform: translateY(-10px);} }
@keyframes qtPulse { 50% { box-shadow: 0 0 0 6px rgba(0,201,167,.15);} }
@keyframes qtGlow { 0%,100% { text-shadow: 0 0 18px rgba(77,180,255,.35);} 50% { text-shadow: 0 0 42px rgba(77,180,255,.7);} }
@keyframes qtGrow { from { transform: scaleY(0);} to { transform: scaleY(1);} }
@keyframes qtFall { 0% { transform: translateY(-5vh) rotate(0); opacity:1;} 100% { transform: translateY(106vh) rotate(720deg); opacity:.6;} }
@keyframes qtShine { 0%,60% { left:-80%;} 100% { left:130%;} }

.qt-rise { animation: qtRise .6s cubic-bezier(.22,1,.36,1) both; }

/* ================= brand / topbar ================= */
.qt-topbar { display:flex; align-items:center; gap:14px; padding: 6px 2px 14px;
  border-bottom: 1px solid var(--stroke); margin-bottom: 18px; position: relative; z-index: 1; }
.qt-brand { font-weight: 900; font-size: 30px; letter-spacing: -.5px;
  background: linear-gradient(92deg, #4db4ff, #9be1ff 45%, #ff5d73);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
.qt-div { width:1px; height:26px; background: var(--stroke); }
.qt-spacer { flex: 1; }

.qt-pill { padding: 6px 14px; border-radius: 999px; background: var(--glass);
  border: 1px solid var(--stroke); font-size: 13px; font-weight: 600; color: var(--dim);
  display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; }
.qt-pill b { color: var(--gold); }
.qt-pill .dot { width:8px; height:8px; border-radius:50%; background: var(--teal); animation: qtPulse 1.6s infinite; }
.qt-pill.red { background: rgba(226,24,54,.15); border-color: rgba(226,24,54,.4); color: #ff7b8d; }

/* ================= cards & text ================= */
.qt-card { background: var(--glass); border: 1px solid var(--stroke); border-radius: 20px;
  padding: 22px 26px; box-shadow: 0 20px 60px rgba(0,0,0,.35); position: relative; z-index: 1; }
.qt-h1 { font-size: 46px; font-weight: 900; line-height: 1.05; color: var(--text); }
.qt-sub { color: var(--dim); font-size: 15px; }
.qt-arc { display:block; margin: 6px 0 14px; }

/* pin banner */
.qt-pin { font-size: 64px; font-weight: 900; letter-spacing: 12px; text-align:center;
  background: linear-gradient(92deg, #4db4ff, #9be1ff, #ffd76e);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
  animation: qtGlow 2.4s ease-in-out infinite; }

/* player chips */
.qt-chips { display:flex; flex-wrap: wrap; gap: 10px; }
.qt-chip { display:inline-flex; align-items:center; gap:8px; padding: 7px 16px 7px 8px;
  background: rgba(255,255,255,.1); border: 1px solid var(--stroke); border-radius: 999px;
  font-weight: 600; font-size: 14px; color: var(--text); animation: qtPop .45s cubic-bezier(.34,1.56,.64,1) both; }
.qt-chip .em { font-size: 19px; width: 30px; height: 30px; border-radius: 50%;
  background: rgba(0,0,0,.3); display:flex; align-items:center; justify-content:center; }
.qt-chip .tm { font-size: 11px; color: var(--citi-sky); font-weight: 700; }

/* HUD */
.qt-hud { display:flex; align-items:center; gap:14px; flex-wrap:wrap; margin-bottom: 12px; }
.qt-hud .qno { font-weight: 800; font-size: 18px; color: var(--citi-sky); }
.qt-hud .bar { flex:1; min-width: 120px; height: 10px; background: rgba(0,0,0,.35); border-radius: 99px; overflow:hidden; }
.qt-hud .bar i { display:block; height:100%; border-radius:99px;
  background: linear-gradient(90deg, var(--citi-blue), var(--citi-sky)); box-shadow: 0 0 12px rgba(77,180,255,.6); }
.qt-streak { display:inline-flex; align-items:center; gap:6px; font-weight:800; font-size:15px; color: var(--text);
  background: linear-gradient(135deg, rgba(255,100,40,.25), rgba(255,60,60,.15));
  border: 1px solid rgba(255,140,60,.4); padding: 6px 14px; border-radius: 999px; }
.qt-streak .fl { animation: qtBounce 1s ease-in-out infinite; display:inline-block; }
.qt-score { font-weight: 900; font-size: 17px; color: var(--text); background: var(--glass);
  border: 1px solid var(--stroke); padding: 6px 16px; border-radius: 999px; }
.qt-score b { color: var(--gold); }

/* timer */
.qt-timerwrap { display:flex; justify-content:center; margin: 4px 0 10px; }
.qt-timer { position: relative; width: 86px; height: 86px; }
.qt-timer svg { transform: rotate(-90deg); }
.qt-timer .num { position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-size: 30px; font-weight: 900; color: var(--text); }
.qt-timer.danger .num { color: var(--citi-red); }

/* question text */
.qt-question { text-align:center; font-size: 26px; font-weight: 700; line-height: 1.4;
  color: var(--text); margin: 6px auto 18px; max-width: 820px; }
.qt-cat { text-align:center; font-size: 12px; letter-spacing: 2.5px; color: var(--citi-sky);
  font-weight: 700; margin-bottom: 6px; text-transform: uppercase; }

/* verdict */
.qt-verdict { text-align:center; padding: 26px 10px 8px; animation: qtPop .5s cubic-bezier(.34,1.56,.64,1) both; }
.qt-verdict .big { font-size: 52px; font-weight: 900; }
.qt-verdict .big.good { color: var(--teal); text-shadow: 0 0 40px rgba(0,201,167,.5); }
.qt-verdict .big.bad { color: var(--citi-red); text-shadow: 0 0 40px rgba(226,24,54,.45); }
.qt-verdict .sub { color: var(--dim); font-size: 16px; margin-top: 6px; }
.qt-verdict .sub b { color: var(--gold); }

/* podium */
.qt-podium { display:flex; align-items:flex-end; justify-content:center; gap:18px; margin: 18px 0 8px; }
.qt-step { text-align:center; width: 150px; }
.qt-step .av { font-size: 40px; animation: qtBounce 2.6s ease-in-out infinite; }
.qt-step .who { font-weight: 700; font-size: 15px; color: var(--text); }
.qt-step .pts { font-weight: 900; color: var(--gold); font-size: 16px; margin-bottom: 8px; }
.qt-step .blk { border-radius: 14px 14px 0 0; display:flex; align-items:flex-start; justify-content:center;
  padding-top: 10px; font-size: 32px; font-weight: 900; color: rgba(255,255,255,.85);
  animation: qtGrow .9s cubic-bezier(.22,1,.36,1) both; transform-origin: bottom; }
.qt-step.p1 .blk { height: 150px; background: linear-gradient(180deg,#ffd76e,#b8860b); box-shadow: 0 0 40px rgba(255,194,51,.3); animation-delay:.7s; }
.qt-step.p2 .blk { height: 110px; background: linear-gradient(180deg,#b9d4f0,#5f7d9c); animation-delay:.4s; }
.qt-step.p3 .blk { height: 82px;  background: linear-gradient(180deg,#e8a06b,#9c5a2e); animation-delay:.15s; }
.qt-step .crown { font-size: 28px; display:block; animation: qtBounce 1.6s ease-in-out infinite; }

/* rank rows */
.qt-row { display:flex; align-items:center; gap:14px; padding: 10px 18px; margin-bottom: 8px;
  background: var(--glass); border: 1px solid var(--stroke); border-radius: 16px;
  animation: qtRise .5s both; color: var(--text); }
.qt-row .rk { font-weight: 900; width: 36px; color: var(--dim); }
.qt-row .em { font-size: 22px; }
.qt-row .nm { font-weight: 700; flex: 1; }
.qt-row .nm .tm { font-size: 11px; color: var(--citi-sky); font-weight: 700; margin-left: 8px; }
.qt-row .pt { font-weight: 900; color: var(--gold); }
.qt-row.me { border-color: rgba(77,180,255,.55); background: linear-gradient(135deg, rgba(0,136,206,.22), rgba(0,59,112,.28)); }
.qt-row.me .nm::after { content: " — YOU"; color: var(--citi-sky); font-size: 11px; letter-spacing: 1px; }

/* voting cards */
.qt-vote { background: var(--glass); border: 1px solid var(--stroke); border-radius: 16px;
  padding: 16px 18px; margin-bottom: 6px; color: var(--text); animation: qtRise .5s both; }
.qt-vote .who { font-weight: 700; font-size: 14px; color: var(--citi-sky); margin-bottom: 6px; }
.qt-vote .txt { font-size: 15.5px; line-height: 1.55; }
.qt-vote .cnt { float: right; font-weight: 900; color: var(--gold); }

/* distribution bars (host) */
.qt-bars { display:flex; align-items:flex-end; justify-content:center; gap: 22px; height: 170px; margin: 14px 0 4px; }
.qt-barcol { display:flex; flex-direction:column; align-items:center; width: 84px; height: 100%; justify-content:flex-end; gap: 6px; }
.qt-bar { width: 100%; border-radius: 10px 10px 4px 4px; display:flex; align-items:flex-start;
  justify-content:center; padding-top: 6px; font-weight: 900; color: #fff;
  animation: qtGrow .8s cubic-bezier(.22,1,.36,1) both; transform-origin: bottom; }
.qt-barcol .lb { font-size: 12px; color: var(--dim); font-weight: 600; text-align: center; }
.qt-barcol.win .lb { color: var(--teal); font-weight: 800; }

/* confetti */
.qt-cf { position: fixed; top: -20px; border-radius: 3px; z-index: 9; pointer-events: none; animation: qtFall linear forwards; }

/* awards */
.qt-award { display:inline-flex; align-items:center; gap:8px; padding: 10px 18px; margin: 4px 6px 4px 0;
  border-radius: 14px; font-size: 14px; font-weight: 600; color: var(--text);
  background: var(--glass); border: 1px solid var(--stroke); animation: qtPop .5s both; }
.qt-award b { color: var(--citi-sky); }

/* kpi cards */
.qt-kpi { background: var(--glass); border: 1px solid var(--stroke); border-radius: 18px;
  padding: 18px 20px; text-align:center; animation: qtRise .6s both; }
.qt-kpi .n { font-size: 30px; font-weight: 900; color: var(--citi-sky); }
.qt-kpi .l { font-size: 11.5px; letter-spacing: 1px; color: var(--dim); font-weight: 700; }

/* ================= streamlit widget styling ================= */
.stButton > button, .stFormSubmitButton > button {
  border-radius: 999px !important; border: none !important; font-weight: 700 !important;
  padding: 12px 26px !important; font-size: 16px !important; color: #fff !important;
  background: linear-gradient(135deg, #0088ce, #003b70) !important;
  box-shadow: 0 8px 22px rgba(0,136,206,.35) !important;
  transition: transform .18s cubic-bezier(.34,1.56,.64,1), box-shadow .2s !important;
  position: relative; overflow: hidden;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
  transform: translateY(-3px) scale(1.02); box-shadow: 0 14px 30px rgba(0,136,206,.5) !important; }
.stButton > button:active { transform: scale(.97); }

/* secondary = ghost */
.stButton > button[kind="secondary"] {
  background: rgba(255,255,255,.08) !important; border: 1px solid var(--stroke) !important;
  box-shadow: none !important; color: var(--text) !important;
}

/* answer buttons — Kahoot colours via container keys
   (".stButton > button" kept in the selector to out-rank the ghost rule above) */
div[class*="st-key-ans0"] .stButton > button { background: linear-gradient(135deg,#0088ce,#005a9e) !important; }
div[class*="st-key-ans1"] .stButton > button { background: linear-gradient(135deg,#e21836,#a80f26) !important; box-shadow: 0 8px 22px rgba(226,24,54,.35) !important; }
div[class*="st-key-ans2"] .stButton > button { background: linear-gradient(135deg,#00c9a7,#00806a) !important; box-shadow: 0 8px 22px rgba(0,201,167,.3) !important; }
div[class*="st-key-ans3"] .stButton > button { background: linear-gradient(135deg,#ff9d2e,#d97706) !important; box-shadow: 0 8px 22px rgba(255,157,46,.3) !important; }
div[class*="st-key-ans"] .stButton > button {
  min-height: 84px !important; font-size: 18px !important; font-weight: 700 !important;
  border-radius: 18px !important; white-space: normal !important; text-align: left !important;
  color: #fff !important;
}

/* red / gold / vote variants */
div[class*="st-key-red"] .stButton > button { background: linear-gradient(135deg,#ff415e,#e21836) !important; color: #fff !important; box-shadow: 0 8px 22px rgba(226,24,54,.4) !important; border: none !important; }
div[class*="st-key-gold"] .stButton > button { background: linear-gradient(135deg,#ffd76e,#ff9d2e) !important; color: #3a2400 !important; box-shadow: 0 8px 22px rgba(255,194,51,.35) !important; border: none !important; }
div[class*="st-key-vote"] .stButton > button { background: linear-gradient(135deg,#7c5cff,#4b32b4) !important; color: #fff !important; box-shadow: 0 8px 22px rgba(124,92,255,.35) !important; border: none !important; }
div[class*="st-key-avat"] .stButton > button {
  background: rgba(0,0,0,.28) !important; border: 2px solid var(--stroke) !important;
  font-size: 26px !important; min-height: 60px !important; border-radius: 16px !important;
  box-shadow: none !important; padding: 6px !important;
}
div[class*="st-key-avat"] .stButton > button:hover { border-color: var(--citi-sky) !important; transform: scale(1.12) rotate(-5deg); }

/* inputs */
.stTextInput input, .stTextArea textarea, .stNumberInput input,
div[data-baseweb="select"] > div {
  background: rgba(0,0,0,.28) !important; border: 1.5px solid var(--stroke) !important;
  border-radius: 13px !important; color: var(--text) !important; font-size: 15px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--citi-sky) !important; box-shadow: 0 0 0 4px rgba(77,180,255,.15) !important; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label,
.stMultiSelect label, .stSlider label, .stCheckbox label, .stRadio label {
  color: var(--dim) !important; font-weight: 600 !important; }

/* big PIN entry */
div[class*="st-key-pinbox"] input {
  text-align: center; font-size: 28px !important; letter-spacing: 10px; font-weight: 800; }

/* tabs */
.stTabs [data-baseweb="tab-list"] { background: rgba(0,0,0,.3); border-radius: 999px; padding: 5px; gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 999px; font-weight: 700; color: var(--dim); padding: 8px 20px; }
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg,#0088ce,#003b70) !important; color: #fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* dataframe + metric */
[data-testid="stMetric"] { background: var(--glass); border: 1px solid var(--stroke);
  border-radius: 16px; padding: 14px 18px; }
[data-testid="stMetricValue"] { color: var(--citi-sky); font-weight: 800; }
[data-testid="stMetricLabel"] { color: var(--dim); }

.stAlert { border-radius: 14px; }
.stProgress > div > div { background: linear-gradient(90deg, var(--citi-blue), var(--citi-sky)) !important; }

/* cursor glow / mouse spotlight (div is created by JS, moved via transform) */
#qt-glow {
  position: fixed; top: 0; left: 0; width: 460px; height: 460px;
  border-radius: 50%; pointer-events: none; z-index: 3; opacity: 0;
  transition: opacity .4s ease;
  background: radial-gradient(circle,
    rgba(77,180,255,.16) 0%, rgba(0,136,206,.09) 30%,
    rgba(226,24,54,.04) 55%, transparent 72%);
  mix-blend-mode: screen;
}

/* ink-in-water fluid trail (canvas created by JS, painted every frame) */
#qt-ink {
  position: fixed; inset: 0; pointer-events: none; z-index: 2;
  filter: blur(14px) saturate(1.35);
  mix-blend-mode: screen; opacity: .85;
}
</style>
<div class="qt-orb" style="width:440px;height:440px;background:#005a9e;top:-150px;left:-110px;"></div>
<div class="qt-orb" style="width:360px;height:360px;background:#e2183655;bottom:-110px;right:-70px;animation-delay:-6s;"></div>
<div class="qt-orb" style="width:280px;height:280px;background:#0088ce66;top:45%;left:60%;animation-delay:-12s;"></div>
"""


# Cursor effects: scripts inside st.markdown never execute, so this runs in a
# zero-height component iframe and drives layers on the parent page:
#   #qt-glow — soft spotlight that lerps behind the cursor
#   #qt-ink  — ink-in-water fluid trail: drops spawn at the cursor, swell,
#              swirl and dissolve on a blurred additive canvas
# A generation counter lets a remounted iframe take over cleanly (old
# listeners removed, old paint loop stops) so the effect survives reruns.
_GLOW_JS = """
<script>
(function () {
  const P = window.parent, doc = P.document;
  P.__qtFxGen = (P.__qtFxGen || 0) + 1;
  const gen = P.__qtFxGen;
  if (P.__qtFxCleanup) { try { P.__qtFxCleanup(); } catch (e) {} }

  // ---- layers ----
  let glow = doc.getElementById("qt-glow");
  if (!glow) { glow = doc.createElement("div"); glow.id = "qt-glow"; doc.body.appendChild(glow); }
  let cv = doc.getElementById("qt-ink");
  if (!cv) { cv = doc.createElement("canvas"); cv.id = "qt-ink"; doc.body.appendChild(cv); }
  const ctx = cv.getContext("2d");
  function resize() { cv.width = P.innerWidth; cv.height = P.innerHeight; }
  resize();

  // ---- state ----
  const PALETTE = [[77,180,255],[0,136,206],[226,24,54],[255,194,51],[124,92,255],[0,201,167]];
  const drops = [];
  let tx = -600, ty = -600, x = tx, y = ty, lastSpawn = 0;

  function onMove(e) {
    tx = e.clientX; ty = e.clientY;
    glow.style.opacity = "1";
    const now = performance.now();
    if (now - lastSpawn < 18) return;               // spawn rate limit
    lastSpawn = now;
    const c = PALETTE[(Math.random() * PALETTE.length) | 0];
    drops.push({
      x: tx, y: ty,
      r: 5 + Math.random() * 9,                     // ink drop starts small…
      grow: 1.4 + Math.random() * 2.2,              // …and blooms outward
      a: 0.55,
      dx: (Math.random() - 0.5) * 1.4,              // slow drift
      dy: (Math.random() - 0.5) * 1.4 - 0.25,       // slight upward buoyancy
      swirl: Math.random() * 6.283, c,
    });
    if (drops.length > 130) drops.splice(0, drops.length - 130);
  }
  function onLeave() { glow.style.opacity = "0"; }

  doc.addEventListener("mousemove", onMove);
  doc.addEventListener("mouseleave", onLeave);
  P.addEventListener("resize", resize);
  P.__qtFxCleanup = () => {
    doc.removeEventListener("mousemove", onMove);
    doc.removeEventListener("mouseleave", onLeave);
    P.removeEventListener("resize", resize);
  };

  // ---- paint loop ----
  (function loop() {
    if (P.__qtFxGen !== gen) return;                // a newer iframe took over
    x += (tx - x) * 0.16;                           // lerp = soft trailing glow
    y += (ty - y) * 0.16;
    glow.style.transform = `translate(${x - 230}px, ${y - 230}px)`;

    ctx.clearRect(0, 0, cv.width, cv.height);
    ctx.globalCompositeOperation = "lighter";       // additive = luminous fluid
    for (let i = drops.length - 1; i >= 0; i--) {
      const d = drops[i];
      d.r += d.grow; d.grow *= 0.985;               // diffusion slows over time
      d.a *= 0.955;                                 // ink fades as it spreads
      d.swirl += 0.05;
      d.x += d.dx + Math.cos(d.swirl) * 0.7;        // curling water currents
      d.y += d.dy + Math.sin(d.swirl * 0.8) * 0.55;
      if (d.a < 0.012) { drops.splice(i, 1); continue; }
      const g = ctx.createRadialGradient(d.x, d.y, 0, d.x, d.y, d.r);
      g.addColorStop(0, `rgba(${d.c[0]},${d.c[1]},${d.c[2]},${d.a})`);
      g.addColorStop(1, `rgba(${d.c[0]},${d.c[1]},${d.c[2]},0)`);
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, 6.283); ctx.fill();
    }
    P.requestAnimationFrame(loop);
  })();
})();
</script>
"""


def inject() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    st_components.html(_GLOW_JS, height=0)

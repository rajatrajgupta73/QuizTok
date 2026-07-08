"""ABC Company-branded QuizTok theme — matches the HTML prototype design."""
import streamlit as st
import streamlit.components.v1 as st_components

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&family=Baloo+2:wght@600;700;800&display=swap');
/* ================= base ================= */
:root {
  --abc-navy: #003b70; --abc-blue: #0088ce; --abc-sky: #4db4ff;
  --abc-red: #e21836; --gold: #ffc233; --teal: #00c9a7;
  --glass: rgba(255,255,255,0.06); --stroke: rgba(255,255,255,0.14);
  --text: #eef5ff; --dim: #9db4d0;
  --radius: 22px;
}
html, body, [class*="css"] {
  font-family: 'Poppins', "Segoe UI", Arial, sans-serif;
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
/* Headless feel — hide Streamlit's loading/refresh indicators */
[data-testid="stStatusWidget"] { visibility: hidden !important; }
[data-testid="stDecoration"]  { display: none !important; }
/* content sits above the floating background symbols (.qt-floaters) */
[data-testid="stAppViewContainer"] { position: relative; isolation: isolate; min-height: 100vh; }
.block-container { padding-top: 1.2rem; max-width: 1150px; position: relative; z-index: 2; }
[data-testid="stMain"],
section.main { position: relative; z-index: 2; }
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="stColumn"],
[data-testid="column"],
[data-testid="stMarkdownContainer"],
[data-testid="stTextInput"],
[data-testid="stForm"],
.stTabs,
[data-testid="stWidget"] { position: relative; z-index: 2; }

/* transition-page particles must never leak into the next page's layout */
*:not(#qt-tr) > .qt-tr-pt { display: none !important; }

/* transition — hide ghost login DOM that Streamlit has not pruned yet */
body:has(.qt-transition-scope) [data-testid="stVerticalBlockBorderWrapper"]:has(.qt-login-scope) {
  display: none !important;
}
body:has(.qt-transition-scope) [data-testid="stAppViewContainer"] {
  background: #010811 !important;
}
body:has(.qt-transition-scope) #qt-tr {
  z-index: 99999 !important;
}

/* Hide Streamlit form instruction tooltips */
[data-testid="stFormSubmitButton"] + div[data-testid="stMarkdownContainer"],
.stForm [data-testid="InputInstructions"],
.stTextInput [data-testid="InputInstructions"],
input[type="text"]::placeholder,
input[type="email"]::placeholder,
input[type="password"]::placeholder {
  /* Keep placeholders visible but hide instruction text */
}
[data-testid="InputInstructions"] { display: none !important; }
.stTextInput > div[data-testid="stMarkdownContainer"]:last-child { display: none !important; }
div[class*="InputInstructions"] { display: none !important; }

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
/* page header — brand bar + logout/exit stay on one row */
[data-testid="stHorizontalBlock"]:has(.qt-topbar) {
  flex-wrap: nowrap !important;
  align-items: center !important;
}
[data-testid="stHorizontalBlock"]:has(.qt-topbar) > [data-testid="stColumn"]:first-child,
[data-testid="stHorizontalBlock"]:has(.qt-topbar) > [data-testid="column"]:first-child {
  flex: 1 1 auto !important;
  min-width: 0 !important;
}
[data-testid="stHorizontalBlock"]:has(.qt-topbar) > [data-testid="stColumn"]:last-child,
[data-testid="stHorizontalBlock"]:has(.qt-topbar) > [data-testid="column"]:last-child {
  flex: 0 0 auto !important;
  width: auto !important;
  min-width: max-content !important;
}
div[class*="st-key-quiz_logout"] .stButton > button,
div[class*="st-key-results_exit"] .stButton > button,
div[class*="st-key-lobby_leave"] .stButton > button,
div[class*="st-key-hub_logout"] .stButton > button,
div[class*="st-key-qt_logout"] .stButton > button,
div[class*="st-key-admin_logout"] .stButton > button,
div[class*="st-key-host_logout"] .stButton > button {
  white-space: nowrap !important;
}
div[class*="st-key-quiz_logout"] .stButton > button p,
div[class*="st-key-results_exit"] .stButton > button p,
div[class*="st-key-lobby_leave"] .stButton > button p,
div[class*="st-key-hub_logout"] .stButton > button p,
div[class*="st-key-qt_logout"] .stButton > button p,
div[class*="st-key-admin_logout"] .stButton > button p,
div[class*="st-key-host_logout"] .stButton > button p {
  white-space: nowrap !important;
}
/* participant logout — neon outline glow */
div[class*="st-key-hub_logout"] .stButton > button,
div[class*="st-key-quiz_logout"] .stButton > button,
div[class*="st-key-results_exit"] .stButton > button {
  border: 2px solid rgba(77,180,255,.8) !important;
  background: rgba(0,59,112,.5) !important;
  color: #e8f4ff !important;
  box-shadow: 0 0 14px rgba(77,180,255,.5), 0 0 28px rgba(0,201,167,.28),
              inset 0 0 12px rgba(77,180,255,.14) !important;
  animation: qtLogoutNeon 2.2s ease-in-out infinite !important;
}
div[class*="st-key-hub_logout"] .stButton > button p,
div[class*="st-key-quiz_logout"] .stButton > button p,
div[class*="st-key-results_exit"] .stButton > button p {
  color: #e8f4ff !important;
}
@keyframes qtLogoutNeon {
  0%, 100% {
    border-color: rgba(77,180,255,.65);
    box-shadow: 0 0 12px rgba(77,180,255,.4), 0 0 22px rgba(0,201,167,.2),
                inset 0 0 10px rgba(77,180,255,.1);
  }
  50% {
    border-color: rgba(0,201,167,.9);
    box-shadow: 0 0 22px rgba(77,180,255,.75), 0 0 42px rgba(0,201,167,.45),
                inset 0 0 18px rgba(77,180,255,.2);
  }
}
.qt-brand { font-family: 'Baloo 2', cursive; font-weight: 800; font-size: 38px; letter-spacing: -.5px;
  background: linear-gradient(92deg, #4db4ff, #9be1ff 45%, #ff5d73);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
.qt-div { width:1px; height:26px; background: var(--stroke); }
.qt-spacer { flex: 1; }

.qt-pill { padding: 6px 14px; border-radius: 999px; background: var(--glass);
  border: 1px solid var(--stroke); font-size: 13px; font-weight: 600; color: var(--dim);
  display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; }
.qt-pill b { color: var(--gold); }
.qt-pill .dot { width:8px; height:8px; border-radius:50%; background: var(--teal); animation: qtPulse 1.6s infinite; }
.qt-pill.red { background: linear-gradient(135deg,#f09433,#dc2743 55%,#bc1888);
  border: 1px solid rgba(220,39,118,.55); color: #fff;
  box-shadow: 0 4px 14px rgba(204,35,102,.35); }

/* ================= cards & text ================= */
.qt-card { background: var(--glass); border: 1px solid var(--stroke); border-radius: 20px;
  padding: 22px 26px; box-shadow: 0 20px 60px rgba(0,0,0,.35); position: relative; z-index: 1; }
.qt-h1 { font-size: 74px; font-weight: 900; line-height: 1.02; color: var(--text); }
.qt-h3 { font-family: 'Baloo 2', cursive; font-size: 22px; font-weight: 700; color: var(--text);
  display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.qt-h3 .count { font-size: 14px; background: var(--abc-red); color: #fff; border-radius: 999px;
  padding: 3px 12px; animation: qtPop .4s both; }

/* bouncing waiting dots */
.qt-dots span { animation: qtBounce 1.2s ease-in-out infinite; display: inline-block;
  font-size: 22px; color: var(--abc-sky); }
.qt-dots span:nth-child(2) { animation-delay: .15s; } .qt-dots span:nth-child(3) { animation-delay: .3s; }

/* me-strip (lobby) */
.qt-mestrip { margin-top: 14px; display: flex; align-items: center; gap: 16px;
  background: linear-gradient(135deg, rgba(0,136,206,.22), rgba(0,59,112,.3));
  border: 1px solid rgba(77,180,255,.35); border-radius: 18px; padding: 14px 20px; }
.qt-mestrip .av { font-size: 32px; animation: qtBounce 2.6s ease-in-out infinite; }
.qt-mestrip .name { font-weight: 700; font-size: 18px; color: var(--text); }
.qt-mestrip .tag { font-size: 12.5px; color: var(--dim); }
.qt-mestrip .ready { margin-left: auto; }

/* question stage card */
.qt-qcard { text-align: center; padding: 34px 40px 30px; margin-bottom: 20px; }

/* live pulsing label (host stage) */
.qt-now { font-size: 12px; letter-spacing: 3px; color: #ff7b8d; font-weight: 700;
  margin-bottom: 12px; text-align: center; animation: qtPulse 1.6s infinite; }

/* quiz library rows */
.qt-quizrow { display: flex; align-items: center; gap: 16px; padding: 15px 16px;
  border-radius: 16px; background: var(--glass); border: 1px solid var(--stroke);
  margin-bottom: 10px; transition: background .2s, transform .2s; }
.qt-quizrow:hover { background: rgba(255,255,255,.1); transform: translateX(5px); }
.qt-quizrow .thumb { width: 52px; height: 52px; border-radius: 14px; font-size: 25px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #0088ce, #005a9e); }
.qt-quizrow .ttl { font-weight: 700; font-size: 15.5px; color: var(--text); }
.qt-quizrow .mt { font-size: 12.5px; color: var(--dim); }
.qt-status { font-size: 11px; font-weight: 700; letter-spacing: 1px; padding: 4px 10px;
  border-radius: 999px; margin-left: auto; white-space: nowrap; }
.qt-status.live { background: rgba(226,24,54,.2); color: #ff7b8d; animation: qtPulse 1.6s infinite; }
.qt-status.ready { background: rgba(0,201,167,.15); color: var(--teal); }
.qt-status.draft { background: rgba(255,255,255,.1); color: var(--dim); }

/* game-flow timeline (host) */
.qt-tl { display: flex; gap: 14px; padding: 10px 0; align-items: flex-start; position: relative; }
.qt-tl .dot2 { width: 14px; height: 14px; border-radius: 50%; margin-top: 4px; flex-shrink: 0;
  background: var(--stroke); position: relative; z-index: 1; }
.qt-tl.done .dot2 { background: var(--teal); }
.qt-tl.now .dot2 { background: var(--abc-red); animation: qtPulse 1.4s infinite; }
.qt-tl:not(:last-child)::before { content: ''; position: absolute; left: 6px; top: 22px;
  bottom: -8px; width: 2px; background: var(--stroke); }
.qt-tl .txt { font-size: 14px; font-weight: 600; color: var(--text); }
.qt-tl .mt { font-size: 12px; color: var(--dim); font-weight: 400; }
.qt-tl.now .txt { color: #ff7b8d; }

/* badges — matching prototype .badge */
.qt-badge {
  display: inline-flex; align-items: center; gap: 10px;
  background: var(--glass); border: 1px solid var(--stroke);
  border-radius: 16px; padding: 12px 18px; font-size: 14px; font-weight: 600;
  animation: qtBounce 3.4s ease-in-out infinite; margin-right: 10px;
}
.qt-badge:nth-child(2) { animation-delay: 0.5s; }
.qt-badge:nth-child(3) { animation-delay: 1s; }
.qt-badge:nth-child(4) { animation-delay: 1.5s; }
.qt-badge .ico { font-size: 22px; }

/* floaters — absolute layer inside stAppViewContainer, behind all UI */
.qt-floaters { position: absolute; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
.qt-floater {
  position: absolute; opacity: 0.14; font-family: 'Baloo 2', cursive;
  font-weight: 800; color: var(--abc-sky);
  animation: qtFloatUp 14s linear infinite;
}
@keyframes qtFloatUp {
  0%   { transform: translateY(105vh) rotate(0deg); opacity: 0; }
  10%  { opacity: 0.16; }
  90%  { opacity: 0.16; }
  100% { transform: translateY(-10vh) rotate(360deg); opacity: 0; }
}

/* mascot on login card */
.qt-mascot {
  position: absolute; top: -46px; right: -20px;
  width: 92px; height: 92px; border-radius: 28px;
  background: linear-gradient(135deg, var(--abc-red), #ff6b81);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Baloo 2', cursive; font-size: 52px; font-weight: 800; color: #fff;
  box-shadow: 0 18px 40px rgba(226, 24, 54, 0.45);
  animation: qtMascotFloat 3s ease-in-out infinite;
  transform: rotate(8deg); z-index: 10;
}
@keyframes qtMascotFloat {
  0%, 100% { transform: rotate(8deg) translateY(0); }
  50% { transform: rotate(-4deg) translateY(-14px); }
}

/* glow ring on login card */
.qt-glow-ring {
  position: absolute; inset: -2px; border-radius: var(--radius); z-index: -1;
  background: linear-gradient(135deg, rgba(77,180,255,0.5), transparent 40%, rgba(226,24,54,0.4));
  filter: blur(14px); opacity: 0.6; animation: qtGlowSpin 6s linear infinite;
}
@keyframes qtGlowSpin { 50% { opacity: 0.25; } }

/* login card: .qt-login-card marker is inside the right column on login page */
body:has(.qt-login-scope) [data-testid="stColumn"]:has(.qt-login-card),
body:has(.qt-login-scope) [data-testid="column"]:has(.qt-login-card) {
  background: var(--glass); border: 1px solid var(--stroke);
  border-radius: var(--radius); backdrop-filter: blur(16px);
  box-shadow: 0 20px 60px rgba(0,0,0,.45); padding: 40px 38px 34px !important;
  position: relative; overflow: visible; z-index: 2;
}
body:has(.qt-login-scope) [data-testid="stHorizontalBlock"]:has(.qt-login-card) {
  overflow: visible;
}
.qt-sub { color: var(--dim); font-size: 15px; }
.qt-arc { display:block; margin: 6px 0 14px; }

/* pin banner */
.qt-pin { font-family: 'Baloo 2', cursive; font-size: 72px; font-weight: 800; letter-spacing: 14px; text-align:center;
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
.qt-chip .tm { font-size: 11px; color: var(--abc-sky); font-weight: 700; }

/* HUD */
.qt-hud { display:flex; align-items:center; gap:14px; flex-wrap:wrap; margin-bottom: 12px; }
.qt-hud .qno { font-family: 'Baloo 2', cursive; font-weight: 800; font-size: 20px; color: var(--abc-sky); }
.qt-hud .bar { flex:1; min-width: 120px; height: 10px; background: rgba(0,0,0,.35); border-radius: 99px; overflow:hidden; }
.qt-hud .bar i { display:block; height:100%; border-radius:99px;
  background: linear-gradient(90deg, var(--abc-blue), var(--abc-sky)); box-shadow: 0 0 12px rgba(77,180,255,.6); }
.qt-streak { display:inline-flex; align-items:center; gap:6px; font-weight:800; font-size:15px; color: var(--text);
  background: linear-gradient(135deg, rgba(255,100,40,.25), rgba(255,60,60,.15));
  border: 1px solid rgba(255,140,60,.4); padding: 6px 14px; border-radius: 999px; }
.qt-streak .fl { animation: qtBounce 1s ease-in-out infinite; display:inline-block; }
.qt-score { font-family: 'Baloo 2', cursive; font-weight: 800; font-size: 19px; color: var(--text); background: var(--glass);
  border: 1px solid var(--stroke); padding: 6px 16px; border-radius: 999px; }
.qt-score b { color: var(--gold); }

/* timer */
.qt-timerwrap { display:flex; justify-content:center; margin: 4px 0 10px; }
.qt-timer { position: relative; width: 96px; height: 96px; margin: 0 auto; }
.qt-timer svg { display: block; width: 100%; height: 100%; transform: rotate(-90deg); }
.qt-timer .num { position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-family: 'Baloo 2', cursive; font-size: 34px; font-weight: 800; color: var(--text);
  line-height: 1; pointer-events: none; }
.qt-timer.danger .num { color: var(--abc-red); }
/* Smooth ring sweep — fills the gap between 0.5s server rerenders */
.qt-timer-stroke { transition: stroke-dashoffset 0.52s linear; }

/* question text */
.qt-question { text-align:center; font-size: 26px; font-weight: 700; line-height: 1.4;
  color: var(--text); margin: 6px auto 18px; max-width: 820px; }
.qt-cat { text-align:center; font-size: 12px; letter-spacing: 2.5px; color: var(--abc-sky);
  font-weight: 700; margin-bottom: 6px; text-transform: uppercase; }

/* question media — image / audio / video rounds */
.qt-qmedia-badge { text-align:center; font-size:11px; letter-spacing:2px; font-weight:700;
  color:var(--gold); margin:-4px 0 12px; text-transform:uppercase; }
.qt-qmedia { margin: 0 auto 16px; max-width: 720px; border-radius: 16px; overflow: hidden;
  background: rgba(0,0,0,.25); border: 1px solid rgba(255,255,255,.08); }
.qt-qmedia img { display:block; width:100%; border-radius:16px; }
.qt-qmedia-label { text-align:center; font-size:13px; color:var(--abc-sky); font-weight:600;
  padding:12px 16px 4px; }
body:has(.qt-quiz-scope) .qt-qmedia { max-width: none; margin-bottom: 20px; }
  body:has(.qt-quiz-scope) .qt-qmedia video { width:100%; max-height:min(52vh,420px); border-radius:12px; }

/* participant performance review */
.qt-perf-summary { display:flex; align-items:center; gap:14px; padding:16px 18px; margin-bottom:14px;
  background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.08); border-radius:16px; }
.qt-perf-summary .av { font-size:36px; line-height:1; }
.qt-perf-summary .name { display:block; font-weight:700; font-size:17px; color:#eef5ff; }
.qt-perf-summary .meta { display:block; font-size:13px; color:#7a94b0; margin-top:4px; }
.qt-perf-tip { font-size:13.5px; color:#b8cce0; padding:8px 14px; margin:6px 0;
  background:rgba(0,136,206,.1); border-left:3px solid var(--abc-blue); border-radius:0 10px 10px 0; }
.qt-perf-q { padding:14px 16px; margin:10px 0; border-radius:14px;
  background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.07); }
.qt-perf-q.good { border-left:3px solid var(--teal); }
.qt-perf-q.bad { border-left:3px solid var(--abc-red); }
.qt-perf-q.subj { border-left:3px solid var(--gold); }
.qt-perf-q .qtop { font-size:14.5px; color:#eef5ff; margin-bottom:8px; line-height:1.45; }
.qt-perf-q .qans { font-size:13px; color:#b8cce0; margin:4px 0; }
.qt-perf-q .qans .lbl { font-size:10px; letter-spacing:1.2px; text-transform:uppercase;
  color:#7a94b0; margin-right:6px; }
.qt-perf-q .qres { font-size:13px; margin-top:8px; font-weight:600; }

/* participant quiz — larger question stage, stats stay on the left rail */
body:has(.qt-quiz-scope) .qt-qcard { padding: 40px 52px 36px; margin-bottom: 24px; }
body:has(.qt-quiz-scope) .qt-question { font-size: 32px; line-height: 1.45; max-width: none;
  margin: 8px auto 22px; }
body:has(.qt-quiz-scope) .qt-cat { font-size: 13px; margin-bottom: 10px; }
body:has(.qt-quiz-scope) .qt-timerwrap { margin: 8px 0 16px; }
body:has(.qt-quiz-scope) .qt-timer { width: 96px; height: 96px; }
body:has(.qt-quiz-scope) .qt-timer .num { font-size: 34px; }
body:has(.qt-quiz-scope) div[class*="st-key-ans"] .stButton > button {
  min-height: 98px !important; font-size: 21px !important; padding-left: 28px !important;
  border-radius: 22px !important;
}
body:has(.qt-quiz-scope) div[class*="st-key-ans"] .stButton > button p {
  font-size: 21px !important; line-height: 1.35 !important;
}

/* participant quiz — left stats rail: fixed-width panel, content-height, flush-left box only */
body:has(.qt-quiz-scope) [data-testid="stHorizontalBlock"]:has(.qt-quiz-stats-col) {
  align-items: flex-start !important;
  overflow: visible !important;
}
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-stats-col),
body:has(.qt-quiz-scope) [data-testid="column"]:has(.qt-quiz-stats-col) {
  flex: 0 0 clamp(260px, 28vw, 360px) !important;
  max-width: clamp(260px, 28vw, 360px) !important;
  min-width: 260px !important;
  align-self: flex-start !important;
  overflow: visible !important;
}
body:has(.qt-quiz-scope) .qt-stats-rail {
  box-sizing: border-box;
  height: auto !important;
  min-height: 0 !important;
  flex: none !important;
  padding: 18px 16px 16px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  overflow: hidden;
  margin: 0;
  position: relative;
  left: calc(-1 * clamp(1.25rem, 4vw, 3rem));
  /* extend left flush; pinch right edge inward so the panel reads further left */
  width: calc(100% + clamp(1.25rem, 4vw, 3rem) - clamp(16.1rem, 41vw, 24.9rem)) !important;
  max-width: calc(100% + clamp(1.25rem, 4vw, 3rem) - clamp(16.1rem, 41vw, 24.9rem)) !important;
  border-radius: 16px;
}
body:has(.qt-quiz-scope) .qt-stats-rail-fill {
  flex: 1 1 auto;
  min-height: 0;
  pointer-events: none;
}
/* participant quiz — stage column: sit right of stats rail with breathing room */
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-stage-col),
body:has(.qt-quiz-scope) [data-testid="column"]:has(.qt-quiz-stage-col) {
  margin-left: calc(-1 * clamp(4.5rem, 12vw, 8rem)) !important;
  padding-left: clamp(1.25rem, 3.5vw, 2.75rem) !important;
  padding-right: clamp(0.5rem, 1.5vw, 1rem) !important;
  flex: 1 1 auto !important;
  max-width: none !important;
  min-width: 0 !important;
}
/* participant quiz — questions, timer, answer grid nudged right */
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-stage-col) .qt-qcard,
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-stage-col) .qt-timerwrap,
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-stage-col) .qt-verdict,
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-stage-col) .qt-vote,
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-stage-col) div[class*="st-key-ans"],
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-stage-col) div[class*="st-key-vote"],
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-stage-col) [data-testid="stForm"] {
  margin-left: clamp(0.75rem, 2.5vw, 2rem) !important;
  margin-right: clamp(0.25rem, 1vw, 0.75rem) !important;
}
/* participant quiz — team chat rail: fixed right panel, flush to screen edge */
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-chat-col),
body:has(.qt-quiz-scope) [data-testid="column"]:has(.qt-quiz-chat-col) {
  flex: 0 0 clamp(250px, 24vw, 340px) !important;
  max-width: clamp(250px, 24vw, 340px) !important;
  min-width: 240px !important;
  margin-left: auto !important;
  align-self: flex-start !important;
  overflow: visible !important;
  position: relative;
  right: calc(-1 * clamp(0.75rem, 2.5vw, 2rem));
  width: calc(100% + clamp(0.75rem, 2.5vw, 2rem)) !important;
  max-width: calc(clamp(250px, 24vw, 340px) + clamp(0.75rem, 2.5vw, 2rem)) !important;
}
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-chat-col) [data-testid="stVerticalBlock"],
body:has(.qt-quiz-scope) [data-testid="column"]:has(.qt-quiz-chat-col) [data-testid="stVerticalBlock"] {
  align-items: stretch !important;
  width: 100% !important;
}
body:has(.qt-quiz-scope) .qt-chat-head {
  text-align: left !important;
  letter-spacing: 2px;
  margin-bottom: 10px;
}
body:has(.qt-quiz-scope) .qt-chat-solo {
  text-align: left !important;
  font-size: 12.5px !important;
  line-height: 1.5;
  padding: 14px 16px !important;
  max-width: 100%;
}
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-chat-col) .qt-chatbox {
  width: 100%;
}
body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-chat-col) [data-testid="stForm"] {
  margin-top: 8px;
  width: 100%;
}
@media (min-width: 1180px) {
  body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-chat-col),
  body:has(.qt-quiz-scope) [data-testid="column"]:has(.qt-quiz-chat-col) {
    right: calc(-1 * (max(0px, (100vw - 1150px) / 2) + 0.85rem));
    max-width: calc(clamp(250px, 24vw, 340px) + max(0px, (100vw - 1150px) / 2) + 0.85rem) !important;
  }
}
@media (min-width: 1180px) {
  body:has(.qt-quiz-scope) .qt-stats-rail {
    left: calc(-1 * (max(0px, (100vw - 1150px) / 2) + 1.6rem));
    width: calc(100% + max(0px, (100vw - 1150px) / 2) + 1.6rem - clamp(16.1rem, 41vw, 24.9rem)) !important;
    max-width: calc(100% + max(0px, (100vw - 1150px) / 2) + 1.6rem - clamp(16.1rem, 41vw, 24.9rem)) !important;
  }
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-cat {
  text-align: left !important;
  margin-bottom: 12px;
  letter-spacing: 2px;
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl {
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  padding: 12px 0 14px;
  font-size: 13.5px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl .nm,
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl .em {
  width: 100%;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl .bar {
  width: 100%;
  max-width: 100%;
  flex: none;
  height: 9px;
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl .pt {
  align-self: flex-end;
  font-size: 15px;
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl:has(.bar) {
  flex-direction: row;
  flex-wrap: wrap;
  align-items: center;
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl:has(.bar) .nm {
  flex: 1 1 100%;
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl:has(.bar) .bar {
  flex: 1 1 auto;
  min-width: 0;
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl:has(.bar) .pt {
  flex: 0 0 auto;
  margin-left: 8px;
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl:not(:has(.bar)) {
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
  gap: 10px;
  padding: 11px 0;
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl:not(:has(.bar)) .em {
  width: auto;
  flex-shrink: 0;
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl:not(:has(.bar)) .nm {
  flex: 1 1 auto;
  min-width: 0;
}
body:has(.qt-quiz-scope) .qt-stats-rail .qt-rl:not(:has(.bar)) .pt {
  align-self: auto;
  flex-shrink: 0;
}

/* verdict */
.qt-verdict { text-align:center; padding: 26px 10px 8px; animation: qtPop .5s cubic-bezier(.34,1.56,.64,1) both; }
.qt-verdict .big { font-family: 'Baloo 2', cursive; font-size: 60px; font-weight: 800; }
.qt-verdict .big.good { color: #4ade80; text-shadow: 0 0 40px rgba(74,222,128,.55); }
.qt-verdict .big.bad { color: #fca5a5; text-shadow: 0 0 40px rgba(252,165,165,.5); }
.qt-verdict .sub { color: var(--dim); font-size: 16px; margin-top: 6px; }
.qt-verdict .sub b { color: var(--gold); }
.qt-verdict-answer {
  display: inline-flex; flex-direction: column; align-items: center; gap: 10px;
  margin-top: 20px; padding: 14px 22px 16px; border-radius: 18px; max-width: 92%;
  background: linear-gradient(135deg, rgba(0,201,167,.16), rgba(74,222,128,.1));
  border: 2px solid rgba(0,201,167,.55);
  box-shadow: 0 0 28px rgba(0,201,167,.32), inset 0 1px 0 rgba(255,255,255,.14);
  animation: qtPop .55s cubic-bezier(.34,1.56,.64,1) .15s both;
}
.qt-verdict-ans-tag {
  font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
  color: #5eead4;
}
.qt-verdict-ans-row { display: flex; align-items: center; gap: 14px; }
.qt-verdict-ans-letter {
  width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center;
  justify-content: center; font-family: 'Baloo 2', cursive; font-size: 20px; font-weight: 800;
  color: #fff; flex-shrink: 0; box-shadow: 0 4px 14px rgba(0,0,0,.35);
}
.qt-verdict-ans-text {
  font-family: 'Baloo 2', cursive; font-size: 22px; font-weight: 700; color: #fff;
  text-align: left; line-height: 1.25;
  text-shadow: 0 0 18px rgba(255,255,255,.25);
}

/* podium */
.qt-podium { display:flex; align-items:flex-end; justify-content:center; gap:18px; margin: 18px 0 8px; }
.qt-step { text-align:center; width: 150px; }
.qt-step .av { font-size: 40px; animation: qtBounce 2.6s ease-in-out infinite; }
.qt-step .who { font-weight: 700; font-size: 16px; color: var(--text); }
.qt-step .pts { font-family: 'Baloo 2', cursive; font-weight: 800; color: var(--gold); font-size: 18px; margin-bottom: 8px; }
.qt-step .blk { border-radius: 18px 18px 0 0; display:flex; align-items:flex-start; justify-content:center;
  padding-top: 10px; font-family: 'Baloo 2', cursive; font-size: 40px; font-weight: 800; color: rgba(255,255,255,.85);
  animation: qtGrow .9s cubic-bezier(.22,1,.36,1) both; transform-origin: bottom; }
.qt-step.p1 .blk { height: 150px; background: linear-gradient(180deg,#ffd76e,#b8860b); box-shadow: 0 0 40px rgba(255,194,51,.3); animation-delay:.7s; }
.qt-step.p2 .blk { height: 110px; background: linear-gradient(180deg,#b9d4f0,#5f7d9c); animation-delay:.4s; }
.qt-step.p3 .blk { height: 82px;  background: linear-gradient(180deg,#e8a06b,#9c5a2e); animation-delay:.15s; }
.qt-step .crown { font-size: 28px; display:block; animation: qtBounce 1.6s ease-in-out infinite; }

/* rank rows */
.qt-row { display:flex; align-items:center; gap:14px; padding: 10px 18px; margin-bottom: 8px;
  background: var(--glass); border: 1px solid var(--stroke); border-radius: 16px;
  animation: qtRise .5s both; color: var(--text); }
.qt-row .rk { font-family: 'Baloo 2', cursive; font-size: 20px; font-weight: 800; width: 40px; color: var(--dim); }
.qt-row .em { font-size: 22px; }
.qt-row .nm { font-weight: 700; flex: 1; }
.qt-row .nm .tm { font-size: 11px; color: var(--abc-sky); font-weight: 700; margin-left: 8px; }
.qt-row .pt { font-family: 'Baloo 2', cursive; font-size: 19px; font-weight: 800; color: var(--gold); }
.qt-row.me { border-color: rgba(77,180,255,.55); background: linear-gradient(135deg, rgba(0,136,206,.22), rgba(0,59,112,.28)); }
.qt-row.me .nm::after { content: " — YOU"; color: var(--abc-sky); font-size: 11px; letter-spacing: 1px; }
.qt-team-results { display: flex; flex-direction: column; gap: 0; }

/* voting cards */
.qt-vote { background: var(--glass); border: 1px solid var(--stroke); border-radius: 16px;
  padding: 16px 18px; margin-bottom: 6px; color: var(--text); animation: qtRise .5s both; }
.qt-vote .who { font-weight: 700; font-size: 14px; color: var(--abc-sky); margin-bottom: 6px; }
.qt-vote .txt { font-size: 15.5px; line-height: 1.55; }
.qt-vote .cnt { float: right; font-weight: 900; color: var(--gold); }

/* distribution bars — kept for host view compat */
.qt-bars { display:flex; align-items:flex-end; justify-content:center; gap: 22px; height: 170px; margin: 14px 0 4px; }
.qt-barcol { display:flex; flex-direction:column; align-items:center; width: 84px; height: 100%; justify-content:flex-end; gap: 6px; }
.qt-bar { width: 100%; border-radius: 12px 12px 6px 6px; display:flex; align-items:flex-start;
  justify-content:center; padding-top: 6px; font-family: 'Baloo 2', cursive; font-weight: 800; font-size: 18px; color: #fff;
  animation: qtGrow .8s cubic-bezier(.22,1,.36,1) both; transform-origin: bottom; }
.qt-barcol .lb { font-size: 12px; color: var(--dim); font-weight: 600; text-align: center; }
.qt-barcol.win .lb { color: var(--teal); font-weight: 800; }

/* KBC audience-poll bars (participant reveal) */
.qt-kbc-poll { display:flex; flex-direction:column; gap:10px; margin:18px 0 8px; }
.qt-kbc-row { display:flex; align-items:center; gap:10px; animation: qtPop .5s cubic-bezier(.34,1.56,.64,1) both; }
.qt-kbc-row:nth-child(1) { animation-delay:.05s; }
.qt-kbc-row:nth-child(2) { animation-delay:.12s; }
.qt-kbc-row:nth-child(3) { animation-delay:.19s; }
.qt-kbc-row:nth-child(4) { animation-delay:.26s; }
.qt-kbc-label { width:36px; height:36px; border-radius:50%; display:flex; align-items:center;
  justify-content:center; font-family:'Baloo 2',cursive; font-weight:900; font-size:16px;
  color:#fff; flex-shrink:0; box-shadow:0 4px 12px rgba(0,0,0,.35); }
.qt-kbc-track { flex:1; background:rgba(255,255,255,.06); border-radius:999px;
  height:38px; position:relative; overflow:hidden;
  border:1px solid rgba(255,255,255,.1); }
.qt-kbc-fill { height:100%; border-radius:999px; transition:width 0.9s cubic-bezier(.22,1,.36,1);
  animation: qtKbcGrow .9s cubic-bezier(.22,1,.36,1) both; }
.qt-kbc-opt { position:absolute; left:14px; top:50%; transform:translateY(-50%);
  font-size:13px; font-weight:600; color:#eef5ff; white-space:nowrap;
  overflow:hidden; text-overflow:ellipsis; max-width:calc(100% - 20px); pointer-events:none; }
.qt-kbc-row.win .qt-kbc-track { border-color:rgba(255,255,255,.35); }
.qt-kbc-row.win .qt-kbc-opt { font-weight:800; }
.qt-kbc-pct { min-width:54px; text-align:right; font-family:'Baloo 2',cursive;
  font-weight:800; font-size:18px; color:#eef5ff; line-height:1.1; }
.qt-kbc-cnt { font-family:Poppins,sans-serif; font-size:10.5px; color:rgba(255,255,255,.45); font-weight:500; }
@keyframes qtKbcGrow { from { width:0 !important; } }

/* confetti */
.qt-cf { position: fixed; top: -20px; border-radius: 3px; z-index: 9; pointer-events: none; animation: qtFall linear forwards; }

/* awards */
.qt-award { display:inline-flex; align-items:center; gap:8px; padding: 10px 18px; margin: 4px 6px 4px 0;
  border-radius: 14px; font-size: 14px; font-weight: 600; color: var(--text);
  background: var(--glass); border: 1px solid var(--stroke); animation: qtPop .5s both; }
.qt-award b { color: var(--abc-sky); }

/* results page — champion hero spotlight */
body:has(.qt-results-scope) .qt-champ-hero {
  text-align: center; margin: 0 auto 28px; max-width: 620px;
}
body:has(.qt-results-scope) .qt-champ-trophy {
  font-size: 110px; line-height: 1; margin-bottom: 4px;
  animation: qtBounce 2.6s ease-in-out infinite;
  filter: drop-shadow(0 20px 50px rgba(255,194,51,.45));
}
body:has(.qt-results-scope) .qt-champ-headline {
  font-family: 'Baloo 2', cursive; font-size: 56px; font-weight: 800; line-height: 1.1;
  background: linear-gradient(92deg, #ffd76e, #ff9d2e, #ff5d73);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: 20px;
}
body:has(.qt-results-scope) .qt-champ-spotlight {
  position: relative; display: inline-flex; align-items: center; gap: 16px;
  padding: 20px 32px 20px 24px; border-radius: 26px; overflow: hidden;
  background: linear-gradient(135deg, rgba(255,194,51,.16) 0%, rgba(77,180,255,.07) 48%, rgba(0,201,167,.12) 100%);
  border: 1px solid rgba(255,194,51,.5);
  box-shadow: 0 0 36px rgba(255,194,51,.25), 0 10px 40px rgba(0,0,0,.38),
              inset 0 1px 0 rgba(255,255,255,.14);
  animation: qtChampPulse 3.2s ease-in-out infinite;
}
@keyframes qtChampPulse {
  0%, 100% {
    box-shadow: 0 0 36px rgba(255,194,51,.25), 0 10px 40px rgba(0,0,0,.38),
                inset 0 1px 0 rgba(255,255,255,.14);
    border-color: rgba(255,194,51,.5);
  }
  50% {
    box-shadow: 0 0 56px rgba(255,194,51,.42), 0 12px 48px rgba(0,0,0,.42),
                inset 0 1px 0 rgba(255,255,255,.2);
    border-color: rgba(255,210,80,.75);
  }
}
body:has(.qt-results-scope) .qt-champ-glow {
  position: absolute; inset: -40% -10%; z-index: 0; pointer-events: none;
  background: radial-gradient(ellipse at 30% 50%, rgba(255,194,51,.28) 0%, transparent 62%);
}
body:has(.qt-results-scope) .qt-champ-avatar {
  position: relative; z-index: 1; font-size: 58px; line-height: 1;
  filter: drop-shadow(0 6px 18px rgba(255,194,51,.45));
  animation: qtChampAvatar 2.8s ease-in-out infinite;
}
@keyframes qtChampAvatar {
  0%, 100% { transform: scale(1) rotate(0deg); }
  50% { transform: scale(1.06) rotate(-4deg); }
}
body:has(.qt-results-scope) .qt-champ-identity {
  position: relative; z-index: 1; display: flex; flex-direction: column;
  align-items: flex-start; gap: 2px; text-align: left;
}
body:has(.qt-results-scope) .qt-champ-name {
  font-family: 'Baloo 2', cursive; font-size: 38px; font-weight: 800; line-height: 1.05;
  color: #fff; letter-spacing: .3px;
  text-shadow: 0 0 24px rgba(255,194,51,.55), 0 2px 8px rgba(0,0,0,.35);
}
body:has(.qt-results-scope) .qt-champ-tagline {
  font-size: 13px; font-weight: 700; letter-spacing: 2.8px; text-transform: uppercase;
  color: var(--gold);
  text-shadow: 0 0 14px rgba(255,194,51,.45);
}
body:has(.qt-results-scope) .qt-champ-crown {
  position: relative; z-index: 1; font-size: 36px; line-height: 1;
  filter: drop-shadow(0 4px 12px rgba(255,194,51,.5));
  animation: qtChampCrown 2.4s ease-in-out infinite;
}
@keyframes qtChampCrown {
  0%, 100% { transform: translateY(0) rotate(-8deg); }
  50% { transform: translateY(-6px) rotate(6deg); }
}

/* results page — big section headings, neon dividers, awards in one row */
body:has(.qt-results-scope) .qt-section-h {
  text-align: center; font-family: 'Baloo 2', cursive; font-size: 36px; font-weight: 800;
  letter-spacing: 3px; text-transform: uppercase; margin: 20px 0 16px; color: var(--abc-sky);
  text-shadow: 0 0 20px rgba(77,180,255,.55), 0 0 40px rgba(77,180,255,.22);
}
body:has(.qt-results-scope) .qt-neon-rule {
  height: 2px; margin: 26px auto 20px; max-width: 94%; border-radius: 2px;
  background: linear-gradient(90deg, transparent 0%, var(--abc-sky) 18%, var(--teal) 42%,
              var(--gold) 58%, var(--abc-red) 82%, transparent 100%);
  box-shadow: 0 0 14px rgba(77,180,255,.65), 0 0 32px rgba(0,201,167,.35),
              0 0 48px rgba(255,194,51,.18);
  animation: qtNeonPulse 2.4s ease-in-out infinite;
}
@keyframes qtNeonPulse {
  0%, 100% { opacity: .72; filter: brightness(1); }
  50% { opacity: 1; filter: brightness(1.3); }
}
body:has(.qt-results-scope) .qt-awards-scroll {
  overflow-x: auto; margin-bottom: 8px; padding-bottom: 8px;
  -webkit-overflow-scrolling: touch; scrollbar-width: thin;
  scroll-padding-inline: 16px;
}
body:has(.qt-results-scope) [data-testid="stMarkdownContainer"]:has(.qt-awards-scroll) {
  overflow: visible;
}
body:has(.qt-results-scope) .qt-awards-row {
  display: inline-flex; flex-wrap: nowrap; justify-content: center; align-items: stretch;
  gap: 10px; min-width: 100%; padding: 6px 16px 10px; box-sizing: border-box;
}
body:has(.qt-results-scope) .qt-awards-row .qt-award {
  flex: 0 0 auto; white-space: nowrap; margin: 0; padding: 12px 16px; font-size: 13.5px;
  border-color: rgba(77,180,255,.35);
  box-shadow: 0 0 12px rgba(77,180,255,.12);
}

/* kpi cards */
.qt-kpi { background: var(--glass); border: 1px solid var(--stroke); border-radius: 18px;
  padding: 18px 20px; text-align:center; animation: qtRise .6s both; }
.qt-kpi { overflow: hidden; }
.qt-kpi .n { font-family: 'Baloo 2', cursive; font-size: 34px; font-weight: 800; color: var(--abc-sky); }
.qt-kpi .spark { position: absolute; bottom: -6px; right: -6px; font-size: 54px; opacity: .12; }
.qt-kpi.gold .n { color: var(--gold); } .qt-kpi.teal .n { color: var(--teal); }
.qt-kpi.pink .n { color: #ff7b8d; }
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
div[class*="st-key-ans1"] .stButton > button { background: linear-gradient(135deg,#c4b5fd,#a78bfa 55%,#8b5cf6) !important; box-shadow: 0 8px 22px rgba(139,92,246,.4) !important; }
div[class*="st-key-ans2"] .stButton > button { background: linear-gradient(135deg,#00c9a7,#00806a) !important; box-shadow: 0 8px 22px rgba(0,201,167,.3) !important; }
div[class*="st-key-ans3"] .stButton > button { background: linear-gradient(135deg,#ff9d2e,#d97706) !important; box-shadow: 0 8px 22px rgba(255,157,46,.3) !important; }
div[class*="st-key-ans"] .stButton > button {
  min-height: 84px !important; font-size: 19px !important; font-weight: 700 !important;
  border-radius: 20px !important; white-space: normal !important; text-align: left !important;
  color: #fff !important; justify-content: flex-start !important; padding-left: 26px !important;
}
div[class*="st-key-ans"] .stButton > button p {
  font-size: 19px !important; font-weight: 700 !important; text-align: left !important; }

/* red / gold / vote variants */
div[class*="st-key-red"] .stButton > button { background: linear-gradient(135deg,#ff415e,#e21836) !important; color: #fff !important; box-shadow: 0 8px 22px rgba(226,24,54,.4) !important; border: none !important; }
div[class*="st-key-gold"] .stButton > button { background: linear-gradient(135deg,#ffd76e,#ff9d2e) !important; color: #3a2400 !important; box-shadow: 0 8px 22px rgba(255,194,51,.35) !important; border: none !important; }
div[class*="st-key-vote"] .stButton > button { background: linear-gradient(135deg,#7c5cff,#4b32b4) !important; color: #fff !important; box-shadow: 0 8px 22px rgba(124,92,255,.35) !important; border: none !important; }
div[class*="st-key-avat"] .stButton > button {
  background: rgba(0,0,0,.28) !important; border: 2px solid var(--stroke) !important;
  font-size: 26px !important; min-height: 60px !important; border-radius: 16px !important;
  box-shadow: none !important; padding: 6px !important;
}
div[class*="st-key-avat"] .stButton > button:hover { border-color: var(--abc-sky) !important; transform: scale(1.12) rotate(-5deg); }

/* login page — large avatar picker grid */
body:has(.qt-login-scope) div[class*="st-key-login_avat"] {
  overflow: visible !important;
}
body:has(.qt-login-scope) div[class*="st-key-login_avat"] .stButton {
  width: 100% !important;
}
body:has(.qt-login-scope) div[class*="st-key-login_avat"] .stButton > button {
  background: rgba(0,0,0,.32) !important;
  border: 2px solid var(--stroke) !important;
  font-size: 40px !important;
  line-height: 1 !important;
  min-height: 80px !important;
  width: 100% !important;
  border-radius: 18px !important;
  box-shadow: none !important;
  padding: 8px !important;
  overflow: visible !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
}
body:has(.qt-login-scope) div[class*="st-key-login_avat"] .stButton > button p {
  font-size: 40px !important;
  line-height: 1 !important;
  margin: 0 !important;
  padding: 0 !important;
  width: 100% !important;
  text-align: center !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
body:has(.qt-login-scope) div[class*="st-key-login_avat"] .stButton > button[kind="primary"] {
  border-color: var(--abc-sky) !important;
  background: rgba(0,136,206,.28) !important;
  box-shadow: 0 0 20px rgba(77,180,255,.45) !important;
  color: inherit !important;
}
body:has(.qt-login-scope) div[class*="st-key-login_avat"] .stButton > button:hover {
  border-color: var(--abc-sky) !important;
  background: rgba(0,136,206,.22) !important;
  transform: scale(1.06);
  box-shadow: 0 0 22px rgba(77,180,255,.35) !important;
}

/* inputs */
.stTextInput input, .stTextArea textarea, .stNumberInput input,
div[data-baseweb="select"] > div {
  background: rgba(0,0,0,.28) !important; border: 1.5px solid var(--stroke) !important;
  border-radius: 13px !important; color: var(--text) !important; font-size: 15px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--abc-sky) !important; box-shadow: 0 0 0 4px rgba(77,180,255,.15) !important; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label,
.stMultiSelect label, .stSlider label, .stCheckbox label, .stRadio label {
  color: var(--dim) !important; font-weight: 600 !important; }

/* settle button — rendered once after each page switch, clicked by JS only */
div[class*="st-key-qt_settle"] { display: none !important; }

/* big PIN entry */
div[class*="st-key-pinbox"] input {
  text-align: center; font-size: 28px !important; letter-spacing: 10px; font-weight: 800; }

/* tabs */
.stTabs [data-baseweb="tab-list"] { background: rgba(0,0,0,.3); border-radius: 999px; padding: 5px; gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 999px; font-weight: 700; color: var(--dim); padding: 8px 20px; }
body:has(.qt-login-scope) .stTabs [data-baseweb="tab"] {
  display: inline-flex; align-items: center; gap: 8px;
}
.qt-tab-ico { display: inline-flex; align-items: center; flex-shrink: 0; line-height: 0; }
.qt-tab-ico svg { stroke: currentColor; }
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg,#0088ce,#003b70) !important; color: #fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* dataframe + metric */
[data-testid="stMetric"] { background: var(--glass); border: 1px solid var(--stroke);
  border-radius: 16px; padding: 14px 18px; }
[data-testid="stMetricValue"] { color: var(--abc-sky); font-weight: 800; }
[data-testid="stMetricLabel"] { color: var(--dim); }

.stAlert { border-radius: 14px; }
[data-testid="stExpander"] details {
  background: rgba(0,0,0,.2) !important; border: 1px solid var(--stroke) !important;
  border-radius: 14px !important; }
[data-testid="stExpander"] summary { color: var(--dim) !important; font-weight: 600; font-size: 13px; }
.stProgress > div > div { background: linear-gradient(90deg, var(--abc-blue), var(--abc-sky)) !important; }

#qt-creator-credit { font-size: 25px !important; letter-spacing: 0.5px; }
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

/* ================= side rails: live stats + team chat ================= */
.qt-rail { background: var(--glass); border: 1px solid var(--stroke); border-radius: 16px;
  padding: 12px 14px 8px; }
.qt-rl { display: flex; align-items: center; gap: 8px; padding: 6px 2px; font-size: 12.5px;
  color: var(--text); border-bottom: 1px dashed rgba(255,255,255,.07); }
.qt-rl:last-child { border-bottom: none; }
.qt-rl .em { font-size: 14px; white-space: nowrap; }
.qt-rl .nm { flex: 1; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.qt-rl .bar { flex: 1.2; height: 7px; background: rgba(0,0,0,.35); border-radius: 99px; overflow: hidden; }
.qt-rl .bar i { display: block; height: 100%; border-radius: 99px;
  background: linear-gradient(90deg, var(--abc-blue), var(--abc-sky)); }
.qt-rl .pt { font-family: 'Baloo 2', cursive; font-weight: 800; font-size: 13px; color: var(--gold); }

.qt-chatbox { display: flex; flex-direction: column-reverse; gap: 8px; height: 320px; overflow-y: auto;
  background: rgba(0,0,0,.25); border: 1px solid var(--stroke); border-radius: 16px; padding: 12px; }
.qt-msg { max-width: 92%; background: rgba(255,255,255,.08); border: 1px solid var(--stroke);
  border-radius: 14px 14px 14px 4px; padding: 7px 11px; font-size: 13px; color: var(--text);
  align-self: flex-start; animation: qtPop .25s both; }
.qt-msg.me { align-self: flex-end; border-radius: 14px 14px 4px 14px;
  background: linear-gradient(135deg, rgba(0,136,206,.35), rgba(0,59,112,.4));
  border-color: rgba(77,180,255,.35); }
.qt-msg .who { display: block; font-size: 10.5px; color: var(--abc-sky); font-weight: 700; margin-bottom: 2px; }
.qt-msg .txt { line-height: 1.45; word-break: break-word; }

/* ================= Domain Academy / learn panel ================= */
body:has(.qt-learn-scope) .qt-learn-rail { margin-top: 8px; }
.qt-learn-rail { padding: 18px 20px 16px; }
.qt-learn-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
.qt-learn-stats { display: flex; gap: 14px; }
.qt-learn-stat { font-size: 11px; color: var(--dim); text-align: right; }
.qt-learn-stat b { display: block; font-size: 18px; color: var(--gold); font-family: 'Baloo 2', cursive; }
.qt-learn-rings { display: flex; flex-wrap: wrap; gap: 12px; margin: 12px 0; }
.qt-learn-ring-item { display: flex; align-items: center; gap: 8px; font-size: 10px; color: var(--dim); }
.qt-learn-ring { width: 42px; height: 42px; transform: rotate(-90deg); }
.qt-learn-ring-bg { fill: none; stroke: rgba(255,255,255,.08); stroke-width: 3; }
.qt-learn-ring-fill { fill: none; stroke: var(--abc-sky); stroke-width: 3; stroke-linecap: round;
  transition: stroke-dasharray 0.8s cubic-bezier(.4,0,.2,1); filter: drop-shadow(0 0 4px rgba(77,180,255,.5)); }
.qt-learn-ring-lbl b { color: var(--abc-sky); }
.qt-learn-daily { margin: 14px 0; padding: 12px; background: rgba(0,136,206,.08); border-radius: 14px;
  border: 1px solid rgba(77,180,255,.2); }
.qt-learn-challenge { font-size: 12px; color: var(--dim); margin: 10px 0; }
.qt-learn-ach { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0; }
.qt-learn-tree { max-height: 320px; overflow-y: auto; padding-right: 4px; }
.qt-tree-branch { margin-bottom: 4px; }
.qt-tree-summary { cursor: pointer; font-size: 13px; font-weight: 600; color: var(--text);
  list-style: none; padding: 6px 0; display: flex; align-items: center; gap: 8px; }
.qt-tree-summary::-webkit-details-marker { display: none; }
.qt-tree-chevron { display: inline-block; transition: transform 0.25s ease; color: var(--abc-sky); font-size: 10px; }
details[open] > .qt-tree-summary .qt-tree-chevron { transform: rotate(90deg); }
.qt-tree-count { margin-left: auto; font-size: 10px; color: var(--dim); font-weight: 500; }
.qt-tree-row.term { display: flex; align-items: center; gap: 8px; padding: 5px 0 5px 8px;
  font-size: 12.5px; border-bottom: 1px dashed rgba(255,255,255,.05); }
.qt-tree-label { flex: 1; font-weight: 600; color: var(--abc-sky); }
.qt-learn-badge { font-size: 9px; padding: 2px 8px; border-radius: 99px; font-weight: 700; letter-spacing: 0.5px; }
.qt-learn-badge.mastered { background: rgba(0,201,167,.15); color: var(--teal); border: 1px solid rgba(0,201,167,.35); }
.qt-learn-badge.viewed { background: rgba(77,180,255,.12); color: var(--abc-sky); border: 1px solid rgba(77,180,255,.25); }
.qt-learn-badge.review { background: rgba(226,24,54,.12); color: var(--abc-red); border: 1px solid rgba(226,24,54,.3); }
.qt-learn-badge.new { background: rgba(255,255,255,.06); color: var(--dim); border: 1px solid var(--stroke); }
.qt-learn-term { padding: 12px; background: rgba(0,0,0,.2); border-radius: 12px; margin-top: 8px; }
.qt-learn-term-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.qt-learn-abbr { font-family: 'Baloo 2', cursive; font-size: 22px; font-weight: 800; color: var(--gold); }
.qt-learn-expansion { font-size: 13px; font-weight: 600; color: var(--text); margin: 4px 0; }
.qt-learn-def { font-size: 12px; color: var(--dim); line-height: 1.5; margin: 0; }
.qt-learn-example { font-size: 11.5px; color: var(--abc-sky); margin: 8px 0 0; line-height: 1.45; }
.qt-learn-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.qt-team-challenge { padding: 10px 12px !important; }

/* business banking paths (participant hub) */
.qt-business-paths { margin-bottom: 12px; }
.qt-path-branch { margin-bottom: 10px; padding: 10px 12px; background: rgba(0,0,0,.18);
  border: 1px solid var(--stroke); border-radius: 12px; }
.qt-path-summary { cursor: pointer; font-size: 14px; font-weight: 700; color: var(--text);
  list-style: none; display: flex; align-items: center; gap: 8px; }
.qt-path-summary::-webkit-details-marker { display: none; }
.qt-path-blurb { font-size: 11.5px; color: var(--dim); margin: 8px 0 10px; line-height: 1.45; }
.qt-path-term { font-size: 12px; padding: 5px 0; border-bottom: 1px dashed rgba(255,255,255,.06);
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.qt-path-term b { color: var(--gold); min-width: 48px; }
body:has(.qt-hub-scope) .qt-learn-tree { max-height: 420px; }

/* participant hub — left nav rail (clean flex, no negative-margin overlap) */
body:has(.qt-hub-scope) [data-testid="stHorizontalBlock"]:has(.qt-hub-nav-col) {
  align-items: flex-start !important;
  overflow: visible !important;
}
body:has(.qt-hub-scope) [data-testid="stColumn"]:has(.qt-hub-nav-col),
body:has(.qt-hub-scope) [data-testid="column"]:has(.qt-hub-nav-col) {
  align-self: flex-start !important;
  overflow: visible !important;
  position: sticky;
  top: 12px;
}
body:has(.qt-hub-scope) .qt-hub-nav-rail {
  box-sizing: border-box;
  padding: 18px 16px 14px;
  margin: 0 0 10px;
}
body:has(.qt-hub-scope) .qt-hub-nav-rail .qt-cat {
  text-align: left !important;
  margin-bottom: 6px;
  letter-spacing: 2px;
}
body:has(.qt-hub-scope) .qt-hub-nav-title {
  display: flex; align-items: center; gap: 10px;
}
.qt-hub-nav-inner {
  display: inline-flex; align-items: center; gap: 12px; width: 100%;
}
.qt-hub-nav-label { line-height: 1.2; }
.qt-hub-nav-ico {
  display: inline-flex; align-items: center; flex-shrink: 0; line-height: 0;
  transition: transform .18s ease, filter .2s ease;
}
.qt-hub-nav-ico svg { display: block; }
.qt-hub-nav-ico.is-active {
  transform: scale(1.12);
  filter: drop-shadow(0 0 6px rgba(77,180,255,.55));
}
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_"] .stButton > button:hover .qt-hub-nav-ico {
  transform: scale(1.08);
}
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_"] .stButton > button {
  display: inline-flex !important;
  align-items: center !important;
}
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_"] .stButton > button p {
  display: flex !important;
  align-items: center !important;
  width: 100% !important;
  margin: 0 !important;
}
body:has(.qt-hub-nav-collapsed) div[class*="st-key-hub_nav_"]:not([class*="hub_nav_toggle"]) .qt-hub-nav-inner {
  justify-content: center;
}
body:has(.qt-hub-nav-collapsed) div[class*="st-key-hub_nav_toggle"] .qt-hub-nav-inner {
  justify-content: center;
}
body:has(.qt-hub-scope) .qt-hub-nav-who {
  font-size: 13px; font-weight: 700; color: var(--text);
  padding: 10px 0 4px; border-top: 1px dashed rgba(255,255,255,.08);
  margin-top: 10px;
}
body:has(.qt-hub-scope) [data-testid="stColumn"]:has(.qt-hub-main-col),
body:has(.qt-hub-scope) [data-testid="column"]:has(.qt-hub-main-col) {
  min-width: 0 !important;
}
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_"] { margin-bottom: 6px; }
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_"] .stButton > button {
  justify-content: flex-start !important;
  text-align: left !important;
  border-radius: 14px !important;
  padding: 13px 16px !important;
  font-size: 14.5px !important;
  font-weight: 600 !important;
  width: 100% !important;
  transition: transform .18s ease, box-shadow .2s, border-color .2s !important;
}
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_"] .stButton > button p {
  text-align: left !important;
  font-size: 14.5px !important;
}
/* collapsed rail — icon-only, centered */
body:has(.qt-hub-nav-collapsed) div[class*="st-key-hub_nav_"]:not([class*="hub_nav_toggle"]) .stButton > button {
  justify-content: center !important;
  text-align: center !important;
  padding: 12px 0 !important;
}
body:has(.qt-hub-nav-collapsed) div[class*="st-key-hub_nav_"]:not([class*="hub_nav_toggle"]) .stButton > button p {
  justify-content: center !important;
  text-align: center !important;
}
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_"] .stButton > button[kind="secondary"] {
  background: rgba(255,255,255,.04) !important;
  border: 1px solid rgba(255,255,255,.1) !important;
  box-shadow: none !important;
  color: var(--text-dim) !important;
}
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_"] .stButton > button[kind="secondary"]:hover {
  background: rgba(255,255,255,.1) !important;
  color: var(--text) !important;
  transform: translateX(4px);
  border-color: rgba(77,180,255,.25) !important;
}
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_"] .stButton > button[kind="primary"] {
  background: linear-gradient(135deg, rgba(0,136,206,.32), rgba(0,59,112,.55)) !important;
  border: 1px solid rgba(77,180,255,.45) !important;
  box-shadow: 0 0 16px rgba(77,180,255,.22), inset 0 0 12px rgba(77,180,255,.08) !important;
  color: #fff !important;
}
/* collapse / expand toggle — overrides generic nav-button rules above */
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_toggle"] { margin-bottom: 12px; }
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_toggle"] .stButton > button {
  border-radius: 12px !important;
  padding: 10px 12px !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  color: var(--text-dim) !important;
  background: rgba(255,255,255,.05) !important;
  border: 1px solid rgba(255,255,255,.12) !important;
  box-shadow: none !important;
  transform: none !important;
  justify-content: center !important;
}
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_toggle"] .stButton > button p {
  font-size: 13px !important;
  justify-content: center !important;
}
body:has(.qt-hub-scope) div[class*="st-key-hub_nav_toggle"] .stButton > button:hover {
  color: var(--text) !important;
  background: rgba(255,255,255,.1) !important;
  border-color: rgba(77,180,255,.3) !important;
  transform: none !important;
}
body:has(.qt-hub-scope) .qt-hub-join-card { margin-bottom: 18px; padding: 22px 26px 18px; }
body:has(.qt-hub-join-active) [data-testid="stForm"] {
  background: var(--glass);
  border: 1px solid var(--stroke);
  border-radius: 16px;
  padding: 20px 24px 12px;
}
body:has(.qt-hub-join-active) [data-testid="stFormSubmitButton"] > button {
  margin-top: 8px;
}

/* quiz domain guide drawer (parent-realm) */
#qt-learn-drawer { position: fixed; inset: 0; z-index: 99990; pointer-events: none; opacity: 0; transition: opacity 0.3s ease; }
#qt-learn-drawer.open { pointer-events: auto; opacity: 1; }
.qt-drawer-backdrop { position: absolute; inset: 0; background: rgba(1,8,17,.65); backdrop-filter: blur(4px); }
.qt-drawer-panel { position: absolute; top: 0; right: 0; width: min(380px, 92vw); height: 100%;
  background: #0a1628; border-left: 1px solid var(--stroke); padding: 20px 18px;
  overflow-y: auto; box-shadow: -8px 0 40px rgba(0,0,0,.45); }
.qt-drawer-enter { animation: qtDrawerIn 0.35s cubic-bezier(.22,1,.36,1) forwards; }
.qt-drawer-exit { animation: qtDrawerOut 0.28s ease forwards; }
@keyframes qtDrawerIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
@keyframes qtDrawerOut { from { transform: translateX(0); } to { transform: translateX(100%); } }
.qt-drawer-close { position: absolute; top: 14px; right: 14px; background: rgba(255,255,255,.08);
  border: 1px solid var(--stroke); color: var(--text); border-radius: 50%; width: 32px; height: 32px;
  cursor: pointer; font-size: 14px; }
.qt-drawer-head { font-family: 'Baloo 2', cursive; font-size: 22px; font-weight: 800; margin-bottom: 4px; }
.qt-drawer-sub { font-size: 11px; color: var(--dim); margin-bottom: 16px; letter-spacing: 1px; }
.qt-drawer-term { padding: 10px 0; border-bottom: 1px dashed rgba(255,255,255,.07); }
.qt-drawer-abbr { font-weight: 800; color: var(--gold); font-size: 15px; }
.qt-drawer-exp { font-size: 12px; font-weight: 600; margin: 2px 0; }
.qt-drawer-def { font-size: 11px; color: var(--dim); line-height: 1.4; }
.qt-learn-fab { position: fixed; bottom: 24px; right: 24px; z-index: 9998;
  background: linear-gradient(135deg, #0088ce, #003b70); color: #fff; border: 1px solid rgba(77,180,255,.4);
  border-radius: 999px; padding: 12px 20px; font-family: Poppins, sans-serif; font-weight: 700;
  font-size: 13px; cursor: pointer; box-shadow: 0 8px 28px rgba(0,136,206,.45);
  animation: qtGlow 2.2s ease-in-out infinite; }
.qt-learn-fab:hover { transform: scale(1.05); }

/* points pop + term mastered burst */
.qt-points-pop { position: fixed; left: 50%; top: 42%; transform: translate(-50%, 0) scale(0.6);
  font-family: 'Baloo 2', cursive; font-size: 48px; font-weight: 800; color: var(--gold);
  text-shadow: 0 0 20px rgba(255,194,51,.8); z-index: 99999; pointer-events: none; opacity: 0;
  transition: opacity 0.2s, transform 0.5s cubic-bezier(.34,1.56,.64,1); }
.qt-points-pop.show { opacity: 1; transform: translate(-50%, -40px) scale(1); }
.qt-master-burst { position: fixed; left: 50%; top: 50%; transform: translate(-50%,-50%);
  z-index: 99999; pointer-events: none; }
.qt-master-burst span { position: absolute; width: 8px; height: 8px; border-radius: 50%;
  background: var(--teal); box-shadow: 0 0 10px var(--teal); opacity: 0; }
.qt-master-burst.pop span:nth-child(1) { animation: qtBurst 0.9s ease forwards; transform: rotate(0deg) translateY(-40px); }
.qt-master-burst.pop span:nth-child(2) { animation: qtBurst 0.9s 0.05s ease forwards; transform: rotate(72deg) translateY(-40px); }
.qt-master-burst.pop span:nth-child(3) { animation: qtBurst 0.9s 0.1s ease forwards; transform: rotate(144deg) translateY(-40px); }
.qt-master-burst.pop span:nth-child(4) { animation: qtBurst 0.9s 0.15s ease forwards; transform: rotate(216deg) translateY(-40px); }
.qt-master-burst.pop span:nth-child(5) { animation: qtBurst 0.9s 0.2s ease forwards; transform: rotate(288deg) translateY(-40px); }
@keyframes qtBurst { 0% { opacity: 1; } 100% { opacity: 0; transform: rotate(var(--r,0deg)) translateY(-80px) scale(0); } }

/* streak fire upgrade on HUD */
body:has(.qt-quiz-scope) .qt-hud .streak-hot-3 { box-shadow: 0 0 12px rgba(255,140,60,.4); }
body:has(.qt-quiz-scope) .qt-hud .streak-hot-5 { box-shadow: 0 0 20px rgba(255,100,40,.55); animation: qtGlow 1.5s ease-in-out infinite; }
body:has(.qt-quiz-scope) .qt-hud .streak-hot-10 { box-shadow: 0 0 28px rgba(226,24,54,.6); animation: qtGlow 0.9s ease-in-out infinite; }

/* ================= responsive ================= */
html { -webkit-text-size-adjust: 100%; }

/* laptops / small desktops */
@media (max-width: 1180px) {
  .block-container { max-width: 100%; padding-left: 1.6rem; padding-right: 1.6rem; }
}

/* tablets (iPad portrait ≈ 768–1024px) */
@media (max-width: 1024px) {
  .qt-h1 { font-size: 54px !important; }
  .qt-h1 .qt-brand { font-size: 58px !important; }
  .qt-pin { font-size: 54px; letter-spacing: 10px; }
  body:has(.qt-quiz-scope) .qt-question { font-size: 26px; }
  body:has(.qt-quiz-scope) .qt-qcard { padding: 30px 28px 26px; }
  body:has(.qt-quiz-scope) div[class*="st-key-ans"] .stButton > button { min-height: 84px !important; font-size: 18px !important; }
  body:has(.qt-quiz-scope) div[class*="st-key-ans"] .stButton > button p { font-size: 18px !important; }
  .qt-question { font-size: 22px; }
  .qt-qcard { padding: 26px 24px 24px; }
}

/* small tablets / large phones — stack Streamlit columns vertically */
@media (max-width: 880px) {
  [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
  [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex: 1 1 100% !important; width: 100% !important; min-width: 100% !important;
  }
  body:has(.qt-login-scope) [data-testid="stColumn"]:has(.qt-login-card),
  body:has(.qt-login-scope) [data-testid="column"]:has(.qt-login-card) {
    padding: 28px 22px 26px !important;
  }
  body:has(.qt-quiz-scope) .qt-stats-rail {
    left: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    min-height: 0 !important;
    border-radius: 16px !important;
  }
  body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-stage-col),
  body:has(.qt-quiz-scope) [data-testid="column"]:has(.qt-quiz-stage-col) {
    margin-left: 0 !important;
    padding-left: 0 !important;
  }
  body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-chat-col),
  body:has(.qt-quiz-scope) [data-testid="column"]:has(.qt-quiz-chat-col) {
    flex: 1 1 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
    margin-left: 0 !important;
    right: 0 !important;
    width: 100% !important;
  }
  body:has(.qt-quiz-scope) .qt-chat-head,
  body:has(.qt-quiz-scope) .qt-chat-solo {
    text-align: left !important;
    margin-left: 0;
  }
  body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-stage-col) .qt-qcard,
  body:has(.qt-quiz-scope) [data-testid="stColumn"]:has(.qt-quiz-stage-col) div[class*="st-key-ans"] {
    margin-left: 0 !important;
  }
  body:has(.qt-hub-scope) .qt-hub-nav-rail {
    left: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    border-radius: 16px !important;
  }
  body:has(.qt-hub-scope) [data-testid="stColumn"]:has(.qt-hub-main-col),
  body:has(.qt-hub-scope) [data-testid="column"]:has(.qt-hub-main-col) {
    margin-left: 0 !important;
  }
  .qt-mascot { width: 66px; height: 66px; font-size: 36px; top: -26px; right: -12px; border-radius: 20px; }
  .qt-podium { gap: 10px; }
  .qt-step { width: 100px; }
  .qt-step .blk { font-size: 30px; }
  .qt-bars { gap: 12px; height: 140px; }
  .qt-barcol { width: 58px; }
  .qt-topbar { flex-wrap: wrap; gap: 10px; }
  #qt-creator-credit { right: 10px !important; bottom: 10px !important;
    background: rgba(5,13,28,.78); padding: 6px 16px; border-radius: 999px;
    border: 1px solid rgba(255,255,255,.12); opacity: 1 !important; }
}

/* phones */
@media (max-width: 640px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: .8rem; }
  .qt-h1 { font-size: 38px !important; }
  .qt-h1 .qt-brand { font-size: 42px !important; }
  .qt-brand { font-size: 30px; }
  .qt-pin { font-size: 42px; letter-spacing: 6px; }
  body:has(.qt-quiz-scope) .qt-question { font-size: 22px; margin-bottom: 14px; }
  body:has(.qt-quiz-scope) div[class*="st-key-ans"] .stButton > button { min-height: 72px !important; font-size: 17px !important; padding-left: 20px !important; }
  body:has(.qt-quiz-scope) div[class*="st-key-ans"] .stButton > button p { font-size: 17px !important; }
  .qt-question { font-size: 19px; margin-bottom: 12px; }
  .qt-verdict .big { font-size: 42px; }
  .qt-verdict-ans-text { font-size: 18px; }
  .qt-verdict-ans-letter { width: 36px; height: 36px; font-size: 17px; }
  .qt-pill { font-size: 11.5px; padding: 5px 10px; }
  .qt-badge { padding: 9px 13px; font-size: 12.5px; margin-right: 6px; }
  .qt-card { padding: 16px 16px; }
  div[class*="st-key-ans"] .stButton > button { min-height: 62px !important; font-size: 16px !important; padding-left: 18px !important; }
  div[class*="st-key-ans"] .stButton > button p { font-size: 16px !important; }
  .stButton > button, .stFormSubmitButton > button { padding: 11px 20px !important; font-size: 15px !important; }
  .qt-hud .qno { font-size: 16px; }
  .stTabs [data-baseweb="tab-list"] { overflow-x: auto; }
  .stTabs [data-baseweb="tab"] { padding: 8px 13px; font-size: 13.5px; white-space: nowrap; }
  .qt-timer { width: 72px; height: 72px; }
  .qt-timer .num { font-size: 26px; }
  .qt-mestrip { flex-wrap: wrap; padding: 12px 14px; }
  .qt-kpi .n { font-size: 26px; }
  body:has(.qt-results-scope) .qt-champ-headline { font-size: 42px; }
  body:has(.qt-results-scope) .qt-champ-trophy { font-size: 88px; }
  body:has(.qt-results-scope) .qt-champ-spotlight {
    flex-wrap: wrap; justify-content: center; gap: 10px 14px;
    padding: 16px 20px; max-width: 100%;
  }
  body:has(.qt-results-scope) .qt-champ-identity { align-items: center; text-align: center; }
  body:has(.qt-results-scope) .qt-champ-name { font-size: 30px; }
  body:has(.qt-results-scope) .qt-champ-avatar { font-size: 48px; }
  body:has(.qt-results-scope) .qt-champ-crown { font-size: 28px; }
  .qt-chatbox { height: 220px; }
  #qt-creator-credit { right: 10px !important; bottom: 10px !important; font-size: 22px !important;
    background: rgba(5,13,28,.78); padding: 6px 14px; border-radius: 999px;
    border: 1px solid rgba(255,255,255,.12); opacity: 1 !important; }
}

/* touch devices — restore the native cursor, drop pointer-only effects */
@media (hover: none), (pointer: coarse) {
  #qt-glow, #qt-ink { display: none !important; }
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
  const staleCursor = doc.getElementById("qt-neon-cursor");
  if (staleCursor) staleCursor.remove();

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


_FLOATERS_JS = """
<script>
(function() {
  const P = window.parent, doc = P.document;

  function mountFloaters() {
    const host = doc.querySelector('[data-testid="stAppViewContainer"]') || doc.querySelector('.stApp');
    if (!host) return;
    host.style.position = 'relative';
    host.style.isolation = 'isolate';
    let wrap = doc.getElementById('qt-floaters');
    if (!wrap) {
      const syms = ['?', '!', '★', '▲', '●', '◆', '?', '♦'];
      wrap = doc.createElement('div');
      wrap.id = 'qt-floaters';
      wrap.className = 'qt-floaters';
      for (let i = 0; i < 14; i++) {
        const s = doc.createElement('span');
        s.className = 'qt-floater';
        s.textContent = syms[i % syms.length];
        s.style.left = (Math.random() * 100) + 'vw';
        s.style.animationDelay = (Math.random() * -14) + 's';
        s.style.animationDuration = (10 + Math.random() * 10) + 's';
        s.style.fontSize = (16 + Math.random() * 26) + 'px';
        wrap.appendChild(s);
      }
    }
    if (wrap.parentElement !== host || host.firstChild !== wrap) {
      host.insertBefore(wrap, host.firstChild);
    }
    const main = host.querySelector('section.main, [data-testid="stMain"]');
    if (main) { main.style.position = 'relative'; main.style.zIndex = '2'; }
  }

  mountFloaters();
  if (P.__qtFloaterJanitor) clearInterval(P.__qtFloaterJanitor);
  P.__qtFloaterJanitor = setInterval(mountFloaters, 400);

  function syncStatsRailHeight() {
    const rail = doc.querySelector('.qt-stats-rail');
    if (!doc.querySelector('.qt-quiz-scope') || !rail || P.innerWidth <= 880) {
      if (rail) rail.style.minHeight = '';
      return;
    }
    let anchor = null;
    const ans = doc.querySelectorAll('div[class*="st-key-ans"] .stButton > button');
    if (ans.length) anchor = ans[ans.length - 1];
    else {
      const verdict = doc.querySelector('.qt-verdict');
      if (verdict) anchor = verdict;
      else {
        const votes = doc.querySelectorAll('div[class*="st-key-vote"] .stButton > button');
        if (votes.length) anchor = votes[votes.length - 1];
      }
    }
    if (!anchor) { rail.style.minHeight = ''; return; }
    rail.style.minHeight = '';
    const railTop = rail.getBoundingClientRect().top;
    const needed = anchor.getBoundingClientRect().bottom - railTop;
    const minH = Math.max(rail.offsetHeight, needed);
    if (minH > 0) rail.style.minHeight = minH + 'px';
  }

  syncStatsRailHeight();
  if (P.__qtStatsRailSync) clearInterval(P.__qtStatsRailSync);
  P.__qtStatsRailSync = setInterval(syncStatsRailHeight, 350);
  P.addEventListener('resize', syncStatsRailHeight);

  // parent-realm janitor: keeps the login mascot/glow-ring in sync with the login page
  if (!P.__qtJanitor) {
    const s = doc.createElement('script');
    s.textContent = "window.__qtJanitor = setInterval(function(){" +
      "var scope = document.querySelector('.qt-login-scope');" +
      "var marker = document.querySelector('.qt-login-card');" +
      "var card = marker ? marker.closest('[data-testid=\\\"stColumn\\\"], [data-testid=\\\"column\\\"]') : null;" +
      "var m = document.getElementById('qt-login-mascot');" +
      "if (!scope || !card) {" +
      "  if (m) m.remove();" +
      "  document.querySelectorAll('.qt-glow-ring').forEach(function(r){ r.remove(); });" +
      "  return;" +
      "}" +
      "card.style.position = 'relative'; card.style.overflow = 'visible';" +
      "var ring = card.querySelector('.qt-glow-ring');" +
      "if (!ring) {" +
      "  ring = document.createElement('div'); ring.className = 'qt-glow-ring';" +
      "  card.insertBefore(ring, card.firstChild);" +
      "} else if (ring.parentElement !== card) { card.insertBefore(ring, card.firstChild); }" +
      "if (!m) {" +
      "  m = document.createElement('div'); m.id = 'qt-login-mascot';" +
      "  m.className = 'qt-mascot'; m.textContent = '?'; card.appendChild(m);" +
      "} else if (m.parentElement !== card) { card.appendChild(m); }" +
      "}, 600);";
    doc.body.appendChild(s);
  }
})();
</script>
"""


def inject() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    st_components.html(_GLOW_JS, height=0)
    st_components.html(_FLOATERS_JS, height=0)

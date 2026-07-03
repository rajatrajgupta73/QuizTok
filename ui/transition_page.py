"""Neon loading transition shown after login — 0→100% with role, name and SOEID/email."""
import time
import streamlit as st
import streamlit.components.v1 as components

import config

_ICONS   = {"admin": "⚡", "host": "🎛️", "participant": "🎮"}
_LABELS  = {"admin": "ADMIN", "host": "HOST", "participant": "PARTICIPANT"}
_ACCENTS = {
    "admin":       ("#e21836", "226,24,54"),
    "host":        ("#00c9a7", "0,201,167"),
    "participant": ("#0088ce", "0,136,206"),
}


def render() -> None:
    role = st.session_state.get("role", "")
    if not role:
        st.session_state["page"] = "login"
        st.rerun()
        return

    dest     = st.session_state.get("dest_page", "lobby")
    accent, glow = _ACCENTS.get(role, _ACCENTS["participant"])
    icon     = _ICONS.get(role, "🎮")
    label    = _LABELS.get(role, "PARTICIPANT")

    if role == "participant":
        name  = st.session_state.get("nick", "Player")
        sub   = st.session_state.get("soeid", "")
        team  = st.session_state.get("team", "")
    elif role == "host":
        name  = st.session_state.get("admin_name", "Host")
        sub   = st.session_state.get("admin_email", "")
        team  = st.session_state.get("team", "")
    else:
        name  = st.session_state.get("admin_name", "Admin")
        sub   = st.session_state.get("admin_email", "")
        team  = ""

    st.markdown(_overlay(name, sub, team, label, icon, accent, glow), unsafe_allow_html=True)
    components.html(_js(), height=1)
    time.sleep(3.4)
    st.session_state["page"] = dest
    st.rerun()


# ── HTML overlay (position:fixed full-screen — no scripts) ──────────────────

def _overlay(name: str, sub: str, team: str, label: str, icon: str,
             accent: str, glow: str) -> str:
    team_html = (
        f'<div class="qt-tr-team"><span style="opacity:.45;margin-right:6px;font-size:9px">'
        f'TEAM</span>{team}</div>'
    ) if team else ""

    return f"""
<style>
[data-testid="stHeader"]{{display:none!important}}
.block-container{{padding:0!important;max-width:100vw!important}}
[data-testid="stAppViewContainer"]{{background:#010811!important}}
[data-testid="stVerticalBlock"]{{gap:0!important}}

#qt-tr{{
  position:fixed;inset:0;z-index:9999;
  background:#010811;
  display:flex;align-items:center;justify-content:center;
  overflow:hidden;
  font-family:'Poppins','Segoe UI',sans-serif;
}}

/* animated grid */
#qt-tr::before{{
  content:'';position:absolute;inset:0;
  background-image:
    linear-gradient(rgba({glow},.04) 1px,transparent 1px),
    linear-gradient(90deg,rgba({glow},.04) 1px,transparent 1px);
  background-size:44px 44px;
  animation:qt-grid 10s linear infinite;
}}
@keyframes qt-grid{{
  from{{background-position:0 0,0 0}}
  to{{background-position:0 44px,44px 0}}
}}

/* radial vignette glow behind center */
#qt-tr::after{{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 60% 50% at 50% 50%,
    rgba({glow},.09) 0%,transparent 70%);
  pointer-events:none;
}}

/* scan line */
.qt-tr-scan{{
  position:absolute;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,rgba({glow},.55),transparent);
  animation:qt-scan 2.5s linear infinite;pointer-events:none;
}}
@keyframes qt-scan{{
  0%{{top:-2px;opacity:0}}5%{{opacity:1}}95%{{opacity:.6}}100%{{top:100%;opacity:0}}
}}

/* corner brackets */
.qt-tr-c{{position:absolute;width:52px;height:52px;border-color:{accent};border-style:solid;animation:qt-cp 2.5s ease-in-out infinite}}
@keyframes qt-cp{{0%,100%{{opacity:.3}}50%{{opacity:.85}}}}
.qt-tr-c.tl{{top:22px;left:22px;border-width:2px 0 0 2px}}
.qt-tr-c.tr{{top:22px;right:22px;border-width:2px 2px 0 0}}
.qt-tr-c.bl{{bottom:22px;left:22px;border-width:0 0 2px 2px}}
.qt-tr-c.br{{bottom:22px;right:22px;border-width:0 2px 2px 0}}

/* center block */
.qt-tr-mid{{
  position:relative;z-index:10;text-align:center;
  animation:qt-rise .7s cubic-bezier(.34,1.56,.64,1) forwards;
}}
@keyframes qt-rise{{
  from{{opacity:0;transform:translateY(30px) scale(.93)}}
  to{{opacity:1;transform:translateY(0) scale(1)}}
}}

/* icon ring */
.qt-tr-ring{{
  width:84px;height:84px;border-radius:50%;
  border:2px solid {accent};
  margin:0 auto 20px;
  display:flex;align-items:center;justify-content:center;
  font-size:32px;line-height:1;
  background:rgba({glow},.08);
  box-shadow:0 0 28px rgba({glow},.55),inset 0 0 22px rgba({glow},.12);
  animation:qt-rp 2.2s ease-in-out infinite;
}}
@keyframes qt-rp{{
  0%,100%{{box-shadow:0 0 28px rgba({glow},.55),inset 0 0 22px rgba({glow},.12)}}
  50%{{box-shadow:0 0 52px rgba({glow},.9),inset 0 0 36px rgba({glow},.22)}}
}}

/* role badge */
.qt-tr-badge{{
  display:inline-block;padding:4px 20px;
  border:1px solid rgba({glow},.6);border-radius:99px;
  color:{accent};font-size:10px;font-weight:700;letter-spacing:4px;
  background:rgba({glow},.08);box-shadow:0 0 12px rgba({glow},.3);
  margin-bottom:14px;
}}

/* name */
.qt-tr-name{{
  font-size:clamp(28px,6vw,50px);font-weight:800;color:#fff;
  line-height:1.1;letter-spacing:-1px;margin-bottom:8px;
  text-shadow:0 0 22px rgba({glow},.9),0 0 55px rgba({glow},.4),0 0 95px rgba({glow},.15);
}}

/* soeid / email */
.qt-tr-sub{{
  font-size:12px;color:rgba(255,255,255,.38);
  letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;
}}

/* team pill */
.qt-tr-team{{
  display:inline-block;padding:4px 16px;margin-bottom:0;
  background:rgba({glow},.1);border:1px solid rgba({glow},.28);
  border-radius:99px;color:{accent};
  font-size:11px;letter-spacing:1px;font-weight:600;
}}

/* progress */
.qt-tr-prog{{margin-top:32px;width:340px;max-width:86vw}}

.qt-tr-pct-row{{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:9px;
}}
.qt-tr-lbl{{font-size:10px;letter-spacing:2px;color:rgba(255,255,255,.28);text-transform:uppercase}}
.qt-tr-pct{{
  font-size:14px;font-weight:700;color:{accent};
  text-shadow:0 0 10px {accent};font-variant-numeric:tabular-nums;
}}

.qt-tr-bar-bg{{width:100%;height:4px;background:rgba(255,255,255,.06);border-radius:99px;overflow:hidden}}
.qt-tr-bar-fill{{
  height:100%;width:0;border-radius:99px;
  background:linear-gradient(90deg,{accent},rgba(255,255,255,.65));
  box-shadow:0 0 12px {accent},0 0 28px rgba({glow},.5);
  animation:qt-bar 3.1s cubic-bezier(.4,0,.2,1) forwards;
}}
@keyframes qt-bar{{0%{{width:0%}}100%{{width:100%}}}}

/* bounce dots */
.qt-tr-dots{{display:flex;gap:7px;justify-content:center;margin-top:18px}}
.qt-tr-dot{{
  width:6px;height:6px;border-radius:50%;
  background:{accent};box-shadow:0 0 6px {accent};
  animation:qt-dot 1.2s ease-in-out infinite;
}}
.qt-tr-dot:nth-child(2){{animation-delay:.2s}}
.qt-tr-dot:nth-child(3){{animation-delay:.4s}}
@keyframes qt-dot{{
  0%,80%,100%{{transform:scale(.6);opacity:.35}}
  40%{{transform:scale(1.35);opacity:1}}
}}

/* floating particles (spawned by JS) */
.qt-tr-pt{{
  position:absolute;border-radius:50%;background:{accent};
  pointer-events:none;animation:qt-pt linear infinite;
}}
@keyframes qt-pt{{
  0%{{transform:translateY(110vh);opacity:0}}
  6%{{opacity:.75}}94%{{opacity:.3}}
  100%{{transform:translateY(-10vh);opacity:0}}
}}
</style>

<div id="qt-tr">
  <div class="qt-tr-scan"></div>
  <div class="qt-tr-c tl"></div><div class="qt-tr-c tr"></div>
  <div class="qt-tr-c bl"></div><div class="qt-tr-c br"></div>

  <div class="qt-tr-mid">
    <div class="qt-tr-ring">{icon}</div>
    <div class="qt-tr-badge">{label}</div>
    <div class="qt-tr-name">{name}</div>
    <div class="qt-tr-sub">{sub}</div>
    {team_html}
    <div class="qt-tr-prog">
      <div class="qt-tr-pct-row">
        <span class="qt-tr-lbl">Loading Profile</span>
        <span class="qt-tr-pct" id="qt-tr-pct">0%</span>
      </div>
      <div class="qt-tr-bar-bg"><div class="qt-tr-bar-fill"></div></div>
      <div class="qt-tr-dots">
        <div class="qt-tr-dot"></div>
        <div class="qt-tr-dot"></div>
        <div class="qt-tr-dot"></div>
      </div>
    </div>
  </div>
</div>
"""


# ── JS (runs inside an iframe, reaches parent DOM) ──────────────────────────

def _js() -> str:
    return """
<script>
(function(){
  var par = window.parent;
  var el  = par.document.getElementById('qt-tr-pct');
  if (!el) return;

  var start = Date.now(), dur = 3100;

  function ease(t){ return t<.5 ? 4*t*t*t : 1-Math.pow(-2*t+2,3)/2; }

  function tick(){
    var t = Math.min((Date.now()-start)/dur, 1);
    el.textContent = Math.floor(ease(t)*100)+'%';
    if(t<1) requestAnimationFrame(tick); else el.textContent='100%';
  }
  requestAnimationFrame(tick);

  // spawn floating particles
  var overlay = par.document.getElementById('qt-tr');
  if(overlay){
    for(var i=0;i<38;i++){
      var p = par.document.createElement('div');
      p.className='qt-tr-pt';
      var sz = 1.5 + Math.random()*3.5;
      p.style.cssText='width:'+sz+'px;height:'+sz+'px;'
        +'left:'+(Math.random()*100)+'vw;'
        +'animation-duration:'+(4+Math.random()*5)+'s;'
        +'animation-delay:'+(Math.random()*3.5)+'s;'
        +'box-shadow:0 0 '+(sz*3)+'px currentColor;';
      overlay.appendChild(p);
    }
  }
})();
</script>
"""

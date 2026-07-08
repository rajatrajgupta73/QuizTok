"""Domain Academy — learn panel rail (lobby) and slide-out drawer (quiz)."""
from __future__ import annotations

import html
import json

import streamlit as st
import streamlit.components.v1 as components

from core import domain_knowledge, feedback


def _esc(text: str) -> str:
    return html.escape(str(text or ""))


def _status_badge(status: str) -> str:
    badges = {
        "mastered": '<span class="qt-learn-badge mastered">✓ Mastered</span>',
        "viewed": '<span class="qt-learn-badge viewed">Seen</span>',
        "needs_review": '<span class="qt-learn-badge review">Review</span>',
    }
    return badges.get(status, '<span class="qt-learn-badge new">New</span>')


def term_detail_card(term: dict, status: str = "") -> str:
    chips = ""
    qids = str(term.get("related_qids") or "").split(",")
    qids = [q.strip() for q in qids if q.strip()]
    if qids:
        chips = "".join(f'<span class="qt-badge">{_esc(q)}</span>' for q in qids[:4])
        chips = f'<div class="qt-learn-chips">{chips}</div>'
    return (
        f'<div class="qt-learn-term qt-rise">'
        f'<div class="qt-learn-term-head">'
        f'<span class="qt-learn-abbr">{_esc(term.get("abbr", ""))}</span>'
        f'{_status_badge(status)}</div>'
        f'<div class="qt-learn-expansion">{_esc(term.get("expansion", ""))}</div>'
        f'<p class="qt-learn-def">{_esc(term.get("definition", ""))}</p>'
        f'<p class="qt-learn-example"><b>Example:</b> {_esc(term.get("example", ""))}</p>'
        f'{("<div class=\"qt-sub\" style=\"font-size:10px;margin-top:8px\">Related questions: </div>" + chips) if chips else ""}'
        f'</div>'
    )


def _progress_rings(summary: dict) -> str:
    rings = []
    for label, info in summary.get("by_domain", {}).items():
        total = max(info.get("total", 1), 1)
        pct = int(info.get("mastered", 0) / total * 100)
        rings.append(
            f'<div class="qt-learn-ring-item">'
            f'<svg class="qt-learn-ring" viewBox="0 0 36 36">'
            f'<path class="qt-learn-ring-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>'
            f'<path class="qt-learn-ring-fill" stroke-dasharray="{pct},100" '
            f'd="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>'
            f'</svg>'
            f'<div class="qt-learn-ring-lbl">{info.get("emoji", "")} {_esc(label[:14])}'
            f'<br><b>{info.get("mastered", 0)}/{total}</b></div></div>'
        )
    return f'<div class="qt-learn-rings">{"".join(rings)}</div>'


def _tree_html(parent_id: str, progress: dict[str, str], depth: int = 0) -> str:
    rows = []
    for node in domain_knowledge.get_children(parent_id):
        nid = node["node_id"]
        ntype = node.get("node_type", "")
        label = _esc(node.get("label", ""))
        emoji = node.get("emoji", "")
        indent = depth * 16
        if ntype == "term":
            term = domain_knowledge.get_term_by_node(nid)
            if not term:
                continue
            tid = term["term_id"]
            status = progress.get(tid, "")
            rows.append(
                f'<div class="qt-tree-row term" style="padding-left:{indent}px" '
                f'data-term="{_esc(tid)}">'
                f'<span class="qt-tree-dot">📖</span>'
                f'<span class="qt-tree-label">{label}</span>'
                f'{_status_badge(status)}</div>'
            )
        else:
            children = domain_knowledge.get_children(nid)
            rows.append(
                f'<details class="qt-tree-branch" style="margin-left:{indent}px" '
                f'{"open" if depth == 0 else ""}>'
                f'<summary class="qt-tree-summary">'
                f'<span class="qt-tree-chevron">▸</span>{emoji} {label}'
                f'<span class="qt-tree-count">{len([c for c in children if c.get("node_type") == "term"])} terms</span>'
                f'</summary>'
                f'{_tree_html(nid, progress, depth + 1)}'
                f'</details>'
            )
    return "".join(rows)


def _business_paths_html(progress: dict[str, str]) -> str:
    blocks = []
    for path in domain_knowledge.BUSINESS_PATHS:
        terms = domain_knowledge.terms_for_path(path["id"])[:12]
        term_rows = ""
        for t in terms:
            tid = t["term_id"]
            term_rows += (
                f'<div class="qt-path-term">'
                f'<b>{_esc(t["abbr"])}</b> — {_esc(t["expansion"][:55])}'
                f'{_status_badge(progress.get(tid, ""))}</div>'
            )
        blocks.append(
            f'<details class="qt-path-branch" open>'
            f'<summary class="qt-path-summary">{path["emoji"]} {_esc(path["label"])}'
            f'<span class="qt-tree-count">{len(terms)} terms</span></summary>'
            f'<p class="qt-path-blurb">{_esc(path["blurb"])}</p>'
            f'{term_rows}'
            f'</details>'
        )
    return f'<div class="qt-business-paths">{"".join(blocks)}</div>'


def _render_academy_learn_body(nick: str, page: str) -> None:
    """Banking domain academy — paths, tree, search, term actions (no feedback)."""
    st.markdown('<span class="qt-learn-scope"></span>', unsafe_allow_html=True)
    pk = domain_knowledge.player_key(nick)
    summary = domain_knowledge.progress_summary(pk)
    progress = domain_knowledge.progress_for_player(pk)
    daily = domain_knowledge.daily_term()
    achievements = domain_knowledge.player_achievements(pk)

    daily_html = term_detail_card(daily, progress.get(daily["term_id"], "")) if daily else ""
    ach_html = ""
    if achievements:
        ach_html = "".join(
            f'<span class="qt-badge" title="{_esc(a["desc"])}">🏅 {_esc(a["title"])}</span>'
            for a in achievements[:5]
        )
        ach_html = f'<div class="qt-learn-ach">{ach_html}</div>'

    st.markdown(
        f'<div class="qt-rail qt-learn-rail qt-rise">'
        f'<div class="qt-learn-head">'
        f'<div><div class="qt-cat">📚 BANKING DOMAIN ACADEMY</div>'
        f'<div class="qt-sub" style="font-size:12px">Loans · Assets · Wealth · Customer Service · Operations · Digital</div></div>'
        f'<div class="qt-learn-stats">'
        f'<span class="qt-learn-stat"><b>{summary["mastered"]}</b> mastered</span>'
        f'<span class="qt-learn-stat"><b>{summary["viewed"]}</b> viewed</span>'
        f'</div></div>'
        f'{_progress_rings(summary)}'
        f'{ach_html}'
        f'<div class="qt-learn-daily"><div class="qt-cat" style="font-size:11px">🌟 Domain Drop of the Day</div>'
        f'{daily_html}</div>'
        f'<div class="qt-cat" style="margin:18px 0 10px">Business banking paths</div>'
        f'{_business_paths_html(progress)}'
        f'<div class="qt-cat" style="margin:18px 0 8px">Full knowledge tree</div>'
        f'<div class="qt-learn-tree">{_tree_html("", progress)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    search_q = st.text_input("Search glossary", placeholder="e.g. UPI, FCR, KYC, loans…", key=f"learn_search_{page}")
    if search_q.strip():
        hits = domain_knowledge.search_terms(search_q.strip(), limit=8)
        for t in hits:
            st.markdown(term_detail_card(t, progress.get(t["term_id"], "")), unsafe_allow_html=True)

    _render_term_actions(pk, page)


def domain_academy_learn(nick: str, page: str = "hub") -> None:
    """Learn business terms panel (participant hub section)."""
    _render_academy_learn_body(nick, page)


def domain_academy_hub(nick: str, quiz_category: str = "", page: str = "hub") -> None:
    """Full academy block — learn + feedback (results page and legacy callers)."""
    _render_academy_learn_body(nick, page)
    _render_feedback_form(nick, page)


def domain_academy_rail(nick: str, quiz_category: str = "", page: str = "lobby") -> None:
    """Full-width Domain Academy section for lobby (and results)."""
    st.markdown('<span class="qt-learn-scope"></span>', unsafe_allow_html=True)
    pk = domain_knowledge.player_key(nick)
    summary = domain_knowledge.progress_summary(pk)
    progress = domain_knowledge.progress_for_player(pk)
    daily = domain_knowledge.daily_term()
    challenge = domain_knowledge.team_challenge_terms()
    achievements = domain_knowledge.player_achievements(pk)
    next_term = domain_knowledge.next_unviewed_term(pk, quiz_category.split("+")[0].strip() if quiz_category else "")

    daily_html = ""
    if daily:
        daily_html = term_detail_card(daily, progress.get(daily["term_id"], ""))

    ach_html = ""
    if achievements:
        ach_html = "".join(
            f'<span class="qt-badge" title="{_esc(a["desc"])}">🏅 {_esc(a["title"])}</span>'
            for a in achievements[:4]
        )
        ach_html = f'<div class="qt-learn-ach">{ach_html}</div>'

    challenge_html = ", ".join(_esc(t) for t in challenge)
    next_html = ""
    if next_term:
        next_html = (
            f'<div class="qt-sub" style="margin-top:8px">Continue: '
            f'<b style="color:#4db4ff">{_esc(next_term["abbr"])}</b> — '
            f'{_esc(next_term["expansion"][:50])}…</div>'
        )

    st.markdown(
        f'<div class="qt-rail qt-learn-rail qt-rise">'
        f'<div class="qt-learn-head">'
        f'<div><div class="qt-cat">📚 OPS ACADEMY</div>'
        f'<div class="qt-sub" style="font-size:12px">Know it before you quiz it</div></div>'
        f'<div class="qt-learn-stats">'
        f'<span class="qt-learn-stat"><b>{summary["mastered"]}</b> mastered</span>'
        f'<span class="qt-learn-stat"><b>{summary["viewed"]}</b> viewed</span>'
        f'</div></div>'
        f'{_progress_rings(summary)}'
        f'{ach_html}'
        f'<div class="qt-learn-daily"><div class="qt-cat" style="font-size:11px">🌟 Domain Drop of the Day</div>'
        f'{daily_html}</div>'
        f'<div class="qt-learn-challenge">'
        f'<span class="qt-pill">🎯 Team challenge</span> Master: {challenge_html}</div>'
        f'{next_html}'
        f'<div class="qt-cat" style="margin:16px 0 8px">Browse the knowledge tree</div>'
        f'<div class="qt-learn-tree">{_tree_html("", progress)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    _render_term_actions(pk, page)
    _render_feedback_form(nick, page)


def _render_term_actions(pk: str, page: str) -> None:
    col1, col2, col3 = st.columns(3)
    terms = domain_knowledge.load_terms()
    term_ids = terms["term_id"].tolist() if not terms.empty else []
    with col1:
        sel = st.selectbox("Select term", [""] + term_ids, key=f"learn_term_{page}", format_func=lambda x: x or "—")
    with col2:
        if st.button("Mark viewed 👁️", key=f"learn_view_{page}"):
            if sel:
                domain_knowledge.mark_viewed(pk, sel)
                st.rerun()
    with col3:
        if st.button("Got it ✓", key=f"learn_master_{page}"):
            if sel:
                domain_knowledge.mark_mastered(pk, sel)
                inject_term_mastered_burst()
                st.rerun()


def render_feedback_panel(nick: str, page: str = "hub") -> None:
    """Dedicated feedback section on the participant hub."""
    st.markdown('<div class="qt-h3">💡 Feedback</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="qt-sub" style="margin-bottom:14px">Share ideas for animations, content, UX, or operations — '
        'your suggestions go straight to the admin team.</div>',
        unsafe_allow_html=True,
    )
    _render_feedback_form(nick, page, expanded=True)


def _render_feedback_form(nick: str, page: str, expanded: bool = False) -> None:
    form_body = lambda: _feedback_form_fields(nick, page)
    if expanded:
        form_body()
    else:
        with st.expander("💡 Suggest an improvement"):
            form_body()


def _feedback_form_fields(nick: str, page: str) -> None:
    with st.form(f"feedback_{page}", border=False):
        cat = st.selectbox("Category", feedback.FEEDBACK_CATEGORIES, key=f"fb_cat_{page}")
        msg = st.text_area("Your idea", placeholder="Animations, content, UX, operations…", key=f"fb_msg_{page}")
        if st.form_submit_button("Send feedback 🚀"):
            if msg.strip():
                role = st.session_state.get("role", "participant")
                feedback.submit(nick, role, cat, page, msg)
                st.success("Thanks — your idea was sent to the team!")
            else:
                st.warning("Please enter a message.")


def domain_drawer_inject(quiz_category: str = "") -> None:
    """Parent-realm slide-out drawer for in-quiz reference (JS-only toggle)."""
    terms = domain_knowledge.terms_for_category(quiz_category.split("+")[0].strip()) if quiz_category else []
    if not terms and quiz_category:
        terms = domain_knowledge.search_terms(quiz_category[:20], limit=15)
    if not terms:
        terms = domain_knowledge.load_terms().head(20).to_dict("records")

    cards = []
    for t in terms[:24]:
        cards.append(
            f'<div class="qt-drawer-term">'
            f'<div class="qt-drawer-abbr">{_esc(t["abbr"])}</div>'
            f'<div class="qt-drawer-exp">{_esc(t["expansion"])}</div>'
            f'<div class="qt-drawer-def">{_esc(str(t.get("definition", ""))[:120])}…</div>'
            f'</div>'
        )
    cards_json = json.dumps("".join(cards))
    cat_label = _esc(quiz_category or "Banking & Operations")

    components.html(
        f'<script>'
        f'(function(){{'
        f'var P=window.parent, doc=P.document;'
        f'if(P.__qtLearnDrawerInit) return;'
        f'P.__qtLearnDrawerInit=true;'
        f'function ensureDrawer(){{'
        f'  var d=doc.getElementById("qt-learn-drawer");'
        f'  if(d) return d;'
        f'  d=doc.createElement("div");'
        f'  d.id="qt-learn-drawer";'
        f'  d.innerHTML='
        f'"<div class=\\"qt-drawer-backdrop\\"></div>"'
        f'+"<div class=\\"qt-drawer-panel qt-drawer-enter\\">"'
        f'+"<button class=\\"qt-drawer-close\\" aria-label=\\"Close\\">✕</button>"'
        f'+"<div class=\\"qt-drawer-head\\">📚 Domain Guide</div>"'
        f'+"<div class=\\"qt-drawer-sub\\">{cat_label}</div>"'
        f'+"<div class=\\"qt-drawer-body\\">{cards_json}</div>"'
        f'+"</div>";'
        f'  doc.body.appendChild(d);'
        f'  d.querySelector(".qt-drawer-backdrop").onclick=closeDrawer;'
        f'  d.querySelector(".qt-drawer-close").onclick=closeDrawer;'
        f'  return d;'
        f'}}'
        f'function openDrawer(){{'
        f'  var d=ensureDrawer();'
        f'  d.classList.add("open");'
        f'  d.querySelector(".qt-drawer-panel").classList.remove("qt-drawer-exit");'
        f'  d.querySelector(".qt-drawer-panel").classList.add("qt-drawer-enter");'
        f'}}'
        f'function closeDrawer(){{'
        f'  var d=doc.getElementById("qt-learn-drawer");'
        f'  if(!d) return;'
        f'  d.classList.remove("open");'
        f'}}'
        f'P.qtOpenLearnDrawer=openDrawer;'
        f'P.qtCloseLearnDrawer=closeDrawer;'
        f'function injectBtn(){{'
        f'  if(!doc.querySelector(".qt-quiz-scope")){{'
        f'    var old=doc.getElementById("qt-learn-fab");'
        f'    if(old) old.remove();'
        f'    return;'
        f'  }}'
        f'  if(doc.getElementById("qt-learn-fab")) return;'
        f'  var btn=doc.createElement("button");'
        f'  btn.id="qt-learn-fab";'
        f'  btn.className="qt-learn-fab";'
        f'  btn.textContent="📚 Domain Guide";'
        f'  btn.onclick=openDrawer;'
        f'  doc.body.appendChild(btn);'
        f'}}'
        f'setInterval(function(){{'
        f'  if(doc.querySelector(".qt-learn-scope")&&!doc.querySelector(".qt-quiz-scope")){{'
        f'    var d=doc.getElementById("qt-learn-drawer");'
        f'    if(d) d.remove();'
        f'    var f=doc.getElementById("qt-learn-fab");'
        f'    if(f) f.remove();'
        f'  }} else {{ injectBtn(); }}'
        f'}},800);'
        f'}})();'
        f'</script>',
        height=0,
    )


def inject_term_mastered_burst() -> None:
    """CSS particle burst when a term is marked mastered."""
    components.html(
        '<script>'
        '(function(){'
        'var doc=window.parent.document;'
        'if(doc.getElementById("qt-master-burst")) return;'
        'var el=document.createElement("div");'
        'el.id="qt-master-burst";'
        'el.className="qt-master-burst";'
        'el.innerHTML="<span></span><span></span><span></span><span></span><span></span>";'
        'doc.body.appendChild(el);'
        'setTimeout(function(){el.classList.add("pop");},50);'
        'setTimeout(function(){el.remove();},1200);'
        '})();'
        '</script>',
        height=0,
    )

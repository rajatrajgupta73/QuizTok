"""Domain knowledge tree, learning progress, achievements — Banking & Ops Academy."""
from __future__ import annotations

import re
from datetime import datetime

import pandas as pd

import config
from core import question_bank, storage

# Domain root metadata (maps to question_bank categories)
_DOMAIN_META = {
    question_bank.CAT_OPS: ("🏦", "Banking Operations"),
    question_bank.CAT_KPI: ("📊", "KPI & Metrics"),
    question_bank.CAT_CS: ("💬", "Customer Experience"),
    question_bank.CAT_SS: ("📱", "Self-Service & Digital"),
    question_bank.CAT_IVR: ("☎️", "IVR"),
    question_bank.CAT_AI: ("🤖", "Agent Assist & LLM"),
    question_bank.CAT_SUBJ: ("🎭", "Scenarios & Soft Skills"),
}

_OPS_TOPIC_META = {
    "compliance": ("🛡️", "Compliance"),
    "payments": ("💳", "Payments"),
    "accounts": ("🏧", "Accounts & Cards"),
}

_ACHIEVEMENTS = {
    "kyc_champion": ("KYC Champion", "Master all Compliance terms", "compliance"),
    "payments_pro": ("Payments Pro", "Master all Payments terms", "payments"),
    "kpi_wizard": ("KPI Wizard", "Master 10 KPI & Metrics terms", question_bank.CAT_KPI),
    "speed_demon": ("Speed Demon", "Answer 5 KPI questions correctly in one game", "speed"),
    "team_teacher": ("Team Teacher", "Receive 10+ votes on subjective answers", "votes"),
    "domain_explorer": ("Domain Explorer", "View 25 glossary terms", "viewed"),
}

_STATUS_RANK = {"viewed": 1, "needs_review": 2, "mastered": 3}

# Banking business-line paths shown in participant profile hub
BUSINESS_PATHS = [
    {
        "id": "path-loans",
        "emoji": "🏠",
        "label": "Loans & Lending",
        "blurb": "Origination, underwriting, disbursement, NPA and collections",
        "term_ids": ["NPA", "CDD", "EDD", "KYC", "AML", "RCA", "SOP", "MKR-CHKR"],
    },
    {
        "id": "path-assets",
        "emoji": "📈",
        "label": "Assets & Treasury",
        "blurb": "Balance sheet, liquidity, reconciliation and settlement",
        "term_ids": ["CASA", "NPA", "GL", "RECON", "EOD", "RTGS", "NEFT", "SWIFT"],
    },
    {
        "id": "path-wealth",
        "emoji": "💎",
        "label": "Wealth Management",
        "blurb": "Premium clients, PEP screening and advisory journeys",
        "term_ids": ["PEP", "EDD", "KYC", "FATCA", "LEI", "CRM", "CX", "NBA"],
    },
    {
        "id": "path-cx",
        "emoji": "💬",
        "label": "Customer Service",
        "blurb": "Contact center, empathy, escalation and closed-loop feedback",
        "category": question_bank.CAT_CS,
    },
    {
        "id": "path-ops",
        "emoji": "🏦",
        "label": "Operations & Payments",
        "blurb": "UPI, IMPS, cards, compliance rails and back-office controls",
        "category": question_bank.CAT_OPS,
    },
    {
        "id": "path-digital",
        "emoji": "📱",
        "label": "Digital & Channels",
        "blurb": "IVR, self-service, chatbots and agent-assist AI",
        "categories": [question_bank.CAT_SS, question_bank.CAT_IVR, question_bank.CAT_AI],
    },
]


def ensure_domain_tree() -> None:
    """Create domain_tree.xlsx from TERMS if missing."""
    if config.DOMAIN_TREE_XLSX.exists():
        return
    _build_and_write_tree()


def ensure_progress_files() -> None:
    """Ensure learning progress and feedback workbooks exist."""
    storage.ensure_data_dir()
    if not config.LEARNING_PROGRESS_XLSX.exists():
        storage.write_sheet(config.LEARNING_PROGRESS_XLSX, "progress", pd.DataFrame())
        storage.write_sheet(config.LEARNING_PROGRESS_XLSX, "achievements", pd.DataFrame())
    if not config.FEEDBACK_XLSX.exists():
        storage.write_sheet(config.FEEDBACK_XLSX, "feedback", pd.DataFrame())


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _example_for(abbr: str, expansion: str, category: str) -> str:
    examples = {
        "UPI": "Customer pays a merchant using a VPA like name@bank",
        "KYC": "Verify ID and address documents before opening an account",
        "FCR": "Resolve the billing dispute on the first call without a callback",
        "IVR": "Caller says 'block my card' and NLU routes to card-block flow",
        "RAG": "Agent assist pulls the latest policy doc before suggesting an answer",
    }
    if abbr in examples:
        return examples[abbr]
    return f"Apply {expansion} in daily {category.lower()} workflows."


def _build_and_write_tree() -> None:
    nodes: list[dict] = []
    terms_rows: list[dict] = []
    abbr_to_topic: dict[str, str] = {}
    for topic_id, abbrs in config.OPS_TOPIC_TERMS.items():
        for ab in abbrs:
            abbr_to_topic[ab] = topic_id

    sort_d = 0
    for cat, (emoji, label) in _DOMAIN_META.items():
        dom_id = _slug(label)
        sort_d += 1
        nodes.append({
            "node_id": dom_id, "parent_id": "", "label": label, "emoji": emoji,
            "category": cat, "sort_order": sort_d, "node_type": "domain",
        })

        if cat == question_bank.CAT_OPS:
            for ti, (topic_key, (temoji, tlabel)) in enumerate(_OPS_TOPIC_META.items()):
                topic_id = f"{dom_id}-{topic_key}"
                nodes.append({
                    "node_id": topic_id, "parent_id": dom_id, "label": tlabel, "emoji": temoji,
                    "category": cat, "sort_order": ti + 1, "node_type": "topic",
                })
        else:
            topic_id = f"{dom_id}-core"
            nodes.append({
                "node_id": topic_id, "parent_id": dom_id, "label": f"{label} Essentials",
                "emoji": emoji, "category": cat, "sort_order": 1, "node_type": "topic",
            })

        cat_terms = [(a, e, d) for a, e, d, c in question_bank.TERMS if c == cat]
        for ti, (abbr, expansion, definition) in enumerate(cat_terms):
            if cat == question_bank.CAT_OPS:
                topic_key = abbr_to_topic.get(abbr, "accounts")
                parent = f"{dom_id}-{topic_key}"
            else:
                parent = f"{dom_id}-core"
            node_id = f"{parent}-{_slug(abbr)}"
            nodes.append({
                "node_id": node_id, "parent_id": parent, "label": abbr, "emoji": "📖",
                "category": cat, "sort_order": ti + 1, "node_type": "term",
            })
            terms_rows.append({
                "term_id": abbr,
                "node_id": node_id,
                "abbr": abbr,
                "expansion": expansion,
                "definition": definition,
                "example": _example_for(abbr, expansion, cat),
                "related_qids": "",
            })

    nodes_df = pd.DataFrame(nodes)
    terms_df = pd.DataFrame(terms_rows)
    storage.write_sheet(config.DOMAIN_TREE_XLSX, "nodes", nodes_df)
    storage.write_sheet(config.DOMAIN_TREE_XLSX, "terms", terms_df)
    sync_related_qids()


def terms_for_path(path_id: str) -> list[dict]:
    """Terms belonging to a business-line path."""
    path = next((p for p in BUSINESS_PATHS if p["id"] == path_id), None)
    if not path:
        return []
    terms = load_terms()
    if path.get("term_ids"):
        ids = set(path["term_ids"])
        return terms[terms["term_id"].isin(ids)].to_dict("records")
    if path.get("category"):
        return terms_for_category(path["category"])
    if path.get("categories"):
        out = []
        for cat in path["categories"]:
            out.extend(terms_for_category(cat))
        return out
    return []


def load_nodes() -> pd.DataFrame:
    ensure_domain_tree()
    return storage.read_sheet(config.DOMAIN_TREE_XLSX, "nodes")


def load_tree() -> pd.DataFrame:
    """Alias for nodes dataframe."""
    return load_nodes()


def load_terms() -> pd.DataFrame:
    ensure_domain_tree()
    return storage.read_sheet(config.DOMAIN_TREE_XLSX, "terms")


def get_children(parent_id: str = "") -> list[dict]:
    df = load_nodes()
    pid = parent_id or ""
    sub = df[df["parent_id"].fillna("").astype(str) == pid]
    sub = sub.sort_values("sort_order")
    return sub.to_dict("records")


def get_term(term_id: str) -> dict | None:
    df = load_terms()
    row = df[df["term_id"] == term_id]
    if row.empty:
        return None
    return row.iloc[0].to_dict()


def get_term_by_node(node_id: str) -> dict | None:
    df = load_terms()
    row = df[df["node_id"] == node_id]
    if row.empty:
        return None
    return row.iloc[0].to_dict()


def search_terms(query: str, limit: int = 20) -> list[dict]:
    q = query.strip().lower()
    if not q:
        return []
    df = load_terms()
    mask = (
        df["abbr"].str.lower().str.contains(q, na=False)
        | df["expansion"].str.lower().str.contains(q, na=False)
        | df["definition"].str.lower().str.contains(q, na=False)
    )
    return df[mask].head(limit).to_dict("records")


def terms_for_category(category: str) -> list[dict]:
    nodes = load_nodes()
    terms = load_terms()
    term_nodes = set(nodes[(nodes["category"] == category) & (nodes["node_type"] == "term")]["node_id"])
    return terms[terms["node_id"].isin(term_nodes)].to_dict("records")


def sync_related_qids() -> int:
    """Link bank questions to glossary terms by keyword match."""
    ensure_domain_tree()
    try:
        bank = question_bank.load_bank()
    except Exception:
        return 0
    terms_df = load_terms()
    terms_df["related_qids"] = terms_df["related_qids"].astype(str).replace("nan", "")
    updated = 0
    for i, row in terms_df.iterrows():
        abbr = str(row["abbr"])
        exp = str(row["expansion"])
        pattern = re.compile(re.escape(abbr) + r"\b|" + re.escape(exp), re.I)
        hits = bank[bank["question"].astype(str).str.contains(pattern, na=False)]["qid"].tolist()
        if not hits:
            hits = bank[
                bank["question"].astype(str).str.contains(re.escape(abbr), case=False, na=False)
            ]["qid"].head(5).tolist()
        qids = ",".join(str(q) for q in hits[:8])
        if qids != str(row.get("related_qids") or ""):
            terms_df.at[i, "related_qids"] = qids
            updated += 1
    storage.write_sheet(config.DOMAIN_TREE_XLSX, "terms", terms_df)
    return updated


def daily_term() -> dict | None:
    """Term-of-the-day (deterministic by date)."""
    terms = load_terms()
    if terms.empty:
        return None
    day = datetime.now().toordinal()
    row = terms.iloc[day % len(terms)]
    return row.to_dict()


def player_key(nick: str = "", soeid: str = "") -> str:
    key = (soeid or nick or "guest").strip().lower()
    return re.sub(r"\s+", "_", key)


# ---------------- Learning progress ----------------

def _progress_df() -> pd.DataFrame:
    ensure_progress_files()
    return storage.read_sheet(config.LEARNING_PROGRESS_XLSX, "progress")


def _save_progress(df: pd.DataFrame) -> None:
    storage.write_sheet(config.LEARNING_PROGRESS_XLSX, "progress", df)


def mark_viewed(pk: str, term_id: str) -> None:
    _upsert_progress(pk, term_id, "viewed", "learn_panel")


def mark_mastered(pk: str, term_id: str, source: str = "learn_panel") -> None:
    _upsert_progress(pk, term_id, "mastered", source)
    _check_achievements(pk)


def mark_needs_review(pk: str, term_id: str) -> None:
    df = _progress_df()
    existing = df[(df["player_key"] == pk) & (df["term_id"] == term_id)]
    if not existing.empty and existing.iloc[0]["status"] == "mastered":
        return
    _upsert_progress(pk, term_id, "needs_review", "quiz_wrong")


def _upsert_progress(pk: str, term_id: str, status: str, source: str) -> None:
    if not pk or not term_id:
        return
    df = _progress_df()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mask = (df["player_key"] == pk) & (df["term_id"] == term_id)
    if mask.any():
        idx = df[mask].index[0]
        old = str(df.at[idx, "status"])
        if _STATUS_RANK.get(status, 0) >= _STATUS_RANK.get(old, 0):
            df.at[idx, "status"] = status
            df.at[idx, "source"] = source
            df.at[idx, "updated_at"] = now
    else:
        df = pd.concat([df, pd.DataFrame([{
            "player_key": pk, "term_id": term_id, "status": status,
            "source": source, "updated_at": now,
        }])], ignore_index=True)
    _save_progress(df)


def progress_for_player(pk: str) -> dict[str, str]:
    df = _progress_df()
    sub = df[df["player_key"] == pk]
    return {str(r["term_id"]): str(r["status"]) for _, r in sub.iterrows()}


def progress_summary(pk: str) -> dict:
    prog = progress_for_player(pk)
    terms = load_terms()
    nodes = load_nodes()
    term_to_cat: dict[str, str] = {}
    for _, t in terms.iterrows():
        n = nodes[nodes["node_id"] == t["node_id"]]
        term_to_cat[str(t["term_id"])] = str(n.iloc[0]["category"]) if not n.empty else ""

    total = len(terms)
    viewed = sum(1 for s in prog.values() if s in ("viewed", "mastered", "needs_review"))
    mastered = sum(1 for s in prog.values() if s == "mastered")
    by_domain: dict[str, dict] = {}
    for cat, (emoji, label) in _DOMAIN_META.items():
        term_ids = [tid for tid, c in term_to_cat.items() if c == cat]
        dm = sum(1 for tid in term_ids if prog.get(tid) == "mastered")
        by_domain[label] = {
            "mastered": dm, "total": len(term_ids), "emoji": emoji,
            "category": cat, "node_id": _slug(label),
        }
    return {"viewed": viewed, "mastered": mastered, "total": total, "by_domain": by_domain}


def next_unviewed_term(pk: str, category: str = "") -> dict | None:
    prog = progress_for_player(pk)
    terms = terms_for_category(category) if category else load_terms().to_dict("records")
    for t in terms:
        if t["term_id"] not in prog:
            return t
    return None


def terms_from_qids(qids: list[str]) -> list[str]:
    """Map question bank qids to term_ids."""
    if not qids:
        return []
    terms = load_terms()
    found: list[str] = []
    for _, row in terms.iterrows():
        related = str(row.get("related_qids") or "").split(",")
        if any(q.strip() in qids for q in related if q.strip()):
            found.append(str(row["term_id"]))
    return found


# ---------------- Achievements ----------------

def _achievements_df() -> pd.DataFrame:
    ensure_progress_files()
    return storage.read_sheet(config.LEARNING_PROGRESS_XLSX, "achievements")


def player_achievements(pk: str) -> list[dict]:
    df = _achievements_df()
    sub = df[df["player_key"] == pk]
    out = []
    for _, r in sub.iterrows():
        aid = str(r["achievement_id"])
        meta = _ACHIEVEMENTS.get(aid, (aid, "", ""))
        out.append({"id": aid, "title": meta[0], "desc": meta[1], "earned_at": r["earned_at"]})
    return out


def _award(pk: str, achievement_id: str) -> None:
    df = _achievements_df()
    if not df[(df["player_key"] == pk) & (df["achievement_id"] == achievement_id)].empty:
        return
    storage.append_rows(config.LEARNING_PROGRESS_XLSX, "achievements", [{
        "player_key": pk,
        "achievement_id": achievement_id,
        "earned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])


def _check_achievements(pk: str) -> None:
    summary = progress_summary(pk)
    prog = progress_for_player(pk)
    if summary["viewed"] >= 25:
        _award(pk, "domain_explorer")
    for topic_key in ("compliance", "payments"):
        meta = _OPS_TOPIC_META[topic_key]
        topic_terms = config.OPS_TOPIC_TERMS[topic_key]
        if all(prog.get(t) == "mastered" for t in topic_terms):
            _award(pk, "kyc_champion" if topic_key == "compliance" else "payments_pro")
    kpi_terms = [a for a, _, _, c in question_bank.TERMS if c == question_bank.CAT_KPI]
    kpi_mastered = sum(1 for t in kpi_terms if prog.get(t) == "mastered")
    if kpi_mastered >= 10:
        _award(pk, "kpi_wizard")


def check_game_achievements(pk: str, game_stats: dict) -> None:
    """Post-game achievement checks (speed demon, team teacher)."""
    if game_stats.get("kpi_correct_fast", 0) >= 5:
        _award(pk, "speed_demon")
    if game_stats.get("votes_received", 0) >= 10:
        _award(pk, "team_teacher")


def team_challenge_terms() -> list[str]:
    """Daily team challenge: 3 terms from a rotating topic."""
    topics = list(config.OPS_TOPIC_TERMS.keys())
    day = datetime.now().toordinal()
    topic = topics[day % len(topics)]
    terms = config.OPS_TOPIC_TERMS[topic][:3]
    return terms


def track_question_outcome(nick: str, question_text: str, correct: bool | None) -> None:
    """Update learning progress from a quiz answer."""
    pk = player_key(nick)
    if not pk or correct is None:
        return
    try:
        bank = question_bank.load_bank()
        hits = bank[bank["question"].astype(str) == str(question_text)]["qid"].tolist()
    except Exception:
        hits = []
    term_ids = terms_from_qids(hits)
    if not term_ids:
        q_lower = question_text.lower()
        for _, row in load_terms().iterrows():
            if str(row["abbr"]).lower() in q_lower or str(row["expansion"]).lower()[:20] in q_lower:
                term_ids.append(str(row["term_id"]))
    for tid in set(term_ids):
        if correct:
            mark_mastered(pk, tid, "quiz_correct")
        else:
            mark_needs_review(pk, tid)


def game_learning_stats(g: dict, nick: str) -> dict:
    """Stats for post-game achievement checks."""
    me = g["players"].get(nick, {})
    kpi_correct_fast = 0
    votes = 0
    for a in me.get("answers", []):
        if a.get("votes"):
            votes += int(a["votes"])
        if a.get("correct") and a.get("time_taken", 99) < 5:
            kpi_correct_fast += 1
    return {"kpi_correct_fast": kpi_correct_fast, "votes_received": votes}


def learning_analytics() -> dict:
    """Admin KPIs for domain learning."""
    prog = _progress_df()
    terms = load_terms()
    if prog.empty:
        return {"active_learners": 0, "total_mastered": 0, "top_missed": [], "by_domain": {}}
    active = int(prog["player_key"].nunique())
    mastered = int((prog["status"] == "mastered").sum())
    missed = prog[prog["status"] == "needs_review"]["term_id"].value_counts().head(5)
    top_missed = [{"term_id": t, "count": int(c)} for t, c in missed.items()]
    summary_by_cat: dict[str, int] = {}
    term_to_cat = {}
    nodes = load_nodes()
    for _, t in terms.iterrows():
        n = nodes[nodes["node_id"] == t["node_id"]]
        term_to_cat[str(t["term_id"])] = str(n.iloc[0]["category"]) if not n.empty else ""
    for _, r in prog[prog["status"] == "mastered"].iterrows():
        cat = term_to_cat.get(str(r["term_id"]), "Other")
        summary_by_cat[cat] = summary_by_cat.get(cat, 0) + 1
    return {
        "active_learners": active,
        "total_mastered": mastered,
        "top_missed": top_missed,
        "by_domain": summary_by_cat,
    }


def build_quiz_with_mode(title: str, emoji: str, categories: list[str], difficulties: list[str],
                         n_questions: int, mode: str, created_by: str,
                         player_key_for_mastery: str = "") -> str:
    """Extended quiz builder supporting gamified modes."""
    mode_cfg = config.QUIZ_MODE_PRESETS.get(mode, config.QUIZ_MODE_PRESETS["standard"])
    bank = question_bank.load_bank()
    subj_count = int(mode_cfg.get("subjective", 2))
    filt = mode_cfg.get("filter")

    if filt == "subjective_only":
        subj = bank[bank["qtype"] == "subjective"]
        if categories:
            subj = subj[subj["category"].isin(categories)]
        picked = subj.sample(n=min(n_questions, len(subj)), random_state=None)
        mcq = picked.iloc[0:0]
        picked_subj = picked
    else:
        mcq = bank[(bank["qtype"] == "mcq") & bank["category"].isin(categories)]
        if difficulties:
            mcq = mcq[mcq["difficulty"].isin(difficulties)]
        if filt == "acronym":
            pattern = r"What does .+ stand for\?"
            mcq = mcq[mcq["question"].str.contains(pattern, case=False, na=False)]
        elif filt == "mastery" and player_key_for_mastery:
            prog = progress_for_player(player_key_for_mastery)
            weak_terms = [t for t, s in prog.items() if s != "mastered"]
            terms_df = load_terms()
            weak_qids: set[str] = set()
            for tid in weak_terms[:30]:
                row = terms_df[terms_df["term_id"] == tid]
                if not row.empty:
                    for q in str(row.iloc[0]["related_qids"]).split(","):
                        if q.strip():
                            weak_qids.add(q.strip())
            if weak_qids:
                mcq = mcq[mcq["qid"].isin(weak_qids)]
        subj = bank[bank["qtype"] == "subjective"]
        n_mcq = max(0, n_questions - subj_count)
        picked = mcq.sample(n=min(n_mcq, len(mcq)), random_state=None)
        picked_subj = subj.sample(n=min(subj_count, len(subj)), random_state=None)

    from datetime import datetime as dt
    quiz_id = "bank-" + dt.now().strftime("%y%m%d-%H%M%S")
    storage.add_quiz(quiz_id, title, emoji, " + ".join(categories)[:60] or "Mixed",
                     config.DEFAULT_TIMER_SEC, created_by)
    frames = pd.concat([picked, picked_subj]).sample(frac=1) if not picked.empty or not picked_subj.empty else picked
    if frames.empty:
        raise ValueError("No questions matched the selected mode and filters.")
    for _, r in frames.iterrows():
        storage.add_question(
            quiz_id, str(r["question"]),
            [str(r["opt_a"]), str(r["opt_b"]), str(r["opt_c"]), str(r["opt_d"])],
            str(r["correct"]) if r["qtype"] == "mcq" else "",
            int(r["timer_sec"]), int(r["points"]), qtype=str(r["qtype"]),
        )
    return quiz_id

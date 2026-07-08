"""Participant feedback and suggestions."""
import uuid
from datetime import datetime

import pandas as pd

import config
from core import storage

FEEDBACK_CATEGORIES = ["animation", "content", "ux", "operations", "other"]
FEEDBACK_STATUSES = ["new", "reviewed", "planned", "done"]


def submit(player: str, role: str, category: str, page: str, message: str) -> str:
    domain_knowledge_ensure()
    fid = str(uuid.uuid4())[:8]
    storage.append_rows(config.FEEDBACK_XLSX, "feedback", [{
        "feedback_id": fid,
        "player": player,
        "role": role,
        "category": category if category in FEEDBACK_CATEGORIES else "other",
        "page": page,
        "message": message.strip(),
        "status": "new",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])
    return fid


def list_feedback(status: str = "", category: str = "") -> pd.DataFrame:
    domain_knowledge_ensure()
    df = storage.read_sheet(config.FEEDBACK_XLSX, "feedback")
    if df.empty:
        return df
    if status:
        df = df[df["status"] == status]
    if category:
        df = df[df["category"] == category]
    return df.sort_values("created_at", ascending=False)


def update_status(feedback_id: str, status: str) -> None:
    df = storage.read_sheet(config.FEEDBACK_XLSX, "feedback")
    if df.empty:
        return
    mask = df["feedback_id"] == feedback_id
    if mask.any():
        df.loc[mask, "status"] = status if status in FEEDBACK_STATUSES else "reviewed"
        storage.write_sheet(config.FEEDBACK_XLSX, "feedback", df)


def domain_knowledge_ensure() -> None:
    from core import domain_knowledge
    domain_knowledge.ensure_progress_files()

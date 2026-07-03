"""Admin authentication (users.xlsx) + participant identity helpers."""
import hashlib
from datetime import datetime

import config
from core import storage, logger


def _hash(pwd: str) -> str:
    return hashlib.sha256(("quiztok::" + pwd).encode("utf-8")).hexdigest()


def ensure_default_admin() -> None:
    df = storage.read_sheet(config.USERS_XLSX, "admins")
    if df.empty:
        storage.append_rows(config.USERS_XLSX, "admins", [{
            "email": config.DEFAULT_ADMIN_EMAIL,
            "name": config.DEFAULT_ADMIN_NAME,
            "password_hash": _hash(config.DEFAULT_ADMIN_PASSWORD),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }])


def verify_admin(email: str, password: str) -> tuple[bool, str]:
    """Returns (ok, admin display name)."""
    df = storage.read_sheet(config.USERS_XLSX, "admins")
    row = df[df["email"].str.lower() == email.strip().lower()]
    if row.empty or row.iloc[0]["password_hash"] != _hash(password):
        logger.log(email, "admin", "login_failed")
        return False, ""
    logger.log(email, "admin", "login_ok")
    return True, str(row.iloc[0]["name"])


def add_admin(email: str, name: str, password: str, added_by: str) -> bool:
    df = storage.read_sheet(config.USERS_XLSX, "admins")
    if not df[df["email"].str.lower() == email.strip().lower()].empty:
        return False
    storage.append_rows(config.USERS_XLSX, "admins", [{
        "email": email.strip(), "name": name.strip(), "password_hash": _hash(password),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])
    logger.log(added_by, "admin", "admin_added", email)
    return True

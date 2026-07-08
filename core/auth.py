"""Admin authentication (users.xlsx) + participant identity helpers."""
import hashlib
from datetime import datetime

import config
from core import storage, logger


def _hash(pwd: str) -> str:
    return hashlib.sha256(("quiztok::" + pwd).encode("utf-8")).hexdigest()


def ensure_default_admin() -> None:
    df = storage.read_sheet(config.USERS_XLSX, "admins")
    expected_hash = _hash(config.DEFAULT_ADMIN_PASSWORD)
    existing = df[df["email"].str.lower() == config.DEFAULT_ADMIN_EMAIL.lower()]
    if existing.empty:
        storage.append_rows(config.USERS_XLSX, "admins", [{
            "email": config.DEFAULT_ADMIN_EMAIL,
            "name": config.DEFAULT_ADMIN_NAME,
            "password_hash": expected_hash,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }])
    elif str(existing.iloc[0]["password_hash"]) != expected_hash:
        # Update password hash to match current config
        df.loc[df["email"].str.lower() == config.DEFAULT_ADMIN_EMAIL.lower(), "password_hash"] = expected_hash
        storage.write_sheet(config.USERS_XLSX, "admins", df)


def ensure_default_host() -> None:
    df = storage.read_sheet(config.USERS_XLSX, "admins")
    expected_hash = _hash(config.DEFAULT_HOST_PASSWORD)
    existing = df[df["email"].str.lower() == config.DEFAULT_HOST_EMAIL.lower()]
    if existing.empty:
        storage.append_rows(config.USERS_XLSX, "admins", [{
            "email": config.DEFAULT_HOST_EMAIL,
            "name": config.DEFAULT_HOST_NAME,
            "password_hash": expected_hash,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }])
    elif str(existing.iloc[0]["password_hash"]) != expected_hash:
        df.loc[df["email"].str.lower() == config.DEFAULT_HOST_EMAIL.lower(), "password_hash"] = expected_hash
        storage.write_sheet(config.USERS_XLSX, "admins", df)


def verify_host(email: str, password: str) -> tuple[bool, str]:
    """Returns (ok, host display name). Only host@abc.com is a valid host login."""
    if email.strip().lower() != config.DEFAULT_HOST_EMAIL.lower():
        logger.log(email, "host", "login_failed")
        return False, ""
    ensure_default_host()
    df = storage.read_sheet(config.USERS_XLSX, "admins")
    row = df[df["email"].str.lower() == config.DEFAULT_HOST_EMAIL.lower()]
    if row.empty or str(row.iloc[0]["password_hash"]) != _hash(password):
        logger.log(email, "host", "login_failed")
        return False, ""
    logger.log(email, "host", "login_ok")
    return True, str(row.iloc[0]["name"])


def verify_admin(email: str, password: str) -> tuple[bool, str]:
    """Returns (ok, admin display name)."""
    ensure_default_admin()
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

"""Activity logging — every meaningful action is appended to data/activity_log.xlsx."""
from datetime import datetime

import config
from core import storage


def log(actor: str, role: str, action: str, details: str = "") -> None:
    try:
        storage.append_rows(config.ACTIVITY_XLSX, "log", [{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "actor": actor,
            "role": role,
            "action": action,
            "details": details,
        }])
    except PermissionError:
        # file open in Excel — never crash the game because of logging
        pass


def tail(n: int = 50):
    df = storage.read_sheet(config.ACTIVITY_XLSX, "log")
    return df.tail(n).iloc[::-1]

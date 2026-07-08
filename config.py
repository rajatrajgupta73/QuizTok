"""QuizTok configuration — paths, branding, game constants (all local, no internet needed)."""
from pathlib import Path

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

USERS_XLSX = DATA_DIR / "users.xlsx"
QUIZZES_XLSX = DATA_DIR / "quizzes.xlsx"
RESULTS_XLSX = DATA_DIR / "results.xlsx"
ACTIVITY_XLSX = DATA_DIR / "activity_log.xlsx"
QUESTION_BANK_XLSX = DATA_DIR / "question_bank.xlsx"
TEAMS_XLSX = DATA_DIR / "teams.xlsx"
DOMAIN_TREE_XLSX = DATA_DIR / "domain_tree.xlsx"
LEARNING_PROGRESS_XLSX = DATA_DIR / "learning_progress.xlsx"
FEEDBACK_XLSX = DATA_DIR / "feedback.xlsx"
LIVE_GAME_JSON = DATA_DIR / "live_game.json"
MEDIA_DIR = DATA_DIR / "media"

# Uploaded question media (image / audio / video) — local files only
MEDIA_MAX_BYTES = 25 * 1024 * 1024  # 25 MB
MEDIA_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MEDIA_AUDIO_EXT = {".mp3", ".wav", ".ogg", ".m4a", ".aac"}
MEDIA_VIDEO_EXT = {".mp4", ".webm", ".mov", ".mkv"}

# Domain Academy — topic groups under Banking Operations
OPS_TOPIC_TERMS = {
    "compliance": ["KYC", "AML", "CDD", "EDD", "PEP", "STR", "CTR", "FATCA", "LEI"],
    "payments": ["RTGS", "NEFT", "IMPS", "UPI", "NACH", "SWIFT", "IBAN", "ACH", "MICR", "IFSC", "DD"],
    "accounts": ["CASA", "EMV", "CVV", "OTP", "2FA", "POS", "NPA", "GL", "CBK", "RECON", "MKR-CHKR", "EOD", "SOP", "RCA", "CTS"],
}

# Gamified quiz build presets (admin Question Bank tab)
QUIZ_MODE_PRESETS = {
    "standard": {"label": "Standard Mix", "subjective": 2, "filter": None},
    "acronym_blitz": {"label": "Acronym Blitz", "subjective": 0, "filter": "acronym"},
    "scenario_showdown": {"label": "Scenario Showdown", "subjective": 10, "filter": "subjective_only"},
    "mastery_match": {"label": "Mastery Match", "subjective": 1, "filter": "mastery"},
}

# ---------- App ----------
APP_NAME = "QuizTok"
APP_TAGLINE = "Play. Learn. QuizTok it!"
DEFAULT_ADMIN_EMAIL = "admin@abc.com"
DEFAULT_ADMIN_PASSWORD = "admin123"          # change after first login
DEFAULT_ADMIN_NAME = "QuizTok Admin"

DEFAULT_HOST_EMAIL = "host@abc.com"
DEFAULT_HOST_PASSWORD = "host123"
DEFAULT_HOST_NAME = "QuizTok Host"

# ---------- ABC Company branding ----------
ABC_NAVY = "#003b70"
ABC_BLUE = "#0088ce"
ABC_SKY = "#4db4ff"
ABC_RED = "#e21836"
GOLD = "#ffc233"
TEAL = "#00c9a7"

# ---------- Game rules ----------
BASE_POINTS = 1000            # per MCQ question, before bonuses
STREAK_BONUS_PER_LEVEL = 50   # extra points per current streak level
STREAK_BONUS_CAP = 5          # streak levels that earn bonus
DEFAULT_TIMER_SEC = 20
SUBJECTIVE_TIMER_SEC = 45     # time to type a subjective answer
VOTING_TIMER_SEC = 30         # time to vote on subjective answers
VOTE_POINTS = 300             # points per vote received
VOTE_WINNER_BONUS = 500       # extra for the most-voted answer(s)
PIN_LENGTH = 6

QUESTION_BANK_SIZE = 2000     # rows generated into question_bank.xlsx

AVATARS = ["🦊", "🐼", "🦁", "🐸", "🦄", "🐙", "🐯", "🦉", "🐨", "🐵", "🦖", "🐳"]

TEAM_SUGGESTIONS = ["Blue Sparks", "Red Arcs", "Gold Rush", "Teal Titans", "Ops Avengers", "CX Crusaders"]
BOT_TEAMS = ["Blue Sparks", "Red Arcs"]

# canned bot replies for subjective rounds
BOT_SUBJECTIVE_ANSWERS = [
    "I would first acknowledge the customer's frustration, then verify the account and resolve the root cause before offering a goodwill gesture.",
    "Listen fully, apologise once sincerely, fix the issue, and follow up within 24 hours so the customer never has to call back.",
    "Use the IVR data and CRM history so the customer never repeats themselves, then solve it on first contact.",
    "I'd pull the agent-assist summary, confirm the intent, and give one clear next step instead of transferring the call.",
    "Empathy first, accuracy second, speed third — in that order, every single time.",
    "Automate the boring 80% with self-service and save the human touch for the moments that actually need it.",
    "Root-cause it: one fixed process beats a hundred apologies.",
    "Turn the complaint into feedback — log it, fix it, and tell the customer what changed because of them.",
]

# Bots used when the host enables "demo bots" (name, avatar, skill = chance of correct answer)
BOT_ROSTER = [
    ("Priya P.", "🐼", 0.82),
    ("Arjun_Roars", "🦁", 0.68),
    ("KermitTheDev", "🐸", 0.72),
    ("Sneha ✨", "🦄", 0.88),
    ("Octo-Ops", "🐙", 0.60),
    ("NightOwl_Sam", "🦉", 0.55),
    ("TigerTeam_Vik", "🐯", 0.50),
    ("ChillKarthik", "🐨", 0.45),
]

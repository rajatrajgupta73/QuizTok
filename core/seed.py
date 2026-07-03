"""First-run setup: creates data folder, default admin and sample quizzes."""
import config
from core import storage, auth

SAMPLE_QUIZZES = [
    {
        "quiz_id": "citi-trivia", "title": "Citi Trivia & Team Fun", "emoji": "🎬",
        "category": "Mixed", "timer_sec": 20,
        "questions": [
            ("In which year was Citi (then City Bank of New York) founded?",
             ["1789", "1812", "1865", "1901"], "B"),
            ("What does the red arc in the Citi logo represent?",
             ["A rainbow", "An umbrella heritage", "A smile", "A bridge"], "B"),
            ("Which of these is a Citi value?",
             ["Move fast, break things", "We take ownership", "Always be closing", "Fail forward"], "B"),
            ("Roughly how many countries does Citi operate in?",
             ["about 60", "about 95", "about 160", "about 200"], "C"),
            ("Which city hosts Citi's global headquarters?",
             ["London", "Singapore", "New York", "Mumbai"], "C"),
            ("The 'thank you' rewards program by Citi is called…",
             ["ThankYou®", "GraciasPoints", "CitiCoins", "MerciMiles"], "A"),
            ("Which emoji best describes Friday team calls? 😄",
             ["😴", "🎉", "📊", "All of them, in that order"], "D"),
            ("Speed bonus in QuizTok is earned by…",
             ["Answering fast", "Answering last", "Using hints", "Bribing the host"], "A"),
        ],
    },
    {
        "quiz_id": "citi-history", "title": "Citi History & Values Sprint", "emoji": "💼",
        "category": "Trivia", "timer_sec": 15,
        "questions": [
            ("Citi's ATMs were an industry first in which decade?",
             ["1950s", "1970s", "1990s", "2000s"], "B"),
            ("Which Citi value is about doing what's right?",
             ["Leadership", "Responsible Finance", "Innovation", "Speed"], "B"),
            ("Citi's mascot in QuizTok is a…",
             ["Red question mark", "Blue owl", "Gold trophy", "Green frog"], "A"),
            ("The best team quiz strategy is…",
             ["Panic", "Guess everything", "Read the question 😉", "Blame the Wi-Fi"], "C"),
            ("A 🔥 streak in QuizTok resets when you…",
             ["Answer wrong", "Answer fast", "Win a round", "High-five"], "A"),
            ("Which one is NOT a QuizTok award?",
             ["Speed Demon", "Longest Streak", "Sharp Shooter", "Best Excel Formula"], "D"),
        ],
    },
    {
        "quiz_id": "emoji-movies", "title": "Emoji Movie Puzzles", "emoji": "🧩",
        "category": "Picture Round", "timer_sec": 25,
        "questions": [
            ("🦁👑 = which movie?",
             ["Madagascar", "The Lion King", "Jungle Book", "Zootopia"], "B"),
            ("🕷️🧑 = which hero?",
             ["Batman", "Ant-Man", "Spider-Man", "Iron Man"], "C"),
            ("🚢🧊💔 = which movie?",
             ["Titanic", "Frozen", "Life of Pi", "Poseidon"], "A"),
            ("👽📞🏠 = which classic?",
             ["Alien", "E.T.", "Arrival", "Men in Black"], "B"),
            ("🧙‍♂️💍🌋 = which saga?",
             ["Harry Potter", "Narnia", "Lord of the Rings", "Eragon"], "C"),
        ],
    },
]


def run() -> None:
    """Idempotent — safe to call on every app start."""
    storage.ensure_data_dir()
    auth.ensure_default_admin()

    existing = storage.get_quizzes()
    for q in SAMPLE_QUIZZES:
        if not existing.empty and (existing["quiz_id"] == q["quiz_id"]).any():
            continue
        storage.add_quiz(q["quiz_id"], q["title"], q["emoji"], q["category"], q["timer_sec"], "seed")
        for text, options, correct in q["questions"]:
            storage.add_question(q["quiz_id"], text, options, correct, q["timer_sec"], config.BASE_POINTS)

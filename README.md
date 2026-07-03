# QuizTok 🎮 — Citi Team Fun Quiz Platform

A fully-offline, animated, gamified live-quiz platform built with **Python + Streamlit**.
Citi branding (Citi Blue `#003b70` · Bright Blue `#0088ce` · Red Arc `#e21836`), Kahoot-style
energy, a **2,000-question banking-domain library**, subjective **voting rounds**, teams,
bots, streaks, podiums — and every byte of data saved to **Excel**.

## 🚀 Run it (VS Code / any machine)

```bash
cd QuizTok
pip install -r requirements.txt   # streamlit, pandas, openpyxl — one-time
streamlit run app.py
```

Open http://localhost:8501. No internet needed at runtime — fonts, styling, data are all local.

**Default admin login:** `admin@citi.com` / `citi123`

## 🕹️ How to play

1. **Admin** logs in → *Quiz Library* → **Host 🎛️** a quiz → a 6-digit PIN appears.
2. **Participants** open the app (new tab / another machine on LAN), enter **PIN + nickname**,
   optionally pick a **team**, choose an avatar in the lobby.
3. Admin hits **🚀 LAUNCH** — MCQ rounds have speed bonuses + 🔥 streaks;
   **subjective rounds** collect typed answers, then everyone **votes 🗳️** for the best one
   (300 pts/vote + 500 winner bonus).
4. Podium, team battle result and Funky Awards at the end — all saved to Excel.

No second player around? Use **🤖 Play Solo Demo vs Bots** on the login page.

## 📁 Folder structure

```
QuizTok/
├── app.py                  # entry point + router
├── config.py               # paths, branding, game rules
├── requirements.txt
├── .streamlit/config.toml  # dark Citi theme
├── core/                   # business logic (no UI)
│   ├── storage.py          #   Excel read/write layer
│   ├── auth.py             #   admin login (SHA-256), default admin
│   ├── logger.py           #   activity logging → activity_log.xlsx
│   ├── game.py             #   live game engine, scoring, voting, teams, bots
│   ├── question_bank.py    #   generates the 2,000-question bank + quiz builder
│   └── seed.py             #   first-run sample quizzes
├── ui/                     # presentation (Streamlit)
│   ├── theme.py            #   Citi-branded CSS + animations (offline)
│   ├── components.py       #   logo, podium, timer ring, confetti, chips…
│   ├── login_page.py       #   participant join + admin sign-in
│   ├── lobby_page.py       #   avatars + live roster
│   ├── quiz_page.py        #   MCQ / subjective / voting / reveal
│   ├── results_page.py     #   champion, team battle, awards
│   ├── admin_page.py       #   dashboard, library, bank, builder, reports
│   └── host_page.py        #   live host controls
├── data/                   # ALL persisted data (auto-created, open in Excel)
│   ├── question_bank.xlsx  #   2,000 banking-domain questions
│   ├── quizzes.xlsx        #   quizzes + their questions
│   ├── users.xlsx          #   admin accounts
│   ├── results.xlsx        #   games · scores · every answer with votes/timings
│   ├── activity_log.xlsx   #   every login/join/answer/vote/host action
│   └── live_game.json      #   the single live game (shared across tabs)
└── prototype/              # original HTML/CSS design mockups
```

## 🏦 Question bank (2,000 questions)

Generated locally into `data/question_bank.xlsx` on first run, covering:

| Category | Content |
|---|---|
| Banking Operations | KYC/AML, payments (RTGS/NEFT/UPI/SWIFT), clearing, controls, chargebacks |
| KPI & Metrics | AHT, FCR, NPS, CSAT, SLA, occupancy, shrinkage **+ calculation questions** |
| Customer Service | CRM, VOC, empathy, escalation, closed-loop feedback, scenarios |
| Self-Service & Digital | chatbots, containment/deflection, e-KYC, omnichannel |
| IVR | DTMF/ASR/TTS/NLU, routing, containment, courtesy callback, VUI |
| Agent Assist & LLM | RAG, prompts, hallucination, guardrails, auto-QA, summarisation |
| Subjective (Vote Rounds) | open-ended prompts scored by participant votes |

Admins can filter the bank (category / difficulty / search) and **create a quiz from the
selection** in one click — including how many subjective voting rounds to mix in.
The Excel file is editable: add your own rows and they're instantly usable.

## 🗳️ Voting rounds

Subjective questions have no "correct" option — everyone types an answer, then the room
votes (you can't vote for yourself). Votes → points → they count toward the **individual
podium and the team battle**, and the most-voted player earns the 🗳️ *Crowd Favourite* award.

## 📊 Excel logging

Every action is appended to `data/activity_log.xlsx` (timestamp, actor, role, action, details):
logins, joins, answers, votes, hosting actions. Full game results land in `data/results.xlsx`
across three sheets — `games`, `scores` (with teams and votes) and `answers` (every pick,
vote count, timing and points).

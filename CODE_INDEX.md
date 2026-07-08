# QuizTok Code Index
**Complete Reference Guide for Code Navigation & Editing**

This index maps every file, function, and key concept in the QuizTok codebase. Use this when making queries or edits to quickly find what you need.

---

## 📁 PROJECT STRUCTURE

```
QuizTok/
├── app.py                    # Entry point & page router
├── config.py                 # All constants, paths, colors, timers
├── requirements.txt          # Python dependencies
├── CLAUDE.md                # Project context for AI assistant
├── README.md                # User documentation
├── CODE_INDEX.md            # This file — complete code reference
├── HOW_TO_USE_INDEX.md      # Guide for using this index
│
├── core/                    # Business logic layer
│   ├── __init__.py
│   ├── game.py              # Live game engine (state machine, scoring, chat)
│   ├── storage.py           # Excel read/write operations
│   ├── auth.py              # Admin authentication
│   ├── question_bank.py     # 2000-question generator
│   ├── seed.py              # First-run database setup
│   └── logger.py            # Activity logging
│
├── ui/                      # Presentation layer (Streamlit)
│   ├── __init__.py
│   ├── theme.py             # All CSS & visual effects (JS: glow, neon cursor, floaters)
│   ├── components.py        # Reusable UI elements (chat, countdown, sound effects)
│   ├── login_page.py        # Login/join page
│   ├── transition_page.py   # Neon loading transition after login (role-based)
│   ├── lobby_page.py        # Pre-game waiting room (with team chat)
│   ├── quiz_page.py         # Player question view (3-column: stats | stage | chat)
│   ├── results_page.py      # Post-game leaderboard & awards
│   ├── admin_page.py        # Quiz builder, team management & admin panel
│   └── host_page.py         # Host control dashboard (Command Center, force controls)
│
├── data/                    # "Database" (Excel files)
│   ├── users.xlsx           # Admin/host accounts
│   ├── quizzes.xlsx         # Quiz library + questions
│   ├── results.xlsx         # Game history
│   ├── question_bank.xlsx   # 2000 pre-generated questions
│   ├── teams.xlsx           # Team registry
│   ├── activity_log.xlsx    # Audit trail
│   └── live_game.json       # Active game state (shared, includes chat)
│
├── prototype/               # Design source of truth (HTML)
│   ├── index.html           # Login page design
│   ├── lobby.html           # Lobby design
│   ├── quiz.html            # Question screen design
│   ├── leaderboard.html     # Mid-game rankings
│   ├── results.html         # Final results design
│   ├── admin.html           # Admin panel design
│   ├── host.html            # Host control design
│   ├── ink.js               # Ink canvas effect
│   └── css/styles.css       # Prototype CSS
│
├── frontend/                # Frontend assets (node_modules only — no app code)
│
└── assets/                  # Static resources (if any)
```

---

## 🎯 QUICK LOOKUP TABLE

| **To edit...**                     | **File to modify**                |
|------------------------------------|-----------------------------------|
| Colors, fonts, branding            | `ui/theme.py` + `config.py`       |
| Game rules (points, timers)        | `config.py`                       |
| Login page UI                      | `ui/login_page.py`                |
| Transition screen                  | `ui/transition_page.py`           |
| Lobby waiting screen               | `ui/lobby_page.py`                |
| Quiz question screen               | `ui/quiz_page.py`                 |
| Results/leaderboard page           | `ui/results_page.py`              |
| Admin dashboard                    | `ui/admin_page.py`                |
| Host control panel                 | `ui/host_page.py`                 |
| Game state machine & scoring       | `core/game.py`                    |
| Database schema & Excel ops        | `core/storage.py`                 |
| Admin login                        | `core/auth.py`                    |
| Reusable UI components             | `ui/components.py`                |
| CSS animations & styling           | `ui/theme.py`                     |
| Sound effects & audio              | `ui/components.py` (sound_effects, countdown_popup) |
| Team chat                          | `core/game.py` (post_chat) + `ui/components.py` (team_chat_rail) |
| Question generation                | `core/question_bank.py`           |
| App initialization                 | `app.py`                          |
| Design reference                   | `prototype/` HTML files           |

---

## 📋 FILE DETAILS

### **app.py** — Entry Point
**Purpose:** Bootstrap the app and route pages based on session state

**Key Functions:**
- `_bootstrap()` — One-time setup: seeds data, creates 2000 questions

**Pages Map:**
```python
"login"      → login_page.render()
"transition" → transition_page.render()    # neon loading screen after login
"lobby"      → lobby_page.render()
"quiz"       → quiz_page.render()
"results"    → results_page.render()
"admin"      → admin_page.render()
"host"       → host_page.render()
```

**Page-Switch Settle Logic:**
- `st.session_state["_last_page"]` tracks the previous page
- `st.session_state["_settle"]` is set `True` on page change
- `ui.components.autorefresh()` detects `_settle` and lets the first run complete (via a hidden `qt_settle` button clicked by JS) so Streamlit prunes stale DOM elements from the previous page
- Admin/host pages require `role` in `("admin", "host")`; transition page requires an active `role`

**Dependencies:** All UI pages, core.seed, core.question_bank, ui.theme

---

### **config.py** — Configuration Constants
**Purpose:** Single source of truth for all constants (no secrets, everything local)

**Key Sections:**
- **Paths:** `DATA_DIR`, `USERS_XLSX`, `QUIZZES_XLSX`, `RESULTS_XLSX`, `ACTIVITY_XLSX`, `QUESTION_BANK_XLSX`, `TEAMS_XLSX`, `LIVE_GAME_JSON`
- **Branding:** `APP_NAME`, `APP_TAGLINE`, colors (`ABC_NAVY`, `ABC_BLUE`, `ABC_SKY`, `ABC_RED`, `GOLD`, `TEAL`)
- **Default Credentials:**
  - Admin: `admin@abc.com` / `admin123`
  - Host: `host@abc.com` / `host123`
- **Game Rules:**
  - `BASE_POINTS = 1000` (per MCQ question)
  - `STREAK_BONUS_PER_LEVEL = 50` (bonus per streak level)
  - `STREAK_BONUS_CAP = 5` (max streak levels earning bonus)
  - `DEFAULT_TIMER_SEC = 20`
  - `SUBJECTIVE_TIMER_SEC = 45` (time to type answer)
  - `VOTING_TIMER_SEC = 30` (time to vote)
  - `VOTE_POINTS = 300` (per vote received)
  - `VOTE_WINNER_BONUS = 500` (extra for most-voted answer)
  - `PIN_LENGTH = 6`
- **Questions:** `QUESTION_BANK_SIZE = 2000`
- **Avatars:** `AVATARS` list (12 emoji avatars)
- **Teams:** `TEAM_SUGGESTIONS`, `BOT_TEAMS`
- **Bot Config:** `BOT_ROSTER` (name, avatar, skill), `BOT_SUBJECTIVE_ANSWERS` (8 canned replies)

**When to Edit:**
- Changing point values → `BASE_POINTS`, `STREAK_BONUS_PER_LEVEL`, `VOTE_POINTS`, `VOTE_WINNER_BONUS`
- Adjusting timers → `DEFAULT_TIMER_SEC`, `SUBJECTIVE_TIMER_SEC`, `VOTING_TIMER_SEC`
- Brand colors → `ABC_*` constants
- Bot behavior → `BOT_ROSTER`, `BOT_SUBJECTIVE_ANSWERS`
- Add new data files → Add path constant here

---

### **core/game.py** — Game Engine
**Purpose:** All live game logic — state machine, scoring, bot AI, team chat, voting, leaderboards

**Game State Machine:**
```
LOBBY → QUESTION → (VOTING for subjective) → REVEAL → QUESTION → ... → FINISHED
```

**Game State (live_game.json):**
```python
{
  "pin": str, "status": str, "quiz_id": str, "host": str,
  "players": {nick: {avatar, is_bot, skill, team, soeid, streak, score, answers[], votes_received}},
  "questions": [...], "q_index": int, "timer_sec": int,
  "phase_start_ts": float, "reveal_started": float,
  "bot_plan": [...],  # bot answer delays & correctness
  "chat": {team: [messages]},  # team-scoped chat, wiped on finish()
  "awards": {...}, "finished_by": str
}
```

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `load()` / `save(g)` | Read/write live_game.json (atomic writes) |
| `clear()` | Delete live_game.json |
| `create_game(quiz_id, host, with_bots, bot_count)` | Initialize new game with PIN |
| `join(pin, nick, avatar, team, soeid)` | Player joins lobby → `(ok, msg)` |
| `set_avatar(nick, avatar)` | Change player avatar in lobby |
| `start(actor)` | Host starts game (LOBBY → QUESTION) |
| `_begin_question(g, idx)` | Set up next question + timer |
| `current_q(g)` / `time_left(g)` | Get current question / remaining seconds |
| `has_answered(g, nick)` | Check if player answered current question |
| `_score_mcq(g, nick, choice, tl)` | Calculate MCQ score (base + time + streak) |
| `submit_answer(nick, choice)` | Record MCQ answer, return result dict |
| `submit_text(nick, text)` | Record subjective text answer |
| `current_answers(g)` | List who has answered (for host view) |
| `submit_vote(voter, target)` | Vote for best subjective answer |
| `has_voted(g, nick)` | Check if player already voted |
| `post_chat(nick, text)` | Post message to player's team chat (keeps last 50) |
| `_begin_voting(g)` / `_finish_voting(g)` | Start/end subjective voting phase |
| `tick(g)` | Auto-advance state: bot answers, phase timeouts |
| `_materialize_bot_answers(g)` | Bots submit answers at planned delays |
| `_reveal_mcq(g)` | Auto-reveal MCQ answer on timeout |
| `force_reveal(actor)` | Host forces end of answer phase |
| `force_end_voting(actor)` | Host forces end of voting phase |
| `next_question(actor)` | Advance to next question or finish |
| `leaderboard(g)` | Individual player rankings |
| `team_leaderboard(g)` | Team aggregate rankings |
| `answer_distribution(g)` | Count answers per option (bar chart data) |
| `compute_awards(g)` | Named awards: "⚡ Speed Demon", "🔥 Longest Streak", "🎯 Sharp Shooter", "🗳️ Crowd Favourite" |
| `finish(actor)` | End game, clear chat, compute awards, persist results |
| `_persist_results(g)` | Save game/score/answer rows to results.xlsx |
| `start_solo_demo(nick, avatar, team)` | Create solo game with bots, auto-start |

**Scoring Logic:**
```python
# MCQ:
base_points = 1000
time_bonus = base * (time_left / timer)
streak_bonus = min(streak, STREAK_BONUS_CAP) * STREAK_BONUS_PER_LEVEL
total = base + time_bonus + streak_bonus

# Subjective:
points = votes_received * VOTE_POINTS
if most_votes: points += VOTE_WINNER_BONUS
```

**Bot AI:**
- `skill` = probability of correct answer (0.0–1.0)
- Bot answer plans pre-computed in `g["bot_plan"]` with delays & `will_correct` flags
- Bots submit MCQ answers at staggered intervals via `_materialize_bot_answers()`
- Bots submit canned subjective answers from `config.BOT_SUBJECTIVE_ANSWERS`
- Bots also vote in voting phase

**Team Chat:**
- Messages stored in `g["chat"][team]` as list of `{nick, text, ts}`
- Capped at 50 messages per team
- Wiped on `finish()` and `clear()`

**When to Edit:**
- Change scoring formula → `_score_mcq()`, `compute_awards()`
- Adjust bot behavior → `_materialize_bot_answers()`, `tick()` logic
- Modify state transitions → `_begin_question()`, `next_question()`, `_begin_voting()`
- Add chat features → `post_chat()`

---

### **core/storage.py** — Data Layer
**Purpose:** All Excel read/write operations (users, quizzes, results, teams)

**Schema Map:**
```python
SCHEMAS = {
    users.xlsx / admins:      ["email", "name", "password_hash", "created_at"]
    quizzes.xlsx / quizzes:   ["quiz_id", "title", "emoji", "category", "timer_sec", ...]
    quizzes.xlsx / questions: ["quiz_id", "q_index", "qtype", "question", "opt_a", ...]
    results.xlsx / games:     ["game_id", "quiz_title", "played_at", "winner", ...]
    results.xlsx / scores:    ["game_id", "rank", "player", "score", ...]
    results.xlsx / answers:   ["game_id", "player", "q_index", "picked", ...]
    teams.xlsx / teams:       ["name", "emoji", "color", "created_by", "created_at"]
    activity_log.xlsx / log:  ["timestamp", "actor", "role", "action", "details"]
}
```

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `ensure_data_dir()` | Create data/ directory if missing |
| `read_sheet(path, sheet)` | Load one Excel sheet as DataFrame |
| `write_sheet(path, sheet, df)` | Save DataFrame (preserves other sheets) |
| `append_rows(path, sheet, rows)` | Add rows without rewriting file |
| `get_quizzes()` | Load all quizzes |
| `get_questions(quiz_id)` | Load questions for one quiz |
| `add_quiz(quiz_id, title, emoji, category, timer_sec, created_by)` | Create a new quiz row |
| `add_question(quiz_id, question, options, correct_letter, timer_sec, points, qtype)` | Add question to quiz |
| `question_count(quiz_id)` | Count questions in a quiz |
| `delete_quiz(quiz_id)` | Remove quiz + all its questions |
| `save_game_results(game_row, score_rows, answer_rows)` | Persist completed game |
| `get_kpis()` | Dashboard stats (games played, avg scores, etc.) |
| `get_teams()` | Load registered teams |
| `upsert_team(name, emoji, color, created_by)` | Create or update team |
| `delete_team(name)` | Remove team from registry |
| `get_team_scoreboard()` | Aggregate team scores across all games |

**When to Edit:**
- Add new Excel columns → Update SCHEMAS dict
- New data file → Add path to config.py + schema here
- Change data format → Modify read/write helpers

---

### **core/auth.py** — Authentication
**Purpose:** Admin/host login verification (users.xlsx)

**Key Functions:**
- `verify_admin(email, password)` → `(ok: bool, name: str)`
- `add_admin(email, name, password, added_by)` → `bool`
- `ensure_default_admin()` — Seeds admin@abc.com / admin123 + host@abc.com / host123 on first run

**Security:**
- SHA-256 password hashing with salt prefix
- No API calls, no network, fully local

---

### **core/question_bank.py** — Question Generator
**Purpose:** Create 2000 diverse questions (10 categories, 3 difficulties)

**Categories:**
1. Banking & ABC Company Knowledge
2. Financial Terms
3. Customer Service
4. Compliance & Risk
5. Technology in Banking
6. Team Culture
7. Capital Markets
8. Products & Solutions
9. Professional Skills
10. Fun Trivia

**Difficulty:** Easy (40%), Medium (40%), Hard (20%)

**Key Functions:**
- `ensure_bank()` — Generates question_bank.xlsx if missing
- `build_quiz_from_bank(title, category, count)` — Random sample into new quiz

**When to Edit:**
- Add categories → Modify category generator functions
- Change question count → `config.QUESTION_BANK_SIZE`

---

### **core/seed.py** — First-Run Setup
**Purpose:** Create initial data files (admin/host users, sample quizzes)

**Key Functions:**
- `run()` — Idempotent: seeds only if users.xlsx is missing

---

### **core/logger.py** — Activity Log
**Purpose:** Audit trail of all user actions

**Function:** `log(actor, role, action, details="")`

**Examples:**
```python
log("user@abc.com", "admin", "login_ok")
log("Priya", "participant", "joined_game", pin)
log("host@abc.com", "admin", "quiz_created", quiz_id)
```

Writes to `activity_log.xlsx`

---

### **ui/theme.py** — Visual Design
**Purpose:** All CSS, animations, JS effects

**Key Function:**
- `inject()` — Applies all CSS + injects JavaScript effects

**What's Inside:**
- **CSS Variables:** Colors, glass effects, borders, fonts
- **Animations:** Rise, bounce, pulse, glow, fall (floaters)
- **Kahoot Answer Buttons:** 4-color grid (blue/red/gold/teal) via `.st-key-ans0..3`
- **Login Page Effects:** Glow ring, ink canvas, floating symbols
- **Streamlit Overrides:** Hide menu, sidebar, adjust spacing
- **Hidden settle button:** `.st-key-qt_settle` (used by autorefresh for page-switch cleanup)

**JavaScript Effects (injected via `st.components.v1.html` iframes):**
- `_GLOW_JS` — Cursor glow ring + ink-in-water canvas paint loop
- `_FLOATERS_JS` — Floating symbols + parent-realm DOM janitor (cleans login mascot/glow across reruns)
- `_NEON_CURSOR_JS` — Neon cursor trail effect

**Key CSS Classes:**
```css
.qt-topbar         /* Header with logo & pills */
.qt-card           /* Glass card container */
.qt-pin            /* Big centered PIN display */
.qt-timer          /* Circular countdown */
.qt-hud            /* Quiz progress bar + streak */
.qt-podium         /* 1st/2nd/3rd place display */
.qt-verdict        /* Correct/Wrong feedback */
.qt-tr-*           /* Transition page elements (grid, scan line, ring, particles) */
.st-key-ans0..3    /* Kahoot answer button colors */
.st-key-qt_settle  /* Hidden settle button for page-switch cleanup */
```

**When to Edit:**
- Change colors → CSS `:root` variables + `config.py`
- Add animations → @keyframes blocks
- Modify button styles → `.st-key-*` classes

---

### **ui/components.py** — Reusable UI Elements
**Purpose:** HTML builders for repeated UI patterns

**Key Components:**

| Function | Returns | Purpose |
|----------|---------|---------|
| `citi_logo(width, ink)` | SVG HTML | Official ABC Company wordmark |
| `red_arc(width)` | SVG HTML | Brand accent arc |
| `topbar(*pills_html)` | Markdown | Header with logo + status pills |
| `pill(text, live_dot, red)` | HTML | Status badge |
| `pin_banner(pin, subtitle)` | Markdown | Large centered PIN display |
| `player_chips(players)` | Markdown | Animated player name tags |
| `team_grouped_chips(players)` | Markdown | Players grouped by team with team headers |
| `hud(q_no, q_total, streak, score)` | Markdown | Quiz progress HUD |
| `timer_ring(seconds_left, total)` | Markdown | Circular countdown timer |
| `question_text(category, text)` | Markdown | Formatted question display |
| `verdict(good, title, sub)` | Markdown | Correct/Wrong feedback with streak |
| `podium(board)` | Markdown | 1st/2nd/3rd place display |
| `rank_rows(board, me, start, limit)` | Markdown | Ranked player rows (beyond top 3) |
| `team_rows(teams)` | Markdown | Team leaderboard rows |
| `distribution_bars(counts, options, correct)` | Markdown | Answer distribution bar chart |
| `confetti(n)` | Markdown | Confetti animation overlay |
| `awards_strip(awards)` | Markdown | Post-game awards display |
| `kpi_card(col, number, label, spark, tone)` | Markdown | Admin dashboard KPI card |
| `waiting_dots(text)` | Markdown | Animated waiting indicator |
| `autorefresh(seconds)` | None | Poll game state (sleep + rerun); handles `_settle` on page switch |
| `stats_rail(teams, top3, my_team, me)` | Markdown | Left sidebar: team scores + top 3 players |
| `team_chat_rail(g, nick)` | Markdown | Right sidebar: team-scoped chat with composer |
| `countdown_popup(q_index, reveal_started, reveal_duration)` | Markdown | JS countdown overlay (3→2→1→GO!) with Web Audio beeps |
| `sound_effects()` | Markdown | Injects Web Audio API hover/click sounds on answer/vote/avatar buttons |

**When to Edit:**
- Change component styling → Update HTML in function
- New reusable element → Add new function here

---

### **ui/login_page.py** — Login & Join Page
**Purpose:** Entry point — participant join (PIN) + admin sign-in

**Layout:**
- Left: Hero (logo, tagline, badges)
- Right: 2 tabs
  - **Participant tab:** PIN input, nickname, SOEID, team selector, avatar picker, solo demo button
  - **Admin tab:** Email/password login

**Session State Set:**
- `role` → "participant", "admin", or "host"
- `nick`, `team`, `soeid`, `avatar`, `admin_email`, `admin_name`
- `page` → "transition" (then auto-forwards to "lobby" or "admin")

**When to Edit:**
- Change hero text → Markdown string in left column
- Modify form layout → Streamlit form components
- Add/remove team options → `config.TEAM_SUGGESTIONS`

---

### **ui/transition_page.py** — Neon Loading Transition (NEW)
**Purpose:** Full-screen animated transition shown after login before entering the app

**Key Function:**
- `render()` — Displays role-specific loading animation (3.4s), then forwards to destination page

**Features:**
- Role-based styling: admin (red ⚡), host (teal 🎛️), participant (blue 🎮)
- Animated grid background with scan line
- Corner bracket decorations
- Pulsing icon ring with glow
- Name, SOEID/email, team pill display
- Animated progress bar (0→100% in 3.1s)
- Floating particles spawned by JS
- "Loading Profile" label with animated dots

**Session State Used:**
- `role`, `nick`, `soeid`, `team`, `admin_name`, `admin_email`
- `dest_page` → where to go after transition (default: "lobby")

**When to Edit:**
- Change animation duration → `time.sleep(3.4)` and `dur = 3100` in `_js()`
- Modify role colors → `_ACCENTS` dict
- Add/remove displayed info → `_overlay()` HTML template

---

### **ui/lobby_page.py** — Waiting Room
**Purpose:** Pre-game lobby (players see PIN, wait for host to start)

**Features:**
- PIN banner with join count
- Avatar picker grid
- Team-grouped player chip list
- "Me" card showing current player
- Team chat rail (right sidebar)
- Auto-refresh every 1.5 seconds

**When to Edit:**
- Change refresh rate → `autorefresh(seconds)` parameter
- Modify player display → `team_grouped_chips()` call
- Adjust chat → `team_chat_rail()` component

---

### **ui/quiz_page.py** — Question Screen
**Purpose:** Player view during quiz — 3-column layout with stats, stage, and chat

**Layout (3 columns):**
```
rail_l (1.0)    | stage (2.3)       | rail_r (1.1)
stats_rail()    | question/voting   | team_chat_rail()
                | /reveal content   |
```

**Key Functions:**
- `render()` — Routes to phase-specific renderer
- `_render_question(g, q, nick)` — MCQ answer buttons or subjective text input
- `_render_voting(g, nick)` — Vote for best subjective answer
- `_render_reveal(g, q, nick, is_controller)` — Show correct answer + verdict

**Flow:**
1. QUESTION phase → Show question + 4 answer buttons (or text input for subjective)
2. Player submits answer
3. VOTING phase (subjective only) → Vote for best answer
4. REVEAL phase → Show correct answer + verdict + distribution bars
5. Auto-advance to next question

**Components Used:**
- Timer ring (countdown)
- HUD (progress, streak, score)
- MCQ: 4 Kahoot-colored buttons (`.st-key-ans0..3`)
- Subjective: Text area + voting buttons
- Verdict: Correct ✓ / Wrong ✗ with streak update
- Sound effects on buttons
- Countdown popup (3→2→1→GO!) with audio

**When to Edit:**
- Change button layout → Streamlit columns in `_render_question()`
- Modify answer submission → `game.submit_answer()` / `submit_text()`
- Adjust verdict display → `verdict()` component
- Change column widths → `st.columns([1, 2.3, 1.1])`

---

### **ui/results_page.py** — Final Leaderboard
**Purpose:** Post-game results — individual & team rankings, podium, awards

**Features:**
- Podium (top 3 players)
- Awards strip (Speed Demon, Longest Streak, Sharp Shooter, Crowd Favourite)
- Individual leaderboard table (rank_rows)
- Team leaderboard (team_rows)
- Per-player answer breakdown
- Confetti animation
- Replay or return to lobby buttons

**When to Edit:**
- Change podium design → `podium()` component in `components.py`
- Modify leaderboard table → `rank_rows()` / `team_rows()` calls
- Add new award → `compute_awards()` in `core/game.py`

---

### **ui/admin_page.py** — Admin Dashboard
**Purpose:** Quiz management, question bank, team management, KPIs, user admin

**Key Functions:**
- `render()` — Tab router
- `_dashboard()` — KPI cards + recent results
- `_quiz_library(email)` — Create/edit/delete quizzes
- `_question_bank(email)` — Browse & use question bank
- `_question_builder(email)` — Manual question entry (MCQ/subjective)
- `_teams(email)` — Team management (add/edit/delete teams)

**Tabs:**
1. **Dashboard:** Game stats, recent results
2. **Quiz Library:** Create/edit/delete quizzes, build from question bank
3. **Question Builder:** Add/edit questions (MCQ or subjective)
4. **Teams:** Register teams with name, emoji, color
5. **Users:** Add admin/host accounts

**Key Features:**
- Create quiz from question bank (auto-generate)
- Manual question entry
- Delete quizzes
- View KPIs (total games, avg score, top categories)
- Team CRUD operations

**When to Edit:**
- Add KPI metric → `storage.get_kpis()` + display logic
- Change quiz form → Streamlit form components
- Add team field → `storage.upsert_team()` schema

---

### **ui/host_page.py** — Host Control Panel
**Purpose:** Admin controls live game (start, advance, force controls, see real-time state)

**Key Functions:**
- `render()` — Main router
- `_lobby(g, email)` — Show PIN, player list, "Start Game" button
- `_game_flow(g)` — Status-based router for live game phases
- `_hype(g)` — Pre-question hype screen
- `_live(g, email)` — Live question view: question, timer, who answered, force controls
- `_reveal(g, email)` — Answer reveal: correct answer, distribution, scores, next button

**Host Navigation:**
- **"🎛️ Command Center"** button → Back to admin page
- **"🔄 Change / New Game"** button → Finish current game (if active), clear state, go to admin

**Host Controls:**
- Start game from lobby
- Force advance / end answering (`game.force_reveal()`)
- Force end voting (`game.force_end_voting()`)
- End game early (`game.finish()`)
- Manual next-question button
- Live player answer status
- Real-time score updates
- Subjective voting monitor

**When to Edit:**
- Change host view layout → Streamlit UI structure in `_live()` / `_reveal()`
- Add host controls → New buttons calling `game.*` functions

---

## 🔍 COMMON EDIT SCENARIOS

### **Scenario 1: Change Scoring Formula**
**Files to Edit:**
1. `config.py` — Adjust `BASE_POINTS`, `STREAK_BONUS_PER_LEVEL`, `STREAK_BONUS_CAP`, `VOTE_POINTS`, `VOTE_WINNER_BONUS`
2. `core/game.py` — Modify `_score_mcq()` and `compute_awards()` functions
3. Optional: Update docstring in `game.py` with new formula

---

### **Scenario 2: Add New Question Type**
**Files to Edit:**
1. `core/storage.py` — Add to SCHEMAS (questions sheet)
2. `core/game.py` — Handle new type in `submit_answer()` / `tick()` / `_begin_question()`
3. `ui/quiz_page.py` — Add UI for new type in `_render_question()`
4. `ui/admin_page.py` — Add form fields for new type in `_question_builder()`

---

### **Scenario 3: Change Brand Colors**
**Files to Edit:**
1. `config.py` — Update color constants (`ABC_*`, `GOLD`, `TEAL`)
2. `ui/theme.py` — Update CSS `:root` variables (`--abc-navy`, etc.)
3. `prototype/css/styles.css` — Keep design prototype in sync

---

### **Scenario 4: Modify Timer Duration**
**Files to Edit:**
1. `config.py` — Change `DEFAULT_TIMER_SEC`, `SUBJECTIVE_TIMER_SEC`, `VOTING_TIMER_SEC`
2. Optional: Override per-quiz in admin panel (already supported)

---

### **Scenario 5: Add New Page**
**Files to Create/Edit:**
1. Create `ui/new_page.py` with `render()` function
2. `app.py` — Add to `PAGES` dict + role checks if needed
3. Add navigation button in existing page → `st.session_state["page"] = "new_page"`

---

### **Scenario 6: Add New Team Chat Feature**
**Files to Edit:**
1. `core/game.py` — Modify `post_chat()` (e.g., add emoji reactions, pinned messages)
2. `ui/components.py` — Update `team_chat_rail()` rendering

---

### **Scenario 7: Add Sound/Audio Effects**
**Files to Edit:**
1. `ui/components.py` — Modify `sound_effects()` (Web Audio API hooking) or `countdown_popup()` (beeps)

---

## 🛠 HOW TO USE THIS INDEX

### **For Code Queries:**
1. **Find the feature:** Use Quick Lookup Table
2. **Identify the file:** See File Details section
3. **Locate the function:** Check Key Functions list
4. **Read dependencies:** See "When to Edit" notes

### **For Editing:**
1. **Identify what to change:** Use Common Edit Scenarios
2. **Find all affected files:** Cross-reference dependencies
3. **Make changes:** Edit files in order (config → core → ui)
4. **Check prototype:** Match design in `prototype/` folder

### **For Understanding Flow:**
```
User Action → UI Page → Core Logic → Storage → Data File
   ↓            ↓          ↓           ↓          ↓
Click Join → login_page → game.join → Excel → quizzes.xlsx
                ↓
         transition_page (neon loading, 3.4s)
                ↓
            lobby_page (waiting room + chat)
```

### **For Debugging:**
1. Check `data/activity_log.xlsx` for user actions
2. Check `data/live_game.json` for current state (including `chat` and `bot_plan`)
3. Check browser console for JS errors (theme effects, sound, countdown)
4. Check terminal for Streamlit errors

---

## 📚 DEPENDENCY MAP

```
app.py
├── core.seed
├── core.question_bank
├── ui.theme
└── ui.*_page
    ├── ui.components
    ├── core.game
    ├── core.storage
    └── core.auth

core.game
├── core.storage (persist results)
├── core.logger (audit trail)
└── config (rules & constants)

core.storage
├── config (file paths)
└── pandas / openpyxl (Excel I/O)

ui.*_page
├── ui.components (reusable UI: chat, stats rail, countdown, sounds)
├── ui.theme (via app.py inject)
└── core.* (business logic)

ui.components
├── config (brand colors, paths)
└── streamlit (st.markdown, st.components.v1.html)

ui.transition_page
├── config (brand colors)
└── streamlit.components.v1 (JS iframe for particles + progress)
```

---

## 🎨 DESIGN CONSISTENCY

**Always check `prototype/` before editing UI:**
- `prototype/index.html` → `ui/login_page.py`
- `prototype/lobby.html` → `ui/lobby_page.py`
- `prototype/quiz.html` → `ui/quiz_page.py`
- `prototype/leaderboard.html` → Mid-game rankings (used in quiz_page reveal)
- `prototype/results.html` → `ui/results_page.py`
- `prototype/admin.html` → `ui/admin_page.py`
- `prototype/host.html` → `ui/host_page.py`

**Note:** `ui/transition_page.py` has no prototype counterpart — it's a custom neon loading screen.

**CSS Source:** `prototype/css/styles.css` should match `ui/theme.py`

---

## 🚀 COMMON TASKS CHEAT SHEET

| Task | Files | Function |
|------|-------|----------|
| Add new question | admin_page.py | Question Builder tab |
| Change scoring | config.py, game.py | BASE_POINTS, _score_mcq() |
| Modify UI colors | theme.py, config.py | CSS vars, color constants |
| Add admin user | auth.py, admin_page.py | add_admin() |
| Generate questions | question_bank.py | ensure_bank() |
| Change timer | config.py | DEFAULT_TIMER_SEC |
| Delete a quiz | storage.py, admin_page.py | delete_quiz() |
| Manage teams | storage.py, admin_page.py | upsert_team(), delete_team() |
| View game logs | N/A | Open data/activity_log.xlsx |
| Debug game state | N/A | Open data/live_game.json |
| Edit branding | login_page.py, theme.py | Hero section, CSS |
| Add bot | config.py | BOT_ROSTER list |
| Change transition screen | transition_page.py | _overlay(), _js() |
| Add chat feature | game.py, components.py | post_chat(), team_chat_rail() |
| Modify sound effects | components.py | sound_effects(), countdown_popup() |
| Force-advance game | game.py, host_page.py | force_reveal(), force_end_voting() |
| Start solo demo | game.py, login_page.py | start_solo_demo() |

---

## 📝 NOTES FOR AI ASSISTANTS

When querying this codebase:
1. **Always specify the file** using this index
2. **Check dependencies** before making changes
3. **Match prototype design** for UI edits
4. **Update CLAUDE.md** if architecture changes
5. **Test flow:** login → transition → lobby → quiz → results
6. **Remember:** Everything is local (no API calls, no secrets)
7. **Chat data** lives in `live_game.json` under `g["chat"][team]` — cleared on game finish
8. **Page-switch ghosting** is handled by `_settle` flag + `autorefresh()` hidden button pattern

**Token-efficient queries:**
- ❌ "Read entire codebase"
- ✅ "Read game.py lines 170-200" (scoring logic)
- ✅ "Search for 'BASE_POINTS' in config.py and game.py"

---

**Last Updated:** 2026-07-04
**Version:** 2.0
**Maintainer:** QuizTok Team

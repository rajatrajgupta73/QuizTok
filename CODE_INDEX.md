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
│
├── core/                    # Business logic layer
│   ├── game.py              # Live game engine (state machine, scoring)
│   ├── storage.py           # Excel read/write operations
│   ├── auth.py              # Admin authentication
│   ├── question_bank.py     # 2000-question generator
│   ├── seed.py              # First-run database setup
│   └── logger.py            # Activity logging
│
├── ui/                      # Presentation layer (Streamlit)
│   ├── theme.py             # All CSS & visual effects
│   ├── components.py        # Reusable UI elements
│   ├── login_page.py        # Login/join page
│   ├── lobby_page.py        # Pre-game waiting room
│   ├── quiz_page.py         # Player question view
│   ├── results_page.py      # Post-game leaderboard
│   ├── admin_page.py        # Quiz builder & admin panel
│   └── host_page.py         # Host control dashboard
│
├── data/                    # "Database" (Excel files)
│   ├── users.xlsx           # Admin accounts
│   ├── quizzes.xlsx         # Quiz library + questions
│   ├── results.xlsx         # Game history
│   ├── question_bank.xlsx   # 2000 pre-generated questions
│   ├── activity_log.xlsx    # Audit trail
│   └── live_game.json       # Active game state (shared)
│
├── prototype/               # Design source of truth (HTML)
│   ├── index.html           # Login page design
│   ├── lobby.html           # Lobby design
│   ├── quiz.html            # Question screen design
│   ├── leaderboard.html     # Mid-game rankings
│   ├── results.html         # Final results design
│   ├── admin.html           # Admin panel design
│   ├── host.html            # Host control design
│   └── css/styles.css       # Prototype CSS
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
| Question generation                | `core/question_bank.py`           |
| App initialization                 | `app.py`                          |
| Design reference                   | `prototype/` HTML files           |

---

## 📋 FILE DETAILS

### **app.py** — Entry Point
**Purpose:** Bootstrap the app and route pages based on session state

**Key Functions:**
- `_bootstrap()` — One-time setup: seeds data, creates 2000 questions
- Page routing via `st.session_state["page"]`

**Pages Map:**
```python
"login"   → login_page.render()
"lobby"   → lobby_page.render()
"quiz"    → quiz_page.render()
"results" → results_page.render()
"admin"   → admin_page.render()
"host"    → host_page.render()
```

**Dependencies:** All UI pages, core.seed, core.question_bank, ui.theme

---

### **config.py** — Configuration Constants
**Purpose:** Single source of truth for all constants (no secrets, everything local)

**Key Sections:**
- **Paths:** DATA_DIR, USERS_XLSX, QUIZZES_XLSX, etc.
- **Branding:** APP_NAME, colors (CITI_NAVY, CITI_BLUE, CITI_RED, GOLD)
- **Game Rules:**
  - `BASE_POINTS = 1000` (per question)
  - `STREAK_BONUS_PER_LEVEL = 50` (bonus per streak)
  - `DEFAULT_TIMER_SEC = 20`
  - `VOTE_POINTS = 300` (per vote in subjective questions)
- **Bot Config:** BOT_ROSTER (name, avatar, skill level)
- **Teams:** TEAM_SUGGESTIONS, BOT_TEAMS

**When to Edit:**
- Changing point values → `BASE_POINTS`, `STREAK_BONUS_PER_LEVEL`
- Adjusting timers → `DEFAULT_TIMER_SEC`, `VOTING_TIMER_SEC`
- Brand colors → CITI_* constants
- Bot behavior → BOT_ROSTER tuples

---

### **core/game.py** — Game Engine
**Purpose:** All live game logic — state machine, scoring, bot AI, team leaderboards

**Game State Machine:**
```
LOBBY → QUESTION → REVEAL → QUESTION → ... → FINISHED
        (for subjective: QUESTION → VOTING → REVEAL)
```

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `load()` / `save(g)` | Read/write live_game.json (atomic writes) |
| `create_game(quiz_id, host, with_bots)` | Initialize new game with PIN |
| `join(pin, nick, avatar, team)` | Player joins lobby |
| `start(actor)` | Host starts game (LOBBY → QUESTION) |
| `answer_mcq(nick, choice, time_taken)` | Record MCQ answer + calculate score |
| `answer_subjective(nick, text)` | Record typed answer for voting |
| `vote(voter, target)` | Submit vote for best answer |
| `next_question(actor)` | Advance to next question |
| `tick()` | Auto-advance state (bots answer, phase timeouts) |
| `leaderboard(g, team_mode)` | Generate ranked list |
| `finalize(g)` | Save results to results.xlsx |

**Scoring Logic:**
```python
# MCQ:
base_points = 1000
time_bonus = base * (time_left / timer)
streak_bonus = min(streak, 5) * 50
total = base + time_bonus + streak_bonus

# Subjective:
points = votes_received * 300
if most_votes: points += 500
```

**Bot AI:**
- `skill` = probability of correct answer (0.0–1.0)
- Bots answer at random intervals with slight delays
- Bot subjective answers picked from `config.BOT_SUBJECTIVE_ANSWERS`

**When to Edit:**
- Change scoring formula → `answer_mcq()` function
- Adjust bot behavior → `_bot_should_answer()`, `tick()` logic
- Modify state transitions → `_begin_question()`, `next_question()`

---

### **core/storage.py** — Data Layer
**Purpose:** All Excel read/write operations (users, quizzes, results)

**Schema Map:**
```python
SCHEMAS = {
    users.xlsx / admins:     ["email", "name", "password_hash", "created_at"]
    quizzes.xlsx / quizzes:  ["quiz_id", "title", "emoji", "category", "timer_sec", ...]
    quizzes.xlsx / questions: ["quiz_id", "q_index", "qtype", "question", "opt_a", ...]
    results.xlsx / games:     ["game_id", "quiz_title", "played_at", "winner", ...]
    results.xlsx / scores:    ["game_id", "rank", "player", "score", ...]
    results.xlsx / answers:   ["game_id", "player", "q_index", "picked", ...]
    activity_log.xlsx / log:  ["timestamp", "actor", "role", "action", "details"]
}
```

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `read_sheet(path, sheet)` | Load one Excel sheet as DataFrame |
| `write_sheet(path, sheet, df)` | Save DataFrame (preserves other sheets) |
| `append_rows(path, sheet, rows)` | Add rows without rewriting file |
| `get_quizzes()` | Load all quizzes |
| `get_questions(quiz_id)` | Load questions for one quiz |
| `save_quiz(row, questions)` | Create or update quiz + questions |
| `get_results(limit)` | Recent game history |
| `get_kpis()` | Dashboard stats (games played, avg scores, etc.) |

**When to Edit:**
- Add new Excel columns → Update SCHEMAS dict
- New data file → Add path to config.py + schema here
- Change data format → Modify read/write helpers

---

### **core/auth.py** — Authentication
**Purpose:** Admin login verification (users.xlsx)

**Key Functions:**
- `verify_admin(email, password)` → `(ok: bool, name: str)`
- `add_admin(email, name, password, added_by)` → `bool`
- `ensure_default_admin()` — Seeds admin@citi.com / citi123 on first run

**Security:**
- SHA-256 password hashing with salt prefix
- No API calls, no network, fully local

---

### **core/question_bank.py** — Question Generator
**Purpose:** Create 2000 diverse questions (10 categories, 3 difficulties)

**Categories:**
1. Banking & Citi Knowledge
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

### **core/logger.py** — Activity Log
**Purpose:** Audit trail of all user actions

**Function:** `log(actor, role, action, details="")`

**Examples:**
```python
log("user@citi.com", "admin", "login_ok")
log("Priya", "participant", "joined_game", pin)
log("host@citi.com", "admin", "quiz_created", quiz_id)
```

Writes to `activity_log.xlsx`

---

### **ui/theme.py** — Visual Design
**Purpose:** All CSS, animations, JS effects

**What's Inside:**
- **CSS Variables:** Colors, glass effects, borders, fonts
- **Animations:** Rise, bounce, pulse, glow, fall (floaters)
- **Kahoot Answer Buttons:** 4-color grid (blue/red/gold/teal)
- **Login Page Effects:** Glow ring, ink canvas, floating symbols
- **Streamlit Overrides:** Hide menu, sidebar, adjust spacing

**Key CSS Classes:**
```css
.qt-topbar         /* Header with logo & pills */
.qt-card           /* Glass card container */
.qt-pin            /* Big centered PIN display */
.qt-timer          /* Circular countdown */
.qt-hud            /* Quiz progress bar + streak */
.qt-podium         /* 1st/2nd/3rd place display */
.qt-verdict        /* Correct/Wrong feedback */
.st-key-ans0..3    /* Kahoot answer button colors */
```

**JavaScript Effects:**
- Glow ring (rotating gradient)
- Ink splash canvas (mouse tracking)
- Floating symbols (login page)
- DOM janitor (cleans up across reruns)

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
| `citi_logo(width, ink)` | SVG HTML | Official Citi wordmark |
| `red_arc(width)` | SVG HTML | Brand accent arc |
| `topbar(*pills)` | Markdown | Header with logo + status pills |
| `pill(text, live_dot, red)` | HTML | Status badge |
| `pin_banner(pin, subtitle)` | Markdown | Large centered PIN display |
| `player_chips(players)` | Markdown | Animated player name tags |
| `hud(q_no, q_total, streak, score)` | Markdown | Quiz progress HUD |
| `timer_ring(sec_left, total)` | Markdown | Circular countdown timer |
| `question_text(category, text)` | Markdown | Formatted question display |
| `verdict(correct, streak)` | Markdown | Correct/Wrong feedback with streak |
| `podium(top3)` | Markdown | 1st/2nd/3rd place display |
| `autorefresh(seconds)` | None | Poll game state (sleep + rerun) |

**When to Edit:**
- Change component styling → Update HTML in function
- New reusable element → Add new function here

---

### **ui/login_page.py** — Login & Join Page
**Purpose:** Entry point — participant join (PIN) + admin sign-in

**Layout:**
- Left: Hero (logo, tagline, badges)
- Right: 2 tabs
  - **Participant tab:** PIN input, nickname, team selector, solo demo button
  - **Admin tab:** Email/password login

**Session State Set:**
- `role` → "participant" or "admin"
- `nick`, `team`, `admin_email`, `admin_name`
- `page` → "lobby" or "admin"

**When to Edit:**
- Change hero text → Markdown string in left column
- Modify form layout → Streamlit form components
- Add/remove team options → `config.TEAM_SUGGESTIONS`

---

### **ui/lobby_page.py** — Waiting Room
**Purpose:** Pre-game lobby (players see PIN, wait for host to start)

**Features:**
- PIN banner with join count
- Player chip list (animated)
- "Me" card showing current player
- Auto-refresh every 2 seconds
- Ready status

**When to Edit:**
- Change refresh rate → `autorefresh(seconds)` parameter
- Modify player display → `player_chips()` call

---

### **ui/quiz_page.py** — Question Screen
**Purpose:** Player view during quiz — answer MCQ/subjective, see feedback

**Flow:**
1. QUESTION phase → Show question + 4 answer buttons (or text input)
2. Player submits answer
3. VOTING phase (subjective only) → Vote for best answer
4. REVEAL phase → Show correct answer + verdict
5. Auto-advance to next question

**Components:**
- Timer ring (countdown)
- HUD (progress, streak, score)
- MCQ: 4 Kahoot-colored buttons (`.st-key-ans0..3`)
- Subjective: Text area + voting buttons
- Verdict: Correct ✓ / Wrong ✗ with streak update

**When to Edit:**
- Change button layout → Streamlit columns
- Modify answer submission → `game.answer_mcq()` / `answer_subjective()`
- Adjust verdict display → `verdict()` component

---

### **ui/results_page.py** — Final Leaderboard
**Purpose:** Post-game results — individual & team rankings, podium

**Features:**
- Podium (top 3 players)
- Full leaderboard table
- Team leaderboard (if teams present)
- Per-player answer breakdown
- Replay or return to lobby buttons

**When to Edit:**
- Change podium design → `podium()` component in `components.py`
- Modify leaderboard table → Streamlit dataframe display

---

### **ui/admin_page.py** — Admin Dashboard
**Purpose:** Quiz management, KPIs, user admin

**Tabs:**
1. **Dashboard:** Game stats, recent results
2. **Quiz Library:** Create/edit/delete quizzes
3. **Question Builder:** Add/edit questions (MCQ or subjective)
4. **User Management:** Add admin accounts

**Key Features:**
- Create quiz from question bank (auto-generate)
- Manual question entry
- Publish/unpublish quizzes
- View KPIs (total games, avg score, top categories)

**When to Edit:**
- Add KPI metric → `storage.get_kpis()` + display logic
- Change quiz form → Streamlit form components

---

### **ui/host_page.py** — Host Control Panel
**Purpose:** Admin controls live game (start, advance, see real-time state)

**Flow:**
1. Host creates game (picks quiz, enables bots)
2. LOBBY → Show PIN, player list, "Start Game" button
3. QUESTION → See question text, timer, who answered
4. REVEAL → Show correct answer, scores update
5. Repeat until FINISHED
6. Finalize & save results

**Components:**
- Live player status (answered/waiting)
- Real-time score updates
- Manual next-question button
- Subjective voting monitor

**When to Edit:**
- Change host view layout → Streamlit UI structure
- Add host controls → New buttons calling `game.*` functions

---

## 🔍 COMMON EDIT SCENARIOS

### **Scenario 1: Change Scoring Formula**
**Files to Edit:**
1. `config.py` — Adjust `BASE_POINTS`, `STREAK_BONUS_PER_LEVEL`
2. `core/game.py` — Modify `answer_mcq()` function (line ~170)
3. Optional: Update docstring in `game.py` with new formula

**Example:**
```python
# In config.py:
BASE_POINTS = 1500  # Changed from 1000

# In core/game.py, answer_mcq():
base = 1500  # Update here too
```

---

### **Scenario 2: Add New Question Type**
**Files to Edit:**
1. `core/storage.py` — Add to SCHEMAS (questions sheet)
2. `core/game.py` — Handle new type in `answer_*` functions
3. `ui/quiz_page.py` — Add UI for new type
4. `ui/admin_page.py` — Add form fields for new type

---

### **Scenario 3: Change Brand Colors**
**Files to Edit:**
1. `config.py` — Update color constants (CITI_*, GOLD, TEAL)
2. `ui/theme.py` — Update CSS `:root` variables (--citi-navy, etc.)
3. `prototype/css/styles.css` — Keep design prototype in sync

---

### **Scenario 4: Modify Timer Duration**
**Files to Edit:**
1. `config.py` — Change `DEFAULT_TIMER_SEC`
2. Optional: Override per-quiz in admin panel (already supported)

---

### **Scenario 5: Add New Page**
**Files to Create/Edit:**
1. Create `ui/new_page.py` with `render()` function
2. `app.py` — Add to PAGES dict
3. Add navigation button in existing page → `st.session_state["page"] = "new_page"`

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
```

### **For Debugging:**
1. Check `data/activity_log.xlsx` for user actions
2. Check `data/live_game.json` for current state
3. Check browser console for JS errors (theme effects)
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
├── core.storage (data persistence)
├── core.logger (audit trail)
└── config (rules & constants)

ui.*_page
├── ui.components (reusable UI)
├── ui.theme (via app.py inject)
└── core.* (business logic)
```

---

## 🎨 DESIGN CONSISTENCY

**Always check `prototype/` before editing UI:**
- `prototype/index.html` → `ui/login_page.py`
- `prototype/lobby.html` → `ui/lobby_page.py`
- `prototype/quiz.html` → `ui/quiz_page.py`
- `prototype/results.html` → `ui/results_page.py`
- `prototype/admin.html` → `ui/admin_page.py`
- `prototype/host.html` → `ui/host_page.py`

**CSS Source:** `prototype/css/styles.css` should match `ui/theme.py`

---

## 🚀 COMMON TASKS CHEAT SHEET

| Task | Files | Function |
|------|-------|----------|
| Add new question | admin_page.py | Question Builder tab |
| Change scoring | config.py, game.py | BASE_POINTS, answer_mcq() |
| Modify UI colors | theme.py, config.py | CSS vars, color constants |
| Add admin user | auth.py, admin_page.py | add_admin() |
| Generate questions | question_bank.py | ensure_bank() |
| Change timer | config.py | DEFAULT_TIMER_SEC |
| View game logs | N/A | Open data/activity_log.xlsx |
| Debug game state | N/A | Open data/live_game.json |
| Edit branding | login_page.py, theme.py | Hero section, CSS |
| Add bot | config.py | BOT_ROSTER list |

---

## 📝 NOTES FOR AI ASSISTANTS

When querying this codebase:
1. **Always specify the file** using this index
2. **Check dependencies** before making changes
3. **Match prototype design** for UI edits
4. **Update CLAUDE.md** if architecture changes
5. **Test flow:** login → lobby → quiz → results
6. **Remember:** Everything is local (no API calls, no secrets)

**Token-efficient queries:**
- ❌ "Read entire codebase"
- ✅ "Read game.py lines 170-200" (scoring logic)
- ✅ "Search for 'BASE_POINTS' in config.py and game.py"

---

**Last Updated:** 2026-07-03
**Version:** 1.0
**Maintainer:** QuizTok Team

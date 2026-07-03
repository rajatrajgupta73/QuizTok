# QuizTok — Citi-branded team quiz app (Streamlit)

Kahoot-style live quiz platform for Citi team events. 100% local: Excel files as the database, no internet required at runtime (Google Fonts load via CSS `@import` when online; falls back to system fonts offline).

**Run:** `streamlit run app.py` (from this directory) → http://localhost:8501
**Default admin:** admin@citi.com / citi123 (demo credential, shown on the login page)

## Architecture

Single Streamlit process. `app.py` routes by `st.session_state["page"]` →
`login | lobby | quiz | results | admin | host` (admin/host require `role == "admin"`).
Multi-client play works by polling shared state on disk: `ui.components.autorefresh(sec)`
does `time.sleep + st.rerun`, and `core.game.tick()` advances bots and phases.

### File map

| Path | Purpose |
|---|---|
| `app.py` | Entry: bootstrap (seed + question bank), theme inject, page router |
| `config.py` | Timers, points, avatars, team suggestions, data-file paths |
| `core/game.py` | All game logic: create/join/start, scoring, bots, phases, leaderboards |
| `core/storage.py` | Excel read/write helpers, quizzes/questions/results/KPIs |
| `core/question_bank.py` | 2000-question bank (data/question_bank.xlsx), build-quiz-from-bank |
| `core/auth.py` | Admin verification (users.xlsx) |
| `core/seed.py` | First-run seeding (admin user, sample quizzes) |
| `core/logger.py` | Activity log → data/activity_log.xlsx |
| `ui/theme.py` | All CSS (`qt-*` classes) + JS effects (glow/ink canvas, floaters, janitor) |
| `ui/components.py` | HTML components: topbar, pills, pin banner, podium, HUD, timer ring… |
| `ui/*_page.py` | One render() per page |
| `data/*.xlsx` | The "database" — editable in Excel |
| `prototype/*.html` | **Design source of truth** — static HTML mockups of every page |

### Game state (JSON on disk, managed by core/game.py)

Statuses: `LOBBY → QUESTION → (VOTING for subjective) → REVEAL → … → FINISHED`.
Players dict holds per-player `answers` list: `{q, choice, text, correct, time_taken, points, votes}`.
Host is an admin email, or `"__solo__"` for the solo-vs-bots demo.

## Design system (must match prototype/)

The visual target is `prototype/` (index/lobby/quiz/leaderboard/results/admin/host
.html + `css/styles.css`). When changing UI, check the prototype page first.

- Fonts: **Poppins** body, **Baloo 2** for display numbers/headings (PIN, timer,
  scores, podium, verdict, h3 panels). Loaded via `@import` inside the `<style>` block.
- Palette: citi-navy `#003b70`, citi-blue `#0088ce`, citi-sky `#4db4ff`,
  citi-red `#e21836`, gold `#ffc233`, teal `#00c9a7`; glass cards
  `rgba(255,255,255,.06)` + 1px stroke + blur.
- Button variants via Streamlit container keys: `st-key-ans0..3` (Kahoot answer
  colors), `st-key-red*`, `st-key-gold*`, `st-key-vote*`, `st-key-avat*`,
  `st-key-pinbox` (big centered PIN input).

## Gotchas (learned the hard way)

- `st.markdown` HTML: keep everything in ONE `<style>` block with no stray tags
  before it — a `<link>` tag first makes the markdown parser cut the HTML block at
  the first blank line and dump raw CSS as visible text. Use `@import` for fonts.
- Column test-id is `data-testid="stColumn"` in this Streamlit version (not `"column"`).
- Login-page-only styling is scoped via a `.qt-login-scope` marker + `body:has()`;
  the mascot/glow-ring are injected by a parent-realm "janitor" interval in
  `theme.py` (`_FLOATERS_JS`) because Streamlit reuses DOM nodes across reruns —
  one-shot injections leak onto other pages.
- Scripts never execute inside `st.markdown`; use `st.components.v1.html` (iframe)
  and reach the parent page via `window.parent`.
- `ui.autorefresh` blocks the script run (sleep+rerun) — only call it as the last
  statement of a render path.

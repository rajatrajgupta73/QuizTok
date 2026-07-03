# How to Use CODE_INDEX.md for Efficient Code Editing

## 🎯 Overview
`CODE_INDEX.md` is your navigation map for the entire QuizTok codebase. It helps you (and AI assistants) quickly find what to edit without reading the entire project.

---

## 📖 When to Use the Index

### ✅ Use it when you want to:
- Find which file contains a specific feature
- Understand what a file does before opening it
- See all functions in a module at a glance
- Find dependencies between files
- Get common edit scenarios/examples
- Understand the data flow

### ❌ Don't need it for:
- Simple text searches ("find all occurrences of X")
- Reading small utility files
- Making one-line config changes

---

## 🔍 How to Query Code Using the Index

### **Step 1: Identify the Feature Area**
Use the **Quick Lookup Table** (section 2 of CODE_INDEX.md):

```
Example: "I want to change the scoring"
→ Quick Lookup says: config.py + core/game.py
```

### **Step 2: Find the Specific Function**
Go to the file's detail section and check **Key Functions** table:

```
Example: In game.py section
→ Key Functions shows: answer_mcq() handles MCQ scoring (line ~170)
```

### **Step 3: Make a Targeted Query**
Instead of reading the whole file, ask for specific lines:

```
❌ BAD:  "Read entire game.py"
✅ GOOD: "Read game.py lines 170-200" (scoring function)
✅ GOOD: "Search for BASE_POINTS in config.py and game.py"
```

---

## ✏️ How to Edit Code Using the Index

### **Example 1: Change Timer Duration**

1. **Open CODE_INDEX.md** → Go to "Common Tasks Cheat Sheet"
2. **Find:** "Change timer" → Says: config.py, DEFAULT_TIMER_SEC
3. **Query:** "Show me DEFAULT_TIMER_SEC in config.py"
4. **Edit:** Change value from 20 to 30
5. **Done!** (No need to search other files)

### **Example 2: Modify Scoring Formula**

1. **Open CODE_INDEX.md** → Go to "Scenario 1: Change Scoring Formula"
2. **Files listed:** config.py (constants) + core/game.py (logic)
3. **Query 1:** "Show BASE_POINTS in config.py"
4. **Query 2:** "Show answer_mcq function in core/game.py lines 170-200"
5. **Edit both:** Update BASE_POINTS and the calculation
6. **Verify:** Check formula docstring matches

### **Example 3: Add New UI Element to Login Page**

1. **Open CODE_INDEX.md** → Find "ui/login_page.py" section
2. **Check dependencies:** Uses ui/components.py, ui/theme.py
3. **Check design:** Prototype is prototype/index.html
4. **Query 1:** "Read ui/login_page.py render() function"
5. **Query 2:** "Show available components in ui/components.py"
6. **Add element:** Insert new component in login_page.py
7. **Add styling:** Update theme.py if needed

---

## 🎨 For AI Assistants: Efficient Context Gathering

### **Token-Efficient Pattern:**

```
1. USER: "Change the points system"

2. AI: [Checks CODE_INDEX.md]
   → Quick Lookup: config.py + core/game.py
   → Scenario 1 shows exactly what to edit

3. AI: [Reads only needed lines]
   ✅ Read config.py lines 30-40 (point constants)
   ✅ Read game.py lines 170-220 (scoring function)
   ❌ Does NOT read entire codebase

4. AI: Makes targeted edits with full context
```

### **Multi-File Edits:**

Use **Dependency Map** (section in CODE_INDEX) to find all affected files:

```
Example: "Change branding colors"
→ Dependency Map shows:
  - config.py (color constants)
  - ui/theme.py (CSS variables)
  - prototype/css/styles.css (design reference)

→ Read only those 3 files, make coordinated changes
```

---

## 🔧 Common Query Patterns

### Pattern 1: Feature Location
```
Query: "Where is the login authentication code?"
Index: → "Quick Lookup Table" → auth.py
Result: Read core/auth.py, verify_admin() function
```

### Pattern 2: Understanding Data Flow
```
Query: "How does a quiz get saved?"
Index: → "Dependency Map" + storage.py section
Result: admin_page → storage.save_quiz() → quizzes.xlsx
```

### Pattern 3: Design Consistency
```
Query: "What should the lobby page look like?"
Index: → "Design Consistency" section
Result: Check prototype/lobby.html before editing ui/lobby_page.py
```

### Pattern 4: Debugging
```
Query: "Where are game states stored?"
Index: → "For Debugging" section
Result: Check data/live_game.json + activity_log.xlsx
```

---

## 📚 Index Structure Reference

```
CODE_INDEX.md
├── 1. Project Structure (file tree)
├── 2. Quick Lookup Table (feature → file mapping)
├── 3. File Details (what each file does)
│   ├── Key functions per file
│   ├── Dependencies
│   └── "When to Edit" notes
├── 4. Common Edit Scenarios (step-by-step examples)
├── 5. How to Use This Index (query patterns)
├── 6. Dependency Map (file relationships)
├── 7. Design Consistency (prototype → code mapping)
└── 8. Common Tasks Cheat Sheet (quick reference)
```

**Use sections in this order:**
1. **Quick Lookup** → Find the file
2. **File Details** → Find the function
3. **Common Scenarios** → See examples
4. **Dependency Map** → Find related files

---

## ⚡ Power User Tips

### Tip 1: Start with Scenarios
Before reading any code, check "Common Edit Scenarios" — your task might already be documented with steps.

### Tip 2: Cross-Reference Prototype
When editing UI, open both:
- `CODE_INDEX.md` (find the file)
- `prototype/*.html` (see the design target)

### Tip 3: Use Cheat Sheet for Quick Edits
"Common Tasks Cheat Sheet" lists file + function for 1-line edits.

### Tip 4: Check "When to Edit" Notes
Every file section has "When to Edit" — tells you if your change needs other files updated too.

### Tip 5: Grep Before Read
If you know the variable/function name:
```
grep "BASE_POINTS" → finds all occurrences
CODE_INDEX → tells you which file is the source of truth
```

---

## 🚀 Example Workflow

**Task:** "Add a new team name to the suggestions"

### Traditional Approach (Inefficient):
```
1. Search entire codebase for "team"
2. Find 50+ matches across 10 files
3. Read multiple files to understand context
4. Make changes in wrong place
5. Debug why it doesn't work
```

### With CODE_INDEX (Efficient):
```
1. Open CODE_INDEX.md
2. Search for "team" → Quick Lookup says config.py
3. File Details: TEAM_SUGGESTIONS list
4. Read config.py lines 45-48
5. Add new team name to list
6. Done! (30 seconds vs 30 minutes)
```

---

## 🎓 Learning the Codebase

**For New Developers:**

**Day 1:** Read these sections of CODE_INDEX.md
- Project Structure
- Quick Lookup Table
- Dependency Map

**Day 2:** Pick one feature area (e.g., "scoring")
- Read that file's detail section
- Read the actual code file
- Compare prototype HTML to UI code

**Day 3:** Try a Common Edit Scenario
- Follow the step-by-step guide
- Make the edit
- Test it

**Week 2+:** Use index as reference
- Don't memorize code locations
- Look them up in index each time
- Muscle memory builds naturally

---

## 📝 Maintaining the Index

**When to Update CODE_INDEX.md:**
- ✅ Add new file → Add to Project Structure + File Details
- ✅ Add new major function → Add to Key Functions table
- ✅ Change architecture → Update Dependency Map
- ✅ Common question from team → Add to Cheat Sheet
- ❌ Minor variable rename → No update needed
- ❌ Tweak CSS value → No update needed

**Rule:** Update index when the *structure* changes, not when *values* change.

---

## 🤖 For AI Coding Assistants

**System Prompt Guidance:**

```
When user requests a code edit:
1. Check if CODE_INDEX.md exists
2. Read relevant section (not entire file)
3. Use Quick Lookup to find target file
4. Read only needed lines from source files
5. Check "When to Edit" for dependencies
6. Make coordinated edits across all affected files
7. Verify against prototype if UI change

This saves 80-95% of tokens vs reading entire codebase.
```

**Token Budget Example:**
```
❌ Without index: 50,000 tokens to read codebase
✅ With index:    2,000 tokens to read index
                  3,000 tokens to read specific sections
                  = 5,000 tokens total (90% savings!)
```

---

## 📞 Quick Reference Card

```
┌─────────────────────────────────────────────┐
│  QUIZTOK CODE_INDEX.md QUICK REF            │
├─────────────────────────────────────────────┤
│  Need...              → Go to...            │
├─────────────────────────────────────────────┤
│  Find file            → Quick Lookup Table  │
│  Find function        → File Details        │
│  Edit example         → Common Scenarios    │
│  See relationships    → Dependency Map      │
│  Match design         → Design Consistency  │
│  Quick task           → Cheat Sheet         │
│  Understand flow      → How to Use section  │
└─────────────────────────────────────────────┘
```

---

**Pro tip:** Bookmark CODE_INDEX.md in your IDE — it's designed to be your first stop for any QuizTok code task!

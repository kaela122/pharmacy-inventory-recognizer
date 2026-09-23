# PharmaHub — Pharmacy Inventory + Product-Code Recognizer (CCAUTOMA · COM244)

PharmaHub is a pharmacy **Inventory Management System** with a built-in **automata
recognizer**. The recognizer is the CCAUTOMA graded part: a **minimized DFA** that decides
whether a pharmacy product code (like `M001`, `S002`, `C001`) is valid. Every medicine you add
is checked by that DFA before it can be saved — that is how the two halves connect.

- **Backend:** Python + FastAPI + SQLAlchemy (PostgreSQL, with automatic SQLite fallback)
- **Frontend:** TypeScript + React (Vite)
- **Automata:** `Regular Expression -> NFA -> DFA -> Minimized DFA -> simulator`

---

## What you need first (install once)

1. **Python 3.11+** — https://www.python.org/downloads/ (tick *"Add Python to PATH"* while installing)
2. **Node.js 18+** — https://nodejs.org (the "LTS" button)

PostgreSQL is optional. If you don't set it up, the app automatically uses a local SQLite
file, so it still runs. (See "Using PostgreSQL" near the end.)

To check they installed, open Command Prompt and type `python --version` and `node --version`.

---

## How to run it — step by step (Windows)

You need **two windows open at the same time**: one for the backend, one for the frontend.

### STEP 1 — Start the backend (window 1)

1. Open **Command Prompt**.
2. Go into the backend folder (change the path to where you unzipped the project):
   ```
   cd /d L:\pharmacy-inventory-recognizer\backend
   ```
3. Install the backend libraries (first time only):
   ```
   python -m pip install -r requirements.txt
   ```
4. Start it:
   ```
   python -m uvicorn app.main:app --reload
   ```
5. Leave this window open. When it says **`Application startup complete`**, the backend is on.
   The first start also creates the database and fills in the demo data automatically.

### STEP 2 — Start the frontend (window 2)

1. Open a **second** Command Prompt.
2. Go into the frontend folder:
   ```
   cd /d L:\pharmacy-inventory-recognizer\frontend
   ```
3. Install the frontend libraries (first time only):
   ```
   npm install
   ```
4. Start it:
   ```
   npm run dev
   ```
5. It shows a link like **`http://localhost:5173`**. Open that in your browser.

### STEP 3 — Log in

On the login screen, click any demo credential to fill it in, then **Authorize & Connect**:

| Employee ID | Password    | Role              | Can do                                   |
|-------------|-------------|-------------------|------------------------------------------|
| `ADMIN001`  | `admin123`  | System Admin      | Everything, including deleting medicines |
| `INVMGR01`  | `invmgr123` | Inventory Manager | Add/edit medicines and categories        |
| `PHARM001`  | `pharma123` | Pharmacist        | View everything (no adding/deleting)     |

> **Faster way:** double-click `start.bat` in the project folder — it opens both windows for you.
> First time only, double-click `setup.bat` once to install everything.

---

## What each screen does

- **Dashboard** — totals (units, SKUs, low-stock, out-of-stock), a low-stock alert list, and a
  category distribution chart.
- **Medicines** — the full product list. Search, filter by status (In / Low / Out of Stock), and
  add a medicine. Adding runs the **DFA check on the code** and blocks invalid ones.
- **Categories** — each category with its SKU count, total units, and total value; click to expand
  and see the medicines inside.
- **Orders** — purchase orders from suppliers, with totals and expandable line items.
- **Suppliers** — the supplier list with contact details; add, edit, or remove suppliers.
- **Analytics** — stock by category, inventory value by category, a status donut, and a
  "needs restocking" table.
- **Code Recognizer** — type any code and watch the DFA move through its states and accept/reject it.
- **Users** — *(admin only)* add staff accounts and set their role.

Each medicine also has **Stock** (record a stock-in / stock-out / adjustment) and **History**
(see every past stock change) — this is the inventory logging behind the numbers.

---

## The automata part (what gets graded)

- Full write-up (problem, language, RE, NFA, subset construction, minimization): **`docs/AUTOMATA_DESIGN.md`**
- Test cases with state paths and results: **`docs/TEST_RESULTS.md`**
- Final report (all 24 required sections, Word): **`docs/PharmaHub_CCAUTOMA_Report.docx`**
- Defense plan with timing and likely questions: **`docs/DEMO_SCRIPT.md`**
- The DFA in code (one source of truth): **`backend/app/automata/definitions.py`**
- NFA → DFA → minimized DFA, built in code: **`backend/app/automata/construction.py`**
- Same construction in the web app, step by step: **Automata Theory** page (sidebar)
- Standalone command-line simulator (no web needed):
  ```
  cd /d L:\pharmacy-inventory-recognizer
  python cli/simulator.py
  ```
  `python cli/simulator.py --demo` runs the 10 accepted + 10 rejected test cases.
  `python cli/simulator.py --theory` shows the NFA, subset construction and minimization step by step.
  (Or just double-click `run-simulator.bat`.)
- Automated tests, including the RE = NFA = DFA = minimized DFA equivalence check:
  ```
  cd /d L:\pharmacy-inventory-recognizer\backend
  python -m pytest -v
  ```

**Language:** one letter `M` / `S` / `C`, then exactly three digits.
`M` = Medicine, `S` = Supplement, `C` = Consumable. Example valid codes: `M001`, `S250`, `C999`.

---

## Using PostgreSQL instead of SQLite (optional)

The database lives in `backend/.env`. By default it uses SQLite (a local file), so you can ignore
this. To use PostgreSQL, open `backend/.env`, comment the SQLite line, and set your own password on
the PostgreSQL line:

```
# DATABASE_URL=sqlite:///./pharmahub.db
DATABASE_URL=postgresql+psycopg://postgres:YOURPASSWORD@localhost:5432/pharmahub
```

Create the database once in psql: `CREATE DATABASE pharmahub;` then start the backend again.

---

## Project layout

See **`docs/STRUCTURE.md`** for the folder tree and what each part does, and
**`docs/SYSTEM_DESIGN.md`** for the architecture and how the DFA is used.

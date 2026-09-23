# Project Structure

```
pharmacy-inventory-recognizer/
├── README.md                     how to install and run
├── setup.bat / start.bat         Windows helpers (install once / start both servers)
├── run-backend.bat, run-frontend.bat, run-simulator.bat
│
├── cli/
│   └── simulator.py              working automata simulator (no web needed)
│
├── backend/
│   ├── app/
│   │   ├── automata/             ← the graded automata part
│   │   │   ├── definitions.py    Σ, states, δ, start, accept (minimized DFA)
│   │   │   ├── dfa.py            runs the DFA symbol by symbol, records the trace
│   │   │   ├── recognizer.py     verdict + human-readable reason + decoded category
│   │   │   └── construction.py   ε-NFA, subset construction, minimization
│   │   ├── api/routes/           REST endpoints (recognizer, products, orders, ...)
│   │   ├── services/             business rules (ProductService calls the DFA)
│   │   ├── models/, schemas/     database tables and request/response shapes
│   │   ├── db/                   session + demo-data seeding
│   │   └── core/                 settings and security
│   └── tests/
│       ├── test_recognizer.py    accepted/rejected sets and reasons
│       └── test_equivalence.py   RE = NFA = DFA = minimized DFA
│
├── frontend/
│   └── src/
│       ├── lib/dfa.ts            TypeScript copy of the DFA for live animation
│       └── pages/                RecognizerPage, TheoryPage (Automata Theory), MedicinesPage, ...
│   └── public/diagrams/          NFA / DFA / minimized DFA SVGs shown on the Automata Theory page
│
└── docs/
    ├── PharmaHub_CCAUTOMA_Report.docx   final report (24 sections)
    ├── DEMO_SCRIPT.md            defense timing, who says what, likely questions
    ├── AUTOMATA_DESIGN.md        problem, language, RE, NFA, subset construction, minimization
    ├── TEST_RESULTS.md           test cases with state paths and results
    ├── SYSTEM_DESIGN.md          architecture and how the DFA is used
    ├── STRUCTURE.md              this file
    ├── diagrams/                 NFA, DFA and minimized DFA (PNG + SVG), and the script that draws them
    └── screenshots/              screens of the web app and the CLI simulator
```

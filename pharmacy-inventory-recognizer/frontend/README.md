# Frontend (React + TypeScript + Vite)

## Setup & run
```bash
npm install
npm run dev
# open http://localhost:5173  (make sure the backend is running on :8000)
```

Vite proxies `/api` to the FastAPI backend, so the recognizer page calls the
same minimized DFA the CLI simulator uses.

## Structure
```
src/
  api/         fetch client + recognizer calls
  pages/       RecognizerPage.tsx (the code validator UI)
  types/       shared TypeScript interfaces
  App.tsx      root component
  main.tsx     entry point
```

## Back-end Terminal
cd pharmacy-inventory-recognizer\backend
python -m uvicorn app.main:app --reload

## Front-end Terminal
cd pharmacy-inventory-recognizer\frontend
npm install
npm run dev

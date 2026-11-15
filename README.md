# AI HOUSEHOLD ASSISTANT

Ask your home anything — food safety, appliances, energy saving.
Now with **accounts**, a **profile menu**, and a **History** page.

```
house-ai-backend/    FastAPI + LangGraph + SQLite   (runs on port 8000)
house-ai-frontend/   React + Vite                   (runs on port 5173)
```

## What's new

| Feature | Where it lives |
|---|---|
| Sign up / log in | `house-ai-frontend/src/pages/Login.jsx`, backend `auth.py` + `/signup` `/login` routes |
| Profile picture (top left) with **History** and **Log out** | `src/components/ProfileMenu.jsx` |
| History list page, and a detail page with the full answer | `src/pages/History.jsx`, `src/pages/HistoryDetail.jsx` |
| "Recent queries" removed from the home page | `src/pages/Home.jsx` |
| Search bar keeps your question after you press Ask | `src/pages/Home.jsx` |
| All backend calls in one place | `src/api.js` |
| Users, login sessions and history saved in a database | `house-ai-backend/database.py` (SQLite file, created automatically) |

---

## Setup (first time only)

You need **Python 3.10+** and **Node.js 18+** installed.

### 1. Backend

Open a terminal in the `house-ai-backend` folder.

**Windows (PowerShell / Command Prompt)**
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Mac / Linux**
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Make sure `house-ai-backend/.env` contains your Groq key:
```
GROQ_API_KEY=your_key_here
```

### 2. Frontend

Open a second terminal in the `house-ai-frontend` folder:
```
npm install
```

Make sure `house-ai-frontend/.env` contains:
```
VITE_API_URL=http://localhost:8000
```

---

## Run it (every time)

You need **both** running at once, in two terminals.

**Terminal 1 — backend** (inside `house-ai-backend`, with the venv activated)
```
uvicorn api.index:app --reload --port 8000
```

**Terminal 2 — frontend** (inside `house-ai-frontend`)
```
npm run dev
```

Open **http://localhost:5173** → click **Create an account** → ask away.

The first time the backend starts it creates `house-ai-backend/household.db`.
To wipe all users and history, stop the server and delete that file.

---

## How the login works (simple version)

1. You sign up or log in → the backend checks your password and sends back a random **token**.
2. The frontend saves the token in the browser (`localStorage`) and sends it with every request.
3. The backend looks the token up in the `sessions` table to know who you are.
4. **Log out** deletes the token. Tokens also expire after 30 days.

Passwords are never stored — only a salted hash (`auth.py`).

## API routes

| Method | Route | Login needed | What it does |
|---|---|---|---|
| POST | `/signup` | no | Create account, returns token |
| POST | `/login` | no | Returns token |
| GET | `/me` | yes | Who am I? |
| POST | `/logout` | yes | Ends the session |
| POST | `/chat` | yes | Asks the AI **and saves it to history** |
| GET | `/history` | yes | Your past queries (newest first) |
| GET | `/history/{id}` | yes | One query with the full answer |

---

## Deploying to Vercel (important)

- **Frontend:** add `VITE_API_URL` (your backend URL) in the Vercel project settings.
  `house-ai-frontend/vercel.json` is included so refreshing `/history` doesn't 404.
- **Backend:** Vercel can't keep a SQLite file — the disk is wiped regularly, so accounts
  and history would vanish. For a real deployment, swap SQLite for a hosted database
  (Neon / Supabase Postgres, or Turso). Only `database.py` needs to change.
  Also set `GROQ_API_KEY` in the backend's Vercel settings.

## Notes

- The `.py` files in the project's top folder (next to this README) are older copies of the
  ones in `house-ai-backend/`. The app only uses the `house-ai-backend` ones.
- `.env` holds your secret key — don't upload it to GitHub (a `.gitignore` is included
  in the backend folder).

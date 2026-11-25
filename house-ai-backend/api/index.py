from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import graph
import database
from auth import hash_password, check_password, get_token, get_current_user
from youtube_service import get_youtube_link
# Create the database tables the first time the server starts
database.init_db()

app = FastAPI()

# --- CORS ---
# Your frontend and backend are deployed as separate Vercel projects,
# so the browser will block requests unless the frontend's origin is
# explicitly allowed here. Replace the placeholder below with your
# actual frontend URL before going to production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
         "https://ai-household-assistant-p86f.vercel.app",
        "http://localhost:5173",  # local Vite dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.get("/")
def home():
    return {"message": "House AI Backend is running"}

# ---------------- Authentication ----------------
@app.post("/signup")
def signup(request: SignupRequest):
    name = request.name.strip()
    email = request.email.strip().lower()

    if not name:
        raise HTTPException(status_code=400, detail="Please enter your name")
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Please enter a valid email")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if database.get_user_by_email(email):
        raise HTTPException(status_code=400, detail="That email is already registered")

    user_id = database.create_user(name, email, hash_password(request.password))
    token = database.create_session(user_id)
    return {"token": token, "user": {"id": user_id, "name": name, "email": email}}

@app.post("/login")
def login(request: LoginRequest):
    email = request.email.strip().lower()
    user = database.get_user_by_email(email)

    if not user or not check_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Wrong email or password")

    token = database.create_session(user["id"])
    return {"token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}

@app.get("/me")
def me(user=Depends(get_current_user)):
    return {"id": user["id"], "name": user["name"], "email": user["email"]}

@app.post("/logout")
def logout(token: str = Depends(get_token)):
    database.delete_session(token)
    return {"message": "Logged out"}

# ---------------- Chat (login required) ----------------
@app.post("/chat")
def chat(request: ChatRequest, user=Depends(get_current_user)):

    final_state = graph.invoke({
        "user_query": request.message
    })

    answer = final_state["final_response"]

    # Generate YouTube link for recipe responses
    youtube_link = None

    if isinstance(answer, str):
        answer_lower = answer.lower()

    if "ingredients:" in answer_lower and "instructions:" in answer_lower:
        youtube_link = get_youtube_link(request.message)
    # Save response in database
    query_id = database.save_query(
        user["id"],
        request.message,
        answer
    )

    return {
        "response": answer,
        "youtube_link": youtube_link,
        "id": query_id
    }


# ---------------- History (login required) ----------------
@app.get("/history")
def history(user=Depends(get_current_user)):
    rows = database.get_history(user["id"])
    return [dict(row) for row in rows]

@app.get("/history/{query_id}")
def history_item(query_id: int, user=Depends(get_current_user)):
    row = database.get_history_item(user["id"], query_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Query not found")
    return dict(row)

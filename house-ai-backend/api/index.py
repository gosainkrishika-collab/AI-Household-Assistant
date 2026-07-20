from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import graph

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
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "House AI Backend is running"}

@app.post("/chat")
def chat(request: ChatRequest):

    final_state = graph.invoke({
        "user_query": request.message
    })

    return {
        "response": final_state["final_response"]
    }
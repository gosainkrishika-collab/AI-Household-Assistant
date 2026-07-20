from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "House AI Backend is running"}

@app.post("/chat")
def chat(request: ChatRequest):
    return {
        "response": "Hello from House AI",
        "agent": "general"
    }
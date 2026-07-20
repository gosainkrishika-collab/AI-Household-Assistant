from fastapi import FastAPI
from pydantic import BaseModel
from graph import graph

app = FastAPI()

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
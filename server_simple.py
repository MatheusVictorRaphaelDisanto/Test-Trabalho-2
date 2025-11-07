# server_simple.py
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Clans BOT", version="1.0.0")

# CORS - PERMITE TUDO
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    model: str
    timestamp: str

@app.get("/")
def home():
    return {"message": "🚀 Servidor rodando na porta 8000!", "status": "online"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/chat")
def chat(request: ChatRequest):
    resposta = f"🤖 Clans BOT diz: Recebi sua mensagem '{request.message}'. Servidor funcionando na porta 8000!"
    
    return ChatResponse(
        reply=resposta,
        model="python-server",
        timestamp=datetime.now().isoformat()
    )

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 INICIANDO SERVIDOR NA PORTA 8000")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
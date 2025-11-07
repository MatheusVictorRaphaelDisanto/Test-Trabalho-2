# backend/main.py
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

# Carregar variáveis de ambiente
load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    print("⚠️  Aviso: DEEPSEEK_API_KEY não encontrada no .env")
    # Para teste, vamos usar uma chave fictícia
    API_KEY = "test-key"

app = FastAPI(title="Clans BOT API", description="API para o chatbot especializado em Clash of Clans")

# Configuração CORS para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (apenas para desenvolvimento)
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
async def root():
    return {
        "message": "🚀 Clans BOT API está funcionando!", 
        "status": "online",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "Clans BOT API",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: str = Header(None)):
    print(f"📨 Mensagem recebida: {request.message}")
    
    # Verificação simplificada de autenticação para desenvolvimento
    expected_token = os.getenv("FRONTEND_TOKEN", "SuaChaveAqui123")
    
    if authorization:
        try:
            token = authorization.replace("Bearer ", "").strip()
            if token != expected_token:
                raise HTTPException(status_code=401, detail="Token inválido")
        except:
            raise HTTPException(status_code=401, detail="Formato de autorização inválido")
    else:
        # Para desenvolvimento, permitir sem auth
        print("⚠️  Aviso: Requisição sem token de autorização")

    # Se não tiver a chave real da DeepSeek, retornar resposta de teste
    if API_KEY == "test-key":
        print("🔧 Modo de teste - usando resposta simulada")
        return ChatResponse(
            reply="🤖 **MODO DE TESTE** - Esta é uma resposta simulada do Clans BOT. Pergunte-me sobre Clash of Clans! (Para usar a API real, configure DEEPSEEK_API_KEY no .env)",
            model="deepseek-chat-test",
            timestamp=datetime.utcnow().isoformat()
        )

    # Preparar requisição para DeepSeek (se tiver chave real)
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        system_message = """Você é um assistente especializado em Clash of Clans. 
        Responda perguntas sobre estratégias, tropas, construções, clãs, guerras, 
        atualizações do jogo e dicas para jogadores."""
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": request.message}
            ],
            "max_tokens": 500,
            "temperature": 0.7,
            "stream": False
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if resp.status_code != 200:
            error_detail = f"Erro na API DeepSeek: {resp.status_code}"
            print(f"❌ Erro DeepSeek: {error_detail}")
            raise HTTPException(status_code=500, detail=error_detail)

        result = resp.json()
        
        if "choices" not in result or len(result["choices"]) == 0:
            raise HTTPException(status_code=500, detail="Resposta da API em formato inválido")
        
        reply = result["choices"][0]["message"]["content"]
        print(f"✅ Resposta enviada: {reply[:50]}...")

        return ChatResponse(
            reply=reply,
            model=result.get("model", "deepseek-chat"),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Timeout na comunicação com a API DeepSeek")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Erro de conexão: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Clans BOT API...")
    print("📡 Endpoints disponíveis:")
    print("   http://localhost:8000")
    print("   http://localhost:8000/health")
    print("   http://localhost:8000/api/v1/chat")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
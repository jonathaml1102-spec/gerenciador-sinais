from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from zoneinfo import ZoneInfo

app = FastAPI(title="Gerenciador de Sinais API")

# CORS liberado para frontend (Lovable, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de entrada
class SignalRequest(BaseModel):
    symbol: str
    direction: str
    timeframe: str

# Rota principal
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API online",
        "time_jst": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()
    }

# Health check
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "time_jst": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()
    }

# Gerar sinal
@app.post("/signal")
def generate_signal(data: SignalRequest):
    return {
        "symbol": data.symbol,
        "direction": data.direction,
        "timeframe": data.timeframe,
        "generated_at_jst": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()
    }

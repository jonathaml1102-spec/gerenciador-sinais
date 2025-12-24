from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Gerenciador de Sinais API")

# CORS (permite frontend externo como Lovable)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SignalRequest(BaseModel):
    symbol: str
    direction: str
    timeframe: str

@app.get("/")
def root():
    return {"status": "ok", "message": "API online"}

@app.get("/health")
def health():
    return {"status": "healthy", "time": datetime.utcnow().isoformat()}

@app.post("/signal")
def generate_signal(data: SignalRequest):
    return {
        "symbol": data.symbol,
        "direction": data.direction,
        "timeframe": data.timeframe,
        "generated_at": datetime.utcnow().isoformat()
    }
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Gerenciador de Sinais API")

class SignalRequest(BaseModel):
    symbol: str
    direction: str
    timeframe: str

@app.get("/")
def root():
    return {"status": "ok", "message": "API online"}

@app.get("/health")
def health():
    return {"status": "healthy", "time": datetime.utcnow()}

@app.post("/signal")
def generate_signal(data: SignalRequest):
    return {
        "symbol": data.symbol,
        "direction": data.direction,
        "timeframe": data.timeframe,
        "generated_at": datetime.utcnow()
    }
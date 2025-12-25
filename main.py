from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

app = FastAPI(title="Gerenciador de Sinais API")

# CORS liberado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== MODELO =====
class SignalRequest(BaseModel):
    symbol: str
    direction: str | None = None
    timeframe: str

# ===== ROTAS =====
@app.get("/")
def root():
    return {
        "status": "ok",
        "time_jst": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "time_jst": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()
    }

# ===== PREÇO EM TEMPO REAL (CRYPTO - BINANCE) =====
@app.get("/price")
def get_price(symbol: str = Query(..., description="Ex: BTCUSDT")):
    url = "https://api.binance.com/api/v3/ticker/price"
    response = requests.get(url, params={"symbol": symbol.upper()}, timeout=10)

    if response.status_code != 200:
        return {"error": "Símbolo inválido ou erro na Binance"}

    data = response.json()

    return {
        "symbol": symbol.upper(),
        "price": float(data["price"]),
        "time_jst": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()
    }

# ===== GERAR SINAL =====
@app.post("/signal")
def generate_signal(data: SignalRequest):
    # Lógica simples inicial (depois evolui para IA)
    direction = "BUY" if datetime.utcnow().second % 2 == 0 else "SELL"

    entry_time = datetime.now(ZoneInfo("Asia/Tokyo"))
    expiry_minutes = 5

    return {
        "symbol": data.symbol,
        "direction": direction,
        "timeframe": data.timeframe,
        "entry_time_jst": entry_time.isoformat(),
        "expiry_minutes": expiry_minutes
    }
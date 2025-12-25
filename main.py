from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
import uuid

app = FastAPI(title="Gerenciador de Sinais API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JST = ZoneInfo("Asia/Tokyo")

# ===== MODELOS =====
class TradeRequest(BaseModel):
    symbol: str
    timeframe: int  # minutos

# ===== STORAGE TEMP (MVP) =====
TRADES = {}

# ===== PREÇO BINANCE =====
def get_binance_price(symbol: str) -> float:
    url = "https://api.binance.com/api/v3/ticker/price"
    r = requests.get(url, params={"symbol": symbol.upper()}, timeout=10)
    r.raise_for_status()
    return float(r.json()["price"])

# ===== HEALTH =====
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "time_jst": datetime.now(JST).isoformat()
    }

# ===== CRIAR TRADE =====
@app.post("/trade")
def create_trade(data: TradeRequest):
    trade_id = str(uuid.uuid4())

    now = datetime.now(JST)
    entry_time = now + timedelta(minutes=2)
    expiry_time = entry_time + timedelta(minutes=data.timeframe)

    direction = "BUY" if now.second % 2 == 0 else "SELL"

    TRADES[trade_id] = {
        "id": trade_id,
        "symbol": data.symbol.upper(),
        "direction": direction,
        "timeframe": data.timeframe,
        "entry_time": entry_time,
        "expiry_time": expiry_time,
        "entry_price": None,
        "result": None,
    }

    return {
        "trade_id": trade_id,
        "symbol": data.symbol.upper(),
        "direction": direction,
        "entry_time_jst": entry_time.isoformat(),
        "expiry_time_jst": expiry_time.isoformat(),
    }

# ===== STATUS DO TRADE =====
@app.get("/trade/{trade_id}")
def trade_status(trade_id: str):
    trade = TRADES.get(trade_id)
    if not trade:
        return {"error": "Trade not found"}

    now = datetime.now(JST)

    # Registrar preço de entrada
    if trade["entry_price"] is None and now >= trade["entry_time"]:
        trade["entry_price"] = get_binance_price(trade["symbol"])

    # Finalizar trade
    if trade["entry_price"] and trade["result"] is None and now >= trade["expiry_time"]:
        final_price = get_binance_price(trade["symbol"])

        if trade["direction"] == "BUY":
            trade["result"] = "WIN" if final_price > trade["entry_price"] else "LOSS"
        else:
            trade["result"] = "WIN" if final_price < trade["entry_price"] else "LOSS"

        trade["final_price"] = final_price

    return {
        "trade_id": trade["id"],
        "symbol": trade["symbol"],
        "direction": trade["direction"],
        "entry_price": trade["entry_price"],
        "result": trade["result"],
        "time_jst": now.isoformat(),
    }
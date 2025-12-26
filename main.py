from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import requests
import uuid

from sqlalchemy.orm import Session
from db import SessionLocal, Base, engine
from models import Trade

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

# cria tabela automaticamente no SQLite (persistente no Disk do Render)
Base.metadata.create_all(bind=engine)

class TradeRequest(BaseModel):
    symbol: str
    timeframe: int  # minutos

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_binance_price(symbol: str) -> float:
    url = "https://api.binance.com/api/v3/ticker/price"
    r = requests.get(url, params={"symbol": symbol.upper()}, timeout=10)
    r.raise_for_status()
    return float(r.json()["price"])

@app.get("/health")
def health():
    return {"status": "healthy", "time_jst": datetime.now(JST).isoformat()}

@app.post("/trade")
def create_trade(data: TradeRequest, db: Session = Depends(get_db)):
    trade_id = str(uuid.uuid4())

    now = datetime.now(JST)
    entry_time = now + timedelta(minutes=2)
    expiry_time = entry_time + timedelta(minutes=data.timeframe)

    direction = "BUY" if now.second % 2 == 0 else "SELL"

    trade = Trade(
        id=trade_id,
        symbol=data.symbol.upper(),
        direction=direction,
        timeframe=data.timeframe,
        entry_time_jst=entry_time.isoformat(),
        expiry_time_jst=expiry_time.isoformat(),
        entry_price=None,
        final_price=None,
        result=None,
    )

    db.add(trade)
    db.commit()
    db.refresh(trade)

    return {
        "trade_id": trade.id,
        "symbol": trade.symbol,
        "direction": trade.direction,
        "entry_time_jst": trade.entry_time_jst,
        "expiry_time_jst": trade.expiry_time_jst,
    }

@app.get("/trade/{trade_id}")
def trade_status(trade_id: str, db: Session = Depends(get_db)):
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        return {"error": "Trade not found"}

    now = datetime.now(JST)

    entry_time = datetime.fromisoformat(trade.entry_time_jst)
    expiry_time = datetime.fromisoformat(trade.expiry_time_jst)

    if trade.entry_price is None and now >= entry_time:
        trade.entry_price = get_binance_price(trade.symbol)
        db.commit()
        db.refresh(trade)

    if trade.entry_price is not None and trade.result is None and now >= expiry_time:
        final_price = get_binance_price(trade.symbol)
        trade.final_price = final_price

        if trade.direction == "BUY":
            trade.result = "WIN" if final_price > trade.entry_price else "LOSS"
        else:
            trade.result = "WIN" if final_price < trade.entry_price else "LOSS"

        db.commit()
        db.refresh(trade)

    return {
        "trade_id": trade.id,
        "symbol": trade.symbol,
        "direction": trade.direction,
        "entry_price": trade.entry_price,
        "final_price": trade.final_price,
        "result": trade.result,
        "time_jst": now.isoformat(),
    }
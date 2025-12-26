from sqlalchemy import Column, String, Integer, Float
from db import Base

class Trade(Base):
    _tablename_ = "trades"

    id = Column(String, primary_key=True, index=True)
    symbol = Column(String)
    direction = Column(String)
    timeframe = Column(Integer)

    entry_time_jst = Column(String)
    expiry_time_jst = Column(String)

    entry_price = Column(Float, nullable=True)
    final_price = Column(Float, nullable=True)
    result = Column(String, nullable=True)
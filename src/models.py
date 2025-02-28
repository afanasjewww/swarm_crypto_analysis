from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class OHLCData(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None

class TechnicalIndicators(BaseModel):
    sma: float
    ema: float
    rsi: float
    macd: float
    atr: float
    bollinger_bands: List[float]  # [upper, middle, lower]

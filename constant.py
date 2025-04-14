from MetaTrader5 import TIMEFRAME_M1, TIMEFRAME_M5, TIMEFRAME_M15, TIMEFRAME_H1, TIMEFRAME_H4, TIMEFRAME_D1
from typing import Literal

TimeFrameKeysLiteral = Literal["1m", "5m", "15m", "h1", "h4", "d1"]
TimeFrames: dict[str, str] = {
    "1m": TIMEFRAME_M1,
    "5m": TIMEFRAME_M5,
    "15m": TIMEFRAME_M15,
    "h1": TIMEFRAME_H1,
    "h4": TIMEFRAME_H4,
    "d1": TIMEFRAME_D1
}

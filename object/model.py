from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal

from common.constant import TimeFrameKeysLiteral


@dataclass
class TrendObject:
    level: int
    trend: str


@dataclass
class MarkerObject:
    text: Optional[str]
    position: Optional[Literal["above", "inside", "below"]]
    color: Optional[str]
    shape: Optional[Literal["arrow_up", "arrow_down", "circle", "square", "triangleUp", "triangleDown"]]
    time: datetime


@dataclass
class NoteTrendObject:
    trend: Literal["Uptrend", "Downtrend", "Sideways"]
    time_frame: TimeFrameKeysLiteral

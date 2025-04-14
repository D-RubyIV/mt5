from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal


@dataclass
class MarkerObject:
    text: Optional[str]
    position: Optional[Literal["above", "inside", "below"]]
    color: Optional[str]
    shape: Optional[Literal["arrow_up", "arrow_down", "circle", "square", "triangleUp", "triangleDown"]]
    time: datetime
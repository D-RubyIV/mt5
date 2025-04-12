from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Literal

@dataclass
class MarkerObject:
    text: Optional[str]
    position: Optional[Literal["allow", "inside", "below"]]
    color: Optional[str]
    shape: Optional[Literal["arrow_up", "arrow_down", "circle", "square", "triangleUp", "triangleDown"]]
    time: datetime
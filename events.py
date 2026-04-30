import os
import random

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

class Event(ABC):
    """
    Abstract base class for all events
    """
    event_type: str = "event"

    @abstractmethod
    def perform(self) -> int | str:
        """
        Run the event and return the result
        """
        pass

    @abstractmethod
    def possible_outcomes(self) -> list[int | str | None]:
        """
        Return possible outcomes
        """
        pass

    @abstractmethod
    def label(self) -> str:
        """
        
        """
        pass

    def to_record(self, outcome: int | str) -> dict[str, str | int]:
        """
        
        """
        return {
            "type": self.event_type,
            "label": self.label(),
            "outcome": outcome,
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }
    
class Coin(Event):

    def __init__(self, p_heads: float = 0.5) -> None:
        if not 0.0 <= p_heads <= 1.0:
            raise ValueError("p_heads must be between 0 and 1")
        self.p_heads = p_heads
        self.type = self.label()

    def perform(self) -> str:
        flip_result = "Heads" if random.random() < self.p_heads else "Tails"
        return flip_result
    
    def possible_outcomes(self) -> list[str]:
        return ["Heads", "Tails"]
    
    def label(self) -> str:
        if self.p_heads == 0.5:
            return "Fair Coin"
        
        return f"Biased Coin (p={self.p_heads:.2f})"
    

class Die(Event):
    def __init__(self, faces: int = 6) -> None:
        if faces < 4:
            raise ValueError("Die must have at least 4 faces")
        self.faces = faces
        self.type = f"d{faces}"

    def perform(self) -> int:
            return random.randint(1, self.faces)
        
    def possible_outcomes(self) -> list:
            return list(range(1, self.faces + 1))
        
    def label(self) -> str:
            return f"d{self.faces}"
        
    
def event_factory(event_type: str, params: dict) -> Event:
    if event_type == "coin":
        return Coin(p_heads=params.get("p_heads", 0.5))
    elif event_type == "die":
        return Die(faces=params.get("faces", 6))
    else:
        raise ValueError(f"Unknown value provided for event_type: {event_type}")
    

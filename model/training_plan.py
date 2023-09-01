import uuid
from typing import Optional, List
from pydantic import BaseModel, Field


class Equipment(BaseModel):
    Paddles: bool = False
    KickBoard: bool = False
    PullBuoy: bool = False
    Snorkel: bool = False
    Other: Optional[str]


class Exercise(BaseModel):
    Volume: float
    VolumeUnits: str = "m"
    Time: Optional[float]
    TimeUnits: str = "min"
    Stroke: str
    Speed: int = None
    Legs: bool = False
    Arms: bool = False
    Equipment: Optional[Equipment]
    Comments: Optional[str]


class TrainingPlan(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    LevelWeekDay: str = None
    Level: int
    Week: int
    Day: int
    Exercises: List[Exercise]

    def set_LevelWeekDay(self):
        self.LevelWeekDay: str = str(self.Level) + str(self.Week) + str(self.Day)

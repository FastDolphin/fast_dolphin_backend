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
    LevelWeekDay: str = None
    Level: int
    Week: int
    Day: int
    Exercises: List[Exercise]
    TotalVolume: float = 0.0
    TotalTime: float = 0.0

    def set_LevelWeekDay(self):
        self.LevelWeekDay: str = str(self.Level) + str(self.Week) + str(self.Day)

    def set_total_volume_and_time(self):
        if self.Exercises:
            for exercise in self.Exercises:
                if isinstance(exercise.Volume, float) or isinstance(
                    exercise.Volume, int
                ):
                    self.TotalVolume += exercise.Volume
                if isinstance(exercise.Time, float) or isinstance(exercise.Time, int):
                    self.TotalTime += exercise.Time


class TrainingPlanWithId(TrainingPlan):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")

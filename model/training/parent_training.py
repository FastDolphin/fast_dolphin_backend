import uuid
from typing import List, Optional

from pydantic import BaseModel, Field, validator

try:
    from ..dryland_training_plan import DryLandExercise
except ModuleNotFoundError:
    from model.dryland_training_plan import DryLandExercise


class ParentTraining(BaseModel):
    LevelWeekDay: Optional[str] = None
    Level: int
    Week: int
    Day: int
    inGym: bool
    Exercises: List[DryLandExercise]
    TotalNumberExercises: int = 0
    TotalTime: float = 0.0
    TotalTimeUnits: str = "сек"

    def set_LevelWeekDay(self):
        self.LevelWeekDay: str = str(self.Level) + str(self.Week) + str(self.Day)

    def set_total_number_of_exercises(self):
        if self.Exercises:
            self.TotalNumberExercises = len(self.Exercises)

    def set_total_training_time(self):
        for exercise in self.Exercises:
            exercise.set_total_exercise_time()
            self.TotalTime += exercise.TotalExerciseTime

    @validator("TotalTimeUnits", pre=True, always=True)
    def check_total_time_units(cls, value):
        if value not in ["сек", "мин"]:
            raise ValueError("TotalTimeUnits must be either 'сек' or 'мин'")
        return value


class ParentTrainingWithID(ParentTraining):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")

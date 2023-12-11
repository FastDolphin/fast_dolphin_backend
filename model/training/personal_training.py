import uuid
from typing import List

from pydantic import BaseModel, Field, validator

try:
    from ..dryland_training_plan import DryLandExercise
except ModuleNotFoundError:
    from model.dryland_training_plan import DryLandExercise


class PersonalTraining(BaseModel):
    TgIdYearWeekDay: str = None
    TgId: int
    Year: int
    Week: int
    Day: int
    inGym: bool
    Exercises: List[DryLandExercise]
    TotalNumberExercises: int = 0
    TotalTime: float = 0.0
    TotalTimeUnits: str = "сек"

    def set_TgIdYearWeekDay(self):
        self.TgIdYearWeekDay = (
            str(self.TgId) + str(self.Year) + str(self.Week) + str(self.Day)
        )

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


class PersonalTrainingWithID(PersonalTraining):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")


class PersonalTrainingMetaData(BaseModel):
    TgId: int
    Year: int
    Week: int


class PersonalTrainingMetaDataWithID(PersonalTrainingMetaData):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")

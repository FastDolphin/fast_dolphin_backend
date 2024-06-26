import uuid
from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field, validator

try:
    from ..dryland_training_plan import DryLandExercise
    from ..training_plan import Exercise as WaterExercise
except ModuleNotFoundError:
    from model.dryland_training_plan import DryLandExercise
    from model.training_plan import Exercise as WaterExercise


class PersonalTraining(BaseModel):
    TgIdYearWeekDay: Optional[str] = None
    ApiKeyYearWeekDay: Optional[str] = None
    TgId: int = 0
    ApiKey: str = ""
    Year: int
    Week: int
    Day: int
    trainingType: Union[Literal["fitness"], Literal["swimming"]] = "fitness"
    inGym: bool = True
    inSwimmingPool: bool = False
    Exercises: List[Union[DryLandExercise, WaterExercise]]
    TotalNumberExercises: int = 0
    TotalTime: float = 0.0
    TotalTimeUnits: str = "сек"
    TotalVolume: float = 0.0
    TotalVolumeUnits: str = "м"

    def set_TgIdYearWeekDay(self):
        self.TgIdYearWeekDay = (
            str(self.TgId) + str(self.Year) + str(self.Week) + str(self.Day)
        )

    def set_ApiKeyYearWeekDay(self):
        self.ApiKeyYearWeekDay = (
            str(self.ApiKey) + str(self.Year) + str(self.Week) + str(self.Day)
        )

    def set_total_number_of_exercises(self):
        if self.Exercises:
            self.TotalNumberExercises = len(self.Exercises)

    def set_total_training_time(self):
        if self.Exercises and self.TotalTime == 0:
            for exercise in self.Exercises:
                if hasattr(exercise, "set_total_exercise_time"):
                    exercise.set_total_exercise_time()
                    self.TotalTime += exercise.TotalExerciseTime

    def set_total_volume_and_time(self):
        if self.Exercises and self.TotalVolume == 0 and self.TotalTime == 0:
            for exercise in self.Exercises:
                if isinstance(exercise.Volume, float) or isinstance(
                    exercise.Volume, int
                ):
                    self.TotalVolume += exercise.Volume
                if isinstance(exercise.Time, float) or isinstance(exercise.Time, int):
                    self.TotalTime += exercise.Time

    @validator("TotalVolumeUnits", pre=True, always=True)
    def check_total_volume_units(cls, value):
        if value not in ["м", "км"]:
            raise ValueError("TotalVolumeUnits must be either 'м' or 'км'")
        return value

    @validator("TotalTimeUnits", pre=True, always=True)
    def check_total_time_units(cls, value):
        if value not in ["сек", "мин"]:
            raise ValueError("TotalTimeUnits must be either 'сек' or 'мин'")
        return value

    @validator("inGym")
    def validate_in_gym(cls, in_gym, values):
        if in_gym and values.get("trainingType") != "fitness":
            raise ValueError("inGym can only be True if trainingType is 'fitness'")
        return in_gym

    @validator("inSwimmingPool")
    def validate_in_swimming_pool(cls, in_swimming_pool, values):
        if in_swimming_pool and values.get("trainingType") != "swimming":
            raise ValueError(
                "inSwimmingPool can only be True if trainingType is 'swimming'"
            )
        return in_swimming_pool


class PersonalTrainingWithID(PersonalTraining):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")


class PersonalTrainingMetaData(BaseModel):
    TgId: int
    Year: int
    Week: int


class PersonalTrainingMetaDataWithID(PersonalTrainingMetaData):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")

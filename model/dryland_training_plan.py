from pydantic import BaseModel, validator
from typing import Optional


class DryLandExercise(BaseModel):
    Name: str
    nSets: float = 1.0
    nReps: float = 1.0
    Time: Optional[float] = None
    TimeUnits: str = "мин"
    Weight: float = 0.0
    WeightUnits: str = "кг"
    OtherResistance: Optional[str] = None
    ResistanceComments: Optional[str] = None
    Speed: Optional[int] = None
    Comments: Optional[str] = None
    TotalExerciseTime: float = 0.0

    _AverageRepTime: int = 3
    _AverageRepTimeUnits: str = "сек"
    _AverageRestTime: int = 60
    _AverageRestTimeUnits: str = "сек"

    def set_total_exercise_time(self):
        if self.Time is None or self.Time == 0.0:
            one_set_and_rest_time: float = (
                self._AverageRepTime * self.nReps + self._AverageRestTime
            )
            self.TotalExerciseTime = one_set_and_rest_time * self.nSets
        elif self.TimeUnits == "мин":
            one_set_and_rest_time: float = self.Time * 60 + self._AverageRestTime
            self.TotalExerciseTime = one_set_and_rest_time * self.nSets
        else:
            one_set_and_rest_time: float = self.Time + self._AverageRestTime
            self.TotalExerciseTime = one_set_and_rest_time * self.nSets

    @validator("TimeUnits", pre=True, always=True)
    def check_time_units(cls, value):
        if value not in ["сек", "мин"]:
            raise ValueError("TimeUnits must be either 'сек' or 'мин'")
        return value

    @validator("WeightUnits", pre=True, always=True)
    def check_weight_units(cls, value):
        if value not in ["кг"]:
            raise ValueError("WeightUnits must be 'кг'")
        return value
